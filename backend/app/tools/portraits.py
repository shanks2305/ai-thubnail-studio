from io import BytesIO

from PIL import Image
from sqlalchemy.orm import Session

from app.db.models import Asset, Project
from app.tools.colors import mean_luminance
from app.tools.storage import read_bytes

MAX_PEOPLE = 3


def load_people(session: Session, project: Project) -> list[Image.Image]:
    del session
    uploaded = [asset for asset in project.assets if asset.kind in {"face", "person"}]
    chosen = uploaded or [asset for asset in project.assets if asset.kind == "video_person"]
    images: list[Image.Image] = []
    for asset in chosen[:MAX_PEOPLE]:
        try:
            images.append(Image.open(BytesIO(read_bytes(asset.path))).convert("RGB"))
        except OSError:
            continue
    return images


def subject_portrait(image: Image.Image) -> Image.Image:
    rgb = image.convert("RGB")
    width, height = rgb.size
    sample = rgb.resize((48, 48))
    left = mean_luminance(sample.crop((0, 0, 24, 48)))
    right = mean_luminance(sample.crop((24, 0, 48, 48)))
    crop_w = max(int(width * 0.42), 1)
    crop_h = max(int(height * 0.78), 1)
    margin_x = int(width * 0.05)
    y = int(height * 0.04)
    x = margin_x if left >= right else max(width - crop_w - margin_x, 0)
    return rgb.crop((x, y, min(x + crop_w, width), min(y + crop_h, height)))


def jpeg_bytes(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.convert("RGB").save(buffer, format="JPEG", quality=90)
    return buffer.getvalue()


def has_uploaded_people(project: Project) -> bool:
    return any(asset.kind in {"face", "person"} for asset in project.assets)


def video_person_asset(project_id: str, path: str) -> Asset:
    from uuid import uuid4

    return Asset(
        id=str(uuid4()),
        project_id=project_id,
        kind="video_person",
        content_type="image/jpeg",
        path=path,
    )
