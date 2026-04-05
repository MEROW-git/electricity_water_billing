"""Searchable customer selector widget."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk


class CustomerCombobox(ttk.Combobox):
    """Combobox that lists customers and resolves short customer IDs."""

    def __init__(self, parent, app, textvariable=None, width=24, **kwargs):
        self.app = app
        self._display_to_id = {}
        self._filtered_values = []
        super().__init__(parent, textvariable=textvariable, width=width, **kwargs)
        self.configure(state="normal")
        self.bind("<KeyRelease>", self._filter_values)

    def refresh_values(self):
        customers = self.app.customer_ctrl.get_all_customers()
        items = []
        self._display_to_id = {}

        for customer in sorted(customers.values(), key=lambda c: c.customer_id):
            if not customer.is_active:
                continue
            display = f"{customer.customer_id} - {customer.name}"
            items.append(display)
            self._display_to_id[display] = customer.customer_id

        self._filtered_values = items
        self["values"] = items

    def _filter_values(self, _event=None):
        typed = self.get().strip().lower()
        if not typed:
            self["values"] = self._filtered_values
            return

        matches = []
        for display, customer_id in self._display_to_id.items():
            short_id = customer_id.split("-")[-1]
            short_num = str(int(short_id)) if short_id.isdigit() else short_id
            haystacks = [
                display.lower(),
                customer_id.lower(),
                short_id.lower(),
                short_num.lower(),
            ]
            if any(typed in value for value in haystacks):
                matches.append(display)

        self["values"] = matches or self._filtered_values

    def get_customer_id(self):
        raw = self.get().strip()
        if not raw:
            return ""
        if raw in self._display_to_id:
            return self._display_to_id[raw]
        return self.app.customer_ctrl.resolve_customer_id(raw.upper()) or ""
