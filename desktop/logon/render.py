#!/usr/bin/env python3
# Render the Afterglow logon banner and bar masters to the exact bitmaps msgina.dll loads, plus PNG previews for the docs.
# Usage: render.py OUT_DIR
#
# banner-a.svg (1652 x 288) becomes afterglow-banner.bmp, 413 x 72, and bar.svg (1652 x 20) becomes afterglow-bar.bmp, 413 x 5:
# 24-bit uncompressed BMPs, bottom-up, like the msgina.dll resources IDI_ROSLOGO and IDI_BAR they replace. The masters are four
# times the target, so rsvg-convert draws each at 1652 wide and a box filter averages every 4 x 4 block into one pixel. The BMP
# header carries no dates, resolution or colour profile, so the same masters give the same bytes. The previews are PNGs at 2x
# and 4x, and afterglow-logon-preview.png shows the banner over the bar at 2x. Needs rsvg-convert and Pillow.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
import io
import os
import struct
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SCALE = 4
# name, master, width and height of the bitmap msgina.dll expects
TARGETS = (
	("banner", "banner-a.svg", 413, 72),
	("bar", "bar.svg", 413, 5),
)


def rasterise(master, width, height):
	"""The master at its own size as 8-bit RGB. Fails when any pixel is see-through: a BMP has nothing to blend it with."""
	try:
		result = subprocess.run(
			["rsvg-convert", "--format", "png", "--width", str(width), "--height", str(height), os.path.join(HERE, master)],
			check=True,
			stdout=subprocess.PIPE,
		)
	except FileNotFoundError:
		sys.exit("render.py: rsvg-convert is required (the librsvg2-bin package)")
	image = Image.open(io.BytesIO(result.stdout)).convert("RGBA")
	if image.getchannel("A").getextrema() != (255, 255):
		sys.exit(f"render.py: {master} has transparent pixels, and a logon bitmap cannot")
	return image.convert("RGB")


def bmp24(image):
	"""A 24-bit BI_RGB BMP, rows bottom-up and padded to four bytes, with a zeroed pixel density and no colour table."""
	width, height = image.size
	pad = b"\0" * (-width * 3 % 4)
	pixels = image.tobytes()
	rows = []
	for y in range(height - 1, -1, -1):
		row = pixels[y * width * 3 : (y + 1) * width * 3]
		rows.append(b"".join(row[x : x + 3][::-1] for x in range(0, len(row), 3)) + pad)
	data = b"".join(rows)
	header = struct.pack("<2sIHHI", b"BM", 14 + 40 + len(data), 0, 0, 14 + 40)
	info = struct.pack("<IiiHHIIiiII", 40, width, height, 1, 24, 0, len(data), 0, 0, 0, 0)
	return header + info + data


def render(out_dir):
	os.makedirs(out_dir, exist_ok=True)
	sheet = {}
	for name, master, width, height in TARGETS:
		big = rasterise(master, width * SCALE, height * SCALE)
		small = big.resize((width, height), Image.BOX)
		with open(os.path.join(out_dir, f"afterglow-{name}.bmp"), "wb") as f:
			f.write(bmp24(small))
		half = big.resize((width * 2, height * 2), Image.BOX)
		half.save(os.path.join(out_dir, f"afterglow-{name}-2x.png"), optimize=False)
		big.save(os.path.join(out_dir, f"afterglow-{name}-4x.png"), optimize=False)
		sheet[name] = half
	preview = Image.new("RGB", (sheet["banner"].width, sheet["banner"].height + sheet["bar"].height))
	preview.paste(sheet["banner"], (0, 0))
	preview.paste(sheet["bar"], (0, sheet["banner"].height))
	preview.save(os.path.join(out_dir, "afterglow-logon-preview.png"), optimize=False)


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit("usage: render.py OUT_DIR")
	render(sys.argv[1])
