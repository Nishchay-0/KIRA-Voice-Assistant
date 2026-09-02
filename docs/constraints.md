# Architecture Constraints & Decision Records (ADRs)

This document formalizes hard rules, technical constraints, and settled architecture decisions for KIRA Voice Assistant.

---

## 🔒 Hard Constraints

1. **Zero Personal Identifiable Information (PII) Policy:**
   - Real names, personal emails, personal filesystem directories (e.g., `C:\Users\<username>`), private keys, and live database dumps must NEVER be committed or pushed to any repository.
   - All tests, fixtures, logs, and mocks must strictly use synthetic or sanitized data.

2. **Cross-Platform Compatibility:**
   - Zero platform lock-in. All core engines must run seamlessly on Windows, macOS, Linux, and Docker Linux containers.

3. **No Unsafe Code Execution:**
   - Never use `eval()` or `exec()` for parsing math or user expressions. All arithmetic evaluation must strictly use Abstract Syntax Tree (`ast.parse`) with whitelisted operators (`smart_calculator.py`).

4. **Preservation of Roman Hinglish Intent:**
   - Multi-lingual inputs containing Roman Hinglish song/video queries (e.g., `play kya baat hai`) must NOT be forcibly translated into English (e.g., `what's the matter`). Original text must be prioritized for media search.

---

## 🏛️ Architecture Decision Records (ADRs)

### ADR 001: Multi-Service Docker Architecture for Audio vs. Headless CLI
- **Context:** Forwarding microphone and speaker hardware into Docker containers differs across Linux (`/dev/snd`), Windows (WSLg / PulseAudio TCP), and macOS. Running on remote cloud servers has no audio hardware.
- **Decision:** Provide two distinct Compose services:
  1. `kira`: Live audio with `/dev/snd` and PulseAudio mapping.
  2. `kira-cli`: Text-interactive CLI mode with zero hardware dependencies.
- **Consequences:** Eliminates runtime crashes on machines without audio forwarding while preserving high-fidelity audio capabilities where available.

### ADR 002: Dual-Engine STT and TTS Fallback
- **Context:** High-quality neural voices (Edge TTS) and online STT (Google Speech Recognition) require active internet access; local speech synthesis (pyttsx3) and Whisper work completely offline.
- **Decision:** Implement automatic graceful degradation:
  - STT: Google STT (online fast) -> Whisper (offline CPU/GPU model) -> Interactive Typed CLI (offline/headless fallback).
  - TTS: Edge Neural TTS -> pyttsx3 offline engine -> Colorized terminal print fallback.
- **Consequences:** KIRA remains operational under all network, hardware, and deployment conditions.
