#!/usr/bin/env python3
# Review-only card-face alternative C, "Pixel set E": the cards in the icon set's own language. Pips are hand-hinted pixel shapes in set E's materials
# with the keyline on their edge pixels and a lit step at the top left, as the hinted 16 px icons are; the courts are icon tiles on set E's
# dusk plate, drawn with its Pen (crown and rising sun, crescent, evening star); the border is a stepped gold ring.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# Every pixel of a pip is one of three tones of its material: the keyline (desktop/icons/gen_e.py's retune of the material's 16 px edge,
# which reaches 3:1 on cream and on the dusk felt), the lit tone on the top and left, and the base. The shading is worked out after a pip is
# placed and turned, so the light always comes from the top left. Deterministic: no randomness, no clock and no environment input.
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "faces"))
import faces as F  # noqa: E402

E = F.ICONS
NAME = "pixel"
TITLE = "C, Pixel set E"
ROSE_MAT, DUSK_MAT = E.MATS["rose"], E.MATS["dusk"]

# The pips, 12 x 12, hinted by hand (an even size, so a pip centres on the card's even width and turns onto the same pixel grid)
PIPS = {
	"hearts": [".###....###.", "#####..#####", "############", "############", "############", "############", ".##########.", "..########..",
		"...######...", "....####....", ".....##.....", "............"],
	"diamonds": [".....##.....", "....####....", "....####....", "...######...", "..########..", ".##########.", ".##########.", "..########..",
		"...######...", "....####....", "....####....", ".....##....."],
	"spades": [".....##.....", "....####....", "...######...", "..########..", ".##########.", "############", "############", "############",
		".####..####.", ".....##.....", "....####....", "...######..."],
	"clubs": ["....####....", "...######...", "...######...", "...######...", ".##.####.##.", "############", "############", "############",
		".##..##..##.", ".....##.....", "....####....", "...######..."],
}
PIP_SIZE = 12


def material(suit):
	return ROSE_MAT if suit in F.WARM else DUSK_MAT


def tones(suit):
	"""(base, lit, keyline) of a suit's material."""
	mat = material(suit)
	return mat.base, mat.lit, E.retune(mat.px_edge())


def shade(cells):
	"""Split a set of cells into keyline (touching the outside), lit (an outside cell within two steps up or left) and base."""
	cells = set(cells)
	edge, lit, base = [], [], []
	for x, y in sorted(cells):
		if any((x + dx, y + dy) not in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
			edge.append((x, y))
		elif (x - 2, y) not in cells or (x, y - 2) not in cells or (x - 1, y - 1) not in cells:
			lit.append((x, y))
		else:
			base.append((x, y))
	return edge, lit, base


def shaded(cells, suit):
	base_colour, lit_colour, edge_colour = tones(suit)
	edge, lit, base = shade(cells)
	return F.pixels(base, base_colour) + F.pixels(lit, lit_colour) + F.pixels(edge, edge_colour)


def pip_cells(suit, cx, cy, flip=False):
	"""A 12 x 12 pip centred on the pixel corner (cx, cy); turned pips are placed upright first, then turned about the card's centre."""
	left, top = int(cx) - PIP_SIZE // 2, int(cy) - PIP_SIZE // 2
	if flip:
		left, top = F.WIDTH - (left + PIP_SIZE), F.HEIGHT - (top + PIP_SIZE)
	return F.bitmap_cells(PIPS[suit], left, top, flip=flip)


def frame():
	"""The cream face in a stepped gold ring: the orange-300 line on the third pixel ring, a pale lit step inside it on the top and left."""
	ring = [(x, 2) for x in range(4, 68)] + [(x, 109) for x in range(4, 68)] + [(2, y) for y in range(4, 108)] + [(69, y) for y in range(4, 108)]
	ring += [(3, 3), (68, 3), (3, 108), (68, 108)]  # the stepped corners
	lit = [(x, 3) for x in range(4, 68)] + [(3, y) for y in range(4, 108)]
	return '<rect x="0" y="0" width="72" height="112" fill="%s"/>%s%s' % (F.CREAM, F.pixels(lit, F.PALE), F.pixels(ring, F.GOLD_LINE))


def pips(rank_index, suit):
	cells = []
	for x, y, flip in F.pip_layout(rank_index + 1, columns=(22, 36, 50), top=23, bottom=89):
		cells.append(pip_cells(suit, x, round(y), flip))
	return "".join(shaded(group, suit) for group in cells)


def ring_cells(cx, cy, outer, inner):
	return [(x, y) for y in range(int(cy - outer) - 1, int(cy + outer) + 2) for x in range(int(cx - outer) - 1, int(cx + outer) + 2)
		if inner ** 2 <= (x + 0.5 - cx) ** 2 + (y + 0.5 - cy) ** 2 <= outer ** 2]


def ace(suit):
	"""The suit large, as a hinted pixel shape in its material, in a stepped gold sun ring."""
	big = F.coverage_mask(F.suit_outlines(suit, 15, 15, 30), 0, 0, 30, 30)
	cells = F.bitmap_cells(big, 21, 41)
	ring = ring_cells(36, 56, 22, 20.6)
	inner_ring = ring_cells(36, 56, 20.6, 19.4)
	return F.pixels(inner_ring, F.BRAND_GOLD) + F.pixels(ring, F.GOLD_LINE) + shaded(cells, suit)


# ---- the courts: icon tiles drawn with set E's Pen on its dusk plate ---------------------------------------------------------------------------
def crescent_d(cx, cy, outer, inner, offset):
	"""A crescent: the outer circle less an inner one moved up and to the right by offset, as one outline of two arcs."""
	shift_x, shift_y = offset, -offset * 0.6
	distance = F.math.hypot(shift_x, shift_y)
	along = (distance ** 2 + outer ** 2 - inner ** 2) / (2 * distance)
	across = F.math.sqrt(outer ** 2 - along ** 2)
	unit_x, unit_y = shift_x / distance, shift_y / distance
	first = (cx + along * unit_x - across * unit_y, cy + along * unit_y + across * unit_x)
	second = (cx + along * unit_x + across * unit_y, cy + along * unit_y - across * unit_x)
	return "M%s %s A%s %s 0 1 1 %s %s A%s %s 0 0 0 %s %s Z" % (F.number(first[0]), F.number(first[1]), F.number(outer), F.number(outer), F.number(second[0]),
		F.number(second[1]), F.number(inner), F.number(inner), F.number(first[0]), F.number(first[1]))


def star_d(cx, cy, reach, waist):
	points = []
	for step in range(8):
		radius = reach if step % 2 == 0 else waist
		angle = F.math.radians(step * 45 - 90)
		points.append((cx + radius * F.math.cos(angle), cy + radius * F.math.sin(angle), 0.4))
	return E.poly(points)


def badge(pen, suit):
	"""The suit as a badge at the plate's lower right, as the icon set's badges are: a rose or light disc with the suit on it."""
	if suit in F.WARM:
		pen.face(E.circ(37, 37, 7.5), E.MATS["rose"])
		pen.raw(F.suit_path(suit, 37, 37, 8, F.PAPER[900]))
	else:
		pen.face(E.circ(37, 37, 7.5), E.MATS["front"])
		pen.raw(F.suit_path(suit, 37, 37, 8, F.SKY1))


def king(pen, suit):
	pen.fill(E.circ(24, 31, 12.5), F.mix(F.ORANGE[200], F.SKY7, 0.55))  # the sun's glow, then the sun rising behind the crown
	pen.fill(E.circ(24, 31, 9.5), F.ORANGE[200])
	pen.face(E.poly([(14.5, 33, 1), (13.5, 19, 0.8), (19, 25, 0.8), (24, 15.5, 0.8), (29, 25, 0.8), (34.5, 19, 0.8), (33.5, 33, 1)]), E.MATS["goldl"])
	pen.face(E.RR(13, 30, 22, 5.5, 2), E.MATS["gold"])
	pen.face(E.circ(24, 32.7, 1.8), E.MATS["rose"], band=False)
	pen.raw('<rect x="7" y="35.5" width="34" height="1.4" rx="0.7" fill="%s"/>' % F.BRAND_GOLD)  # the horizon
	badge(pen, suit)


def queen(pen, suit):
	pen.face(crescent_d(22, 25, 12, 10, 5), E.MATS["goldl"])
	for x, y in ((33, 11), (38, 18), (30, 18)):
		pen.fill(star_d(x, y, 3, 1), F.BRAND_GOLD)
	badge(pen, suit)


def jack(pen, suit):
	pen.face(star_d(22, 22, 13, 4), E.MATS["goldl"])
	pen.fill(E.circ(22, 22, 2.4), F.PALE)
	badge(pen, suit)


COURTS = {10: jack, 11: queen, 12: king}
TILE_SCALE = 1.2  # the 48-unit icon grid at 57.6 card pixels: the plate is 45.6 pixels square


def tile(prefix, draw, scale=TILE_SCALE, centre_y=50):
	pen = E.Pen(prefix, 48)
	E.plate(pen)
	draw(pen)
	offset_x, offset_y = 36 - 24 * scale, centre_y - 24 * scale
	return "".join(pen.defs.values()), '<g transform="translate(%s %s) scale(%s)">%s</g>' % (F.number(offset_x), F.number(offset_y), F.number(scale),
		"".join(pen.out))


def court(rank_index, suit):
	defs, art = tile("c%d%s" % (rank_index, suit[0]), lambda pen: COURTS[rank_index](pen, suit))
	return defs, art + shaded(pip_cells(suit, 36, 90), suit)


def face(rank_index, suit):
	defs = ""
	if rank_index == 0:
		art = ace(suit)
	elif rank_index >= 10:
		defs, art = court(rank_index, suit)
	else:
		art = pips(rank_index, suit)
	body = frame() + art + F.index(F.RANKS[rank_index], suit)
	return F.document(F.card_title(TITLE, rank_index, suit), F.card_note(TITLE, F.resource_id(rank_index, suit)), body, defs)


def joker():
	"""The four suits round a small sun on the dusk plate, the wild card of the deck; JOKER down the left side in the index font."""
	def draw(pen):
		pen.fill(E.circ(24, 24, 4), F.ORANGE[200])
		for suit, (x, y) in zip(("spades", "hearts", "clubs", "diamonds"), ((24, 12.5), (35.5, 24), (24, 35.5), (12.5, 24))):
			mat = E.MATS["rose"] if suit in F.WARM else E.MATS["front"]
			pen.face(E.circ(x, y, 5.5), mat)
			pen.raw(F.suit_path(suit, x, y, 6, F.PAPER[900] if suit in F.WARM else F.SKY1))

	defs, art = tile("joker", draw, 1.05, 56)
	word = []
	for position, letter in enumerate("JOKER"):
		word += F.bitmap_cells(F.RANK_GLYPHS[letter], 5, 5 + position * 10)
		word += F.bitmap_cells(F.RANK_GLYPHS[letter], 5, 5 + position * 10, flip=True)
	body = frame() + art + F.pixels(word, F.DUSK)
	return F.document("Afterglow card face, %s: joker" % TITLE, F.card_note(TITLE, F.JOKER), body, defs)


def free_card():
	"""An empty cell: the stepped gold ring and a dotted outline of the plate where a card may go."""
	outline = [(x, y) for x, y in ring_cells(36, 56, 14, 12.8) if (x + y) % 2 == 0]
	body = frame() + F.pixels(outline, F.GOLD_LINE) + F.pixels([(x, 56) for x in range(26, 46) if x % 2 == 0], F.GOLD_LINE)
	return F.document("Afterglow card face, %s: free cell" % TITLE, F.card_note(TITLE, F.FREE_CARD), body)
