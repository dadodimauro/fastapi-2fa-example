import pytest
from fastapi import status
from httpx import AsyncClient

from fastapi_2fa_example.auth.schemas import TokenType
from fastapi_2fa_example.auth.utils import create_jwt_token
from fastapi_2fa_example.models.user import User
from tests.fixtures.database import SaveFixture
from tests.fixtures.random_objects import create_user


@pytest.mark.asyncio
class TestGet:
    @pytest.mark.auth
    async def test_get_user(self, client: AsyncClient, random_user: User) -> None:
        response = await client.get(
            "/api/v1/users/me",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["id"] == random_user.id

    async def test_get_user_unauthenticated(self, client: AsyncClient) -> None:
        response = await client.get(
            "/api/v1/users/me",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_user_not_found(self, client: AsyncClient) -> None:
        token_str = create_jwt_token(user_id=9999, type=TokenType.ACCESS, exp=10)
        headers = {"Authorization": f"Bearer {token_str}"}
        response = await client.get(
            "/api/v1/users/me",
            headers=headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_get_user_invalid_token(self, client: AsyncClient) -> None:
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get(
            "/api/v1/users/me",
            headers=headers,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
class TestGetAll:
    @pytest.mark.auth
    async def test_get_all_users(
        self, client: AsyncClient, save_fixture: SaveFixture
    ) -> None:
        await create_user(save_fixture)

        response = await client.get(
            "/api/v1/users",
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 2  # 1 from token fixture + 1 created here

    async def test_get_all_users_unauthenticated(self, client: AsyncClient) -> None:
        response = await client.get(
            "/api/v1/users",
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    async def test_get_all_users_invalid_token(self, client: AsyncClient) -> None:
        headers = {"Authorization": "Bearer invalid_token"}
        response = await client.get(
            "/api/v1/users",
            headers=headers,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
