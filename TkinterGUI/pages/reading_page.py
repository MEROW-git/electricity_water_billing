"""Meter reading page."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from TkinterGUI.pages.base_page import BasePage
from TkinterGUI.widgets.customer_combobox import CustomerCombobox


class ReadingPage(BasePage):
    """Page for updating customer meter readings."""

    def __init__(self, parent, app):
        super().__init__(parent, app, "Meter Reading", "Update both readings from one form. Leave one box empty if only one reading changes.")

        form_box = ttk.LabelFrame(self, text="Update Customer Readings", padding=16)
        form_box.pack(fill="x", pady=(0, 12))

        self.customer_id_var = tk.StringVar()
        self.electricity_var = tk.StringVar()
        self.water_var = tk.StringVar()
        self.electricity_note_var = tk.StringVar(value="Electricity old reading: N/A")
        self.water_note_var = tk.StringVar(value="Water old reading: N/A")
        self.search_var = tk.StringVar()
        self.customer_rows = []

        ttk.Label(form_box, text="Customer ID").grid(row=0, column=0, sticky="w")
        ttk.Label(form_box, text="Electricity Reading").grid(row=0, column=1, sticky="w")
        ttk.Label(form_box, text="Water Reading").grid(row=0, column=2, sticky="w")

        self.customer_combo = CustomerCombobox(form_box, self.app, textvariable=self.customer_id_var)
        self.customer_combo.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(4, 6))
        self.customer_combo.bind("<<ComboboxSelected>>", self.on_customer_change)
        self.customer_combo.bind("<FocusOut>", self.on_customer_change)

        ttk.Entry(form_box, textvariable=self.electricity_var).grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(4, 6))
        ttk.Entry(form_box, textvariable=self.water_var).grid(row=1, column=2, sticky="ew", padx=(0, 8), pady=(4, 6))
        ttk.Button(form_box, text="Update Readings", command=self.update_readings).grid(row=1, column=3, sticky="ew")

        ttk.Label(form_box, textvariable=self.electricity_note_var, style="Muted.TLabel").grid(row=2, column=1, sticky="w")
        ttk.Label(form_box, textvariable=self.water_note_var, style="Muted.TLabel").grid(row=2, column=2, sticky="w")

        for idx in range(4):
            form_box.columnconfigure(idx, weight=1)

        list_frame = ttk.LabelFrame(self, text="Customers And Current Meter Readings", padding=12)
        list_frame.pack(fill="both", expand=True)

        search_row = ttk.Frame(list_frame)
        search_row.pack(fill="x", pady=(0, 8))
        ttk.Label(search_row, text="Search").pack(side="left", padx=(0, 8))
        search_entry = ttk.Entry(search_row, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(search_row, text="Find", command=self.apply_search).pack(side="left", padx=8)
        ttk.Button(search_row, text="Clear", command=self.clear_search).pack(side="left")
        ttk.Label(
            search_row,
            text="Search by customer ID, customer name, electric meter ID, or water meter ID",
            style="Muted.TLabel",
        ).pack(side="left", padx=(12, 0))
        self.search_var.trace_add("write", self.on_search_change)

        columns = ("customer_id", "name", "electricity_meter", "electricity_old", "water_meter", "water_old")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        headings = [
            ("customer_id", "Customer ID", 120),
            ("name", "Customer Name", 220),
            ("electricity_meter", "Electric Meter", 120),
            ("electricity_old", "Electric Old", 120),
            ("water_meter", "Water Meter", 120),
            ("water_old", "Water Old", 120),
        ]
        for col, text, width in headings:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.output = tk.Text(self, height=8, wrap="word")
        self.output.pack(fill="x", pady=(12, 0))
        self.add_status_bar()

    def refresh(self):
        self.customer_combo.refresh_values()
        self.populate_customer_list()
        self.update_notes("")
        self.set_status("Loaded customer reading list.")

    def populate_customer_list(self):
        self.customer_rows = []
        customers = self.app.customer_ctrl.get_all_customers()
        for customer in sorted(customers.values(), key=lambda c: c.customer_id):
            if not customer.is_active:
                continue
            meters = self.app.meter_ctrl.get_customer_meters(customer.customer_id)
            elec = meters.get("electricity")
            water = meters.get("water")
            self.customer_rows.append(
                (
                    customer.customer_id,
                    customer.name,
                    elec.meter_id if elec else "Not assigned",
                    f"{elec.current_reading:.2f}" if elec else "N/A",
                    water.meter_id if water else "Not assigned",
                    f"{water.current_reading:.2f}" if water else "N/A",
                )
            )
        self.apply_search()

    def render_rows(self, rows):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row_values in rows:
            self.tree.insert("", "end", values=row_values)

    def on_search_change(self, *_args):
        self.apply_search()

    def apply_search(self):
        keyword = self.search_var.get().strip().lower()
        if not keyword:
            self.render_rows(self.customer_rows)
            self.set_status(f"Showing {len(self.customer_rows)} customer row(s).")
            return

        filtered = []
        for row in self.customer_rows:
            customer_id, name, electric_meter, _electric_old, water_meter, _water_old = row
            if (
                keyword in customer_id.lower()
                or keyword in name.lower()
                or keyword in electric_meter.lower()
                or keyword in water_meter.lower()
            ):
                filtered.append(row)

        self.render_rows(filtered)
        self.set_status(f"Found {len(filtered)} matching customer row(s).")

    def clear_search(self):
        self.search_var.set("")

    def on_tree_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        customer_id = values[0]
        self.customer_id_var.set(customer_id)
        self.update_notes(customer_id)
        self.set_status(f"Selected {customer_id} for reading update.")

    def on_customer_change(self, _event=None):
        customer_id = self.customer_combo.get_customer_id()
        self.update_notes(customer_id)

    def update_notes(self, customer_id):
        if not customer_id:
            self.electricity_note_var.set("Electricity old reading: N/A")
            self.water_note_var.set("Water old reading: N/A")
            return

        meters = self.app.meter_ctrl.get_customer_meters(customer_id)
        electricity = meters.get("electricity")
        water = meters.get("water")

        if electricity:
            self.electricity_note_var.set(
                f"Electricity old reading: {electricity.current_reading:.2f} "
                f"(Meter {electricity.meter_id})"
            )
        else:
            self.electricity_note_var.set("Electricity old reading: Not assigned")

        if water:
            self.water_note_var.set(
                f"Water old reading: {water.current_reading:.2f} "
                f"(Meter {water.meter_id})"
            )
        else:
            self.water_note_var.set("Water old reading: Not assigned")

    def update_readings(self):
        customer_id = self.customer_combo.get_customer_id()
        if not customer_id:
            self.error("Customer not found", "Choose or type a valid customer ID.")
            return

        meters = self.app.meter_ctrl.get_customer_meters(customer_id)
        if not meters["electricity"] and not meters["water"]:
            self.error("No meters", "This customer has no assigned meters.")
            return

        electricity_text = self.electricity_var.get().strip()
        water_text = self.water_var.get().strip()

        if not electricity_text and not water_text:
            self.warn("Missing readings", "Enter electricity, water, or both readings.")
            return

        lines = [f"Customer: {customer_id}"]
        success_any = False

        if electricity_text:
            if not meters["electricity"]:
                self.error("Missing electricity meter", "This customer does not have an electricity meter.")
                return
            try:
                electricity_value = float(electricity_text)
            except ValueError:
                self.error("Invalid electricity reading", "Electricity reading must be numeric.")
                return
            s1, m1, u1 = self.app.meter_ctrl.update_reading(meters["electricity"].meter_id, electricity_value)
            lines.append(f"Electricity: {m1}" + (f" (Usage: {u1:.2f})" if s1 else ""))
            success_any = success_any or s1

        if water_text:
            if not meters["water"]:
                self.error("Missing water meter", "This customer does not have a water meter.")
                return
            try:
                water_value = float(water_text)
            except ValueError:
                self.error("Invalid water reading", "Water reading must be numeric.")
                return
            s2, m2, u2 = self.app.meter_ctrl.update_reading(meters["water"].meter_id, water_value)
            lines.append(f"Water: {m2}" + (f" (Usage: {u2:.2f})" if s2 else ""))
            success_any = success_any or s2

        self.output.delete("1.0", "end")
        self.output.insert("1.0", "\n".join(lines))

        if success_any:
            self.electricity_var.set("")
            self.water_var.set("")
            self.refresh()
            self.customer_id_var.set(customer_id)
            self.update_notes(customer_id)
            self.set_status(f"Updated readings for {customer_id}.")
        else:
            self.set_status(f"No readings were updated for {customer_id}.")
