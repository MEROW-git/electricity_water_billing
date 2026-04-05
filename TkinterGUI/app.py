"""Tkinter desktop UI for the billing system."""

from __future__ import annotations

import os
import sys
import tkinter as tk
from tkinter import ttk


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from auth.auth import AuthManager
from controllers.billing_controller import BillingController
from controllers.customer_controller import CustomerController
from controllers.meter_controller import MeterController
from controllers.payment_controller import PaymentController
from reports.report import ReportGenerator
from utils.file_handler import initialize_data_files
from TkinterGUI.pages.billing_page import BillingPage
from TkinterGUI.pages.customer_page import CustomerPage
from TkinterGUI.pages.dashboard_page import DashboardPage
from TkinterGUI.pages.login_page import LoginPage
from TkinterGUI.pages.meter_page import MeterPage
from TkinterGUI.pages.payment_page import PaymentPage
from TkinterGUI.pages.reading_page import ReadingPage
from TkinterGUI.pages.reports_page import ReportsPage
from TkinterGUI.pages.users_page import UsersPage


class BillingGUI(tk.Tk):
    """Main Tkinter application."""

    def __init__(self):
        super().__init__()
        initialize_data_files()

        self.title("Electricity & Water Billing System")
        self.state("zoomed")
        self.resizable(False, False)
        self.configure(bg="#eef3f8")

        self.auth = AuthManager()
        self.customer_ctrl = CustomerController()
        self.meter_ctrl = MeterController()
        self.billing_ctrl = BillingController()
        self.payment_ctrl = PaymentController()
        self.reports = ReportGenerator()

        self.style = ttk.Style(self)
        self._configure_styles()

        self.current_screen = None
        self.sidebar = None
        self.content = None
        self.page_instances = {}

        self.show_login()

    def _configure_styles(self):
        self.style.theme_use("clam")
        self.style.configure("App.TFrame", background="#eef3f8")
        self.style.configure("Sidebar.TFrame", background="#16324f")
        self.style.configure("Card.TFrame", background="#ffffff")
        self.style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"), background="#eef3f8", foreground="#17324d")
        self.style.configure("Muted.TLabel", font=("Segoe UI", 10), background="#eef3f8", foreground="#536779")
        self.style.configure("CardTitle.TLabel", font=("Segoe UI", 13, "bold"), background="#ffffff", foreground="#17324d")
        self.style.configure("CardText.TLabel", font=("Segoe UI", 10), background="#ffffff", foreground="#536779")
        self.style.configure("Sidebar.TLabel", font=("Segoe UI", 16, "bold"), background="#16324f", foreground="#ffffff")
        self.style.configure("SidebarSmall.TLabel", font=("Segoe UI", 10), background="#16324f", foreground="#d5e1eb")
        self.style.configure("Nav.TButton", font=("Segoe UI", 10))
        self.style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def show_login(self):
        if self.current_screen is not None:
            self.current_screen.destroy()
        self.current_screen = LoginPage(self)
        self.current_screen.pack(fill="both", expand=True)

    def show_workspace(self):
        if self.current_screen is not None:
            self.current_screen.destroy()

        container = ttk.Frame(self, style="App.TFrame")
        container.pack(fill="both", expand=True)
        self.current_screen = container

        self.sidebar = ttk.Frame(container, width=260, padding=18, style="Sidebar.TFrame")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.content = ttk.Frame(container, padding=18, style="App.TFrame")
        self.content.pack(side="right", fill="both", expand=True)

        self.page_instances = {}
        self._build_sidebar()
        self.show_page("dashboard")

    def _build_sidebar(self):
        permissions = self.auth.get_menu_access()

        ttk.Label(self.sidebar, text="Billing System", style="Sidebar.TLabel").pack(anchor="w")
        ttk.Label(self.sidebar, text=f"{self.auth.current_user} ({self.auth.current_role})", style="SidebarSmall.TLabel").pack(anchor="w", pady=(6, 18))

        nav_items = [
            ("dashboard", "Dashboard", True),
            ("customers", "Customer Management", permissions.get("customer_manage")),
            ("meters", "Meter Management", permissions.get("meter_manage")),
            ("readings", "Meter Reading", permissions.get("reading_manage")),
            ("billing", "Billing & Invoices", permissions.get("billing_manage")),
            ("payments", "Payments", permissions.get("payment_manage")),
            ("reports", "Reports", permissions.get("reports")),
            ("users", "User Management", permissions.get("user_manage")),
        ]

        for page_key, label, allowed in nav_items:
            if allowed:
                ttk.Button(self.sidebar, text=label, style="Nav.TButton", command=lambda key=page_key: self.show_page(key)).pack(fill="x", pady=4)

        ttk.Button(self.sidebar, text="Logout", command=self.logout).pack(side="bottom", fill="x", pady=(18, 0))

    def show_page(self, page_name: str):
        for child in self.content.winfo_children():
            child.pack_forget()

        if page_name not in self.page_instances:
            pages = {
                "dashboard": DashboardPage,
                "customers": CustomerPage,
                "meters": MeterPage,
                "readings": ReadingPage,
                "billing": BillingPage,
                "payments": PaymentPage,
                "reports": ReportsPage,
                "users": UsersPage,
            }
            self.page_instances[page_name] = pages[page_name](self.content, self)

        page = self.page_instances[page_name]
        page.pack(fill="both", expand=True)
        if hasattr(page, "refresh"):
            page.refresh()

    def logout(self):
        self.auth.logout()
        self.show_login()

    def refresh_sidebar(self):
        if self.sidebar is None or self.current_screen is None or self.content is None:
            return
        self.sidebar.destroy()
        self.sidebar = ttk.Frame(self.current_screen, width=260, padding=18, style="Sidebar.TFrame")
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        self._build_sidebar()


def main():
    """Run the Tkinter desktop app."""
    app = BillingGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
