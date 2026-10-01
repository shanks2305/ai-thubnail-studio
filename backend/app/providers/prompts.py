from functools import lru_cache
from pathlib import Path


@lru_cache
def load_prompt(agent: str) -> str:
    path = Path(__file__).resolve().parents[2] / "prompts" / agent / "v1.md"
    if not path.exists():
        return "Return one JSON object that matches the requested schema."
    return path.read_text(encoding="utf-8")
