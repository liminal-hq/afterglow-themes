#!/usr/bin/env python3
# Render the card faces to review sheets: a contact sheet for the selected set and for each alternative, and an overview comparing them.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
#   python3 render_sheets.py OUT_DIR [--stock STOCK_DIR]
#
# Draws every master of every direction (gen_faces.py's, in memory) with rsvg-convert at four times the bitmap and averages each 4 x 4
# block into one pixel, as desktop/cards/render.py does for the shipped art, then lays out OUT_DIR/card-faces-<direction>.png: the
# representative cards (A, 2, 5, 7, 10, J, Q, K of every suit, the joker and the free cell) at 1x, 2x and 4x on the dusk felt and the stock
# green, both corner indices with what cardlib's overlaps leave showing, a Solitaire table and Spider tables (one, two and four suits) laid
# out by desktop/cards/render.py as the games lay them out, and a colour-blind strip (deuteranopia,
# protanopia and tritanopia after Machado, Oliveira and Fernandes 2009 at full severity, and greyscale). OUT_DIR/card-faces-overview.png
# puts the three side by side. Cards on the tables get cardlib's black border and cut corners, and the backs are card-back-sunset.svg.
# With --stock, a folder of the stock cards.dll bitmaps as NN.bmp, the overview adds them as a reference column; they are only shown, never
# drawn from. Needs rsvg-convert, Pillow and numpy. The sheets are review images (their text depends on the fonts installed), so they are
# not checked by pixels; the copies in desktop/cards/faces/sheets are the ones the README shows.
import io
import os
import subprocess
import sys

import numpy
from PIL import Image, ImageDraw, ImageFont

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import faces as F  # noqa: E402
import gen_faces  # noqa: E402

CARD_RENDER = F.load("card_render", os.path.join(os.path.dirname(HERE), "render.py"))
WIDTH, HEIGHT = F.WIDTH, F.HEIGHT
DUSK_FELT = (0x1F, 0x25, 0x54)
STOCK_FELT = (0, 80, 0)
SHEET_BACKGROUND = (0x16, 0x18, 0x2C)
TEXT, MUTED = (0xF2, 0xEF, 0xF4), (0xB8, 0xB6, 0xC8)
REPRESENTATIVE_RANKS = (0, 1, 4, 6, 9, 10, 11, 12)
SUIT_ROWS = ("hearts", "spades", "diamonds", "clubs")
FONT_DIR = "/usr/share/fonts/noto"
DESCRIPTIONS = {
	"classic": ("A. Classic dusk (selected)", "The traditional layout on a cream face in a thin gold border. Rose hearts and diamonds, dusk-indigo "
		"spades and clubs, the index at the top left and turned at the bottom right. The ace is its suit in a gold sun ring. Double-ended courts "
		"are drawn once and coloured by suit; the king wears a rising-sun crown. The joker is a double-ended jester, and the free cell carries the "
		"Afterglow sun on its horizon under the dusk arcs."),
	"horizon": ("B. Horizon (alternative)", "Every face is a window onto the sunset back's horizon. The pips sit on a faint dawn sky with a gold horizon line, and "
		"the ace is its suit rising as the sun over the dusk arcs. The courts are night panels: the king is the crowned sun, the queen the moon, "
		"the jack the evening star, each reflected in the water."),
	"pixel": ("C. Pixel set E (alternative)", "The cards in the icon set's language. Pips are hand-hinted pixel shapes in set E's rose and dusk materials, with "
		"the keyline on their edge and a lit step at the top left. Courts are icon tiles on the dusk plate, drawn with set E's Pen. The border "
		"is a stepped gold ring."),
}

# Machado, Oliveira and Fernandes (2009), severity 1.0, on linear RGB
SIMULATIONS = (
	("deuteranopia", ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881))),
	("protanopia", ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998))),
	("tritanopia", ((1.255528, -0.076749, -0.178779), (-0.078411, 0.930809, 0.147602), (0.004733, 0.691367, 0.303900))),
)


def font(size, bold=False):
	path = os.path.join(FONT_DIR, "NotoSans-Bold.ttf" if bold else "NotoSans-Regular.ttf")
	return ImageFont.truetype(path, size) if os.path.exists(path) else ImageFont.load_default(size)


def rasterise(svg_text):
	"""A master at 4x, box-filtered to the bitmap, as desktop/cards/render.py draws the shipped art."""
	result = subprocess.run(["rsvg-convert", "--format", "png", "--width", str(WIDTH * F.SCALE), "--height", str(HEIGHT * F.SCALE)], input=svg_text.encode(),
		check=True, stdout=subprocess.PIPE)
	image = Image.open(io.BytesIO(result.stdout)).convert("RGBA")
	if image.getchannel("A").getextrema() != (255, 255):
		sys.exit("render_sheets.py: a master has transparent pixels")
	return image.convert("RGB").resize((WIDTH, HEIGHT), Image.BOX)


def corner_mask():
	"""The pixels of a card cardlib draws (all but the three cut pixels at each corner)."""
	mask = Image.new("L", (WIDTH, HEIGHT), 255)
	right, bottom = WIDTH - 1, HEIGHT - 1
	for x, y in ((0, 0), (1, 0), (0, 1), (right, 0), (right - 1, 0), (right, 1), (0, bottom), (1, bottom), (0, bottom - 1), (right, bottom), (right - 1, bottom),
			(right, bottom - 1)):
		mask.putpixel((x, y), 0)
	return mask


MASK = corner_mask()


class Deck:
	"""One direction's cards as cardlib shows them (black border over the outer ring), keyed by (rank_index, suit), 'joker', 'free' and 'back'."""

	def __init__(self, direction):
		module = gen_faces.DIRECTIONS[direction]
		self.cards = {}
		for suit in F.SUITS:
			for rank_index in range(13):
				self.cards[(rank_index, suit)] = self.bordered(rasterise(module.face(rank_index, suit)))
		self.cards["joker"] = self.bordered(rasterise(module.joker()))
		self.cards["free"] = self.bordered(rasterise(module.free_card()))
		for name in ("card-back-sunset", "card-o"):
			with open(os.path.join(os.path.dirname(HERE), name + ".svg")) as handle:
				self.cards[name] = self.bordered(rasterise(handle.read()))
		self.named = {name: card for name, card in self.cards.items() if isinstance(name, str)}
		for suit in F.SUITS:
			for rank_index in range(13):
				self.named[CARD_RENDER.face_key(rank_index, suit)] = self.cards[(rank_index, suit)]

	@staticmethod
	def bordered(card):
		return CARD_RENDER.as_cardlib_draws(card, (0, 0, 0))

	def __getitem__(self, key):
		return self.cards[key]


def place(canvas, card, x, y, scale=1):
	if scale != 1:
		card = card.resize((WIDTH * scale, HEIGHT * scale), Image.NEAREST)
		mask = MASK.resize((WIDTH * scale, HEIGHT * scale), Image.NEAREST)
	else:
		mask = MASK
	canvas.paste(card, (x, y), mask)


def representative(deck):
	rows = [[deck[(rank_index, suit)] for rank_index in REPRESENTATIVE_RANKS] for suit in SUIT_ROWS]
	rows.append([deck["joker"], deck["free"]])
	return rows


def card_grid(rows, scale, felt, gap=None):
	gap = gap if gap is not None else 6 * scale
	columns = max(len(row) for row in rows)
	width = gap + columns * (WIDTH * scale + gap)
	height = gap + len(rows) * (HEIGHT * scale + gap)
	canvas = Image.new("RGB", (width, height), felt)
	for row_index, row in enumerate(rows):
		for column_index, card in enumerate(row):
			place(canvas, card, gap + column_index * (WIDTH * scale + gap), gap + row_index * (HEIGHT * scale + gap), scale)
	return canvas


def corner_demo(deck):
	"""A row of six face-up cards stacked by Solitaire's 16 rows, a waste fan of three by 12 columns, and one whole card, at 4x."""
	offset = int(HEIGHT / 6.7)
	stack = [(12, "spades"), (11, "hearts"), (10, "clubs"), (9, "diamonds"), (8, "spades"), (7, "hearts")]
	width = 16 + WIDTH + 24 + 2 * 12 + WIDTH + 24 + WIDTH + 16
	height = 16 + (len(stack) - 1) * offset + HEIGHT + 16
	canvas = Image.new("RGB", (width, height), DUSK_FELT)
	for step, card in enumerate(stack):
		place(canvas, deck[card], 16, 16 + step * offset)
	for step, card in enumerate([(4, "clubs"), (11, "diamonds"), (6, "spades")]):
		place(canvas, deck[card], 16 + WIDTH + 24 + step * 12, 16)
	place(canvas, deck[(9, "hearts")], 16 + WIDTH + 24 + 2 * 12 + WIDTH + 24, 16)
	return canvas.resize((width * 4, height * 4), Image.NEAREST)


# ---- colour-blind simulation -----------------------------------------------------------------------------------------------------------------
def simulate(image, matrix):
	values = numpy.asarray(image, dtype=numpy.float64) / 255
	linear = numpy.where(values <= 0.04045, values / 12.92, ((values + 0.055) / 1.055) ** 2.4)
	mixed = numpy.clip(linear @ numpy.array(matrix).T, 0, 1)
	encoded = numpy.where(mixed <= 0.0031308, mixed * 12.92, 1.055 * mixed ** (1 / 2.4) - 0.055)
	return Image.fromarray(numpy.round(encoded * 255).astype(numpy.uint8), "RGB")


def colour_blind_strip(deck):
	picks = [(0, "hearts"), (6, "spades"), (9, "diamonds"), (12, "clubs"), (11, "hearts"), (10, "spades"), (4, "diamonds"), (1, "clubs")]
	dusk = card_grid([[deck[pick] for pick in picks[:4]]], 2, DUSK_FELT)
	green = card_grid([[deck[pick] for pick in picks[4:]]], 2, STOCK_FELT)
	strip = Image.new("RGB", (dusk.width + green.width, dusk.height))
	strip.paste(dusk, (0, 0))
	strip.paste(green, (dusk.width, 0))
	versions = [("as seen", strip)] + [(name, simulate(strip, matrix)) for name, matrix in SIMULATIONS] + [("greyscale", strip.convert("L").convert("RGB"))]
	return versions


# ---- sheets -----------------------------------------------------------------------------------------------------------------------------------
class Sheet:
	def __init__(self, width):
		self.width = width
		self.blocks = []  # (image, x, y)
		self.texts = []  # (x, y, text, font, colour)
		self.y = 0

	def text(self, words, size=28, bold=False, colour=TEXT, x=40, wrap=None):
		chosen = font(size, bold)
		lines = [words]
		if wrap:
			lines, line = [], ""
			for word in words.split():
				trial = (line + " " + word).strip()
				if chosen.getlength(trial) > wrap and line:
					lines.append(line)
					line = word
				else:
					line = trial
			lines.append(line)
		for line in lines:
			self.texts.append((x, self.y, line, chosen, colour))
			self.y += int(size * 1.4)

	def row(self, images, gap=30, x=40, labels=None, label_size=22):
		if labels:
			for image_x, label in zip(self.positions(images, gap, x), labels):
				self.texts.append((image_x, self.y, label, font(label_size), MUTED))
			self.y += int(label_size * 1.5)
		for image_x, image in zip(self.positions(images, gap, x), images):
			self.blocks.append((image, image_x, self.y))
		self.y += max(image.height for image in images) + gap

	@staticmethod
	def positions(images, gap, x):
		result = []
		for image in images:
			result.append(x)
			x += image.width + gap
		return result

	def space(self, amount):
		self.y += amount

	def save(self, path):
		canvas = Image.new("RGB", (self.width, self.y + 40), SHEET_BACKGROUND)
		for image, x, y in self.blocks:
			canvas.paste(image, (x, y))
		draw = ImageDraw.Draw(canvas)
		for x, y, line, chosen, colour in self.texts:
			draw.text((x, y), line, font=chosen, fill=colour)
		canvas.save(path, optimize=True)


def contact_sheet(direction, deck, path):
	title, description = DESCRIPTIONS[direction]
	if direction != gen_faces.SELECTED.NAME:
		description += " Review only: not shipped."
	sheet = Sheet(2560)
	sheet.space(36)
	sheet.text("Afterglow card faces, direction " + title, 48, bold=True)
	sheet.text(description, 26, colour=MUTED, wrap=2400)
	sheet.text("ReactOS cards.dll, 72 x 112. Cards carry cardlib's black border and cut corners. The back is card-back-sunset.", 22, colour=MUTED)
	sheet.space(20)
	rows = representative(deck)
	flat = [card for row in rows for card in row]
	one_x_rows = [flat[index:index + 12] for index in range(0, len(flat), 12)]
	sheet.text("1x, the real size", 30, bold=True)
	sheet.row([card_grid(one_x_rows, 1, DUSK_FELT), card_grid(one_x_rows, 1, STOCK_FELT)], labels=["on the dusk felt (#1f2554)", "on the stock green (0, 80, 0)"])
	sheet.text("2x", 30, bold=True)
	sheet.row([card_grid(rows, 2, DUSK_FELT), card_grid(rows, 2, STOCK_FELT)], labels=["dusk felt", "stock green"])
	sheet.text("4x", 30, bold=True)
	sheet.row([card_grid(rows[0:2], 4, DUSK_FELT)], labels=["hearts and spades on the dusk felt"])
	sheet.row([card_grid(rows[2:4], 4, STOCK_FELT)], labels=["diamonds and clubs on the stock green"])
	sheet.row([card_grid(rows[4:5], 4, DUSK_FELT)], labels=["the joker (66) and the free cell (53)"])
	sheet.text("Both corners, and what cardlib's overlaps leave showing (4x)", 30, bold=True)
	sheet.text("A Solitaire row shows each card's top 16 rows, the waste fan each card's left 12 columns, and the top card of a pile all of it, "
		"with the turned index at the bottom right.", 22, colour=MUTED, wrap=2400)
	sheet.row([corner_demo(deck)])
	sheet.text("Solitaire, as cardlib lays it out", 30, bold=True)
	dusk_table = CARD_RENDER.solitaire_table(deck.named, DUSK_FELT)
	sheet.row([dusk_table.resize((dusk_table.width * 2, dusk_table.height * 2), Image.NEAREST), CARD_RENDER.solitaire_table(deck.named, STOCK_FELT)],
		labels=["2x on the dusk felt", "1x on the stock green"])
	sheet.text("Spider Solitaire at 1x", 30, bold=True)
	sheet.row([CARD_RENDER.spider_table(deck.named, DUSK_FELT, ("spades",)), CARD_RENDER.spider_table(deck.named, DUSK_FELT, ("spades", "hearts")),
		CARD_RENDER.spider_table(deck.named, STOCK_FELT, ("spades", "hearts", "clubs", "diamonds"))], gap=20, x=20,
		labels=["one suit (dusk felt)", "two suits (dusk felt)", "four suits (stock green)"])
	two_suit = CARD_RENDER.spider_table(deck.named, DUSK_FELT, ("spades", "hearts"))
	sheet.row([two_suit.resize((two_suit.width * 2, two_suit.height * 2), Image.NEAREST)], labels=["two suits at 2x on the dusk felt"])
	sheet.text("Colour-blind simulation (Machado 2009, full severity) at 2x", 30, bold=True)
	for name, image in colour_blind_strip(deck):
		sheet.row([image], gap=16, labels=[name])
	sheet.save(path)


def overview(decks, path, stock_dir=None):
	sheet = Sheet(2900)
	sheet.space(36)
	sheet.text("Afterglow card faces: the selected set and two alternatives", 48, bold=True)
	sheet.text("Each column: the same eight cards at 2x on the dusk felt, then Solitaire at 1x. The back is card-back-sunset in all three.", 26, colour=MUTED)
	sheet.space(20)
	picks = [(0, "hearts"), (6, "clubs"), (9, "diamonds"), (0, "spades"), (10, "spades"), (11, "hearts"), (12, "clubs"), (12, "diamonds")]
	columns = []
	for direction, deck in decks.items():
		grid = card_grid([[deck[pick] for pick in picks[:4]], [deck[pick] for pick in picks[4:]]], 2, DUSK_FELT)
		columns.append((DESCRIPTIONS[direction][0], grid, CARD_RENDER.solitaire_table(deck.named, DUSK_FELT)))
	if stock_dir:
		stock = {}
		for rank_index, suit in picks:
			bitmap = Image.open(os.path.join(stock_dir, "%02d.bmp" % F.resource_id(rank_index, suit))).convert("RGB")
			stock[(rank_index, suit)] = CARD_RENDER.as_cardlib_draws(bitmap, (0, 0, 0))
		grid = card_grid([[stock[pick] for pick in picks[:4]], [stock[pick] for pick in picks[4:]]], 2, STOCK_FELT)
		columns.append(("Stock ReactOS (reference)", grid, None))
	x = 40
	top = sheet.y
	for name, grid, table in columns:
		sheet.texts.append((x, top, name, font(34, True), TEXT))
		sheet.blocks.append((grid, x, top + 56))
		if table is not None:
			sheet.blocks.append((table, x, top + 56 + grid.height + 24))
		x += max(grid.width, table.width if table is not None else 0) + 40
	sheet.width = x
	sheet.y = top + 56 + columns[0][1].height + 24 + columns[0][2].height
	sheet.save(path)


def main():
	arguments = sys.argv[1:]
	stock_dir = None
	if "--stock" in arguments:
		at = arguments.index("--stock")
		stock_dir = arguments[at + 1]
		del arguments[at:at + 2]
	if len(arguments) != 1:
		sys.exit("usage: render_sheets.py OUT_DIR [--stock STOCK_DIR]")
	out = arguments[0]
	os.makedirs(out, exist_ok=True)
	decks = {}
	for direction in gen_faces.DIRECTIONS:
		decks[direction] = Deck(direction)
		contact_sheet(direction, decks[direction], os.path.join(out, "card-faces-%s.png" % direction))
		print("card-faces-%s.png" % direction)
	overview(decks, os.path.join(out, "card-faces-overview.png"), stock_dir)
	print("card-faces-overview.png")


if __name__ == "__main__":
	main()
