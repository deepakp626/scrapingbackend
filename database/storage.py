import os
import re

from supabase import create_client, Client
from storage3.exceptions import StorageApiError

from utils.image import compress_image_to_webp


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL environment variable is not set")

if not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_KEY environment variable is not set")


supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY,
)

BUCKET_NAME = "blog-thumbnail"


def _safe_filename(slug: str, extension: str = "webp") -> str:
    """
    Convert blog slug into a safe and consistent storage filename.

    Example:
        "my-first-blog"
        -> "my-first-blog.webp"

        "My First Blog!"
        -> "my-first-blog-.webp"
    """

    filename = re.sub(
        r"[^a-zA-Z0-9_-]",
        "-",
        slug,
    ).lower()

    return f"{filename}.{extension}"


def upload_image(
    slug: str,
    file_bytes: bytes,
    extension: str = "webp",
):
    """
    Upload or replace a blog thumbnail.

    Uses upsert=True so uploading an existing filename
    replaces the existing Supabase object instead of
    returning an 'already exists' error.
    """

    if not file_bytes:
        raise ValueError("Image file is empty")

    # ---------------------------------------------------------
    # Create consistent filename
    # ---------------------------------------------------------

    filename = _safe_filename(
        slug,
        extension,
    )

    # ---------------------------------------------------------
    # Compress image
    # ---------------------------------------------------------

    try:
        compressed_file_bytes = compress_image_to_webp(
            file_bytes
        )
    except Exception as e:
        raise ValueError(
            f"Failed to compress image: {str(e)}"
        ) from e

    if not compressed_file_bytes:
        raise ValueError(
            "Image compression returned empty data"
        )

    # ---------------------------------------------------------
    # Upload with UPSERT
    # ---------------------------------------------------------

    try:
        storage = supabase.storage.from_(
            BUCKET_NAME
        )

        storage.upload(
            path=filename,
            file=compressed_file_bytes,
            file_options={
                "content-type": "image/webp",
                "upsert": "true",
            },
        )

    except StorageApiError as e:
        raise RuntimeError(
            f"Supabase image upload failed: {str(e)}"
        ) from e

    # ---------------------------------------------------------
    # Get public URL
    # ---------------------------------------------------------

    try:
        image_url = storage.get_public_url(
            filename
        )
    except Exception as e:
        raise RuntimeError(
            f"Image uploaded but failed to get public URL: {str(e)}"
        ) from e

    return {
        "path": filename,
        "url": image_url,
    }


def delete_image(slug: str):
    """
    Delete a blog thumbnail from Supabase.
    """

    filename = _safe_filename(
        slug,
        "webp",
    )

    try:
        storage = supabase.storage.from_(
            BUCKET_NAME
        )

        response = storage.remove(
            [filename]
        )

        return response

    except StorageApiError as e:
        raise RuntimeError(
            f"Failed to delete image '{filename}': {str(e)}"
        ) from e


def replace_image(
    slug: str,
    new_file_bytes: bytes,
):
    """
    Replace an existing image.

    No delete is required because upload_image()
    already uses upsert=True.
    """

    return upload_image(
        slug=slug,
        file_bytes=new_file_bytes,
        extension="webp",
    )