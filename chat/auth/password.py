import argon2


def hash_password(password: str, ) -> str:
    b_password: bytes = password.encode()
    save_password: bytes = argon2.PasswordHasher().hash(b_password)
    return save_password

def verify_password(verified_password: str, _hash: str) -> bool:
    try:
        return argon2.PasswordHasher().verify(_hash.encode(), verified_password.encode())
    except argon2.exceptions.VerifyMismatchError:
        return False
