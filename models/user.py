from typing import Optional, Dict, Any


class User:
    def __init__(
        self,
        name: str,
        email: str,
        password_hash: str,
        user_id: Optional[int] = None,
        created_at: Optional[str] = None
    ):
        self._user_id = user_id
        self._name = name
        self._email = email
        self._password_hash = password_hash
        self._created_at = created_at

    @property
    def id(self) -> Optional[int]:
        return self._user_id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Name cannot be empty.")
        self._name = value.strip()

    @property
    def email(self) -> str:
        return self._email

    @property
    def password_hash(self) -> str:
        return self._password_hash

    @property
    def created_at(self) -> Optional[str]:
        return self._created_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self._user_id,
            "name": self._name,
            "email": self._email,
            "created_at": self._created_at
        }

    @classmethod
    def from_row(cls, row) -> "User":
        return cls(
            user_id=row["id"],
            name=row["name"],
            email=row["email"],
            password_hash=row["password_hash"],
            created_at=row["created_at"]
        )

    def __repr__(self) -> str:
        return f"<User id={self._user_id} name='{self._name}' email='{self._email}'>"
