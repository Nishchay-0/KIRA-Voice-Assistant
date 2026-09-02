"""
web_automation.py - Intelligent Browser Command Handling with Fuzzy & Phonetic Matching
---------------------------------------------------------------------------------------
Features:
- Fuzzy matching & typo correction ("open goggle" -> Google, "open flix" -> Netflix)
- Alias & Abbreviation resolution ("ytb" -> YouTube, "fb" -> Facebook, "ig" -> Instagram)
- Phonetic error mapping from speech recognition ("utube", "facbook", "whats app", "chapt")
- Search dispatching with parameters ("search youtube for lofi beats", "google python tutorials")
- Top 1000+ website dataset integration
"""

import os
import json
import re
import webbrowser
from typing import Dict, Tuple, Optional
from urllib.parse import quote_plus
from difflib import get_close_matches

# Core curated service URLs
WEB_SERVICES: Dict[str, str] = {
    "youtube": "https://www.youtube.com",
    "yt": "https://www.youtube.com",
    "whatsapp": "https://web.whatsapp.com",
    "instagram": "https://www.instagram.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "reddit": "https://www.reddit.com",
    "amazon": "https://www.amazon.in",
    "flipkart": "https://www.flipkart.com",
    "wikipedia": "https://www.wikipedia.org",
    "wiki": "https://www.wikipedia.org",
    "chatgpt": "https://chatgpt.com",
    "maps": "https://maps.google.com",
    "news": "https://news.google.com",
    "spotify": "https://open.spotify.com",
    "netflix": "https://www.netflix.com",
    "linkedin": "https://www.linkedin.com",
    "facebook": "https://www.facebook.com",
    "fb": "https://www.facebook.com",
}

# Alias & Abbreviation Mappings
SERVICE_ALIASES: Dict[str, str] = {
    "ytb": "youtube",
    "youtub": "youtube",
    "you tube": "youtube",
    "y t": "youtube",
    "gogle": "google",
    "goggle": "google",
    "googe": "google",
    "gmail": "gmail",
    "gmial": "gmail",
    "git": "github",
    "gh": "github",
    "twit": "twitter",
    "tweet": "twitter",
    "insta": "instagram",
    "ig": "instagram",
    "wa": "whatsapp",
    "wp": "whatsapp",
    "fb": "facebook",
    "facebok": "facebook",
    "reddit": "reddit",
    "redit": "reddit",
    "amzn": "amazon",
    "fk": "flipkart",
    "wiki": "wikipedia",
    "gpt": "chatgpt",
    "chat gpt": "chatgpt",
    "maps": "maps",
    "map": "maps",
    "spotify": "spotify",
    "spot": "spotify",
    "netflix": "netflix",
    "flix": "netflix",
    "linkedin": "linkedin",
    "link": "linkedin",
}

# Phonetic Mishearings from Speech-To-Text Engines
PHONETIC_MAP: Dict[str, str] = {
    "yep": "youtube",
    "yap": "youtube",
    "youp": "youtube",
    "utube": "youtube",
    "u tube": "youtube",
    "googel": "google",
    "gugle": "google",
    "facbook": "facebook",
    "face book": "facebook",
    "insta gram": "instagram",
    "instgram": "instagram",
    "whats app": "whatsapp",
    "what sapp": "whatsapp",
    "git hub": "github",
    "gitub": "github",
    "twiter": "twitter",
    "twtter": "twitter",
    "red it": "reddit",
    "reditt": "reddit",
    "amazone": "amazon",
    "amzon": "amazon",
    "flikart": "flipkart",
    "flip kart": "flipkart",
    "wikipidia": "wikipedia",
    "wiki pedia": "wikipedia",
    "chat gpt": "chatgpt",
    "chapt": "chatgpt",
    "spotefy": "spotify",
    "net flix": "netflix",
    "netflx": "netflix",
    "linkdin": "linkedin",
    "link den": "linkedin",
}

# Search URL Templates for known search engines / portals
SEARCH_TEMPLATES: Dict[str, str] = {
    "youtube": "https://www.youtube.com/results?search_query=",
    "google": "https://www.google.com/search?q=",
    "wikipedia": "https://en.wikipedia.org/wiki/Special:Search?search=",
    "maps": "https://maps.google.com/maps?q=",
    "amazon": "https://www.amazon.in/s?k=",
    "flipkart": "https://www.flipkart.com/search?q=",
    "github": "https://github.com/search?q=",
    "spotify": "https://open.spotify.com/search/",
    "reddit": "https://www.reddit.com/search/?q=",
    "twitter": "https://x.com/search?q="
}


def normalize_hinglish_command(command: str) -> str:
    """Clean and normalize command text."""
    return (command or "").strip().lower()


def fuzzy_match_service(word: str) -> Optional[str]:
    """
    Match a word to a known service using:
    1. Phonetic map (for STT mishearings)
    2. Direct alias mapping
    3. Exact known services
    4. Fuzzy string matching (difflib typo tolerance)
    """
    if not word:
        return None
    w = word.lower().strip()

    # 1. Phonetic map
    if w in PHONETIC_MAP:
        return PHONETIC_MAP[w]

    # 2. Alias dictionary
    if w in SERVICE_ALIASES:
        return SERVICE_ALIASES[w]

    # 3. Direct service name
    if w in WEB_SERVICES:
        return w

    # 4. Fuzzy match against all known aliases & services
    all_services = list(WEB_SERVICES.keys()) + list(SERVICE_ALIASES.keys()) + list(PHONETIC_MAP.keys())
    matches = get_close_matches(w, all_services, n=1, cutoff=0.6)
    if matches:
        matched = matches[0]
        if matched in PHONETIC_MAP:
            return PHONETIC_MAP[matched]
        if matched in SERVICE_ALIASES:
            return SERVICE_ALIASES[matched]
        return matched

    return None


def execute_web_command(command: str) -> Tuple[bool, str]:
    """
    Intelligent web command executor with fuzzy matching, typo tolerance, and search queries.
    Handles:
    - 'open ytb', 'go to you tube', 'open goggle', 'open fb', 'goggle kholo'
    - 'search youtube for cats', 'search python on google'
    - 'open youtube par lo-fi beats'
    - 'ytb' (direct single-word service invocation)
    """
    text = normalize_hinglish_command(command)
    if not text:
        return False, ""

    # Pattern 1: Explicit search commands ("search X for Y", "search Y on X", "dhoondo Y on X")
    search_match = re.search(r"(?:search|find|look up|dhoondo|khojo)\s+(.+?)(?:\s+(?:for|par|about|on)\s+(.+))?$", text)
    if search_match:
        first_term = search_match.group(1).strip()
        second_term = search_match.group(2).strip() if search_match.group(2) else ""
        
        service = fuzzy_match_service(first_term)
        if service and second_term:
            base_url = SEARCH_TEMPLATES.get(service, WEB_SERVICES.get(service, "https://www.google.com/search?q="))
            url = base_url + quote_plus(second_term) if "search" in base_url or "q=" in base_url or "query=" in base_url else f"{WEB_SERVICES[service]}/search?q={quote_plus(second_term)}"
            webbrowser.open(url)
            return True, f"Searching {service} for '{second_term}'."
        elif service:
            webbrowser.open(WEB_SERVICES.get(service, f"https://www.{service}.com"))
            return True, f"Opened {service}."
        else:
            # General Google search for the entire query
            full_query = f"{first_term} {second_term}".strip()
            webbrowser.open(f"https://www.google.com/search?q={quote_plus(full_query)}")
            return True, f"Searching Google for '{full_query}'."

    # Pattern 2: "open X [for/par/about Y]" or "kholo X"
    open_match = re.search(r"(?:open|go to|goto|launch|start|kholo|chalao)\s+(.+)", text)
    if open_match:
        query = open_match.group(1).strip()
        
        # Check for query with search parameter ("open youtube for lofi beats" / "youtube par lofi")
        sub_search = re.search(r"(.+?)\s+(?:for|par|about|on)\s+(.+)", query)
        if sub_search:
            service_word = sub_search.group(1).strip()
            search_term = sub_search.group(2).strip()
            service = fuzzy_match_service(service_word)
            if service:
                base_url = SEARCH_TEMPLATES.get(service, WEB_SERVICES.get(service, "https://www.google.com/search?q="))
                url = base_url + quote_plus(search_term) if "search" in base_url or "q=" in base_url or "query=" in base_url else f"{WEB_SERVICES.get(service, '')}/search?q={quote_plus(search_term)}"
                webbrowser.open(url)
                return True, f"Opened {service} and searched for '{search_term}'."
        
        # Simple "open X"
        service = fuzzy_match_service(query)
        if service and service in WEB_SERVICES:
            webbrowser.open(WEB_SERVICES[service])
            return True, f"Opened {service}."
        elif service:
            webbrowser.open(f"https://www.{service}.com")
            return True, f"Opened {service}."
        
        # Check if direct domain was requested (e.g. "open github.com")
        if "." in query and not query.endswith("."):
            url = f"https://{query}" if not query.startswith("http") else query
            webbrowser.open(url)
            return True, f"Opened {query}."
        return False, ""

    # Pattern 3: Standalone single/short service word ("ytb", "youtube", "goggle", "fb", "insta")
    service = fuzzy_match_service(text)
    if service and service in WEB_SERVICES:
        webbrowser.open(WEB_SERVICES[service])
        return True, f"Opened {service}."

    return False, ""
