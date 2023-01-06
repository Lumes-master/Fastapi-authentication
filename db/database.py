from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from settings import settings

engine = create_engine(settings.database_url, future=True)
async_engine = create_async_engine(settings.async_database_url, echo=True)
Session = sessionmaker(bind=engine, autoflush=False, autocommit=False,
    future=True)

Async_session = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    )


Base = declarative_base()



async def async_get_db():
    async with Async_session() as db:
        yield db


