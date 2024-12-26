from core.constants import USER_FILES_QUOTA_MB


def is_available_user_quota_for_file(user_current_files_size: float, file_size: float) -> bool:
    """Доступна ли квота пользователя для загрузки файла.

    :param int user_current_files_size: Текущий размер всех файлов пользователя.

    :param int file_size: Размер файла.

    :return bool: True - доступна, False - нет доступа.
    """
    return user_current_files_size + file_size <= USER_FILES_QUOTA_MB
