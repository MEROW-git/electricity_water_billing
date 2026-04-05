"""
Bill Model
Represents monthly utility bills with calculation logic
"""

class Bill:
    """Bill entity for electricity and water charges"""
    
    # Configurable rates (Riel per unit)
    ELECTRICITY_RATE = 750  # Riel per kWh
    WATER_RATE = 500        # Riel per m³
    
    def __init__(self, bill_id, customer_id, year, month, 
                 electricity_usage, water_usage, 
                 electricity_amount=None, water_amount=None,
                 total_amount=None, status="unpaid", created_date=None):
        self.bill_id = bill_id
        self.customer_id = customer_id
        self.year = year
        self.month = month
        self.period = f"{year}-{month:02d}"
        
        # Usage data
        self.electricity_usage = electricity_usage  # kWh
        self.water_usage = water_usage              # m³
        
        # Calculated amounts (auto-calculate if not provided)
        self.electricity_amount = electricity_amount or self._calc_electricity()
        self.water_amount = water_amount or self._calc_water()
        self.total_amount = total_amount or (self.electricity_amount + self.water_amount)
        
        self.status = status  # 'unpaid', 'paid', 'partial'
        self.created_date = created_date or self._get_current_date()
        self.paid_date = None
        self.paid_amount = 0
    
    def _calc_electricity(self):
        """Calculate electricity charge"""
        return self.electricity_usage * self.ELECTRICITY_RATE
    
    def _calc_water(self):
        """Calculate water charge"""
        return self.water_usage * self.WATER_RATE
    
    def _get_current_date(self):
        """Get current date"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    def record_payment(self, amount):
        """
        Record payment against bill
        Returns: (success, message, remaining_balance)
        """
        if amount <= 0:
            return (False, "Payment amount must be positive", self.total_amount - self.paid_amount)
        
        self.paid_amount += amount
        
        from datetime import datetime
        self.paid_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        remaining = self.total_amount - self.paid_amount
        
        if remaining <= 0:
            self.status = "paid"
            return (True, f"Bill fully paid. Change: {abs(remaining):.0f} Riel", 0)
        else:
            self.status = "partial"
            return (True, f"Partial payment recorded. Remaining: {remaining:.0f} Riel", remaining)
    
    def get_balance(self):
        """Get remaining balance"""
        return self.total_amount - self.paid_amount
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "bill_id": self.bill_id,
            "customer_id": self.customer_id,
            "year": self.year,
            "month": self.month,
            "period": self.period,
            "electricity_usage": self.electricity_usage,
            "water_usage": self.water_usage,
            "electricity_amount": self.electricity_amount,
            "water_amount": self.water_amount,
            "total_amount": self.total_amount,
            "status": self.status,
            "created_date": self.created_date,
            "paid_date": self.paid_date,
            "paid_amount": self.paid_amount
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Bill from dictionary"""
        bill = cls(
            bill_id=data["bill_id"],
            customer_id=data["customer_id"],
            year=data["year"],
            month=data["month"],
            electricity_usage=data["electricity_usage"],
            water_usage=data["water_usage"],
            electricity_amount=data.get("electricity_amount"),
            water_amount=data.get("water_amount"),
            total_amount=data.get("total_amount"),
            status=data.get("status", "unpaid"),
            created_date=data.get("created_date")
        )
        bill.paid_date = data.get("paid_date")
        bill.paid_amount = data.get("paid_amount", 0)
        return bill
    
    def __str__(self):
        return (f"[{self.bill_id}] {self.period} - "
                f"Amount: {self.total_amount:.0f} Riel - "
                f"Status: {self.status.upper()}")