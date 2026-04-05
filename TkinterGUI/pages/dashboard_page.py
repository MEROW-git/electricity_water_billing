"""Dashboard page."""

from __future__ import annotations

from tkinter import ttk

from TkinterGUI.pages.base_page import BasePage


class DashboardPage(BasePage):
    """Summary landing page."""

    def __init__(self, parent, app):
        super().__init__(parent, app, "Dashboard", "Overview of the billing system data.")
        self.cards_frame = ttk.Frame(self, style="App.TFrame")
        self.cards_frame.pack(fill="x", pady=(4, 12))
        self.add_status_bar()

    def refresh(self):
        for child in self.cards_frame.winfo_children():
            child.destroy()

        customers = self.app.customer_ctrl.get_all_customers()
        meters = self.app.meter_ctrl.get_all_meters()
        bills = self.app.billing_ctrl.get_all_bills()
        payments = self.app.payment_ctrl.get_all_payments()
        unpaid = self.app.billing_ctrl.get_unpaid_bills()

        stats = [
            ("Customers", str(len([c for c in customers.values() if c.is_active]))),
            ("Meters", str(len(meters))),
            ("Bills", str(len(bills))),
            ("Payments", str(len(payments))),
            ("Unpaid Bills", str(len(unpaid))),
        ]

        for index, (label, value) in enumerate(stats):
            card = ttk.Frame(self.cards_frame, padding=18, style="Card.TFrame")
            card.grid(row=0, column=index, sticky="nsew", padx=(0 if index == 0 else 8, 0))
            ttk.Label(card, text=label, style="CardText.TLabel").pack(anchor="w")
            ttk.Label(card, text=value, style="CardTitle.TLabel").pack(anchor="w", pady=(10, 0))
            self.cards_frame.columnconfigure(index, weight=1)

        self.set_status("Dashboard refreshed.")
