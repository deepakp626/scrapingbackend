from io import BytesIO
from PIL import Image


def compress_image_to_webp(
    image_bytes: bytes,
    target_size_kb: int = 100,
    min_quality: int = 10,
    max_quality: int = 95,
) -> bytes:
    """
    Compress image only if its size is greater than target_size_kb.
    Output format will always be WebP if compression is performed.
    """

    target_size = target_size_kb * 1024

    # If image is already within target size, return as-is
    if len(image_bytes) <= target_size:
        return image_bytes

    image = Image.open(BytesIO(image_bytes))

    # Convert to RGB
    if image.mode in ("RGBA", "P"):
        background = Image.new("RGB", image.size, (255, 255, 255))
        background.paste(
            image,
            mask=image.split()[-1] if image.mode == "RGBA" else None,
        )
        image = background
    else:
        image = image.convert("RGB")

    best_output = None
    low = min_quality
    high = max_quality

    # Binary search for best quality
    while low <= high:
        quality = (low + high) // 2

        output = BytesIO()
        image.save(
            output,
            format="WEBP",
            quality=quality,
            optimize=True,
            method=6,
        )

        size = output.tell()

        if size <= target_size:
            best_output = output.getvalue()
            low = quality + 1
        else:
            high = quality - 1

    # Resize if still too large
    if best_output is None:
        width, height = image.size

        while width > 100 and height > 100:
            width = int(width * 0.9)
            height = int(height * 0.9)

            resized = image.resize((width, height), Image.LANCZOS)

            output = BytesIO()
            resized.save(
                output,
                format="WEBP",
                quality=min_quality,
                optimize=True,
                method=6,
            )

            if output.tell() <= target_size:
                best_output = output.getvalue()
                break

    # Fallback if target size couldn't be achieved
    if best_output is None:
        output = BytesIO()
        image.save(
            output,
            format="WEBP",
            quality=min_quality,
            optimize=True,
            method=6,
        )
        best_output = output.getvalue()

    return best_output