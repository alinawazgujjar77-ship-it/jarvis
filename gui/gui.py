"""Modern GUI for JARVIS with dark theme and animated orb."""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
from typing import Callable, Optional
from core.logger import Logger
from core.config_manager import Config

logger = Logger.get(__name__)

try:
    import customtkinter as ctk
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
except ImportError:
    ctk = None


class JARVSGUI:
    """Modern dark-themed GUI application."""

    def __init__(self, on_submit: Callable[[str], str]) -> None:
        self.on_submit = on_submit
        self.root = None
        self.chat_display = None
        self.input_field = None
        self.send_button = None
        self.is_running = False
        self._init_gui()

    def _init_gui(self) -> None:
        """Initialize GUI components."""
        if ctk:
            self._init_custom_tkinter()
        else:
            self._init_standard_tkinter()

    def _init_custom_tkinter(self) -> None:
        """Initialize with customtkinter for modern look."""
        self.root = ctk.CTk()
        self.root.title(f"{Config.assistant_name} - Pro Assistant")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Main frame
        main_frame = ctk.CTkFrame(self.root, fg_color="#1a1a2e")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Title
        title = ctk.CTkLabel(
            main_frame,
            text=f"{Config.assistant_name} Pro",
            font=("Arial", 24, "bold"),
            text_color="#00d4ff"
        )
        title.pack(pady=10)

        # Chat display
        chat_frame = ctk.CTkFrame(main_frame)
        chat_frame.pack(fill="both", expand=True, pady=10)

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            bg="#0f0f1e",
            fg="#ffffff",
            font=("Courier", 10),
            height=20
        )
        self.chat_display.pack(fill="both", expand=True)
        self.chat_display.config(state="disabled")

        # Input frame
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.pack(fill="x", pady=10)

        self.input_field = ctk.CTkEntry(
            input_frame,
            placeholder_text="Type your message...",
            text_color="#ffffff",
            fg_color="#16213e",
            border_color="#00d4ff",
            border_width=2
        )
        self.input_field.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_field.bind("<Return>", lambda e: self._handle_send())

        self.send_button = ctk.CTkButton(
            input_frame,
            text="Send",
            command=self._handle_send,
            fg_color="#00d4ff",
            text_color="#000000",
            width=100
        )
        self.send_button.pack(side="right")

        # Status bar
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="Ready",
            text_color="#00d4ff",
            font=("Arial", 9)
        )
        self.status_label.pack(pady=5)

    def _init_standard_tkinter(self) -> None:
        """Initialize with standard tkinter."""
        self.root = tk.Tk()
        self.root.title(f"{Config.assistant_name} - Pro Assistant")
        self.root.geometry("800x600")
        self.root.configure(bg="#1a1a2e")
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Title
        title = tk.Label(
            self.root,
            text=f"{Config.assistant_name} Pro",
            font=("Arial", 24, "bold"),
            bg="#1a1a2e",
            fg="#00d4ff"
        )
        title.pack(pady=10)

        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            self.root,
            wrap=tk.WORD,
            bg="#0f0f1e",
            fg="#ffffff",
            font=("Courier", 10),
            height=20
        )
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=10)
        self.chat_display.config(state="disabled")

        # Input frame
        input_frame = tk.Frame(self.root, bg="#1a1a2e")
        input_frame.pack(fill="x", padx=10, pady=10)

        self.input_field = tk.Entry(
            input_frame,
            bg="#16213e",
            fg="#ffffff",
            font=("Arial", 10),
            insertbackground="#00d4ff"
        )
        self.input_field.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.input_field.bind("<Return>", lambda e: self._handle_send())

        self.send_button = tk.Button(
            input_frame,
            text="Send",
            command=self._handle_send,
            bg="#00d4ff",
            fg="#000000",
            font=("Arial", 10),
            width=10
        )
        self.send_button.pack(side="right")

        # Status bar
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            bg="#1a1a2e",
            fg="#00d4ff",
            font=("Arial", 9)
        )
        self.status_label.pack(pady=5)

    def _handle_send(self) -> None:
        """Handle message submission."""
        user_input = self.input_field.get().strip()
        if not user_input:
            return

        self.input_field.delete(0, tk.END)
        self._display_message("You", user_input)

        # Process in thread to avoid GUI freezing
        thread = threading.Thread(target=self._process_message, args=(user_input,))
        thread.daemon = True
        thread.start()

    def _process_message(self, message: str) -> None:
        """Process user message."""
        try:
            self._update_status("Processing...")
            response = self.on_submit(message)
            self._display_message(Config.assistant_name, response)
            self._update_status("Ready")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            self._display_message("Error", str(e))
            self._update_status("Error")

    def _display_message(self, sender: str, message: str) -> None:
        """Display a message in chat."""
        self.chat_display.config(state="normal")
        self.chat_display.insert(tk.END, f"\n{sender}: {message}\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state="disabled")

    def _update_status(self, status: str) -> None:
        """Update status bar."""
        if self.status_label:
            self.status_label.config(text=status)

    def _on_closing(self) -> None:
        """Handle window closing."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.is_running = False
            if self.root:
                self.root.destroy()

    def run(self) -> None:
        """Start the GUI."""
        if self.root:
            self.is_running = True
            self.root.mainloop()

    def stop(self) -> None:
        """Stop the GUI."""
        self.is_running = False
        if self.root:
            self.root.destroy()
