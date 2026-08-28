# Personal Finance Manager

A robust, modular, object-oriented **console-based Personal Finance Manager** application built in **Python** backed by an **SQLite** database.

Designed as a CV/resume-worthy software engineering project demonstrating Python best practices, standard libraries (`sqlite3`, `hashlib`, `hmac`, `datetime`, `csv`), custom exception handling, separation of concerns, and parameterized SQL security.

---

## Key Features

- **User Authentication**: Secure registration and multi-user login using PBKDF2-HMAC-SHA256 password hashing with unique random salts.
- **Default & Custom Category Management**: Seeded default categories (Salary, Freelancing, Food, Travel, etc.) upon user registration with full custom CRUD and relational integrity protection preventing deletion of categories tied to active transactions.
- **Income & Expense Tracking**: Record financial transactions with strict validation (positive amounts, formatted dates in `DD-MM-YYYY`, type matching).
- **Transaction Search & Multi-criteria Filtering**: Flexible keyword search (descriptions, categories, amounts, dates) and multi-parameter filters (transaction type, date range, minimum and maximum amounts).
- **Financial Analytics & Reporting**:
  - **Overall Summary**: Total income, total expenses, net balance, transaction counts.
  - **Monthly Reports**: Selected month/year breakdown, highest spending category, highest single expense, and average daily expense.
  - **Category-wise Spending Report**: Categorized expense totals with spending percentage shares and high/low spending identifiers.
- **CSV Data Export Engine**: Export all user transactions or monthly reports directly into clean CSV files under `reports/`.
- **Data Security & Multi-User Isolation**: Parameterized SQL queries preventing SQL injection, strict user data isolation, and encrypted credential storage.

---

## Technologies Used

- **Python 3.x**: Core application runtime
- **SQLite3 & SQL**: Relational database storage with foreign key constraints (`PRAGMA foreign_keys = ON;`)
- **Standard Libraries**: `hashlib`, `hmac`, `datetime`, `csv`, `re`, `os`, `sys`

---

## Project Structure

```text
Expense Manager Python/
├── main.py                     # Entry point & interactive console CLI menu controller
├── requirements.txt            # Project dependencies documentation
├── README.md                   # Complete documentation
├── .gitignore                  # Git ignore patterns
│
├── database/                   # Database access layer
│   ├── __init__.py
│   ├── connection.py           # Connection factory, context manager, FK pragma
│   └── schema.py               # Table DDL scripts and DB initialization
│
├── models/                     # Object-Oriented Domain Entities
│   ├── __init__.py
│   ├── user.py                 # User domain entity
│   ├── category.py             # Category entity
│   └── transaction.py          # Transaction entity
│
├── services/                   # Business Logic Layer
│   ├── __init__.py
│   ├── auth_service.py         # Registration, login, security, default seeding
│   ├── category_service.py     # Custom category CRUD & deletion protection
│   ├── transaction_service.py  # Income/expense CRUD, search, filter
│   └── report_service.py       # Financial summaries, monthly reports, CSV export
│
├── utils/                      # Shared Utilities & Security Framework
│   ├── __init__.py
│   ├── exceptions.py           # Custom domain exception hierarchy
│   ├── security.py             # Password Hashing & Verification
│   ├── validators.py           # Reusable input validators
│   └── helpers.py              # Pretty ASCII table formatter & layout tools
│
└── reports/                    # Target directory for generated CSV reports
    └── .gitkeep
```

---

## Installation & Setup

### 1. Clone Repository & Navigate

```bash
git clone <repository-url>
cd "Finance Manager"
```

### 2. Set Up Virtual Environment (Optional)

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Running the Application

To launch the interactive console application:

```bash
python main.py
```

---

## Database Architecture

The SQLite database (`finance.db`) utilizes 3 relational tables:

```text
+-------------------+       +-------------------+       +-------------------+
|       users       |       |    categories     |       |   transactions    |
+-------------------+       +-------------------+       +-------------------+
| id (PK)           |<-----\| id (PK)           |<-----\| id (PK)           |
| name              |       | user_id (FK)      |       | user_id (FK)      |
| email (UNIQUE)    |       | name              |       | category_id (FK)  |
| password_hash     |       | type              |       | type              |
| created_at        |       +-------------------+       | amount            |
+-------------------+                                   | description       |
                                                        | transaction_date  |
                                                        | created_at        |
                                                        +-------------------+
```

- **Foreign Keys**: Enabled via `PRAGMA foreign_keys = ON;`.
- **Integrity Rules**: Deleting a user cascade-deletes their categories and transactions (`ON DELETE CASCADE`). Deleting a category with active transactions is blocked (`ON DELETE RESTRICT`).

---

## Future Improvements

- Budget limit setting with threshold alert notifications.
- Recurring automated transactions (e.g. monthly subscriptions/rent).
- Graphical dashboard using Tkinter or PyQt.
- REST API layer built with FastAPI.
- Migration support for PostgreSQL / MySQL backends.
