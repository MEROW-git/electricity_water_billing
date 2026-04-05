"""Login page for the desktop app."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk


class LoginPage(ttk.Frame):
    """Login screen."""

    def __init__(self, app):
        super().__init__(app, padding=24, style="App.TFrame")
        self.app = app

        card = ttk.Frame(self, padding=30, style="Card.TFrame")
        card.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(card, text="Electricity & Water Billing System", style="Header.TLabel").grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(card, text="Use your real account from the SQLite database", style="Muted.TLabel").grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 20))

        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()

        ttk.Label(card, text="Username").grid(row=2, column=0, sticky="w")
        username_entry = ttk.Entry(card, textvariable=self.username_var, width=34)
        username_entry.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(4, 12))

        ttk.Label(card, text="Password").grid(row=4, column=0, sticky="w")
        ttk.Entry(card, textvariable=self.password_var, show="*", width=34).grid(row=5, column=0, columnspan=2, sticky="ew", pady=(4, 16))

        ttk.Button(card, text="Login", command=self.attempt_login).grid(row=6, column=0, columnspan=2, sticky="ew")
        ttk.Label(card, text="Default admin: admin / admin123", style="Muted.TLabel").grid(row=7, column=0, columnspan=2, sticky="w", pady=(14, 0))

        username_entry.focus_set()
        self.bind_all("<Return>", self._submit)

    def _submit(self, _event):
        self.attempt_login()

    def attempt_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get()

        if not username or not password:
            messagebox.showwarning("Missing information", "Please enter both username and password.")
            return

        success, message = self.app.auth.login(username, password)
        if not success and "MFA code sent" in message:
            code = self.prompt_mfa_code(username)
            if not code:
                return
            success, message = self.app.auth.login(username, password, code)

        if success:
            self.unbind_all("<Return>")
            self.app.show_workspace()
        else:
            messagebox.showerror("Login failed", message)

    def prompt_mfa_code(self, username):
        dialog = tk.Toplevel(self)
        dialog.title("MFA Verification")
        dialog.transient(self.app)
        dialog.grab_set()
        dialog.resizable(False, False)

        frame = ttk.Frame(dialog, padding=20, style="Card.TFrame")
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=f"Enter the MFA code for {username}").pack(anchor="w")

        code_var = tk.StringVar()
        entry = ttk.Entry(frame, textvariable=code_var, width=18)
        entry.pack(fill="x", pady=(10, 12))
        entry.focus_set()

        result = {"value": None}

        def submit():
            result["value"] = code_var.get().strip()
            dialog.destroy()

        ttk.Button(frame, text="Verify", command=submit).pack(fill="x")
        dialog.bind("<Return>", lambda _event: submit())
        self.wait_window(dialog)
        return result["value"]
