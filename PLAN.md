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
| **Persistent Memory & Super Prompt** | Created `CLAUDE.md`, `PLAN.md`, `docs/known-issues.md`, `docs/constraints.md`, and `.env.example`. | Active |

---

## 🚧 Current Task in Progress
- **Setup & Enforcement of Enterprise Super Prompt Agreement**:
  - Establishing persistent memory files (`CLAUDE.md`, `PLAN.md`, `docs/known-issues.md`, `docs/constraints.md`, `.env.example`).
  - Enforcing zero-PII leakage policy and automated git sync protocols across all sessions.

---

## 🔮 Planned Future Steps
1. **Container Test Suite Expansion**: Expand pytest unit tests for containerized audio fallback verification.
2. **WebSocket Audio Streaming API**: Optional remote web client integration for browser-based voice control.
3. **Advanced Offline LLM Integration**: Add local Ollama/GGUF model provider support for conversational question answering.

---

## 📝 Session Handoff Note
- **Exact Changes Made**:
  1. Built multi-platform Docker container environment with Dockerfile, docker-compose.yml, entrypoint script, and cross-platform runners (`run_docker.ps1`, `run_docker.sh`, `DOCKER.md`).
  2. Created persistent memory architecture: `CLAUDE.md`, `PLAN.md`, `docs/known-issues.md`, `docs/constraints.md`, and `.env.example`.
  3. Verified 0 syntax errors across all modules.
- **Open Work**:
  - None. Baseline environment and persistent memory fully operational and synced.
- **Discovered Constraints**:
  - Windows host audio pass-through to Docker containers requires either PulseAudio over TCP or WSLg socket forwarding; `kira-cli` is the zero-dependency fallback.
