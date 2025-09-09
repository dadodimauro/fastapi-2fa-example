from pydantic import BaseModel, EmailStr, Field, SecretStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: SecretStr = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=2, max_length=50)
    surname: str = Field(..., min_length=2, max_length=50)
    enable_2fa: bool = Field(
        default=False, description="Enable two-factor authentication"
    )


class RegisterResponse(BaseModel):
    requires_2fa: bool = Field(default=False, description="Whether 2FA is required")
    login_token: str | None = Field(
        default=None, description="Login token if 2FA is enabled"
    )


class LoginRequest(BaseModel):
    email: EmailStr
    password: SecretStr = Field(..., min_length=8, max_length=128)


class LoginResponse(BaseModel):
    requires_2fa: bool = Field(default=False, description="Whether 2FA is required")
    login_token: str | None = Field(
        default=None, description="Login token if 2FA is enabled"
    )
    access_token: str | None = Field(
        default=None, description="Access token if 2FA is not enabled"
    )


class TwoFARequest(BaseModel):
    login_token: str = Field(..., description="Login token")
    otp: str = Field(..., min_length=6, max_length=6)


class TwoFAResponse(BaseModel):
    access_token: str = Field(
        ..., description="Access token after successful 2FA verification"
    )
