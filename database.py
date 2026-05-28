from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import settings

engine = create_async_engine(settings.database_url)                                             # engine = connection to the database

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)     # Factory that creates a database session. session is a transaction with db
                                                                                                #  each request gets its own session

class Base(DeclarativeBase):
    pass


async def get_db():                                                                             # dependency func that provides sessions to routes
    async with AsyncSessionLocal() as session:
        yield session