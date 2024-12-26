import logging

from application.backgroud_tasks.broker import broker
from infrastructure.databases import database
from infrastructure.repositories.messages import MessageRepository


logger = logging.getLogger("uvicorn")


@broker.task("save_new_chat_message_in_db")
async def save_new_chat_message_in_db(
    chat_id: int, sender_id: int, text: str | None = None, file: str | None = None
) -> None:
    """Сохранить новое сообщение в базу данных.

    :param int chat_id: ID чата.

    :param int sender_id: ID отправителя.

    :param str text | None: Текст сообщения.

    :param str file | None: Путь к файлу.
    """

    async with database.get_connection() as connection:
        message_repository = MessageRepository(connection)

        await message_repository.add(chat_id, sender_id, text, file)

        logger.info(
            f"Task message saved in DB: chat_id={chat_id},"
            "sender_id={sender_id}, text={text}, file={file}"
        )
