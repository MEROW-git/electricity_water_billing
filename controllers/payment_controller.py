"""
Payment Controller
Handles bill payments and transaction recording
"""

from models.bill import Bill
from controllers.billing_controller import BillingController
from utils.file_handler import load_json, save_json
from datetime import datetime

class PaymentController:
    """Manages payment transactions"""
    
    def __init__(self):
        self.billing_controller = BillingController()
        self.payments_file = "payments.json"
    
    def get_all_payments(self):
        """Get all payment records"""
        return load_json(self.payments_file, {})
    
    def record_payment(self, bill_id, amount):
        """
        Process payment for a bill
        Returns: (success, message, change/balance)
        """
        # Validate amount
        try:
            amount = float(amount)
            if amount <= 0:
                return (False, "Payment amount must be positive", 0)
        except ValueError:
            return (False, "Invalid amount", 0)
        
        # Get bill
        bill = self.billing_controller.get_bill(bill_id)
        if not bill:
            return (False, f"Bill {bill_id} not found", 0)
        
        if bill.status == "paid":
            return (False, "Bill is already fully paid", 0)
        
        # Process payment
        success, message, remaining = bill.record_payment(amount)
        
        if success:
            # Update bill in storage
            bills_data = load_json("bills.json", {})
            bills_data[bill_id] = bill.to_dict()
            save_json("bills.json", bills_data)
            
            # Record payment transaction
            self._save_payment_record(bill_id, amount, bill.customer_id)
        
        return (success, message, remaining)
    
    def _save_payment_record(self, bill_id, amount, customer_id):
        """Save payment to transaction log"""
        payments = load_json(self.payments_file, {})
        
        payment_id = f"P-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        payments[payment_id] = {
            "payment_id": payment_id,
            "bill_id": bill_id,
            "customer_id": customer_id,
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        save_json(self.payments_file, payments)
        return payment_id
    
    def get_customer_payments(self, customer_id):
        """Get payment history for customer"""
        payments = self.get_all_payments()
        return [p for p in payments.values() if p["customer_id"] == customer_id]
    
    def display_payments(self, payments_list=None):
        """Display payment records"""
        if payments_list is None:
            payments_list = list(self.get_all_payments().values())
        
        if not payments_list:
            return "No payments recorded."
        
        lines = []
        lines.append("\n" + "="*80)
        lines.append(f"{'Payment ID':<20} {'Date':<20} {'Bill ID':<20} {'Amount':>15}")
        lines.append("-"*80)
        
        total = 0
        for payment in payments_list:
            lines.append(
                f"{payment['payment_id']:<20} "
                f"{payment['date']:<20} "
                f"{payment['bill_id']:<20} "
                f"{payment['amount']:>15,.0f}"
            )
            total += payment['amount']
        
        lines.append("-"*80)
        lines.append(f"{'TOTAL':<60} {total:>15,.0f}")
        lines.append("="*80)
        
        return "\n".join(lines)