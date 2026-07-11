import os
import ast
import fnmatch
import platform
import subprocess
import shutil
import tempfile
import time
from typing import List, Optional

try:
    import pyperclip
except Exception:
    pyperclip = None

try:
    import pytesseract
    from PIL import Image
except Exception:
    pytesseract = None

try:
    import pyautogui
except Exception:
    pyautogui = None

try:
    import psutil
except Exception:
    psutil = None

from search import SearchEngine


def web_search(query: str) -> List[dict]:
    se = SearchEngine()
    return se.search(query)


def calculator(expr: str):
    """
    Safely evaluate arithmetic expressions using ast parsing. Supports +,-,*,/,**,(),%,//.
    """
    try:
        node = ast.parse(expr, mode="eval")

        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                raise ValueError("Function calls are not allowed in calculator")
            if isinstance(n, ast.Name):
                raise ValueError("Names are not allowed in calculator")

        compiled = compile(node, "<ast>", "eval")
        return eval(compiled, {"__builtins__": {}})
    except Exception as e:
        return f"Calculator error: {e}"


def file_search(name_pattern: str, path: str = ".", max_results: int = 10):
    """
    Search for files by filename pattern (supports Unix shell-style wildcards) and return paths.
    """
    matches = []
    for root, dirs, files in os.walk(path):
        for filename in files:
            if fnmatch.fnmatch(filename, name_pattern):
                matches.append(os.path.join(root, filename))
                if len(matches) >= max_results:
                    return matches
    return matches


def copy_to_clipboard(text: str) -> str:
    if not pyperclip:
        return "pyperclip not installed"
    try:
        pyperclip.copy(text)
        return "Text copied to clipboard."
    except Exception as e:
        return f"Clipboard error: {e}"


def paste_from_clipboard() -> str:
    if not pyperclip:
        return "pyperclip not installed"
    try:
        return pyperclip.paste()
    except Exception as e:
        return f"Clipboard error: {e}"


def ocr_from_image(image_path: str) -> str:
    if not pytesseract:
        return "pytesseract not installed"
    if not os.path.exists(image_path):
        return "Image not found"
    try:
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        return f"OCR error: {e}"


def take_screenshot(save_path: Optional[str] = None) -> str:
    if not pyautogui:
        return "pyautogui not installed"
    try:
        if not save_path:
            fd, save_path = tempfile.mkstemp(suffix=".png")
            os.close(fd)
        img = pyautogui.screenshot()
        img.save(save_path)
        return save_path
    except Exception as e:
        return f"Screenshot error: {e}"


def screenshot_to_ocr(save_path: Optional[str] = None) -> str:
    shot = take_screenshot(save_path)
    if not shot or shot.startswith("Screenshot error"):
        return shot
    return ocr_from_image(shot)


def open_app(target: str) -> str:
    """
    Open an application by path or by command. Returns a message or PID/handle info.
    """
    try:
        # If it's a path
        if os.path.exists(target):
            if platform.system() == "Windows":
                os.startfile(target)
                return f"Opened {target}"
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", target])
                return f"Opened {target}"
            else:
                subprocess.Popen(["xdg-open", target])
                return f"Opened {target}"

        # Otherwise try to run as command
        proc = subprocess.Popen(target.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return f"Started process PID {proc.pid}"
    except Exception as e:
        return f"Open app error: {e}"


def close_app(process_name: str) -> str:
    if not psutil:
        return "psutil not installed"
    try:
        found = []
        for p in psutil.process_iter(["pid", "name", "cmdline"]):
            name = (p.info.get("name") or "")
            cmd = " ".join(p.info.get("cmdline") or [])
            if process_name.lower() in name.lower() or process_name.lower() in cmd.lower():
                try:
                    p.terminate()
                    p.wait(timeout=5)
                    found.append(p.info["pid"])
                except Exception:
                    try:
                        p.kill()
                    except Exception:
                        pass
        if not found:
            return f"No running process found matching '{process_name}'."
        return f"Terminated processes: {found}"
    except Exception as e:
        return f"Close app error: {e}"


def create_folder(path: str) -> str:
    try:
        os.makedirs(path, exist_ok=True)
        return f"Folder created: {path}"
    except Exception as e:
        return f"Create folder error: {e}"


def create_file(path: str, content: str = "") -> str:
    try:
        dirpath = os.path.dirname(path)
        if dirpath and not os.path.exists(dirpath):
            os.makedirs(dirpath, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File created: {path}"
    except Exception as e:
        return f"Create file error: {e}"


def keyboard_type(text: str, interval: float = 0.01) -> str:
    if not pyautogui:
        return "pyautogui not installed"
    try:
        pyautogui.write(text, interval=interval)
        return "Typed text."
    except Exception as e:
        return f"Keyboard error: {e}"


def press_key(key: str) -> str:
    if not pyautogui:
        return "pyautogui not installed"
    try:
        pyautogui.press(key)
        return f"Pressed key: {key}"
    except Exception as e:
        return f"Keyboard error: {e}"


def move_mouse(x: int, y: int) -> str:
    if not pyautogui:
        return "pyautogui not installed"
    try:
        pyautogui.moveTo(x, y)
        return f"Moved mouse to {x},{y}"
    except Exception as e:
        return f"Mouse error: {e}"


def click_mouse(x: Optional[int] = None, y: Optional[int] = None, button: str = "left") -> str:
    if not pyautogui:
        return "pyautogui not installed"
    try:
        if x is not None and y is not None:
            pyautogui.click(x, y, button=button)
        else:
            pyautogui.click(button=button)
        return "Click performed"
    except Exception as e:
        return f"Mouse error: {e}"


def get_volume() -> str:
    system = platform.system()
    try:
        if system == "Darwin":
            cmd = ["osascript", "-e", "output volume of (get volume settings)"]
            out = subprocess.check_output(cmd).decode().strip()
            return out
        elif system == "Linux":
            if shutil.which("amixer"):
                out = subprocess.check_output(["amixer", "get", "Master"]).decode()
                # crude parse
                import re

                m = re.search(r"\[(\d+)%\]", out)
                if m:
                    return m.group(1)
                return out
            else:
                return "amixer not found"
        elif system == "Windows":
            return "Volume query not implemented on Windows"
        else:
            return "Unsupported OS for volume"
    except Exception as e:
        return f"Get volume error: {e}"


def set_volume(value: int) -> str:
    system = platform.system()
    try:
        if not (0 <= value <= 100):
            return "Volume must be between 0 and 100"
        if system == "Darwin":
            cmd = ["osascript", "-e", f"set volume output volume {value}"]
            subprocess.check_call(cmd)
            return f"Volume set to {value}"
        elif system == "Linux":
            if shutil.which("amixer"):
                subprocess.check_call(["amixer", "set", "Master", f"{value}%"], stdout=subprocess.DEVNULL)
                return f"Volume set to {value}"
            else:
                return "amixer not found"
        elif system == "Windows":
            return "Set volume not implemented on Windows"
        else:
            return "Unsupported OS for volume"
    except Exception as e:
        return f"Set volume error: {e}"
