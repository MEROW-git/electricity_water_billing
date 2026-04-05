"""Meter reading page."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from TkinterGUI.pages.base_page import BasePage


class ReadingPage(BasePage):
    """Page for updating readings."""

    def __init__(self, parent, app):
        super().__init__(parent, app, "Meter Reading", "Update one meter or both readings for a customer.")

        single_box = ttk.LabelFrame(self, text="Update Single Meter", padding=16)
        single_box.pack(fill="x", pady=(0, 12))

        self.meter_id_var = tk.StringVar()
        self.single_reading_var = tk.StringVar()
        ttk.Label(single_box, text="Meter ID").grid(row=0, column=0, sticky="w")
        ttk.Label(single_box, text="New Reading").grid(row=0, column=1, sticky="w")
        ttk.Entry(single_box, textvariable=self.meter_id_var).grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Entry(single_box, textvariable=self.single_reading_var).grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Button(single_box, text="Update Meter", command=self.update_single_meter).grid(row=1, column=2, sticky="ew")
        for idx in range(3):
            single_box.columnconfigure(idx, weight=1)

        both_box = ttk.LabelFrame(self, text="Update Both Readings For Customer", padding=16)
        both_box.pack(fill="x", pady=(0, 12))

        self.customer_id_var = tk.StringVar()
        self.electricity_var = tk.StringVar()
        self.water_var = tk.StringVar()

        ttk.Label(both_box, text="Customer ID").grid(row=0, column=0, sticky="w")
        ttk.Label(both_box, text="Electricity Reading").grid(row=0, column=1, sticky="w")
        ttk.Label(both_box, text="Water Reading").grid(row=0, column=2, sticky="w")
        ttk.Entry(both_box, textvariable=self.customer_id_var).grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Entry(both_box, textvariable=self.electricity_var).grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Entry(both_box, textvariable=self.water_var).grid(row=1, column=2, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Button(both_box, text="Update Both", command=self.update_both_readings).grid(row=1, column=3, sticky="ew")
        for idx in range(4):
            both_box.columnconfigure(idx, weight=1)

        self.output = tk.Text(self, wrap="word")
        self.output.pack(fill="both", expand=True)
        self.add_status_bar()

    def update_single_meter(self):
        try:
            reading = float(self.single_reading_var.get().strip())
        except ValueError:
            self.error("Invalid value", "Reading must be numeric.")
            return
        meter_id = self.meter_id_var.get().strip().upper()
        success, message, usage = self.app.meter_ctrl.update_reading(meter_id, reading)
        if success:
            self.output.delete("1.0", "end")
            self.output.insert("1.0", f"{message}\nUsage this period: {usage:.2f}")
            self.set_status(f"Updated {meter_id}.")
        else:
            self.error("Unable to update reading", message)

    def update_both_readings(self):
        customer_id = self.customer_id_var.get().strip().upper()
        meters = self.app.meter_ctrl.get_customer_meters(customer_id)
        if not meters["electricity"] or not meters["water"]:
            self.error("Missing meters", "Customer does not have both meters assigned.")
            return
        try:
            elec = float(self.electricity_var.get().strip())
            water = float(self.water_var.get().strip())
        except ValueError:
            self.error("Invalid value", "Both readings must be numeric.")
            return
        s1, m1, u1 = self.app.meter_ctrl.update_reading(meters["electricity"].meter_id, elec)
        s2, m2, u2 = self.app.meter_ctrl.update_reading(meters["water"].meter_id, water)
        if s1 and s2:
            self.output.delete("1.0", "end")
            self.output.insert(
                "1.0",
                f"Electricity: {m1} (Usage: {u1:.2f})\nWater: {m2} (Usage: {u2:.2f})",
            )
            self.set_status(f"Updated both readings for {customer_id}.")
        else:
            self.error("Unable to update both readings", f"Electricity: {m1}\nWater: {m2}")
