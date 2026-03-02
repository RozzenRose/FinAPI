from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(settings.database_url)

session_factory = async_sessionmaker(engine)

class Base(DeclarativeBase):
    pass