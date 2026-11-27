#!/usr/bin/env python3
# Render the Afterglow card masters to the bitmaps cards.dll holds, plus a preview of the Solitaire table on the proposed dusk felt.
# Usage: render.py OUT_DIR
#
# Each master is drawn by rsvg-convert at four times its bitmap and a box filter averages every 4 x 4 block into one pixel, then it is
# written as a 24-bit uncompressed bottom-up BMP with no dates, resolution or colour profile: card-back-sunset.bmp (cards.dll 54),
# card-x.bmp (67) and card-o.bmp (68), all 72 x 112. The stock bitmaps are 8-bit; cardlib copies each one into a screen-compatible bitmap
# with BitBlt, so a 24-bit bitmap of the same size draws the same way (it is larger, so the patch places it in a new section, as the icon
# patches do). afterglow-cards-preview.png shows them at 2x as cardlib draws them: the black border it paints over each card's outer ring,
# the corner pixels left out, and the empty foundation piles as cardlib's CreateSinkBmp draws them from the felt colour. It depends only on
# the masters (the stock card faces are not part of it). Needs rsvg-convert and Pillow.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
import io
import os
import struct
import subprocess
import sys

from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SCALE = 4
WIDTH, HEIGHT = 72, 112
TARGETS = (("card-back-sunset", "card-back-sunset.svg"), ("card-x", "card-x.svg"), ("card-o", "card-o.svg"))
FELT = (0x1F, 0x25, 0x54)  # gen_cards.py's FELT, the dusk sky's deepest tone


def rasterise(path):
	"""The master at 4x as 8-bit RGB. Fails when any pixel is see-through: a BMP has nothing to blend it with."""
	try:
		result = subprocess.run(["rsvg-convert", "--format", "png", "--width", str(WIDTH * SCALE), "--height", str(HEIGHT * SCALE), path], check=True,
			stdout=subprocess.PIPE)
	except FileNotFoundError:
		sys.exit("render.py: rsvg-convert is required (the librsvg2-bin package)")
	image = Image.open(io.BytesIO(result.stdout)).convert("RGBA")
	if image.getchannel("A").getextrema() != (255, 255):
		sys.exit(f"render.py: {os.path.basename(path)} has transparent pixels, and a card bitmap cannot")
	return image.convert("RGB").resize((WIDTH, HEIGHT), Image.BOX)


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


def scaled(colour, target, ratio):
	return tuple(round(channel + (goal - channel) * ratio) for channel, goal in zip(colour, target))


def as_cardlib_draws(card, felt):
	"""A card as cardlib puts it on the table: its black border over the outer ring, cut at the corners, and the corner pixels left as felt."""
	picture = card.copy()
	draw = ImageDraw.Draw(picture)
	right, bottom = WIDTH - 1, HEIGHT - 1
	draw.line([(2, 0), (right - 2, 0), (right, 2), (right, bottom - 2), (right - 2, bottom), (2, bottom), (0, bottom - 2), (0, 2), (2, 0)], fill=(0, 0, 0))
	for x, y in ((0, 0), (1, 0), (0, 1), (right, 0), (right - 1, 0), (right, 1), (0, bottom), (1, bottom), (0, bottom - 1), (right, bottom),
			(right - 1, bottom), (right, bottom - 1)):
		picture.putpixel((x, y), felt)
	return picture


def sink(felt):
	"""cardlib's empty pile (CreateSinkBmp): a checker of the felt and a step toward white, with a shadow rim, from the felt colour."""
	light = scaled(felt, (255, 255, 255), 0.2)
	shadow, shadow_soft = scaled(felt, (0, 0, 0), 0.4), scaled(felt, (0, 0, 0), 0.2)
	picture = Image.new("RGB", (WIDTH, HEIGHT), felt)
	for y in range(2, HEIGHT - 2):
		for x in range(2, WIDTH - 2):
			if (x + y) % 2:
				picture.putpixel((x, y), light)
	picture.putpixel((2, 2), felt)
	draw = ImageDraw.Draw(picture)
	right, bottom = WIDTH - 1, HEIGHT - 1
	draw.line([(2, 0), (right - 2, 0), (right, 2)], fill=shadow)
	draw.line([(right, 2), (right, bottom - 2), (right - 2, bottom), (2, bottom), (0, bottom - 2)], fill=shadow_soft)
	draw.line([(0, bottom - 2), (0, 2), (2, 0)], fill=shadow)
	draw.line([(right - 1, 3), (right - 1, bottom - 1)], fill=light)
	draw.line([(right - 2, bottom - 1), (3, bottom - 1)], fill=light)
	return picture


def render(out_dir):
	os.makedirs(out_dir, exist_ok=True)
	images = {}
	for name, master in TARGETS:
		small = rasterise(os.path.join(HERE, master))
		with open(os.path.join(out_dir, f"{name}.bmp"), "wb") as handle:
			handle.write(bmp24(small))
		images[name] = small
	back = as_cardlib_draws(images["card-back-sunset"], FELT)
	gap = 16
	width = gap * 9 + WIDTH * 8  # the table, and a column at the right for the cross mark
	height = gap * 3 + HEIGHT * 2
	table = Image.new("RGB", (width, height), FELT)
	for offset in range(3, -1, -1):  # the deck: a few cards' edges showing under the top one
		table.paste(back, (gap + offset * 2, gap + offset))
	table.paste(as_cardlib_draws(images["card-o"], FELT), (gap * 2 + WIDTH, gap))
	for column in range(3, 7):
		table.paste(sink(FELT), (gap + column * (WIDTH + gap), gap))
	for column in range(7):  # the tableau's face-down cards, as cardlib stacks them
		for step in range(column + 1):
			table.paste(back, (gap + column * (WIDTH + gap), gap * 2 + HEIGHT + step * 3))
	table.paste(as_cardlib_draws(images["card-x"], FELT), (gap + 7 * (WIDTH + gap), gap))
	table.resize((width * 2, height * 2), Image.NEAREST).save(os.path.join(out_dir, "afterglow-cards-preview.png"), optimize=False)


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit("usage: render.py OUT_DIR")
	render(sys.argv[1])
