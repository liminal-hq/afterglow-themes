#!/usr/bin/env python3
# Render the Afterglow icon masters to PNG at 16, 32 and 48 px and pack one .ico per icon with those three frames.
# Usage: render.py OUT_DIR
#
# Writes OUT_DIR/png/ID-SIZE.png, OUT_DIR/ico/ID.ico, the shortcut arrow as png/arrow-SIZE.png and ico/arrow.ico, the contact sheet
# afterglow-icons-sheet.png and a preview of the arrow over six icons, afterglow-arrow-preview.png. ReactOS never asks for 24 px, so there
# is no 24 px frame. Each size draws from the master built for it: 48 from svg/ID.svg, 32 from svg/32/ID.svg (the 32 px profile, still a
# 48 viewBox), and 16 from the hinted redraw svg/ID-16.svg where one exists, otherwise from svg/16/ID.svg. The arrow draws from
# arrow/arrow-48.svg, arrow-32.svg and the pixel-drawn arrow-16-hinted.svg. The soft shadows are blurs in the masters, so each size bakes
# its own when rsvg-convert rasterises it. An .ico holds three uncompressed 32-bit BGRA DIB frames (alpha in the pixels, an all-zero AND
# mask), the classic layout every Windows since 95 reads, ReactOS included; no PNG-compressed frames, which older icon loaders reject. The
# ico bytes carry no dates and depend only on the rendered pixels, so the same masters and the same rsvg-convert give the same files; the
# PNGs and the two preview images are written as rsvg-convert and Pillow make them. Needs rsvg-convert and Pillow.
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
ARROW = os.path.join(HERE, "arrow")
SIZES = (16, 32, 48)


def ids():
	"""Every icon id: the 48 px masters directly in svg/, without the hinted -16 redraws."""
	return sorted(f[:-4] for f in os.listdir(SVG) if f.endswith(".svg") and not f.endswith("-16.svg"))


def master(icon, size):
	"""The SVG that draws `icon` at `size`."""
	if icon == "arrow":
		return os.path.join(ARROW, "arrow-16-hinted.svg" if size == 16 else f"arrow-{size}.svg")
	if size == 32:
		return os.path.join(SVG, "32", icon + ".svg")
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
	pixels = {}
	for icon in ids() + ["arrow"]:
		frames = []
		for size in SIZES:
			data = rsvg(master(icon, size), size, size)
			with open(os.path.join(png_dir, f"{icon}-{size}.png"), "wb") as f:
				f.write(data)
			image = Image.open(io.BytesIO(data)).convert("RGBA")
			if image.size != (size, size):
				sys.exit(f"render.py: {icon} at {size} came out {image.size[0]} x {image.size[1]}")
			frames.append(image)
			pixels[icon, size] = image
		with open(os.path.join(ico_dir, icon + ".ico"), "wb") as f:
			f.write(ico(frames))
	with open(os.path.join(out_dir, "afterglow-icons-sheet.png"), "wb") as f:
		f.write(subprocess.run(["rsvg-convert", "--format", "png", os.path.join(HERE, "sheet.svg")], check=True, stdout=subprocess.PIPE).stdout)
	arrow_preview(pixels).save(os.path.join(out_dir, "afterglow-arrow-preview.png"), optimize=False)


def arrow_preview(pixels):
	"""The arrow over six icons at 48, 32 and 16 px on the desktop and on cream, composited the way ReactOS does (at 0, 0, same size), at 3x."""
	shown = ("folder", "doc", "mycomputer", "hdd", "recycle", "program")
	grounds = ((9, 14, 42), (212, 208, 200))
	pad, scale = 8, 3
	width = pad + len(shown) * (48 + 32 + 16 + 3 * pad)
	sheet = Image.new("RGBA", (width, 2 * (48 + 2 * pad)), (0, 0, 0, 255))
	for row, ground in enumerate(grounds):
		y = row * (48 + 2 * pad)
		sheet.paste(Image.new("RGBA", (width, 48 + 2 * pad), ground + (255,)), (0, y))
		x = pad
		for icon in shown:
			for size in SIZES[::-1]:
				frame = pixels[icon, size].copy()
				frame.alpha_composite(pixels["arrow", size])
				sheet.alpha_composite(frame, (x, y + pad + (48 - size)))
				x += size + pad
	return sheet.resize((sheet.width * scale, sheet.height * scale), Image.NEAREST)


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit("usage: render.py OUT_DIR")
	render(sys.argv[1])
