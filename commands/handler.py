import re
from typing import Tuple

from voice import speak, listen
from tools import utils
from config import COMMAND_ALLOWLIST, COMMAND_DENYLIST


class CommandHandler:
    def __init__(self, memory=None):
        self.memory = memory

    def _confirm(self, prompt: str) -> bool:
        speak(prompt + " Say 'yes' to confirm, or 'no' to cancel.")
        resp = listen()
        if not resp:
            return False
        return resp.strip().lower() in ("yes", "y", "sure", "confirm")

    def _is_allowed(self, command: str) -> Tuple[bool, str]:
        lc = command.lower()
        # Deny if any denylist substring present
        for d in COMMAND_DENYLIST:
            ds = d.strip().lower()
            if not ds:
                continue
            if ds in lc:
                return False, f"Command contains denied pattern: '{ds}'"
        # If allowlist present, require at least one allow token
        if COMMAND_ALLOWLIST:
            ok = False
            for a in COMMAND_ALLOWLIST:
                as_ = a.strip().lower()
                if not as_:
                    continue
                if as_ in lc:
                    ok = True
                    break
            if not ok:
                return False, "Command not allowed by allowlist."
        return True, ""

    def handle(self, command: str) -> Tuple[bool, str]:
        """
        Handle system/utility commands. Returns (handled: bool, response: str).
        If handled is False, the caller should pass the command to the AI.
        """
        if not command or not command.strip():
            return True, "No command provided."

        # Safety check
        allowed, reason = self._is_allowed(command)
        if not allowed:
            return True, f"Command blocked for safety: {reason}"

        c = command.strip()
        lc = c.lower()

        # Calculator
        m = re.match(r"(?:calculate|what is|compute)\s+(.+)", lc)
        if m:
            expr = m.group(1)
            res = utils.calculator(expr)
            return True, f"Calculator result: {res}"

        # Web search
        if lc.startswith("search for ") or lc.startswith("web search ") or lc.startswith("google "):
            query = c.split(" ", 2)[-1] if len(c.split(" ")) >= 3 else c
            results = utils.web_search(query)
            if not results:
                return True, "No search results found."
            text = "Top results:\n" + "\n".join([f"- {r['title']}: {r['link']}" for r in results[:5]])
            return True, text

        # Take screenshot
        if "screenshot" in lc or "take screenshot" in lc:
            path = utils.take_screenshot()
            return True, f"Screenshot saved to: {path}"

        # OCR image (file path provided)
        m = re.match(r"ocr(?:\s+image)?\s+(.*)", lc)
        if m:
            img = command.split(" ", 1)[1]
            res = utils.ocr_from_image(img)
            return True, f"OCR result:\n{res}"

        # Open app
        m = re.match(r"open(?:\s+app)?\s+(.*)", lc)
        if m:
            target = command.split(" ", 1)[1]
            res = utils.open_app(target)
            return True, res

        # Close app (requires confirmation)
        m = re.match(r"close(?:\s+app)?\s+(.*)", lc)
        if m:
            target = command.split(" ", 1)[1]
            if not self._confirm(f"Are you sure you want to close '{target}'?"):
                return True, "Cancelled closing the app."
            res = utils.close_app(target)
            return True, res

        # Create folder
        m = re.match(r"create folder\s+(.*)", lc)
        if m:
            path = command.split(" ", 2)[2]
            res = utils.create_folder(path)
            return True, res

        # Create file
        m = re.match(r"create file\s+([^\s]+)(?:\s+with content\s+(.*))?", lc)
        if m:
            parts = command.split(" ", 3)
            path = parts[2]
            content = parts[3] if len(parts) > 3 else ""
            res = utils.create_file(path, content)
            return True, res

        # Copy to clipboard
        m = re.match(r"copy\s+(.*)", lc)
        if m:
            text = command.split(" ", 1)[1]
            res = utils.copy_to_clipboard(text)
            return True, res

        # Paste from clipboard
        if lc.strip() in ("paste", "paste clipboard"):
            res = utils.paste_from_clipboard()
            return True, f"Clipboard contents:\n{res}"

        # File search
        m = re.match(r"find file\s+(.*)", lc)
        if m:
            pattern = command.split(" ", 2)[2]
            res = utils.file_search(pattern)
            if not res:
                return True, "No files found."
            return True, "Files found:\n" + "\n".join(res)

        # Keyboard/mouse actions (require confirmation)
        if lc.startswith("type "):
            text = command.split(" ", 1)[1]
            if not self._confirm(f"Type the following text: {text}? This will send keystrokes to the active window."):
                return True, "Typing cancelled."
            res = utils.keyboard_type(text)
            return True, res

        if lc.startswith("press "):
            key = command.split(" ", 1)[1]
            if not self._confirm(f"Press key {key}?"):
                return True, "Key press cancelled."
            res = utils.press_key(key)
            return True, res

        if lc.startswith("move mouse to "):
            parts = re.findall(r"-?\d+", lc)
            if len(parts) >= 2:
                x, y = int(parts[0]), int(parts[1])
                res = utils.move_mouse(x, y)
                return True, res

        if lc.startswith("click"):
            if not self._confirm("Perform a mouse click now?"):
                return True, "Click cancelled."
            res = utils.click_mouse()
            return True, res

        # Volume control
        m = re.match(r"set volume to\s+(\d+)", lc)
        if m:
            value = int(m.group(1))
            res = utils.set_volume(value)
            return True, res

        if "what is the volume" in lc or "get volume" in lc:
            res = utils.get_volume()
            return True, f"Volume: {res}"

        # If no command matched
        return False, ""
