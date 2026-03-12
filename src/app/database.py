from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session

from .db_models import Base

DATABASE_URL = "sqlite:///./matches.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True,
)

# Enable foreign key constraints for SQLite
@event.listens_for(Engine, "connect")
def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_tables():
    Base.metadata.create_all(engine)


def get_db():
    with Session(engine) as session:
        yield session



