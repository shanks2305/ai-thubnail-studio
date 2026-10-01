from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from app.domain.state import DesignSpec
from app.tools.colors import darken, hex_to_rgb, lerp, lighten

CANVAS = (1280, 720)
FONT_PATH = Path(__file__).resolve().parents[1] / "assets" / "fonts" / "Anton-Regular.ttf"
SIZE_PX = {"medium": 64, "large": 84, "very large": 108}


def cover(image: Image.Image, width: int, height: int) -> Image.Image:
    scale = max(width / image.width, height / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = max((resized.width - width) // 2, 0)
    top = max((resized.height - height) // 2, 0)
    return resized.crop((left, top, left + width, top + height))


def make_studio_background(spec: DesignSpec) -> Image.Image:
    width, height = CANVAS
    palette = spec.palette or ["#16130f", "#ff4d2e", "#f2c14e"]
    base = hex_to_rgb(palette[0])
    accent = hex_to_rgb(palette[1] if len(palette) > 1 else "#ff4d2e")
    gold = hex_to_rgb(palette[2] if len(palette) > 2 else "#f2c14e")
    image = Image.new("RGB", CANVAS, base)
    draw = ImageDraw.Draw(image)
    for x in range(width):
        color = lerp(base, darken(accent, 0.45), (x / width) * 0.9)
        draw.line([(x, 0), (x, height)], fill=color)
    subject_on_right = str(spec.subject.get("position", "right")) != "left"
    center_x = 980 if subject_on_right else 280
    overlay = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    shapes = ImageDraw.Draw(overlay)
    shapes.ellipse((center_x - 300, 40, center_x + 250, 700), fill=(*accent, 235))
    shapes.ellipse((center_x - 90, 140, center_x + 170, 560), fill=(*lighten(gold, 0.15), 200))
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def compose(background: Image.Image, spec: DesignSpec) -> Image.Image:
    image = cover(background.convert("RGB"), *CANVAS)
    if spec.scrim:
        image = _apply_scrim(image, spec.text.position)
    _draw_headline(image, spec)
    return image


def _apply_scrim(image: Image.Image, position: str) -> Image.Image:
    width, height = image.size
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for x in range(width):
        if position == "right":
            strength = x / width
        elif position == "center":
            strength = 1 - abs(x - width / 2) / (width / 2)
        else:
            strength = 1 - x / width
        draw.line([(x, 0), (x, height)], fill=(6, 6, 8, int(200 * strength)))
    return Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")


def _draw_headline(image: Image.Image, spec: DesignSpec) -> None:
    draw = ImageDraw.Draw(image)
    size = SIZE_PX.get(spec.text.size, 108)
    font = _font(FONT_PATH, size)
    max_width = 980 if spec.text.position == "center" else 700
    lines = _wrap(draw, spec.text.content.upper(), font, max_width)[:3]
    line_height = int(size * 0.9)
    block_height = len(lines) * line_height
    y = max((CANVAS[1] - block_height) // 2, 80)
    color = hex_to_rgb(spec.text.color)
    for line in lines:
        x = _line_x(draw, line, font, spec.text.position)
        draw.text((x + 4, y + 4), line, font=font, fill=(0, 0, 0))
        draw.text((x, y), line, font=font, fill=color)
        y += line_height


def _line_x(draw: ImageDraw.ImageDraw, line: str, font: ImageFont.ImageFont, position: str) -> int:
    width = draw.textlength(line, font=font)
    if position == "right":
        return int(CANVAS[0] - 72 - width)
    if position == "center":
        return int((CANVAS[0] - width) / 2)
    return 72


def _wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split() or ["WATCH"]
    lines: list[str] = []
    current = ""
    for word in words:
        trial = word if not current else f"{current} {word}"
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
            continue
        if current:
            lines.append(current)
        current = word
    if current:
        lines.append(current)
    return lines


def _font(path: Path, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if path.exists():
        return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def image_bytes(image: Image.Image, image_format: str = "PNG") -> bytes:
    buffer = BytesIO()
    if image_format == "JPEG":
        image.convert("RGB").save(buffer, format="JPEG", quality=92)
    else:
        image.save(buffer, format=image_format)
    return buffer.getvalue()
