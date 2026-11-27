#!/usr/bin/env python3
# Review-only card-face alternative B, "Horizon": every face is a window onto the same horizon as the sunset back. The pips sit on a faint dawn sky with
# a gold horizon line, the ace is its suit rising as the sun over the dusk arcs, and the courts are night panels with a celestial emblem
# above the water and its reflection below: the king the crowned sun, the queen the moon, the jack the evening star.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# The panel has the back's frame (a cream margin and a thin gold border), so a face and a back read as one deck; the index sits in the
# margin above it, where cardlib's 16-row overlap shows it. The courts' sky leans rose for the red suits and indigo for the black ones.
# Deterministic: no randomness, no clock and no environment input.
import math
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "faces"))
import faces as F  # noqa: E402

NAME = "horizon"
TITLE = "B, Horizon"
PIP_HEIGHT = 12.5
PANEL = (12.5, 15.5, 47, 81)  # x, y, width, height: the window onto the horizon
HORIZON_Y = 56
NIGHT = "#141634"
WATER_TOP = "#262c5e"
STARS = ((18, 21, 0.6), (25, 30, 0.45), (52, 22, 0.7), (47, 31, 0.45), (20, 44, 0.5), (55, 41, 0.5), (29, 19, 0.4), (43, 18, 0.4))


def panel_rect(fill, stroke=F.GOLD_LINE):
	x, y, width, height = PANEL
	return F.rounded_rect(x, y, width, height, 3, fill=fill, stroke=stroke)


def ink(gradient_id, colour):
	"""The horizon line: the colour in the middle, fading out at both ends, as the back's horizon is."""
	return ('<linearGradient id="%s" x1="13" y1="0" x2="59" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="%s" stop-opacity="0"/>'
		'<stop offset="0.5" stop-color="%s"/><stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>') % (gradient_id, colour, colour, colour)


def day_defs():
	sky = F.vertical("sky", 16, 96, ((0, F.mix(F.CREAM, F.PURPLE[100], 0.2)), (0.5, F.mix(F.CREAM, F.PALE, 0.7)), (1, F.mix(F.CREAM, F.PURPLE[100], 0.1))))
	return sky + ink("line", F.ORANGE[200]) + '<clipPath id="panel"><rect x="13" y="16" width="46" height="80" rx="2.5"/></clipPath>'


def day_panel():
	return panel_rect("url(#sky)") + '<rect x="13" y="%s" width="46" height="1" fill="url(#line)"/>' % F.number(HORIZON_Y - 0.5)


def frame():
	return '<rect x="0" y="0" width="72" height="112" fill="%s"/>' % F.CREAM


def mirror(body):
	"""A reflection in the water: the drawing flipped about the horizon."""
	return '<g transform="matrix(1 0 0 -1 0 %s)">%s</g>' % (F.number(2 * HORIZON_Y), body)


def glints(colour, opacity=1.0):
	return "".join('<rect x="%s" y="%s" width="%s" height="1" rx="0.5" fill="%s" fill-opacity="%s"/>' % (F.number(36 - width / 2), F.number(y), F.number(width),
		colour, F.number(opacity * alpha)) for y, width, alpha in ((60, 18, 0.8), (64.5, 12, 0.6), (69, 7, 0.45), (73.5, 4, 0.3)))


def pips(rank_index, suit):
	colour = F.suit_colour(suit)
	layout = F.pip_layout(rank_index + 1, top=23, bottom=89)
	return day_defs(), day_panel() + "".join(F.suit_path(suit, x, y, PIP_HEIGHT, colour, flip=flip) for x, y, flip in layout)


def ace(suit):
	"""The suit as the sun: risen just clear of the horizon over three dusk arcs, its reflection and glints in the water below."""
	colour = F.suit_colour(suit)
	defs = day_defs() + '<clipPath id="above"><rect x="13" y="16" width="46" height="%s"/></clipPath>' % F.number(HORIZON_Y - 16)
	defs += '<clipPath id="below"><rect x="13" y="%s" width="46" height="40"/></clipPath>' % F.number(HORIZON_Y)
	arcs = "".join('<circle cx="36" cy="%d" r="%s" fill="%s"/>' % (HORIZON_Y, F.number(radius), F.mix(colour, F.CREAM, tint))
		for radius, tint in ((22, 0.84), (17.5, 0.74), (13.5, 0.62)))
	sun = F.suit_path(suit, 36, 42.5, 24, colour)
	body = "".join([
		panel_rect("url(#sky)"),
		'<g clip-path="url(#above)">%s</g>' % arcs,
		'<g clip-path="url(#below)" opacity="0.16">%s</g>' % mirror(arcs + sun),
		sun,
		'<rect x="13" y="%s" width="46" height="1.2" fill="url(#line)"/>' % F.number(HORIZON_Y - 0.6),
		glints(F.ORANGE[200], 0.9),
	])
	return defs, body


# ---- the courts: night panels with an emblem over the water ----------------------------------------------------------------------------------
def night_defs(suit):
	low = F.SKY7 if suit in F.WARM else F.HORIZON
	defs = F.vertical("night", 16, HORIZON_Y, ((0, F.SKY1), (0.55, F.SKY4), (1, low)))
	defs += F.vertical("water", HORIZON_Y, 96, ((0, WATER_TOP), (1, NIGHT)))
	defs += ink("line", F.BRAND_GOLD)
	defs += '<clipPath id="panel"><rect x="13" y="16" width="46" height="80" rx="2.5"/></clipPath>'
	defs += '<clipPath id="above"><rect x="13" y="16" width="46" height="%s"/></clipPath>' % F.number(HORIZON_Y - 16)
	defs += '<clipPath id="below"><rect x="13" y="%s" width="46" height="40"/></clipPath>' % F.number(HORIZON_Y)
	return defs


def stars():
	return "".join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (F.number(x), F.number(y), F.number(radius), F.PALE) for x, y, radius in STARS)


def sun_king(suit):
	"""The risen sun in a crown of rays, the suit in pale on its face."""
	rays = []
	for step in range(12):
		angle = math.radians(step * 30 + 15)
		rays.append("M%s %s L%s %s" % (F.number(36 + 11 * math.cos(angle)), F.number(39 + 11 * math.sin(angle)), F.number(36 + 14 * math.cos(angle)),
			F.number(39 + 14 * math.sin(angle))))
	return "".join([
		'<circle cx="36" cy="39" r="16.5" fill="%s" fill-opacity="0.35"/>' % F.SKY7,
		'<path d="%s" stroke="%s" stroke-width="1.4" stroke-linecap="round"/>' % (" ".join(rays), F.BRAND_GOLD),
		'<circle cx="36" cy="39" r="9" fill="%s"/>' % F.ORANGE[200],
		'<ellipse cx="33.2" cy="35.2" rx="3.4" ry="1.9" fill="%s" fill-opacity="0.75"/>' % F.PALE,
		'<path d="M29.5 29 L31.5 23.5 L34 27 L36 21.5 L38 27 L40.5 23.5 L42.5 29 Z" fill="%s"/>' % F.BRAND_GOLD,  # the crown on the sun
		'<rect x="29.5" y="28.4" width="13" height="1.8" rx="0.6" fill="%s"/>' % F.ORANGE[200],
		F.suit_path(suit, 36, 41, 7, F.mix(F.ORANGE[500], F.ORANGE[200], 0.1)),
	])


def moon_queen(suit):
	"""The crescent moon with a small tiara of stars, the suit in pale beside it."""
	return "".join([
		'<circle cx="36" cy="39" r="14" fill="%s" fill-opacity="0.3"/>' % F.PURPLE[300],
		'<path d="M38.5 29.5 A10 10 0 1 0 38.5 48.5 A8.2 8.2 0 1 1 38.5 29.5 Z" fill="%s"/>' % F.PALE,  # the crescent
		"".join('<path d="M%s %s l1 2.4 2.4 1 -2.4 1 -1 2.4 -1 -2.4 -2.4 -1 2.4 -1 Z" fill="%s"/>' % (F.number(x), F.number(y), F.BRAND_GOLD)
			for x, y in ((30, 22), (36, 19.5), (42, 22))),
		F.suit_path(suit, 40, 39, 7.5, F.BRAND_GOLD),
	])


def star_jack(suit):
	"""The evening star, bright above the horizon, with the suit hanging under it."""
	return "".join([
		'<circle cx="36" cy="34" r="11" fill="%s" fill-opacity="0.3"/>' % F.PURPLE[300],
		'<path d="M36 22 C36.8 30 38 31.2 46 34 C38 36.8 36.8 38 36 46 C35.2 38 34 36.8 26 34 C34 31.2 35.2 30 36 22 Z" fill="%s"/>' % F.BRAND_GOLD,
		'<circle cx="36" cy="34" r="2" fill="%s"/>' % F.PALE,
		F.suit_path(suit, 36, 50.5, 6.5, F.PALE),
	])


EMBLEMS = {10: star_jack, 11: moon_queen, 12: sun_king}


def night_scene(emblem, line_colour=F.BRAND_GOLD):
	return "".join([
		panel_rect("url(#night)", stroke=F.GOLD_LINE),
		'<g clip-path="url(#panel)"><rect x="13" y="%s" width="46" height="40" fill="url(#water)"/>' % F.number(HORIZON_Y),
		'<g clip-path="url(#above)">%s%s</g>' % (stars(), emblem),
		'<g clip-path="url(#below)" opacity="0.32">%s</g>' % mirror(emblem),
		'<rect x="13" y="%s" width="46" height="1.2" fill="url(#line)"/>' % F.number(HORIZON_Y - 0.6),
		glints(F.ORANGE[200], 0.8),
		"</g>",
	])


def court(rank_index, suit):
	return night_defs(suit), night_scene(EMBLEMS[rank_index](suit))


def face(rank_index, suit):
	if rank_index == 0:
		defs, art = ace(suit)
	elif rank_index >= 10:
		defs, art = court(rank_index, suit)
	else:
		defs, art = pips(rank_index, suit)
	body = frame() + art + F.index(F.RANKS[rank_index], suit)
	return F.document(F.card_title(TITLE, rank_index, suit), F.card_note(TITLE, F.resource_id(rank_index, suit)), body, defs)


def joker():
	"""The eclipse: the moon across the sun, a gold corona round it, over the water; JOKER down the left margin in the index font."""
	corona = []
	for step in range(16):
		angle = math.radians(step * 22.5)
		length = 15 if step % 2 else 17
		corona.append("M%s %s L%s %s" % (F.number(36 + 11 * math.cos(angle)), F.number(38 + 11 * math.sin(angle)), F.number(36 + length * math.cos(angle)),
			F.number(38 + length * math.sin(angle))))
	emblem = "".join([
		'<path d="%s" stroke="%s" stroke-width="1.2" stroke-linecap="round"/>' % (" ".join(corona), F.BRAND_GOLD),
		'<circle cx="36" cy="38" r="9.6" fill="%s"/>' % F.ORANGE[200],
		'<circle cx="37.6" cy="37" r="8.6" fill="%s"/>' % F.SKY1,
		'<circle cx="28.4" cy="40.6" r="1.1" fill="%s"/>' % F.PALE,
	])
	word = []
	for position, letter in enumerate("JOKER"):
		word += F.bitmap_cells(F.RANK_GLYPHS[letter], 3, 4 + position * 10)
		word += F.bitmap_cells(F.RANK_GLYPHS[letter], 3, 4 + position * 10, flip=True)
	defs = night_defs("spades")
	body = frame() + night_scene(emblem) + F.pixels(word, F.DUSK)
	return F.document("Afterglow card face, %s: joker" % TITLE, F.card_note(TITLE, F.JOKER), body, defs)


def free_card():
	"""An empty window: the dawn sky and its horizon with nothing on it yet, and the outline of the sun about to rise."""
	defs = day_defs()
	body = "".join([
		frame(),
		day_panel(),
		'<path d="M26 56 A10 10 0 0 1 46 56" fill="none" stroke="%s" stroke-width="1.2" stroke-dasharray="2 1.6"/>' % F.GOLD_LINE,
		glints(F.GOLD_LINE, 0.6),
	])
	return F.document("Afterglow card face, %s: free cell" % TITLE, F.card_note(TITLE, F.FREE_CARD), body, defs)
