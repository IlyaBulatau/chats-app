import logging

from backgroud_tasks.broker import broker
from infrastructure.databases import database
from infrastructure.repositories.messages import MessageRepository


logger = logging.getLogger("uvicorn")


@broker.task("save_new_chat_message_in_db")
async def save_new_chat_message_in_db(chat_id: int, sender_id: int, text: str) -> None:
    """Сохранить новое сообщение в базу данных."""
    async with database.get_connection() as connection:
        message_repository = MessageRepository(connection)
        await message_repository.add(chat_id, sender_id, text)
        logger.info(
            f"Task message saved in DB: chat_id={chat_id}, sender_id={sender_id}, text={text}"
        )
