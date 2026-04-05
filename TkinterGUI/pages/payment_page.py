"""Payments page."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from TkinterGUI.pages.base_page import BasePage
from TkinterGUI.widgets.customer_combobox import CustomerCombobox


class PaymentPage(BasePage):
    """Page for recording payments against the newest unpaid bill only."""

    def __init__(self, parent, app):
        super().__init__(parent, app, "Payments", "Pay only the newest generated unpaid bill for each customer.")

        self.bill_lookup = {}
        self.selected_bill_id = None

        form = ttk.LabelFrame(self, text="Record Payment", padding=16)
        form.pack(fill="x", pady=(0, 12))

        self.bill_id_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.customer_var = tk.StringVar()
        self.period_var = tk.StringVar(value="Period: N/A")
        self.total_var = tk.StringVar(value="Total bill: N/A")
        self.paid_var = tk.StringVar(value="Paid so far: N/A")
        self.balance_var = tk.StringVar(value="Amount to pay: N/A")

        ttk.Label(form, text="Customer").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Bill ID").grid(row=0, column=1, sticky="w")
        ttk.Label(form, text="Payment Amount").grid(row=0, column=2, sticky="w")

        self.customer_combo = CustomerCombobox(form, self.app, textvariable=self.customer_var)
        self.customer_combo.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(4, 8))
        self.customer_combo.bind("<<ComboboxSelected>>", self.on_customer_selected)
        self.customer_combo.bind("<FocusOut>", self.on_customer_selected)

        bill_entry = ttk.Entry(form, textvariable=self.bill_id_var)
        bill_entry.grid(row=1, column=1, sticky="ew", padx=(0, 8), pady=(4, 8))
        bill_entry.bind("<FocusOut>", self.on_bill_id_entered)

        ttk.Entry(form, textvariable=self.amount_var).grid(row=1, column=2, sticky="ew", padx=(0, 8), pady=(4, 8))
        ttk.Button(form, text="Pay Selected Bill", command=self.pay_bill).grid(row=1, column=3, sticky="ew")

        ttk.Label(form, textvariable=self.period_var, style="Muted.TLabel").grid(row=2, column=0, sticky="w")
        ttk.Label(form, textvariable=self.total_var, style="Muted.TLabel").grid(row=2, column=1, sticky="w")
        ttk.Label(form, textvariable=self.paid_var, style="Muted.TLabel").grid(row=2, column=2, sticky="w")
        ttk.Label(form, textvariable=self.balance_var, style="Muted.TLabel").grid(row=2, column=3, sticky="w")

        for idx in range(4):
            form.columnconfigure(idx, weight=1)

        list_frame = ttk.LabelFrame(self, text="Newest Unpaid Bill Per Customer", padding=12)
        list_frame.pack(fill="both", expand=True)

        search_row = ttk.Frame(list_frame)
        search_row.pack(fill="x", pady=(0, 8))
        self.search_var = tk.StringVar()
        ttk.Label(search_row, text="Search").pack(side="left", padx=(0, 8))
        search_entry = ttk.Entry(search_row, textvariable=self.search_var)
        search_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(search_row, text="Find", command=self.apply_search).pack(side="left", padx=8)
        ttk.Button(search_row, text="Clear", command=self.clear_search).pack(side="left")
        ttk.Label(
            search_row,
            text="Search by customer ID, customer name, bill ID, or period",
            style="Muted.TLabel",
        ).pack(side="left", padx=(12, 0))
        self.search_var.trace_add("write", self.on_search_change)

        columns = ("customer_id", "customer_name", "bill_id", "period", "total", "paid", "balance", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col, text, width in [
            ("customer_id", "Customer ID", 120),
            ("customer_name", "Customer Name", 220),
            ("bill_id", "Bill ID", 180),
            ("period", "Period", 100),
            ("total", "Total", 110),
            ("paid", "Paid", 110),
            ("balance", "To Pay", 110),
            ("status", "Status", 90),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.history = tk.Text(self, height=8, wrap="word")
        self.history.pack(fill="x", pady=(12, 0))
        self.add_status_bar()

    def refresh(self):
        self.customer_combo.refresh_values()
        latest_bills = self.app.billing_ctrl.get_latest_payable_bills()
        customers = self.app.customer_ctrl.get_all_customers()

        self.bill_lookup = {}
        self.rows = []
        for bill in sorted(latest_bills, key=lambda item: (item.year, item.month, item.customer_id), reverse=True):
            customer = customers.get(bill.customer_id)
            customer_name = customer.name if customer else bill.customer_id
            row = (
                bill.customer_id,
                customer_name,
                bill.bill_id,
                bill.period,
                f"{bill.total_amount:,.0f}",
                f"{bill.paid_amount:,.0f}",
                f"{bill.get_balance():,.0f}",
                bill.status,
            )
            self.bill_lookup[bill.bill_id] = bill
            self.rows.append(row)

        self.apply_search()
        self.history.delete("1.0", "end")
        self.history.insert("1.0", "Select a newest unpaid bill from the table or choose a customer to auto-fill the form.")
        self.set_status(f"Loaded {len(self.rows)} newest unpaid bill(s).")

    def on_search_change(self, *_args):
        self.apply_search()

    def apply_search(self):
        keyword = self.search_var.get().strip().lower()
        if not keyword:
            filtered = self.rows
        else:
            filtered = []
            for row in self.rows:
                customer_id, customer_name, bill_id, period, *_rest = row
                if (
                    keyword in customer_id.lower()
                    or keyword in customer_name.lower()
                    or keyword in bill_id.lower()
                    or keyword in period.lower()
                ):
                    filtered.append(row)

        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in filtered:
            self.tree.insert("", "end", values=row)

    def clear_search(self):
        self.search_var.set("")

    def on_tree_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        bill_id = self.tree.item(selected[0], "values")[2]
        bill = self.bill_lookup.get(bill_id)
        if bill:
            self.load_bill_into_form(bill)

    def on_customer_selected(self, _event=None):
        customer_id = self.customer_combo.get_customer_id()
        if not customer_id:
            return
        bill = self.app.billing_ctrl.get_latest_payable_bill_for_customer(customer_id)
        if not bill:
            self.clear_bill_details()
            self.warn("No payable bill", f"{customer_id} has no newest unpaid bill to pay.")
            return
        self.load_bill_into_form(bill)

    def on_bill_id_entered(self, _event=None):
        bill_id = self.bill_id_var.get().strip().upper()
        if not bill_id:
            return
        bill = self.app.billing_ctrl.get_bill(bill_id)
        if not bill:
            self.clear_bill_details()
            self.error("Bill not found", f"{bill_id} was not found.")
            return

        latest = self.app.billing_ctrl.get_latest_payable_bill_for_customer(bill.customer_id)
        if latest is None:
            self.clear_bill_details()
            self.warn("No payable bill", f"{bill.customer_id} has no unpaid bill to pay.")
            return
        if latest.bill_id != bill.bill_id:
            self.load_bill_into_form(latest)
            self.warn("Older bill blocked", f"Only the newest unpaid bill can be paid. Latest bill is {latest.bill_id}.")
            return

        self.load_bill_into_form(bill)

    def load_bill_into_form(self, bill):
        self.selected_bill_id = bill.bill_id
        self.bill_id_var.set(bill.bill_id)
        self.customer_var.set(bill.customer_id)
        self.amount_var.set(f"{bill.get_balance():.0f}")
        self.period_var.set(f"Period: {bill.period}")
        self.total_var.set(f"Total bill: {bill.total_amount:,.0f} Riel")
        self.paid_var.set(f"Paid so far: {bill.paid_amount:,.0f} Riel")
        self.balance_var.set(f"Amount to pay: {bill.get_balance():,.0f} Riel")
        self.history.delete("1.0", "end")
        self.history.insert("1.0", self.app.billing_ctrl.display_bill(bill))
        self.set_status(f"Loaded payable bill {bill.bill_id} for {bill.customer_id}.")

    def clear_bill_details(self):
        self.selected_bill_id = None
        self.amount_var.set("")
        self.period_var.set("Period: N/A")
        self.total_var.set("Total bill: N/A")
        self.paid_var.set("Paid so far: N/A")
        self.balance_var.set("Amount to pay: N/A")

    def pay_bill(self):
        bill_id = self.bill_id_var.get().strip().upper()
        if not bill_id:
            self.warn("Missing bill", "Select or enter a bill ID first.")
            return

        try:
            amount = float(self.amount_var.get().strip())
        except ValueError:
            self.error("Invalid amount", "Payment amount must be numeric.")
            return

        success, message, remaining = self.app.payment_ctrl.record_payment(bill_id, amount)
        if success:
            self.refresh()
            latest = self.app.billing_ctrl.get_bill(bill_id)
            self.history.delete("1.0", "end")
            self.history.insert("1.0", f"{message}\nRemaining: {remaining:,.0f} Riel")
            if latest and latest.status != "paid":
                self.load_bill_into_form(latest)
            else:
                self.clear_bill_details()
                self.bill_id_var.set("")
                self.customer_var.set("")
            self.set_status(f"Payment recorded for {bill_id}.")
        else:
            self.error("Payment failed", message)
