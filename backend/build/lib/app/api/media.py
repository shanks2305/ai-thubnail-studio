from io import BytesIO
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response
from PIL import Image

from app.api.projects import require_project
from app.core.database import session_scope
from app.db.models import Asset, Generation, utcnow
from app.tools.compositor import image_bytes
from app.tools.storage import read_bytes, save_bytes

router = APIRouter()
MAX_BYTES = 8 * 1024 * 1024
MAX_REFERENCES = 6
FORMATS = {
    "png": ("PNG", "image/png", "png"),
    "jpeg": ("JPEG", "image/jpeg", "jpg"),
    "jpg": ("JPEG", "image/jpeg", "jpg"),
    "webp": ("WEBP", "image/webp", "webp"),
}
PIL_FORMATS = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp"}


@router.post("/projects/{project_id}/references", status_code=201)
def upload_references(project_id: str, files: list[UploadFile] = File(...)) -> dict:
    prepared = [_read_image(upload) for upload in files]
    with session_scope() as session:
        project = require_project(session, project_id)
        existing = sum(1 for asset in project.assets if asset.kind == "reference")
        if existing + len(prepared) > MAX_REFERENCES:
            raise HTTPException(status_code=400, detail="A project can hold up to 6 reference images.")
        for data, suffix, content_type in prepared:
            path = save_bytes(project.id, "reference", data, suffix)
            session.add(
                Asset(
                    id=str(uuid4()),
                    project_id=project.id,
                    kind="reference",
                    content_type=content_type,
                    path=path,
                )
            )
        project.updated_at = utcnow()
        session.flush()
        rows = [asset for asset in session.query(Asset).filter_by(project_id=project.id, kind="reference")]
        references = [{"id": asset.id, "url": f"/api/assets/{asset.id}"} for asset in rows]
    return {"references": references}


@router.get("/assets/{asset_id}")
def get_asset(asset_id: str) -> Response:
    with session_scope() as session:
        asset = session.get(Asset, asset_id)
        if asset is None:
            raise HTTPException(status_code=404, detail="Asset not found.")
        try:
            data = read_bytes(asset.path)
        except (OSError, ValueError) as exc:
            raise HTTPException(status_code=404, detail="Asset not found.") from exc
        media_type = asset.content_type
    return Response(content=data, media_type=media_type, headers={"Cache-Control": "no-store"})


@router.get("/generations/{generation_id}/export")
def export_generation(generation_id: str, format: str = "png") -> Response:
    selected = FORMATS.get(format.lower())
    if selected is None:
        raise HTTPException(status_code=400, detail="Export PNG, JPG, or WebP.")
    pil_format, media_type, extension = selected
    with session_scope() as session:
        generation = session.get(Generation, generation_id)
        if generation is None or not generation.image_asset_id:
            raise HTTPException(status_code=404, detail="Thumbnail not found.")
        asset = session.get(Asset, generation.image_asset_id)
        if asset is None:
            raise HTTPException(status_code=404, detail="Thumbnail not found.")
        image = Image.open(BytesIO(read_bytes(asset.path))).convert("RGB")
    payload = image_bytes(image, pil_format)
    filename = f'thumbnail.{extension}'
    return Response(
        content=payload,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _read_image(upload: UploadFile) -> tuple[bytes, str, str]:
    data = upload.file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=400, detail="Each reference must be under 8 MB.")
    try:
        image = Image.open(BytesIO(data))
        image.load()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Upload a PNG, JPG, or WebP image.") from exc
    suffix = PIL_FORMATS.get(image.format or "")
    if suffix is None:
        raise HTTPException(status_code=400, detail="Upload a PNG, JPG, or WebP image.")
    content_type = {".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp"}[suffix]
    return data, suffix, content_type
