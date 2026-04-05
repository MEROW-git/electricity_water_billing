"""
Meter Controller
Manages meter assignments and reading updates
"""

from models.meter import Meter
from utils.file_handler import load_json, save_json

class MeterController:
    """Handles meter operations"""
    
    def __init__(self):
        self.data_file = "meters.json"
    
    def get_all_meters(self):
        """Get all meters"""
        data = load_json(self.data_file, {})
        return {mid: Meter.from_dict(mdata) for mid, mdata in data.items()}
    
    def get_customer_meters(self, customer_id):
        """Get both meters for a customer"""
        meters = self.get_all_meters()
        customer_meters = {
            "electricity": None,
            "water": None
        }
        
        for meter in meters.values():
            if meter.customer_id == customer_id:
                if meter.meter_type == "electricity":
                    customer_meters["electricity"] = meter
                elif meter.meter_type == "water":
                    customer_meters["water"] = meter
        
        return customer_meters
    
    def generate_meter_id(self, meter_type):
        """Generate meter ID (E-001 for electric, W-001 for water)"""
        data = load_json(self.data_file, {})
        prefix = "E" if meter_type == "electricity" else "W"
        
        max_num = 0
        for mid in data.keys():
            if mid.startswith(prefix):
                try:
                    num = int(mid.split("-")[1])
                    if num > max_num:
                        max_num = num
                except (IndexError, ValueError):
                    continue
        
        return f"{prefix}-{max_num + 1:03d}"
    
    def assign_meters(self, customer_id, elec_previous=0, water_previous=0):
        """
        Assign both electricity and water meters to customer
        Returns: (success, message, elec_id, water_id)
        """
        # Check if customer already has meters
        existing = self.get_customer_meters(customer_id)
        if existing["electricity"] or existing["water"]:
            return (False, "Customer already has meters assigned", None, None)
        
        data = load_json(self.data_file, {})
        
        # Create electricity meter
        elec_id = self.generate_meter_id("electricity")
        elec_meter = Meter(
            meter_id=elec_id,
            customer_id=customer_id,
            meter_type="electricity",
            previous_reading=elec_previous
        )
        data[elec_id] = elec_meter.to_dict()
        
        # Create water meter
        water_id = self.generate_meter_id("water")
        water_meter = Meter(
            meter_id=water_id,
            customer_id=customer_id,
            meter_type="water",
            previous_reading=water_previous
        )
        data[water_id] = water_meter.to_dict()
        
        if save_json(self.data_file, data):
            return (True, "Meters assigned successfully", elec_id, water_id)
        return (False, "Failed to assign meters", None, None)
    
    def update_reading(self, meter_id, new_reading):
        """
        Update meter reading with validation
        Returns: (success, message, usage)
        """
        data = load_json(self.data_file, {})
        
        if meter_id not in data:
            return (False, f"Meter {meter_id} not found", 0)
        
        meter = Meter.from_dict(data[meter_id])
        success, message, usage = meter.update_reading(new_reading)
        
        if success:
            data[meter_id] = meter.to_dict()
            save_json(self.data_file, data)
        
        return (success, message, usage)
    
    def get_reading_history(self, customer_id):
        """Get current readings for both meters"""
        meters = self.get_customer_meters(customer_id)
        
        result = {}
        for mtype, meter in meters.items():
            if meter:
                result[mtype] = {
                    "meter_id": meter.meter_id,
                    "previous": meter.previous_reading,
                    "current": meter.current_reading,
                    "usage": meter.get_usage(),
                    "last_updated": meter.last_updated
                }
            else:
                result[mtype] = None
        
        return result
    
    def display_meters(self):
        """Display all meters"""
        meters = self.get_all_meters()
        
        if not meters:
            return "No meters found."
        
        lines = []
        lines.append("\n" + "="*90)
        lines.append(f"{'Meter ID':<10} {'Type':<12} {'Customer':<12} "
                    f"{'Previous':<10} {'Current':<10} {'Usage':<10} {'Last Update':<16}")
        lines.append("-"*90)
        
        for meter in meters.values():
            usage = meter.get_usage()
            lines.append(
                f"{meter.meter_id:<10} "
                f"{meter.meter_type.title():<12} "
                f"{meter.customer_id:<12} "
                f"{meter.previous_reading:<10.2f} "
                f"{meter.current_reading:<10.2f} "
                f"{usage:<10.2f} "
                f"{str(meter.last_updated or 'N/A'):<16}"
            )
        
        lines.append("="*90)
        return "\n".join(lines)