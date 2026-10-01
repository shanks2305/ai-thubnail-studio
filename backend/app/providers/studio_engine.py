import re
from typing import Any

from app.domain.styles import style_prompt
from app.providers.research_fallback import research_from_gathered


def run_task(task: str, payload: dict[str, Any]) -> dict[str, Any]:
    handlers = {
        "video_analyst": _video_brief,
        "reference_analyst": _reference_profile,
        "audience_analyst": _audience,
        "researcher": research_from_gathered,
        "hook_strategist": _hooks,
        "creative_director": _concepts,
        "visual_director": _design_spec,
    }
    handler = handlers.get(task)
    if handler is None:
        raise ValueError(f"Unknown studio task: {task}")
    return handler(payload)


def _video_brief(payload: dict[str, Any]) -> dict[str, Any]:
    description = str(payload.get("description") or "")
    youtube = payload.get("youtube") or {}
    title = str(youtube.get("title") or "") if isinstance(youtube, dict) else ""
    topic = title or _clause(description)
    words = _keywords(description)
    return {
        "topic": topic[:180],
        "core_story": description[:800],
        "central_tension": _tension(description, words),
        "key_entities": words[:5],
        "audience": "People who decide in a second whether the outcome is worth the click.",
        "emotional_angles": ["curiosity", "stakes", "surprise"],
        "visual_opportunities": [
            "One dominant subject with empty space for a short headline",
            "A comparison that makes a winner obvious",
            "A close crop that makes the result feel immediate",
        ],
    }


def _audience(payload: dict[str, Any]) -> dict[str, Any]:
    brief = payload.get("video_brief") if isinstance(payload.get("video_brief"), dict) else {}
    viewer = str(brief.get("audience") or "A viewer scrolling on a phone")
    return {
        "viewer": viewer[:240],
        "belief": "They have seen a similar claim and want a specific result.",
        "click_reason": "The frame promises one outcome they can judge in a second.",
        "avoid": ["Vague promises", "More than five words", "Tiny unreadable type"],
    }


def _reference_profile(payload: dict[str, Any]) -> dict[str, Any]:
    references = payload.get("references") if isinstance(payload.get("references"), list) else []
    saved = payload.get("creator_style") or payload.get("channel_style")
    if not references and isinstance(saved, dict) and saved.get("style_summary"):
        return _saved_profile(saved)
    if not references:
        return _default_profile()
    colors: list[str] = []
    for reference in references:
        if isinstance(reference, dict):
            colors.extend(str(color) for color in reference.get("dominant_colors", []))
    side = "right"
    first = references[0]
    if isinstance(first, dict) and first.get("subject_side") in {"left", "right"}:
        side = str(first["subject_side"])
    text_side = "left" if side == "right" else "right"
    return {
        "style_summary": "Match the reference contrast and keep the subject on the busy side of the frame.",
        "composition": {"subject_position": side, "text_position": text_side, "subject_scale": "large"},
        "typography": {"word_count": "2-5", "weight": "heavy", "contrast": "high"},
        "color_palette": (colors or ["#16130f", "#ff4d2e", "#f2c14e"])[:4],
        "visual_language": ["high contrast", "bold type", "single subject"],
        "do_not_copy": ["Do not recreate a specific creator's face, logo, or exact layout."],
    }


def _hooks(payload: dict[str, Any]) -> dict[str, Any]:
    brief = payload.get("video_brief") if isinstance(payload.get("video_brief"), dict) else {}
    words = [str(word) for word in brief.get("key_entities", [])] or _keywords(str(payload.get("description") or ""))
    description = str(payload.get("description") or "")
    hooks = [{"id": "", "text": text, "angle": angle} for text, angle in _hook_lines(words, description)]
    game = _game_name(payload)
    if game:
        hooks.insert(0, {"id": "", "text": game.upper()[:28], "angle": "the game"})
    return {"hooks": hooks[:4]}


def _concepts(payload: dict[str, Any]) -> dict[str, Any]:
    brief = payload.get("video_brief") if isinstance(payload.get("video_brief"), dict) else {}
    topic = str(brief.get("topic") or "this video")
    hook_rows = payload.get("hooks") if isinstance(payload.get("hooks"), list) else []
    texts = [str(row.get("text")) for row in hook_rows if isinstance(row, dict) and row.get("text")]
    if len(texts) < 4:
        texts = [text for text, _angle in _hook_lines(_keywords(topic), topic)]
    frames = [
        ("The reaction", "surprise", "A person fills the foreground and reacts to the result.", "The face stays large. The headline sits in the empty half."),
        ("The proof", "certainty", "One clear winner sits in front of the attempts behind it.", "The winner is sharp. Everything else falls out of focus."),
        ("The question", "skepticism", "The frame asks one question and leaves the answer inside the video.", "Few objects. The question is the only text."),
        ("The stakes", "urgency", "Show what changes if the claim is true.", "Calm on the text side, disruption behind the subject."),
    ]
    look = style_prompt(str(payload.get("creative_style") or "cinematic"))
    game = _game_name(payload)
    place = f"Inside {game}. " if game else ""
    person = "The creator or a person from the video" if payload.get("has_people") else "A person"
    concepts = []
    for index, (name, emotion, story, composition) in enumerate(frames):
        hook = texts[index % len(texts)]
        concepts.append(
            {
                "id": "",
                "name": name,
                "hook": hook,
                "visual_story": f"{story} The video is about {topic}.",
                "subject": f"{person} fills the foreground and expresses {emotion}. {story} No text in the scene.",
                "background": f"{place}{look} Depth, not a collage of tiny details.",
                "composition": composition,
                "text": hook,
                "emotional_direction": emotion,
                "why_it_works": f"It turns “{topic}” into one claim a viewer can read on a phone.",
            }
        )
    return {"concepts": concepts}


def _design_spec(payload: dict[str, Any]) -> dict[str, Any]:
    concept = payload.get("concept") if isinstance(payload.get("concept"), dict) else {}
    profile = payload.get("reference_profile") if isinstance(payload.get("reference_profile"), dict) else {}
    composition = profile.get("composition") if isinstance(profile.get("composition"), dict) else {}
    text_position = composition.get("text_position") if composition.get("text_position") in {"left", "center", "right"} else "left"
    subject_position = "left" if text_position == "right" else "right"
    brand = payload.get("brand") if isinstance(payload.get("brand"), dict) else {}
    palette = profile.get("color_palette") if isinstance(profile.get("color_palette"), list) else []
    if isinstance(brand.get("colors"), list) and brand["colors"]:
        palette = brand["colors"]
    font = brand.get("font") if brand.get("font") in {"anton", "bebas"} else "anton"
    headline = str(concept.get("text") or concept.get("hook") or "WATCH THIS")
    subject = str(concept.get("subject") or "A single expressive subject")
    background = str(concept.get("background") or "A dark cinematic background")
    style = str(payload.get("creative_style") or "cinematic")
    return {
        "canvas": "1280x720",
        "subject": {"position": subject_position, "scale": "large", "description": subject, "style": style},
        "background": {"description": background, "depth": "medium"},
        "lighting": "Hard key light and deep shadows so the subject reads at thumbnail size.",
        "composition": str(concept.get("composition") or "Subject opposite the headline."),
        "text": {
            "content": headline,
            "position": text_position,
            "size": "very large",
            "color": "#ffffff",
            "font": font,
            "stroke": True,
            "vertical": "middle",
        },
        "image_prompt": f"{style_prompt(style)} {subject} {background} No text, letters, logos, or watermark.",
        "palette": [str(color) for color in palette][:4],
        "scrim": False,
    }


def _game_name(payload: dict[str, Any]) -> str:
    research = payload.get("research_brief")
    if not isinstance(research, dict):
        return ""
    game = research.get("game")
    if not isinstance(game, dict):
        return ""
    return str(game.get("name") or "").strip()


def _saved_profile(saved: dict[str, Any]) -> dict[str, Any]:
    return {
        "style_summary": str(saved.get("style_summary")),
        "composition": saved.get("composition") if isinstance(saved.get("composition"), dict) else {},
        "typography": saved.get("typography") if isinstance(saved.get("typography"), dict) else {},
        "color_palette": list(saved.get("color_palette") or [])[:6],
        "visual_language": [str(item) for item in saved.get("visual_language") or []],
        "do_not_copy": [str(item) for item in saved.get("do_not_copy") or []],
    }


def _default_profile() -> dict[str, Any]:
    return {
        "style_summary": "No reference uploaded. Use a high-contrast layout with one subject and a short headline.",
        "composition": {"subject_position": "right", "text_position": "left", "subject_scale": "large"},
        "typography": {"word_count": "2-5", "weight": "heavy", "contrast": "high"},
        "color_palette": ["#16130f", "#ff4d2e", "#f2c14e"],
        "visual_language": ["cinematic", "high contrast"],
        "do_not_copy": ["Do not imitate a specific creator's thumbnail."],
    }


def _hook_lines(words: list[str], description: str) -> list[tuple[str, str]]:
    number = re.search(r"\b\d+\b", description)
    lead = " ".join(word.upper() for word in words[:2]) or "WATCH THIS"
    lines: list[tuple[str, str]] = []
    if number:
        lines.append((f"{number.group()} TRIED", "reduction"))
        lines.append(("1 ACTUALLY WORKS", "winner"))
    lines.append((lead[:28], "direct claim"))
    if words:
        lines.append((f"WHY {words[0].upper()}?"[:28], "question"))
    lines.append(("THE REAL RESULT", "outcome"))
    unique: list[tuple[str, str]] = []
    seen: set[str] = set()
    for text, angle in lines:
        if text in seen:
            continue
        seen.add(text)
        unique.append((text, angle))
    while len(unique) < 4:
        unique.append((f"IDEA {len(unique) + 1}", "alternate"))
    return unique[:4]


def _keywords(description: str) -> list[str]:
    stop = {
        "the", "a", "an", "to", "of", "and", "or", "for", "in", "on", "with", "that", "this",
        "which", "can", "see", "one", "i", "my", "we", "it", "is", "was", "are", "be", "from",
        "your", "you", "how", "what", "when", "who", "into", "about", "just", "really", "actually",
        "tested", "using", "use", "than",
    }
    words = re.findall(r"[A-Za-z][A-Za-z0-9'+-]*", description)
    picked: list[str] = []
    for word in words:
        if word.lower() in stop or len(word) < 3:
            continue
        if word not in picked:
            picked.append(word)
    return picked[:6]


def _clause(description: str) -> str:
    text = " ".join(description.split())
    for mark in ".?!":
        if mark in text:
            text = text.split(mark)[0]
            break
    return text[:180] or "Untitled video"


def _tension(description: str, words: list[str]) -> str:
    if re.search(r"\b\d+\b", description):
        return "Many options, and only one of them matters."
    if words:
        return f"Whether {words[0]} changes the outcome the viewer expects."
    return "A result that is more specific than the title suggests."
