import logging

from PIL import Image
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.agents.runner import record_step, run_structured
from app.core.config import get_settings
from app.db.models import Project
from app.domain.state import Critique, DesignSpec
from app.providers.base import ProviderError
from app.tools.compositor import image_bytes
from app.tools.critic import critique_image

logger = logging.getLogger(__name__)


def judge_thumbnail(session: Session, project: Project, image: Image.Image, spec: DesignSpec) -> Critique:
    """Pixel checks run first; the judge model only sees thumbnails that pass them."""
    settings = get_settings()
    checks = critique_image(image, spec)
    if not checks.passed or settings.provider_for("judge") == "studio":
        return _record_checks(session, project, checks)
    try:
        verdict = run_structured(
            session,
            project,
            "critic",
            {"description": project.description, "design_spec": spec.model_dump(), "pixel_checks": checks.model_dump()},
            Critique,
            images=(image_bytes(image),),
        )
    except (ProviderError, ValidationError):
        if settings.is_production:
            raise
        logger.warning("The judge model failed; using the pixel checks")
        return _record_checks(session, project, checks)
    return _apply_pass_rule(verdict, settings.pass_score)


def _apply_pass_rule(verdict: Critique, pass_score: int) -> Critique:
    score = max(0, min(100, verdict.overall))
    passed = score >= pass_score and not any(issue.severity == "high" for issue in verdict.issues)
    return verdict.model_copy(update={"overall": score, "passed": passed})


def _record_checks(session: Session, project: Project, checks: Critique) -> Critique:
    record_step(
        session,
        project.id,
        "critic",
        "local-contrast",
        "pixel-critic",
        {"overall": checks.overall, "passed": checks.passed},
    )
    return checks
