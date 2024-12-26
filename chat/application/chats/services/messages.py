from application.dto.files import FileReadDTO
from application.dto.messages import MessageReadDTO
from application.files.files import get_file_type, get_filename
from infrastructure.repositories.messages import MessageRepository
from infrastructure.storages.s3 import FileStorage


class MessageReader:
    """Читатель сообщений."""

    def __init__(self, message_repository: MessageRepository, flie_storage: FileStorage):
        self.message_repository = message_repository
        self.file_storage = flie_storage

    async def get_messages_from_db(self, chat_id: int) -> list[MessageReadDTO] | None:
        """Получить сообщения из базы данных.

        :param int chat_id: ID чата.

        :return list[`MessageReadDTO`] | None: Список сообщений.
        """
        messages = await self.message_repository.get_many_by_chat_id(chat_id)

        if not messages:
            return None

        result = []

        for message in messages:
            if message.file:
                name = get_filename(message.file)
                url = await self.file_storage.get_object_url(message.file)
                type = get_file_type(message.file)  # noqa: A001
                file = FileReadDTO(name=name, url=url, type=type)
            else:
                file = None

            result.append(
                MessageReadDTO(
                    id=message.id,
                    uid=message.uid,
                    chat_id=message.chat_id,
                    sender_id=message.sender_id,
                    text=message.text,
                    created_at=message.created_at,
                    file=file,
                )
            )

        return result
