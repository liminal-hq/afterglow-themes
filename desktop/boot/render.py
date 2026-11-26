#!/usr/bin/env python3
# Render the Afterglow boot logo master to the exact 16-colour bitmap the ReactOS kernel boot screen loads, plus previews.
# Usage: render.py OUT_DIR
#
# boot-logo.svg (1656 x 1464) becomes a 414 x 366 bitmap in the 16 colours of palette.json. rsvg-convert draws the master at its
# own size, a box filter averages every 4 x 4 block into one pixel, and each pixel then takes the palette entry nearest to it in
# six-bit space (the VGA DAC keeps the top six bits of each channel, so that is the space the screen is seen in): the smallest
# squared distance between six-bit values wins, and a tie goes to the lower index. There is no dither: the master is drawn in flat
# palette colours, so only its edges and text need a nearer colour, and dithering would also swell the RLE4 runs past the slot.
# The progress bar's box is then forced to index 0, because the kernel draws the bar frame and fill there. Nothing in the output
# depends on the date or the machine.
#
# It writes afterglow-logo-4bit.bmp (4-bit, uncompressed), afterglow-logo-rle4.bmp (the same bitmap RLE4-compressed bottom-up,
# like the bitmap resource it replaces: BITMAPINFOHEADER, 16-entry palette, then the runs), afterglow-logo-1x.png and
# afterglow-logo-2x.png (through the colours the screen shows), and afterglow-logo-report.txt (the sizes against the slot).
# Needs rsvg-convert and Pillow.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
import io
import json
import os
import struct
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MASTER = "boot-logo.svg"
SCALE = 4


def load_palette():
	with open(os.path.join(HERE, "palette.json"), encoding="utf-8") as f:
		spec = json.load(f)
	colours = [tuple(int(e["rgb"][i : i + 2], 16) for i in (1, 3, 5)) for e in spec["entries"]]
	assert [e["index"] for e in spec["entries"]] == list(range(16))
	assert all(c & 3 == 0 for rgb in colours for c in rgb), "palette entries must be exact in six bits"
	box = spec["progressBox"]
	return spec, colours, (box["x"], box["y"], box["x"] + box["width"], box["y"] + box["height"])


def rasterise(width, height):
	"""The master at its own size as 8-bit RGB. Fails when any pixel is see-through: a bitmap has nothing to blend it with."""
	try:
		result = subprocess.run(
			["rsvg-convert", "--format", "png", "--width", str(width), "--height", str(height), os.path.join(HERE, MASTER)],
			check=True,
			stdout=subprocess.PIPE,
		)
	except FileNotFoundError:
		sys.exit("render.py: rsvg-convert is required (the librsvg2-bin package)")
	image = Image.open(io.BytesIO(result.stdout)).convert("RGBA")
	if image.getchannel("A").getextrema() != (255, 255):
		sys.exit(f"render.py: {MASTER} has transparent pixels, and the boot logo cannot")
	return image.convert("RGB")


def quantise(image, colours, box):
	"""Palette indices, row by row, for an RGB image."""
	width, height = image.size
	six = [tuple(c >> 2 for c in rgb) for rgb in colours]
	cache = {}

	def nearest(rgb):
		key = tuple(c >> 2 for c in rgb)
		if key not in cache:
			cache[key] = min(range(16), key=lambda i: (sum((a - b) ** 2 for a, b in zip(key, six[i])), i))
		return cache[key]

	pixels = image.load()
	rows = []
	for y in range(height):
		row = []
		for x in range(width):
			row.append(0 if box[0] <= x < box[2] and box[1] <= y < box[3] else nearest(pixels[x, y]))
		rows.append(row)
	return rows


def palette_bytes(colours):
	return b"".join(bytes((b, g, r, 0)) for r, g, b in colours)


def bmp(width, height, colours, bits, compression):
	info = struct.pack("<IiiHHIIiiII", 40, width, height, 1, 4, compression, len(bits), 0, 0, 16, 0)
	dib = info + palette_bytes(colours) + bits
	return b"BM" + struct.pack("<IHHI", 14 + len(dib), 0, 0, 14 + 40 + 64) + dib


def raw4(rows):
	"""Uncompressed 4-bit rows, bottom-up, two pixels a byte and padded to four bytes."""
	out = bytearray()
	for row in reversed(rows):
		packed = bytearray()
		for x in range(0, len(row), 2):
			packed.append((row[x] << 4) | (row[x + 1] if x + 1 < len(row) else 0))
		packed += b"\0" * (-len(packed) % 4)
		out += packed
	return bytes(out)


def rle4(rows):
	"""Encoded-mode runs only (count, colour pair), bottom-up, an end of line after each row and an end of bitmap at the last."""
	out = bytearray()
	for row in reversed(rows):
		x = 0
		while x < len(row):
			colour, run = row[x], 1
			while x + run < len(row) and row[x + run] == colour and run < 255:
				run += 1
			out += bytes((run, (colour << 4) | colour))
			x += run
		out += b"\0\0"
	out[-2:] = b"\0\1"
	return bytes(out)


def rle4_decode(bits, width, height):
	"""The pixels an RLE4 stream draws, for the round-trip check; handles encoded and absolute runs and the escapes."""
	rows = [[0] * width for _ in range(height)]
	x, y, i = 0, height - 1, 0
	while i < len(bits):
		count, value = bits[i], bits[i + 1]
		i += 2
		if count:
			for k in range(count):
				if 0 <= y < height and x < width:
					rows[y][x] = (value >> 4) if k % 2 == 0 else (value & 15)
				x += 1
		elif value == 0:
			x, y = 0, y - 1
		elif value == 1:
			break
		elif value == 2:
			x, y, i = x + bits[i], y - bits[i + 1], i + 2
		else:
			for k in range(value):
				byte = bits[i + k // 2]
				if 0 <= y < height and x < width:
					rows[y][x] = (byte >> 4) if k % 2 == 0 else (byte & 15)
				x += 1
			i += ((value + 1) // 2 + 1) & ~1
	return rows


def display(colours):
	"""The colours the DAC shows: six bits expanded back to eight."""
	return [tuple((c >> 2 << 2) | (c >> 4) for c in rgb) for rgb in colours]


def render(out_dir):
	spec, colours, box = load_palette()
	width, height = spec["size"]
	os.makedirs(out_dir, exist_ok=True)
	rows = quantise(rasterise(width * SCALE, height * SCALE).resize((width, height), Image.BOX), colours, box)
	compressed = rle4(rows)
	assert rle4_decode(compressed, width, height) == rows, "the RLE4 stream does not decode to the bitmap"
	files = {
		"afterglow-logo-4bit.bmp": bmp(width, height, colours, raw4(rows), 0),
		"afterglow-logo-rle4.bmp": bmp(width, height, colours, compressed, 2),
	}
	shown = Image.new("RGB", (width, height))
	shown.putdata([display(colours)[i] for row in rows for i in row])
	shown.save(os.path.join(out_dir, "afterglow-logo-1x.png"), optimize=False)
	shown.resize((width * 2, height * 2), Image.NEAREST).save(os.path.join(out_dir, "afterglow-logo-2x.png"), optimize=False)
	for name, data in files.items():
		with open(os.path.join(out_dir, name), "wb") as f:
			f.write(data)
	dib = len(files["afterglow-logo-rle4.bmp"]) - 14
	used = sorted({i for row in rows for i in row})
	report = (
		f"canvas {width} x {height}\n"
		f"palette indices used: {' '.join(map(str, used))}\n"
		f"RLE4 pixel data: {len(compressed)} bytes\n"
		f"RLE4 DIB (header, palette and runs): {dib} bytes, slot {spec['slot']}, {spec['slot'] - dib} to spare\n"
		f"4-bit uncompressed file: {len(files['afterglow-logo-4bit.bmp'])} bytes\n"
	)
	with open(os.path.join(out_dir, "afterglow-logo-report.txt"), "w", encoding="utf-8") as f:
		f.write(report)
	if dib > spec["slot"]:
		sys.exit(f"render.py: the RLE4 DIB is {dib} bytes and the slot holds {spec['slot']}")
	return report


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit("usage: render.py OUT_DIR")
	print(render(sys.argv[1]), end="")
