import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from .db_models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")


# Async engine with connection pooling
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,       # Test connections before using them
    pool_size=10,             # Max persistent connections in pool
    max_overflow=20,          # Extra connections allowed beyond pool_size under heavy load
    pool_timeout=30,          # Seconds to wait for a connection before raising error
    pool_recycle=1800,        # Recycle connections after 30 min (prevents stale connections)
)

# Async session
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create tables (async)
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

#  Clean shutdown — call this in lifespan
async def close_db():
    await engine.dispose()
    print("Database connection pool closed")

# Dependency
async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        except Exception:
            await db.rollback()  # Rollback on any unhandled exception
            raise
        finally:
            await db.close()