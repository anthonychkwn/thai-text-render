"""Edge cases that used to raise, clip, or leak instead of rendering."""
import numpy as np
import pytest
from PIL import Image

import thai_text_render as ttr

TEXT = "เนื่องจาก"
SIZE = 48


def alpha_of(layer):
    return np.array(layer)[:, :, 3]


@pytest.mark.parametrize("tracking", [-20, -40, -200])
def test_tight_tracking_neither_crashes_nor_clips(font, tracking):
    # Negative tracking overlaps the glyphs. Sizing the canvas from the summed
    # advances shrinks it faster than the ink shrinks, so the glyphs used to be
    # cut off, and past the point where the advances summed below zero the
    # canvas allocation raised outright.
    layer = ttr.make_layer(TEXT, font, SIZE, tracking=tracking)
    a = alpha_of(layer)
    assert a.max() > 0, "nothing was drawn"
    assert a[:, 0].max() == 0, "ink is clipped against the left edge"
    assert a[:, -1].max() == 0, "ink is clipped against the right edge"


def test_tight_tracking_keeps_the_glyphs_it_started_with(font):
    # Overlapping glyphs may merge, but tightening must not delete ink.
    loose = alpha_of(ttr.make_layer(TEXT, font, SIZE, tracking=0))
    tight = alpha_of(ttr.make_layer(TEXT, font, SIZE, tracking=-20))
    assert (tight > 40).sum() > (loose > 40).sum() * 0.5


def test_normal_tracking_is_unchanged(font):
    w, h = ttr.measure(TEXT, font, SIZE)
    assert w > 0 and h > 0
    a = alpha_of(ttr.make_layer(TEXT, font, SIZE))
    assert a[:, 0].max() == 0 and a[:, -1].max() == 0


@pytest.mark.parametrize("anchor", ["lx", "xm", "l", "", "mmm"])
def test_invalid_anchor_says_what_is_wrong(font, anchor):
    canvas = Image.new("RGBA", (400, 200), (0, 0, 0, 255))
    with pytest.raises(ValueError, match="anchor"):
        ttr.draw(canvas, TEXT, 100, 100, font, SIZE, anchor=anchor)


def test_clear_cache_releases_layers_and_redraws_identically(font):
    ttr.clear_cache()
    assert len(ttr._LAYER_CACHE) == 0
    before = ttr.make_layer(TEXT, font, SIZE).tobytes()
    assert len(ttr._LAYER_CACHE) == 1
    ttr.clear_cache()
    assert len(ttr._LAYER_CACHE) == 0
    assert ttr.make_layer(TEXT, font, SIZE).tobytes() == before


def test_empty_text_gives_a_blank_layer(font):
    # HarfBuzz reports glyph_positions as None, not [], for an empty buffer.
    layer = ttr.make_layer("", font, SIZE)
    assert layer.size[0] > 0 and layer.size[1] > 0
    assert alpha_of(layer).max() == 0


def test_a_blank_line_between_two_lines_is_allowed(font):
    # What a caption track produces for a paragraph break.
    spaced = ttr.measure("ก\n\nข", font, SIZE)
    tight = ttr.measure("ก\nข", font, SIZE)
    assert spaced[1] > tight[1]
