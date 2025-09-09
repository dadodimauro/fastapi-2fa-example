from pydantic import BaseModel, EmailStr, Field, SecretStr


class UserCreate(BaseModel):
    email: EmailStr
    password: SecretStr
    name: str = Field(..., min_length=2, max_length=50)
    surname: str = Field(..., min_length=2, max_length=50)
    enable_2fa: bool = Field(
        default=False, description="Enable two-factor authentication"
    )


class User(UserCreate):
    id: int
