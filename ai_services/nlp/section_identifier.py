"""
IPC/BNS Section Identifier — NLP-based section detection
"""

from typing import List, Dict
import re
from ai_services.agents.research_agent import LEGAL_KEYWORDS, IPC_BNS_MAP


class IPCSectionIdentifier:
    def identify_sections(self, query: str) -> List[Dict]:
        query_lower = query.lower()
        results = []
        for keyword, section_nums in LEGAL_KEYWORDS.items():
            if keyword in query_lower:
                for num in section_nums:
                    if num in IPC_BNS_MAP:
                        m = IPC_BNS_MAP[num]
                        results.append({
                            "section": m["ipc"],
                            "punishment": m["punishment"],
                            "keyword_matched": keyword,
                        })
        return results


class BNSSectionIdentifier:
    def identify_sections(self, query: str) -> List[Dict]:
        query_lower = query.lower()
        results = []
        for keyword, section_nums in LEGAL_KEYWORDS.items():
            if keyword in query_lower:
                for num in section_nums:
                    if num in IPC_BNS_MAP:
                        m = IPC_BNS_MAP[num]
                        results.append({
                            "section": m["bns"],
                            "punishment": m["punishment"],
                            "keyword_matched": keyword,
                            "replaces": m["ipc"],
                        })
        return results
