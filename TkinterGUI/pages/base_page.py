"""Shared helpers for GUI pages."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class BasePage(ttk.Frame):
    """Base page with shared helpers and styling."""

    def __init__(self, parent, app, title, subtitle):
        super().__init__(parent, style="App.TFrame")
        self.app = app
        self.status_var = tk.StringVar(value="Ready")

        header = ttk.Frame(self, style="App.TFrame")
        header.pack(fill="x", pady=(0, 12))
        ttk.Label(header, text=title, style="Header.TLabel").pack(anchor="w")
        ttk.Label(header, text=subtitle, style="Muted.TLabel").pack(anchor="w", pady=(4, 0))

    def add_status_bar(self):
        ttk.Label(self, textvariable=self.status_var, style="Muted.TLabel").pack(anchor="w", pady=(12, 0))

    def set_status(self, message):
        self.status_var.set(message)

    def info(self, title, message):
        messagebox.showinfo(title, message)

    def error(self, title, message):
        messagebox.showerror(title, message)

    def warn(self, title, message):
        messagebox.showwarning(title, message)

    def refresh(self):
        return None
