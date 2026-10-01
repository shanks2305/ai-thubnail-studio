from app.domain.state import DesignSpec


def apply_editor(spec: DesignSpec, body) -> DesignSpec:
    updated = spec.model_copy(deep=True)
    updated.text.content = body.content
    updated.text.position = body.position
    updated.text.size = body.size
    updated.text.color = body.color
    if body.font is not None:
        updated.text.font = body.font
    if body.stroke is not None:
        updated.text.stroke = body.stroke
    if body.vertical is not None:
        updated.text.vertical = body.vertical
    if body.scrim_strength is not None:
        updated.scrim_strength = body.scrim_strength
        updated.scrim = body.scrim_strength > 0
    if body.palette is not None:
        updated.palette = body.palette
    if body.recolor is not None:
        updated.recolor = body.recolor
    return updated
