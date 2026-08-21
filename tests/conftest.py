"""Locate a Thai OpenType font to render the tests against."""
import os
import shutil
import subprocess

import pytest

# Any of these is enough; the tests only need real Thai glyphs with GPOS marks.
CANDIDATES = [
    r"C:\Users\chonl\AppData\Local\Microsoft\Windows\Fonts\Kanit-SemiBold.ttf",
    r"C:\Windows\Fonts\tahoma.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansThai-Regular.ttf",
]


def _resolve():
    env = os.environ.get("THAI_FONT") or os.environ.get("FONT")
    if env and os.path.exists(env):
        return env
    if shutil.which("fc-match"):
        out = subprocess.run(
            ["fc-match", "-f", "%{file}", "Noto Sans Thai"],
            capture_output=True, text=True,
        ).stdout.strip()
        if out and os.path.exists(out):
            return out
    for path in CANDIDATES:
        if os.path.exists(path):
            return path
    return None


@pytest.fixture(scope="session")
def font():
    path = _resolve()
    if path is None:
        pytest.skip("no Thai font found; set THAI_FONT to a .ttf path")
    return path
