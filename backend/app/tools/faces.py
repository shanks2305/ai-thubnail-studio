from io import BytesIO
from uuid import uuid4

from PIL import Image
from sqlalchemy.orm import Session

from app.db.models import Asset, Project
from app.tools import youtube
from app.tools.portraits import MAX_PEOPLE, jpeg_bytes
from app.tools.storage import save_bytes
from app.tools.youtube import parse_video_id


def face_crop(image: Image.Image) -> Image.Image | None:
    rgb = image.convert("RGB")
    width, height = rgb.size
    if width < 32 or height < 32:
        return None
    sample_w = 96
    sample_h = max(int(sample_w * height / width), 1)
    raw = rgb.resize((sample_w, sample_h)).convert("YCbCr").tobytes()
    points = [
        ((offset // 3) % sample_w, (offset // 3) // sample_w)
        for offset in range(0, len(raw), 3)
        if _is_skin(raw[offset : offset + 3])
    ]
    if len(points) < 8:
        return None
    min_x, max_x = min(point[0] for point in points), max(point[0] for point in points)
    min_y, max_y = min(point[1] for point in points), max(point[1] for point in points)
    left = max(0, int(min_x * width / sample_w) - _pad(max_x - min_x, width / sample_w))
    top = max(0, int(min_y * height / sample_h) - _pad(max_y - min_y, height / sample_h))
    right = min(width, int((max_x + 1) * width / sample_w) + _pad(max_x - min_x, width / sample_w))
    bottom = min(height, int((max_y + 1) * height / sample_h) + _pad(max_y - min_y, height / sample_h))
    if right - left < 16 or bottom - top < 16:
        return None
    return rgb.crop((left, top, right, bottom))


def save_player_faces(session: Session, project: Project) -> int:
    existing = [asset for asset in project.assets if asset.kind == "person"]
    if existing or not project.youtube_url:
        return len(existing)
    video_id = parse_video_id(project.youtube_url)
    if video_id is None:
        return 0
    saved = 0
    for index in (1, 2, 3):
        if saved >= MAX_PEOPLE:
            break
        crop = _frame_face(video_id, index)
        if crop is None:
            continue
        path = save_bytes(project.id, "person", jpeg_bytes(crop), ".jpg")
        session.add(
            Asset(id=str(uuid4()), project_id=project.id, kind="person", content_type="image/jpeg", path=path)
        )
        saved += 1
    if saved:
        session.commit()
        session.refresh(project)
    return saved


def _frame_face(video_id: str, index: int) -> Image.Image | None:
    data = youtube.download_bytes(f"https://i.ytimg.com/vi/{video_id}/{index}.jpg")
    if data is None:
        return None
    try:
        return face_crop(Image.open(BytesIO(data)))
    except OSError:
        return None


def _is_skin(pixel: tuple[int, ...]) -> bool:
    y, cb, cr = pixel[:3]
    return y > 50 and 77 <= cb <= 127 and 133 <= cr <= 173


def _pad(span: int, scale: float) -> int:
    return int(span * scale * 0.45)
