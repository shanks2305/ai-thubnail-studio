import hashlib
import hmac
import secrets
from contextvars import ContextVar

from fastapi import HTTPException, Request
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.library import Member

_owner: ContextVar[str] = ContextVar("studio_owner", default="local")
PUBLIC_PATHS = {"/api/system", "/openapi.json", "/docs", "/redoc"}


def current_owner() -> str:
    return _owner.get()


def set_owner(owner_id: str) -> None:
    _owner.set(owner_id)


def primary_owner_id(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()[:32]


def new_member_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(24)
    return token, hashlib.sha256(token.encode()).hexdigest()


def resolve_owner(request: Request, session: Session) -> str:
    settings = get_settings()
    if not settings.auth_token:
        return "local"
    token = _presented_token(request)
    if token and hmac.compare_digest(token, settings.auth_token):
        return primary_owner_id(token)
    if token:
        digest = hashlib.sha256(token.encode()).hexdigest()
        member = session.query(Member).filter_by(token_hash=digest).one_or_none()
        if member is not None:
            return member.id
    raise HTTPException(status_code=401, detail="Sign in to use the studio.")


def _presented_token(request: Request) -> str:
    header = request.headers.get("authorization", "")
    if header.lower().startswith("bearer "):
        return header[7:].strip()
    return request.query_params.get("access_token", "").strip()
