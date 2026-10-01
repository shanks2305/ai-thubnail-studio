from io import BytesIO

from PIL import Image
from sqlalchemy.orm import Session

from app.db.models import Project
from app.tools.storage import read_bytes


def load_portrait(session: Session, project: Project) -> Image.Image | None:
    asset = next((item for item in project.assets if item.kind == "face"), None)
    if asset is None:
        return None
    try:
        return Image.open(BytesIO(read_bytes(asset.path))).convert("RGB")
    except OSError:
        return None
