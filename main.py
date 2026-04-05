#!/usr/bin/env python3
"""
Electricity & Water Supply Billing System


Main Application Entry Point
"""

import os
import sys

# Ensure all modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from auth.auth import AuthManager
from controllers.customer_controller import CustomerController
from controllers.meter_controller import MeterController
from controllers.billing_controller import BillingController
from controllers.payment_controller import PaymentController
from reports.report import ReportGenerator
from utils.file_handler import initialize_data_files, load_json

class BillingSystem:
    """Main application controller"""
    
    def __init__(self):
        self.auth = AuthManager()
        self.customer_ctrl = CustomerController()
        self.meter_ctrl = MeterController()
        self.billing_ctrl = BillingController()
        self.payment_ctrl = PaymentController()
        self.reports = ReportGenerator()
        
        # Initialize data files
        initialize_data_files()
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('clear' if os.name == 'posix' else 'cls')
    
    def display_project_info(self):
        """Display project information with lecture name and member group"""
        print("\n" + "="*60)
        print("  ELECTRICITY & WATER BILLING SYSTEM".center(60))
        print("="*60)
        print("\nLecture Name: Try Vorn".center(60))
        print("\nMember Group:".center(60))
        members = [
            "1. Kheuy Sophea",
            "2. Doeu Yongyan",
            "3. Po Chunhean",
            "4. Hong Mouyhoin",
            "5. Chan Sreynet",
            "6. Oeun Sreypich",
            "7. Horm Menghong",
            "8. Meas Puttivireak",
            "9. Roeurn Seiha"
        ]
        for member in members:
            print(member.center(60))
        print("="*60 + "\n")
    
    def print_header(self, title):
        """Print formatted header"""
        print("\n" + "="*60)
        print(f"  {title}".center(60))
        print("="*60)
    
    def get_input(self, prompt, required=True):
        """Get user input with validation"""
        while True:
            value = input(prompt).strip()
            if value or not required:
                return value
            print("This field is required. Please try again.")
    
    def get_number(self, prompt, min_val=None, max_val=None, allow_zero=True):
        """Get numeric input"""
        while True:
            try:
                value = float(input(prompt))
                if not allow_zero and value == 0:
                    print("Value cannot be zero.")
                    continue
                if min_val is not None and value < min_val:
                    print(f"Value must be at least {min_val}.")
                    continue
                if max_val is not None and value > max_val:
                    print(f"Value must be at most {max_val}.")
                    continue
                return value
            except ValueError:
                print("Please enter a valid number.")
    
    def pause(self):
        """Pause for user to read"""
        input("\nPress Enter to continue...")

    def prompt_customer_id(self, prompt):
        """Prompt for a customer identifier and resolve to full ID.

        Returns full ID or None if not found.
        """
        raw = self.get_input(prompt).strip()
        cust_id = self.customer_ctrl.resolve_customer_id(raw.upper())
        if not cust_id:
            print("Customer not found.")
        return cust_id
    
    # ==================== MENU SYSTEM ====================
    
    def main_menu(self):
        """Display main menu based on role"""
        permissions = self.auth.get_menu_access()
        
        print("\n" + "="*60)
        print("  MAIN MENU".center(60))
        print("="*60)
        
        options = []
        opt_num = 1
        
        if permissions.get("customer_manage"):
            print(f"  {opt_num}. Customer Management")
            options.append("customer")
            opt_num += 1
        
        if permissions.get("meter_manage"):
            print(f"  {opt_num}. Meter Management")
            options.append("meter")
            opt_num += 1
        
        if permissions.get("reading_manage"):
            print(f"  {opt_num}. Meter Reading")
            options.append("reading")
            opt_num += 1
        
        if permissions.get("billing_manage"):
            print(f"  {opt_num}. Billing & Invoices")
            options.append("billing")
            opt_num += 1
        
        if permissions.get("payment_manage"):
            print(f"  {opt_num}. Payments")
            options.append("payment")
            opt_num += 1
        
        if permissions.get("reports"):
            print(f"  {opt_num}. Reports")
            options.append("reports")
            opt_num += 1
        
        if permissions.get("user_manage"):
            print(f"  {opt_num}. User Management (Admin)")
            options.append("users")
            opt_num += 1
        
        print(f"  0. Logout")
        print("="*60)
        
        choice = input("Select option: ").strip()
        
        if choice == "0":
            return self.logout()
        
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        
        print("Invalid option!")
        return None
    
    # ==================== CUSTOMER MENU ====================
    
    def customer_menu(self):
        """Customer management submenu"""
        while True:
            self.print_header("CUSTOMER MANAGEMENT")
            print("1. Add New Customer")
            print("2. View All Customers")
            print("3. Search Customer")
            print("4. View Customer Details")
            print("5. Update Customer")
            print("0. Back to Main Menu")
            
            choice = input("\nSelect: ").strip()
            
            if choice == "1":
                self.add_customer_flow()
            elif choice == "2":
                print(self.customer_ctrl.display_customers())
            elif choice == "3":
                self.search_customer_flow()
            elif choice == "4":
                self.view_customer_flow()
            elif choice == "5":
                self.update_customer_flow()
            elif choice == "0":
                break
            else:
                print("Invalid option")
            
            self.pause()
    
    def add_customer_flow(self):
        """Add one or more new customers workflow"""
        self.print_header("ADD NEW CUSTOMER")

        # Ask how many customers to create
        while True:
            count_str = self.get_input("How many customers would you like to add? ")
            try:
                count = int(count_str)
                if count < 1:
                    print("Please enter a number greater than 0.")
                    continue
                break
            except ValueError:
                print("Please enter a valid integer.")

        for idx in range(count):
            print(f"\n--- Customer {idx+1} of {count} ---")
            name = self.get_input("Full Name: ")
            phone = self.get_input("Phone Number: ")
            address = self.get_input("Address: ")

            success, message, cust_id = self.customer_ctrl.add_customer(name, phone, address)

            if success:
                print(f"\n✓ {message}")
                print(f"Customer ID: {cust_id}")

                # Option to assign meters immediately
                assign = input("\nAssign meters now? (y/n): ").lower()
                if assign == 'y':
                    self.assign_meters_flow(cust_id)
            else:
                print(f"\n✗ {message}")

            # If more remain, ask whether to continue or abort early
            if idx < count - 1:
                cont = input("\nAdd next customer? (y/n): ").strip().lower()
                if cont != 'y':
                    print("Stopping customer entry early.")
                    break
    
    def search_customer_flow(self):
        """Search for customers"""
        keyword = self.get_input("Search (name/phone/ID): ")
        results = self.customer_ctrl.search_customers(keyword)
        
        if not results:
            print("No customers found.")
        else:
            print(f"\nFound {len(results)} customer(s):")
            for c in results:
                print(f"  {c}")
    
    def view_customer_flow(self):
        """View specific customer with meters and bills"""
        cust_id = self.prompt_customer_id("Enter Customer ID: ")
        if not cust_id:
            return
        customer = self.customer_ctrl.get_customer(cust_id)
        
        # resolve_customer_id already checked existence but double-check
        if not customer:
            print("Customer not found.")
            return
        
        print(f"\n--- CUSTOMER DETAILS ---")
        print(f"ID:       {customer.customer_id}")
        print(f"Name:     {customer.name}")
        print(f"Phone:    {customer.phone}")
        print(f"Address:  {customer.address}")
        print(f"Since:    {customer.created_date}")
        
        # Show meters
        meters = self.meter_ctrl.get_customer_meters(cust_id)
        print(f"\n--- METERS ---")
        for mtype, meter in meters.items():
            if meter:
                print(f"{mtype.title()}: {meter.meter_id}")
                print(f"  Current Reading: {meter.current_reading}")
                print(f"  Previous: {meter.previous_reading}")
                print(f"  Usage: {meter.get_usage()}")
            else:
                print(f"{mtype.title()}: Not assigned")
        
        # Show recent bills
        bills = self.billing_ctrl.get_customer_bills(cust_id)
        if bills:
            print(f"\n--- RECENT BILLS ---")
            for bill in sorted(bills, key=lambda x: x.period, reverse=True)[:5]:
                status_icon = "✓" if bill.status == "paid" else "✗"
                print(f"{status_icon} {bill.period}: {bill.total_amount:,.0f} Riel ({bill.status})")
    
    def update_customer_flow(self):
        """Update customer information"""
        cust_id = self.prompt_customer_id("Customer ID to update: ")
        if not cust_id:
            return
        customer = self.customer_ctrl.get_customer(cust_id)
        
        if not customer:
            print("Customer not found.")
            return
        
        print(f"Current Name: {customer.name}")
        name = input("New Name (press Enter to keep): ").strip()
        
        print(f"Current Phone: {customer.phone}")
        phone = input("New Phone (press Enter to keep): ").strip()
        
        print(f"Current Address: {customer.address}")
        address = input("New Address (press Enter to keep): ").strip()
        
        success, message = self.customer_ctrl.update_customer(
            cust_id, 
            name or None, 
            phone or None, 
            address or None
        )
        print(message)
    
    # ==================== METER MENU ====================
    
    def meter_menu(self):
        """Meter management submenu"""
        while True:
            self.print_header("METER MANAGEMENT")
            print("1. Assign Meters to Customer")
            print("2. View All Meters")
            print("3. View Customer Meters")
            print("0. Back to Main Menu")
            
            choice = input("\nSelect: ").strip()
            
            if choice == "1":
                cust_id = self.prompt_customer_id("Customer ID: ")
                if cust_id:
                    self.assign_meters_flow(cust_id)
            elif choice == "2":
                print(self.meter_ctrl.display_meters())
            elif choice == "3":
                cust_id = self.prompt_customer_id("Customer ID: ")
                if cust_id:
                    readings = self.meter_ctrl.get_reading_history(cust_id)
                    if readings["electricity"]:
                        print(f"\nElectricity: {readings['electricity']}")
                    if readings["water"]:
                        print(f"Water: {readings['water']}")
            elif choice == "0":
                break
            else:
                print("Invalid option")
            
            self.pause()
    
    def assign_meters_flow(self, customer_id):
        """Assign meters to customer"""
        # Check if customer exists
        customer = self.customer_ctrl.get_customer(customer_id)
        if not customer:
            print(f"Customer {customer_id} not found.")
            return
        
        print(f"\nAssigning meters to: {customer.name}")
        
        elec_prev = self.get_number("Initial Electricity Reading (kWh): ", min_val=0)
        water_prev = self.get_number("Initial Water Reading (m³): ", min_val=0)
        
        success, message, elec_id, water_id = self.meter_ctrl.assign_meters(
            customer_id, elec_prev, water_prev
        )
        
        if success:
            print(f"\n✓ {message}")
            print(f"Electricity Meter: {elec_id}")
            print(f"Water Meter: {water_id}")
        else:
            print(f"\n✗ {message}")
    
    # ==================== READING MENU ====================
    
    def reading_menu(self):
        """Meter reading submenu"""
        while True:
            self.print_header("METER READING")
            print("1. Input Electricity Reading")
            print("2. Input Water Reading")
            print("3. Input Both Readings")
            print("4. Input Both Readings for All Customers (Ctrl+C to stop anytime)")
            print("0. Back to Main Menu")
            
            choice = input("\nSelect: ").strip()
            
            if choice == "1":
                self.input_reading_flow("electricity")
            elif choice == "2":
                self.input_reading_flow("water")
            elif choice == "3":
                self.input_both_readings_flow()
            elif choice == "4":
                self.input_all_readings_flow()
            elif choice == "0":
                break
            else:
                print("Invalid option")
            
            self.pause()
    
    def input_reading_flow(self, meter_type):
        """Input reading for specific meter"""
        meter_id = self.get_input(f"Enter {meter_type.title()} Meter ID: ").upper()
        
        # Get current reading for reference
        meters = self.meter_ctrl.get_all_meters()
        if meter_id not in meters:
            print("Meter not found.")
            return
        
        meter = meters[meter_id]
        print(f"\nCurrent stored reading: {meter.current_reading}")
        
        new_reading = self.get_number(f"Enter new reading: ", min_val=meter.current_reading)
        
        success, message, usage = self.meter_ctrl.update_reading(meter_id, new_reading)
        print(f"\n{message}")
        if success:
            print(f"Usage this period: {usage:.2f} units")
    
    def input_both_readings_flow(self):
        """Input readings for both meters of a customer"""
        cust_id = self.prompt_customer_id("Customer ID: ")
        if not cust_id:
            return
        meters = self.meter_ctrl.get_customer_meters(cust_id)
        
        if not meters["electricity"] or not meters["water"]:
            print("Customer does not have both meters assigned.")
            return
        
        print(f"\n--- ELECTRICITY METER: {meters['electricity'].meter_id} ---")
        print(f"Previous: {meters['electricity'].current_reading}")
        elec_new = self.get_number("New Reading (kWh): ", min_val=meters['electricity'].current_reading)
        
        print(f"\n--- WATER METER: {meters['water'].meter_id} ---")
        print(f"Previous: {meters['water'].current_reading}")
        water_new = self.get_number("New Reading (m³): ", min_val=meters['water'].current_reading)
        
        # Update both
        s1, m1, u1 = self.meter_ctrl.update_reading(meters['electricity'].meter_id, elec_new)
        s2, m2, u2 = self.meter_ctrl.update_reading(meters['water'].meter_id, water_new)
        
        print(f"\nElectricity: {m1} (Usage: {u1:.2f} kWh)")
        print(f"Water: {m2} (Usage: {u2:.2f} m³)")

    def input_all_readings_flow(self):
        """Iterate through all customers and prompt for both readings.

        Skips any customer who already has both meters updated (current != previous)
        or who does not have both meters assigned.  User may interrupt with
        Ctrl+C to stop early.
        """
        meters = self.meter_ctrl.get_all_meters()
        # group meters by customer
        cust_map = {}
        for m in meters.values():
            cust_map.setdefault(m.customer_id, {})[m.meter_type] = m

        try:
            for cid, types in cust_map.items():
                elec = types.get("electricity")
                water = types.get("water")
                if not elec or not water:
                    continue
                # skip if both already updated
                if (elec.current_reading != elec.previous_reading and
                        water.current_reading != water.previous_reading):
                    continue

                customer = self.customer_ctrl.get_customer(cid)
                print(f"\n--- Customer {cid} ({customer.name}) ---")
                print(f"Electricity previous: {elec.current_reading}")
                elec_new = self.get_number("New Electricity Reading (kWh): ", min_val=elec.current_reading)
                print(f"Water previous: {water.current_reading}")
                water_new = self.get_number("New Water Reading (m³): ", min_val=water.current_reading)

                self.meter_ctrl.update_reading(elec.meter_id, elec_new)
                self.meter_ctrl.update_reading(water.meter_id, water_new)
        except KeyboardInterrupt:
            print("\nInput interrupted by user, returning to menu.")
            return
    
    # ==================== BILLING MENU ====================
    
    def billing_menu(self):
        """Billing management submenu"""
        while True:
            self.print_header("BILLING & INVOICES")
            print("1. Generate Monthly Bill")
            print("2. Generate Bills for All Customers")
            print("3. View All Bills")
            print("4. View Customer Bills")
            print("5. View Specific Bill")
            print("6. View Unpaid Bills")
            print("7. Print Bill (to text file)")
            print("8. Print All Bills for Period (to files)")
            print("0. Back to Main Menu")
            
            choice = input("\nSelect: ").strip()
            
            if choice == "1":
                self.generate_bill_flow()
            elif choice == "2":
                self.generate_all_bills_flow()
            elif choice == "3":
                print(self.billing_ctrl.display_bills_list())
            elif choice == "4":
                cust_id = self.prompt_customer_id("Customer ID: ")
                if cust_id:
                    bills = self.billing_ctrl.get_customer_bills(cust_id)
                    print(self.billing_ctrl.display_bills_list(bills))
            elif choice == "5":
                bill_id = self.get_input("Bill ID: ").upper()
                bill = self.billing_ctrl.get_bill(bill_id)
                if bill:
                    print(self.billing_ctrl.display_bill(bill))
                else:
                    print("Bill not found.")
            elif choice == "6":
                unpaid = self.billing_ctrl.get_unpaid_bills()
                print(self.billing_ctrl.display_bills_list(unpaid))
            elif choice == "7":
                self.print_bill_flow()
            elif choice == "8":
                self.print_bills_period_flow()
            elif choice == "0":
                break
            else:
                print("Invalid option")
            
            self.pause()
    
    def generate_bill_flow(self):
        """Generate bill for customer"""
        cust_id = self.prompt_customer_id("Customer ID: ")
        if not cust_id:
            return
        
        # Validate customer has meters with readings
        meters = self.meter_ctrl.get_reading_history(cust_id)
        if not meters["electricity"] or not meters["water"]:
            print("Customer must have both meters assigned.")
            return
        
        print(f"\nCurrent readings:")
        print(f"  Electricity: {meters['electricity']['current']:.2f} kWh")
        print(f"  Water: {meters['water']['current']:.2f} m³")
        
        year = int(self.get_input("Year (e.g., 2024): "))
        month = int(self.get_number("Month (1-12): ", min_val=1, max_val=12))
        
        # Confirm
        print(f"\nGenerate bill for {cust_id} - {year}-{month:02d}?")
        if input("Confirm (y/n): ").lower() != 'y':
            print("Cancelled.")
            return
        
        success, message, bill = self.billing_ctrl.generate_monthly_bill(cust_id, year, month)
        
        print(f"\n{message}")
        if success and bill:
            print(self.billing_ctrl.display_bill(bill))

    def generate_all_bills_flow(self):
        """Generate monthly bills for all customers"""
        year = int(self.get_input("Year (e.g., 2024): "))
        month = int(self.get_number("Month (1-12): ", min_val=1, max_val=12))
        print(f"\nGenerating bills for {year}-{month:02d}...")
        generated, skipped = self.billing_ctrl.generate_all_monthly_bills(year, month)
        if generated:
            print(f"\nGenerated {len(generated)} bill(s):")
            for cid, bid in generated:
                print(f"  {cid} -> {bid}")
        if skipped:
            print(f"\nSkipped {len(skipped)} customer(s):")
            for cid, reason in skipped:
                print(f"  {cid}: {reason}")

    def print_bill_flow(self):
        """Export a single bill to a text file (A5-friendly)."""
        bill_id = self.get_input("Bill ID: ").upper()
        bill = self.billing_ctrl.get_bill(bill_id)
        if not bill:
            print("Bill not found.")
            return
        # attempt to get customer name
        customers = load_json("customers.json", {})
        cust = customers.get(bill.customer_id)
        cust_name = cust.get("name") if cust else None
        try:
            path = self.billing_ctrl.export_bill_to_pdf(bill, out_dir="prints", filename=None, customer_name=cust_name)
            print(f"\nBill exported to PDF: {path}")
        except ImportError as e:
            print(str(e))
            print("Falling back to text export...")
            path = self.billing_ctrl.export_bill_to_text(bill, out_dir="prints", filename=None, customer_name=cust_name)
            print(f"\nBill exported to: {path}")

    def print_bills_period_flow(self):
        """Export all bills for a period to files."""
        year = int(self.get_input("Year (e.g., 2024): "))
        month = int(self.get_number("Month (1-12): ", min_val=1, max_val=12))
        try:
            path, skipped = self.billing_ctrl.export_bills_to_pdf_period(year, month, out_dir="prints")
            if path:
                print(f"\nAll bills exported to PDF: {path}")
        except ImportError as e:
            print(str(e))
            print("Falling back to individual text exports...")
            exported, skipped = self.billing_ctrl.export_bills_for_period(year, month, out_dir="prints")
            if exported:
                print(f"\nExported {len(exported)} bill(s):")
                for cid, bid, path in exported:
                    print(f"  {cid} -> {bid} ({path})")
            if skipped:
                print(f"\nSkipped {len(skipped)} customer(s):")
                for cid, reason in skipped:
                    print(f"  {cid}: {reason}")
    
    # ==================== PAYMENT MENU ====================
    
    def payment_menu(self):
        """Payment processing submenu"""
        while True:
            self.print_header("PAYMENT MANAGEMENT")
            print("1. Pay Bill")
            print("2. View Payment History")
            print("3. View Customer Payments")
            print("0. Back to Main Menu")
            
            choice = input("\nSelect: ").strip()
            
            if choice == "1":
                self.pay_bill_flow()
            elif choice == "2":
                print(self.payment_ctrl.display_payments())
            elif choice == "3":
                cust_id = self.prompt_customer_id("Customer ID: ")
                if cust_id:
                    payments = self.payment_ctrl.get_customer_payments(cust_id)
                    print(self.payment_ctrl.display_payments(payments))
            elif choice == "0":
                break
            else:
                print("Invalid option")
            
            self.pause()
    
    def pay_bill_flow(self):
        """Process bill payment"""
        bill_id = self.get_input("Bill ID: ").upper()
        bill = self.billing_ctrl.get_bill(bill_id)
        
        if not bill:
            print("Bill not found.")
            return
        
        if bill.status == "paid":
            print("This bill is already paid in full.")
            return
        
        print(self.billing_ctrl.display_bill(bill))
        
        balance = bill.get_balance()
        print(f"\nOutstanding Balance: {balance:,.0f} Riel")
        
        amount = self.get_number("Payment Amount (Riel): ", min_val=1)
        
        success, message, remaining = self.payment_ctrl.record_payment(bill_id, amount)
        print(f"\n{message}")
        
        if success and remaining > 0:
            print(f"Remaining balance: {remaining:,.0f} Riel")
    
    # ==================== REPORTS MENU ====================
    
    def reports_menu(self):
        """Reports submenu"""
        while True:
            self.print_header("REPORTS")
            print("1. Monthly Report")
            print("2. Yearly Report")
            print("3. Unpaid Bills Report")
            print("4. Customer Statement")
            print("0. Back to Main Menu")
            
            choice = input("\nSelect: ").strip()
            
            if choice == "1":
                year = int(self.get_input("Year: "))
                month = int(self.get_number("Month (1-12): ", min_val=1, max_val=12))
                print(self.reports.monthly_report(year, month))
            elif choice == "2":
                year = int(self.get_input("Year: "))
                print(self.reports.yearly_report(year))
            elif choice == "3":
                print(self.reports.unpaid_bills_report())
            elif choice == "4":
                cust_id = self.prompt_customer_id("Customer ID: ")
                if cust_id:
                    print(self.reports.customer_statement(cust_id))
            elif choice == "0":
                break
            else:
                print("Invalid option")
            
            self.pause()
    
    # ==================== USER MANAGEMENT (ADMIN) ====================
    
    def users_menu(self):
        """User management (admin only)"""
        while True:
            self.print_header("USER MANAGEMENT (ADMIN ONLY)")
            print("1. Create New User")
            print("2. List Users")
            print("0. Back to Main Menu")
            
            choice = input("\nSelect: ").strip()
            
            if choice == "1":
                self.create_user_flow()
            elif choice == "2":
                self.list_users()
            elif choice == "0":
                break
            else:
                print("Invalid option")
            
            self.pause()
    
    def create_user_flow(self):
        """Create new system user"""
        print("\n--- CREATE NEW USER ---")
        username = self.get_input("Username: ")
        
        import getpass
        password = getpass.getpass("Password: ")
        confirm = getpass.getpass("Confirm Password: ")
        
        if password != confirm:
            print("Passwords do not match!")
            return
        
        print("\nSelect Role:")
        print("1. Admin (full access)")
        print("2. Staff (limited access)")
        role_choice = input("Select (1-2): ").strip()
        role = "admin" if role_choice == "1" else "staff"
        
        name = self.get_input("Full Name: ")
        email = self.get_input("Email: ")
        phone_number = self.get_input("Phone Number: ")
        
        success, message = self.auth.create_user(
            username, password, role, name, email, phone_number
        )
        print(f"\n{message}")
    
    def list_users(self):
        """Display system users"""
        from utils.file_handler import load_json
        users = load_json("users.json", {})
        
        print("\n--- SYSTEM USERS ---")
        for username, data in users.items():
            print(
                f"  {username:<15} | "
                f"{data.get('role', 'unknown'):<10} | "
                f"{data.get('name', 'N/A'):<25} | "
                f"{data.get('email', 'N/A'):<30} | "
                f"{data.get('phone_number', 'N/A')}"
            )
    
    # ==================== MAIN LOOP ====================
    
    def logout(self):
        """Logout current user"""
        self.auth.logout()
        print("\nLogged out successfully.")
        return "logout"
    
    def run(self):
        """Main application loop"""
        while True:
            self.clear_screen()
            self.display_project_info()
            
            # Login phase
            if not self.auth.is_authenticated:
                if not self.auth.prompt_login():
                    retry = input("\nTry again? (y/n): ").lower()
                    if retry != 'y':
                        print("Goodbye!")
                        break
                    continue
            
            # Main menu phase
            self.clear_screen()
            print(f"\nLogged in as: {self.auth.current_user} ({self.auth.current_role})")
            
            result = self.main_menu()
            
            if result == "logout":
                continue
            elif result == "customer":
                self.customer_menu()
            elif result == "meter":
                self.meter_menu()
            elif result == "reading":
                self.reading_menu()
            elif result == "billing":
                self.billing_menu()
            elif result == "payment":
                self.payment_menu()
            elif result == "reports":
                self.reports_menu()
            elif result == "users":
                self.users_menu()


def main():
    """Application entry point"""
    try:
        app = BillingSystem()
        app.run()
    except KeyboardInterrupt:
        print("\n\nSystem interrupted. Goodbye!")
    except Exception as e:
        print(f"\nSystem error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
