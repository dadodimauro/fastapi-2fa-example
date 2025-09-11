from typing import Any

import httpx
from pydantic import BaseModel, Field

from fastapi_2fa_example.config import settings
from fastapi_2fa_example.logger import logger


class SendGridEmail(BaseModel):
    personalizations: list[dict[str, Any]]
    from_: dict[str, str] = Field(..., serialization_alias="from")
    content: list[dict[str, str]]


async def send_email(
    to_email: str, subject: str, body: str
) -> None:  # pragma: no cover
    """Mock email sender function"""
    logger.warning(
        f"Sending email to {to_email} with subject '{subject}' and body: {body}"
    )

    if settings.is_testing():
        logger.warning("Skipping actual email sending in testing mode.")
        return

    if not settings.ENABLE_SENDGRID:
        logger.error("SendGrid is disabled. Email not sent.")
        return

    email = SendGridEmail(
        personalizations=[
            {
                "to": [{"email": to_email}],
                "subject": subject,
            }
        ],
        from_={"email": settings.EMAIL_FROM},
        content=[{"type": "text/plain", "value": body}],
    )

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.sendgrid.com/v3/mail/send",
            headers={
                "Authorization": f"Bearer {settings.SENDGRID_API_KEY.get_secret_value()}",
                "Content-Type": "application/json",
            },
            json=email.model_dump(by_alias=True, mode="json"),
        )
        response.raise_for_status()

    logger.info(f"Email sent to {to_email}")
    return
