"""Browser command handling for Kira AI."""

import re
import webbrowser
from typing import Dict, Tuple
from urllib.parse import quote_plus


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
}


def normalize_hinglish_command(command: str) -> str:
    return (command or "").strip()


def execute_web_command(command: str) -> Tuple[bool, str]:
    text = normalize_hinglish_command(command)
    lowered = text.lower()
    match = re.search(r"\b(?:open|go to|search|google|wikipedia|wiki)\s+([a-z0-9]+)(?:\s+(?:for|par)\s+(.+))?", lowered)
    if not match:
        return False, ""
    service = match.group(1)
    if service not in WEB_SERVICES:
        return False, ""
    url = WEB_SERVICES[service]
    query = match.group(2)
    if query:
        url += "/search?q=" + quote_plus(query)
    webbrowser.open(url)
    return True, f"Opened {service}."
