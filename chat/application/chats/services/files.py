import base64
from uuid import UUID

from slugify import slugify

from application.chats.ws.validators import ReceivedFile
from core.constants import StorageDirectory
from infrastructure.storages.s3 import FileStorage


class FileMessageCreator:
    """Создает сообщения чата."""

    def __init__(self, file_storage: FileStorage, file_data: ReceivedFile) -> None:
        self.file_storage = file_storage
        self.file_data = file_data

    async def create(self, chat_uid: UUID) -> str:
        """
        Создает путь к файлу, загружает файл сохраняя его в хранилище,
        отдает путь к файлу в хранилище.

        :param `UUID` chat_uid: Уникальный идентификатор чата.

        :return `str`: Путь к файлу в хранилище.
        """

        file_dir = StorageDirectory.MESSAGE.format(chat_uid=chat_uid)
        file_name, file_extension = self.file_data.filename.rsplit(".", 1)
        file_path = file_dir + "/" + slugify(file_name) + "." + file_extension

        await self.file_storage.upload(
            file=base64.b64decode(self.file_data.content), path=file_path
        )

        return file_path
