"""User management page."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from utils.file_handler import load_json
from TkinterGUI.pages.base_page import BasePage


class UsersPage(BasePage):
    """Admin page for user management."""

    def __init__(self, parent, app):
        super().__init__(parent, app, "User Management", "Create users and manage MFA settings.")

        form = ttk.LabelFrame(self, text="Create Or Edit User", padding=16)
        form.pack(fill="x", pady=(0, 12))

        self.selected_username = None
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.email_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.role_var = tk.StringVar(value="staff")
        self.mfa_var = tk.BooleanVar(value=False)

        labels = ["Username", "Password", "Full Name", "Email", "Phone", "Role", "MFA"]
        for idx, label in enumerate(labels):
            ttk.Label(form, text=label).grid(row=0, column=idx, sticky="w")

        ttk.Entry(form, textvariable=self.username_var).grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Entry(form, textvariable=self.password_var, show="*").grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Entry(form, textvariable=self.name_var).grid(row=1, column=2, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Entry(form, textvariable=self.email_var).grid(row=1, column=3, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Entry(form, textvariable=self.phone_var).grid(row=1, column=4, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Combobox(form, textvariable=self.role_var, values=("admin", "staff"), state="readonly").grid(row=1, column=5, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Checkbutton(form, variable=self.mfa_var).grid(row=1, column=6, sticky="w", padx=(0, 8), pady=(4, 10))
        ttk.Button(form, text="Create User", command=self.create_user).grid(row=1, column=7, sticky="ew", padx=(0, 8))
        ttk.Button(form, text="Update Selected", command=self.update_user).grid(row=1, column=8, sticky="ew", padx=(0, 8))
        ttk.Button(form, text="Clear Form", command=self.clear_form).grid(row=1, column=9, sticky="ew")

        ttk.Label(
            form,
            text="Password is only used when creating a new user.",
            style="Muted.TLabel",
        ).grid(row=2, column=0, columnspan=10, sticky="w")

        for idx in range(10):
            form.columnconfigure(idx, weight=1)

        actions = ttk.Frame(self, style="App.TFrame")
        actions.pack(fill="x", pady=(0, 8))
        ttk.Button(actions, text="Refresh Users", command=self.refresh).pack(side="left")
        ttk.Button(actions, text="Enable MFA", command=self.enable_mfa).pack(side="left", padx=8)
        ttk.Button(actions, text="Disable MFA", command=self.disable_mfa).pack(side="left")

        columns = ("username", "role", "name", "email", "phone_number", "mfa_enabled")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col, text, width in [
            ("username", "Username", 120),
            ("role", "Role", 90),
            ("name", "Name", 220),
            ("email", "Email", 220),
            ("phone_number", "Phone", 120),
            ("mfa_enabled", "MFA", 80),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width)
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.pack(fill="both", expand=True)

        self.add_status_bar()

    def refresh(self):
        users = load_json("users.json", {})
        for row in self.tree.get_children():
            self.tree.delete(row)
        for username, data in users.items():
            self.tree.insert(
                "",
                "end",
                values=(
                    username,
                    data.get("role", "unknown"),
                    data.get("name", ""),
                    data.get("email", ""),
                    data.get("phone_number", ""),
                    str(data.get("mfa_enabled", False)),
                ),
            )
        self.set_status(f"Loaded {len(users)} user(s).")

    def on_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.selected_username = values[0]
        self.username_var.set(values[0])
        self.password_var.set("")
        self.name_var.set(values[2])
        self.email_var.set(values[3])
        self.phone_var.set(values[4])
        self.role_var.set(values[1])
        self.mfa_var.set(str(values[5]).lower() == "true")
        self.set_status(f"Loaded user '{self.selected_username}' into the form.")

    def create_user(self):
        success, message = self.app.auth.create_user(
            self.username_var.get().strip(),
            self.password_var.get(),
            self.role_var.get(),
            self.name_var.get().strip(),
            self.email_var.get().strip(),
            self.phone_var.get().strip(),
        )
        if success:
            self.clear_form()
            self.refresh()
            self.set_status(message)
        else:
            self.error("Unable to create user", message)

    def update_user(self):
        if not self.selected_username:
            self.warn("No selection", "Please select a user to edit first.")
            return

        success, message = self.app.auth.update_user(
            self.selected_username,
            self.username_var.get().strip(),
            self.role_var.get(),
            self.name_var.get().strip(),
            self.email_var.get().strip(),
            self.phone_var.get().strip(),
            self.mfa_var.get(),
        )
        if success:
            updated_username = self.username_var.get().strip()
            self.selected_username = updated_username
            self.refresh()
            self.app.refresh_sidebar()
            self.set_status(message)
        else:
            self.error("Unable to update user", message)

    def clear_form(self):
        self.selected_username = None
        for var in (self.username_var, self.password_var, self.name_var, self.email_var, self.phone_var):
            var.set("")
        self.role_var.set("staff")
        self.mfa_var.set(False)
        self.set_status("Form cleared.")

    def _selected_username(self):
        selected = self.tree.selection()
        if not selected:
            self.warn("No selection", "Please select a user first.")
            return None
        return self.tree.item(selected[0], "values")[0]

    def enable_mfa(self):
        username = self._selected_username()
        if not username:
            return
        success, message = self.app.auth.enable_mfa(username)
        if success:
            self.refresh()
            self.set_status(message)
        else:
            self.error("Unable to enable MFA", message)

    def disable_mfa(self):
        username = self._selected_username()
        if not username:
            return
        success, message = self.app.auth.disable_mfa(username)
        if success:
            self.refresh()
            self.set_status(message)
        else:
            self.error("Unable to disable MFA", message)
