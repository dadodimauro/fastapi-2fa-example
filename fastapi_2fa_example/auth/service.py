from fastapi_2fa_example.config import settings
from fastapi_2fa_example.redis import Redis

from .schemas import OTP


class OTPService:
    async def add(self, redis: Redis, otp: OTP) -> None:
        """Add a one-time password (OTP) to Redis.

        Args:
            redis (Redis): The Redis client.
            otp (OTP): The OTP data to store.
        """
        key = f"otp:{otp.user_id}"
        await redis.set(
            name=key, value=otp.model_dump_json(), ex=settings.OTP_EXPIRE_MINUTES * 60
        )

    async def get_by_user_id(self, redis: Redis, user_id: int) -> OTP | None:
        """Retrieve an OTP by user ID from Redis.

        Args:
            redis (Redis): The Redis client.
            user_id (int): The user ID associated with the OTP.

        Returns:
            OTP | None: The retrieved OTP data or None if not found.
        """
        key = f"otp:{user_id}"
        otp_data = await redis.get(key)
        if otp_data:
            return OTP.model_validate_json(otp_data)
        return None

    async def delete(self, redis: Redis, user_id: int) -> None:
        """Delete an OTP by user ID from Redis.

        Args:
            redis (Redis): The Redis client.
            user_id (int): The user ID associated with the OTP to delete.
        """
        key = f"otp:{user_id}"
        await redis.delete(key)


otp_service = OTPService()
