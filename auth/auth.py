"""
Authentication Module
Handles user login, logout, and role-based access control
"""

import hashlib
import getpass
import random
import time
from utils.file_handler import load_json, save_json

class AuthManager:
    """Manages user authentication and session state"""
    
    MFA_TTL_SECONDS = 300  # 5 minutes

    def __init__(self):
        self.current_user = None
        self.current_role = None
        self.is_authenticated = False
        self.pending_mfa = {}  # maps username -> (code, expires_at)
    
    def hash_password(self, password):
        """SHA256 hashing for passwords"""
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_credentials(self, username, password):
        """Validate username/password pair (returns bool)"""
        users = load_json("users.json", {})
        if username not in users:
            return False
        stored_hash = users[username].get("password", "")

        if len(stored_hash) == 64:  # already SHA256
            return self.hash_password(password) == stored_hash
        return password == stored_hash

    def enable_mfa(self, username):
        """Enable MFA for a user by marking records"""
        users = load_json("users.json", {})
        if username not in users:
            return (False, "User not found")
        users[username]["mfa_enabled"] = True
        save_json("users.json", users)
        return (True, "MFA enabled")

    def disable_mfa(self, username):
        """Disable MFA for a user"""
        users = load_json("users.json", {})
        if username not in users:
            return (False, "User not found")
        users[username]["mfa_enabled"] = False
        save_json("users.json", users)
        return (True, "MFA disabled")

    def _generate_mfa_code(self, username):
        """Generate and store one-time MFA token"""
        code = f"{random.randint(0, 999999):06d}"
        expires_at = time.time() + self.MFA_TTL_SECONDS
        self.pending_mfa[username] = (code, expires_at)
        return code

    def send_mfa_code(self, username):
        """Send MFA code to user (simulated via console)"""
        code = self._generate_mfa_code(username)
        # In real app, send by SMS/email. Here we print for demo/test.
        print(f"[MFA] code for {username}: {code} (valid 5 minutes)")
        return code

    def verify_mfa_code(self, username, code):
        """Check MFA code validity"""
        payload = self.pending_mfa.get(username)
        if not payload:
            return False
        stored_code, expires_at = payload
        if time.time() > expires_at:
            del self.pending_mfa[username]
            return False
        if code != stored_code:
            return False

        del self.pending_mfa[username]
        return True

    def login(self, username, password, mfa_code=None):
        """
        Authenticate user against stored credentials, with optional MFA.
        Returns: (success: bool, message: str)
        """
        users = load_json("users.json", {})

        if username not in users:
            return (False, "Invalid username or password")

        user_data = users[username]

        if not self.verify_credentials(username, password):
            return (False, "Invalid username or password")

        # MFA request
        if user_data.get("mfa_enabled"):
            if mfa_code is None:
                self.send_mfa_code(username)
                return (False, "MFA code sent. Please provide code to complete login.")

            if not self.verify_mfa_code(username, str(mfa_code).zfill(6)):
                return (False, "Invalid or expired MFA code")

        # Successful login
        self.current_user = username
        self.current_role = user_data.get("role", "staff")
        self.is_authenticated = True

        return (True, f"Welcome, {user_data.get('name', username)}!")
    
    def logout(self):
        """Clear current session"""
        self.current_user = None
        self.current_role = None
        self.is_authenticated = False
        return True
    
    def create_user(self, username, password, role, name, email="", phone_number=""):
        """
        Create new user (Admin only)
        Returns: (success, message)
        """
        if not self.is_admin():
            return (False, "Permission denied: Admin only")
        
        users = load_json("users.json", {})
        
        if username in users:
            return (False, f"User '{username}' already exists")
        
        users[username] = {
            "password": self.hash_password(password),
            "role": role,
            "name": name,
            "email": email,
            "phone_number": phone_number,
            "mfa_enabled": False
        }
        
        if save_json("users.json", users):
            return (True, f"User '{username}' created successfully")
        return (False, "Failed to save user data")

    def update_user(self, current_username, new_username, role, name, email="", phone_number="", mfa_enabled=False):
        """
        Update an existing user (Admin only)
        Returns: (success, message)
        """
        if not self.is_admin():
            return (False, "Permission denied: Admin only")

        users = load_json("users.json", {})

        if current_username not in users:
            return (False, f"User '{current_username}' not found")

        new_username = (new_username or "").strip()
        name = (name or "").strip()
        role = (role or "").strip()

        if not new_username:
            return (False, "Username is required")
        if not name:
            return (False, "Full name is required")
        if role not in ("admin", "staff"):
            return (False, "Role must be 'admin' or 'staff'")
        if new_username != current_username and new_username in users:
            return (False, f"User '{new_username}' already exists")

        user_data = users[current_username]
        updated_data = {
            "password": user_data.get("password", ""),
            "role": role,
            "name": name,
            "email": email,
            "phone_number": phone_number,
            "mfa_enabled": bool(mfa_enabled),
        }

        if new_username != current_username:
            del users[current_username]
        users[new_username] = updated_data

        if save_json("users.json", users):
            if self.current_user == current_username:
                self.current_user = new_username
                self.current_role = role
            return (True, f"User '{current_username}' updated successfully")
        return (False, "Failed to save user data")
    
    def is_admin(self):
        """Check if current user is admin"""
        return self.is_authenticated and self.current_role == "admin"
    
    def is_staff(self):
        """Check if current user is staff"""
        return self.is_authenticated and self.current_role == "staff"
    
    def get_menu_access(self):
        """
        Return allowed menu items based on role
        Returns: dict of menu permissions
        """
        if not self.is_authenticated:
            return {}
        
        # Admin: Full access
        if self.is_admin():
            return {
                "customer_manage": True,
                "meter_manage": True,
                "reading_manage": True,
                "billing_manage": True,
                "payment_manage": True,
                "reports": True,
                "user_manage": True,
                "settings": True
            }
        
        # Staff: Limited access (no user management, no settings)
        return {
            "customer_manage": True,
            "meter_manage": True,
            "reading_manage": True,
            "billing_manage": True,
            "payment_manage": True,
            "reports": True,
            "user_manage": False,
            "settings": False
        }
    
    def prompt_login(self):
        """Interactive login prompt"""
        print("\n" + "="*50)
        print("       ELECTRICITY & WATER BILLING SYSTEM")
        print("              (គណនាបង់ថ្លៃភ្លើង និងទឹក)")
        print("="*50)
        print("\nPlease login to continue")
        
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ")

        success, message = self.login(username, password)

        if not success and "MFA code sent" in message:
            print(f"\n⚠️ {message}")
            mfa_code = input("Enter MFA code: ").strip()
            success, message = self.login(username, password, mfa_code)

        if success:
            print(f"\n✓ {message}")
            print(f"Role: {self.current_role.upper()}")
        else:
            print(f"\n✗ {message}")

        return success
