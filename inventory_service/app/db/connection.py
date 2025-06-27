import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .models import Base
from ..monitoring import db_connection_errors_counter, resource

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    db_connection_errors_counter.add(1, {"service": resource.attributes.get("service.name", "unknown")})
    raise ValueError("DATABASE_URL environment variable not set")

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def create_tables():
    """Create tables in the database if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db() -> AsyncSession:
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except Exception as e:
        db_connection_errors_counter.add(1, {"service": resource.attributes.get("service.name", "unknown")})
        raise 