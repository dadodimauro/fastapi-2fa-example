import secrets
from datetime import UTC, datetime, timedelta

import jwt
from passlib.hash import sha256_crypt
from pydantic import ValidationError

from fastapi_2fa_example.config import settings
from fastapi_2fa_example.logger import logger

from .schemas import Token, TokenType


def hash_password(password: str) -> str:
    return sha256_crypt.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return sha256_crypt.verify(password, password_hash)


def create_jwt_token(user_id: int, type: TokenType, exp: int | None = None) -> str:
    """
    Create a new JWT token for a user.

    Args:
        user_id (int): The ID of the user.
        type (TokenType): The type of token to create (access or login).
        exp (int | None): The expiration time in minutes. If None, defaults to settings.

    Returns:
        str: The encoded JWT one-time token.
    """

    if exp is None:
        if type == TokenType.ACCESS:
            exp = settings.ACCESS_TOKEN_EXPIRE_MINUTES
        elif type == TokenType.LOGIN:
            exp = settings.LOGIN_TOKEN_EXPIRE_MINUTES
        else:
            raise ValueError("Invalid token type")

    token = Token(
        user_id=user_id,
        exp=datetime.now(tz=UTC) + timedelta(minutes=exp),
        type=type,
    )
    return jwt.encode(  # type: ignore
        payload=token.model_dump(),
        key=settings.JWT_SECRET.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_token(token_str: str) -> Token:
    """
    Decode and validate a JWT token.

    Args:
        token_str (str): The encoded JWT token.

    Returns:
        Token: The decoded JWT token.
    """
    try:
        payload: str = jwt.decode(  # type: ignore
            jwt=token_str,
            key=settings.JWT_SECRET.get_secret_value(),
            algorithms=[settings.JWT_ALGORITHM],
        )
        return Token.model_validate(payload)

    except jwt.ExpiredSignatureError as e:
        logger.exception("Token has expired")
        raise ValueError("Token has expired") from e
    except jwt.PyJWKError as e:
        logger.exception("Invalid token")
        raise ValueError("Invalid token") from e
    except ValidationError as e:
        logger.exception("Invalid token payload")
        raise ValueError("Invalid token payload") from e
    except Exception as e:
        logger.exception("Failed to decode token")
        raise ValueError("Failed to decode token") from e


def generate_otp() -> str:
    """Generate a random 6-digit OTP code."""

    return "".join(str(secrets.randbelow(10)) for _ in range(6))
