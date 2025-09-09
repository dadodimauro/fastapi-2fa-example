from fastapi import APIRouter, Depends, status

from fastapi_2fa_example.postgres import AsyncSession, get_db_session

from .schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    TwoFARequest,
    TwoFAResponse,
)

router = APIRouter(
    prefix="",
    tags=["auth"],
)


@router.post(
    "/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    register_request: RegisterRequest, session: AsyncSession = Depends(get_db_session)
) -> RegisterResponse: ...


@router.post("/login", response_model=LoginResponse)
async def login(
    login_request: LoginRequest, session: AsyncSession = Depends(get_db_session)
) -> LoginResponse: ...


@router.post("/2fa", response_model=TwoFAResponse)
async def verify_2fa(
    two_fa_request: TwoFARequest, session: AsyncSession = Depends(get_db_session)
) -> TwoFAResponse: ...
