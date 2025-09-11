from fastapi import APIRouter, Depends, HTTPException, status

from fastapi_2fa_example.logger import logger
from fastapi_2fa_example.mail_sender import send_email
from fastapi_2fa_example.postgres import AsyncSession, get_db_session
from fastapi_2fa_example.redis import (
    RedisAsyncConnectionPool,
    get_redis_client_from_pool,
    get_redis_pool,
)
from fastapi_2fa_example.users.schemas import UserCreate
from fastapi_2fa_example.users.service import user_service

from .schemas import (
    OTP,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
    TokenType,
    TwoFARequest,
    TwoFAResponse,
)
from .service import otp_service
from .utils import (
    create_jwt_token,
    decode_token,
    generate_otp,
    hash_password,
    verify_password,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Register a new user with email and password (Optionally enable 2FA).",
    responses={status.HTTP_409_CONFLICT: {"description": "User already exists"}},
)
async def register(
    register_request: RegisterRequest, session: AsyncSession = Depends(get_db_session)
) -> RegisterResponse:
    if await user_service.get_by_email(session, register_request.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
        )

    user_create = UserCreate(
        email=register_request.email,
        password_hash=hash_password(register_request.password.get_secret_value()),
        name=register_request.name,
        surname=register_request.surname,
        requires_2fa=register_request.requires_2fa,
    )
    user = await user_service.add(session, user_create)

    return RegisterResponse(requires_2fa=user.requires_2fa, email=user.email)


@router.post(
    "/login",
    summary="User login",
    description="Authenticate user and initiate 2FA if enabled.",
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"}},
)
async def login(
    login_request: LoginRequest,
    session: AsyncSession = Depends(get_db_session),
    redis_pool: RedisAsyncConnectionPool = Depends(get_redis_pool),
) -> LoginResponse:
    user = await user_service.get_by_email(session=session, email=login_request.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email",
        )
    if not verify_password(
        password=login_request.password.get_secret_value(),
        password_hash=user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )
    if user.requires_2fa:
        otp = generate_otp()
        async with get_redis_client_from_pool(redis_pool) as redis:
            await otp_service.add(
                redis=redis,
                otp=OTP(
                    user_id=user.id,
                    otp=otp,
                ),
            )

        # send email
        try:
            await send_email(
                to_email=user.email,
                subject="Your OTP Code",
                body=f"Your OTP code is: {otp}",
            )
        except Exception as e:  # pragma: no cover
            logger.exception(f"Failed to send email: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send OTP email",
            )

        tmp_token = create_jwt_token(
            user_id=user.id,
            type=TokenType.LOGIN,
        )
        return LoginResponse(requires_2fa=True, tmp_token=tmp_token, access_token=None)
    else:
        access_token = create_jwt_token(user_id=user.id, type=TokenType.ACCESS)
        return LoginResponse(
            requires_2fa=False, tmp_token=None, access_token=access_token
        )


@router.post(
    "/verify-2fa",
    summary="Verify 2FA OTP",
    description="Verify the OTP for 2FA login.",
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid token type"},
    },
)
async def verify_2fa(
    two_fa_request: TwoFARequest,
    redis_pool: RedisAsyncConnectionPool = Depends(get_redis_pool),
) -> TwoFAResponse:
    try:
        payload = decode_token(two_fa_request.tmp_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    if payload.type != TokenType.LOGIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token type",
        )

    async with get_redis_client_from_pool(redis_pool) as redis:
        otp = await otp_service.get_by_user_id(redis=redis, user_id=payload.user_id)

        if otp is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="OTP expired or not found",
            )
        if otp.otp != two_fa_request.otp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid OTP",
            )

        await otp_service.delete(redis=redis, user_id=payload.user_id)

    access_token = create_jwt_token(user_id=payload.user_id, type=TokenType.ACCESS)
    return TwoFAResponse(access_token=access_token)
