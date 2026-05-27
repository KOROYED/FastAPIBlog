import uuid                                                             # for generating unique file names
from io import BytesIO                                                  # for working with image bytes in memory
from pathlib import Path                                                # for file operations

from PIL import Image, ImageOps


PROFILE_PICS_DIR = Path("media/profile_pics")


def process_profile_image(content: bytes) -> str:
    with Image.open(BytesIO(content)) as original:                                              # open img from bytes that we receive
        img = ImageOps.exif_transpose(original)                                                 # fixes orientation issues

        img = ImageOps.fit(img, (300, 300), method=Image.Resampling.LANCZOS)

        if img.mode in ("RGBA", "LA", "P"):                                                     # convert to rgb (needed to save in JPEG)
            img = img.convert("RGB")

        filename = f"{uuid.uuid4().hex}.jpg"                                                    # we ignore user's filename and generate our own for security
        filepath = PROFILE_PICS_DIR / filename

        PROFILE_PICS_DIR.mkdir(parents=True, exist_ok=True)

        img.save(filepath, "JPEG", quality=85, optimize=True)

    return filename


def delete_profile_image(filename: str | None) -> None:
    if filename is None:
        return
    
    filepath = PROFILE_PICS_DIR / filename
    if filepath.exists():
        filepath.unlink()