# Electricity & Water Billing System

A Python billing system for managing utility customers, meter readings, billing, payments, and reports.

The project supports:
- a CLI app
- a Tkinter desktop GUI
- SQLite storage in `data/billing.db`

## Features

- User login with `admin` and `staff` roles
- Optional MFA support
- Customer management
- Meter assignment and meter reading updates
- Monthly bill generation
- Payment tracking
- Reports and customer statements
- Bill export to text and PDF

## Billing Rates

- Electricity: `750` Riel per kWh
- Water: `500` Riel per m3

These values are defined in [bill.py](e:/Python/electricity_water_billing/models/bill.py).

## Requirements

- Python 3.10 or newer
- Windows, macOS, or Linux
- `reportlab` only if you want PDF export

Install the optional PDF package with:

```powershell
pip install reportlab
```

## Project Structure

```text
electricity_water_billing/
|-- auth/
|-- controllers/
|-- data/
|-- models/
|-- reports/
|-- TkinterGUI/
|-- utils/
|-- main.py
|-- run_gui.py
```

## How To Run This Project On Another Computer

1. Clone the repository:

```powershell
git clone <your-repo-url>
cd electricity_water_billing
```

2. Make sure Python is installed:

```powershell
python --version
```

3. Optional: create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

4. Optional: install PDF export support:

```powershell
pip install reportlab
```

5. Run either the CLI version or the GUI version.

CLI:

```powershell
python main.py
```

Tkinter GUI:

```powershell
python run_gui.py
```

## First Run

On first run, the app will:
- create the `data/` folder if it does not exist
- create the SQLite database at [billing.db](e:/Python/electricity_water_billing/data/billing.db)
- create a default admin account if the database is empty
- migrate old JSON files from `data/` into SQLite if they exist

Default admin login:

- Username: `admin`
- Password: `admin123`

## Database

The app now uses SQLite.

Main database file:
- [billing.db](e:/Python/electricity_water_billing/data/billing.db)

Legacy JSON files such as `users.json`, `customers.json`, `meters.json`, `bills.json`, and `payments.json` are only used for one-time migration when present.

## GUI Entry Point

The Tkinter desktop app starts from [run_gui.py](e:/Python/electricity_water_billing/run_gui.py) and uses pages inside [TkinterGUI](e:/Python/electricity_water_billing/TkinterGUI).

## CLI Entry Point

The console version starts from [main.py](e:/Python/electricity_water_billing/main.py).

## Main Workflow

1. Log in as admin or staff.
2. Add customers.
3. Assign electricity and water meters.
4. Enter meter readings.
5. Generate bills.
6. Record payments.
7. View reports or export invoices.

## Notes

- PDF export requires `reportlab`
- Generated print files go into `prints/`
- Real database files should usually not be pushed to a public repository
- Review `data/billing.db` before sharing the project
