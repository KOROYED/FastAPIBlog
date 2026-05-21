from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./blog.db"

engine = create_engine(                                                                         # engine = connection to the database
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},                                                  # this one is sqlite specific coz it normally supports only 1 thread
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)                     # Factory that creates a database session. session is a transaction with db
                                                                                                #  each request gets its own session

class Base(DeclarativeBase):
    pass


def get_db():                                                                                   # dependency func that provides sessions to routes
    with SessionLocal() as db:
        yield db