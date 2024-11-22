from infrastructure.databases.postgres import PostgresDB

from settings import DB_SETTINGS


database = PostgresDB(dsn=DB_SETTINGS.dsn)
