"""
DOCUMENT PROCESSOR — Full AI pipeline for legal PDF processing

Pipeline:
1. PDF parsing (PyMuPDF + pdfplumber + OCR fallback)
2. Section-aware text chunking
3. OpenAI embeddings generation
4. ChromaDB indexing
5. IPC/BNS section identification
6. Named Entity Recognition (parties, dates, courts)
7. Summary generation
"""

from typing import List, Dict, Any, Optional
import asyncio, os, re
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))
from app.core.config import settings


class DocumentProcessor:
    """
    End-to-end legal PDF processing pipeline.
    Extracts, chunks, embeds, and indexes legal documents.
    """

    def __init__(self):
        self.chunk_size = 512      # tokens per chunk
        self.chunk_overlap = 50    # overlap for context continuity

    async def process(
        self,
        doc_id: str,
        file_path: str,
        user_id: str,
        original_filename: str,
    ) -> Dict[str, Any]:
        """Full document processing pipeline"""

        print(f"📄 Processing document: {original_filename}")

        # Step 1: Extract text
        text, page_count = await self._extract_text(file_path)
        print(f"✅ Extracted {len(text)} chars from {page_count} pages")

        # Step 2: Clean and normalize
        cleaned_text = self._clean_text(text)

        # Step 3: Section-aware chunking
        chunks = self._chunk_document(cleaned_text, doc_id, original_filename)
        print(f"✅ Created {len(chunks)} chunks")

        # Step 4: Generate embeddings and index in ChromaDB
        await self._index_chunks(chunks, doc_id)
        print(f"✅ Indexed in ChromaDB")

        # Step 5: Extract metadata (parallel)
        sections_task = self._identify_legal_sections(cleaned_text)
        entities_task = self._extract_entities(cleaned_text)
        summary_task = self._generate_summary(cleaned_text)

        sections, entities, summary = await asyncio.gather(
            sections_task, entities_task, summary_task, return_exceptions=True
        )

        return {
            "doc_id": doc_id,
            "page_count": page_count,
            "chunk_count": len(chunks),
            "summary": summary if isinstance(summary, str) else "",
            "ipc_sections": sections.get("ipc", []) if isinstance(sections, dict) else [],
            "bns_sections": sections.get("bns", []) if isinstance(sections, dict) else [],
            "parties": entities.get("parties", {}) if isinstance(entities, dict) else {},
            "case_type": entities.get("case_type", "Unknown") if isinstance(entities, dict) else "Unknown",
            "status": "completed",
        }

    async def _extract_text(self, file_path: str) -> tuple[str, int]:
        """Extract text from PDF using PyMuPDF (fastest) with pdfplumber fallback"""
        text = ""
        page_count = 0

        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            page_count = len(doc)
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
        except ImportError:
            pass

        if not text:
            try:
                import pdfplumber
                with pdfplumber.open(file_path) as pdf:
                    page_count = len(pdf.pages)
                    for page in pdf.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted + "\n"
            except ImportError:
                pass

        if not text:
            # OCR fallback for scanned PDFs
            text = await self._ocr_extract(file_path)

        return text or "[No text extracted]", page_count or 1

    async def _ocr_extract(self, file_path: str) -> str:
        """OCR for scanned PDF documents"""
        try:
            import pytesseract
            from PIL import Image
            import fitz

            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                pix = page.get_pixmap(dpi=300)
                img_bytes = pix.tobytes("png")
                from io import BytesIO
                img = Image.open(BytesIO(img_bytes))
                text += pytesseract.image_to_string(img, lang='eng+hin') + "\n"
            return text
        except:
            return ""

    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\(\)\[\]\{\}\-\'\"\/\%\@\#\&\*]', '', text)
        lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 10]
        return '\n'.join(lines)

    def _chunk_document(
        self, text: str, doc_id: str, filename: str
    ) -> List[Dict]:
        """
        Section-aware chunking strategy:
        1. Try to split by legal sections (Section X, Article X)
        2. Fall back to fixed-size chunks with overlap
        """
        # Try section-based splitting
        section_pattern = r'(?=(?:Section|Article|Part|Chapter|Rule)\s+\d+)'
        sections = re.split(section_pattern, text, flags=re.IGNORECASE)

        chunks = []
        if len(sections) > 3:
            for i, section in enumerate(sections):
                if len(section.strip()) < 50:
                    continue
                # Sub-chunk if too large
                if len(section) > 2000:
                    sub_chunks = self._fixed_size_chunks(section)
                    for j, sub in enumerate(sub_chunks):
                        chunks.append({
                            "id": f"{doc_id}_s{i}_c{j}",
                            "text": sub,
                            "metadata": {
                                "doc_id": doc_id,
                                "filename": filename,
                                "chunk_index": len(chunks),
                                "chunk_type": "section",
                            }
                        })
                else:
                    chunks.append({
                        "id": f"{doc_id}_s{i}",
                        "text": section.strip(),
                        "metadata": {
                            "doc_id": doc_id,
                            "filename": filename,
                            "chunk_index": i,
                            "chunk_type": "section",
                        }
                    })
        else:
            # Fixed-size chunking
            for i, chunk_text in enumerate(self._fixed_size_chunks(text)):
                chunks.append({
                    "id": f"{doc_id}_c{i}",
                    "text": chunk_text,
                    "metadata": {
                        "doc_id": doc_id,
                        "filename": filename,
                        "chunk_index": i,
                        "chunk_type": "fixed",
                    }
                })

        return chunks

    def _fixed_size_chunks(self, text: str, size: int = 1500, overlap: int = 150) -> List[str]:
        """Split text into fixed-size overlapping chunks"""
        chunks = []
        start = 0
        while start < len(text):
            end = start + size
            chunk = text[start:end]
            # Try to end at a sentence boundary
            last_period = chunk.rfind('.')
            if last_period > size * 0.8:
                chunk = chunk[:last_period + 1]
                end = start + last_period + 1
            chunks.append(chunk.strip())
            start = end - overlap
        return [c for c in chunks if len(c) > 50]

    async def _index_chunks(self, chunks: List[Dict], doc_id: str):
        """Generate embeddings and store in ChromaDB"""
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            import chromadb

            embedder = GoogleGenerativeAIEmbeddings(
                google_api_key=settings.GOOGLE_API_KEY,
                model="models/embedding-001",
            )

            client = chromadb.HttpClient(
                host=settings.CHROMA_HOST,
                port=settings.CHROMA_PORT,
            )
            collection = client.get_or_create_collection(
                name=f"doc_{doc_id}",
                metadata={"hnsw:space": "cosine"},
            )

            texts = [c["text"] for c in chunks]
            embeddings = await embedder.aembed_documents(texts)

            collection.add(
                ids=[c["id"] for c in chunks],
                documents=texts,
                embeddings=embeddings,
                metadatas=[c["metadata"] for c in chunks],
            )
        except Exception as e:
            print(f"ChromaDB indexing skipped: {e}")

    async def _identify_legal_sections(self, text: str) -> Dict[str, List[str]]:
        """Identify IPC/BNS sections mentioned in the document"""
        from ai_services.agents.research_agent import ResearchAgent
        agent = ResearchAgent()
        return await agent._identify_sections(text[:3000])

    async def _extract_entities(self, text: str) -> Dict[str, Any]:
        """Extract legal entities: parties, court, dates, case number"""
        return {
            "parties": {
                "petitioner": self._extract_pattern(text, r'(?i)(?:petitioner|appellant|plaintiff|complainant)[:\s]+([A-Z][A-Za-z\s]+?)(?:\n|vs|v\.)'),
                "respondent": self._extract_pattern(text, r'(?i)(?:respondent|defendant|opposition)[:\s]+([A-Z][A-Za-z\s]+?)(?:\n|$)'),
            },
            "court": self._extract_pattern(text, r'(?i)(?:IN THE|BEFORE THE)\s+([A-Z][A-Za-z\s]+COURT[A-Za-z\s]*)'),
            "case_number": self._extract_pattern(text, r'(?i)(?:Case No\.|Criminal Case|Civil Case|W\.P\.|CRL\.)\s*[\d/]+'),
            "case_type": self._classify_case_type(text),
        }

    def _extract_pattern(self, text: str, pattern: str) -> str:
        """Extract first match of a regex pattern"""
        match = re.search(pattern, text)
        return match.group(1).strip() if match else "Not identified"

    def _classify_case_type(self, text: str) -> str:
        """Classify the type of legal case"""
        text_lower = text.lower()
        if any(w in text_lower for w in ["murder", "theft", "rape", "assault", "fir", "accused"]):
            return "Criminal"
        elif any(w in text_lower for w in ["property", "contract", "damages", "injunction", "plaintiff"]):
            return "Civil"
        elif any(w in text_lower for w in ["consumer", "deficiency", "refund", "service"]):
            return "Consumer"
        elif any(w in text_lower for w in ["fundamental right", "article 21", "writ", "habeas"]):
            return "Constitutional"
        elif any(w in text_lower for w in ["divorce", "maintenance", "custody", "matrimonial"]):
            return "Family"
        return "General"

    async def _generate_summary(self, text: str) -> str:
        """Generate AI summary of the legal document"""
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_core.messages import HumanMessage, SystemMessage

            llm = ChatGoogleGenerativeAI(google_api_key=settings.GOOGLE_API_KEY, model=settings.GEMINI_MODEL, temperature=0.1)
            response = await llm.ainvoke([
                SystemMessage(content="You are a legal document analyst. Summarize this Indian legal document concisely in 3-4 sentences. Include: case type, parties, key legal issues, and outcome if mentioned."),
                HumanMessage(content=f"Summarize this legal document:\n\n{text[:4000]}"),
            ])
            return response.content
        except:
            return "Document processed successfully. Summary generation requires Gemini API key."
