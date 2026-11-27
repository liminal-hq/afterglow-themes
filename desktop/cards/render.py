#!/usr/bin/env python3
# Render the Afterglow card masters to the bitmaps cards.dll holds, plus a preview of a Solitaire and a Spider table on the dusk felt.
# Usage: render.py OUT_DIR
#
# Each master is drawn by rsvg-convert at four times its bitmap and a box filter averages every 4 x 4 block into one pixel, then it is
# written as a 24-bit uncompressed bottom-up BMP with no dates, resolution or colour profile: card-back-sunset.bmp (cards.dll 54),
# card-x.bmp (67), card-o.bmp (68) and the faces from desktop/cards/faces, card-NN-<suit>-<rank>.bmp (1 to 52), card-53-free-cell.bmp and
# card-66-joker.bmp, all 72 x 112. The stock bitmaps are 8-bit; cardlib copies each one into a screen-compatible bitmap with BitBlt, so a
# 24-bit bitmap of the same size draws the same way (it is larger, so the patch places it in a new section, as the icon patches do).
# afterglow-cards-preview.png shows a Solitaire table and a two-suit Spider table at 2x as cardlib draws them: the black border it paints
# over each card's outer ring, the corner pixels left out, the rows stacked by the games' own offsets, and the empty foundation piles as
# cardlib's CreateSinkBmp draws them from the felt colour. It depends only on the masters. Needs rsvg-convert and Pillow.
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
FACES = os.path.join(HERE, "faces")
TARGETS = (("card-back-sunset", "card-back-sunset.svg"), ("card-x", "card-x.svg"), ("card-o", "card-o.svg")) + tuple(
	("card-" + name[:-4], os.path.join("faces", name)) for name in sorted(os.listdir(FACES)) if name.endswith(".svg"))
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


def corner_mask():
	"""The pixels cardlib draws of a card: all but the three cut pixels at each corner, where the felt or the card below shows."""
	mask = Image.new("L", (WIDTH, HEIGHT), 255)
	right, bottom = WIDTH - 1, HEIGHT - 1
	for x, y in ((0, 0), (1, 0), (0, 1), (right, 0), (right - 1, 0), (right, 1), (0, bottom), (1, bottom), (0, bottom - 1), (right, bottom),
			(right - 1, bottom), (right, bottom - 1)):
		mask.putpixel((x, y), 0)
	return mask


def face_key(rank_index, suit):
	"""The render name of a face: rank_index 0 (ace) to 12 (king), suit order clubs, diamonds, hearts, spades as in cards.dll."""
	suits = ("clubs", "diamonds", "hearts", "spades")
	names = ("ace", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "jack", "queen", "king")
	return "card-%02d-%s-%s" % (suits.index(suit) * 13 + rank_index + 1, suit, names[rank_index])


def place(table, card, x, y):
	table.paste(card, (x, y), corner_mask())


def solitaire_table(cards, felt):
	"""Solitaire mid-game as the game lays it out (solcreate.cpp): X_BORDER 20, Y_BORDERWITHFRAME 20, the empty deck's ring, the waste
	fanned by CS_DEFXOFF (12), the foundations over the four right-hand rows, the rows 32 below and stacked by __cardheight / 6.7 (16),
	face-down cards included. cards maps face_key names, 'card-back-sunset' and 'card-o' to bordered cards."""
	offset = int(HEIGHT / 6.7)
	width, height = 20 + 7 * (WIDTH + 10) + 10, 20 + HEIGHT + 32 + 11 * offset + HEIGHT + 20
	table = Image.new("RGB", (width, height), felt)
	place(table, cards["card-o"], 20, 20)
	for step, card in enumerate([(4, "clubs"), (11, "diamonds"), (8, "spades")]):
		place(table, cards[face_key(*card)], 20 + WIDTH + 18 + step * 12, 20)
	columns = [20 + index * (WIDTH + 10) for index in range(7)]
	for index, top in enumerate([(2, "hearts"), (0, "spades"), None, (1, "diamonds")]):
		if top is None:
			table.paste(sink(felt), (columns[3 + index], 20))
		else:
			place(table, cards[face_key(*top)], columns[3 + index], 20)
	rows = [
		[(12, "spades"), (11, "hearts"), (10, "clubs"), (9, "diamonds")],
		[(6, "hearts")],
		[(9, "clubs"), (8, "hearts"), (7, "spades")],
		[(4, "diamonds"), (3, "clubs")],
		[(11, "spades"), (10, "diamonds"), (9, "spades"), (8, "diamonds"), (7, "clubs"), (6, "diamonds")],
		[(12, "hearts")],
		[(6, "spades"), (5, "hearts"), (4, "clubs"), (3, "hearts"), (2, "spades")],
	]
	for index, face_up in enumerate(rows):
		stack = ["card-back-sunset"] * index + [face_key(*card) for card in face_up]
		for step, name in enumerate(stack):
			place(table, cards[name], columns[index], 20 + HEIGHT + 32 + step * offset)
	return table


def spider_table(cards, felt, suits):
	"""Spider mid-game as the game lays it out (spigame.cpp): ten rows 77 pixels apart from x 39, stacked by __cardheight / 6.4 (17), the
	deck at the bottom right, in the game's minimum client height. suits is the deck: ('spades',), ('spades', 'hearts') or all four."""
	offset = int(HEIGHT / 6.4)
	width = 10 * WIDTH + 13 * 5 + 12 + 30
	height = 2 * 5 + 3 * HEIGHT + 6 * offset
	table = Image.new("RGB", (width, height), felt)
	runs = [[12, 11, 10, 9], [5, 4], [8, 7, 6, 5, 4, 3, 2], [0], [11, 10], [9, 8, 7, 6], [3, 2, 1], [12], [6, 5, 4, 3, 2, 1, 0], [10, 9]]
	for index, run in enumerate(runs):
		stack = ["card-back-sunset"] * (5 if index < 4 else 4)
		for step, rank_index in enumerate(run):
			stack.append(face_key(rank_index, suits[(index + step // 3) % len(suits)]))
		for step, name in enumerate(stack):
			place(table, cards[name], index * (WIDTH + 5) + 6 * 6 + 3, 5 + step * offset)
	for step in range(4):
		place(table, cards["card-back-sunset"], width - 5 - WIDTH - 12 - step * 10, height - 5 - HEIGHT)
	return table


def render(out_dir):
	os.makedirs(out_dir, exist_ok=True)
	cards = {}
	for name, master in TARGETS:
		small = rasterise(os.path.join(HERE, master))
		with open(os.path.join(out_dir, f"{name}.bmp"), "wb") as handle:
			handle.write(bmp24(small))
		cards[name] = as_cardlib_draws(small, FELT)
	solitaire = solitaire_table(cards, FELT)
	spider = spider_table(cards, FELT, ("spades", "hearts"))
	gap = 16
	preview = Image.new("RGB", (max(solitaire.width, spider.width), solitaire.height + gap + spider.height), (0x14, 0x16, 0x34))
	preview.paste(solitaire, (0, 0))
	preview.paste(spider, (0, solitaire.height + gap))
	preview.resize((preview.width * 2, preview.height * 2), Image.NEAREST).save(os.path.join(out_dir, "afterglow-cards-preview.png"), optimize=False)


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit("usage: render.py OUT_DIR")
	render(sys.argv[1])
