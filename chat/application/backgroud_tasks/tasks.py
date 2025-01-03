import logging
from uuid import UUID

from application.backgroud_tasks.broker import broker
from application.files.files import calculate_file_size_from_bytes_to_mb
from infrastructure.databases import database
from infrastructure.repositories.messages import MessageRepository
from infrastructure.repositories.users import UserRepository
from infrastructure.storages.s3 import FileStorage


logger = logging.getLogger("uvicorn")


@broker.task("save_new_chat_message_in_db")
async def save_new_chat_message_in_db(
    chat_id: int, uid: UUID, sender_id: int, text: str | None = None, file: str | None = None
) -> None:
    """Сохранить новое сообщение в базу данных.

    :param int chat_id: ID чата.

    :param UUID uid: Уникальный идентификатор сообщения.

    :param int sender_id: ID отправителя.

    :param str text | None: Текст сообщения.

    :param str file | None: Путь к файлу.
    """

    async with database.get_connection() as connection:
        message_repository = MessageRepository(connection)

        await message_repository.add_with_uid(uid, chat_id, sender_id, text, file)

        logger.info(
            f"Task message saved in DB: chat_id={chat_id},"
            "sender_id={sender_id}, text={text}, file={file}"
        )


@broker.task("remove_message_with_file")
async def remove_message_with_file(file_path: str, owner_id: int) -> None:
    """Удалить сообщение с файлом. Пересчитать квоту пользователя.

    :param str file: Путь к файлу.

    :param int owner_id: ID пользователя.
    """

    storage = FileStorage()

    try:
        file_info = await storage.get_object_info(file_path)

        file_size_bytes = int(file_info["ContentLength"])
        file_size_mb = calculate_file_size_from_bytes_to_mb(file_size_bytes)

        async with database.get_connection() as connection:
            user_repository = UserRepository(connection)

            await user_repository.decrement_files_mb(owner_id, file_size_mb)

        await storage.delete_object(file_path)

        logger.info(f"Task remove message with file: {file_path} complete")
    except Exception as exc:
        logger.error(f"Task remove message with file: {file_path} failed with error: {exc}")
