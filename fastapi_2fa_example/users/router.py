from collections.abc import Sequence

from fastapi import APIRouter, Depends, HTTPException, status

from fastapi_2fa_example.auth.dependencies import validate_access_token
from fastapi_2fa_example.auth.schemas import Token
from fastapi_2fa_example.models import User as UserModel
from fastapi_2fa_example.postgres import AsyncSession, get_db_session

from .schemas import User
from .service import user_service

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "", response_model=list[User], dependencies=[Depends(validate_access_token)]
)
async def get_users(
    session: AsyncSession = Depends(get_db_session),
) -> Sequence[UserModel]:
    return await user_service.get_all(session=session)


@router.get("/me", response_model=User)
async def get_me(
    token: Token = Depends(validate_access_token),
    session: AsyncSession = Depends(get_db_session),
) -> UserModel:
    user = await user_service.get(session=session, user_id=token.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
