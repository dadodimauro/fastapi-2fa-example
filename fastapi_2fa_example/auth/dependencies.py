from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from fastapi_2fa_example.logger import logger

from .schemas import Token, TokenType
from .utils import decode_token

bearer_scheme = HTTPBearer()


class TokenValidator:
    def __init__(self, token_type: TokenType):
        self.token_type = token_type

    def __call__(
        self,
        token: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
    ) -> Token:
        try:
            decoded_token = decode_token(token.credentials)
            if decoded_token.type != self.token_type:
                raise ValueError(
                    f"Invalid token type: expected {self.token_type}, got {decoded_token.type}"
                )
            return decoded_token
        except Exception:
            logger.exception("Token validation failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            )


validate_access_token = TokenValidator(TokenType.ACCESS)
