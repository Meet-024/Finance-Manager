import re
from datetime import datetime
from utils.exceptions import (
    ValidationError,
    InvalidAmountError,
    InvalidDateError
)


def validate_amount(amount_str: str) -> float:
    if not amount_str or not amount_str.strip():
        raise InvalidAmountError("Amount cannot be empty.")
    
    cleaned = amount_str.replace('₹', '').replace(',', '').strip()

    try:
        amount = float(cleaned)
    except ValueError:
        raise InvalidAmountError("Invalid amount. Please enter a valid numeric amount.")

    if amount <= 0:
        raise InvalidAmountError("Amount must be greater than zero.")

    return round(amount, 2)


def validate_email(email_str: str) -> str:
    if not email_str or not email_str.strip():
        raise ValidationError("Email cannot be empty.")

    email = email_str.strip().lower()
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(pattern, email):
        raise ValidationError("Please enter a valid email address (e.g., user@example.com).")

    return email


def validate_date(date_str: str) -> str:
    if not date_str or not date_str.strip():
        raise InvalidDateError("Date cannot be empty.")

    cleaned_date = date_str.strip()
    
    try:
        parsed_dt = datetime.strptime(cleaned_date, "%d-%m-%Y")
        return parsed_dt.strftime("%Y-%m-%d")
    except ValueError:
        raise InvalidDateError("Invalid date format or date does not exist. Use DD-MM-YYYY (e.g., 28-08-2026).")


def format_date_for_display(iso_date_str: str) -> str:
    try:
        parsed_dt = datetime.strptime(iso_date_str, "%Y-%m-%d")
        return parsed_dt.strftime("%d-%m-%Y")
    except (ValueError, TypeError):
        return iso_date_str


def validate_choice(choice_str: str, min_val: int, max_val: int) -> int:
    if not choice_str or not choice_str.strip():
        raise ValidationError("Choice cannot be empty.")

    try:
        choice = int(choice_str.strip())
    except ValueError:
        raise ValidationError(f"Invalid choice. Please enter a number between {min_val} and {max_val}.")

    if not (min_val <= choice <= max_val):
        raise ValidationError(f"Invalid choice. Please select an option between {min_val} and {max_val}.")

    return choice


def validate_required_text(text_str: str, field_name: str = "Field") -> str:
    if not text_str or not text_str.strip():
        raise ValidationError(f"{field_name} cannot be empty.")
    return text_str.strip()
