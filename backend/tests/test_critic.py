from PIL import Image

from app.domain.state import DesignSpec, TextSpec
from app.tools.compositor import compose
from app.tools.critic import critique_image, revise_spec


def _spec(color: str = "#ffffff", scrim: bool = False) -> DesignSpec:
    return DesignSpec(
        text=TextSpec(content="AI WON", position="left", size="very large", color=color),
        scrim=scrim,
        palette=["#ffffff", "#ff4d2e", "#f2c14e"],
    )


def test_white_headline_on_white_fails():
    image = compose(Image.new("RGB", (1280, 720), "white"), _spec())
    critique = critique_image(image, _spec())
    assert critique.passed is False
    assert any(issue.type == "text_readability" for issue in critique.issues)


def test_scrim_revision_becomes_readable():
    spec = _spec()
    background = Image.new("RGB", (1280, 720), "white")
    critique = critique_image(compose(background, spec), spec)
    revised = revise_spec(spec, critique)
    second = critique_image(compose(background, revised), revised)
    assert revised.scrim is True
    assert second.passed is True
