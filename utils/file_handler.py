"""
File Handler Utility
Provides SQLite-backed storage while preserving the existing JSON-like API.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

# Base data directory
DATA_DIR = Path("data")
DB_PATH = DATA_DIR / "billing.db"

TABLE_CONFIG = {
    "users.json": ("users", "username"),
    "customers.json": ("customers", "customer_id"),
    "meters.json": ("meters", "meter_id"),
    "bills.json": ("bills", "bill_id"),
    "payments.json": ("payments", "payment_id"),
}


def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    DATA_DIR.mkdir(exist_ok=True)


def get_file_path(filename):
    """Return legacy JSON path for migration/backward compatibility."""
    ensure_data_dir()
    return DATA_DIR / filename


def get_db_path():
    """Return SQLite database path."""
    ensure_data_dir()
    return DB_PATH


def get_connection():
    """Open SQLite connection."""
    return sqlite3.connect(get_db_path())


def initialize_database():
    """Create SQLite tables if they do not already exist."""
    ensure_data_dir()
    with get_connection() as conn:
        cursor = conn.cursor()
        for _filename, (table_name, key_name) in TABLE_CONFIG.items():
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table_name} (
                    {key_name} TEXT PRIMARY KEY,
                    payload TEXT NOT NULL
                )
                """
            )
        conn.commit()


def _table_is_empty(filename):
    """Return True when the mapped SQLite table has no rows."""
    table_name, _key_name = TABLE_CONFIG[filename]
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0] == 0


def _read_legacy_json(filename, default=None):
    """Read a legacy JSON file directly from disk for migration."""
    filepath = get_file_path(filename)
    if not filepath.exists():
        return default if default is not None else {}

    try:
        with open(filepath, "r", encoding="utf-8") as file_obj:
            return json.load(file_obj)
    except (json.JSONDecodeError, IOError):
        return default if default is not None else {}


def migrate_legacy_json_if_needed(filename):
    """Import legacy JSON data into SQLite the first time a table is used."""
    initialize_database()
    if filename not in TABLE_CONFIG or not _table_is_empty(filename):
        return

    legacy_data = _read_legacy_json(filename, {})
    if legacy_data:
        save_json(filename, legacy_data)


def load_json(filename, default=None):
    """
    Load data from SQLite and return it in the existing JSON-like structure.
    Args:
        filename: Legacy logical file name used throughout the app
        default: Default data structure if missing/corrupt
    Returns:
        Parsed data structure or default
    """
    if filename not in TABLE_CONFIG:
        return default if default is not None else {}

    initialize_database()
    migrate_legacy_json_if_needed(filename)

    table_name, key_name = TABLE_CONFIG[filename]
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {key_name}, payload FROM {table_name}")
            rows = cursor.fetchall()
    except sqlite3.Error:
        return default if default is not None else {}

    data = {}
    for record_key, payload in rows:
        try:
            data[record_key] = json.loads(payload)
        except json.JSONDecodeError:
            continue

    if not data and default is not None:
        return default
    return data


def save_json(filename, data):
    """
    Save data into SQLite using the existing JSON-like structure.
    Args:
        filename: Logical file/table name
        data: Dictionary keyed by the entity ID
    Returns:
        bool: True if successful
    """
    if filename not in TABLE_CONFIG:
        return False

    initialize_database()
    table_name, key_name = TABLE_CONFIG[filename]

    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"DELETE FROM {table_name}")
            if isinstance(data, dict):
                for record_key, payload in data.items():
                    cursor.execute(
                        f"INSERT INTO {table_name} ({key_name}, payload) VALUES (?, ?)",
                        (record_key, json.dumps(payload, ensure_ascii=False)),
                    )
            conn.commit()
        return True
    except sqlite3.Error as error:
        print(f"Error saving {filename}: {error}")
        return False


def initialize_data_files():
    """Initialize SQLite tables and migrate legacy JSON content if present."""
    initialize_database()

    users = load_json("users.json", {})
    if not users:
        users = {
            "admin": {
                "password": "admin123",
                "role": "admin",
                "name": "System Administrator",
                "email": "",
                "phone_number": "",
                "mfa_enabled": False,
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

    files_defaults = {
        "customers.json": {},
        "meters.json": {},
        "bills.json": {},
        "payments.json": {},
    }

    for filename, default in files_defaults.items():
        data = load_json(filename)
        if data is None:
            save_json(filename, default)
