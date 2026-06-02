"""Simple SMTP email service used for password reset notifications."""

from __future__ import annotations

import logging
import smtplib
from email.message import EmailMessage

from app.config import (
    SMTP_FROM_EMAIL,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_USE_TLS,
)

logger = logging.getLogger(__name__)


def send_password_reset_email(to_email: str, reset_link: str) -> bool:
    """
    Send reset-password email.

    Returns True when sent through SMTP; False when SMTP is not configured.
    """
    if not SMTP_HOST or not SMTP_USERNAME or not SMTP_PASSWORD:
        logger.warning(
            "SMTP not configured; password reset link for %s: %s",
            to_email,
            reset_link,
        )
        return False

    msg = EmailMessage()
    msg["Subject"] = "Sakoon AI - Password Reset"
    msg["From"] = SMTP_FROM_EMAIL
    msg["To"] = to_email
    msg.set_content(
        "We received a request to reset your Sakoon password.\n\n"
        f"Reset link: {reset_link}\n\n"
        "This link expires soon. If you did not request this, ignore this email."
    )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=20) as server:
        if SMTP_USE_TLS:
            server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)

    return True
