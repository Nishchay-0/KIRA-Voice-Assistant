"""YouTube playback helpers."""

import webbrowser
from urllib.parse import quote_plus


class YouTubeEngine:
    def play(self, query: str) -> str:
        webbrowser.open("https://www.youtube.com/results?search_query=" + quote_plus(query))
        return f"Playing {query} on YouTube."


def play_youtube_media(query: str) -> str:
    return YouTubeEngine().play(query)
