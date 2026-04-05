"""Payments page."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from TkinterGUI.pages.base_page import BasePage


class PaymentPage(BasePage):
    """Page for recording and viewing payments."""

    def __init__(self, parent, app):
        super().__init__(parent, app, "Payments", "Record bill payments and review payment history.")

        form = ttk.LabelFrame(self, text="Record Payment", padding=16)
        form.pack(fill="x", pady=(0, 12))

        self.bill_id_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.customer_filter_var = tk.StringVar()

        ttk.Label(form, text="Bill ID").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Amount").grid(row=0, column=1, sticky="w")
        ttk.Label(form, text="Customer Filter").grid(row=0, column=2, sticky="w")
        ttk.Entry(form, textvariable=self.bill_id_var).grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Entry(form, textvariable=self.amount_var).grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Entry(form, textvariable=self.customer_filter_var).grid(row=1, column=2, sticky="ew", padx=(0, 8), pady=(4, 10))
        ttk.Button(form, text="Pay Bill", command=self.pay_bill).grid(row=1, column=3, sticky="ew", padx=(0, 8))
        ttk.Button(form, text="Filter By Customer", command=self.filter_by_customer).grid(row=1, column=4, sticky="ew")
        for idx in range(5):
            form.columnconfigure(idx, weight=1)

        columns = ("payment_id", "date", "bill_id", "customer_id", "amount")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col, text, width in [
            ("payment_id", "Payment ID", 180),
            ("date", "Date", 180),
            ("bill_id", "Bill ID", 200),
            ("customer_id", "Customer", 120),
            ("amount", "Amount", 120),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width)
        self.tree.pack(fill="both", expand=True)

        self.add_status_bar()

    def refresh(self):
        payments = list(self.app.payment_ctrl.get_all_payments().values())
        self.populate(payments)
        self.set_status(f"Loaded {len(payments)} payment record(s).")

    def populate(self, payments):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for payment in sorted(payments, key=lambda p: p["date"], reverse=True):
            self.tree.insert(
                "",
                "end",
                values=(
                    payment["payment_id"],
                    payment["date"],
                    payment["bill_id"],
                    payment["customer_id"],
                    f"{payment['amount']:,.0f}",
                ),
            )

    def pay_bill(self):
        try:
            amount = float(self.amount_var.get().strip())
        except ValueError:
            self.error("Invalid amount", "Payment amount must be numeric.")
            return
        bill_id = self.bill_id_var.get().strip().upper()
        success, message, remaining = self.app.payment_ctrl.record_payment(bill_id, amount)
        if success:
            self.refresh()
            self.set_status(f"{message} Remaining: {remaining:,.0f} Riel")
        else:
            self.error("Payment failed", message)

    def filter_by_customer(self):
        customer_id = self.customer_filter_var.get().strip().upper()
        if not customer_id:
            self.refresh()
            return
        payments = self.app.payment_ctrl.get_customer_payments(customer_id)
        self.populate(payments)
        self.set_status(f"Showing {len(payments)} payment(s) for {customer_id}.")
