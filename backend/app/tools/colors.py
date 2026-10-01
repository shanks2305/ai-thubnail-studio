from PIL import Image


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    cleaned = value.strip().lstrip("#")
    if len(cleaned) == 3:
        cleaned = "".join(channel * 2 for channel in cleaned)
    if len(cleaned) != 6:
        return (255, 255, 255)
    try:
        return (int(cleaned[0:2], 16), int(cleaned[2:4], 16), int(cleaned[4:6], 16))
    except ValueError:
        return (255, 255, 255)


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    channels = []
    for channel in rgb:
        value = channel / 255
        channels.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
    red, green, blue = channels
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def mean_luminance(image: Image.Image) -> float:
    sample = image.convert("RGB").resize((24, 24))
    raw = sample.tobytes()
    count = len(raw) // 3
    if count == 0:
        return 0
    total = 0.0
    for index in range(count):
        start = index * 3
        total += relative_luminance((raw[start], raw[start + 1], raw[start + 2]))
    return total / count


def lerp(start: tuple[int, int, int], end: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(round(start[index] + (end[index] - start[index]) * amount) for index in range(3))  # type: ignore[return-value]


def darken(rgb: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(round(channel * (1 - amount)) for channel in rgb)  # type: ignore[return-value]


def lighten(rgb: tuple[int, int, int], amount: float) -> tuple[int, int, int]:
    return tuple(round(channel + (255 - channel) * amount) for channel in rgb)  # type: ignore[return-value]
