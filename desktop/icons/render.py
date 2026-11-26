#!/usr/bin/env python3
# Render the Afterglow icon masters to PNG at 16, 24, 32 and 48 px and pack one .ico per icon with all four frames.
# Usage: render.py OUT_DIR
#
# Writes OUT_DIR/png/ID-SIZE.png, OUT_DIR/ico/ID.ico and OUT_DIR/afterglow-icons-sheet.png (the generator's contact sheet). Each size
# draws from the master built for it: 48 and 32 from svg/ID.svg (32 is the 48 master scaled), 24 from svg/24/ID.svg, and 16 from the
# hinted redraw svg/ID-16.svg where one exists, otherwise from svg/16/ID.svg. An .ico holds four uncompressed 32-bit BGRA DIB frames
# (alpha in the pixels, an all-zero AND mask), the classic layout every Windows since 95 reads, ReactOS included; no PNG-compressed
# frames, which older icon loaders reject. The ico bytes carry no dates and depend only on the rendered pixels, so the same masters
# and the same rsvg-convert give the same files; the PNGs and the sheet are written as rsvg-convert makes them. Needs rsvg-convert and Pillow.
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
SVG = os.path.join(HERE, "svg")
SIZES = (16, 24, 32, 48)


def ids():
	"""Every icon id: the 48 px masters directly in svg/, without the hinted -16 redraws."""
	return sorted(f[:-4] for f in os.listdir(SVG) if f.endswith(".svg") and not f.endswith("-16.svg"))


def master(icon, size):
	"""The SVG that draws `icon` at `size`."""
	if size == 24:
		return os.path.join(SVG, "24", icon + ".svg")
	if size == 16:
		hinted = os.path.join(SVG, icon + "-16.svg")
		return hinted if os.path.exists(hinted) else os.path.join(SVG, "16", icon + ".svg")
	return os.path.join(SVG, icon + ".svg")


def rsvg(path, width, height):
	try:
		result = subprocess.run(
			["rsvg-convert", "--format", "png", "--width", str(width), "--height", str(height), path],
			check=True,
			stdout=subprocess.PIPE,
		)
	except FileNotFoundError:
		sys.exit("render.py: rsvg-convert is required (the librsvg2-bin package)")
	return result.stdout


def dib(image):
	"""A 32-bit BI_RGB icon frame: a BITMAPINFOHEADER of twice the height, bottom-up BGRA rows, then a zero AND mask."""
	width, height = image.size
	rgba = image.tobytes()
	rows = []
	for y in range(height - 1, -1, -1):
		row = rgba[y * width * 4 : (y + 1) * width * 4]
		rows.append(b"".join(row[x + 2 : x + 3] + row[x + 1 : x + 2] + row[x : x + 1] + row[x + 3 : x + 4] for x in range(0, len(row), 4)))
	pixels = b"".join(rows)
	mask = b"\0" * ((-(-width // 32) * 4) * height)
	header = struct.pack("<IiiHHIIiiII", 40, width, height * 2, 1, 32, 0, len(pixels) + len(mask), 0, 0, 0, 0)
	return header + pixels + mask


def ico(frames):
	"""An .ico of the given RGBA images, smallest first."""
	blobs = [dib(image) for image in frames]
	out = [struct.pack("<HHH", 0, 1, len(frames))]
	offset = 6 + 16 * len(frames)
	for image, blob in zip(frames, blobs):
		out.append(struct.pack("<BBBBHHII", image.width, image.height, 0, 0, 1, 32, len(blob), offset))
		offset += len(blob)
	return b"".join(out) + b"".join(blobs)


def render(out_dir):
	png_dir = os.path.join(out_dir, "png")
	ico_dir = os.path.join(out_dir, "ico")
	os.makedirs(png_dir, exist_ok=True)
	os.makedirs(ico_dir, exist_ok=True)
	for icon in ids():
		frames = []
		for size in SIZES:
			data = rsvg(master(icon, size), size, size)
			with open(os.path.join(png_dir, f"{icon}-{size}.png"), "wb") as f:
				f.write(data)
			image = Image.open(io.BytesIO(data)).convert("RGBA")
			if image.size != (size, size):
				sys.exit(f"render.py: {icon} at {size} came out {image.size[0]} x {image.size[1]}")
			frames.append(image)
		with open(os.path.join(ico_dir, icon + ".ico"), "wb") as f:
			f.write(ico(frames))
	with open(os.path.join(out_dir, "afterglow-icons-sheet.png"), "wb") as f:
		f.write(subprocess.run(["rsvg-convert", "--format", "png", os.path.join(HERE, "sheet.svg")], check=True, stdout=subprocess.PIPE).stdout)


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit("usage: render.py OUT_DIR")
	render(sys.argv[1])
