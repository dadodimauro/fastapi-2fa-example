import pytest

from fastapi_2fa_example.auth.utils import hash_password
from fastapi_2fa_example.postgres import AsyncSession
from fastapi_2fa_example.users.schemas import UserCreate
from fastapi_2fa_example.users.service import user_service
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_user


@pytest.mark.asyncio
class TestGet:
    async def test_get(self, session: AsyncSession, save_fixture: SaveFixture) -> None:
        user = await create_user(save_fixture)
        user_fetched = await user_service.get(session, user.id)
        assert user_fetched is not None
        assert user_fetched == user

    async def test_get_not_found(self, session: AsyncSession) -> None:
        user_fetched = await user_service.get(session, 9999)
        assert user_fetched is None


@pytest.mark.asyncio
class TestGetByEmail:
    async def test_get_by_email(
        self, session: AsyncSession, save_fixture: SaveFixture
    ) -> None:
        user = await create_user(save_fixture)
        user_fetched = await user_service.get_by_email(session, user.email)
        assert user_fetched is not None
        assert user_fetched == user

    async def test_get_by_email_not_found(self, session: AsyncSession) -> None:
        user_fetched = await user_service.get_by_email(session, "notfound@example.com")
        assert user_fetched is None


@pytest.mark.asyncio
class TestGetAll:
    async def test_get_all(
        self, session: AsyncSession, save_fixture: SaveFixture
    ) -> None:
        users = [await create_user(save_fixture) for _ in range(3)]
        users_fetched = await user_service.get_all(session)
        assert len(users_fetched) == len(users)
        assert all(user in users_fetched for user in users)

    async def test_get_all_empty(self, session: AsyncSession) -> None:
        users_fetched = await user_service.get_all(session)
        assert users_fetched == []


@pytest.mark.asyncio
class TestAdd:
    async def test_add(self, session: AsyncSession) -> None:
        user_create = UserCreate(
            email="test@example.com",
            password_hash=hash_password("password"),
            name="name",
            surname="surname",
            requires_2fa=False,
        )
        user = await user_service.add(session, user_create)
        assert user is not None

        user_fetched = await user_service.get(session, user.id)
        assert user_fetched is not None
        assert user_fetched == user
