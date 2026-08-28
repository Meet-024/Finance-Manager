from typing import List, Optional, Dict, Any
from database.connection import DatabaseConnection, db_manager
from models.transaction import Transaction
from utils.validators import (
    validate_amount,
    validate_date,
    validate_required_text,
    format_date_for_display
)
from utils.exceptions import (
    ValidationError,
    InvalidAmountError,
    TransactionNotFoundError,
    CategoryNotFoundError
)


class TransactionService:
    def __init__(self, db: DatabaseConnection = db_manager):
        self.db = db

    def add_transaction(
        self,
        user_id: int,
        category_id: int,
        transaction_type: str,
        amount: float,
        description: str,
        date_str: str
    ) -> Transaction:
        t_type = transaction_type.strip().lower()
        if t_type not in ('income', 'expense'):
            raise ValidationError("Transaction type must be 'income' or 'expense'.")

        if amount <= 0:
            raise InvalidAmountError("Amount must be greater than zero.")

        iso_date = validate_date(date_str)

        with self.db.cursor() as cur:
            cur.execute(
                "SELECT id, name, type FROM categories WHERE id = ? AND user_id = ?;",
                (category_id, user_id)
            )
            cat_row = cur.fetchone()
            if not cat_row:
                raise CategoryNotFoundError("Selected category does not exist or does not belong to you.")

            if cat_row["type"] != t_type:
                raise ValidationError(f"Category '{cat_row['name']}' is a {cat_row['type']} category, not a {t_type} category.")

            cur.execute(
                """
                INSERT INTO transactions (user_id, category_id, type, amount, description, transaction_date)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (user_id, category_id, t_type, amount, description.strip(), iso_date)
            )
            tx_id = cur.lastrowid

            cur.execute(
                """
                SELECT t.*, c.name as category_name
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.id = ?;
                """,
                (tx_id,)
            )
            return Transaction.from_row(cur.fetchone())

    def get_transactions(self, user_id: int, limit: Optional[int] = None) -> List[Transaction]:
        query = """
            SELECT t.*, c.name as category_name
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ?
            ORDER BY t.transaction_date DESC, t.id DESC
        """
        params = [user_id]
        if limit and limit > 0:
            query += " LIMIT ?"
            params.append(limit)

        with self.db.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            return [Transaction.from_row(r) for r in rows]

    def get_transaction_by_id(self, user_id: int, transaction_id: int) -> Transaction:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT t.*, c.name as category_name
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.id = ? AND t.user_id = ?;
                """,
                (transaction_id, user_id)
            )
            row = cur.fetchone()
            if not row:
                raise TransactionNotFoundError(f"Transaction ID {transaction_id} not found.")
            return Transaction.from_row(row)

    def search_transactions(self, user_id: int, keyword: str) -> List[Transaction]:
        if not keyword or not keyword.strip():
            return self.get_transactions(user_id)

        term = f"%{keyword.strip()}%"
        date_term = term
        try:
            iso = validate_date(keyword)
            date_term = f"%{iso}%"
        except Exception:
            pass

        query = """
            SELECT t.*, c.name as category_name
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ? AND (
                t.description LIKE ? OR
                c.name LIKE ? OR
                CAST(t.amount AS TEXT) LIKE ? OR
                t.transaction_date LIKE ? OR
                t.transaction_date LIKE ?
            )
            ORDER BY t.transaction_date DESC, t.id DESC
        """

        with self.db.cursor() as cur:
            cur.execute(query, (user_id, term, term, term, term, date_term))
            rows = cur.fetchall()
            return [Transaction.from_row(r) for r in rows]

    def filter_transactions(
        self,
        user_id: int,
        transaction_type: Optional[str] = None,
        category_id: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        min_amount: Optional[float] = None,
        max_amount: Optional[float] = None
    ) -> List[Transaction]:
        conditions = ["t.user_id = ?"]
        params: List[Any] = [user_id]

        if transaction_type and transaction_type.strip().lower() in ('income', 'expense'):
            conditions.append("t.type = ?")
            params.append(transaction_type.strip().lower())

        if category_id:
            conditions.append("t.category_id = ?")
            params.append(category_id)

        if start_date:
            iso_start = validate_date(start_date)
            conditions.append("t.transaction_date >= ?")
            params.append(iso_start)

        if end_date:
            iso_end = validate_date(end_date)
            conditions.append("t.transaction_date <= ?")
            params.append(iso_end)

        if min_amount is not None:
            conditions.append("t.amount >= ?")
            params.append(min_amount)

        if max_amount is not None:
            conditions.append("t.amount <= ?")
            params.append(max_amount)

        where_clause = " AND ".join(conditions)

        query = f"""
            SELECT t.*, c.name as category_name
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE {where_clause}
            ORDER BY t.transaction_date DESC, t.id DESC
        """

        with self.db.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            return [Transaction.from_row(r) for r in rows]

    def edit_transaction(
        self,
        user_id: int,
        transaction_id: int,
        amount: Optional[float] = None,
        category_id: Optional[int] = None,
        description: Optional[str] = None,
        date_str: Optional[str] = None
    ) -> Transaction:
        tx = self.get_transaction_by_id(user_id, transaction_id)

        updates = []
        params = []

        if amount is not None:
            if amount <= 0:
                raise ValidationError("Amount must be greater than zero.")
            updates.append("amount = ?")
            params.append(round(amount, 2))

        if category_id is not None:
            with self.db.cursor() as cur:
                cur.execute(
                    "SELECT id, type FROM categories WHERE id = ? AND user_id = ?;",
                    (category_id, user_id)
                )
                cat_row = cur.fetchone()
                if not cat_row:
                    raise CategoryNotFoundError("Selected category does not exist.")
                if cat_row["type"] != tx.type:
                    raise ValidationError(f"Category type does not match transaction type '{tx.type}'.")
            updates.append("category_id = ?")
            params.append(category_id)

        if description is not None:
            updates.append("description = ?")
            params.append(description.strip())

        if date_str is not None:
            iso_date = validate_date(date_str)
            updates.append("transaction_date = ?")
            params.append(iso_date)

        if not updates:
            return tx

        params.extend([transaction_id, user_id])
        update_sql = f"UPDATE transactions SET {', '.join(updates)} WHERE id = ? AND user_id = ?;"

        with self.db.cursor() as cur:
            cur.execute(update_sql, params)

        return self.get_transaction_by_id(user_id, transaction_id)

    def delete_transaction(self, user_id: int, transaction_id: int) -> bool:
        tx = self.get_transaction_by_id(user_id, transaction_id)

        with self.db.cursor() as cur:
            cur.execute(
                "DELETE FROM transactions WHERE id = ? AND user_id = ?;",
                (tx.id, user_id)
            )
            return True
