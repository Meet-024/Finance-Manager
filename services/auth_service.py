from typing import Optional, Dict, Any
from database.connection import DatabaseConnection, db_manager
from models.user import User
from utils.security import hash_password, verify_password
from utils.validators import validate_email, validate_required_text
from utils.exceptions import ValidationError, AuthenticationError, UserNotFoundError


DEFAULT_INCOME_CATEGORIES = [
    "Salary",
    "Freelancing",
    "Business",
    "Investment",
    "Other"
]

DEFAULT_EXPENSE_CATEGORIES = [
    "Food",
    "Travel",
    "Shopping",
    "Bills",
    "Education",
    "Entertainment",
    "Health",
    "Other"
]


class AuthService:
    def __init__(self, db: DatabaseConnection = db_manager):
        self.db = db

    def register_user(self, name: str, email: str, password: str, confirm_password: str) -> User:
        validated_name = validate_required_text(name, "Name")
        validated_email = validate_email(email)
        validate_required_text(password, "Password")

        if password != confirm_password:
            raise ValidationError("Password and confirm password do not match.")

        pwd_hash = hash_password(password)

        with self.db.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE email = ?;", (validated_email,))
            if cur.fetchone():
                raise AuthenticationError("An account with this email already exists.")

            cur.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?);",
                (validated_name, validated_email, pwd_hash)
            )
            user_id = cur.lastrowid

            for cat in DEFAULT_INCOME_CATEGORIES:
                cur.execute(
                    "INSERT INTO categories (user_id, name, type) VALUES (?, ?, 'income');",
                    (user_id, cat)
                )

            for cat in DEFAULT_EXPENSE_CATEGORIES:
                cur.execute(
                    "INSERT INTO categories (user_id, name, type) VALUES (?, ?, 'expense');",
                    (user_id, cat)
                )

            cur.execute("SELECT * FROM users WHERE id = ?;", (user_id,))
            row = cur.fetchone()
            return User.from_row(row)

    def login_user(self, email: str, password: str) -> User:
        validated_email = validate_email(email)
        validate_required_text(password, "Password")

        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE email = ?;", (validated_email,))
            row = cur.fetchone()

            if not row:
                raise AuthenticationError("Invalid email or password.")

            stored_hash = row["password_hash"]
            if not verify_password(password, stored_hash):
                raise AuthenticationError("Invalid email or password.")

            return User.from_row(row)

    def get_account_details(self, user_id: int) -> Dict[str, Any]:
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = ?;", (user_id,))
            user_row = cur.fetchone()
            if not user_row:
                raise UserNotFoundError("User account not found.")

            user = User.from_row(user_row)

            cur.execute(
                """
                SELECT 
                    COUNT(id) as total_tx,
                    COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_income,
                    COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_expenses
                FROM transactions
                WHERE user_id = ?;
                """,
                (user_id,)
            )
            stats_row = cur.fetchone()

            return {
                "name": user.name,
                "email": user.email,
                "created_at": user.created_at,
                "total_transactions": stats_row["total_tx"],
                "total_income": stats_row["total_income"],
                "total_expenses": stats_row["total_expenses"],
                "net_balance": stats_row["total_income"] - stats_row["total_expenses"]
            }
