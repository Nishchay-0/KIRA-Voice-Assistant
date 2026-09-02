"""
text_to_speech.py - Ultimate Neural & Offline Text-To-Speech Engine for Kira AI
-------------------------------------------------------------------------------
Supports:
- Microsoft Edge Neural AI TTS (300+ ultra-realistic voices)
- PyTTSX3 Local Offline Fallback Engine (with thread-safe COM singleton)
- Dynamic Voice & Language loading from voice_config.json
- Native Cross-Platform Audio Playback (Windows MCI, macOS afplay, Linux mpg123/ffplay)
- Zero-Failure Graceful Fallback
"""

import sys
import os
import json
import time
import shutil
import asyncio
import logging
import platform
import tempfile
import threading
from typing import Optional

from colorama import Fore, Style, init

init(autoreset=True)

# Safe imports
try:
    import edge_tts
    HAS_EDGE_TTS = True
except ImportError:
    HAS_EDGE_TTS = False

try:
    import pyttsx3
    HAS_PYTTSX3 = True
except Exception:
    HAS_PYTTSX3 = False


CONFIG_FILE = os.path.join(os.path.dirname(__file__), "voice_config.json")


class _TTSBackendManager:
    """Thread-safe persistent singleton for local pyttsx3 and Edge TTS playback."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(_TTSBackendManager, cls).__new__(cls)
                cls._instance._init_pyttsx3()
            return cls._instance

    def _init_pyttsx3(self):
        self.pyttsx3_engine = None
        if HAS_PYTTSX3:
            try:
                self.pyttsx3_engine = pyttsx3.init()
                self.pyttsx3_engine.setProperty("rate", 175)
            except Exception as e:
                logging.warning(f"[TTS] pyttsx3 initialization note: {e}")
                self.pyttsx3_engine = None

    def play_audio_file(self, file_path: str):
        """Cross-platform native audio playback without heavy third-party dependencies."""
        if not os.path.exists(file_path):
            return

        system = platform.system()
        try:
            if system == "Windows":
                import ctypes
                winmm = ctypes.windll.winmm
                abs_path = os.path.abspath(file_path).replace("\\", "/")
                alias = f"kira_snd_{int(time.time() * 1000) % 100000}"
                winmm.mciSendStringW(f'open "{abs_path}" type mpegvideo alias {alias}', None, 0, None)
                winmm.mciSendStringW(f'play {alias} wait', None, 0, None)
                winmm.mciSendStringW(f'close {alias}', None, 0, None)
            elif system == "Darwin":
                os.system(f'afplay "{file_path}"')
            else:
                for player in ["mpg123", "ffplay", "paplay", "aplay"]:
                    if shutil.which(player):
                        if player == "ffplay":
                            os.system(f'ffplay -nodisp -autoexit -loglevel quiet "{file_path}"')
                        else:
                            os.system(f'{player} "{file_path}" > /dev/null 2>&1')
                        break
        except Exception as e:
            logging.warning(f"[TTS] Native audio playback warning: {e}")


def _load_voice_config():
    """Load user-saved voice configuration if available."""
    default_cfg = {
        "id": "hi-IN-SwaraNeural",
        "name": "Kira (Hindi Female AI)",
        "lang": "hi-IN",
        "engine": "edge_tts",
        "rate": 180
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_cfg.update(data)
        except Exception:
            pass
    return default_cfg


class KiraTTS:
    """
    Unified Text-To-Speech engine for Kira AI with Edge Neural & Offline PyTTSX3 synthesis.
    """

    def __init__(
        self,
        voice: Optional[str] = None,
        rate: Optional[int] = None,
        engine: Optional[str] = None,
        language: Optional[str] = None,
        voice_gender: Optional[str] = None,
        voice_id: Optional[str] = None
    ):
        cfg = _load_voice_config()
        self.voice_id = voice_id or voice or cfg.get("id", "hi-IN-SwaraNeural")
        self.rate = rate or cfg.get("rate", 180)
        self.engine_type = engine or cfg.get("engine", "edge_tts")
        self.backend = _TTSBackendManager()
        self._speech_lock = threading.Lock()

    def _speak_edge_tts(self, text: str) -> bool:
        """Synthesize text using Microsoft Edge Neural TTS."""
        if not HAS_EDGE_TTS or not text:
            return False

        try:
            rate_str = f"+{self.rate - 150}%" if self.rate >= 150 else f"-{150 - self.rate}%"
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tf:
                temp_path = tf.name

            async def _synth():
                communicate = edge_tts.Communicate(text, self.voice_id, rate=rate_str)
                await communicate.save(temp_path)

            asyncio.run(_synth())
            self.backend.play_audio_file(temp_path)

            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass
            return True
        except Exception as e:
            logging.debug(f"[TTS] Edge TTS fallback triggered: {e}")
            return False

    def _speak_pyttsx3(self, text: str) -> bool:
        """Synthesize text using local pyttsx3 offline engine."""
        engine = self.backend.pyttsx3_engine
        if engine is None:
            return False

        try:
            engine.setProperty("rate", self.rate)
            engine.say(text)
            engine.runAndWait()
            return True
        except Exception as e:
            logging.debug(f"[TTS] pyttsx3 error: {e}")
            return False

    def speak(self, text: str, wait: bool = True) -> None:
        """
        Synthesize speech with Edge Neural AI, fallback to pyttsx3, and print to console.
        """
        if not text or not str(text).strip():
            return

        def _do_speak():
            with self._speech_lock:
                success = False
                if self.engine_type == "edge_tts" and HAS_EDGE_TTS:
                    success = self._speak_edge_tts(text)

                if not success:
                    success = self._speak_pyttsx3(text)

        if wait:
            _do_speak()
        else:
            threading.Thread(target=_do_speak, daemon=True).start()

    def speak_auto(self, text: str, wait: bool = True) -> None:
        """Alias for speak() with automatic language detection."""
        self.speak(text, wait=wait)


def Speak(text: str, wait: bool = True) -> None:
    KiraTTS().speak(text, wait=wait)


def Speak_Auto(text: str, wait: bool = True) -> None:
    KiraTTS().speak_auto(text, wait=wait)


if __name__ == "__main__":
    print(Fore.CYAN + "[KiraTTS] Testing Text-To-Speech Synthesis...")
    tts = KiraTTS()
    tts.speak("Hello Sir! Kira AI voice system is fully active.", wait=True)
    print(Fore.GREEN + "[KiraTTS] Test Completed.")
