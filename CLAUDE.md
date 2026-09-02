> **AGENT DIRECTIVE:** Read this file fully before searching or scanning the codebase. Only search for something if it is not documented here. If you search for and discover new codebase structures, add what you found back into this file before finishing the task so future sessions do not need to repeat the search.

# CLAUDE.md - KIRA AI Voice Assistant

## 📌 Project Overview
- **Project Name:** KIRA Voice Assistant
- **Purpose:** Hands-free, multi-platform, multilingual AI voice assistant & web automation system supporting English, Hindi, and Roman Hinglish with zero-latency intent dispatch, media playback, OS automation, and neural text-to-speech.
- **Stack:** Python 3.10+, PyTorch, Whisper, SpeechRecognition, PyAudio, edge-tts, pyttsx3, Colorama, Docker & Docker Compose.

---

## 🔒 Non-Negotiable Hard Constraints (STRICT)
1. **Zero-PII Leakage Policy:** NEVER commit or push personal data (real names, emails, phone numbers, personal file paths like `C:\Users\<username>`, credentials, private keys, database dumps) to GitHub or remote repositories. Always use synthetic/anonymized data.
2. **Automated Git Sync:** Stage, commit (using descriptive conventional or user request messages), and push immediately to GitHub after completing working batches and command runs.
3. **Cross-Platform Abstraction:** Maintain OS-agnostic abstractions across Windows, macOS, Linux, and Docker containers without hardcoded platform locks.
4. **Clean Modular Architecture:** Maintain Single Responsibility Principle across modules (`speech_to_text.py`, `text_to_speech.py`, `voice_manager.py`, `web_automation.py`, `smart_calculator.py`, `os_automation.py`). Avoid monolithic single-file structures.
5. **Deterministic Testing & Verification:** Verify all Python files with compilation and unit checks before declaring completion.

---

## 🗺️ Module Map

| File / Component | Responsibility | Core Interfaces / Functions |
|---|---|---|
| `main.py` | Central entry point & hands-free event loop | `run_hands_free_kira()`, `process_user_input()`, `get_smart_greeting()` |
| `speech_to_text.py` | Multi-engine voice recognition & Hinglish preservation | `KiraSTT` (`listen_loop()`, `listen_once()`), `devanagari_to_hinglish()`, `load_wake_word()` |
| `text_to_speech.py` | Dual-engine neural & offline TTS audio playback | `KiraTTS` (`speak()`, `speak_auto()`), `Speak()`, `Speak_Auto()` |
| `voice_manager.py` | Edge Neural TTS catalog & voice configuration | `VoiceManager` (`interactive_menu()`, `list_voices()`, `set_voice()`) |
| `web_automation.py` | Intelligent browser dispatcher with fuzzy & phonetic matching | `execute_web_command()`, `fuzzy_match_service()`, `WEB_SERVICES` |
| `intent_classifier.py` | Intelligent intent parsing, entity resolution & confidence scoring | `IntentClassifier.classify()`, `IntentClassifier.resolve_service()` |
| `smart_calculator.py` | AST-based safe mathematical expression evaluator | `execute_smart_calculation()` |
| `os_automation.py` | Cross-platform OS application & settings controls | `execute_os_command()` |
| `youtube_engine.py` | Smart media & music streaming engine | `play_youtube_media()`, `YouTubeEngine` |
| `intent_classifier.py` | Intelligent intent parsing, entity resolution & confidence scoring | `IntentClassifier.classify()`, `IntentClassifier.resolve_service()` |
| `kira_intelligence.py` | Persistent SQLite memory, Q&A knowledge base, semantic search & local LLM | `KiraBrain`, `KiraMemory`, `KiraSemantic`, `get_brain()`, `ask_local_llm()` |
| `kira_memory.db` | SQLite file: `users`, `history`, `knowledge` tables — auto-created on first run | N/A |
| `chroma_db/` | ChromaDB vector index — auto-created when `chromadb` is installed (optional) | N/A |
| `dependency_fixer.py` | Platform- & Docker-aware dependency diagnostics | `repair_plan()`, `repair_plan_json()`, `_is_docker()` |
| `Dockerfile` | Multi-platform container definition with full audio stack | `python:3.11-slim`, ALSA, PortAudio, PulseAudio, espeak-ng |
| `docker-compose.yml` | Container orchestration (`kira`, `kira-cli`, `kira-test`) | Live audio pass-through, text-interactive CLI, persistent volume caching |

---

## ⚡ Execution Commands

### Local Environment
```powershell
# Run Hands-Free Assistant
python main.py

# Run Dependency Status Check
python dependency_fixer.py --request "status"

# Syntax Validation Check (all modules)
python -m py_compile main.py speech_to_text.py text_to_speech.py voice_manager.py web_automation.py intent_classifier.py kira_intelligence.py smart_calculator.py os_automation.py dependency_fixer.py

# Intelligence System Self-Test
python kira_intelligence.py

# Optional: Enable Semantic Layer
# pip install chromadb sentence-transformers  (uncomment lines in requirements.txt first)
```

### Docker Environment
```powershell
# Build Image
docker compose build  # (or: .\run_docker.ps1 build / ./run_docker.sh build)

# Interactive Text CLI Mode (No hardware mic required)
docker compose run --rm kira-cli  # (or: .\run_docker.ps1 cli / ./run_docker.sh cli)

# Live Audio Mode (Hardware Mic & Speaker Pass-Through)
docker compose run --rm kira  # (or: .\run_docker.ps1 run / ./run_docker.sh run)

# Run Automated Container Tests
docker compose run --rm kira-test  # (or: .\run_docker.ps1 test / ./run_docker.sh test)
```

---

## 📚 Living Memory Links
- **Roadmap & Milestones:** [`PLAN.md`](file:///c:/Users/saini/Downloads/OneDrive_2026-08-27/21072026/PLAN.md)
- **Known Issues & Bugs:** [`docs/known-issues.md`](file:///c:/Users/saini/Downloads/OneDrive_2026-08-27/21072026/docs/known-issues.md)
- **Hard Constraints & ADRs:** [`docs/constraints.md`](file:///c:/Users/saini/Downloads/OneDrive_2026-08-27/21072026/docs/constraints.md)
