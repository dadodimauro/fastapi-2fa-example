import asyncio

from fastapi_2fa_example.logger import logger


async def send_email(to_email: str, subject: str, body: str) -> None:
    """Mock email sender function"""
    logger.warning(
        f"Sending email to {to_email} with subject '{subject}' and body: {body}"
    )
    await asyncio.sleep(1)
    logger.info(f"Email sent to {to_email}")
    return
