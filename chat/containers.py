from dependency_injector import containers, providers

from application.chats.services.chats import ChatCreator, ChatReader
from application.chats.services.messages import MessageReader
from application.users.services import UserReader
from infrastructure.databases.postgres import PostgresDB
from infrastructure.repositories.chats import ChatRepository
from infrastructure.repositories.messages import MessageRepository
from infrastructure.repositories.users import UserRepository
from infrastructure.storages.s3 import FileStorage


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["presentation.rest.chats", "presentation.rest.users"]
    )

    config = providers.Configuration()

    file_storage = providers.Factory(FileStorage)
    database_provider = providers.Singleton(PostgresDB, dsn=config.database.dsn)
    database = database_provider()

    db_connection = providers.Resource(database.get_connection_for_di)

    user_repository = providers.Factory(UserRepository, db_connection)
    chat_repository = providers.Factory(ChatRepository, db_connection)
    message_repository = providers.Factory(MessageRepository, db_connection)

    chat_creator = providers.Factory(
        ChatCreator, user_repository=user_repository, chat_repository=chat_repository
    )
    chat_reader = providers.Factory(ChatReader, chat_repository=chat_repository)
    message_reader = providers.Factory(
        MessageReader,
        message_repository=message_repository,
        chat_repository=chat_repository,
        file_storage=file_storage,
    )
    user_reader = providers.Factory(UserReader, user_repository=user_repository)
