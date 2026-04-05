"""Billing and invoice page."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from utils.file_handler import load_json
from TkinterGUI.pages.base_page import BasePage
from TkinterGUI.widgets.customer_combobox import CustomerCombobox


class BillingPage(BasePage):
    """Page for bill generation and invoice viewing."""

    def __init__(self, parent, app):
        super().__init__(parent, app, "Billing & Invoices", "Generate bills, inspect invoices, and export them.")

        top = ttk.Frame(self, style="App.TFrame")
        top.pack(fill="x", pady=(0, 12))

        single = ttk.LabelFrame(top, text="Generate Single Bill", padding=16)
        single.pack(side="left", fill="both", expand=True, padx=(0, 8))

        self.customer_id_var = tk.StringVar()
        self.year_var = tk.StringVar()
        self.month_var = tk.StringVar()
        for idx, label in enumerate(("Customer ID", "Year", "Month")):
            ttk.Label(single, text=label).grid(row=0, column=idx, sticky="w")
        self.customer_combo = CustomerCombobox(single, self.app, textvariable=self.customer_id_var)
        self.customer_combo.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Entry(single, textvariable=self.year_var).grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Entry(single, textvariable=self.month_var).grid(row=1, column=2, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Button(single, text="Generate Bill", command=self.generate_single_bill).grid(row=1, column=3, sticky="ew")
        for idx in range(4):
            single.columnconfigure(idx, weight=1)

        bulk = ttk.LabelFrame(top, text="Generate All Bills", padding=16)
        bulk.pack(side="right", fill="both", expand=True)

        self.all_year_var = tk.StringVar()
        self.all_month_var = tk.StringVar()
        ttk.Label(bulk, text="Year").grid(row=0, column=0, sticky="w")
        ttk.Label(bulk, text="Month").grid(row=0, column=1, sticky="w")
        ttk.Entry(bulk, textvariable=self.all_year_var).grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Entry(bulk, textvariable=self.all_month_var).grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Button(bulk, text="Generate All", command=self.generate_all_bills).grid(row=1, column=2, sticky="ew")
        for idx in range(3):
            bulk.columnconfigure(idx, weight=1)

        middle = ttk.Frame(self, style="App.TFrame")
        middle.pack(fill="both", expand=True)

        left = ttk.Frame(middle, style="App.TFrame")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        controls = ttk.Frame(left, style="App.TFrame")
        controls.pack(fill="x", pady=(0, 8))
        ttk.Button(controls, text="Refresh Bills", command=self.refresh).pack(side="left")
        ttk.Button(controls, text="Show Unpaid", command=self.show_unpaid_bills).pack(side="left", padx=8)
        ttk.Button(controls, text="View Customer Bills", command=self.show_customer_bills).pack(side="left")

        columns = ("bill_id", "period", "customer_id", "total", "status")
        self.tree = ttk.Treeview(left, columns=columns, show="headings")
        for col, text, width in [
            ("bill_id", "Bill ID", 200),
            ("period", "Period", 100),
            ("customer_id", "Customer", 120),
            ("total", "Total", 120),
            ("status", "Status", 100),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width)
        self.tree.bind("<<TreeviewSelect>>", self.on_select_bill)
        self.tree.pack(fill="both", expand=True)

        right = ttk.Frame(middle, style="App.TFrame")
        right.pack(side="right", fill="both", expand=True)

        action_box = ttk.Frame(right, style="App.TFrame")
        action_box.pack(fill="x", pady=(0, 8))
        ttk.Button(action_box, text="Export Selected To Text", command=self.export_selected_text).pack(side="left")
        ttk.Button(action_box, text="Export Selected To PDF", command=self.export_selected_pdf).pack(side="left", padx=8)
        ttk.Button(action_box, text="Export Period To PDF", command=self.export_period_pdf).pack(side="left")

        self.details = tk.Text(right, wrap="word")
        self.details.pack(fill="both", expand=True)

        self.selected_bill_id = None
        self.add_status_bar()

    def refresh(self):
        self.customer_combo.refresh_values()
        bills = list(self.app.billing_ctrl.get_all_bills().values())
        self.populate_bills(bills)
        self.set_status(f"Loaded {len(bills)} bill(s).")

    def populate_bills(self, bills):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for bill in sorted(bills, key=lambda b: (b.year, b.month, b.customer_id), reverse=True):
            self.tree.insert("", "end", values=(bill.bill_id, bill.period, bill.customer_id, f"{bill.total_amount:,.0f}", bill.status))

    def parse_period(self, year_var, month_var):
        try:
            year = int(year_var.get().strip())
            month = int(month_var.get().strip())
            if month < 1 or month > 12:
                raise ValueError
            return year, month
        except ValueError:
            self.error("Invalid period", "Please enter a valid year and month (1-12).")
            return None

    def generate_single_bill(self):
        period = self.parse_period(self.year_var, self.month_var)
        if not period:
            return
        customer_id = self.customer_combo.get_customer_id()
        if not customer_id:
            self.error("Customer not found", "Choose or type a valid customer ID.")
            return
        success, message, bill = self.app.billing_ctrl.generate_monthly_bill(customer_id, period[0], period[1])
        if success:
            self.refresh()
            self.details.delete("1.0", "end")
            self.details.insert("1.0", self.app.billing_ctrl.display_bill(bill))
            self.set_status(message)
        else:
            self.error("Unable to generate bill", message)

    def generate_all_bills(self):
        period = self.parse_period(self.all_year_var, self.all_month_var)
        if not period:
            return
        generated, skipped = self.app.billing_ctrl.generate_all_monthly_bills(period[0], period[1])
        self.refresh()
        lines = [f"Generated: {len(generated)}", f"Skipped: {len(skipped)}"]
        for cid, bid in generated:
            lines.append(f"{cid} -> {bid}")
        for cid, reason in skipped:
            lines.append(f"{cid}: {reason}")
        self.details.delete("1.0", "end")
        self.details.insert("1.0", "\n".join(lines))
        self.set_status(f"Generated {len(generated)} bill(s).")

    def on_select_bill(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        self.selected_bill_id = self.tree.item(selected[0], "values")[0]
        bill = self.app.billing_ctrl.get_bill(self.selected_bill_id)
        self.details.delete("1.0", "end")
        self.details.insert("1.0", self.app.billing_ctrl.display_bill(bill))
        self.set_status(f"Selected {self.selected_bill_id}.")

    def show_unpaid_bills(self):
        unpaid = self.app.billing_ctrl.get_unpaid_bills()
        self.populate_bills(unpaid)
        self.set_status(f"Showing {len(unpaid)} unpaid bill(s).")

    def show_customer_bills(self):
        customer_id = self.customer_combo.get_customer_id()
        if not customer_id:
            self.warn("Missing customer", "Enter a customer ID in the single-bill area first.")
            return
        bills = self.app.billing_ctrl.get_customer_bills(customer_id)
        self.populate_bills(bills)
        self.set_status(f"Showing {len(bills)} bill(s) for {customer_id}.")

    def export_selected_text(self):
        bill = self._get_selected_bill()
        if not bill:
            return
        customers = load_json("customers.json", {})
        cust = customers.get(bill.customer_id)
        name = cust.get("name") if cust else None
        path = self.app.billing_ctrl.export_bill_to_text(bill, out_dir="prints", customer_name=name)
        self.set_status(f"Exported text invoice to {path}.")

    def export_selected_pdf(self):
        bill = self._get_selected_bill()
        if not bill:
            return
        customers = load_json("customers.json", {})
        cust = customers.get(bill.customer_id)
        name = cust.get("name") if cust else None
        try:
            path = self.app.billing_ctrl.export_bill_to_pdf(bill, out_dir="prints", customer_name=name)
            self.set_status(f"Exported PDF invoice to {path}.")
        except ImportError as exc:
            self.error("PDF export unavailable", str(exc))

    def export_period_pdf(self):
        period = self.parse_period(self.all_year_var, self.all_month_var)
        if not period:
            return
        try:
            path, skipped = self.app.billing_ctrl.export_bills_to_pdf_period(period[0], period[1], out_dir="prints")
        except ImportError as exc:
            self.error("PDF export unavailable", str(exc))
            return
        if path:
            self.set_status(f"Exported period PDF to {path}.")
        else:
            self.warn("No bills exported", str(skipped))

    def _get_selected_bill(self):
        if not self.selected_bill_id:
            self.warn("No selection", "Please select a bill first.")
            return None
        return self.app.billing_ctrl.get_bill(self.selected_bill_id)
