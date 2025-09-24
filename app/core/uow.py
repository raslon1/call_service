from abc import ABC, abstractmethod
from typing import AsyncContextManager
from app.repositories.call import CallRepository, RecordingRepository
from app.database import AsyncSessionLocal


class UnitOfWork(ABC):
    call_repo: CallRepository
    recording_repo: RecordingRepository

    @abstractmethod
    async def __aenter__(self) -> "UnitOfWork":
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    async def commit(self):
        pass

    @abstractmethod
    async def rollback(self):
        pass


class SQLAlchemyUnitOfWork(UnitOfWork):
    def __init__(self):
        self.session = None

    async def __aenter__(self) -> "SQLAlchemyUnitOfWork":
        self.session = AsyncSessionLocal()
        self.call_repo = CallRepository(self.session)
        self.recording_repo = RecordingRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            await self.rollback()
        else:
            await self.commit()
        if self.session:
            await self.session.close()

    async def commit(self):
        if self.session:
            await self.session.commit()

    async def rollback(self):
        if self.session:
            await self.session.rollback()