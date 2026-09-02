# Known Issues & Bug Tracking

This document tracks identified bugs, reproduction steps, confirmed fixes, and ongoing anomalies.

---

## 🪲 Tracked Issues & Fixes

### 1. Missing Microphones in Headless / Container Environments
- **Status:** FIXED / MITIGATED
- **Symptom:** `PyAudio` throws `IOError: No Default Input Device Available` or `ALSA lib pcm.c: unable to open slave` when running in Docker or without a connected sound card.
- **Reproduction:** Run `python main.py` inside a container without passing `/dev/snd`.
- **Confirmed Fix:** `speech_to_text.py` catches device initialization errors and automatically degrades gracefully to interactive typed CLI input (`[KiraSTT] Switching to typed commands`).
- **Container Solution:** Added `kira-cli` service in `docker-compose.yml` for instant text-based interaction without audio hardware.

---

### 2. OneDrive Download `_Error.txt` Artifacts
- **Status:** FIXED / CLEANED UP
- **Symptom:** Stray `*_Error.txt` files created during historical cloud drive synchronization interfered with git geometric repacks.
- **Reproduction:** `git commit` producing `fatal: bad object refs/heads_Error.txt`.
- **Confirmed Fix:** Removed stray `.git/*_Error.txt` files and added `*_Error.txt` to `.dockerignore` and `.gitignore`.

---

### 3. PyAudio Installation on Linux / Docker
- **Status:** FIXED
- **Symptom:** `pip install PyAudio` fails due to missing `portaudio.h`.
- **Confirmed Fix:** Included `portaudio19-dev` and `python3-pyaudio` system dependencies in `Dockerfile` and updated `dependency_fixer.py` to recognize `docker-linux` and provide `apt-get` commands.

---

### 4. Missing `Tuple` Typing Import in `voice_manager.py`
- **Status:** FIXED
- **Symptom:** `NameError: name 'Tuple' is not defined` when initializing `VoiceManager` during `main.py` startup.
- **Reproduction:** Running `python main.py` or `import voice_manager`.
- **Confirmed Fix:** Added `Tuple, Any, Callable` to typing imports in `voice_manager.py`. All modules now import with 100% pass rate.

---

### 5. Cross-Platform OS Automation & Windows WASAPI Audio Support
- **Status:** FIXED
- **Symptom:** OS commands only supported Windows `calc.exe` without macOS/Linux fallbacks; Windows WASAPI audio lacked dedicated `pyaudiowpatch` requirements declaration.
- **Reproduction:** Running OS commands on Linux/macOS or initializing WASAPI audio devices on Windows.
- **Confirmed Fix:** Enhanced `os_automation.py` with multi-platform handlers (`Calculator`, `Finder`/`File Explorer`, `TextEdit`/`Notepad`, `Terminal`) across Windows, macOS, and Linux; added `pyaudiowpatch` with `sys_platform == 'win32'` marker to `requirements.txt`; added `stt.listen()` string wrapper and `process_command(text)` in `main.py`.

---

### 6. Silent TTS Playback & Multi-Language STT UnknownValueError
- **Status:** FIXED
- **Symptom:** Assistant seemed unresponsive when spoken to in English while Hindi was active; `pyttsx3` COM engine multiple-instantiation caused audio playback lockups; typing in terminal was blocked during microphone listening.
- **Reproduction:** Speaking English to Google STT in `hi-IN` mode or attempting to type while microphone is active.
- **Confirmed Fix:**
  1. Connected Microsoft Edge Neural TTS with native Windows MCI / macOS afplay / Linux mpg123 audio player, with singleton COM pyttsx3 fallback.
  2. Implemented automatic cross-language recognition fallback in Google STT (`hi-IN` -> `en-IN` -> `en-US`).
  3. Added real-time visual terminal indicators (`🎤 [Listening...]`, `⚡ [Processing...]`).
  4. Added concurrent background keyboard listener thread so users can **both** speak and type commands in real-time.
