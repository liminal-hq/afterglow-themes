#!/usr/bin/env python3
# Render the Afterglow Start orb and Start menu banner masters to the exact resources ReactOS explorer.exe loads, plus PNG previews.
# Usage: render.py OUT_DIR
#
# orb.svg (200 x 160) becomes start-orb.dib, the 25 x 20 32-bit image with straight alpha that explorer.exe holds as bitmap 143, and
# banner.svg (168 x 1864) becomes start-banner.dib, the 21 x 233 24-bit image that is bitmap 158. Both are resource-ready DIBs: a
# BITMAPINFOHEADER and the bits, with no file header, rows bottom-up. The masters are eight times the target, so rsvg-convert draws
# each at its own size and every 8 x 8 block is averaged into one pixel in integer arithmetic (for the orb, weighted by alpha so the
# edge keeps its colour). The same masters give the same bytes. Needs rsvg-convert and Pillow.
#
# explorer.exe draws bitmap 143 with ImageList_LoadImage(cx = 0), so each cell is 20 x 20 (the image height) and only columns 0 to 19
# show, for every Start button state: the disc keeps a transparent margin of at least 1 px inside that square, and columns 20 to 24
# stay clear. The renderer stops if any of that is not so. Bitmap 158 is the strip on the left of the Start menu: its biSizeImage is
# 14,914, the stock value, which is the 14,912 bytes of rows plus two trailing bytes.
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
SCALE = 8
ORB = (25, 20)
CELL = 20  # the part of the orb that explorer shows
BANNER = (21, 233)
BANNER_SIZE_IMAGE = 14914
GOLD = (0xFF, 0xB1, 0x50)  # the Start button's gold, behind the orb in the preview
STAGE = (0x0C, 0x0C, 0x10)


def rasterise(master, width, height):
	"""The master at its own size as 8-bit RGBA."""
	try:
		result = subprocess.run(
			["rsvg-convert", "--format", "png", "--width", str(width), "--height", str(height), os.path.join(HERE, master)],
			check=True,
			stdout=subprocess.PIPE,
		)
	except FileNotFoundError:
		sys.exit("render.py: rsvg-convert is required (the librsvg2-bin package)")
	return Image.open(io.BytesIO(result.stdout)).convert("RGBA")


def reduce_straight(big, width, height):
	"""Average each SCALE x SCALE block to one RGBA pixel with straight alpha: colour weighted by alpha, alpha averaged."""
	src = big.tobytes()
	stride = big.width * 4
	out = bytearray()
	area = SCALE * SCALE
	for y in range(height):
		for x in range(width):
			sa = sr = sg = sb = 0
			for dy in range(SCALE):
				base = (y * SCALE + dy) * stride + x * SCALE * 4
				for dx in range(SCALE):
					r, g, b, a = src[base + dx * 4 : base + dx * 4 + 4]
					sa += a
					sr += r * a
					sg += g * a
					sb += b * a
			if sa == 0:
				out += b"\0\0\0\0"
			else:
				out += bytes(((sr + sa // 2) // sa, (sg + sa // 2) // sa, (sb + sa // 2) // sa, (sa + area // 2) // area))
	return Image.frombytes("RGBA", (width, height), bytes(out))


def reduce_opaque(big, width, height):
	"""Average each SCALE x SCALE block to one RGB pixel. Fails when any pixel is see-through: a 24-bit image has no alpha."""
	if big.getchannel("A").getextrema() != (255, 255):
		sys.exit("render.py: banner.svg has transparent pixels, and the 24-bit banner cannot")
	src = big.convert("RGB").tobytes()
	stride = big.width * 3
	out = bytearray()
	area = SCALE * SCALE
	for y in range(height):
		for x in range(width):
			sums = [0, 0, 0]
			for dy in range(SCALE):
				base = (y * SCALE + dy) * stride + x * SCALE * 3
				row = src[base : base + SCALE * 3]
				for c in range(3):
					sums[c] += sum(row[c::3])
			out += bytes((s + area // 2) // area for s in sums)
	return Image.frombytes("RGB", (width, height), bytes(out))


def check_orb(orb):
	"""The disc must sit inside explorer's 20 x 20 cell with a 1 px transparent margin all round, and clear of columns 20 to 24."""
	alpha = orb.getchannel("A")
	for y in range(orb.height):
		for x in range(orb.width):
			inside = 1 <= x <= CELL - 2 and 1 <= y <= CELL - 2
			if not inside and alpha.getpixel((x, y)) != 0:
				sys.exit(f"render.py: the orb has ink at {x},{y}, outside the 18 x 18 square explorer shows with a 1 px margin")
	if alpha.getbbox() is None:
		sys.exit("render.py: the orb is empty")


def dib32(image):
	"""A 32-bit BI_RGB DIB with straight alpha, rows bottom-up, as the resource holds it (BGRA)."""
	width, height = image.size
	pixels = image.tobytes()
	rows = []
	for y in range(height - 1, -1, -1):
		row = pixels[y * width * 4 : (y + 1) * width * 4]
		rows.append(b"".join(bytes((row[i + 2], row[i + 1], row[i], row[i + 3])) for i in range(0, len(row), 4)))
	bits = b"".join(rows)
	return struct.pack("<IiiHHIIiiII", 40, width, height, 1, 32, 0, len(bits), 3780, 3780, 0, 0) + bits


def dib24(image, size_image):
	"""A 24-bit BI_RGB DIB, rows bottom-up and padded to four bytes, biSizeImage as the stock resource states it."""
	width, height = image.size
	pad = b"\0" * (-width * 3 % 4)
	pixels = image.tobytes()
	rows = []
	for y in range(height - 1, -1, -1):
		row = pixels[y * width * 3 : (y + 1) * width * 3]
		rows.append(b"".join(row[x : x + 3][::-1] for x in range(0, len(row), 3)) + pad)
	bits = b"".join(rows)
	bits += b"\0" * (size_image - len(bits))  # the stock resource carries 2 trailing bytes
	return struct.pack("<IiiHHIIiiII", 40, width, height, 1, 24, 0, size_image, 0, 0, 0, 0) + bits


def preview(orb, banner):
	"""The orb at 10x on the Start button's gold (as it sits in the button) beside the banner at 3x, on a dark stage."""
	glass = Image.new("RGBA", ORB, GOLD + (255,))
	glass.alpha_composite(orb)
	orb10 = glass.resize((ORB[0] * 10, ORB[1] * 10), Image.NEAREST).convert("RGB")
	cell10 = orb10.crop((0, 0, CELL * 10, ORB[1] * 10))
	banner3 = banner.resize((BANNER[0] * 3, BANNER[1] * 3), Image.NEAREST)
	pad = 16
	sheet = Image.new("RGB", (pad * 3 + cell10.width + banner3.width, pad * 2 + banner3.height), STAGE)
	sheet.paste(cell10, (pad, pad))
	sheet.paste(banner3, (pad * 2 + cell10.width, pad))
	return sheet


def render(out_dir):
	os.makedirs(out_dir, exist_ok=True)
	orb = reduce_straight(rasterise("orb.svg", ORB[0] * SCALE, ORB[1] * SCALE), *ORB)
	check_orb(orb)
	banner = reduce_opaque(rasterise("banner.svg", BANNER[0] * SCALE, BANNER[1] * SCALE), *BANNER)
	with open(os.path.join(out_dir, "start-orb.dib"), "wb") as f:
		f.write(dib32(orb))
	with open(os.path.join(out_dir, "start-banner.dib"), "wb") as f:
		f.write(dib24(banner, BANNER_SIZE_IMAGE))
	orb.save(os.path.join(out_dir, "start-orb.png"), optimize=False)
	banner.save(os.path.join(out_dir, "start-banner.png"), optimize=False)
	preview(orb, banner).save(os.path.join(out_dir, "afterglow-start-preview.png"), optimize=False)


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit("usage: render.py OUT_DIR")
	render(sys.argv[1])
