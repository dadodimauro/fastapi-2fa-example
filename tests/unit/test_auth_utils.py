from datetime import UTC, datetime, timedelta

import jwt
import pytest

from fastapi_2fa_example.auth import utils
from fastapi_2fa_example.auth.schemas import Token, TokenType
from fastapi_2fa_example.config import settings


def test_hash_and_verify_password():
    password = "mysecretpassword"
    hashed = utils.hash_password(password)
    assert hashed != password
    assert utils.verify_password(password, hashed)
    assert not utils.verify_password("wrongpassword", hashed)


def test_create_and_decode_jwt_token():
    user_id = 123
    token_type = TokenType.ACCESS
    token_str = utils.create_jwt_token(user_id=user_id, type=token_type, exp=1)
    assert isinstance(token_str, str)
    token = utils.decode_token(token_str=token_str)
    assert isinstance(token, Token)
    assert token.user_id == user_id
    assert token.type == token_type


def test_create_jwt_token_invalid_type():
    with pytest.raises(ValueError):
        utils.create_jwt_token(1, "invalid_type")  # type: ignore


def test_decode_token_expired():
    token = Token(
        user_id=1,
        exp=datetime.now(tz=UTC) - timedelta(minutes=1),
        type=TokenType.ACCESS,
    )
    token_str = jwt.encode(  # type: ignore
        payload=token.model_dump(),
        key=settings.JWT_SECRET.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )
    with pytest.raises(ValueError, match="Token has expired"):
        utils.decode_token(token_str)


def test_decode_token_invalid_signature():
    token = Token(
        user_id=1,
        exp=datetime.now(tz=UTC) + timedelta(minutes=10),
        type=TokenType.ACCESS,
    )
    token_str = jwt.encode(  # type: ignore
        payload=token.model_dump(),
        key="wrongsecret",
        algorithm=settings.JWT_ALGORITHM,
    )
    with pytest.raises(Exception, match="Failed to decode token"):
        utils.decode_token(token_str)


def test_decode_token_invalid_type():
    token = {  # type: ignore
        "user_id": 1,
        "exp": datetime.now(tz=UTC) + timedelta(minutes=10),
        "type": "invalid_type",
    }
    token_str = jwt.encode(  # type: ignore
        payload=token,  # type: ignore
        key=settings.JWT_SECRET.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )
    with pytest.raises(ValueError, match="Invalid token payload"):
        utils.decode_token(token_str)


def test_generate_otp():
    otp = utils.generate_otp()
    assert isinstance(otp, str)
    assert len(otp) == 6
    assert otp.isdigit()
