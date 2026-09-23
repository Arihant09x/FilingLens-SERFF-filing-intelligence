# check_db.py
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings


async def main() -> None:
    engine = create_async_engine(settings.database_url, pool_pre_ping=True)
    async with engine.connect() as conn:
        result = await conn.execute(text("select 1"))
        print("select 1 ->", result.scalar())
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())