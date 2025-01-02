from decimal import ROUND_DOWN, Decimal

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


def calculate_file_size_from_bytes_representation(content: bytes) -> Decimal:
    """
    Расчет размера файла в мегабайтах.

    :param `bytes` content: Содержимое файла.

    :return `float`: Размер файла в мегабайтах.
    """
    return Decimal(len(content) / (1024 * 1024)).quantize(Decimal("0.0001"), rounding=ROUND_DOWN)
