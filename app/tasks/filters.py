from PIL import Image
import pilgram
import os, io, base64
from pathlib import Path
from app.worker.celery_app import celery_app
from file_flow_common import db
from file_flow_common.schema.query import DbAccessQuery
from app.utils.context import Context
from time import time

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))


def _image_to_base64(img: Image.Image) -> str:
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def _open_base64_image(b64_str: str) -> Image.Image:
    img_bytes = base64.b64decode(b64_str)
    return Image.open(io.BytesIO(img_bytes))


@celery_app.task(name="apply_filter", queue="images")
def apply_filter(image_id: str, filter_name: str = "toaster") -> str:
    """Apply Pilgram filter, save on mongoDB, and return base64-encoded image."""
    ctx = Context()

    image_b64 = db.get_document(
        db_query=DbAccessQuery(
            mongo_uri=ctx.MONGO_URI,
            db_name=ctx.DB_NAME,
            collection_name="images",
        ),
        doc_id=image_id,
    )

    if not image_b64 or "base64" not in image_b64:
        raise ValueError(f"Image with ID {image_id} not found in database.")

    if filter_name in image_b64:
        return image_b64[filter_name]

    image = _open_base64_image(image_b64["base64"])

    filter_func = getattr(pilgram, filter_name)
    filtered_image = filter_func(image)
    filtered_image_b64 = _image_to_base64(filtered_image)

    db.upsert_document(
        DbAccessQuery(
            mongo_uri=ctx.MONGO_URI,
            db_name=ctx.DB_NAME,
            collection_name="filtered_images",
        ),
        doc_id=image_id,
        data={f"{filter_name}": filtered_image_b64},
    )

    return {"image_b64": filtered_image_b64}
