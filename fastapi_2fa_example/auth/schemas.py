from datetime import datetime
from enum import StrEnum
from typing import Self

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    SecretStr,
    field_serializer,
    model_validator,
)


class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: SecretStr = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=2, max_length=50)
    surname: str = Field(..., min_length=2, max_length=50)
    requires_2fa: bool = Field(
        default=False, description="Enable two-factor authentication"
    )

    @field_serializer("password", when_used="json")
    def dump_secret(self, v: SecretStr) -> str:
        return v.get_secret_value()


class RegisterResponse(BaseModel):
    requires_2fa: bool = Field(default=False, description="Whether 2FA is required")
    email: EmailStr = Field(..., description="User email")


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email")
    password: SecretStr = Field(..., min_length=8, max_length=128)

    @field_serializer("password", when_used="json")
    def dump_secret(self, v: SecretStr) -> str:
        return v.get_secret_value()


class LoginResponse(BaseModel):
    requires_2fa: bool = Field(default=False, description="Whether 2FA is required")
    tmp_token: str | None = Field(
        default=None, description="Temporary token if 2FA is enabled"
    )
    access_token: str | None = Field(
        default=None, description="Access token if 2FA is not enabled"
    )

    @model_validator(mode="after")
    def verify_tokens(self) -> Self:
        if self.requires_2fa and self.tmp_token is None:
            raise ValueError("tmp_token must be provided if 2FA is required")
        if self.requires_2fa and self.access_token is not None:
            raise ValueError("access_token must not be provided if 2FA is required")
        if not self.requires_2fa and self.access_token is None:
            raise ValueError("access_token must be provided if 2FA is not required")
        return self


class TwoFARequest(BaseModel):
    tmp_token: str = Field(..., description="Temporary token from login")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP code")


class TwoFAResponse(BaseModel):
    access_token: str = Field(
        ..., description="Access token after successful 2FA verification"
    )


class TokenType(StrEnum):
    ACCESS = "access"
    LOGIN = "login"


class Token(BaseModel):
    user_id: int = Field(..., description="User ID")
    exp: datetime = Field(..., description="Expiration time")
    type: TokenType = Field(..., description="Token type")


class OTP(BaseModel):
    user_id: int = Field(..., description="User ID")
    otp: str = Field(..., min_length=6, max_length=6)
