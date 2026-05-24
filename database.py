from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"

engine = create_async_engine(                                                                   # engine = connection to the database
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},                                                  # this one is sqlite specific coz it normally supports only 1 thread
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)     # Factory that creates a database session. session is a transaction with db
                                                                                                #  each request gets its own session

class Base(DeclarativeBase):
    pass


async def get_db():                                                                             # dependency func that provides sessions to routes
    async with AsyncSessionLocal() as session:
        yield session