"""
speech_to_text.py - Universal Multilingual Speech-To-Text Engine for Kira AI
----------------------------------------------------------------------------
Supports:
- Universal Multilingual Voice Input (Hindi, Hinglish, Spanish, French, German, Japanese, Chinese, etc.)
- Roman Hinglish & English Preservation (Does NOT translate song names like 'kya baat hai' into 'what's the matter'!)
- Automatic Backend Translation to English ONLY for non-Latin foreign scripts (Devanagari, CJK, etc.)
- High-Clarity Audio Calibration (Energy threshold tuning & 0.7s pause threshold for fast responsiveness)
- Custom Wake Word & Activation Keyword Persistence (wake_word_config.json)
- Silent timeout handling (eliminates 'listening timed out' error log spam)
"""

import sys
import os
import json
import platform
import logging
from typing import Optional, Callable, Dict

# Configure platform-independent PyAudio loading
def _setup_pyaudio():
    """
    Safely load PyAudio across Windows, macOS, and Linux.
    On Windows, attempts to use pyaudiowpatch for WASAPI support, with fallback to standard PyAudio.
    On non-Windows platforms, uses standard PyAudio directly.
    """
    is_windows = sys.platform.startswith("win32")
    
    if is_windows:
        try:
            import pyaudiowpatch as pyaudio
            sys.modules['pyaudio'] = pyaudio
            return True
        except ImportError:
            pass
            
    try:
        import pyaudio
        sys.modules['pyaudio'] = pyaudio
        return True
    except ImportError:
        logging.warning("PyAudio module could not be imported. Microphone input may fail.")
        return False

# Initialize PyAudio patch prior to speech_recognition import
_setup_pyaudio()

import speech_recognition as sr
from colorama import Fore, Style, init

# Initialize Colorama for terminal color rendering
init(autoreset=True)

# Safe import of mtranslate for backend English translation
try:
    from mtranslate import translate
    HAS_MTRANSLATE = True
except ImportError:
    HAS_MTRANSLATE = False

# Optional import of whisper for offline recognition
try:
    import whisper
    HAS_WHISPER = True
except ImportError:
    HAS_WHISPER = False


WAKE_WORD_FILE = os.path.join(os.path.dirname(__file__), "wake_word_config.json")
DEFAULT_WAKE_WORD = "kira"

# Devanagari to Roman Hinglish Transliteration Map
DEVANAGARI_MAP = {
    'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
    'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'nya',
    'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
    'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
    'प': 'p', 'फ': 'f', 'ब': 'b', 'भ': 'bh', 'म': 'm',
    'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v', 'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h',
    'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ee', 'उ': 'u', 'ऊ': 'oo', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au',
    'ा': 'a', 'ि': 'i', 'ी': 'ee', 'ु': 'u', 'ू': 'oo', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au', 'ं': 'n', '्': ''
}


COMMON_HINDI_WORDS = {
    "नमस्ते": "namaste",
    "नमस्कार": "namaskar",
    "किरा": "kira",
    "कौन": "kaun",
    "क्या": "kya",
    "समय": "samay",
    "वक्त": "waqt",
    "मौसम": "mausam",
    "चलाओ": "chalao",
    "बजाओ": "bajao",
    "खोलो": "kholo",
    "बंद": "band",
    "रोको": "roko"
}


def devanagari_to_hinglish(text: str) -> str:
    """
    Converts Devanagari Hindi text into Roman Hinglish script with common word overrides.
    Example: "नमस्ते किरा" -> "namaste kira"
    """
    if not text:
        return ""
    
    has_devanagari = any('\u0900' <= char <= '\u097F' for char in text)
    if not has_devanagari:
        return text

    # Try exact word overrides first
    words = text.split()
    converted_words = []
    for w in words:
        if w in COMMON_HINDI_WORDS:
            converted_words.append(COMMON_HINDI_WORDS[w])
        else:
            res = []
            for char in w:
                res.append(DEVANAGARI_MAP.get(char, char))
            converted_words.append("".join(res))

    return " ".join(converted_words)


def is_latin_hinglish(text: str) -> bool:
    """
    Checks if text is composed of standard Latin characters (Roman Hinglish / English).
    """
    if not text:
        return True
    return all(ord(char) < 128 or char.isspace() or char in ".,!?'\"-()" for char in text)


def translate_to_english(text: str) -> str:
    """
    Translates input text into English in the backend ONLY if it's in a non-Latin foreign script (Devanagari, CJK, etc.).
    Preserves Roman Hinglish and English song titles/phrases (e.g. 'kya baat hai', 'pasoori', 'brown munde') as-is!
    """
    if not text or not text.strip():
        return ""
    
    # If text is already in Roman Hinglish / ASCII, preserve as-is!
    if is_latin_hinglish(text):
        return text

    if HAS_MTRANSLATE:
        try:
            return translate(text, "en")
        except Exception:
            return text
    return text


def load_wake_word() -> str:
    """
    Loads saved wake word / activation keyword from wake_word_config.json.
    """
    if os.path.exists(WAKE_WORD_FILE):
        try:
            with open(WAKE_WORD_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                return cfg.get("wake_word", DEFAULT_WAKE_WORD).strip().lower()
        except Exception:
            pass
    return DEFAULT_WAKE_WORD


def save_wake_word(keyword: str) -> str:
    """
    Saves a custom private wake word / keyword to wake_word_config.json.
    """
    clean_kw = keyword.strip().lower()
    if not clean_kw:
        clean_kw = DEFAULT_WAKE_WORD

    cfg = {"wake_word": clean_kw}
    try:
        with open(WAKE_WORD_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
        print(Fore.GREEN + f"[KiraSTT] Custom Wake Keyword saved: '{clean_kw}'")
    except Exception as e:
        print(Fore.RED + f"[KiraSTT] Error saving wake keyword: {e}")
    return clean_kw


class KiraSTT:
    """
    Universal Multilingual Speech-To-Text manager for Kira AI with Hinglish Preservation & Backend Translation.
    """
    def __init__(
        self,
        input_language: str = "hi-IN",
        target_language: str = "en",
        engine: str = "google",
        pause_threshold: float = 1.2,
        dynamic_energy_threshold: bool = True
    ):
        self.input_language = input_language
        self.target_language = target_language
        self.engine = engine.lower()
        self.recognizer = sr.Recognizer()
        
        # High-Clarity Microphone Settings with Extended Listening Time
        self.recognizer.pause_threshold = pause_threshold
        self.recognizer.non_speaking_duration = 0.8
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = dynamic_energy_threshold
        self.recognizer.dynamic_energy_adjustment_damping = 0.15
        self.recognizer.dynamic_energy_ratio = 1.5
        self.recognizer.operation_timeout = None
        
        self.wake_word = load_wake_word()
        self.reload_config()

        # Load offline Whisper model if selected and available
        self.whisper_model = None
        if self.engine == "whisper" or self.engine == "auto":
            if HAS_WHISPER:
                try:
                    print(Fore.CYAN + "[KiraSTT] Loading local Whisper model (base)...")
                    self.whisper_model = whisper.load_model("base")
                    print(Fore.GREEN + "[KiraSTT] Whisper model loaded successfully.")
                except Exception as e:
                    print(Fore.YELLOW + f"[KiraSTT] Warning: Failed to load Whisper model ({e}). Defaulting to Google API.")
            else:
                if self.engine == "whisper":
                    print(Fore.YELLOW + "[KiraSTT] Warning: 'whisper' library not found. Falling back to Google API.")
                self.engine = "google"

    def reload_config(self):
        """
        Automatically sync input language and wake word from configuration files.
        """
        self.wake_word = load_wake_word()
        config_path = os.path.join(os.path.dirname(__file__), "voice_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    if cfg.get("lang"):
                        self.input_language = cfg.get("lang")
            except Exception:
                pass

    def is_wake_word_triggered(self, text: str) -> bool:
        """
        Checks if text contains the configured wake word (or default keywords 'kira').
        """
        if not text:
            return False
        clean = text.lower()
        return self.wake_word in clean or "kira" in clean

    def calibrate(self, source: sr.Microphone, duration: int = 1):
        """
        Calibrate microphone for ambient noise levels cleanly.
        """
        print(Fore.YELLOW + "[KiraSTT] Calibrating microphone for optimal clarity...", flush=True)
        self.recognizer.adjust_for_ambient_noise(source, duration=duration)
        print(Fore.GREEN + "[KiraSTT] Microphone calibrated cleanly!", flush=True)

    def _recognize_google(self, audio: sr.AudioData, lang: Optional[str] = None) -> str:
        target_lang = lang or self.input_language
        return self.recognizer.recognize_google(audio, language=target_lang).lower()

    def _recognize_whisper(self, audio: sr.AudioData) -> str:
        if not self.whisper_model:
            raise RuntimeError("Whisper model not initialized.")
        
        import tempfile
        wav_data = audio.get_wav_data()
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(wav_data)
            temp_path = f.name

        try:
            result = self.whisper_model.transcribe(temp_path)
            raw_text = result.get("text", "").strip().lower()
            return raw_text
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def listen_once(self, timeout: Optional[float] = None, phrase_time_limit: Optional[float] = None) -> Optional[Dict[str, str]]:
        """
        Listen for a single spoken sentence in ANY language and return raw + Hinglish + translated English dict.
        """
        self.reload_config()
        try:
            with sr.Microphone() as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

                recognized_text = ""
                if self.engine == "google":
                    try:
                        recognized_text = self._recognize_google(audio)
                    except sr.RequestError:
                        if self.whisper_model:
                            recognized_text = self._recognize_whisper(audio)
                elif self.engine == "whisper":
                    recognized_text = self._recognize_whisper(audio)
                elif self.engine == "auto":
                    try:
                        recognized_text = self._recognize_google(audio)
                    except Exception:
                        if self.whisper_model:
                            recognized_text = self._recognize_whisper(audio)

                if recognized_text:
                    hinglish_text = devanagari_to_hinglish(recognized_text)
                    translated_english = translate_to_english(recognized_text)
                    
                    return {
                        "original": recognized_text,
                        "hinglish": hinglish_text,
                        "english": translated_english
                    }

        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return None
        except Exception as e:
            logging.warning(f"[KiraSTT] Speech recognition warning: {e}")
            return None

    def listen(self, timeout: Optional[float] = None, phrase_time_limit: Optional[float] = None) -> Optional[str]:
        """
        Listen for a single spoken phrase and return recognized text string (with Hinglish conversion).
        """
        res = self.listen_once(timeout=timeout, phrase_time_limit=phrase_time_limit)
        if res:
            return res.get("hinglish") or res.get("original") or res.get("english")
        return None

    def listen_loop(self, callback: Callable[[str, str, str], None], stop_checker: Optional[Callable[[], bool]] = None):
        """
        Continuous listening loop: Preserves Roman Hinglish song names cleanly.
        """
        try:
            with sr.Microphone() as source:
                self.calibrate(source, duration=1)
                print(Fore.GREEN + f"\n=== Kira STT Active [Lang: '{self.input_language}'] (Press Ctrl+C to Stop) ===")
                
                while True:
                    if stop_checker and stop_checker():
                        break
                    
                    self.reload_config()
                    try:
                        audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=15)
                        
                        recognized_text = ""
                        if self.engine == "google":
                            try:
                                recognized_text = self._recognize_google(audio)
                            except sr.RequestError:
                                if self.whisper_model:
                                    recognized_text = self._recognize_whisper(audio)
                        elif self.engine == "whisper":
                            if self.whisper_model:
                                recognized_text = self._recognize_whisper(audio)
                        elif self.engine == "auto":
                            try:
                                recognized_text = self._recognize_google(audio)
                            except Exception:
                                if self.whisper_model:
                                    recognized_text = self._recognize_whisper(audio)

                        if recognized_text:
                            hinglish_text = devanagari_to_hinglish(recognized_text)
                            translated_english = translate_to_english(recognized_text)
                            
                            print("\r" + Fore.CYAN + f"[Spoken Speech Input]: {recognized_text}")
                            if hinglish_text != recognized_text:
                                print(Fore.LIGHTYELLOW_EX + f"[Hinglish]: {hinglish_text}")
                            
                            callback(recognized_text, hinglish_text, translated_english)
                            
                    except (sr.WaitTimeoutError, sr.UnknownValueError):
                        pass
                    except KeyboardInterrupt:
                        print(Fore.YELLOW + "\nStopping listener...")
                        break

        except Exception as e:
            print(Fore.YELLOW + f"[KiraSTT] Audio device unavailable: {e}")
            print(Fore.CYAN + "[KiraSTT] Switching to typed commands. Type 'exit' to stop.")
            while True:
                try:
                    typed_text = input(Fore.WHITE + "\nCommand > ").strip()
                except (EOFError, KeyboardInterrupt):
                    print(Fore.YELLOW + "\nStopping listener...")
                    break
                if not typed_text:
                    continue
                callback(typed_text, typed_text, typed_text)
                if typed_text.lower() in {"exit", "quit", "goodbye", "bye"}:
                    break


if __name__ == "__main__":
    print(Fore.CYAN + "==========================================")
    print(Fore.CYAN + f"   Kira AI STT Engine - OS: {platform.system()}")
    print(Fore.CYAN + "==========================================")
    
    stt_engine = KiraSTT()
    print(Fore.YELLOW + f"Active Wake Keyword: '{stt_engine.wake_word}'")
    res = stt_engine.listen_once()
    if res:
        print(Style.RESET_ALL + f"\nRaw Speech: {res['original']}")
        print(Style.RESET_ALL + f"Hinglish: {res['hinglish']}")
        print(Style.RESET_ALL + f"Backend English: {res['english']}")
    else:
        print(Style.RESET_ALL + "\nNo text captured.")
