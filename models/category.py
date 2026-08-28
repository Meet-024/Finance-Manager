from typing import Optional, Dict, Any


class Category:
    VALID_TYPES = ("income", "expense")

    def __init__(
        self,
        user_id: int,
        name: str,
        category_type: str,
        category_id: Optional[int] = None
    ):
        self._category_id = category_id
        self._user_id = user_id
        self._name = name.strip()
        
        type_lower = category_type.strip().lower()
        if type_lower not in self.VALID_TYPES:
            raise ValueError(f"Category type must be one of {self.VALID_TYPES}")
        self._type = type_lower

    @property
    def id(self) -> Optional[int]:
        return self._category_id

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Category name cannot be empty.")
        self._name = value.strip()

    @property
    def type(self) -> str:
        return self._type

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._category_id,
            "user_id": self._user_id,
            "name": self._name,
            "type": self._type
        }

    @classmethod
    def from_row(cls, row) -> "Category":
        return cls(
            category_id=row["id"],
            user_id=row["user_id"],
            name=row["name"],
            category_type=row["type"]
        )

    def __repr__(self) -> str:
        return f"<Category id={self._category_id} name='{self._name}' type='{self._type}'>"
