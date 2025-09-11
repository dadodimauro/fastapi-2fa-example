from datetime import datetime

import pytest_asyncio

from fastapi_2fa_example.auth.schemas import Token, TokenType
from fastapi_2fa_example.models.user import User


@pytest_asyncio.fixture
async def access_token_fixture(random_user: User) -> Token:
    """Fixture that returns a non-expiring access Token for a random user."""
    return Token(
        user_id=random_user.id,
        type=TokenType.ACCESS,
        exp=datetime.max,
    )
