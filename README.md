# Electricity & Water Billing System

A console-based Python application for managing utility customers, meter readings, monthly billing, payments, and reports.

## Features

- User login with role-based access for `admin` and `staff`
- Optional MFA flow for user accounts
- Customer management with generated IDs like `CUST-001`
- Electricity and water meter assignment and reading updates
- Monthly bill generation using stored meter usage
- Payment recording with partial and full payment support
- Reporting for monthly summaries, yearly summaries, unpaid bills, and customer statements
- Bill export to text files and PDF files

## Billing Rates

- Electricity: `750` Riel per kWh
- Water: `500` Riel per m³

These values are defined in [models/bill.py](e:/Python/electricity_water_billing/models/bill.py).

## Project Structure

```text
electricity_water_billing/
├── auth/              # Authentication and role management
├── controllers/       # Business logic for customers, meters, billing, and payments
├── data/              # JSON data storage
├── models/            # Core data models
├── prints/            # Exported bills (generated files)
├── reports/           # Report generation
├── utils/             # File handling helpers
└── main.py            # Application entry point
```

## Requirements

- Python 3.10 or newer
- Standard library only for core features
- `reportlab` is optional and only needed for PDF export

Install the optional PDF dependency with:

```powershell
pip install reportlab
```

## How To Run

```powershell
python main.py
```

## Default Login

When the project initializes an empty `data/users.json`, it creates a default admin account:

- Username: `admin`
- Password: `admin123`

If your `data/users.json` already exists, the app will use the accounts stored there.

## Data Files

The application stores its data in JSON files inside [data](e:/Python/electricity_water_billing/data):

- `users.json`
- `customers.json`
- `meters.json`
- `bills.json`
- `payments.json`

## Main Workflows

1. Log in as an admin or staff user.
2. Add customers.
3. Assign electricity and water meters.
4. Enter new meter readings.
5. Generate monthly bills.
6. Record payments.
7. View reports or export bills.

## Notes Before Pushing To GitHub

- Do not commit generated files such as `__pycache__/` or exported files in `prints/`
- Review `data/*.json` before pushing if they contain real customer or user information
- Add a `.gitignore` before the first push for a cleaner repository history

## Entry Point

The main application starts from [main.py](e:/Python/electricity_water_billing/main.py).
