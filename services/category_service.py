from typing import List, Optional
from database.connection import DatabaseConnection, db_manager
from models.category import Category
from utils.validators import validate_required_text
from utils.exceptions import (
    ValidationError,
    CategoryNotFoundError,
    CategoryInUseError
)


class CategoryService:
    def __init__(self, db: DatabaseConnection = db_manager):
        self.db = db

    def get_categories(self, user_id: int, category_type: Optional[str] = None) -> List[Category]:
        with self.db.cursor() as cur:
            if category_type:
                c_type = category_type.strip().lower()
                cur.execute(
                    "SELECT * FROM categories WHERE user_id = ? AND type = ? ORDER BY name ASC;",
                    (user_id, c_type)
                )
            else:
                cur.execute(
                    "SELECT * FROM categories WHERE user_id = ? ORDER BY type DESC, name ASC;",
                    (user_id,)
                )
            rows = cur.fetchall()
            return [Category.from_row(row) for row in rows]

    def add_category(self, user_id: int, name: str, category_type: str) -> Category:
        cat_name = validate_required_text(name, "Category name")
        c_type = category_type.strip().lower()
        if c_type not in ('income', 'expense'):
            raise ValidationError("Category type must be either 'income' or 'expense'.")

        with self.db.cursor() as cur:
            cur.execute(
                "SELECT id FROM categories WHERE user_id = ? AND LOWER(name) = LOWER(?) AND type = ?;",
                (user_id, cat_name, c_type)
            )
            if cur.fetchone():
                raise ValidationError(f"A {c_type} category named '{cat_name}' already exists.")

            cur.execute(
                "INSERT INTO categories (user_id, name, type) VALUES (?, ?, ?);",
                (user_id, cat_name, c_type)
            )
            cat_id = cur.lastrowid

            cur.execute("SELECT * FROM categories WHERE id = ?;", (cat_id,))
            row = cur.fetchone()
            return Category.from_row(row)

    def rename_category(self, user_id: int, category_id: int, new_name: str) -> Category:
        cat_name = validate_required_text(new_name, "New category name")

        with self.db.cursor() as cur:
            cur.execute(
                "SELECT * FROM categories WHERE id = ? AND user_id = ?;",
                (category_id, user_id)
            )
            existing = cur.fetchone()
            if not existing:
                raise CategoryNotFoundError("Category not found or access denied.")

            cat_type = existing["type"]

            cur.execute(
                "SELECT id FROM categories WHERE user_id = ? AND LOWER(name) = LOWER(?) AND type = ? AND id != ?;",
                (user_id, cat_name, cat_type, category_id)
            )
            if cur.fetchone():
                raise ValidationError(f"A {cat_type} category named '{cat_name}' already exists.")

            cur.execute(
                "UPDATE categories SET name = ? WHERE id = ? AND user_id = ?;",
                (cat_name, category_id, user_id)
            )

            cur.execute("SELECT * FROM categories WHERE id = ?;", (category_id,))
            return Category.from_row(cur.fetchone())

    def delete_category(self, user_id: int, category_id: int) -> bool:
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT * FROM categories WHERE id = ? AND user_id = ?;",
                (category_id, user_id)
            )
            cat = cur.fetchone()
            if not cat:
                raise CategoryNotFoundError("Category not found or access denied.")

            cur.execute(
                "SELECT COUNT(id) as tx_count FROM transactions WHERE category_id = ? AND user_id = ?;",
                (category_id, user_id)
            )
            tx_count = cur.fetchone()["tx_count"]

            if tx_count > 0:
                raise CategoryInUseError(
                    f"Cannot delete category '{cat['name']}' because it has {tx_count} associated transaction(s)."
                )

            cur.execute(
                "DELETE FROM categories WHERE id = ? AND user_id = ?;",
                (category_id, user_id)
            )
            return True
