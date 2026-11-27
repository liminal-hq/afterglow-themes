#!/usr/bin/env python3
# The parts every proposed Afterglow card-face direction shares: cards.dll's order, cardlib's geometry, the suit shapes, the pip layouts,
# the hand-hinted index font and the SVG writer.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# cards.dll (ReactOS 0.4.16, dll/win32/cards/cards.rc) holds the faces as bitmaps 1 to 52 in suit order clubs, diamonds, hearts, spades,
# ace to king within each suit (resource = suit * 13 + rank), then FreeCard (53), twelve backs (54 to 65), Joker (66), XSign (67) and
# OSign (68). cardlib (sdk/lib/3rdparty/cardlib) loads them into its own order, rank-major ((rank - 1) * 4 + suit, cardbitmaps.cpp), paints
# a black line over each card's outer pixel ring with the corner pixels cut, and draws stacked cards as strips: Solitaire overlaps face-up
# cards by 16 rows (__cardheight / 6.7) and fans the waste pile by 12 columns (CS_DEFXOFF), Spider by 17 rows (__cardheight / 6.4). So the
# index (rank and small suit, side by side) sits in rows 4 to 12 at the top left, and the rank alone in the left 12 columns, as the stock
# faces have it. Every face is drawn in the bitmap's own pixels (viewBox 72 x 112) at four times the size, so render.py's 4x box filter
# keeps the hand-hinted pixel shapes exact. Deterministic: no randomness, no clock and no environment input.
import importlib.util
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
DESKTOP = os.path.dirname(os.path.dirname(HERE))
WIDTH, HEIGHT = 72, 112
SCALE = 4


def load(name, path):
	spec = importlib.util.spec_from_file_location(name, path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


ICONS = load("gen_e", os.path.join(DESKTOP, "icons", "gen_e.py"))
ORANGE, RED, PURPLE, INDIGO, PAPER = ICONS.ORANGE, ICONS.RED, ICONS.PURPLE, ICONS.INDIGO, ICONS.PAPER
SKY1, SKY4, SKY7, HORIZON, PALE, BRAND_GOLD, TILE = ICONS.SKY1, ICONS.SKY4, ICONS.SKY7, ICONS.HORIZON, ICONS.PALE, ICONS.BRAND_GOLD, ICONS.TILE
mix, number, contrast = ICONS.mix, ICONS._n, ICONS.contrast

# ---- the deck -----------------------------------------------------------------------------------------------------------------------------------
SUITS = ("clubs", "diamonds", "hearts", "spades")  # cards.dll's order, and cardlib's eSuit
RANKS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
RANK_NAMES = ("ace", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "jack", "queen", "king")
WARM = ("diamonds", "hearts")
FREE_CARD, JOKER = 53, 66


def resource_id(rank_index, suit):
	"""The cards.dll bitmap of a face: rank_index 0 (ace) to 12 (king)."""
	return SUITS.index(suit) * 13 + rank_index + 1


def master_name(rank_index, suit):
	return "%02d-%s-%s.svg" % (resource_id(rank_index, suit), suit, RANK_NAMES[rank_index])


# ---- colour: the suits on the cream face --------------------------------------------------------------------------------------------------
# Rose and dusk indigo differ in hue and, more, in lightness (luminance 0.155 against 0.023), so red and black stay apart for every kind of
# colour blindness and in greyscale; the four shapes stay apart by silhouette. Both reach 4.5:1 on the cream face.
CREAM = PAPER[900]
ROSE = RED[300]
DUSK = SKY1
GOLD_LINE = ORANGE[300]  # the face's thin gold border: brand gold reads on the dark back, a step deeper on cream
FELT = SKY1
STOCK_FELT = "#005000"


def suit_colour(suit):
	return ROSE if suit in WARM else DUSK


# ---- geometry: shapes as polygons -------------------------------------------------------------------------------------------------------------
def bezier(start, control1, control2, end, steps=24):
	points = []
	for step in range(1, steps + 1):
		t = step / steps
		u = 1 - t
		points.append((u ** 3 * start[0] + 3 * u * u * t * control1[0] + 3 * u * t * t * control2[0] + t ** 3 * end[0],
			u ** 3 * start[1] + 3 * u * u * t * control1[1] + 3 * u * t * t * control2[1] + t ** 3 * end[1]))
	return points


def curve_path(start, segments):
	"""A closed outline from cubic segments ((c1, c2, end) or (end,) for a straight line)."""
	points = [start]
	for segment in segments:
		if len(segment) == 1:
			points.append(segment[0])
		else:
			points.extend(bezier(points[-1], *segment))
	return points[:-1] if points[-1] == points[0] else points


def circle(cx, cy, radius, steps=64):
	return [(cx + radius * math.cos(2 * math.pi * step / steps), cy + radius * math.sin(2 * math.pi * step / steps)) for step in range(steps)]


def signed_area(points):
	return sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(points, points[1:] + points[:1])) / 2


def oriented(points):
	"""Every outline the same way round, so overlapping parts of one shape fill as a union under the nonzero rule."""
	return points if signed_area(points) > 0 else points[::-1]


# The four suits in a unit box (x and y from -0.5 to 0.5, y down), as unions of outlines. Drawn here, not traced from any deck.
HEART = [curve_path((0, 0.5), [
	((-0.12, 0.36), (-0.5, 0.12), (-0.5, -0.16)),
	((-0.5, -0.37), (-0.37, -0.5), (-0.24, -0.5)),
	((-0.11, -0.5), (-0.02, -0.41), (0, -0.3)),
	((0.02, -0.41), (0.11, -0.5), (0.24, -0.5)),
	((0.37, -0.5), (0.5, -0.37), (0.5, -0.16)),
	((0.5, 0.12), (0.12, 0.36), (0, 0.5)),
])]
DIAMOND = [curve_path((0, -0.5), [
	((0.14, -0.3), (0.28, -0.14), (0.4, 0)),
	((0.28, 0.14), (0.14, 0.3), (0, 0.5)),
	((-0.14, 0.3), (-0.28, 0.14), (-0.4, 0)),
	((-0.28, -0.14), (-0.14, -0.3), (0, -0.5)),
])]
SPADE = [curve_path((0, -0.5), [
	((0.12, -0.34), (0.5, -0.12), (0.5, 0.11)),
	((0.5, 0.28), (0.38, 0.37), (0.25, 0.37)),
	((0.14, 0.37), (0.06, 0.32), (0.035, 0.24)),
	((0.05, 0.36), (0.1, 0.45), (0.2, 0.5)),
	((-0.2, 0.5),),
	((-0.1, 0.45), (-0.05, 0.36), (-0.035, 0.24)),
	((-0.06, 0.32), (-0.14, 0.37), (-0.25, 0.37)),
	((-0.38, 0.37), (-0.5, 0.28), (-0.5, 0.11)),
	((-0.5, -0.12), (-0.12, -0.34), (0, -0.5)),
])]
CLUB = [circle(0, -0.255, 0.245), circle(-0.255, 0.09, 0.245), circle(0.255, 0.09, 0.245), [(-0.12, -0.1), (0.12, -0.1), (0.12, 0.16), (-0.12, 0.16)],
	curve_path((-0.04, 0.1), [((0.04, 0.1),), ((0.05, 0.35), (0.11, 0.45), (0.2, 0.5)), ((-0.2, 0.5),), ((-0.11, 0.45), (-0.05, 0.35), (-0.04, 0.1))])]
SHAPES = {"hearts": HEART, "diamonds": DIAMOND, "spades": SPADE, "clubs": CLUB}
ASPECT = {"hearts": 1.0, "diamonds": 1.0, "spades": 0.96, "clubs": 1.0}  # width over height


def placed(outlines, cx, cy, height, width=None, flip=False):
	"""Outlines scaled to a height (and width) and centred at (cx, cy), turned upside down when flip is set."""
	width = height if width is None else width
	sign = -1 if flip else 1
	return [oriented([(cx + sign * x * width, cy + sign * y * height) for x, y in outline]) for outline in outlines]


def path_d(outlines):
	return " ".join("M" + " L".join("%s %s" % (number(x), number(y)) for x, y in outline) + " Z" for outline in outlines)


def suit_outlines(suit, cx, cy, height, flip=False):
	return placed(SHAPES[suit], cx, cy, height, height * ASPECT[suit], flip)


def suit_path(suit, cx, cy, height, colour, flip=False, extra=""):
	return '<path d="%s" fill="%s"%s/>' % (path_d(suit_outlines(suit, cx, cy, height, flip)), colour, extra)


def inside(outlines, x, y):
	"""Point in the union of the outlines (even-odd per outline, so a point in any outline counts)."""
	for outline in outlines:
		crossings = False
		for (x0, y0), (x1, y1) in zip(outline, outline[1:] + outline[:1]):
			if (y0 > y) != (y1 > y) and x < x0 + (y - y0) * (x1 - x0) / (y1 - y0):
				crossings = not crossings
		if crossings:
			return True
	return False


def coverage_mask(outlines, left, top, columns, rows, threshold=0.5, samples=4):
	"""The pixels a shape covers at least threshold of, sampled samples x samples per pixel: the starting point for a hand-hinted bitmap."""
	mask = []
	for row in range(rows):
		line = ""
		for column in range(columns):
			hits = sum(inside(outlines, left + column + (i + 0.5) / samples, top + row + (j + 0.5) / samples) for i in range(samples) for j in range(samples))
			line += "#" if hits >= threshold * samples * samples else "."
		mask.append(line)
	return mask


# ---- pixel bitmaps -------------------------------------------------------------------------------------------------------------------------------
def bitmap_cells(rows, left, top, flip=False, glyph=None):
	"""The pixel cells of a bitmap ('#' set) placed with its top-left at (left, top); flip turns it about the card's centre."""
	cells = []
	for row_index, row in enumerate(rows):
		for column_index, cell in enumerate(row):
			if cell == (glyph or "#"):
				x, y = left + column_index, top + row_index
				if flip:
					x, y = WIDTH - 1 - x, HEIGHT - 1 - y
				cells.append((x, y))
	return cells


def cells_d(cells):
	"""Pixel cells as one path, merged into horizontal runs."""
	by_row = {}
	for x, y in cells:
		by_row.setdefault(y, set()).add(x)
	parts = []
	for y in sorted(by_row):
		columns = sorted(by_row[y])
		start = previous = columns[0]
		for x in columns[1:] + [None]:
			if x is not None and x == previous + 1:
				previous = x
				continue
			parts.append("M%d %dh%dv1h-%dz" % (start, y, previous - start + 1, previous - start + 1))
			if x is not None:
				start = previous = x
	return "".join(parts)


def pixels(cells, colour):
	return '<path d="%s" fill="%s"/>' % (cells_d(cells), colour) if cells else ""


# The index: a bold rank 9 pixels tall, hinted by hand, two-pixel stems so it holds at 1x on any monitor. "10" is the one wide glyph.
RANK_GLYPHS = {
	"A": ["..###..", ".##.##.", "##...##", "##...##", "##...##", "#######", "##...##", "##...##", "##...##"],
	"2": [".#####.", "##...##", ".....##", "....##.", "...##..", "..##...", ".##....", "##.....", "#######"],
	"3": [".#####.", "##...##", ".....##", "..####.", ".....##", ".....##", ".....##", "##...##", ".#####."],
	"4": ["....##.", "...###.", "..####.", ".##.##.", "##..##.", "#######", "....##.", "....##.", "....##."],
	"5": ["#######", "##.....", "##.....", "######.", ".....##", ".....##", ".....##", "##...##", ".#####."],
	"6": ["..####.", ".##....", "##.....", "######.", "##...##", "##...##", "##...##", "##...##", ".#####."],
	"7": ["#######", ".....##", "....##.", "....##.", "...##..", "...##..", "..##...", "..##...", "..##..."],
	"8": [".#####.", "##...##", "##...##", ".#####.", "##...##", "##...##", "##...##", "##...##", ".#####."],
	"9": [".#####.", "##...##", "##...##", "##...##", ".######", ".....##", ".....##", "....##.", ".####.."],
	"10": [".##..####.", "###.##..##", ".##.##..##", ".##.##..##", ".##.##..##", ".##.##..##", ".##.##..##", ".##.##..##", ".##..####."],
	"J": ["..#####", "....##.", "....##.", "....##.", "....##.", "....##.", "##..##.", "##..##.", ".####.."],
	"Q": [".#####.", "##...##", "##...##", "##...##", "##...##", "##...##", "##.####", "##..##.", ".###.##"],
	"K": ["##...##", "##..##.", "##.##..", "####...", "###....", "####...", "##.##..", "##..##.", "##...##"],
	# the joker's vertical word
	"O": [".#####.", "##...##", "##...##", "##...##", "##...##", "##...##", "##...##", "##...##", ".#####."],
	"E": ["#######", "##.....", "##.....", "######.", "##.....", "##.....", "##.....", "##.....", "#######"],
	"R": ["######.", "##...##", "##...##", "##...##", "######.", "##.##..", "##..##.", "##...##", "##...##"],
}
# The small suit beside the rank, 9 x 9, hinted by hand
SUIT_GLYPHS = {
	"hearts": [".##...##.", "####.####", "#########", "#########", "#########", ".#######.", "..#####..", "...###...", "....#...."],
	"diamonds": ["....#....", "...###...", "..#####..", ".#######.", "#########", ".#######.", "..#####..", "...###...", "....#...."],
	"spades": ["....#....", "...###...", "..#####..", ".#######.", "#########", "#########", ".###.###.", "....#....", "...###..."],
	"clubs": ["...###...", "..#####..", "..#####..", "...###...", ".###.###.", "#########", "#########", ".###.###.", "...###..."],
}
INDEX_TOP, INDEX_LEFT = 4, 4  # inside the border ring, a cream row and the face's gold line


def index_cells(rank, suit, left=INDEX_LEFT, top=INDEX_TOP, gap=2):
	"""The rank and small suit cells, top left and turned at the bottom right: (rank cells, suit cells)."""
	glyph = RANK_GLYPHS[rank]
	rank_left = left
	suit_left = rank_left + len(glyph[0]) + gap
	rank_cells = bitmap_cells(glyph, rank_left, top) + bitmap_cells(glyph, rank_left, top, flip=True)
	suit_cells = bitmap_cells(SUIT_GLYPHS[suit], suit_left, top) + bitmap_cells(SUIT_GLYPHS[suit], suit_left, top, flip=True)
	return rank_cells, suit_cells


def index(rank, suit, rank_colour=None, suit_colour_=None):
	rank_cells, suit_cells = index_cells(rank, suit)
	colour = suit_colour(suit)
	return pixels(rank_cells, rank_colour or colour) + pixels(suit_cells, suit_colour_ or colour)


# ---- pips ---------------------------------------------------------------------------------------------------------------------------------------
def pip_layout(count, columns=(21.5, 36, 50.5), top=22, bottom=90):
	"""Where the pips of a numbered card sit, as (x, y, upside_down): the traditional patterns."""
	left, centre, right = columns
	middle = (top + bottom) / 2
	quarter = (bottom - top) / 3
	upper_quarter, lower_quarter = top + quarter, bottom - quarter

	def pair(y):
		return [(left, y), (right, y)]

	layouts = {
		2: [(centre, top), (centre, bottom)],
		3: [(centre, top), (centre, middle), (centre, bottom)],
		4: pair(top) + pair(bottom),
		5: pair(top) + pair(bottom) + [(centre, middle)],
		6: pair(top) + pair(middle) + pair(bottom),
		7: pair(top) + pair(middle) + pair(bottom) + [(centre, (top + middle) / 2)],
		8: pair(top) + pair(middle) + pair(bottom) + [(centre, (top + middle) / 2), (centre, (middle + bottom) / 2)],
		9: pair(top) + pair(upper_quarter) + pair(lower_quarter) + pair(bottom) + [(centre, middle)],
		10: pair(top) + pair(upper_quarter) + pair(lower_quarter) + pair(bottom) + [(centre, (top + upper_quarter) / 2),
			(centre, (lower_quarter + bottom) / 2)],
	}
	return [(x, y, y > middle + 0.01) for x, y in layouts[count]]


# ---- the document -------------------------------------------------------------------------------------------------------------------------------
HEAD = """<?xml version="1.0" encoding="UTF-8"?>
<!--
%s

(c) Copyright 2026 Liminal HQ, Scott Morris
SPDX-License-Identifier: Apache-2.0 OR MIT

%s
-->
"""


def document(title, note, body, defs=""):
	return (HEAD % (title, note) + '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">\n<title>%s</title>\n<defs>%s</defs>\n%s\n</svg>\n'
		% (WIDTH * SCALE, HEIGHT * SCALE, WIDTH, HEIGHT, title, defs, body))


def card_title(direction, rank_index, suit):
	return "Afterglow card face, %s: %s of %s" % (direction, RANK_NAMES[rank_index], suit)


def card_note(direction, resource, selected=False):
	if selected:
		return ("Master in the bitmap's pixels (72 x 112), drawn at 4x; replaces cards.dll bitmap %d.\n"
			"Written by desktop/cards/faces/gen_faces.py, never by hand.") % resource
	return ("Review only (%s), not shipped. Master in the bitmap's pixels (72 x 112), drawn at 4x; an alternative for cards.dll bitmap %d.\n"
		"Written by desktop/cards/faces/gen_faces.py (its alternatives option), never by hand.") % (direction, resource)


def vertical(gradient_id, top, bottom, stops):
	return '<linearGradient id="%s" x1="0" y1="%s" x2="0" y2="%s" gradientUnits="userSpaceOnUse">%s</linearGradient>' % (
		gradient_id, number(top), number(bottom), "".join('<stop offset="%s" stop-color="%s"%s/>' % (number(offset), colour,
		"" if opacity == 1 else ' stop-opacity="%s"' % number(opacity)) for offset, colour, opacity in ((s + (1,))[:3] for s in stops)))


def rounded_rect(x, y, width, height, radius, fill="none", stroke=None, stroke_width=1, extra=""):
	stroke_part = ' stroke="%s" stroke-width="%s"' % (stroke, number(stroke_width)) if stroke else ""
	return '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s"%s%s/>' % (number(x), number(y), number(width), number(height), number(radius), fill,
		stroke_part, extra)


def rotated_copy(body):
	"""The same drawing turned half a turn about the card's centre: the lower half of a double-ended court."""
	return '<g transform="rotate(180 %s %s)">%s</g>' % (number(WIDTH / 2), number(HEIGHT / 2), body)
