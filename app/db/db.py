from typing import AsyncGenerator

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.const.url import DATABASE_URL

async_engine = create_async_engine(DATABASE_URL, future=True)


async def init_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        async_engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
