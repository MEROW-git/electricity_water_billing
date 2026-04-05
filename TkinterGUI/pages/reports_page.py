"""Reports page."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from TkinterGUI.pages.base_page import BasePage


class ReportsPage(BasePage):
    """Generate text reports."""

    def __init__(self, parent, app):
        super().__init__(parent, app, "Reports", "Generate monthly, yearly, unpaid, and customer reports.")

        controls = ttk.LabelFrame(self, text="Report Controls", padding=16)
        controls.pack(fill="x", pady=(0, 12))

        self.year_var = tk.StringVar()
        self.month_var = tk.StringVar()
        self.customer_id_var = tk.StringVar()

        ttk.Label(controls, text="Year").grid(row=0, column=0, sticky="w")
        ttk.Label(controls, text="Month").grid(row=0, column=1, sticky="w")
        ttk.Label(controls, text="Customer ID").grid(row=0, column=2, sticky="w")
        ttk.Entry(controls, textvariable=self.year_var).grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Entry(controls, textvariable=self.month_var).grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Entry(controls, textvariable=self.customer_id_var).grid(row=1, column=2, sticky="ew", padx=(0, 8), pady=(4, 10))

        ttk.Button(controls, text="Monthly Report", command=self.show_monthly).grid(row=1, column=3, sticky="ew", padx=(0, 8))
        ttk.Button(controls, text="Yearly Report", command=self.show_yearly).grid(row=1, column=4, sticky="ew", padx=(0, 8))
        ttk.Button(controls, text="Unpaid Bills", command=self.show_unpaid).grid(row=1, column=5, sticky="ew", padx=(0, 8))
        ttk.Button(controls, text="Customer Statement", command=self.show_customer_statement).grid(row=1, column=6, sticky="ew")

        for idx in range(7):
            controls.columnconfigure(idx, weight=1)

        self.output = tk.Text(self, wrap="word")
        self.output.pack(fill="both", expand=True)
        self.add_status_bar()

    def _parse_year(self):
        try:
            return int(self.year_var.get().strip())
        except ValueError:
            self.error("Invalid year", "Please enter a valid year.")
            return None

    def _parse_year_month(self):
        year = self._parse_year()
        if year is None:
            return None
        try:
            month = int(self.month_var.get().strip())
            if month < 1 or month > 12:
                raise ValueError
            return year, month
        except ValueError:
            self.error("Invalid month", "Please enter a valid month from 1 to 12.")
            return None

    def show_text(self, content, status):
        self.output.delete("1.0", "end")
        self.output.insert("1.0", content)
        self.set_status(status)

    def show_monthly(self):
        period = self._parse_year_month()
        if period:
            self.show_text(self.app.reports.monthly_report(period[0], period[1]), f"Generated monthly report for {period[0]}-{period[1]:02d}.")

    def show_yearly(self):
        year = self._parse_year()
        if year is not None:
            self.show_text(self.app.reports.yearly_report(year), f"Generated yearly report for {year}.")

    def show_unpaid(self):
        self.show_text(self.app.reports.unpaid_bills_report(), "Generated unpaid bills report.")

    def show_customer_statement(self):
        customer_id = self.customer_id_var.get().strip().upper()
        if not customer_id:
            self.warn("Missing customer", "Please enter a customer ID.")
            return
        self.show_text(self.app.reports.customer_statement(customer_id), f"Generated customer statement for {customer_id}.")
