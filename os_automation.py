"""Small cross-platform handlers for common local OS commands."""

import subprocess
import sys
from typing import Tuple


def execute_os_command(command: str) -> Tuple[bool, str]:
    """Execute a supported local command and return (handled, message)."""
    text = (command or "").lower().strip()
    if text in {"open calculator", "calculator", "calculator kholo"}:
        if sys.platform == "win32":
            subprocess.Popen(["calc.exe"])
            return True, "Calculator opened."
        return False, ""
    return False, ""
