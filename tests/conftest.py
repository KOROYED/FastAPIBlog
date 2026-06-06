import os
from collections.abc import AsyncGenerator

os.environ["DATABASE_URL"] = (
    "postgresql+psycopg://bloguser:blogpass@localhost/test_blog"
)
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from database import Base, get_db
from main import app

pytest_plugins = ["anyio"]                                                                  # lets run async tests (gives decorator to mark async)


@pytest.fixture(scope="session")                                                            # scope="session" means that this fixtre runs ONCE for ENTIRE test session
def anyio_backend():
    return "asyncio"                                                                        # set anyio to use asyncio backend (other variants are trio, etc.)


@pytest.fixture(scope="session")
def test_engine():                                                                          # this creates and returns test database engine
    engine = create_async_engine(
        os.environ["DATABASE_URL"],
        poolclass=NullPool,                                      # disables connection pooling. without it they can cause issues between tests, like "Connection already closed", etc.
    )
    return engine


@pytest.fixture(scope="session")
async def setup_database(test_engine):                                                      # at the start of session this creates all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)                                       # async is needed coz create_all is a sync func

    yield                                                                                   # here all tests run

    async with test_engine.begin() as conn:                                                 # when tests are done this runs and drops tables
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()                                                             # and disposes of the engine to clean up connection resourses


# Transaction rollback pattern. Industry standart approach for fast test isolation.
# We create all of our tables once (setup_database), then each test runs inside a database transaction
# After each test completes, rollback that transaction which instantly undoes everything the test did
# then at the end of session we drop all tables (setup_database)
@pytest.fixture                                                                             # this fixture runs for each test(default)
async def db_session(
    test_engine,
    setup_database,
) -> AsyncGenerator[AsyncSession]:
    conn = await test_engine.connect()                                                      # manually create a connection
    trans = await conn.begin()                                                              # then begin a transaction

    test_async_session = async_sessionmaker(                                                # create a session that is bound to this specific connection, not to the engine -
        bind=conn,                                                                          # this means that all operations that test performs will go through this one -
        class_=AsyncSession,                                                                # connection and this one transaction
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",                                           # all of this works coz of this line. this is fake commit magic. When app calls -
    )                                                                                       # session.commit(), sqlalchemy intercepts that call and instead of doing real commit it -
                                                                                            # creates a savepoint, so data looks commited but nothing was commited to db -
                                                                                            # thats why we can rollback everything at the end, coz real transaction was never commited

    async with test_async_session() as session:                                             # opens up session from async_sessionmaker
        try:
            yield session                                                                   # then yield it here to that test. This is the session that test recieves
        finally:
            await session.close()                                                           # after test is done we close the session
            await trans.rollback()                                                          # explicitly rollback the transaction which undoes everything test did. important to not leak data
            await conn.close()                                                              # close the connection


@pytest.fixture
async def client(
    db_session: AsyncSession,
) -> AsyncGenerator[AsyncClient]:
    
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db                                      # dependency_overrides is a dict that lets swap out of any depends func for testing

    async with AsyncClient(
        transport=ASGITransport(app=app),                                                   # makes async client send requests directly in-memory without touching network (for speed). Also ASGITransport doesnt run startup and shutdown code
        base_url="http://test",                                                             # this is required (even tho we dont make network calls, name doesn't matter)
    ) as ac:
        yield ac

    app.dependency_overrides.clear()                                                        # after test is done we clear dependency_overrides so they dont leak between tests


# Auth helpers
async def create_test_user(
    client: AsyncClient,
    username: str = "testuser",
    email: str = "test@example.com",
    password: str = "testpass",
) -> dict:
    responce = await client.post(
        "/api/users",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    assert responce.status_code == 201, f"Failed to create user: {responce.text}"           # code after comma is a message for error that assert raises on failure
    return responce.json()


async def login_user(
    client: AsyncClient,
    email: str = "test@example.com",
    password: str = "testpass",
) -> str:
    response = await client.post(
        "/api/users/token",
        data={                                                                              # we use data and not json coz OAuth2 password request form expects form data
            "username": email,
            "password": password,
        },
    )
    assert response.status_code == 200, f"Failed to login: {response.text}"
    return response.json()["access_token"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization":  f"Bearer {token}"}                                            # creates authorization header dictionary that can be passed to request