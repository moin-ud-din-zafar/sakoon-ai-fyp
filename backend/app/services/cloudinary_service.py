"""Cloudinary upload helpers for user profile images."""

from __future__ import annotations

from typing import Optional

import cloudinary
import cloudinary.uploader

from app.config import CLOUDINARY_KEY, CLOUDINARY_NAME, CLOUDINARY_SECRET


def is_cloudinary_configured() -> bool:
    return bool(CLOUDINARY_NAME and CLOUDINARY_KEY and CLOUDINARY_SECRET)


def _configure() -> None:
    cloudinary.config(
        cloud_name=CLOUDINARY_NAME,
        api_key=CLOUDINARY_KEY,
        api_secret=CLOUDINARY_SECRET,
        secure=True,
    )


def upload_profile_image_bytes(image_bytes: bytes, *, user_id: int) -> Optional[str]:
    """
    Upload profile image bytes to Cloudinary.
    Returns secure URL or None when Cloudinary is not configured.
    """
    if not is_cloudinary_configured():
        return None
    _configure()
    result = cloudinary.uploader.upload(
        image_bytes,
        folder="sakoon/profile-images",
        resource_type="image",
        overwrite=True,
        public_id=f"user-{user_id}",
    )
    return result.get("secure_url")
