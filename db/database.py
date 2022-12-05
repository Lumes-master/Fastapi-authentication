from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from settings import settings

engine = create_engine(settings.database_url, future=True)

Session = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True
)


Base = declarative_base()


def get_db():
    session = Session()
    try:
        yield session
    finally:
        session.close()
