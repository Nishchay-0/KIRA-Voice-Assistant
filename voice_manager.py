"""
voice_manager.py - Voice Discovery, Preview, Speed Control, and Selection System for Kira AI
---------------------------------------------------------------------------------------------
Allows users to browse, search, preview, and select from 300+ Microsoft Edge Neural AI voices (from BettyJJ Gist repo),
system voices, adjust speech speed (WPM), and save preferences for Kira AI assistant sessions.
"""

import sys
import os
import json
import asyncio
import logging
from typing import List, Dict, Optional, Tuple, Any, Callable

from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Safe import pyttsx3
try:
    import pyttsx3
    HAS_PYTTSX3 = True
except Exception:
    HAS_PYTTSX3 = False

# Safe import edge-tts
try:
    import edge_tts
    HAS_EDGE_TTS = True
except Exception:
    HAS_EDGE_TTS = False

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "voice_config.json")
GIST_VOICES_FILE = os.path.join(os.path.dirname(__file__), "edge_voices.json")

# Categorized Popular AI Voice Presets (Top choices for Hinglish, Hindi, English US/UK)
POPULAR_CATEGORIES = [
    {
        "category": "🔥 POPULAR HINGLISH VOICES (Indian Accent)",
        "voices": [
            {
                "id": "en-IN-NeerjaNeural",
                "name": "Kira (Hinglish Indian Female AI)",
                "gender": "female",
                "lang": "en-IN",
                "engine": "edge_tts",
                "personalities": ["Hinglish", "Natural", "Friendly"]
            },
            {
                "id": "en-IN-PrabhatNeural",
                "name": "Kira Male (Hinglish Indian Male AI)",
                "gender": "male",
                "lang": "en-IN",
                "engine": "edge_tts",
                "personalities": ["Hinglish", "Professional"]
            }
        ]
    },
    {
        "category": "🇮🇳 POPULAR HINDI VOICES",
        "voices": [
            {
                "id": "hi-IN-SwaraNeural",
                "name": "Kira (Hindi Female AI)",
                "gender": "female",
                "lang": "hi-IN",
                "engine": "edge_tts",
                "personalities": ["Hindi", "Expressive", "Warm"]
            },
            {
                "id": "hi-IN-MadhurNeural",
                "name": "Kira Male (Hindi Male AI)",
                "gender": "male",
                "lang": "hi-IN",
                "engine": "edge_tts",
                "personalities": ["Hindi", "Clear", "Narrator"]
            }
        ]
    },
    {
        "category": "🇬🇧 / 🇺🇸 POPULAR ENGLISH VOICES (Kira AI)",
        "voices": [
            {
                "id": "en-GB-RyanNeural",
                "name": "Kira (British Male AI)",
                "gender": "male",
                "lang": "en-GB",
                "engine": "edge_tts",
                "personalities": ["British", "Refined", "Kira"]
            },
            {
                "id": "en-US-AvaNeural",
                "name": "Kira (US Female AI)",
                "gender": "female",
                "lang": "en-US",
                "engine": "edge_tts",
                "personalities": ["US English", "Expressive"]
            },
            {
                "id": "en-US-AndrewNeural",
                "name": "Kira Male (US Male AI)",
                "gender": "male",
                "lang": "en-US",
                "engine": "edge_tts",
                "personalities": ["US English", "Conversational"]
            },
            {
                "id": "en-GB-ThomasNeural",
                "name": "Kira (British Formal Male AI)",
                "gender": "male",
                "lang": "en-GB",
                "engine": "edge_tts",
                "personalities": ["British", "Formal"]
            }
        ]
    }
]

# Flattened list for backwards compatibility
CURATED_VOICES = []
for cat in POPULAR_CATEGORIES:
    CURATED_VOICES.extend(cat["voices"])


class VoiceManager:
    """
    Manages system voice discovery, BettyJJ Gist Edge Neural voice discovery, speed control, selection, and config persistence.
    """
    def __init__(self):
        self._pyttsx3_engine = None
        if HAS_PYTTSX3:
            try:
                self._pyttsx3_engine = pyttsx3.init()
            except Exception:
                self._pyttsx3_engine = None

    def get_system_voices(self) -> List[Dict]:
        """
        Scans installed system voices on the local OS.
        """
        discovered = []
        if not self._pyttsx3_engine:
            return discovered

        try:
            voices = self._pyttsx3_engine.getProperty('voices')
            for index, voice in enumerate(voices):
                gender = "female" if "female" in voice.name.lower() or "zira" in voice.name.lower() else "male"
                discovered.append({
                    "index": index + 1,
                    "id": voice.id,
                    "name": f"System: {voice.name}",
                    "gender": gender,
                    "languages": getattr(voice, "languages", ["en"]),
                    "engine": "pyttsx3"
                })
        except Exception as e:
            logging.warning(f"Error fetching system voices: {e}")

        return discovered

    def get_gist_voices(self, filter_term: Optional[str] = None) -> List[Dict]:
        """
        Retrieves Edge Neural voices from the BettyJJ GitHub Gist repository catalog.
        """
        discovered = []
        if not os.path.exists(GIST_VOICES_FILE):
            return self.get_edge_voices(filter_term)

        alias_map = {
            "hinglish": "en-in",
            "hindi": "hi-in",
            "british": "en-gb",
            "uk": "en-gb",
            "us": "en-us",
            "american": "en-us",
            "indian": "en-in"
        }

        search_query = filter_term.lower() if filter_term else ""
        if search_query in alias_map:
            search_query = alias_map[search_query]

        try:
            if os.path.exists(GIST_VOICES_FILE):
                with open(GIST_VOICES_FILE, "r", encoding="utf-8") as f:
                    raw_voices = json.load(f)

                for v in raw_voices:
                    sn = v.get("id", "")
                    loc = v.get("lang", "")
                    gen = v.get("gender", "")
                    pers = v.get("personalities", [])
                    pers_str = ", ".join(pers) if pers else ""

                    if search_query:
                        combined = f"{sn} {loc} {gen} {pers_str}".lower()
                        if search_query not in combined:
                            continue

                    discovered.append(v)

            # Merge any new live Edge TTS voices not present in Gist file
            live_voices = self.get_edge_voices(filter_term)
            existing_ids = {v["id"] for v in discovered}
            for lv in live_voices:
                if lv["id"] not in existing_ids:
                    discovered.append(lv)

        except Exception as e:
            logging.warning(f"Error reading Gist voices file: {e}")
            return self.get_edge_voices(filter_term)

        return discovered

    def get_edge_voices(self, filter_term: Optional[str] = None) -> List[Dict]:
        """
        Fetch all Microsoft Edge Neural AI voices dynamically from edge-tts.
        """
        discovered = []
        if not HAS_EDGE_TTS:
            return discovered

        alias_map = {
            "hinglish": "en-in",
            "hindi": "hi-in",
            "british": "en-gb",
            "uk": "en-gb",
            "us": "en-us",
            "american": "en-us",
            "indian": "en-in"
        }

        search_query = filter_term.lower() if filter_term else ""
        if search_query in alias_map:
            search_query = alias_map[search_query]

        try:
            voices_raw = asyncio.run(edge_tts.list_voices())
            for v in voices_raw:
                short_name = v.get("ShortName", "")
                friendly_name = v.get("FriendlyName", "")
                gender = v.get("Gender", "Unknown").lower()
                locale = v.get("Locale", "")

                if search_query:
                    combined = f"{short_name} {friendly_name} {locale} {gender}".lower()
                    if search_query not in combined:
                        continue

                discovered.append({
                    "id": short_name,
                    "name": f"Edge Neural: {short_name} ({locale})",
                    "gender": gender,
                    "lang": locale,
                    "engine": "edge_tts"
                })
        except Exception as e:
            logging.warning(f"Error fetching Edge voices: {e}")

        return discovered

    def preview_voice(self, voice_info: Dict, sample_text: str = "Hello! I am ready to assist you.", rate: int = 180):
        """
        Play a voice audio preview sample with speed control.
        """
        print(Fore.CYAN + f"\n[Previewing]: {voice_info['name']} (Speed: {rate} WPM)...")
        
        from text_to_speech import KiraTTS
        
        engine_type = voice_info.get("engine", "edge_tts")
        lang = voice_info.get("lang", "en")
        gender = voice_info.get("gender", "female")
        voice_id = voice_info.get("id", "")

        tts = KiraTTS(engine=engine_type, language=lang, rate=rate, voice_gender=gender, voice_id=voice_id)
        tts.speak(sample_text, wait=True)

    def save_config(self, selected_voice: Dict, rate: Optional[int] = None):
        """
        Save active voice choice and speech rate to voice_config.json.
        """
        existing = self.load_config() or {}
        config = selected_voice.copy()
        
        # Preserve or update rate
        if rate is not None:
            config["rate"] = rate
        elif "rate" in existing:
            config["rate"] = existing["rate"]
        else:
            config["rate"] = 180

        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4)
            print(Fore.GREEN + f"\n[VoiceManager] Successfully saved settings: {config['name']} @ {config['rate']} WPM")
        except Exception as e:
            print(Fore.RED + f"[VoiceManager] Failed to save config: {e}")

    def set_speech_speed(self, rate: int):
        """
        Update speech rate (WPM) in configuration.
        """
        existing = self.load_config() or CURATED_VOICES[0].copy()
        existing["rate"] = max(80, min(400, rate))
        self.save_config(existing, rate=existing["rate"])

    def change_language_by_voice(self, command: str) -> Tuple[bool, str]:
        """
        Allows users to switch voice languages directly via voice input or text command.
        Example: 'change language to hindi', 'speak in hinglish', 'voice 3', 'set language 3'
        """
        if not command:
            return False, ""

        clean = command.lower().strip()

        preset_map = {
            "1": POPULAR_CATEGORIES[0]["voices"][0],
            "hinglish": POPULAR_CATEGORIES[0]["voices"][0],
            "2": POPULAR_CATEGORIES[0]["voices"][1],
            "hinglish male": POPULAR_CATEGORIES[0]["voices"][1],
            "3": POPULAR_CATEGORIES[1]["voices"][0],
            "hindi": POPULAR_CATEGORIES[1]["voices"][0],
            "hindi female": POPULAR_CATEGORIES[1]["voices"][0],
            "4": POPULAR_CATEGORIES[1]["voices"][1],
            "hindi male": POPULAR_CATEGORIES[1]["voices"][1],
            "5": POPULAR_CATEGORIES[2]["voices"][0],
            "british": POPULAR_CATEGORIES[2]["voices"][0],
            "english": POPULAR_CATEGORIES[2]["voices"][1],
            "us english": POPULAR_CATEGORIES[2]["voices"][1]
        }

        is_change_intent = any(k in clean for k in ["change language", "set language", "switch language", "speak in", "voice ", "bhasha badlo", "language "])
        
        if is_change_intent or clean in preset_map:
            for key, voice_obj in preset_map.items():
                if key in clean or clean == key:
                    self.save_config(voice_obj)
                    return True, f"Voice language updated to {voice_obj['name']}."

        return False, ""

    @staticmethod
    def load_config() -> Optional[Dict]:
        """
        Load active voice config from file.
        """
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return None

    def interactive_menu(self):
        """
        CLI interface to browse, search, test, choose from 300+ voices, and control speech speed.
        """
        print(Fore.CYAN + "=========================================================================")
        print(Fore.CYAN + "   Kira AI Voice Manager - Popular Voices, Catalog & Speed Control      ")
        print(Fore.CYAN + "=========================================================================")

        system_voices = self.get_system_voices()
        
        all_options = []
        option_num = 1

        # Render Popular Voice Categories at top
        for cat in POPULAR_CATEGORIES:
            print(Fore.YELLOW + f"\n--- {cat['category']} ---")
            for voice in cat["voices"]:
                v_copy = voice.copy()
                v_copy["option_num"] = option_num
                all_options.append(v_copy)
                traits = f" [{', '.join(voice['personalities'])}]" if 'personalities' in voice else ""
                print(f"[{option_num}] {voice['name']} ({voice['gender'].capitalize()}){traits}")
                option_num += 1

        if system_voices:
            print(Fore.YELLOW + "\n--- System Installed Voices ---")
            for sys_v in system_voices:
                v_copy = sys_v.copy()
                v_copy["option_num"] = option_num
                all_options.append(v_copy)
                print(f"[{option_num}] {sys_v['name']} ({sys_v['gender'].capitalize()})")
                option_num += 1

        # Automatically load full Gist voice catalog into options list
        gist_catalog = self.get_gist_voices()
        for g_v in gist_catalog:
            # Skip duplicates already in popular presets
            if any(opt['id'] == g_v['id'] for opt in all_options):
                continue
            g_copy = g_v.copy()
            g_copy["option_num"] = option_num
            all_options.append(g_copy)
            option_num += 1

        print(Fore.LIGHTBLACK_EX + f"\nLoaded total {len(all_options)} voice models into catalog.")

        print("\nCommands & How To Use:")
        print(Fore.GREEN + "  1. SELECT POPULAR VOICE: Type number from popular lists above (e.g. '1' for Hinglish Kira, '5' for British Kira)")
        print(Fore.GREEN + "  2. SEARCH VOICES:  Type 'gist <keyword>' or 'search <keyword>' (e.g. 'gist hinglish', 'gist hindi', 'gist british')")
        print(Fore.GREEN + "  3. BROWSE CATALOG: Type 'list' or 'page <num>' to view 25 voices per page (e.g. 'page 1', 'page 2')")
        print(Fore.GREEN + "  4. TEST / PREVIEW: Type any voice number (e.g. '1', '4', '15') to listen to a test sample!")
        print(Fore.GREEN + "  5. SELECT VOICE:   Type 'set <number>' (e.g. 'set 1') to set active voice for Kira!")
        print(Fore.GREEN + "  6. CHANGE SPEED:   Type 'speed <wpm>' (e.g. 'speed 150', 'speed 220', 'speed fast')")
        print("  - Type 'q' to quit")

        active_config = self.load_config()
        current_rate = active_config.get("rate", 180) if active_config else 180
        if active_config:
            print(Fore.GREEN + f"\nCurrently Active Voice: {active_config.get('name', 'Default')} (Speed: {current_rate} WPM)")

        current_page = 1
        page_size = 25
        max_pages = (len(all_options) + page_size - 1) // page_size

        while True:
            try:
                user_inp = input(Fore.WHITE + "\nSelect choice / command > ").strip().lower()
                if user_inp == "q":
                    break

                if user_inp in ("list", "all", "ls") or user_inp.startswith("page "):
                    if user_inp.startswith("page "):
                        p_str = user_inp.replace("page ", "").strip()
                        if p_str.isdigit():
                            current_page = max(1, min(max_pages, int(p_str)))
                    
                    start_idx = (current_page - 1) * page_size
                    end_idx = min(start_idx + page_size, len(all_options))
                    
                    print(Fore.YELLOW + f"\n--- Voice Catalog (Page {current_page}/{max_pages} - Showing [{start_idx + 1}-{end_idx}] of {len(all_options)}) ---")
                    for v in all_options[start_idx:end_idx]:
                        pers = f" [{', '.join(v['personalities'])}]" if v.get('personalities') else ""
                        print(f"[{v['option_num']}] {v['name']} ({v.get('gender', 'N/A').capitalize()}){pers}")

                    print(Fore.LIGHTBLACK_EX + f"Nav: Type 'page {current_page + 1}' for next page, or 'set <num>' to choose voice.")

                elif user_inp.startswith("gist") or user_inp.startswith("search") or user_inp.startswith("edge"):
                    filter_str = user_inp.replace("gist", "").replace("search", "").replace("edge", "").strip()
                    print(Fore.CYAN + f"\nSearching voices matching '{filter_str or 'all'}'...")
                    matched = self.get_gist_voices(filter_term=filter_str)
                    
                    if not matched:
                        print(Fore.RED + "No voices matched your search.")
                        continue
                    
                    print(Fore.YELLOW + f"\n--- Found {len(matched)} Voices Matching '{filter_str}' ---")
                    for mv in matched[:30]:
                        opt_num = next((opt['option_num'] for opt in all_options if opt['id'] == mv['id']), "N/A")
                        pers = f" [{', '.join(mv['personalities'])}]" if mv.get('personalities') else ""
                        print(f"[{opt_num}] {mv['name']} ({mv.get('gender', 'N/A').capitalize()}){pers}")
                    
                    if len(matched) > 30:
                        print(Fore.LIGHTBLACK_EX + f"... showing top 30 of {len(matched)} matches. Type number to preview, or 'set <num>' to select.")

                elif user_inp.startswith("speed "):
                    val = user_inp.replace("speed ", "").strip()
                    if val == "slow":
                        new_rate = 130
                    elif val == "normal":
                        new_rate = 180
                    elif val == "fast":
                        new_rate = 240
                    elif val.isdigit():
                        new_rate = int(val)
                    else:
                        print(Fore.RED + "Invalid speed format. Use e.g. 'speed 160' or 'speed fast'.")
                        continue
                    
                    self.set_speech_speed(new_rate)
                    current_rate = new_rate
                    print(Fore.GREEN + f"AI speech speed set to {new_rate} WPM.")

                elif user_inp.startswith("set "):
                    num_str = user_inp.replace("set ", "").strip()
                    if num_str.isdigit():
                        idx = int(num_str) - 1
                        if 0 <= idx < len(all_options):
                            chosen = all_options[idx]
                            self.save_config(chosen, rate=current_rate)
                            print(Fore.GREEN + f"Voice updated to: {chosen['name']}")
                            break
                        else:
                            print(Fore.RED + "Invalid voice number.")

                elif user_inp.isdigit():
                    idx = int(user_inp) - 1
                    if 0 <= idx < len(all_options):
                        target = all_options[idx]
                        self.save_config(target, rate=current_rate)
                        print(Fore.GREEN + f"Voice activated & saved to: {target['name']}")
                        self.preview_voice(target, f"Hello! Voice updated to {target['name']}.", rate=current_rate)
                        break
                    else:
                        print(Fore.RED + "Invalid choice number.")
                else:
                    print(Fore.RED + "Type a voice number to test, 'set <num>' to select, 'gist <keyword>' to search, or 'list' to browse pages.")

            except KeyboardInterrupt:
                print("\nExiting menu.")
                break


if __name__ == "__main__":
    vm = VoiceManager()
    vm.interactive_menu()
