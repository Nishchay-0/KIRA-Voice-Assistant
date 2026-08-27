"""Optional text-to-speech support for Kira AI."""

import threading
from typing import Optional


class KiraTTS:
    """Speak text using pyttsx3 when available, or print it as a fallback."""

    def __init__(self, voice: Optional[str] = None, rate: Optional[int] = None,
                 engine: Optional[str] = None, language: Optional[str] = None,
                 voice_gender: Optional[str] = None, voice_id: Optional[str] = None):
        self.voice = voice or "en-IN-NeerjaNeural"
        self.voice_id = voice_id or self.voice
        self.rate = rate or 170
        self._engine = None
        try:
            import pyttsx3
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self.rate)
        except Exception:
            self._engine = None

    def speak(self, text: str, wait: bool = True) -> None:
        if not text:
            return
        if self._engine is not None:
            self._engine.say(text)
            if wait:
                self._engine.runAndWait()
            else:
                threading.Thread(target=self._engine.runAndWait, daemon=True).start()
            return
        print(f"[Kira]: {text}")

    def speak_auto(self, text: str, wait: bool = True) -> None:
        self.speak(text, wait=wait)


def Speak(text: str, wait: bool = True) -> None:
    KiraTTS().speak(text, wait=wait)


def Speak_Auto(text: str, wait: bool = True) -> None:
    KiraTTS().speak_auto(text, wait=wait)
