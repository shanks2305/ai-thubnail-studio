from PIL import Image, ImageDraw

from app.domain.state import DesignSpec, TextSpec


def tint_to_palette(image: Image.Image, palette: list[str]) -> Image.Image:
    from app.tools.compositor import make_studio_background

    grade = make_studio_background(DesignSpec(text=TextSpec(content="X"), palette=palette[:6]))
    if grade.size != image.size:
        grade = grade.resize(image.size)
    return Image.blend(image.convert("RGB"), grade.convert("RGB"), 0.42)


def place_people(image: Image.Image, people: list[Image.Image], spec: DesignSpec) -> Image.Image:
    from PIL import ImageFilter

    from app.tools.compositor import cover

    group = people[:3]
    heights = {1: [620], 2: [540, 480], 3: [480, 440, 400]}[len(group)]
    side = str(spec.subject.get("position", "right"))
    base = image.convert("RGBA")
    for index, (portrait, height) in enumerate(zip(group, heights, strict=True)):
        width = int(height * 0.72)
        sprite = _cutout(cover(portrait.convert("RGB"), width, height), ImageFilter.GaussianBlur(8))
        x, y = _anchor(side, index, len(group), width)
        base.alpha_composite(sprite, (x, max(y, 0)))
    return base.convert("RGB")


def _cutout(cropped: Image.Image, blur) -> Image.Image:
    width, height = cropped.size
    mask = Image.new("L", cropped.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((2, 2, width - 2, height - 2), radius=width // 2, fill=255)
    mask = mask.filter(blur)
    sprite = cropped.convert("RGBA")
    sprite.putalpha(mask)
    return sprite


def _anchor(side: str, index: int, count: int, width: int) -> tuple[int, int]:
    step = 90
    if side == "left":
        return 24 + index * step, 36 + index * 28
    return 1280 - width - 24 - (count - 1 - index) * step, 36 + index * 28
