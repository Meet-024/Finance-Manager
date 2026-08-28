import csv
import os
import calendar
from datetime import datetime
from typing import Dict, Any, List, Optional
from database.connection import DatabaseConnection, db_manager
from utils.validators import format_date_for_display


class ReportService:
    def __init__(self, db: DatabaseConnection = db_manager):
        self.db = db

    def get_financial_summary(self, user_id: int) -> Dict[str, Any]:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT
                    COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_income,
                    COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_expenses,
                    COUNT(CASE WHEN type = 'income' THEN 1 END) as income_count,
                    COUNT(CASE WHEN type = 'expense' THEN 1 END) as expense_count
                FROM transactions
                WHERE user_id = ?;
                """,
                (user_id,)
            )
            row = cur.fetchone()

            total_income = row["total_income"]
            total_expenses = row["total_expenses"]
            balance = total_income - total_expenses

            return {
                "total_income": total_income,
                "total_expenses": total_expenses,
                "balance": balance,
                "income_count": row["income_count"],
                "expense_count": row["expense_count"]
            }

    def get_monthly_report(self, user_id: int, month: int, year: int) -> Dict[str, Any]:
        month_str = f"{year}-{month:02d}"
        month_name = calendar.month_name[month]

        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT
                    COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0) as total_income,
                    COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0) as total_expenses
                FROM transactions
                WHERE user_id = ? AND strftime('%Y-%m', transaction_date) = ?;
                """,
                (user_id, month_str)
            )
            totals = cur.fetchone()
            total_income = totals["total_income"]
            total_expenses = totals["total_expenses"]
            remaining_balance = total_income - total_expenses

            cur.execute(
                """
                SELECT c.name as category_name, SUM(t.amount) as category_total
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ? AND t.type = 'expense' AND strftime('%Y-%m', t.transaction_date) = ?
                GROUP BY c.name
                ORDER BY category_total DESC;
                """,
                (user_id, month_str)
            )
            cat_rows = cur.fetchall()
            expense_breakdown = {row["category_name"]: row["category_total"] for row in cat_rows}

            highest_spending_category = cat_rows[0]["category_name"] if cat_rows else "N/A"

            cur.execute(
                """
                SELECT MAX(amount) as max_expense
                FROM transactions
                WHERE user_id = ? AND type = 'expense' AND strftime('%Y-%m', transaction_date) = ?;
                """,
                (user_id, month_str)
            )
            highest_single_expense = cur.fetchone()["max_expense"] or 0.0

            days_in_month = calendar.monthrange(year, month)[1]
            avg_daily_expense = total_expenses / days_in_month if days_in_month > 0 else 0.0

            return {
                "month_name": month_name,
                "month": month,
                "year": year,
                "total_income": total_income,
                "total_expenses": total_expenses,
                "remaining_balance": remaining_balance,
                "expense_breakdown": expense_breakdown,
                "highest_spending_category": highest_spending_category,
                "highest_single_expense": highest_single_expense,
                "avg_daily_expense": round(avg_daily_expense, 2)
            }

    def get_category_expense_report(self, user_id: int) -> Dict[str, Any]:
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT c.name as category_name, SUM(t.amount) as total_amount
                FROM transactions t
                JOIN categories c ON t.category_id = c.id
                WHERE t.user_id = ? AND t.type = 'expense'
                GROUP BY c.name
                ORDER BY total_amount DESC;
                """,
                (user_id,)
            )
            rows = cur.fetchall()

            total_expenses = sum(r["total_amount"] for r in rows)

            categories_data = []
            for r in rows:
                amt = r["total_amount"]
                pct = (amt / total_expenses * 100) if total_expenses > 0 else 0.0
                categories_data.append({
                    "category": r["category_name"],
                    "amount": amt,
                    "percentage": round(pct, 2)
                })

            highest_cat = categories_data[0]["category"] if categories_data else "N/A"
            lowest_cat = categories_data[-1]["category"] if categories_data else "N/A"

            return {
                "total_expenses": total_expenses,
                "categories": categories_data,
                "highest_category": highest_cat,
                "lowest_category": lowest_cat
            }

    def export_transactions_csv(
        self,
        user_id: int,
        month: Optional[int] = None,
        year: Optional[int] = None,
        output_dir: str = "reports"
    ) -> str:
        os.makedirs(output_dir, exist_ok=True)

        query = """
            SELECT t.id, t.transaction_date, t.type, c.name as category_name, t.description, t.amount
            FROM transactions t
            JOIN categories c ON t.category_id = c.id
            WHERE t.user_id = ?
        """
        params: List[Any] = [user_id]

        filename = "transactions_all.csv"
        if month and year:
            month_str = f"{year}-{month:02d}"
            query += " AND strftime('%Y-%m', t.transaction_date) = ?"
            params.append(month_str)
            filename = f"transactions_{year}_{month:02d}.csv"

        query += " ORDER BY t.transaction_date DESC, t.id DESC;"

        filepath = os.path.join(output_dir, filename)

        with self.db.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

            with open(filepath, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["ID", "Date", "Type", "Category", "Description", "Amount"])

                for row in rows:
                    display_date = format_date_for_display(row["transaction_date"])
                    formatted_type = row["type"].capitalize()
                    writer.writerow([
                        row["id"],
                        display_date,
                        formatted_type,
                        row["category_name"],
                        row["description"] or "",
                        f"{row['amount']:.2f}"
                    ])

        return os.path.abspath(filepath)
