"""
Seed Script — loads the Indian legal corpus into ChromaDB for retrieval.

Usage:
    cd /path/to/Legal_AI_Assistant
    python scripts/seed_legal_data.py

This script:
1. Loads legal_corpus.json
2. Generates embeddings using Google Generative AI
3. Stores in ChromaDB for hybrid retrieval
"""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

CORPUS_PATH = os.path.join(os.path.dirname(__file__), "data/seed/legal_corpus.json")


async def seed():
    from app.core.config import settings

    with open(CORPUS_PATH) as f:
        corpus = json.load(f)

    entries = corpus["entries"]
    print(f"📚 Loading {len(entries)} legal corpus entries into ChromaDB...")

    try:
        import chromadb
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
        collection = client.get_or_create_collection(
            name=settings.CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        embedder = GoogleGenerativeAIEmbeddings(
            google_api_key=settings.GOOGLE_API_KEY,
            model="models/embedding-001",
        )

        texts = [e["text"] for e in entries]
        ids = [e["id"] for e in entries]
        metadatas = [
            {
                "source": e.get("source", ""),
                "category": e.get("category", ""),
                "section": e.get("section", ""),
                "act": e.get("act", ""),
                "year": str(e.get("year", "")),
            }
            for e in entries
        ]

        # Batch embed and store
        batch_size = 10
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i : i + batch_size]
            batch_ids = ids[i : i + batch_size]
            batch_meta = metadatas[i : i + batch_size]

            embeddings = await embedder.aembed_documents(batch_texts)
            collection.upsert(
                ids=batch_ids,
                documents=batch_texts,
                embeddings=embeddings,
                metadatas=batch_meta,
            )
            print(f"  ✅ Indexed {min(i + batch_size, len(texts))}/{len(texts)} entries")

        print(f"\n🎉 Seeding complete! {len(entries)} entries in ChromaDB collection '{settings.CHROMA_COLLECTION_NAME}'")

    except Exception as e:
        print(f"⚠️  ChromaDB not available ({e}). Corpus saved locally only.")
        print("   Start ChromaDB with: docker run -p 8001:8000 chromadb/chroma")


if __name__ == "__main__":
    asyncio.run(seed())
