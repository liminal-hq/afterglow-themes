#!/usr/bin/env python3
# Draw the Afterglow card art for ReactOS's card games as vector masters: the card back that replaces the one carrying the ReactOS logo, two
# alternative backs for review, and the empty-pile marks redrawn on the proposed dusk felt.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
#   python3 gen_cards.py OUT_DIR
#
# Writes OUT_DIR/card-back-sunset.svg (selected), card-x.svg, card-o.svg, alternatives/card-back-lattice.svg and
# alternatives/card-back-rays.svg. Solitaire and Spider Solitaire draw their cards from cards.dll's bitmaps (72 x 112, cardlib's
# LoadCardBitmapsFromLibrary), and the back they start with is bitmap 54 (Background_1, cardlib's nBackCardIdx 53), the only back that
# carries the ReactOS logo; the other eleven backs are neutral patterns and stay. cardlib paints its own black border over each card's
# outer pixel ring and skips the corner pixels, so the art fills the whole bitmap and keeps its detail inside that ring. Each master is drawn
# in the bitmap's own pixels (its viewBox is 72 x 112) and sized four times larger, so render.py draws it at 4x and box-filters it down, as
# the dialog art is. The colours are set E's (desktop/icons/gen_e.py), so the backs are the icon set's sky, sun and gold. Deterministic: no
# randomness, no clock and no environment input.
import importlib.util
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
DESKTOP = os.path.dirname(HERE)
SCALE = 4
WIDTH, HEIGHT = 72, 112


def load(name, path):
	spec = importlib.util.spec_from_file_location(name, path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


GEN = load("gen_e", os.path.join(DESKTOP, "icons", "gen_e.py"))
ORANGE, RED, PURPLE, INDIGO, PAPER = GEN.ORANGE, GEN.RED, GEN.PURPLE, GEN.INDIGO, GEN.PAPER
SKY1, SKY4, SKY7, HORIZON, PALE, BRAND_GOLD, DARK, _n, mix = GEN.SKY1, GEN.SKY4, GEN.SKY7, GEN.HORIZON, GEN.PALE, GEN.BRAND_GOLD, GEN.DARK, GEN._n, GEN.mix

# The felt: cardlib paints the table PALETTERGB(0, 80, 0), a constant in CardWindow's constructor compiled into sol.exe and spider.exe
# (mov dword [ebx+0x144], 0x02005000), and derives the empty-pile sinks from it. The proposed Afterglow felt is the dusk sky's deepest
# tone; the empty-pile marks below are drawn on it, so they and the felt patch go together.
FELT = SKY1
FELT_ALTERNATIVE = SKY4
NIGHT = "#141634"  # the water under the horizon: a step below the felt

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


def vertical(gradient_id, top, bottom, stops):
	return '<linearGradient id="%s" x1="0" y1="%s" x2="0" y2="%s" gradientUnits="userSpaceOnUse">%s</linearGradient>' % (
		gradient_id, top, bottom, "".join('<stop offset="%s" stop-color="%s"/>' % (_n(offset), colour) for offset, colour in stops))


def ink(gradient_id, left, right):
	"""The gold ink line of the boot logo and the dialogs: brand gold in the middle, fading out at both ends."""
	return ('<linearGradient id="%s" x1="%s" y1="0" x2="%s" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="%s" stop-opacity="0"/>'
		'<stop offset="0.5" stop-color="%s"/><stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>') % (gradient_id, left, right, ORANGE[200],
		BRAND_GOLD, ORANGE[200])


def frame(panel_fill):
	"""The card's white margin, the panel and its thin gold border, as every back has them."""
	return "".join([
		'<rect x="0" y="0" width="%d" height="%d" fill="%s"/>' % (WIDTH, HEIGHT, PAPER[900]),
		'<rect x="3.5" y="3.5" width="65" height="105" rx="3" fill="%s"/>' % panel_fill,
		'<rect x="5.75" y="5.75" width="60.5" height="100.5" rx="2" fill="none" stroke="%s" stroke-width="1"/>' % BRAND_GOLD,
	])


# ---- the selected back: the Afterglow sun on its horizon (replaces cards.dll bitmap 54) -------------------------------------------------------------
STARS = ((15, 17, 0.7), (25, 12, 0.5), (49, 15, 0.8), (58, 25, 0.5), (12, 33, 0.5), (41, 26, 0.5), (60, 41, 0.6), (21, 44, 0.45))


def sunset():
	"""The sun half risen over a gold horizon in the boot logo's language: the sky from the dusk's deepest tone to its rose, the sun's dusk
	arcs, a few stars, and the water under the horizon with the sun's glints on it."""
	horizon = 70
	defs = vertical("sky", 4, horizon, ((0, SKY1), (0.55, SKY4), (1, SKY7)))
	defs += vertical("water", horizon, 108, ((0, "#262c5e"), (1, NIGHT)))
	defs += ink("horizon", 6, 66)
	defs += '<clipPath id="above"><rect x="3.5" y="3.5" width="65" height="%s"/></clipPath>' % _n(horizon - 3.5)
	defs += '<clipPath id="panel"><rect x="3.5" y="3.5" width="65" height="105" rx="3"/></clipPath>'
	arcs = "".join('<circle cx="36" cy="%d" r="%s" fill="%s"/>' % (horizon, _n(radius), colour)
		for radius, colour in ((30, "#2e3468"), (24, SKY4), (18.5, "#5a3f6c"), (14, SKY7)))
	stars = "".join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (_n(x), _n(y), _n(radius), PALE) for x, y, radius in STARS)
	glints = "".join('<rect x="%s" y="%s" width="%s" height="1" rx="0.5" fill="%s" fill-opacity="%s"/>' % (_n(36 - width / 2), _n(y), _n(width), ORANGE[200],
		_n(opacity)) for y, width, opacity in ((74, 16, 0.85), (78.5, 11, 0.7), (83, 7, 0.55), (87.5, 4, 0.4)))
	body = "".join([
		frame("url(#sky)"),
		'<g clip-path="url(#panel)">',
		'<rect x="3.5" y="%d" width="65" height="%d" fill="url(#water)"/>' % (horizon, 108.5 - horizon),
		'<g clip-path="url(#above)">%s%s<circle cx="36" cy="%d" r="10" fill="%s"/><ellipse cx="33" cy="%s" rx="4" ry="2.2" fill="%s" fill-opacity="0.8"/></g>' % (
			stars, arcs, horizon, ORANGE[200], _n(horizon - 5), PALE),
		'<rect x="5" y="%s" width="62" height="1.6" rx="0.8" fill="url(#horizon)"/>' % _n(horizon - 0.8),
		glints,
		"</g>",
		'<rect x="5.75" y="5.75" width="60.5" height="100.5" rx="2" fill="none" stroke="%s" stroke-width="1"/>' % BRAND_GOLD,
	])
	return document("Afterglow card back: the sun on the horizon (selected)",
		"Master in the bitmap's pixels (72 x 112), drawn at 4x; replaces cards.dll bitmap 54 (Background_1, the back\nSolitaire and Spider Solitaire start with), the one back that carries the ReactOS logo.", body, defs)


# ---- alternative backs (review only) --------------------------------------------------------------------------------------------------------------
def lattice():
	"""A dusk lattice of thin horizon-violet diagonals with small gold suns at the crossings, and a sun medallion in the middle."""
	defs = vertical("sky", 4, 108, ((0, SKY1), (0.5, SKY4), (1, SKY1)))
	defs += '<clipPath id="panel"><rect x="6.5" y="6.5" width="59" height="99" rx="1.5"/></clipPath>'
	defs += '<clipPath id="medal"><rect x="20" y="40" width="32" height="20"/></clipPath>'
	lines = []
	for index in range(-12, 13):
		offset = index * 9
		lines.append("M%s 0 L%s 112" % (_n(36 + offset - 56 * 0.6), _n(36 + offset + 56 * 0.6)))
		lines.append("M%s 0 L%s 112" % (_n(36 + offset + 56 * 0.6), _n(36 + offset - 56 * 0.6)))
	dots = []
	for row in range(-1, 15):
		for column in range(-1, 10):
			x = 36 + (column - 4) * 9 + (4.5 if row % 2 else 0)
			y = 56 + (row - 6) * 7.5
			dots.append('<circle cx="%s" cy="%s" r="0.9" fill="%s"/>' % (_n(x), _n(y), ORANGE[200]))
	body = "".join([
		frame("url(#sky)"),
		'<g clip-path="url(#panel)"><path d="%s" fill="none" stroke="%s" stroke-width="0.6"/>%s</g>' % (" ".join(lines), HORIZON, "".join(dots)),
		'<circle cx="36" cy="56" r="13" fill="%s" stroke="%s" stroke-width="1"/>' % (SKY1, BRAND_GOLD),
		'<g clip-path="url(#medal)"><circle cx="36" cy="60" r="10" fill="%s"/><circle cx="36" cy="60" r="7" fill="%s"/><circle cx="36" cy="60" r="5" fill="%s"/></g>' % (
			SKY4, SKY7, ORANGE[200]),
		'<rect x="25" y="59.4" width="22" height="1.2" rx="0.6" fill="%s"/>' % BRAND_GOLD,
	])
	return document("Afterglow card back: dusk lattice (review only)",
		"Review only, not shipped: an alternative for cards.dll bitmap 54, in the same frame as card-back-sunset.svg.", body, defs)


def rays():
	"""The whole sun at the centre of a violet-to-rose sky, its rays reaching to the gold border, the same either way up."""
	defs = '<radialGradient id="glow" cx="36" cy="56" r="60" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="%s"/><stop offset="0.45" stop-color="%s"/><stop offset="1" stop-color="%s"/></radialGradient>' % (
		SKY7, SKY4, SKY1)
	defs += '<clipPath id="panel"><rect x="6.5" y="6.5" width="59" height="99" rx="1.5"/></clipPath>'
	beams = []
	for index in range(24):
		angle = math.radians(index * 15 + 7.5)
		inner, outer = 14, 70
		beams.append("M%s %s L%s %s" % (_n(36 + inner * math.cos(angle)), _n(56 + inner * math.sin(angle)), _n(36 + outer * math.cos(angle)),
			_n(56 + outer * math.sin(angle))))
	body = "".join([
		frame("url(#glow)"),
		'<g clip-path="url(#panel)"><path d="%s" fill="none" stroke="%s" stroke-width="1.1" stroke-opacity="0.55" stroke-linecap="round"/></g>' % (
			" ".join(beams), ORANGE[200]),
		'<circle cx="36" cy="56" r="12" fill="%s" fill-opacity="0.35"/><circle cx="36" cy="56" r="9" fill="%s"/>' % (ORANGE[200], ORANGE[200]),
		'<ellipse cx="33" cy="52.5" rx="3.6" ry="2" fill="%s" fill-opacity="0.8"/>' % PALE,
	])
	return document("Afterglow card back: sun and rays (review only)",
		"Review only, not shipped: an alternative for cards.dll bitmap 54, in the same frame as card-back-sunset.svg.", body, defs)


# ---- the empty-pile marks on the dusk felt (cards.dll 67 and 68) -----------------------------------------------------------------------------------
def mark_x():
	body = '<rect x="0" y="0" width="%d" height="%d" fill="%s"/><path d="M22 42 L50 70 M50 42 L22 70" fill="none" stroke="%s" stroke-width="7" stroke-linecap="round"/>' % (
		WIDTH, HEIGHT, FELT, RED[200])
	return document("Afterglow empty-pile mark: the cross", "Master in the bitmap's pixels (72 x 112), drawn at 4x; replaces cards.dll bitmap 67 (XSign, cardlib's CS_EI_X), drawn on\nthe proposed dusk felt (%s), so it ships with the felt patch." % FELT, body)


def mark_o():
	body = '<rect x="0" y="0" width="%d" height="%d" fill="%s"/><circle cx="36" cy="56" r="16" fill="none" stroke="%s" stroke-width="6"/>' % (WIDTH, HEIGHT, FELT,
		ORANGE[200])
	return document("Afterglow empty-pile mark: the ring", "Master in the bitmap's pixels (72 x 112), drawn at 4x; replaces cards.dll bitmap 68 (OSign, cardlib's CS_EI_CIRC: Solitaire's\nempty deck, click to deal again), drawn on the proposed dusk felt (%s), so it ships with the felt patch." % FELT, body)


def main():
	if len(sys.argv) != 2:
		sys.exit("usage: gen_cards.py OUT_DIR")
	out = sys.argv[1]
	os.makedirs(os.path.join(out, "alternatives"), exist_ok=True)
	files = {
		"card-back-sunset.svg": sunset(),
		"card-x.svg": mark_x(),
		"card-o.svg": mark_o(),
		"alternatives/card-back-lattice.svg": lattice(),
		"alternatives/card-back-rays.svg": rays(),
	}
	for name, text in files.items():
		with open(os.path.join(out, name), "w") as handle:
			handle.write(text)
	print("card masters", len(files))


if __name__ == "__main__":
	main()
