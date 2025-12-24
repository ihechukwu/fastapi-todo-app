from sqlmodel import create_engine, SQLModel
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .config import settings

engine = AsyncEngine(create_engine(url=settings.DATABASE_URL))

"""
it is not needed since I am using alembic

 async def init_db():
    async with engine.begin() as conn:
         await conn.run_sync(SQLModel.metadata.create_all)

"""


async def get_session():
    Session = sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        yield session
