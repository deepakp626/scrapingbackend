from supabase import create_client, Client
from utils.image import compress_image_to_webp
from storage3.exceptions import StorageApiError
import os
import re

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

BUCKET_NAME = "blog-thumbnail"




def upload_image(
    slug: str,
    file_bytes: bytes,
    extension: str = "webp"
):
    # Convert slug into a safe filename
    filename = re.sub(r"[^a-zA-Z0-9_-]", "-", slug).lower()
    filename = f"{filename}.{extension}"

    #Compress image 
    compressed_file_bytes = compress_image_to_webp(file_bytes)

    # Upload image
    supabase.storage.from_(BUCKET_NAME).upload(
        path=filename,
        file=compressed_file_bytes,
        file_options={
            "content-type": f"image/{extension}"
        }
    )

    # Get public URL
    image_url = (
        supabase.storage
        .from_(BUCKET_NAME)
        .get_public_url(filename)
    )

    return {
        "path": filename,
        "url": image_url
    }



def delete_image(slug: str):

    filename = f"{slug}.webp"

    try:
        response = (
            supabase.storage
            .from_(BUCKET_NAME)
            .remove([filename])
        )

        return response
    
    except StorageApiError as e:
        raise Exception(f"Failed to delete image: {e}")



def replace_image(slug: str,new_file_bytes:bytes):
    # first delete the old image
    delete_image(slug)
    # then upload the new image
    return upload_image(slug,new_file_bytes)