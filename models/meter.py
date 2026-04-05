"""
Meter Model
Manages electricity (kWh) and water (m³) meter assignments and readings
"""

class Meter:
    """Meter entity tracking utility consumption"""
    
    def __init__(self, meter_id, customer_id, meter_type, previous_reading=0):
        self.meter_id = meter_id          # Unique meter ID
        self.customer_id = customer_id    # Linked customer
        self.meter_type = meter_type      # 'electricity' or 'water'
        self.previous_reading = previous_reading  # Last recorded reading
        self.current_reading = previous_reading   # Current month reading
        self.last_updated = None          # Date of last reading update
    
    def update_reading(self, new_reading):
        """
        Update current reading with validation
        Args:
            new_reading: New meter reading value
        Returns:
            tuple: (success: bool, message: str, usage: float)
        """
        if new_reading < self.previous_reading:
            return (False, 
                   f"Error: Current reading ({new_reading}) cannot be less than "
                   f"previous reading ({self.previous_reading})", 
                   0)
        
        usage = new_reading - self.previous_reading
        
        # Shift current to previous, set new current
        self.previous_reading = self.current_reading
        self.current_reading = new_reading
        
        from datetime import datetime
        self.last_updated = datetime.now().strftime("%Y-%m-%d %H:%M")
        
        return (True, "Reading updated successfully", usage)
    
    def get_usage(self):
        """Calculate current period usage"""
        return self.current_reading - self.previous_reading
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "meter_id": self.meter_id,
            "customer_id": self.customer_id,
            "meter_type": self.meter_type,
            "previous_reading": self.previous_reading,
            "current_reading": self.current_reading,
            "last_updated": self.last_updated
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create Meter from dictionary"""
        meter = cls(
            meter_id=data["meter_id"],
            customer_id=data["customer_id"],
            meter_type=data["meter_type"],
            previous_reading=data.get("previous_reading", 0)
        )
        meter.current_reading = data.get("current_reading", meter.previous_reading)
        meter.last_updated = data.get("last_updated")
        return meter
    
    def __str__(self):
        return (f"[{self.meter_id}] {self.meter_type.title()} - "
                f"Customer: {self.customer_id} - "
                f"Reading: {self.current_reading}")