import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from fastapi_2fa_example.auth.dependencies import TokenValidator
from fastapi_2fa_example.auth.schemas import Token, TokenType
from fastapi_2fa_example.auth.utils import create_jwt_token


def test_token_validator_valid():
    user_id = 1
    token_type = TokenType.ACCESS
    token_str = create_jwt_token(user_id, token_type)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_str)
    validator = TokenValidator(TokenType.ACCESS)
    token = validator(credentials)
    assert isinstance(token, Token)
    assert token.user_id == user_id
    assert token.type == token_type


def test_token_validator_invalid_type():
    user_id = 1
    token_str = create_jwt_token(user_id, TokenType.LOGIN)
    credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_str)
    validator = TokenValidator(TokenType.ACCESS)
    with pytest.raises(HTTPException) as exc:
        validator(credentials)
    assert exc.value.status_code == 401
    assert "Invalid or expired token" in exc.value.detail


def test_token_validator_invalid_token():
    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials="invalid_token"
    )
    validator = TokenValidator(TokenType.ACCESS)
    with pytest.raises(HTTPException) as exc:
        validator(credentials)
    assert exc.value.status_code == 401
    assert "Invalid or expired token" in exc.value.detail
