"""Meter management page."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from TkinterGUI.pages.base_page import BasePage


class MeterPage(BasePage):
    """Page for meter assignment and browsing."""

    def __init__(self, parent, app):
        super().__init__(parent, app, "Meter Management", "Assign meters and review all stored meters.")

        top = ttk.Frame(self, style="App.TFrame")
        top.pack(fill="x", pady=(0, 12))

        assign_box = ttk.LabelFrame(top, text="Assign Meters To Customer", padding=16)
        assign_box.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.customer_id_var = tk.StringVar()
        self.elec_var = tk.StringVar(value="0")
        self.water_var = tk.StringVar(value="0")

        ttk.Label(assign_box, text="Customer ID").grid(row=0, column=0, sticky="w")
        ttk.Label(assign_box, text="Initial Electricity").grid(row=0, column=1, sticky="w")
        ttk.Label(assign_box, text="Initial Water").grid(row=0, column=2, sticky="w")
        ttk.Entry(assign_box, textvariable=self.customer_id_var).grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Entry(assign_box, textvariable=self.elec_var).grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Entry(assign_box, textvariable=self.water_var).grid(row=1, column=2, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Button(assign_box, text="Assign", command=self.assign_meters).grid(row=1, column=3, sticky="ew")

        for idx in range(4):
            assign_box.columnconfigure(idx, weight=1)

        lookup_box = ttk.LabelFrame(top, text="View Customer Meters", padding=16)
        lookup_box.pack(side="right", fill="both", expand=True)

        self.lookup_customer_var = tk.StringVar()
        ttk.Entry(lookup_box, textvariable=self.lookup_customer_var).pack(fill="x", pady=(0, 10))
        ttk.Button(lookup_box, text="Show Customer Meters", command=self.show_customer_meters).pack(fill="x")

        self.customer_meter_text = tk.Text(lookup_box, height=7, wrap="word")
        self.customer_meter_text.pack(fill="both", expand=True, pady=(10, 0))

        table_frame = ttk.Frame(self, style="App.TFrame")
        table_frame.pack(fill="both", expand=True)
        columns = ("meter_id", "meter_type", "customer_id", "previous", "current", "usage", "last_updated")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        headings = [
            ("meter_id", "Meter ID", 90),
            ("meter_type", "Type", 120),
            ("customer_id", "Customer", 110),
            ("previous", "Previous", 100),
            ("current", "Current", 100),
            ("usage", "Usage", 100),
            ("last_updated", "Last Updated", 150),
        ]
        for col, text, width in headings:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.add_status_bar()

    def refresh(self):
        meters = self.app.meter_ctrl.get_all_meters().values()
        for row in self.tree.get_children():
            self.tree.delete(row)
        for meter in meters:
            self.tree.insert(
                "",
                "end",
                values=(
                    meter.meter_id,
                    meter.meter_type,
                    meter.customer_id,
                    f"{meter.previous_reading:.2f}",
                    f"{meter.current_reading:.2f}",
                    f"{meter.get_usage():.2f}",
                    meter.last_updated or "N/A",
                ),
            )
        self.set_status("Meter list refreshed.")

    def assign_meters(self):
        try:
            elec = float(self.elec_var.get().strip())
            water = float(self.water_var.get().strip())
        except ValueError:
            self.error("Invalid value", "Initial readings must be numeric.")
            return

        customer_id = self.customer_id_var.get().strip().upper()
        success, message, elec_id, water_id = self.app.meter_ctrl.assign_meters(customer_id, elec, water)
        if success:
            self.refresh()
            self.set_status(f"{message}: {elec_id}, {water_id}")
        else:
            self.error("Unable to assign meters", message)

    def show_customer_meters(self):
        customer_id = self.lookup_customer_var.get().strip().upper()
        meters = self.app.meter_ctrl.get_customer_meters(customer_id)
        lines = [f"Customer: {customer_id}"]
        for meter_type in ("electricity", "water"):
            meter = meters[meter_type]
            if meter:
                lines.append(
                    f"{meter_type.title()}: {meter.meter_id} | prev {meter.previous_reading:.2f} | "
                    f"current {meter.current_reading:.2f} | usage {meter.get_usage():.2f}"
                )
            else:
                lines.append(f"{meter_type.title()}: Not assigned")
        self.customer_meter_text.delete("1.0", "end")
        self.customer_meter_text.insert("1.0", "\n".join(lines))
        self.set_status(f"Loaded meters for {customer_id}.")
