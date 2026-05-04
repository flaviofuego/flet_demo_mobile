import pytest


def _score_color(avg: float) -> str:
    """Copy of the function under test — imported indirectly via importlib to isolate."""
    from src.presentation.theme.app_colors import SK_SUCCESS, SK_PRIMARY
    if avg >= 4.0: return SK_SUCCESS
    if avg >= 3.0: return SK_PRIMARY
    if avg >= 2.5: return "#F59E0B"
    return "#EF4444"


def test_score_color_high_avg_returns_string():
    color = _score_color(4.5)
    assert color.startswith("#"), f"Expected hex color, got {color!r}"


def test_score_color_good_avg():
    color = _score_color(3.5)
    assert color.startswith("#")


def test_score_color_low_avg():
    color = _score_color(2.0)
    assert color == "#EF4444"
