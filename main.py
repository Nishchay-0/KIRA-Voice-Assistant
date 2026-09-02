"""
main.py - Unified Hands-Free Voice Assistant & Realtime Web Automation System for Kira AI
-----------------------------------------------------------------------------------------
Features:
- Smart Time-Based Greeting on Startup (e.g. 'Good morning Sir! Kira AI is online and ready for your commands.')
- Universal Multilingual & Hinglish Support: Preserves Roman Hinglish song names ('play kya baat hai') as-is!
- Smart TV / Apple TV Style Media Engine: Plays songs, artists, playlists, and trending hits directly (youtube_engine.py)
- Automatic Hands-Free Startup: Launches directly into Voice Control & Web Automation
- Precise Intent Processing: Opens web applications (YouTube, WhatsApp, Instagram, Google, etc.) cleanly
- Ultimate Text-To-Speech (TTS) with Auto Language Detection & Edge Neural AI (text_to_speech.py)
- Voice Manager & Private Wake Keyword Integration (voice_manager.py & wake_word_config.json)
"""

import sys
import os
import time
import platform
from typing import Optional
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Import Core Engines
from speech_to_text import KiraSTT, load_wake_word, save_wake_word, translate_to_english
from text_to_speech import KiraTTS, Speak, Speak_Auto
from voice_manager import VoiceManager
from os_automation import execute_os_command
from web_automation import execute_web_command, WEB_SERVICES, normalize_hinglish_command
from youtube_engine import play_youtube_media, YouTubeEngine
from smart_calculator import execute_smart_calculation
from dependency_fixer import repair_plan_json


def print_banner():
    current_kw = load_wake_word()
    print(Fore.CYAN + "=========================================================================")
    print(Fore.CYAN + "   KIRA AI - UNIVERSAL MULTILINGUAL VOICE & WEB AUTOMATION ENGINE       ")
    print(Fore.CYAN + f"   OS: {platform.system()} | Private Wake Keyword: '{current_kw}'       ")
    print(Fore.CYAN + "=========================================================================")
    print(Fore.GREEN + "  - Universal Hinglish & Multilingual Support (Hindi, English, Hinglish, etc.)")
    print(Fore.GREEN + "  - Smart Media Engine: 'play music', 'play top punjabi songs', 'play kya baat hai'")
    print(Fore.GREEN + "  - Speak any command: 'open youtube', 'whatsapp kholo', 'google python'")
    print(Fore.GREEN + "  - Speak or type 'voice manager' to change voices, or 'set keyword' for wake word")
    print(Fore.LIGHTBLACK_EX + "  - Speak or type 'exit' / 'quit' / 'bye' to stop assistant\n")


def get_smart_greeting() -> str:
    """
    Generates a natural time-based smart greeting for program startup.
    Example: 'Good morning Sir! Kira AI is online and ready for your commands.'
    """
    hour = time.localtime().tm_hour
    if 5 <= hour < 12:
        return "Good morning Sir! Kira AI is online and ready for your commands."
    elif 12 <= hour < 17:
        return "Good afternoon Sir! Kira AI is online and ready for your commands."
    elif 17 <= hour < 22:
        return "Good evening Sir! Kira AI is online and ready for your commands."
    else:
        return "Hello Sir! Kira AI is online and ready for your commands."


def set_private_wake_keyword_menu():
    """
    Allows user to set or update their private wake word / activation keyword once.
    """
    current_kw = load_wake_word()
    print(Fore.YELLOW + "\n--- Set Private Wake Keyword / Activation Password ---")
    print(Fore.CYAN + f"Currently Active Wake Keyword: '{current_kw}'")
    print("This keyword acts as your private voice activation trigger.")
    
    new_kw = input(Fore.WHITE + "Enter new private wake keyword (e.g. 'kira', 'jarvis', 'computer') > ").strip()
    if new_kw:
        saved_kw = save_wake_word(new_kw)
        print(Fore.GREEN + f"Successfully updated private wake keyword to: '{saved_kw}'")
        tts = KiraTTS()
        tts.speak(f"Wake keyword updated to {saved_kw}.", wait=True)


def process_user_input(original_text: str, hinglish_text: str, english_text: str, tts: KiraTTS, stt: KiraSTT) -> bool:
    """
    Processes voice or text input across Web Automation, Smart Media Playback, Voice Settings, and Conversational Responses.
    Preserves Roman Hinglish song names ('play kya baat hai') as-is without unwanted translation.
    """
    raw_text = original_text or hinglish_text or english_text
    if not raw_text or not raw_text.strip():
        return False

    clean_raw = raw_text.lower().strip()
    clean_hinglish = (hinglish_text or "").lower().strip()
    clean_english = (english_text or "").lower().strip()
    combined_text = f"{clean_raw} {clean_hinglish} {clean_english}".strip()

    print(Fore.CYAN + f"\n[User Spoken Voice]: {raw_text}")

    if any(k in combined_text for k in ["fix environment", "install everything", "dependency fix", "repair dependencies"]):
        repair_json = repair_plan_json(request=combined_text)
        print(Fore.YELLOW + repair_json)
        tts.speak_auto("I generated a dependency repair plan. See the terminal for commands.", wait=True)
        return False

    # 1. Try Multi-Platform OS Automation Execution (open/close camera, take photo, settings, calculator, etc.)
    is_os, os_msg = execute_os_command(clean_raw)
    if not is_os and clean_hinglish:
        is_os, os_msg = execute_os_command(clean_hinglish)
    if not is_os and clean_english:
        is_os, os_msg = execute_os_command(clean_english)

    if is_os:
        print(Fore.GREEN + f"[OS Action Executed]: {os_msg}")
        tts.speak_auto(os_msg, wait=True)
        return False

    # 1b. Try Smart AI Calculator, Scientific Math & Deal Comparison Engine
    is_calc, calc_msg = execute_smart_calculation(clean_raw)
    if not is_calc and clean_hinglish:
        is_calc, calc_msg = execute_smart_calculation(clean_hinglish)
    if not is_calc and clean_english:
        is_calc, calc_msg = execute_smart_calculation(clean_english)

    if is_calc:
        print(Fore.GREEN + f"[Smart Calculator]: {calc_msg}")
        tts.speak_auto(calc_msg, wait=True)
        return False

    # 2. Assistant Shutdown / Exit Triggers (Requires explicit Kira/Assistant termination phrases or standalone exit)
    shutdown_phrases = [
        "shutdown kira", "close kira", "stop kira", "exit kira", "goodbye kira", "bye kira",
        "shutdown assistant", "close assistant", "stop assistant", "exit assistant", "goodbye assistant", "bye assistant"
    ]
    standalone_exits = ["exit", "quit", "goodbye", "bye"]

    is_shutdown = any(p in combined_text for p in shutdown_phrases) or clean_raw in standalone_exits or clean_hinglish in standalone_exits or clean_english in standalone_exits

    if is_shutdown:
        msg = "Goodbye Sir! Stopping Kira Assistant."
        print(Fore.YELLOW + f"[Kira]: {msg}")
        tts.speak_auto(msg, wait=True)
        return True

    # 3. Voice Manager Menu Trigger
    if any(k in combined_text for k in ["voice manager", "change voice", "select voice", "voice settings", "voices"]):
        print(Fore.GREEN + "\n>>> Opening Voice Manager...")
        vm = VoiceManager()
        vm.interactive_menu()
        return False

    # 4. Wake Keyword Setup Trigger
    if any(k in combined_text for k in ["set keyword", "wake word", "private password", "change keyword"]):
        set_private_wake_keyword_menu()
        return False

    # 5. Try Web & Smart Media Automation Execution (Test Original / Hinglish text FIRST to preserve song titles!)
    is_web, web_msg = execute_web_command(clean_raw)
    if not is_web and clean_hinglish:
        is_web, web_msg = execute_web_command(clean_hinglish)
    if not is_web and clean_english:
        is_web, web_msg = execute_web_command(clean_english)

    if is_web:
        print(Fore.GREEN + f"[Media/Web Action Executed]: {web_msg}")
        tts.speak_auto(web_msg, wait=True)
        return False

    # 5. Conversational Responses (When not a web command)
    if any(k in combined_text for k in ["hello", "namaste", "hi", "नमस्ते"]):
        response = "Namaste Sir! Main Kira hoon. Aap bataiye main aapki kya help kar sakti hoon?"
    elif any(k in combined_text for k in ["who are you", "kaun ho", "कौन"]):
        response = "Main Kira hoon, aapki AI voice assistant."
    elif any(k in combined_text for k in ["time", "samay", "waqt", "समय"]):
        current_time = time.strftime("%I:%M %p")
        response = f"Abhi time ho raha hai {current_time}."
    elif any(k in combined_text for k in ["weather", "mausam", "मौसम"]):
        response = "Aaj ka mausam saaf hai."
    else:
        response = f"Aapne kaha: '{raw_text}'."

    print(Fore.GREEN + f"[Kira Response]: {response}")
    tts.speak_auto(response, wait=True)
    return False


def process_command(text: str) -> bool:
    """
    Process a single voice or text command string and return True to continue or False to exit.
    """
    if not text:
        return True
    tts = KiraTTS()
    stt = KiraSTT()
    from speech_to_text import devanagari_to_hinglish, translate_to_english
    hinglish = devanagari_to_hinglish(text)
    english = translate_to_english(text)
    should_exit = process_user_input(text, hinglish, english, tts, stt)
    return not should_exit


def run_hands_free_kira():
    """
    Main Hands-Free Voice & Web Automation Engine Loop.
    Automatically active on program startup - no manual menu selection needed!
    """
    print_banner()

    stt = KiraSTT()
    tts = KiraTTS()

    # Time-based smart greeting on startup
    greeting = get_smart_greeting()
    print(Fore.GREEN + f"[Kira]: {greeting}")
    tts.speak_auto(greeting, wait=True)

    print(Fore.YELLOW + "🎤 [Hands-Free Voice Active]: Speak any command into microphone (or type below)...")

    def voice_callback(original: str, hinglish: str, english: str):
        should_exit = process_user_input(original, hinglish, english, tts, stt)
        if should_exit:
            sys.exit(0)

    try:
        # Continuous hands-free voice listener loop
        stt.listen_loop(callback=voice_callback)
    except KeyboardInterrupt:
        print(Fore.CYAN + "\nExiting Kira Assistant. Goodbye!")
        sys.exit(0)


def main():
    run_hands_free_kira()


if __name__ == "__main__":
    main()