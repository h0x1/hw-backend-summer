from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.store.database.sqlalchemy_base import db
from typing import Optional

class Database:
    def __init__(self, app: "Application"):
        self.app = app
        self._engine: Optional[AsyncEngine] = None
        self._db: Optional[declarative_base] = None
        self.session: Optional[AsyncSession] = None

    async def connect(self, *_: list, **__: dict) -> None:
        self._db = db
        self._engine = create_async_engine(
            f"postgresql+asyncpg://{self.app.config.database.user}:{self.app.config.database.password}"
            f"@{self.app.config.database.host}/{self.app.config.database.database}",
            echo=True,
            future=True
        )
        self.session = sessionmaker(
            self._engine,
            expire_on_commit=False,
            class_=AsyncSession
        )

    async def disconnect(self, *_: list, **__: dict) -> None:
        try:
            await self._engine.dispose()
        except Exception:
            pass
