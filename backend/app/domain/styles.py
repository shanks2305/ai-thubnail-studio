from typing import TypedDict


class CreativeStyle(TypedDict):
    id: str
    label: str
    prompt: str


STYLES: tuple[CreativeStyle, ...] = (
    {
        "id": "cinematic",
        "label": "Cinematic",
        "prompt": "Photorealistic cinematic still, dramatic key light, sharp focus, bold contrast.",
    },
    {
        "id": "ghibli",
        "label": "Ghibli",
        "prompt": "Ghibli-inspired hand-painted animation still: soft watercolor light, lush background, gentle atmosphere.",
    },
    {
        "id": "anime",
        "label": "Anime",
        "prompt": "Anime key visual: clean line art, cel shading, saturated color, dynamic pose.",
    },
    {
        "id": "cartoon",
        "label": "Cartoon",
        "prompt": "Cartoon illustration: thick outlines, simplified shapes, playful color, a big readable silhouette.",
    },
    {
        "id": "gaming",
        "label": "Gaming",
        "prompt": "Gaming scene: neon HUD glow, arena energy, high saturation, dramatic rim light.",
    },
    {
        "id": "tech",
        "label": "Tech",
        "prompt": "Tech product scene: dark studio, crisp screens, cool blue light, precise geometry.",
    },
    {
        "id": "comic",
        "label": "Comic",
        "prompt": "Comic-book panel: heavy ink outlines, halftone texture, heroic pose, primary colors.",
    },
    {
        "id": "documentary",
        "label": "Documentary",
        "prompt": "Documentary still: natural light, a real location, honest color, shallow depth of field.",
    },
    {
        "id": "neon",
        "label": "Neon",
        "prompt": "Night scene with magenta and cyan neon rim light, wet surfaces, high contrast.",
    },
    {
        "id": "minimal",
        "label": "Minimal",
        "prompt": "Minimal studio backdrop, one strong color, lots of empty space, graphic and clean.",
    },
)

STYLE_IDS = {item["id"] for item in STYLES}


def style_prompt(style_id: str | None) -> str:
    for item in STYLES:
        if item["id"] == style_id:
            return item["prompt"]
    return STYLES[0]["prompt"]
