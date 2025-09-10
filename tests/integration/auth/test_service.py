import pytest

from fastapi_2fa_example.auth.schemas import OTP
from fastapi_2fa_example.auth.service import otp_service
from fastapi_2fa_example.redis import Redis


@pytest.mark.asyncio
class TestGet:
    async def test_get(self, redis: Redis, random_otp: OTP) -> None:
        otp_fetched = await otp_service.get_by_user_id(
            redis=redis, user_id=random_otp.user_id
        )
        assert otp_fetched is not None
        assert otp_fetched.user_id == random_otp.user_id
        assert otp_fetched.otp == random_otp.otp

    async def test_get_not_found(self, redis: Redis) -> None:
        otp_fetched = await otp_service.get_by_user_id(redis=redis, user_id=123)
        assert otp_fetched is None


@pytest.mark.asyncio
class TestAdd:
    async def test_add(self, redis: Redis) -> None:
        otp = OTP(user_id=123, otp="654321")
        await otp_service.add(redis=redis, otp=otp)

        otp_fetched = await otp_service.get_by_user_id(redis=redis, user_id=otp.user_id)
        assert otp_fetched is not None
        assert otp_fetched.user_id == otp.user_id
        assert otp_fetched.otp == otp.otp

    async def test_add_same_user(self, redis: Redis) -> None:
        user_id = 123
        otp1 = OTP(user_id=user_id, otp="654321")
        otp2 = OTP(user_id=user_id, otp="785876")

        await otp_service.add(redis=redis, otp=otp1)
        await otp_service.add(redis=redis, otp=otp2)

        otp_fetched = await otp_service.get_by_user_id(redis=redis, user_id=user_id)

        assert otp_fetched is not None
        assert otp_fetched.user_id == otp2.user_id
        assert otp_fetched.otp == otp2.otp
        assert otp_fetched.otp != otp1.otp

    async def test_add_multiple_users(self, redis: Redis) -> None:
        otp1 = OTP(user_id=124, otp="654321")
        otp2 = OTP(user_id=125, otp="785876")

        await otp_service.add(redis=redis, otp=otp1)
        await otp_service.add(redis=redis, otp=otp2)

        otp_fetched_1 = await otp_service.get_by_user_id(
            redis=redis, user_id=otp1.user_id
        )
        otp_fetched_2 = await otp_service.get_by_user_id(
            redis=redis, user_id=otp2.user_id
        )

        assert otp_fetched_1 is not None
        assert otp_fetched_1.user_id == otp1.user_id
        assert otp_fetched_1.otp == otp1.otp

        assert otp_fetched_2 is not None
        assert otp_fetched_2.user_id == otp2.user_id
        assert otp_fetched_2.otp == otp2.otp


@pytest.mark.asyncio
class TestDelete:
    async def test_delete(self, redis: Redis, random_otp: OTP) -> None:
        otp_fetched = await otp_service.get_by_user_id(
            redis=redis, user_id=random_otp.user_id
        )
        assert otp_fetched is not None
        assert otp_fetched.user_id == random_otp.user_id
        assert otp_fetched.otp == random_otp.otp

        await otp_service.delete(redis=redis, user_id=random_otp.user_id)

        otp_fetched_after_delete = await otp_service.get_by_user_id(
            redis=redis, user_id=random_otp.user_id
        )
        assert otp_fetched_after_delete is None

    async def test_delete_empty(self, redis: Redis) -> None:
        otp_fetched = await otp_service.delete(redis=redis, user_id=123)
        assert otp_fetched is None

    async def test_delete_multi(self, redis: Redis, random_otp: OTP) -> None:
        otp_fetched = await otp_service.get_by_user_id(
            redis=redis, user_id=random_otp.user_id
        )
        assert otp_fetched is not None
        assert otp_fetched.user_id == random_otp.user_id
        assert otp_fetched.otp == random_otp.otp

        await otp_service.delete(redis=redis, user_id=random_otp.user_id)
        await otp_service.delete(redis=redis, user_id=random_otp.user_id)

        otp_fetched_after_delete = await otp_service.get_by_user_id(
            redis=redis, user_id=random_otp.user_id
        )
        assert otp_fetched_after_delete is None
