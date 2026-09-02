"""Generate platform-aware repair plans for KIRA dependencies."""

import importlib.util
import json
import os
import platform
import re
from typing import Any, Dict, List


DEPENDENCY_MODULES = {
    "SpeechRecognition": "speech_recognition",
    "PyAudio": "pyaudio",
    "torch": "torch",
    "openai-whisper": "whisper",
    "pyttsx3": "pyttsx3",
    "edge-tts": "edge_tts",
    "mtranslate": "mtranslate",
}


def _is_docker() -> bool:
    """Check if currently running inside a Docker container."""
    return os.path.exists("/.dockerenv") or os.environ.get("CONTAINER", "") == "docker"


def _platform_name() -> str:
    if _is_docker():
        return "docker-linux"
    system = platform.system().lower()
    if system.startswith("win"):
        return "windows"
    if system == "darwin":
        return "macos"
    return "linux"


def _base_commands(os_platform: str) -> List[str]:
    if os_platform == "docker-linux":
        return [
            "pip install --upgrade pip",
            "pip install -r requirements.txt",
        ]
    if os_platform == "windows":
        return [
            "py -3.13 -m venv .venv",
            ".venv\\Scripts\\python.exe -m pip install --upgrade pip",
            ".venv\\Scripts\\python.exe -m pip install -r requirements.txt",
        ]
    return [
        "python3 -m venv .venv",
        "source .venv/bin/activate",
        "python -m pip install --upgrade pip",
        "python -m pip install -r requirements.txt",
    ]


def _pyaudio_commands(os_platform: str) -> List[str]:
    if os_platform == "docker-linux":
        return [
            "apt-get update && apt-get install -y portaudio19-dev python3-pyaudio",
            "pip install PyAudio",
        ]
    if os_platform == "windows":
        return [
            "py -3.13 -m venv .venv",
            ".venv\\Scripts\\python.exe -m pip install --upgrade pip",
            ".venv\\Scripts\\python.exe -m pip install PyAudio",
        ]
    if os_platform == "macos":
        return ["brew install portaudio", "python3 -m venv .venv", "source .venv/bin/activate", "python -m pip install PyAudio"]
    return [
        "sudo apt-get update",
        "sudo apt-get install -y portaudio19-dev python3-pyaudio",
        "python3 -m venv .venv",
        "source .venv/bin/activate",
        "python -m pip install PyAudio",
    ]


def dependency_status() -> Dict[str, Any]:
    missing = [package for package, module in DEPENDENCY_MODULES.items()
               if importlib.util.find_spec(module) is None]
    return {"ready": not missing, "missing": missing}


def repair_plan(error_text: str = "", request: str = "") -> Dict[str, Any]:
    os_platform = _platform_name()
    text = f"{error_text} {request}".lower()
    status = dependency_status()
    commands: List[str] = []

    if "pyaudio" in text or "portaudio" in text or "microphone" in text:
        commands.extend(_pyaudio_commands(os_platform))
    elif "torch" in text or "whisper" in text:
        if os_platform == "docker-linux":
            commands.extend([
                "pip install torch --index-url https://download.pytorch.org/whl/cpu",
                "pip install openai-whisper",
            ])
        else:
            interpreter = "py -3.13" if os_platform == "windows" else "python3"
            commands.extend([
                f"{interpreter} -m pip install torch --index-url https://download.pytorch.org/whl/cpu",
                f"{interpreter} -m pip install openai-whisper",
            ])
    elif "modulenotfounderror" in text or "importerror" in text or "missing" in text:
        commands.extend(_base_commands(os_platform))
    elif any(word in text for word in ("install everything", "fix environment")):
        commands.extend(_base_commands(os_platform))

    if not commands and status["missing"]:
        commands.extend(_base_commands(os_platform))

    if commands:
        return {
            "status": "FIX_REQUIRED",
            "detected_os": os_platform,
            "fix_commands": commands,
            "execution_payload": None,
            "message": "Dependencies need repair. Run the listed commands, then restart KIRA.",
        }

    return {
        "status": "READY",
        "detected_os": os_platform,
        "fix_commands": [],
        "execution_payload": {
            "intent": "ready",
            "target": "kira",
            "response_text": "KIRA dependencies are ready.",
        },
        "message": "KIRA dependencies are ready.",
    }


def repair_plan_json(error_text: str = "", request: str = "") -> str:
    return json.dumps(repair_plan(error_text, request), indent=2)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate a KIRA dependency repair plan")
    parser.add_argument("--error", default="")
    parser.add_argument("--request", default="")
    args = parser.parse_args()
    print(repair_plan_json(args.error, args.request))
