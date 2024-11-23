import argon2


def hash_password(
    password: str,
) -> str:
    """Хеширует пароль

    :param str password: Пароль который нужно захешировать

    :return str: Хеш от пароля
    """
    b_password: bytes = password.encode()
    save_password: str = argon2.PasswordHasher().hash(b_password)
    return save_password


def verify_password(verified_password: str, _hash: str) -> bool:
    """Валидация пароля на соответствие хешу

    :param str verified_password: Пароль который нужно проверить

    :param str _hash: Хеш с которым сравнивать

    :return bool: True если пароль соответствуют хешу
    """
    try:
        return argon2.PasswordHasher().verify(_hash.encode(), verified_password.encode())
    except argon2.exceptions.VerifyMismatchError:
        return False
