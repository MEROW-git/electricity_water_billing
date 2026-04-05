"""Customer management page."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from TkinterGUI.pages.base_page import BasePage


class CustomerPage(BasePage):
    """Customer CRUD page."""

    def __init__(self, parent, app):
        super().__init__(parent, app, "Customer Management", "Create, search, and update customer records.")

        controls = ttk.Frame(self, style="App.TFrame")
        controls.pack(fill="x", pady=(0, 12))
        self.search_var = tk.StringVar()
        ttk.Entry(controls, textvariable=self.search_var, width=32).pack(side="left")
        ttk.Button(controls, text="Search", command=self.search_customers).pack(side="left", padx=8)
        ttk.Button(controls, text="Show All", command=self.refresh).pack(side="left")

        form = ttk.LabelFrame(self, text="Customer Form", padding=16)
        form.pack(fill="x", pady=(0, 12))

        self.selected_customer_id = None
        self.name_var = tk.StringVar()
        self.phone_var = tk.StringVar()
        self.address_var = tk.StringVar()

        ttk.Label(form, text="Full Name").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Phone Number").grid(row=0, column=1, sticky="w")
        ttk.Label(form, text="Address").grid(row=0, column=2, sticky="w")

        ttk.Entry(form, textvariable=self.name_var).grid(row=1, column=0, sticky="ew", padx=(0, 10), pady=(4, 10))
        ttk.Entry(form, textvariable=self.phone_var).grid(row=1, column=1, sticky="ew", padx=(0, 10), pady=(4, 10))
        ttk.Entry(form, textvariable=self.address_var).grid(row=1, column=2, sticky="ew", padx=(0, 10), pady=(4, 10))

        ttk.Button(form, text="Add Customer", command=self.add_customer).grid(row=1, column=3, sticky="ew", padx=(0, 6))
        ttk.Button(form, text="Update Selected", command=self.update_customer).grid(row=1, column=4, sticky="ew")

        for col in range(5):
            form.columnconfigure(col, weight=1 if col < 3 else 0)

        table_frame = ttk.Frame(self, style="App.TFrame")
        table_frame.pack(fill="both", expand=True)

        columns = ("customer_id", "name", "phone", "address", "created_date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        for col, text, width in [
            ("customer_id", "Customer ID", 120),
            ("name", "Name", 220),
            ("phone", "Phone", 130),
            ("address", "Address", 300),
            ("created_date", "Created", 110),
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.add_status_bar()

    def refresh(self):
        customers = self.app.customer_ctrl.get_all_customers()
        items = [c for c in customers.values() if c.is_active]
        self.populate(items)
        self.set_status(f"Loaded {len(items)} active customer(s).")

    def populate(self, customers):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for customer in customers:
            self.tree.insert("", "end", values=(customer.customer_id, customer.name, customer.phone, customer.address, customer.created_date))

    def on_select(self, _event):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self.selected_customer_id = values[0]
        self.name_var.set(values[1])
        self.phone_var.set(values[2])
        self.address_var.set(values[3])
        self.set_status(f"Selected customer {self.selected_customer_id}.")

    def add_customer(self):
        success, message, customer_id = self.app.customer_ctrl.add_customer(
            self.name_var.get().strip(),
            self.phone_var.get().strip(),
            self.address_var.get().strip(),
        )
        if success:
            self.name_var.set("")
            self.phone_var.set("")
            self.address_var.set("")
            self.refresh()
            self.set_status(f"{message} ({customer_id})")
        else:
            self.error("Unable to add customer", message)

    def update_customer(self):
        if not self.selected_customer_id:
            self.warn("No selection", "Please select a customer first.")
            return
        success, message = self.app.customer_ctrl.update_customer(
            self.selected_customer_id,
            self.name_var.get().strip() or None,
            self.phone_var.get().strip() or None,
            self.address_var.get().strip() or None,
        )
        if success:
            self.refresh()
            self.set_status(message)
        else:
            self.error("Unable to update customer", message)

    def search_customers(self):
        keyword = self.search_var.get().strip()
        if not keyword:
            self.refresh()
            return
        results = self.app.customer_ctrl.search_customers(keyword)
        self.populate(results)
        self.set_status(f"Found {len(results)} customer(s) for '{keyword}'.")
