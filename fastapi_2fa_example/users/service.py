from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi_2fa_example.models import User as UserModel

from .schemas import UserCreate


class UserService:
    async def get_by_email(self, session: AsyncSession, email: str) -> UserModel | None:
        result = await session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        return result.scalars().first()

    async def add(self, session: AsyncSession, user_create: UserCreate) -> UserModel:
        user = UserModel(
            email=user_create.email,
            password_hash=user_create.password_hash,
            name=user_create.name,
            surname=user_create.surname,
            requires_2fa=user_create.requires_2fa,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    async def get_all(self, session: AsyncSession) -> Sequence[UserModel]:
        result = await session.execute(select(UserModel))
        return result.scalars().all()

    async def get(self, session: AsyncSession, user_id: int) -> UserModel | None:
        return await session.get(UserModel, user_id)


user_service = UserService()
