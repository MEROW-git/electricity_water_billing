"""
Customer Controller
Handles customer CRUD operations and ID generation
"""

from models.customer import Customer
from utils.file_handler import load_json, save_json

class CustomerController:
    """Manages customer business logic"""
    
    def __init__(self):
        self.data_file = "customers.json"
    
    def get_all_customers(self):
        """Retrieve all customers as objects"""
        data = load_json(self.data_file, {})
        return {cid: Customer.from_dict(cdata) for cid, cdata in data.items()}
    
    def get_customer(self, customer_id):
        """Get single customer by ID"""
        data = load_json(self.data_file, {})
        if customer_id in data:
            return Customer.from_dict(data[customer_id])
        return None
    
    def generate_customer_id(self):
        """Auto-generate next customer ID (CUST-001 format)"""
        data = load_json(self.data_file, {})
        
        if not data:
            return "CUST-001"
        
        # Find highest number
        max_num = 0
        for cid in data.keys():
            try:
                num = int(cid.split("-")[1])
                if num > max_num:
                    max_num = num
            except (IndexError, ValueError):
                continue
        
        return f"CUST-{max_num + 1:03d}"
    
    def add_customer(self, name, phone, address):
        """
        Add new customer
        Returns: (success, message, customer_id)
        """
        # Validation
        if not name or len(name) < 2:
            return (False, "Name must be at least 2 characters", None)
        
        if not phone or len(phone) < 8:
            return (False, "Phone must be at least 8 digits", None)
        
        # Generate ID
        customer_id = self.generate_customer_id()
        
        # Create customer
        customer = Customer(
            customer_id=customer_id,
            name=name,
            phone=phone,
            address=address
        )
        
        # Save to JSON
        data = load_json(self.data_file, {})
        data[customer_id] = customer.to_dict()
        
        if save_json(self.data_file, data):
            return (True, f"Customer added successfully: {customer_id}", customer_id)
        return (False, "Failed to save customer data", None)
    
    def update_customer(self, customer_id, name=None, phone=None, address=None):
        """Update customer details"""
        data = load_json(self.data_file, {})
        
        if customer_id not in data:
            return (False, f"Customer {customer_id} not found")
        
        if name:
            data[customer_id]["name"] = name
        if phone:
            data[customer_id]["phone"] = phone
        if address:
            data[customer_id]["address"] = address
        
        if save_json(self.data_file, data):
            return (True, "Customer updated successfully")
        return (False, "Failed to update customer")
    
    def delete_customer(self, customer_id):
        """Soft delete customer (mark inactive)"""
        data = load_json(self.data_file, {})
        
        if customer_id not in data:
            return (False, f"Customer {customer_id} not found")
        
        data[customer_id]["is_active"] = False
        
        if save_json(self.data_file, data):
            return (True, "Customer deactivated successfully")
        return (False, "Failed to deactivate customer")
    
    def search_customers(self, keyword):
        """Search customers by name or ID"""
        customers = self.get_all_customers()
        results = []
        
        keyword = keyword.lower()
        for customer in customers.values():
            if (keyword in customer.customer_id.lower() or 
                keyword in customer.name.lower() or
                keyword in customer.phone.lower()):
                results.append(customer)
        
        return results

    def resolve_customer_id(self, identifier):
        """Return full customer ID given partial input or numeric part.

        - If identifier already matches a key, returns it.
        - If it matches the numeric suffix of a key (e.g. "1" or "001"),
          returns the first matching full ID.
        - Otherwise returns None.
        """
        if not identifier:
            return None
        identifier = identifier.strip().upper()
        data = load_json(self.data_file, {})
        if identifier in data:
            return identifier
        # if format like CUST-1 or cust-1 without padding
        if identifier.startswith("CUST-"):
            parts = identifier.split("-")
            if len(parts) == 2 and parts[1].isdigit():
                padded = f"CUST-{int(parts[1]):03d}"
                if padded in data:
                    return padded
        # try padding numeric alone
        if identifier.isdigit():
            padded = f"CUST-{int(identifier):03d}"
            if padded in data:
                return padded
        # try match suffix of full id
        for cid in data.keys():
            if cid.endswith(identifier):
                return cid
        return None
    
    def display_customers(self):
        """Format customer list for display"""
        customers = self.get_all_customers()
        
        if not customers:
            return "No customers found."
        
        lines = []
        lines.append("\n" + "="*80)
        lines.append(f"{'ID':<12} {'Name':<25} {'Phone':<15} {'Address':<20}")
        lines.append("-"*80)
        
        for customer in customers.values():
            if customer.is_active:
                lines.append(
                    f"{customer.customer_id:<12} "
                    f"{customer.name:<25} "
                    f"{customer.phone:<15} "
                    f"{customer.address[:20]:<20}"
                )
        
        lines.append("="*80)
        lines.append(f"Total active customers: {len([c for c in customers.values() if c.is_active])}")
        
        return "\n".join(lines)