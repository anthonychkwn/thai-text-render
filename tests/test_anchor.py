"""Anchor placement must describe the text, not the glow halo around it."""
import numpy as np
import pytest
from PIL import Image

import thai_text_render as ttr

TEXT = "เนื่องจาก"
SIZE = 48


def ink_bbox(canvas):
    """(left, top, right, bottom) of every pixel the text actually lit up."""
    lum = np.array(canvas)[:, :, :3].max(axis=2)
    ys, xs = np.nonzero(lum > 40)
    assert xs.size, "nothing was drawn"
    return xs.min(), ys.min(), xs.max(), ys.max()


def render(font, **kwargs):
    canvas = Image.new("RGBA", (700, 400), (0, 0, 0, 255))
    ttr.draw(canvas, TEXT, 300, 200, font, SIZE, color=(255, 255, 255), **kwargs)
    return canvas


@pytest.mark.parametrize("anchor", ["lt", "mm", "rb"])
def test_glow_does_not_move_the_text(font, anchor):
    plain = ink_bbox(render(font, anchor=anchor))
    glowing = ink_bbox(render(font, anchor=anchor, glow=8))
    # The halo is a wide soft blur, so compare where the bright glyphs sit.
    assert abs(glowing[0] - plain[0]) <= 1
    assert abs(glowing[1] - plain[1]) <= 1


def test_anchor_places_the_point_where_it_says(font):
    w, h = ttr.measure(TEXT, font, SIZE)
    left, top, right, bottom = ink_bbox(render(font, anchor="lt"))
    # The layer carries a little internal padding, so the ink sits just inside
    # the anchored box rather than exactly on its corner.
    assert 300 <= left <= 300 + w
    assert 200 <= top <= 200 + h

    left, top, right, bottom = ink_bbox(render(font, anchor="rb"))
    assert 300 - w <= right <= 300
    assert 200 - h <= bottom <= 200


def test_measure_covers_the_ink(font):
    w, h = ttr.measure(TEXT, font, SIZE)
    left, top, right, bottom = ink_bbox(render(font, anchor="lt"))
    assert right - left <= w
    assert bottom - top <= h
