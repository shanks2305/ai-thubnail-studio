from app.domain.state import DesignSpec, TextSpec


def test_vertical_word_in_position_moves_to_vertical():
    spec = DesignSpec.model_validate(
        {
            "text": {"content": "LOST", "position": "top"},
            "image_prompt": "a dark hallway",
        }
    )
    assert spec.text.position == "left"
    assert spec.text.vertical == "top"


def test_unknown_text_enums_fall_back():
    text = TextSpec.model_validate(
        {"content": "HI", "position": "above", "size": "huge", "font": "impact", "vertical": "center"}
    )
    assert text.position == "left"
    assert text.size == "very large"
    assert text.font == "anton"
    assert text.vertical == "middle"


def test_explicit_vertical_wins_over_a_misplaced_position():
    text = TextSpec(content="HI", position="bottom", vertical="top")
    assert text.position == "left"
    assert text.vertical == "top"
