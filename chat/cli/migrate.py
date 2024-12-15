import asyncio
import logging

import asyncpg

from settings import DB_SETTINGS


logger = logging.getLogger("uvicorn")


async def main() -> None:
    """Генерация миграций."""

    conn = await asyncpg.connect(dsn=DB_SETTINGS.dsn)

    async with conn.transaction():
        # create users table
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
          id SERIAL PRIMARY KEY,
          username VARCHAR(50) NOT NULL,
          email TEXT NOT NULL UNIQUE,
          password TEXT,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
      """)

        await conn.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at()
          RETURNS TRIGGER AS $$
        BEGIN
          NEW.updated_at = NOW();
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
      """)

        await conn.execute("""
        CREATE OR REPLACE TRIGGER update_updated_at_trigger
          BEFORE UPDATE ON users
          FOR EACH ROW
          EXECUTE PROCEDURE update_updated_at();
      """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS chats (
          id SERIAL PRIMARY KEY,
          uid UUID NOT NULL DEFAULT gen_random_uuid(),
          creator_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
          companion_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
          updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
      """)

        await conn.execute("""
        ALTER TABLE chats
        ADD UNIQUE(creator_id, companion_id);
      """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
          id SERIAL PRIMARY KEY,
          uid UUID NOT NULL DEFAULT gen_random_uuid(),
          chat_id INTEGER NOT NULL REFERENCES chats (id) ON DELETE CASCADE,
          sender_id INTEGER NOT NULL REFERENCES users (id) ON DELETE CASCADE,
          text TEXT NOT NULL,
          created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
      """)

        await conn.execute("""
        CREATE
          UNIQUE INDEX 
        ON 
          chats (LEAST(creator_id, companion_id), GREATEST(creator_id, companion_id));
      """)

    logger.info("Migration completed")


if __name__ == "__main__":
    asyncio.run(main())
