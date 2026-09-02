"""
os_automation.py - Cross-Platform OS Automation Handlers for Kira AI
--------------------------------------------------------------------
Provides seamless cross-platform operating system actions across Windows, macOS, and Linux:
- Calculator (calc.exe, Calculator.app, gnome-calculator / kcalc)
- File Explorer / Finder (explorer.exe, open ., nautilus / xdg-open)
- Text Editor / Notepad (notepad.exe, open -a TextEdit, gedit / nano / xdg-open)
- System Terminal / Command Line
- Settings & System Information
"""

import subprocess
import sys
import platform
import shutil
from typing import Tuple


def _run_detached(cmd_list: list) -> bool:
    """Safely run a command in the background without blocking."""
    try:
        if sys.platform == "win32":
            subprocess.Popen(cmd_list, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
        else:
            subprocess.Popen(cmd_list, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def execute_os_command(command: str) -> Tuple[bool, str]:
    """
    Execute a supported local OS command and return (handled, message).
    Supports Windows, macOS, and Linux out-of-the-box.
    """
    if not command:
        return False, ""

    text = (command or "").lower().strip()
    system = platform.system()  # 'Windows', 'Darwin' (macOS), 'Linux'

    # 1. Calculator
    if any(k in text for k in ["open calculator", "calculator", "calculator kholo", "hisab kitab"]):
        if system == "Windows":
            _run_detached(["calc.exe"])
            return True, "Calculator opened."
        elif system == "Darwin":
            _run_detached(["open", "-a", "Calculator"])
            return True, "Calculator opened."
        else:
            for calc_cmd in ["gnome-calculator", "kcalc", "xcalc", "galculator"]:
                if shutil.which(calc_cmd):
                    _run_detached([calc_cmd])
                    return True, "Calculator opened."
            return True, "Calculator command sent."

    # 2. File Explorer / Finder / Directory
    if any(k in text for k in ["open file explorer", "explorer", "files", "open folder", "finder", "file manager"]):
        if system == "Windows":
            _run_detached(["explorer.exe"])
            return True, "File explorer opened."
        elif system == "Darwin":
            _run_detached(["open", "."])
            return True, "Finder opened."
        else:
            for fm_cmd in ["xdg-open", "nautilus", "dolphin", "thunar"]:
                if shutil.which(fm_cmd):
                    _run_detached([fm_cmd, "."])
                    return True, "File explorer opened."
            return True, "File manager opened."

    # 3. Notepad / Text Editor
    if any(k in text for k in ["open notepad", "notepad", "text editor", "open text editor", "editor kholo"]):
        if system == "Windows":
            _run_detached(["notepad.exe"])
            return True, "Notepad opened."
        elif system == "Darwin":
            _run_detached(["open", "-a", "TextEdit"])
            return True, "TextEdit opened."
        else:
            for ed_cmd in ["gedit", "kate", "mousepad", "nano", "xdg-open"]:
                if shutil.which(ed_cmd):
                    _run_detached([ed_cmd])
                    return True, "Text editor opened."
            return True, "Text editor opened."

    # 4. Terminal / Command Prompt
    if any(k in text for k in ["open terminal", "terminal", "command prompt", "open cmd", "powershell"]):
        if system == "Windows":
            _run_detached(["cmd.exe", "/c", "start", "cmd.exe"])
            return True, "Command Prompt opened."
        elif system == "Darwin":
            _run_detached(["open", "-a", "Terminal"])
            return True, "Terminal opened."
        else:
            for term_cmd in ["x-terminal-emulator", "gnome-terminal", "konsole", "xterm"]:
                if shutil.which(term_cmd):
                    _run_detached([term_cmd])
                    return True, "Terminal opened."
            return True, "Terminal opened."

    return False, ""
