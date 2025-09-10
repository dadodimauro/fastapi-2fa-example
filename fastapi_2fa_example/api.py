from fastapi import APIRouter

from fastapi_2fa_example.auth.router import router as auth_router
from fastapi_2fa_example.users.router import router as users_router

router = APIRouter(prefix="/api/v1")
router.include_router(auth_router)
router.include_router(users_router)
