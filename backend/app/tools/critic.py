from PIL import Image

from app.core.config import get_settings
from app.domain.state import Critique, DesignSpec, Issue
from app.tools.colors import hex_to_rgb, mean_luminance, relative_luminance
from app.tools.compositor import CANVAS


def critique_image(image: Image.Image, spec: DesignSpec) -> Critique:
    region = _text_region(spec.text.position)
    background = mean_luminance(image.crop(region))
    text_luminance = relative_luminance(hex_to_rgb(spec.text.color))
    contrast = abs(text_luminance - background)
    words = [word for word in spec.text.content.split() if word]
    issues: list[Issue] = []
    changes: list[str] = []
    score = 90

    if contrast < 0.35:
        issues.append(
            Issue(
                type="text_readability",
                severity="high",
                message="The headline does not separate from the background.",
            )
        )
        changes.append("Darken the area behind the headline")
        score -= 28
    left = mean_luminance(image.crop((0, 0, CANVAS[0] // 2, CANVAS[1])))
    right = mean_luminance(image.crop((CANVAS[0] // 2, 0, CANVAS[0], CANVAS[1])))
    if abs(left - right) < 0.03:
        issues.append(
            Issue(
                type="flat_separation",
                severity="medium",
                message="The subject does not separate from the background.",
            )
        )
        changes.append("Increase subject contrast and keep the headline side darker")
        score -= 12
    if len(words) > 6:
        issues.append(
            Issue(
                type="text_density",
                severity="medium",
                message="The headline is too long to read on a phone.",
            )
        )
        changes.append("Cut the headline to five words or fewer")
        score -= 16
    if not words:
        issues.append(Issue(type="missing_hook", severity="high", message="The thumbnail has no headline."))
        score -= 40

    score = max(0, min(100, score))
    passed = score >= get_settings().pass_score and not any(issue.severity == "high" for issue in issues)
    return Critique(overall=score, issues=issues, recommended_changes=changes, passed=passed)


def revise_spec(spec: DesignSpec, critique: Critique) -> DesignSpec:
    updated = spec.model_copy(deep=True)
    kinds = {issue.type for issue in critique.issues}
    if "text_readability" in kinds:
        updated.scrim = True
        updated.scrim_strength = max(updated.scrim_strength, 0.78)
        updated.text.color = "#ffffff"
    if "text_density" in kinds:
        updated.text.content = " ".join(updated.text.content.split()[:4])
    return updated


def _text_region(position: str) -> tuple[int, int, int, int]:
    if position == "right":
        return (560, 140, CANVAS[0] - 40, 620)
    if position == "center":
        return (160, 160, 1120, 600)
    return (40, 140, 760, 620)
