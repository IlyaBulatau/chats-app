from core.constants import FileType


IMAGE_EXTENSIONS = ("jpg", "jpeg", "png", "webp", "svg", "bmp", "raw")


def get_file_type(filename: str) -> str:
    """
    Определение типа файла. Тип определяется по расширению.

    :param `str` filename: Имя файла.

    :return `Literal["image", "file"]`: Тип файла.
    """
    _, file_extension = filename.rsplit(".", 1)

    return FileType.IMAGE if file_extension in IMAGE_EXTENSIONS else FileType.FILE


def get_filename(file_url: str) -> str:
    return file_url.rsplit("/", 1)[1]
