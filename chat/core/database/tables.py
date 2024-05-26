import sqlalchemy as db
from sqlalchemy import Column
from sqlalchemy.orm import registry, relationship

from core import constancies as cons


mapper_registry = registry()

user_table = db.Table(
    "users",
    mapper_registry.metadata,
    Column("id", db.Integer, primary_key=True, autoincrement=True, index=True),
    Column("username", db.String(cons.USERNAME_LENGHT), nullable=False, index=True),
    Column("email", db.String, nullable=False, unique=True, index=True),
    Column("password", db.String, nullable=True),
    Column("created_at", db.DateTime, server_default=db.sql.func.now(), nullable=False),
    Column("updated_at", db.DateTime, onupdate=db.sql.func.now(), nullable=True),
)

chat_table = db.Table(
    "chats",
    mapper_registry.metadata,
    Column("id", db.Integer, primary_key=True, autoincrement=True, index=True),
    Column("title", db.String(cons.CHAT_NAME_LENGHT), nullable=False, index=True),
    Column("owner", db.Integer, db.ForeignKey("users.id"), nullable=False, index=True),
)

message_table = db.Table(
    "messages",
    mapper_registry.metadata,
    Column("id", db.Integer, primary_key=True, autoincrement=True, index=True),
    Column("text", db.String(cons.MESSAGE_LENGHT), nullable=False),
    Column("chat_id", db.Integer, db.ForeignKey("chats.id"), nullable=False, index=True),
    Column("user_id", db.Integer, db.ForeignKey("users.id"), nullable=False, index=True),
)

chats_users_table = db.Table(
    "chats_users",
    mapper_registry.metadata,
    Column("id", db.Integer, primary_key=True, autoincrement=True, index=True),
    Column("chat_id", db.Integer, db.ForeignKey("chats.id"), primary_key=True),
    Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
)


def setup_mapper() -> None:
    from core.domains import Chat, Message, User

    mapper_registry.map_imperatively(
        User,
        user_table,
        properties={
            "messages": relationship(Message, backref="user"),
            "chats": relationship(Chat, secondary=chats_users_table, back_populates="user"),
        },
    )
    mapper_registry.map_imperatively(
        Message,
        message_table,
    )
    mapper_registry.map_imperatively(
        Chat,
        chat_table,
        properties={
            "messages": relationship(Message, backref="chat"),
            "user": relationship(User, secondary=chats_users_table, back_populates="chats"),
        },
    )
