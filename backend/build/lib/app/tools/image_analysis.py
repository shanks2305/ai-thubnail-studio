from PIL import Image

from app.tools.colors import mean_luminance


def analyze_image(path: str) -> dict[str, object]:
    image = Image.open(path).convert("RGB")
    small = image.resize((48, 48))
    left = mean_luminance(small.crop((0, 0, 24, 48)))
    right = mean_luminance(small.crop((24, 0, 48, 48)))
    average = (left + right) / 2
    return {
        "dominant_colors": _dominant_colors(small, 3),
        "subject_side": "left" if left > right else "right",
        "brightness": "high" if average > 0.6 else "medium" if average > 0.3 else "low",
    }


def _dominant_colors(image: Image.Image, count: int) -> list[str]:
    quantized = image.quantize(colors=count)
    palette = quantized.getpalette() or []
    colors: list[str] = []
    for index in range(count):
        start = index * 3
        if start + 2 >= len(palette):
            break
        red, green, blue = palette[start : start + 3]
        colors.append(f"#{red:02x}{green:02x}{blue:02x}")
    return colors
