"""
Side-by-side proof: Pillow's own text layout vs HarfBuzz-shaped rendering.

    python demo.py path/to/ThaiFont.ttf

Writes comparison.png. On a Pillow built without libraqm, the left column loses
tone marks that the right column keeps.
"""
import sys

from PIL import Image, ImageDraw, ImageFont

import thai_text_render as ttr

# Each of these carries a vowel sign AND a tone mark on the same base
# consonant, which is what an unshaped renderer drops.
SAMPLES = [
    ("เนื่องจาก", "เนืองจาก"),
    ("ราคานี้", "ราคานี"),
    ("ตั้งใจ", "ตังใจ"),
    ("เพิ่มขึ้น", "เพิมขึน"),
]

FONT = sys.argv[1] if len(sys.argv) > 1 else "fonts/Kanit-SemiBold.ttf"
SIZE = 58
ROW = SIZE + 26
W, H = 1240, 130 + ROW * len(SAMPLES)

img = Image.new("RGBA", (W, H), (18, 18, 22, 255))
d = ImageDraw.Draw(img)
label = ImageFont.load_default()

LEFT, RIGHT = 60, 700

d.text((LEFT, 40), "ImageDraw.text   (no shaping)", fill=(235, 95, 95), font=label)
d.text((RIGHT, 40), "thai_text_render.draw   (HarfBuzz GPOS)", fill=(95, 215, 145), font=label)
d.line([(RIGHT - 40, 30), (RIGHT - 40, H - 30)], fill=(60, 60, 70), width=1)

pil_font = ImageFont.truetype(FONT, SIZE)
y = 90
for correct, _wrong in SAMPLES:
    d.text((LEFT, y), correct, font=pil_font, fill=(255, 255, 255))
    ttr.draw(img, correct, RIGHT, y, FONT, SIZE, color=(255, 255, 255), anchor="lt")
    y += ROW

img.convert("RGB").save("comparison.png")
print("wrote comparison.png")
have_raqm = getattr(ImageFont.core, "HAVE_RAQM", "unknown")
print("libraqm in this Pillow build:", have_raqm)
if have_raqm is True:
    print("note: this build CAN shape, so both columns will look correct.")
