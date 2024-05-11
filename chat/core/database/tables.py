import sqlalchemy as db
from sqlalchemy import Column
from sqlalchemy.orm import registry

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


def setup_mapper():
    from core.domains import User

    mapper_registry.map_imperatively(User, user_table)
