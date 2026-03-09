from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from .db_models import Base

DATABASE_URL = "sqlite:///./matches.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)


def create_tables():
    Base.metadata.create_all(engine)


def get_db():
    with Session(engine) as session:
        yield session



