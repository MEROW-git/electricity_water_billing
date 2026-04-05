"""
File Handler Utility
Handles all JSON file operations with auto-creation
"""

import json
import os
from pathlib import Path

# Base data directory
DATA_DIR = Path("data")

def ensure_data_dir():
    """Create data directory if it doesn't exist"""
    DATA_DIR.mkdir(exist_ok=True)

def get_file_path(filename):
    """Return full path to data file"""
    ensure_data_dir()
    return DATA_DIR / filename

def load_json(filename, default=None):
    """
    Load JSON file or return default if missing/corrupt
    Args:
        filename: Name of JSON file
        default: Default data structure if file missing
    Returns:
        Parsed JSON data or default
    """
    filepath = get_file_path(filename)
    
    if not filepath.exists():
        return default if default is not None else {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return default if default is not None else {}

def save_json(filename, data):
    """
    Save data to JSON file with pretty formatting
    Args:
        filename: Target JSON file
        data: Data to serialize
    Returns:
        bool: True if successful
    """
    filepath = get_file_path(filename)
    ensure_data_dir()
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"Error saving {filename}: {e}")
        return False

def initialize_data_files():
    """Create default data files with initial admin user"""
    ensure_data_dir()
    
    # Default admin user (username: admin, password: admin123)
    users = load_json("users.json", {})
    if not users:
        users = {
            "admin": {
                "password": "admin123",
                "role": "admin",
                "name": "System Administrator",
                "email": "",
                "phone_number": "",
                "mfa_enabled": False
            }
        }
        save_json("users.json", users)
        print("Created default admin user (admin/admin123)")
    else:
        updated = False
        for user_data in users.values():
            if "email" not in user_data:
                user_data["email"] = ""
                updated = True
            if "phone_number" not in user_data:
                user_data["phone_number"] = ""
                updated = True
            if "mfa_enabled" not in user_data:
                user_data["mfa_enabled"] = False
                updated = True
        if updated:
            save_json("users.json", users)
    
    # Initialize empty data files if missing
    files_defaults = {
        "customers.json": {},
        "meters.json": {},
        "bills.json": {},
        "payments.json": {}
    }
    
    for filename, default in files_defaults.items():
        data = load_json(filename)
        if not data:
            save_json(filename, default)
