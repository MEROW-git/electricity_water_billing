"""
Billing Controller
Generates bills and manages billing cycles
"""

from models.bill import Bill
from controllers.meter_controller import MeterController
from utils.file_handler import load_json, save_json
from datetime import datetime

class BillingController:
    """Handles bill generation and management"""
    
    def __init__(self):
        self.data_file = "bills.json"
        self.meter_controller = MeterController()
    
    def get_all_bills(self):
        """Get all bills"""
        data = load_json(self.data_file, {})
        return {bid: Bill.from_dict(bdata) for bid, bdata in data.items()}

    def generate_all_monthly_bills(self, year, month):
        """Generate bills for all customers for given period.

        Returns a tuple (generated, skipped) where generated is a list of
        (customer_id, bill_id) and skipped is a list of (customer_id, reason).
        """
        customers = load_json("customers.json", {})
        generated = []
        skipped = []
        for cid in customers.keys():
            # attempt to generate bill
            success, msg, bill = self.generate_monthly_bill(cid, year, month)
            if success:
                generated.append((cid, bill.bill_id))
            else:
                skipped.append((cid, msg))
        return generated, skipped
    
    def get_customer_bills(self, customer_id):
        """Get all bills for a customer"""
        bills = self.get_all_bills()
        return [bill for bill in bills.values() if bill.customer_id == customer_id]
    
    def generate_bill_id(self, customer_id, year, month):
        """Generate unique bill ID: B-CUST-001-2024-03"""
        return f"B-{customer_id}-{year}-{month:02d}"
    
    def generate_monthly_bill(self, customer_id, year, month):
        """
        Generate bill for specific month
        Returns: (success, message, bill_object)
        """
        # Check if bill already exists
        bill_id = self.generate_bill_id(customer_id, year, month)
        data = load_json(self.data_file, {})
        
        if bill_id in data:
            return (False, f"Bill for {year}-{month:02d} already exists", None)
        
        # Get meter readings
        meters = self.meter_controller.get_customer_meters(customer_id)
        
        if not meters["electricity"] or not meters["water"]:
            return (False, "Customer does not have both meters assigned", None)
        
        elec_meter = meters["electricity"]
        water_meter = meters["water"]
        
        # Calculate usage
        elec_usage = elec_meter.get_usage()
        water_usage = water_meter.get_usage()
        
        if elec_usage < 0 or water_usage < 0:
            return (False, "Invalid meter readings detected", None)
        
        # Create bill
        bill = Bill(
            bill_id=bill_id,
            customer_id=customer_id,
            year=year,
            month=month,
            electricity_usage=elec_usage,
            water_usage=water_usage
        )
        
        # Save
        data[bill_id] = bill.to_dict()
        
        if save_json(self.data_file, data):
            # Reset meter readings for next month (previous becomes current)
            self._reset_meters_for_next_month(elec_meter, water_meter)
            return (True, f"Bill generated: {bill.total_amount:.0f} Riel", bill)
        
        return (False, "Failed to save bill", None)
    
    def _reset_meters_for_next_month(self, elec_meter, water_meter):
        """Prepare meters for next billing cycle"""
        # Update previous to current for next month calculation
        elec_meter.previous_reading = elec_meter.current_reading
        water_meter.previous_reading = water_meter.current_reading
        
        data = load_json("meters.json", {})
        data[elec_meter.meter_id] = elec_meter.to_dict()
        data[water_meter.meter_id] = water_meter.to_dict()
        save_json("meters.json", data)
    
    def get_bill(self, bill_id):
        """Get specific bill"""
        data = load_json(self.data_file, {})
        if bill_id in data:
            return Bill.from_dict(data[bill_id])
        return None
    
    def get_unpaid_bills(self, customer_id=None):
        """Get all unpaid bills, optionally filtered by customer"""
        bills = self.get_all_bills()
        unpaid = []
        
        for bill in bills.values():
            if bill.status in ["unpaid", "partial"]:
                if customer_id is None or bill.customer_id == customer_id:
                    unpaid.append(bill)
        
        return unpaid

    def get_latest_payable_bills(self):
        """Return only the newest unpaid or partial bill for each customer."""
        latest_by_customer = {}

        for bill in self.get_unpaid_bills():
            current = latest_by_customer.get(bill.customer_id)
            if current is None or (bill.year, bill.month, bill.bill_id) > (current.year, current.month, current.bill_id):
                latest_by_customer[bill.customer_id] = bill

        return list(latest_by_customer.values())

    def get_latest_payable_bill_for_customer(self, customer_id):
        """Return the newest unpaid or partial bill for one customer."""
        bills = [bill for bill in self.get_unpaid_bills(customer_id) if bill.customer_id == customer_id]
        if not bills:
            return None
        return max(bills, key=lambda bill: (bill.year, bill.month, bill.bill_id))
    
    def display_bill(self, bill):
        """Format single bill for display"""
        lines = []
        lines.append("\n" + "="*60)
        lines.append("           INVOICE / វិក្កយបត្រ".center(60))
        lines.append("="*60)
        lines.append(f"Bill ID:    {bill.bill_id}")
        lines.append(f"Period:     {bill.period}")
        lines.append(f"Customer:   {bill.customer_id}")
        lines.append("-"*60)
        lines.append("ELECTRICITY USAGE:")
        lines.append(f"  Usage:        {bill.electricity_usage:.2f} kWh")
        lines.append(f"  Rate:         {Bill.ELECTRICITY_RATE} Riel/kWh")
        lines.append(f"  Amount:       {bill.electricity_amount:,.0f} Riel")
        lines.append("-"*60)
        lines.append("WATER USAGE:")
        lines.append(f"  Usage:        {bill.water_usage:.2f} m³")
        lines.append(f"  Rate:         {Bill.WATER_RATE} Riel/m³")
        lines.append(f"  Amount:       {bill.water_amount:,.0f} Riel")
        lines.append("-"*60)
        lines.append(f"TOTAL AMOUNT:   {bill.total_amount:,.0f} Riel")
        lines.append(f"STATUS:         {bill.status.upper()}")
        
        if bill.status != "unpaid":
            lines.append(f"Paid Amount:    {bill.paid_amount:,.0f} Riel")
            lines.append(f"Balance:        {bill.get_balance():,.0f} Riel")
            lines.append(f"Paid Date:      {bill.paid_date or 'N/A'}")
        
        lines.append("="*60)
        return "\n".join(lines)
    
    def display_bills_list(self, bills_list=None):
        """Display list of bills"""
        if bills_list is None:
            bills_list = list(self.get_all_bills().values())
        
        if not bills_list:
            return "No bills found."
        
        lines = []
        lines.append("\n" + "="*100)
        lines.append(f"{'Bill ID':<20} {'Period':<10} {'Customer':<12} "
                    f"{'Electricity':<12} {'Water':<12} {'Total':<12} {'Status':<10}")
        lines.append("-"*100)
        
        for bill in bills_list:
            lines.append(
                f"{bill.bill_id:<20} "
                f"{bill.period:<10} "
                f"{bill.customer_id:<12} "
                f"{bill.electricity_amount:>10,.0f} "
                f"{bill.water_amount:>10,.0f} "
                f"{bill.total_amount:>10,.0f} "
                f"{bill.status.upper():<10}"
            )
        
        lines.append("="*100)
        return "\n".join(lines)

    def export_bill_to_text(self, bill, out_dir="prints", filename=None, customer_name=None):
        """Export single bill to a text file formatted for A5 paper.

        Creates `out_dir` if missing and writes a plain-text invoice file.
        Returns the path to the written file.
        """
        from pathlib import Path
        Path(out_dir).mkdir(exist_ok=True)

        if filename is None:
            # sanitize bill id
            filename = f"{bill.bill_id}.txt"

        path = Path(out_dir) / filename

        # A5 width ~ 40-48 characters; use 44 as reasonable width
        width = 44
        def center(s):
            return s.center(width)

        lines = []
        lines.append(center("INVOICE / វិក្កយបត្រ"))
        lines.append("="*width)
        lines.append(f"Bill ID: {bill.bill_id}")
        lines.append(f"Period:  {bill.period}")
        lines.append(f"Customer:{' ' + (customer_name or bill.customer_id)}")
        lines.append("-"*width)
        lines.append("ELECTRICITY:")
        lines.append(f"  Usage: {bill.electricity_usage:.2f} kWh")
        lines.append(f"  Rate:  {Bill.ELECTRICITY_RATE} Riel/kWh")
        lines.append(f"  Amt:   {bill.electricity_amount:,.0f} Riel")
        lines.append("-"*width)
        lines.append("WATER:")
        lines.append(f"  Usage: {bill.water_usage:.2f} m³")
        lines.append(f"  Rate:  {Bill.WATER_RATE} Riel/m³")
        lines.append(f"  Amt:   {bill.water_amount:,.0f} Riel")
        lines.append("-"*width)
        lines.append(f"TOTAL: {bill.total_amount:,.0f} Riel")
        lines.append(f"STATUS: {bill.status.upper()}")
        if bill.status != "unpaid":
            lines.append(f"Paid: {bill.paid_amount:,.0f} Riel")
            lines.append(f"Balance: {bill.get_balance():,.0f} Riel")
            lines.append(f"Paid Date: {bill.paid_date or 'N/A'}")
        lines.append("="*width)

        with open(path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        return str(path)

    def export_bills_for_period(self, year, month, out_dir="prints"):
        """Export all bills for a given period to individual text files.

        Returns (exported, skipped) lists similar to batch generation.
        """
        from pathlib import Path
        Path(out_dir).mkdir(exist_ok=True)

        exported = []
        skipped = []
        all_bills = self.get_all_bills()
        period = f"{year}-{month:02d}"
        for bill in all_bills.values():
            if bill.period != period:
                continue
            # attempt to get customer name
            customers = load_json("customers.json", {})
            cust = customers.get(bill.customer_id)
            cust_name = cust.get("name") if cust else None
            fname = f"{bill.bill_id}.txt"
            try:
                path = self.export_bill_to_text(bill, out_dir=out_dir, filename=fname, customer_name=cust_name)
                exported.append((bill.customer_id, bill.bill_id, path))
            except Exception as e:
                skipped.append((bill.customer_id, str(e)))

        return exported, skipped

    def export_bill_to_pdf(self, bill, out_dir="prints", filename=None, customer_name=None):
        """Export single bill to a PDF file sized for A5.

        Requires `reportlab`. Raises ImportError if missing.
        Returns written file path.
        """
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A5
            from reportlab.lib.units import mm
        except ImportError:
            raise ImportError("reportlab is required to export PDFs. Install with: pip install reportlab")

        from pathlib import Path
        Path(out_dir).mkdir(exist_ok=True)

        if filename is None:
            filename = f"{bill.bill_id}.pdf"

        path = Path(out_dir) / filename

        c = canvas.Canvas(str(path), pagesize=A5)
        w, h = A5

        margin = 12 * mm
        x = margin
        y = h - margin

        # Header
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(w/2, y, "INVOICE / វិក្កយបត្រ")
        y -= 12 * mm

        c.setFont("Helvetica", 9)
        c.drawString(x, y, f"Bill ID: {bill.bill_id}")
        c.drawRightString(w - margin, y, f"Period: {bill.period}")
        y -= 6 * mm
        c.drawString(x, y, f"Customer: {customer_name or bill.customer_id}")
        y -= 8 * mm

        # Electricity block
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, "ELECTRICITY")
        y -= 6 * mm
        c.setFont("Helvetica", 9)
        c.drawString(x, y, f"Usage: {bill.electricity_usage:.2f} kWh")
        c.drawRightString(w - margin, y, f"Amount: {bill.electricity_amount:,.0f} Riel")
        y -= 6 * mm

        # Water block
        c.setFont("Helvetica-Bold", 10)
        c.drawString(x, y, "WATER")
        y -= 6 * mm
        c.setFont("Helvetica", 9)
        c.drawString(x, y, f"Usage: {bill.water_usage:.2f} m³")
        c.drawRightString(w - margin, y, f"Amount: {bill.water_amount:,.0f} Riel")
        y -= 10 * mm

        # Totals
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x, y, f"TOTAL: {bill.total_amount:,.0f} Riel")
        y -= 8 * mm
        c.setFont("Helvetica", 9)
        c.drawString(x, y, f"STATUS: {bill.status.upper()}")
        if bill.status != "unpaid":
            y -= 6 * mm
            c.drawString(x, y, f"Paid: {bill.paid_amount:,.0f} Riel")
            c.drawRightString(w - margin, y, f"Balance: {bill.get_balance():,.0f} Riel")

        # Footer
        c.setFont("Helvetica-Oblique", 8)
        c.drawCentredString(w/2, margin/2, "Thank you")

        c.showPage()
        c.save()

        return str(path)

    def export_bills_to_pdf_period(self, year, month, out_dir="prints", filename=None):
        """Export all bills for a period into a single multi-page PDF (A5 per page).

        Returns path to created PDF and list of skipped items.
        """
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A5
            from reportlab.lib.units import mm
        except ImportError:
            raise ImportError("reportlab is required to export PDFs. Install with: pip install reportlab")

        from pathlib import Path
        Path(out_dir).mkdir(exist_ok=True)

        if filename is None:
            filename = f"bills_{year}_{month:02d}.pdf"

        path = Path(out_dir) / filename

        c = canvas.Canvas(str(path), pagesize=A5)
        w, h = A5
        margin = 12 * mm
        customers = load_json("customers.json", {})

        all_bills = self.get_all_bills()
        period = f"{year}-{month:02d}"
        skipped = []
        exported_count = 0

        for bill in all_bills.values():
            if bill.period != period:
                continue
            cust = customers.get(bill.customer_id)
            cust_name = cust.get("name") if cust else None

            # draw one page per bill
            y = h - margin
            x = margin
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(w/2, y, "INVOICE / វិក្កយបត្រ")
            y -= 12 * mm
            c.setFont("Helvetica", 9)
            c.drawString(x, y, f"Bill ID: {bill.bill_id}")
            c.drawRightString(w - margin, y, f"Period: {bill.period}")
            y -= 6 * mm
            c.drawString(x, y, f"Customer: {cust_name or bill.customer_id}")
            y -= 8 * mm

            c.setFont("Helvetica-Bold", 10)
            c.drawString(x, y, "ELECTRICITY")
            y -= 6 * mm
            c.setFont("Helvetica", 9)
            c.drawString(x, y, f"Usage: {bill.electricity_usage:.2f} kWh")
            c.drawRightString(w - margin, y, f"Amount: {bill.electricity_amount:,.0f} Riel")
            y -= 6 * mm

            c.setFont("Helvetica-Bold", 10)
            c.drawString(x, y, "WATER")
            y -= 6 * mm
            c.setFont("Helvetica", 9)
            c.drawString(x, y, f"Usage: {bill.water_usage:.2f} m³")
            c.drawRightString(w - margin, y, f"Amount: {bill.water_amount:,.0f} Riel")
            y -= 10 * mm

            c.setFont("Helvetica-Bold", 11)
            c.drawString(x, y, f"TOTAL: {bill.total_amount:,.0f} Riel")
            y -= 8 * mm
            c.setFont("Helvetica", 9)
            c.drawString(x, y, f"STATUS: {bill.status.upper()}")
            if bill.status != "unpaid":
                y -= 6 * mm
                c.drawString(x, y, f"Paid: {bill.paid_amount:,.0f} Riel")
                c.drawRightString(w - margin, y, f"Balance: {bill.get_balance():,.0f} Riel")

            c.setFont("Helvetica-Oblique", 8)
            c.drawCentredString(w/2, margin/2, "Thank you")

            c.showPage()
            exported_count += 1

        if exported_count == 0:
            return None, [("no_bills", "No bills found for period")]

        c.save()
        return str(path), skipped
