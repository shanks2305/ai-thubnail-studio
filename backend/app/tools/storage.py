import shutil
from pathlib import Path
from uuid import uuid4

from app.core.config import get_settings


def save_bytes(project_id: str, kind: str, data: bytes, suffix: str) -> str:
    if get_settings().storage_backend == "s3":
        from app.tools.storage_s3 import save_s3

        return save_s3(project_id, kind, data, suffix)
    root = get_settings().storage_path
    folder = root / project_id / kind
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{uuid4().hex}{suffix}"
    path.write_bytes(data)
    return str(path)


def read_bytes(path: str) -> bytes:
    if path.startswith("s3://"):
        from app.tools.storage_s3 import read_s3

        return read_s3(path)
    resolved = Path(path).resolve()
    root = get_settings().storage_path
    if not resolved.is_relative_to(root):
        raise ValueError("Asset path is outside storage")
    return resolved.read_bytes()


def delete_project_files(project_id: str) -> None:
    if get_settings().storage_backend == "s3":
        from app.tools.storage_s3 import delete_prefix

        delete_prefix(project_id)
        return
    folder = get_settings().storage_path / project_id
    if folder.exists():
        shutil.rmtree(folder)
