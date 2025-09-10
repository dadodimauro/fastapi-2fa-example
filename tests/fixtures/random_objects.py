import random
import string

import pytest_asyncio

from fastapi_2fa_example.auth.schemas import OTP
from fastapi_2fa_example.auth.utils import generate_otp, hash_password
from fastapi_2fa_example.models import User
from fastapi_2fa_example.redis import Redis
from tests.fixtures.database import SaveFixture


def rstr(prefix: str) -> str:
    return prefix + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))


def lstr(suffix: str) -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=6)) + suffix


async def create_user(
    save_fixture: SaveFixture,
    name_prefix: str = "user",
    requires_2fa: bool = False,
    password: str = "password",
) -> User:
    user = User(
        email=rstr(name_prefix) + "@example.com",
        name=rstr(name_prefix),
        surname=rstr(name_prefix),
        password_hash=hash_password(password),
        requires_2fa=requires_2fa,
    )
    await save_fixture(user)
    return user


@pytest_asyncio.fixture
async def random_user(save_fixture: SaveFixture) -> User:
    return await create_user(save_fixture)


@pytest_asyncio.fixture
async def random_2fa_user(save_fixture: SaveFixture) -> User:
    return await create_user(save_fixture, requires_2fa=True)


async def create_otp(
    redis: Redis,
    random_2fa_user: User,
) -> OTP:
    otp = OTP(user_id=random_2fa_user.id, otp=generate_otp())
    key = f"otp:{otp.user_id}"
    await redis.set(name=key, value=otp.model_dump_json())
    return otp


@pytest_asyncio.fixture
async def random_otp(redis: Redis, random_2fa_user: User) -> OTP:
    return await create_otp(redis, random_2fa_user)
