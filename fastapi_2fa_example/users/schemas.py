from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=50)
    surname: str = Field(..., min_length=2, max_length=50)
    requires_2fa: bool = Field(
        default=False, description="Enable two-factor authentication"
    )


class UserCreate(UserBase):
    password_hash: str


class User(UserBase):
    id: int
