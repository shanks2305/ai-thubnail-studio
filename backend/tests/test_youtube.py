from app.tools.youtube import parse_video_id


def test_parse_watch_url():
    assert parse_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_parse_short_url():
    assert parse_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"


def test_parse_shorts_url():
    assert parse_video_id("https://www.youtube.com/shorts/abcdefghijk") == "abcdefghijk"


def test_reject_other_hosts():
    assert parse_video_id("https://vimeo.com/123") is None
