"""
Reports Module
Generates financial and operational reports
"""

from controllers.customer_controller import CustomerController
from controllers.billing_controller import BillingController
from controllers.payment_controller import PaymentController
from utils.file_handler import load_json

class ReportGenerator:
    """Generates various system reports"""
    
    def __init__(self):
        self.customer_ctrl = CustomerController()
        self.billing_ctrl = BillingController()
        self.payment_ctrl = PaymentController()
    
    def monthly_report(self, year, month):
        """
        Generate monthly billing summary
        Shows total usage, revenue, collection status
        """
        bills = self.billing_ctrl.get_all_bills()
        period = f"{year}-{month:02d}"
        
        period_bills = [b for b in bills.values() if b.period == period]
        
        if not period_bills:
            return f"\nNo data found for {period}"
        
        # Calculate totals
        total_elec_usage = sum(b.electricity_usage for b in period_bills)
        total_water_usage = sum(b.water_usage for b in period_bills)
        total_elec_amount = sum(b.electricity_amount for b in period_bills)
        total_water_amount = sum(b.water_amount for b in period_bills)
        total_amount = sum(b.total_amount for b in period_bills)
        
        total_paid = sum(b.paid_amount for b in period_bills)
        total_unpaid = sum(b.get_balance() for b in period_bills)
        
        paid_count = len([b for b in period_bills if b.status == "paid"])
        unpaid_count = len(period_bills) - paid_count
        
        lines = []
        lines.append("\n" + "="*70)
        lines.append(f"       MONTHLY REPORT - {period}".center(70))
        lines.append("="*70)
        lines.append(f"\nTotal Bills Generated: {len(period_bills)}")
        lines.append(f"Paid Bills: {paid_count} | Unpaid Bills: {unpaid_count}")
        lines.append("\n--- USAGE SUMMARY ---")
        lines.append(f"Electricity Usage:  {total_elec_usage:,.2f} kWh")
        lines.append(f"Water Usage:        {total_water_usage:,.2f} m³")
        lines.append("\n--- REVENUE SUMMARY ---")
        lines.append(f"Electricity Revenue: {total_elec_amount:,.0f} Riel")
        lines.append(f"Water Revenue:       {total_water_amount:,.0f} Riel")
        lines.append(f"Total Revenue:       {total_amount:,.0f} Riel")
        lines.append("\n--- COLLECTION STATUS ---")
        lines.append(f"Collected:   {total_paid:,.0f} Riel ({(total_paid/total_amount*100 if total_amount else 0):.1f}%)")
        lines.append(f"Outstanding: {total_unpaid:,.0f} Riel ({(total_unpaid/total_amount*100 if total_amount else 0):.1f}%)")
        lines.append("="*70)
        
        return "\n".join(lines)
    
    def yearly_report(self, year):
        """Generate yearly summary with monthly breakdown"""
        bills = self.billing_ctrl.get_all_bills()
        year_bills = [b for b in bills.values() if b.year == year]
        
        if not year_bills:
            return f"\nNo data found for year {year}"
        
        # Aggregate by month
        monthly_data = {}
        for b in year_bills:
            if b.month not in monthly_data:
                monthly_data[b.month] = {
                    "bills": 0, "elec_usage": 0, "water_usage": 0,
                    "revenue": 0, "collected": 0
                }
            m = monthly_data[b.month]
            m["bills"] += 1
            m["elec_usage"] += b.electricity_usage
            m["water_usage"] += b.water_usage
            m["revenue"] += b.total_amount
            m["collected"] += b.paid_amount
        
        lines = []
        lines.append("\n" + "="*90)
        lines.append(f"       YEARLY REPORT - {year}".center(90))
        lines.append("="*90)
        lines.append(f"\n{'Month':<8} {'Bills':<8} {'Elec(kWh)':<12} {'Water(m³)':<12} "
                    f"{'Revenue':<15} {'Collected':<15} {'Outstanding':<15}")
        lines.append("-"*90)
        
        total_revenue = 0
        total_collected = 0
        
        for month in sorted(monthly_data.keys()):
            m = monthly_data[month]
            outstanding = m["revenue"] - m["collected"]
            total_revenue += m["revenue"]
            total_collected += m["collected"]
            
            lines.append(
                f"{month:02d}/{year:<4} "
                f"{m['bills']:<8} "
                f"{m['elec_usage']:<12.2f} "
                f"{m['water_usage']:<12.2f} "
                f"{m['revenue']:<15,.0f} "
                f"{m['collected']:<15,.0f} "
                f"{outstanding:<15,.0f}"
            )
        
        lines.append("-"*90)
        lines.append(f"{'TOTAL':<8} {len(year_bills):<8} {'':<12} {'':<12} "
                    f"{total_revenue:<15,.0f} {total_collected:<15,.0f} "
                    f"{total_revenue-total_collected:<15,.0f}")
        lines.append("="*90)
        
        return "\n".join(lines)
    
    def unpaid_bills_report(self):
        """Report all outstanding payments"""
        unpaid = self.billing_ctrl.get_unpaid_bills()
        
        if not unpaid:
            return "\n✓ No unpaid bills! All accounts are settled."
        
        total_outstanding = sum(b.get_balance() for b in unpaid)
        
        lines = []
        lines.append("\n" + "="*100)
        lines.append("       UNPAID BILLS REPORT".center(100))
        lines.append("="*100)
        lines.append(f"Total Outstanding Bills: {len(unpaid)}")
        lines.append(f"Total Outstanding Amount: {total_outstanding:,.0f} Riel")
        lines.append("-"*100)
        
        # Group by customer
        by_customer = {}
        for bill in unpaid:
            cid = bill.customer_id
            if cid not in by_customer:
                by_customer[cid] = []
            by_customer[cid].append(bill)
        
        for cid, bills in sorted(by_customer.items()):
            customer = self.customer_ctrl.get_customer(cid)
            name = customer.name if customer else "Unknown"
            lines.append(f"\nCustomer: {cid} - {name}")
            lines.append("-" * 80)
            
            for bill in bills:
                balance = bill.get_balance()
                lines.append(
                    f"  {bill.period:<10} {bill.bill_id:<25} "
                    f"Total: {bill.total_amount:>10,.0f} | "
                    f"Balance: {balance:>10,.0f}"
                )
        
        lines.append("\n" + "="*100)
        return "\n".join(lines)
    
    def customer_statement(self, customer_id):
        """Generate full statement for specific customer"""
        customer = self.customer_ctrl.get_customer(customer_id)
        if not customer:
            return f"\nCustomer {customer_id} not found"
        
        bills = self.billing_ctrl.get_customer_bills(customer_id)
        payments = self.payment_ctrl.get_customer_payments(customer_id)
        
        lines = []
        lines.append("\n" + "="*80)
        lines.append("       CUSTOMER STATEMENT".center(80))
        lines.append("="*80)
        lines.append(f"Customer ID: {customer.customer_id}")
        lines.append(f"Name:        {customer.name}")
        lines.append(f"Phone:       {customer.phone}")
        lines.append(f"Address:     {customer.address}")
        lines.append("-"*80)
        
        # Billing history
        lines.append("\n--- BILLING HISTORY ---")
        if bills:
            total_billed = sum(b.total_amount for b in bills)
            total_paid = sum(b.paid_amount for b in bills)
            
            for bill in sorted(bills, key=lambda x: (x.year, x.month)):
                status = "✓" if bill.status == "paid" else "✗"
                lines.append(
                    f"{status} {bill.period} | "
                    f"Elec: {bill.electricity_usage:>6.2f}kWh | "
                    f"Water: {bill.water_usage:>6.2f}m³ | "
                    f"Total: {bill.total_amount:>10,.0f} | "
                    f"Paid: {bill.paid_amount:>10,.0f}"
                )
            
            lines.append("-"*80)
            lines.append(f"{'Total Billed:':<50} {total_billed:>15,.0f} Riel")
            lines.append(f"{'Total Paid:':<50} {total_paid:>15,.0f} Riel")
            lines.append(f"{'Balance:':<50} {total_billed-total_paid:>15,.0f} Riel")
        else:
            lines.append("No billing history")
        
        lines.append("="*80)
        return "\n".join(lines)