import asyncio

import asyncpg

from settings import DB_SETTINGS


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
            CREATE TRIGGER update_updated_at_trigger
              BEFORE UPDATE ON users
              FOR EACH ROW
              EXECUTE PROCEDURE update_updated_at();
        """)


if __name__ == "__main__":
    asyncio.run(main())
