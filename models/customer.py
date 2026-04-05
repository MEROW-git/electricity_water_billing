"""
Customer Model
Represents a utility customer with personal details
"""

class Customer:
    """Customer entity with identification and contact info"""
    
    def __init__(self, customer_id, name, phone, address, created_date=None):
        self.customer_id = customer_id  # Unique ID (CUST-001 format)
        self.name = name
        self.phone = phone
        self.address = address
        self.created_date = created_date or self._get_current_date()
        self.is_active = True
    
    def _get_current_date(self):
        """Return current date string"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d")
    
    def to_dict(self):
        """Convert object to dictionary for JSON serialization"""
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "phone": self.phone,
            "address": self.address,
            "created_date": self.created_date,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Customer object from dictionary"""
        customer = cls(
            customer_id=data["customer_id"],
            name=data["name"],
            phone=data["phone"],
            address=data["address"],
            created_date=data.get("created_date")
        )
        customer.is_active = data.get("is_active", True)
        return customer
    
    def __str__(self):
        return f"[{self.customer_id}] {self.name} - {self.phone}"