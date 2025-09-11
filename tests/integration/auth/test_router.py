from unittest.mock import AsyncMock

import pytest
from fastapi import status
from httpx import AsyncClient
from pydantic import SecretStr

from fastapi_2fa_example.auth.schemas import LoginRequest, RegisterRequest, TwoFARequest
from fastapi_2fa_example.auth.service import otp_service
from fastapi_2fa_example.models.user import User
from fastapi_2fa_example.redis import Redis


@pytest.mark.asyncio
class TestRegister:
    async def test_register(self, client: AsyncClient) -> None:
        register_request = RegisterRequest(
            email="test@example.com",
            password=SecretStr("password"),
            name="test",
            surname="test",
            requires_2fa=False,
        )
        response = await client.post(
            "/api/v1/auth/register", json=register_request.model_dump(mode="json")
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json().get("email") == register_request.email

    async def test_register_duplicated(
        self, client: AsyncClient, random_user: User
    ) -> None:
        register_request = RegisterRequest(
            email=random_user.email,
            password=SecretStr("password"),
            name=random_user.name,
            surname=random_user.surname,
            requires_2fa=random_user.requires_2fa,
        )
        response = await client.post(
            "/api/v1/auth/register", json=register_request.model_dump(mode="json")
        )
        assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
class TestLogin:
    async def test_login(
        self, client: AsyncClient, mock_send_email: AsyncMock, random_user: User
    ) -> None:
        login_request = LoginRequest(
            email=random_user.email,
            password=SecretStr("password"),
        )
        response = await client.post(
            "/api/v1/auth/login", json=login_request.model_dump(mode="json")
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("requires_2fa") is False
        assert response.json().get("tmp_token") is None
        assert response.json().get("access_token") is not None

        assert mock_send_email.call_count == 0  # no email should be sent

    async def test_wrong_password(
        self, client: AsyncClient, mock_send_email: AsyncMock, random_user: User
    ) -> None:
        login_request = LoginRequest(
            email=random_user.email,
            password=SecretStr("wrong_password"),
        )
        response = await client.post(
            "/api/v1/auth/login", json=login_request.model_dump(mode="json")
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        assert mock_send_email.call_count == 0  # no email should be sent

    async def test_invalid_email(
        self, client: AsyncClient, mock_send_email: AsyncMock, random_user: User
    ) -> None:
        login_request = LoginRequest(
            email="invalid@example.com",
            password=SecretStr("wrong_password"),
        )
        response = await client.post(
            "/api/v1/auth/login", json=login_request.model_dump(mode="json")
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        assert mock_send_email.call_count == 0  # no email should be sent

    async def test_login_2fa(
        self, client: AsyncClient, mock_send_email: AsyncMock, random_2fa_user: User
    ) -> None:
        login_request = LoginRequest(
            email=random_2fa_user.email,
            password=SecretStr("password"),
        )
        response = await client.post(
            "/api/v1/auth/login", json=login_request.model_dump(mode="json")
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("requires_2fa") is True
        assert response.json().get("tmp_token") is not None
        assert response.json().get("access_token") is None

        assert mock_send_email.call_count == 1  # email should be sent
        assert mock_send_email.call_args[1]["to_email"] == random_2fa_user.email
        assert mock_send_email.call_args[1]["subject"] == "Your OTP Code"
        assert mock_send_email.call_args[1]["body"].split(": ")[1].isdigit()  # OTP code


@pytest.mark.asyncio
class TestVerify2FA:
    async def test_verify_2fa(
        self, client: AsyncClient, redis: Redis, random_2fa_user: User
    ) -> None:
        login_request = LoginRequest(
            email=random_2fa_user.email,
            password=SecretStr("password"),
        )
        response = await client.post(
            "/api/v1/auth/login", json=login_request.model_dump(mode="json")
        )
        tmp_token = response.json().get("tmp_token")
        assert tmp_token is not None

        # get OTP
        # TODO: check if this can be done in a cleaner way
        otp = await otp_service.get_by_user_id(redis=redis, user_id=random_2fa_user.id)
        assert otp is not None

        two_fa_request = TwoFARequest(tmp_token=tmp_token, otp=otp.otp)

        response = await client.post(
            "/api/v1/auth/verify-2fa", json=two_fa_request.model_dump(mode="json")
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json().get("access_token") is not None

    async def test_verify_2fa_wrong_token(
        self, client: AsyncClient, redis: Redis, random_2fa_user: User
    ) -> None:
        login_request = LoginRequest(
            email=random_2fa_user.email,
            password=SecretStr("password"),
        )
        response = await client.post(
            "/api/v1/auth/login", json=login_request.model_dump(mode="json")
        )
        assert response.status_code == status.HTTP_200_OK
        tmp_token = "wrong_token"

        # get OTP
        # TODO: check if this can be done in a cleaner way
        otp = await otp_service.get_by_user_id(redis=redis, user_id=random_2fa_user.id)
        assert otp is not None

        two_fa_request = TwoFARequest(tmp_token=tmp_token, otp=otp.otp)

        response = await client.post(
            "/api/v1/auth/verify-2fa", json=two_fa_request.model_dump(mode="json")
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_verify_2fa_wrong_otp(
        self, client: AsyncClient, redis: Redis, random_2fa_user: User
    ) -> None:
        login_request = LoginRequest(
            email=random_2fa_user.email,
            password=SecretStr("password"),
        )
        response = await client.post(
            "/api/v1/auth/login", json=login_request.model_dump(mode="json")
        )
        tmp_token = response.json().get("tmp_token")
        assert tmp_token is not None

        # get OTP
        # TODO: check if this can be done in a cleaner way
        otp = await otp_service.get_by_user_id(redis=redis, user_id=random_2fa_user.id)
        assert otp is not None
        otp.otp = str(int(otp.otp) + 1).zfill(len(otp.otp))  # wrong OTP

        two_fa_request = TwoFARequest(tmp_token=tmp_token, otp=otp.otp)

        response = await client.post(
            "/api/v1/auth/verify-2fa", json=two_fa_request.model_dump(mode="json")
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
