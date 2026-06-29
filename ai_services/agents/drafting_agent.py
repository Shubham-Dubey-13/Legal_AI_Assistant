"""
DRAFTING AGENT — AI-powered legal document generation

Supports:
- FIR (First Information Report)
- Legal Notices
- Petitions (Civil, Criminal, Writ)
- Affidavits
- Bail Applications
- Consumer Complaints
- Contracts & Agreements
- Will / Testament
"""

from typing import Dict, List, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import sys, os, datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../backend'))
from app.core.config import settings

DRAFT_PROMPTS = {
    "fir": """You are a legal drafting expert. Draft a professional First Information Report (FIR) for the Indian Police.

DETAILS:
- Complainant: {parties.get('complainant', 'Not provided')}
- Accused: {parties.get('accused', 'Unknown person')}
- Incident Description: {description}
- Facts: {facts}

Format with proper FIR structure:
1. Police Station details (placeholder)
2. Complainant details  
3. Incident description with date, time, place
4. Names of accused / unknown person
5. Witnesses (if any)
6. Evidence/Property (if any)
7. Applicable sections: {sections}
8. Complainant's signature and date

Use formal language. Reference applicable BNS/IPC sections.""",

    "legal_notice": """Draft a formal Legal Notice as per Indian law standards.

DETAILS:
- Sender: {parties.get('sender', 'Not provided')}
- Recipient: {parties.get('recipient', 'Not provided')}  
- Subject: {description}
- Relief Sought: {relief_sought}
- Facts: {facts}

Structure:
1. Header with sender's address and date
2. "LEGAL NOTICE" heading
3. Introduction identifying the parties
4. Detailed facts and grievances
5. Legal basis (relevant acts and sections)
6. Specific demands/reliefs
7. Time limit (15/30 days)
8. Consequence of non-compliance
9. Advocate signature block

Make it legally precise and professional.""",

    "petition": """Draft a Writ Petition / Civil Petition for Indian courts.

DETAILS:
- Petitioner: {parties.get('petitioner', 'Petitioner')}
- Respondent: {parties.get('respondent', 'Respondent')}
- Case Description: {description}
- Facts: {facts}
- Relief Sought: {relief_sought}

Structure:
IN THE HIGH COURT OF [STATE] AT [CITY]
WRIT PETITION NO. ___ OF {year}

1. Title and Parties
2. Jurisdiction
3. Facts of the Case (numbered paragraphs)
4. Grounds for Petition
5. Constitutional/Statutory Provisions Violated
6. Earlier Proceedings (if any)
7. Prayer/Relief Sought
8. Verification
9. Advocate's signature""",

    "affidavit": """Draft an Affidavit as per Indian legal requirements.

DETAILS:
- Deponent: {parties.get('deponent', 'Deponent')}
- Subject: {description}
- Statements: {facts}

Structure:
AFFIDAVIT

I, [Name], aged [age], residing at [address], do hereby solemnly affirm and state as follows:

1. I am the deponent herein...
2. [Numbered statements]
3. I say that the contents of this affidavit are true to my knowledge...

DEPONENT

Sworn/Affirmed before me this [date] day of [month] [year]
NOTARY PUBLIC / OATH COMMISSIONER""",

    "bail_application": """Draft a Bail Application for Indian criminal courts.

DETAILS:
- Accused: {parties.get('accused', 'Accused')}
- FIR Details: {facts}
- Grounds for Bail: {relief_sought}
- Case Description: {description}

Structure:
IN THE COURT OF SESSIONS JUDGE / CHIEF JUDICIAL MAGISTRATE
BAIL APPLICATION NO. ___ OF {year}

IN THE MATTER OF:
[State/Complainant] vs. [Accused]

APPLICATION FOR BAIL UNDER SECTION 480 BNSS (formerly 437/439 CrPC)

1. Brief Facts
2. Grounds for Bail
   a. Accused is innocent
   b. No flight risk
   c. Evidence not to be tampered
   d. Cooperating with investigation
3. Previous bail applications if any
4. Prayer
5. Advocate signature""",
}


class DraftingAgent:
    """
    AI-powered legal document drafting agent.
    Uses structured prompts + LLM to generate professional legal documents.
    """

    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=settings.GOOGLE_API_KEY,
            model=settings.GEMINI_MODEL,
            temperature=0.3,  # Slightly creative for natural language
        )

    async def generate_draft(
        self,
        draft_type: str,
        description: str,
        parties: Dict[str, str] = None,
        facts: str = "",
        relief_sought: str = "",
        language: str = "en",
        jurisdiction: str = "India",
    ) -> Dict[str, Any]:
        """Generate a legal document draft"""

        parties = parties or {}
        year = datetime.datetime.now().year

        # Get relevant sections
        from ai_services.agents.research_agent import ResearchAgent
        research = ResearchAgent()
        sections_result = await research._identify_sections(description)
        sections = ", ".join(sections_result.get("bns", []) or sections_result.get("ipc", []))

        system_prompt = f"""You are a senior Indian legal expert and advocate with 20+ years of experience.
Draft a professional, legally sound document for {jurisdiction}.
Use formal legal language. Include all mandatory legal elements.
Reference updated laws (BNS 2023, BNSS 2023, BSA 2023 where applicable).
Current year: {year}"""

        # Get template or use generic drafting
        if draft_type in DRAFT_PROMPTS:
            template = DRAFT_PROMPTS[draft_type]
            user_prompt = template.format(
                parties=parties,
                description=description,
                facts=facts,
                relief_sought=relief_sought,
                sections=sections or "Applicable sections to be determined",
                year=year,
            )
        else:
            user_prompt = f"""Draft a professional {draft_type.replace('_', ' ').title()} document.

Parties: {parties}
Description: {description}
Facts: {facts}
Relief sought: {relief_sought}
Applicable sections: {sections}

Make it legally comprehensive and professionally formatted."""

        if language != "en":
            lang_map = {"hi": "Hindi", "ta": "Tamil", "te": "Telugu", "bn": "Bengali", "mr": "Marathi"}
            user_prompt += f"\n\nDraft the document in {lang_map.get(language, 'English')}."

        try:
            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt),
            ])
            content = response.content

            return {
                "title": f"{draft_type.replace('_', ' ').upper()} — AI Generated Draft",
                "content": content,
                "sections_used": sections_result.get("bns", []) + sections_result.get("ipc", []),
                "word_count": len(content.split()),
            }
        except Exception as e:
            return {
                "title": f"{draft_type.upper()} Draft",
                "content": self._get_template_fallback(draft_type, parties, description, year),
                "sections_used": [],
                "word_count": 200,
            }

    def _get_template_fallback(self, draft_type: str, parties: dict, description: str, year: int) -> str:
        """Fallback template when LLM is unavailable"""
        return f"""[AI DRAFT - TEMPLATE MODE]

{draft_type.replace('_', ' ').upper()}

Date: {datetime.date.today().strftime('%d %B %Y')}

Parties:
{chr(10).join([f"- {k.title()}: {v}" for k, v in parties.items()]) if parties else "To be filled"}

Subject: {description}

[This draft was generated in template mode. Please configure your Google Gemini API key for full AI-powered drafting.]

Important Note: This is an AI-generated template and requires review by a qualified legal professional before use.

Contact NALSA for free legal aid: 15100
Website: www.nalsa.gov.in"""
