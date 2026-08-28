from typing import Optional, Dict, Any
from utils.validators import format_date_for_display


class Transaction:
    VALID_TYPES = ("income", "expense")

    def __init__(
        self,
        user_id: int,
        category_id: int,
        transaction_type: str,
        amount: float,
        description: str,
        transaction_date: str,
        transaction_id: Optional[int] = None,
        category_name: Optional[str] = None,
        created_at: Optional[str] = None
    ):
        self._transaction_id = transaction_id
        self._user_id = user_id
        self._category_id = category_id
        
        type_lower = transaction_type.strip().lower()
        if type_lower not in self.VALID_TYPES:
            raise ValueError(f"Transaction type must be one of {self.VALID_TYPES}")
        self._type = type_lower

        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        self._amount = round(amount, 2)
        
        self._description = description.strip() if description else ""
        self._transaction_date = transaction_date
        self._category_name = category_name
        self._created_at = created_at

    @property
    def id(self) -> Optional[int]:
        return self._transaction_id

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def category_id(self) -> int:
        return self._category_id

    @property
    def category_name(self) -> Optional[str]:
        return self._category_name

    @property
    def type(self) -> str:
        return self._type

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def description(self) -> str:
        return self._description

    @property
    def transaction_date(self) -> str:
        return self._transaction_date

    @property
    def display_date(self) -> str:
        return format_date_for_display(self._transaction_date)

    @property
    def created_at(self) -> Optional[str]:
        return self._created_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._transaction_id,
            "user_id": self._user_id,
            "category_id": self._category_id,
            "category_name": self._category_name,
            "type": self._type,
            "amount": self._amount,
            "description": self._description,
            "transaction_date": self._transaction_date,
            "display_date": self.display_date,
            "created_at": self._created_at
        }

    @classmethod
    def from_row(cls, row) -> "Transaction":
        category_name = row["category_name"] if "category_name" in row.keys() else None
        return cls(
            transaction_id=row["id"],
            user_id=row["user_id"],
            category_id=row["category_id"],
            transaction_type=row["type"],
            amount=row["amount"],
            description=row["description"] if row["description"] else "",
            transaction_date=row["transaction_date"],
            category_name=category_name,
            created_at=row["created_at"] if "created_at" in row.keys() else None
        )

    def __repr__(self) -> str:
        return f"<Transaction id={self._transaction_id} type='{self._type}' amount={self._amount} date='{self._transaction_date}'>"
