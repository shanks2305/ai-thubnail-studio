from PIL import Image, ImageDraw

from app.domain.state import DesignSpec, TextSpec


def tint_to_palette(image: Image.Image, palette: list[str]) -> Image.Image:
    from app.tools.compositor import make_studio_background

    grade = make_studio_background(DesignSpec(text=TextSpec(content="X"), palette=palette[:6]))
    if grade.size != image.size:
        grade = grade.resize(image.size)
    return Image.blend(image.convert("RGB"), grade.convert("RGB"), 0.42)


def place_portrait(image: Image.Image, portrait: Image.Image, spec: DesignSpec) -> Image.Image:
    from app.tools.compositor import cover

    size = 460
    cropped = cover(portrait.convert("RGB"), size, size)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((8, 8, size - 8, size - 8), fill=255)
    sprite = cropped.convert("RGBA")
    sprite.putalpha(mask)
    side = str(spec.subject.get("position", "right"))
    x = 760 if side != "left" else 60
    base = image.convert("RGBA")
    base.alpha_composite(sprite, (x, 130))
    return base.convert("RGB")
