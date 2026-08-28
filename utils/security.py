import hashlib
import hmac
import os


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac(
        hash_name='sha256',
        password=password.encode('utf-8'),
        salt=salt,
        iterations=100000
    )
    return f"{salt.hex()}${key.hex()}"


def verify_password(password: str, stored_password_hash: str) -> bool:
    try:
        salt_hex, hash_hex = stored_password_hash.split('$')
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(hash_hex)

        key = hashlib.pbkdf2_hmac(
            hash_name='sha256',
            password=password.encode('utf-8'),
            salt=salt,
            iterations=100000
        )
        return hmac.compare_digest(key, expected_key)
    except (ValueError, AttributeError):
        return False
