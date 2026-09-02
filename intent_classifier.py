"""
intent_classifier.py - Intelligent Lightweight Intent Classification for Kira AI
---------------------------------------------------------------------------------
Provides intent parsing, service extraction, entity resolution, and confidence scoring
across Web Navigation, Media Playback, OS Operations, Calculations, and System Triggers.
"""

import re
from typing import Dict, Any, Optional
from difflib import get_close_matches


class IntentClassifier:
    """
    Intelligent rule-based, phonetic, and fuzzy scoring intent classifier.
    """

    INTENTS: Dict[str, Dict] = {
        "system": {
            "keywords": [
                "exit", "quit", "bye", "goodbye", "shutdown", "stop", "close assistant",
                "stop kira", "band karo", "alvida"
            ]
        },
        "voice_settings": {
            "keywords": [
                "voice manager", "change voice", "select voice", "voice settings",
                "voices", "awaz badlo", "set keyword", "wake word", "private password"
            ]
        },
        "calculator": {
            "keywords": [
                "calculate", "math", "compute", "what is", "plus", "minus",
                "multiply", "divide", "percent", "hisab", "jodo", "ghatao"
            ]
        },
        "play_media": {
            "keywords": [
                "play", "listen", "song", "music", "gana", "video", "track", "sunao", "bajao", "chalao"
            ]
        },
        "open_web": {
            "keywords": ["open", "go to", "goto", "launch", "start", "navigate", "kholo", "chalao"],
            "services": [
                "youtube", "google", "github", "whatsapp", "instagram",
                "twitter", "x", "reddit", "amazon", "flipkart", "wikipedia",
                "chatgpt", "maps", "news", "spotify", "netflix", "linkedin",
                "facebook", "gmail"
            ]
        },
        "search": {
            "keywords": ["search", "find", "look up", "query", "dhoondo", "khojo", "google"]
        }
    }

    PHONETIC_AND_ALIASES: Dict[str, str] = {
        "ytb": "youtube",
        "yt": "youtube",
        "youtub": "youtube",
        "you tube": "youtube",
        "y t": "youtube",
        "utube": "youtube",
        "u tube": "youtube",
        "yep": "youtube",
        "yap": "youtube",
        "gogle": "google",
        "goggle": "google",
        "googe": "google",
        "gugle": "google",
        "fb": "facebook",
        "facebok": "facebook",
        "facbook": "facebook",
        "insta": "instagram",
        "ig": "instagram",
        "instgram": "instagram",
        "wa": "whatsapp",
        "wp": "whatsapp",
        "whats app": "whatsapp",
        "twit": "twitter",
        "tweet": "twitter",
        "twiter": "twitter",
        "git": "github",
        "gh": "github",
        "gitub": "github",
        "amzn": "amazon",
        "amazone": "amazon",
        "fk": "flipkart",
        "flikart": "flipkart",
        "wiki": "wikipedia",
        "wikipidia": "wikipedia",
        "gpt": "chatgpt",
        "chat gpt": "chatgpt",
        "chapt": "chatgpt",
        "spot": "spotify",
        "spotefy": "spotify",
        "flix": "netflix",
        "net flix": "netflix",
        "netflx": "netflix",
        "link": "linkedin",
        "linkdin": "linkedin",
        "gmial": "gmail"
    }

    @classmethod
    def resolve_service(cls, word: str) -> Optional[str]:
        """Resolve a service name with exact, phonetic alias, and fuzzy matching."""
        if not word:
            return None
        w = word.lower().strip()
        if w in cls.PHONETIC_AND_ALIASES:
            return cls.PHONETIC_AND_ALIASES[w]
        if w in cls.INTENTS["open_web"]["services"]:
            return w

        # Fuzzy matching
        all_known = list(cls.INTENTS["open_web"]["services"]) + list(cls.PHONETIC_AND_ALIASES.keys())
        matches = get_close_matches(w, all_known, n=1, cutoff=0.6)
        if matches:
            matched = matches[0]
            return cls.PHONETIC_AND_ALIASES.get(matched, matched)
        return None

    @classmethod
    def classify(cls, text: str) -> Dict[str, Any]:
        """
        Classify input text into structured intent, target service/query, and confidence score.
        Returns: {
            "intent": "system" | "voice_settings" | "calculator" | "play_media" | "open_web" | "search" | "unknown",
            "service": str or None,
            "query": str or None,
            "confidence": float
        }
        """
        if not text:
            return {"intent": "unknown", "service": None, "query": None, "confidence": 0.0}

        cleaned = text.lower().strip()

        # 1. System Shutdown Triggers
        if any(re.search(rf"\b{re.escape(k)}\b", cleaned) for k in cls.INTENTS["system"]["keywords"]) or cleaned in ["exit", "quit", "bye"]:
            return {"intent": "system", "service": None, "query": None, "confidence": 1.0}

        # 2. Voice Settings & Keywords
        if any(k in cleaned for k in cls.INTENTS["voice_settings"]["keywords"]):
            return {"intent": "voice_settings", "service": None, "query": cleaned, "confidence": 0.95}

        # 3. Math & Calculation
        calc_match = re.search(r"(?:calculate|compute|what is|hisab)?\s*([0-9+\-*/%.() ]+)\s*\??", cleaned)
        if calc_match and any(op in calc_match.group(1) for op in ["+", "-", "*", "/", "%"]):
            return {"intent": "calculator", "service": None, "query": calc_match.group(1).strip(), "confidence": 0.95}

        # 4. Media & Music Playback
        if any(re.search(rf"\b{re.escape(k)}\b", cleaned) for k in ["play", "bajao", "chalao", "sunao"]):
            query = re.sub(r"\b(play|bajao|chalao|sunao|music|song|gana|track|on youtube|par)\b", "", cleaned).strip()
            return {"intent": "play_media", "service": "youtube", "query": query or "music", "confidence": 0.9}

        # 5. Search Commands (e.g. "search youtube for lofi", "search cats on google")
        search_match = re.search(r"(?:search|find|look up|dhoondo)\s+(.+?)(?:\s+(?:for|par|about|on)\s+(.+))?$", cleaned)
        if search_match:
            first_part = search_match.group(1).strip()
            second_part = search_match.group(2).strip() if search_match.group(2) else ""
            svc = cls.resolve_service(first_part)
            if svc and second_part:
                return {"intent": "search", "service": svc, "query": second_part, "confidence": 0.95}
            elif svc:
                return {"intent": "open_web", "service": svc, "query": None, "confidence": 0.9}
            else:
                query = f"{first_part} {second_part}".strip()
                return {"intent": "search", "service": "google", "query": query, "confidence": 0.85}

        # 6. Web Navigation ("open ytb", "go to you tube", "goggle kholo", "fb")
        open_match = re.search(r"(?:open|go to|goto|launch|start|kholo)\s+(.+)", cleaned)
        if open_match:
            target = open_match.group(1).strip()
            # check for "open youtube for lofi"
            sub_search = re.search(r"(.+?)\s+(?:for|par|about)\s+(.+)", target)
            if sub_search:
                svc = cls.resolve_service(sub_search.group(1))
                if svc:
                    return {"intent": "search", "service": svc, "query": sub_search.group(2).strip(), "confidence": 0.95}
            svc = cls.resolve_service(target)
            if svc:
                return {"intent": "open_web", "service": svc, "query": None, "confidence": 0.95}

        # 7. Single word service name ("ytb", "youtube", "goggle", "fb")
        direct_svc = cls.resolve_service(cleaned)
        if direct_svc:
            return {"intent": "open_web", "service": direct_svc, "query": None, "confidence": 0.9}

        return {"intent": "unknown", "service": None, "query": cleaned, "confidence": 0.0}
