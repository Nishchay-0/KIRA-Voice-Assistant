# 🐳 KIRA Voice Assistant - Docker Environment Guide

This guide explains how to build, run, and manage **KIRA Voice Assistant** inside a fully containerized, cross-platform Docker environment.

---

## 🌟 Key Features of KIRA Docker Setup

- **Zero Host Dependency Conflicts**: Pre-installed Linux audio stack (`portaudio19-dev`, `python3-pyaudio`, `ffmpeg`, `alsa-utils`, `pulseaudio`, `espeak-ng`).
- **CPU-Optimized Neural AI**: Pre-configured PyTorch CPU build & Whisper model caching to optimize image build times and runtime speed.
- **Dual Runtime Modes**:
  - **Live Audio Mode (`kira`)**: Live hardware microphone & speaker pass-through via `/dev/snd` or PulseAudio.
  - **Text CLI Mode (`kira-cli`)**: Zero-hardware requirement interactive text mode for cloud servers, headless VPS, or WSL2.
- **Persistent Volume Support**: Automatically persists Whisper models, voice configs, wake words, and calculation histories.

---

## 🚀 Quick Start

### 1. Build the Docker Image

Using **PowerShell** (Windows):
```powershell
.\run_docker.ps1 build
```

Using **Bash** (Linux / macOS / WSL):
```bash
./run_docker.sh build
```

Or using **Docker Compose directly**:
```bash
docker compose build
```

---

## 🎮 Running KIRA in Docker

### Option A: Interactive Text CLI Mode (Recommended for quick use / Cloud / WSL)
No audio hardware pass-through required. KIRA accepts typed commands with automatic translation, calculator, web automations, and intelligent responses.

```powershell
# Windows PowerShell
.\run_docker.ps1 cli

# Linux / macOS
./run_docker.sh cli

# Direct Docker Compose
docker compose run --rm kira-cli
```

---

### Option B: Live Audio / Voice Mode (Microphone & Speaker Pass-Through)

#### 🐧 On Linux
Linux natively supports direct ALSA device forwarding (`/dev/snd`):
```bash
# Ensure current user is in the audio group
sudo usermod -aG audio $USER

# Run live audio assistant
./run_docker.sh run
# or
docker compose run --rm kira
```

#### 🪟 On Windows (WSL2 / Docker Desktop with PulseAudio)
To forward microphone & speaker from Windows to Docker:
1. Download and run **PulseAudio for Windows** or use WSLg PulseAudio socket.
2. In WSL2 / PowerShell, verify socket location or set `PULSE_SERVER=tcp:host.docker.internal:4713`.
3. Launch KIRA:
```powershell
docker compose run --rm -e PULSE_SERVER=tcp:host.docker.internal:4713 kira
```

#### 🍏 On macOS
macOS Docker Desktop can stream audio via PulseAudio:
```bash
brew install pulseaudio
pulseaudio --load="module-native-protocol-tcp auth-anonymous=1" --exit-idle-time=-1 --daemon
docker compose run --rm -e PULSE_SERVER=docker.for.mac.host.internal kira
```

---

## 🧪 Testing & Verification

Run automated environment checks and dependency verification inside the container:

```bash
# PowerShell
.\run_docker.ps1 test

# Bash
./run_docker.sh test

# Docker Compose
docker compose run --rm kira-test
```

---

## 🛠️ Docker Compose Service Reference

| Service Name | Description | Command Executed | Audio Pass-Through |
|---|---|---|---|
| `kira` | Main hands-free voice assistant | `python main.py` | ✅ Yes (`/dev/snd`, Pulse) |
| `kira-cli` | Text-interactive assistant | `python main.py` | ❌ No (Fallback Text CLI) |
| `kira-test` | Diagnostic and test runner | `python dependency_fixer.py --request status` | N/A |

---

## 📦 Persistent Volumes

- `kira-whisper-cache`: Persists downloaded OpenAI Whisper speech recognition models so they are not re-downloaded between container runs.
- Project root bind mount (`.:/app`): Synchronizes your custom `voice_config.json`, `wake_word_config.json`, `top_websites.json`, and database files directly with host workspace.

---

## 🔧 Useful Docker Commands

```bash
# Open an interactive shell inside the container
docker compose run --rm --entrypoint /bin/bash kira-cli

# View logs
docker compose logs -f

# Stop and clean up containers
docker compose down

# Clean images and cached volumes
docker compose down --rmi local --volumes
```
