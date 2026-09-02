# PLAN.md - KIRA Voice Assistant Living Roadmap

## 🎯 Active Goal
Implement and maintain the self-enforcing, enterprise-grade working agreement, persistent memory files, zero-PII security policies, and containerized multi-platform workflows for KIRA Voice Assistant.

---

## 🏆 Completed Milestones

| Milestone | Description | Date / Checkpoint |
|---|---|---|
| **Core Voice Assistant Engine** | Multilingual STT, Devanagari-to-Hinglish transliteration, and offline/neural TTS fallback architecture. | 2026-08-27 |
| **Web & Media Automation** | YouTube streaming engine, 1000+ top websites database, smart browser search dispatchers. | 2026-08-27 |
| **AST Smart Calculator** | Safe mathematical expression parser & calculator with zero eval security risk. | 2026-08-27 |
| **Docker Environment Adaptation** | Multi-platform Dockerfile, Docker Compose (`kira`, `kira-cli`, `kira-test`), ALSA/Pulse audio pass-through, and PowerShell/Bash runners. | `a0b7792` (2026-09-02) |
| **Persistent Memory & Super Prompt** | Created `CLAUDE.md`, `PLAN.md`, `docs/known-issues.md`, `docs/constraints.md`, and `.env.example`. | `d538ace` (2026-09-02) |
| **Intelligent Intent & Fuzzy Matching** | Created `intent_classifier.py`, fuzzy typo-tolerant `web_automation.py`, and neural Edge-TTS playback. | Active (2026-09-03) |

---

## 🚧 Current Task in Progress
- All major milestones complete. Repository is in a stable, fully-functional state.
- Working tree is clean and synced with `origin/master`.

---

## 🔮 Planned Future Steps
1. **Semantic Layer Activation**: Install `chromadb` + `sentence-transformers` to enable full embedding-based fuzzy command matching beyond the current difflib approach.
2. **Ollama LLM Integration**: Install Ollama + pull `llama3.2:3b` to enable offline, open-ended conversational answers for any question KIRA doesn't know.
3. **Container Test Suite Expansion**: Expand pytest unit tests covering `kira_intelligence.py` (memory CRUD, knowledge base seeding) and `intent_classifier.py` in Docker `kira-test`.
4. **WebSocket Audio Streaming API**: Optional remote web client for browser-based voice control over WebSocket.

---

## 📝 Session Handoff Note
- **Exact Changes Made (2026-09-03):**
  1. Created `intent_classifier.py` — structured intent + fuzzy service resolution engine.
  2. Rewrote `web_automation.py` — three-layer phonetic/alias/fuzzy dispatcher.
  3. Created `kira_intelligence.py` — SQLite memory, Q&A knowledge base, optional ChromaDB + Ollama.
  4. Updated `main.py` — full `KiraBrain` integration: name learning, Q&A teaching, LLM fallback, personalized greetings.
  5. Updated `requirements.txt`, `CLAUDE.md`, `PLAN.md`, `docs/known-issues.md`.
  6. Committed `3eabf36` and `a636132` to `origin/master`.
- **Open Work:** None. All intelligence layers fully operational.
- **Discovered Constraints:**
  - ChromaDB/SentenceTransformers are optional — core features work without them.
  - Ollama LLM requires host-level install — no pip dependency needed.
  - `kira_memory.db` persists across sessions in the project root.
