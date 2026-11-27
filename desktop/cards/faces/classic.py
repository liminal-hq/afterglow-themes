#!/usr/bin/env python3
# The Afterglow card faces (selected set, "Classic dusk"): the traditional layout on a cream face in a thin gold border, rose and
# dusk-indigo suits, double-ended courts whose king wears a rising-sun crown, a jester joker and a sun-over-horizon free cell.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# Every face carries the index (rank and small suit) at the top left and turned at the bottom right, as a traditional deck does: cardlib
# shows the top-left one where cards overlap and the whole card on top of a pile. Three court figures (king, queen, jack) are drawn once and
# coloured by suit: the robe takes the suit's colour, the trim is
# the brand gold, and a small cream pip on the chest names the suit. The lower half of each court is the upper half turned, as on a
# traditional deck, and a gold horizon line divides them. Deterministic: no randomness, no clock and no environment input.
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import faces as F  # noqa: E402

NAME = "classic"
TITLE = "Classic dusk"
PIP_HEIGHT = 13
SKIN = F.PALE
SKIN_LINE = F.mix(F.ORANGE[400], F.PALE, 0.35)
TRIM = F.ORANGE[200]


def frame():
	"""The cream face and its thin gold border on the third pixel ring, inside cardlib's black line and a cream row."""
	return '<rect x="0" y="0" width="72" height="112" fill="%s"/>%s' % (F.CREAM, F.rounded_rect(2.5, 2.5, 67, 107, 3, stroke=F.GOLD_LINE))


def pips(rank_index, suit):
	colour = F.suit_colour(suit)
	return "".join(F.suit_path(suit, x, y, PIP_HEIGHT, colour, flip=flip) for x, y, flip in F.pip_layout(rank_index + 1))


def ace(suit):
	"""The big suit inside a thin gold sun ring with short rays: the ace as the day's first light."""
	colour = F.suit_colour(suit)
	rays = []
	for step in range(16):
		angle = F.math.radians(step * 22.5)
		inner, outer = 21.5, 24.5 if step % 2 else 26
		rays.append("M%s %s L%s %s" % (F.number(36 + inner * F.math.cos(angle)), F.number(56 + inner * F.math.sin(angle)),
			F.number(36 + outer * F.math.cos(angle)), F.number(56 + outer * F.math.sin(angle))))
	return "".join([
		'<circle cx="36" cy="56" r="19.5" fill="none" stroke="%s" stroke-width="1"/>' % F.GOLD_LINE,
		'<path d="%s" fill="none" stroke="%s" stroke-width="1" stroke-linecap="round"/>' % (" ".join(rays), F.GOLD_LINE),
		F.suit_path(suit, 36, 56, 26, colour),
	])


# ---- the courts: the upper half of each figure, in card pixels; the lower half is this turned ------------------------------------------------
def robe(suit, colour):
	"""Square shoulders and a robe down to the horizon line, a lighter front panel, a gold collar and a cream suit pip on the chest."""
	shade = F.mix(colour, F.CREAM, 0.3)
	return "".join([
		'<path d="M15.5 56 L15.5 51 C15.5 45.5 21 42.5 29 41.5 L43 41.5 C51 42.5 56.5 45.5 56.5 51 L56.5 56 Z" fill="%s"/>' % colour,
		'<path d="M31 42 L41 42 L42 56 L30 56 Z" fill="%s"/>' % shade,
		'<path d="M28 41.5 L36 47.5 L44 41.5 L41.5 40 L36 44 L30.5 40 Z" fill="%s"/>' % TRIM,
		F.suit_path(suit, 36, 51.5, 6, F.CREAM if suit not in F.WARM else F.mix(colour, F.DUSK, 0.35)),
	])


def head(cy=32, radius=7):
	eyes = '<rect x="32.6" y="%s" width="1.4" height="1.6" rx="0.6" fill="%s"/><rect x="38" y="%s" width="1.4" height="1.6" rx="0.6" fill="%s"/>' % (
		F.number(cy - 0.8), F.DUSK, F.number(cy - 0.8), F.DUSK)
	cheeks = '<circle cx="31.6" cy="%s" r="1.1" fill="%s" fill-opacity="0.45"/><circle cx="40.4" cy="%s" r="1.1" fill="%s" fill-opacity="0.45"/>' % (
		F.number(cy + 2.2), F.RED[100], F.number(cy + 2.2), F.RED[100])
	return '<rect x="33.5" y="%s" width="5" height="5" fill="%s"/><circle cx="36" cy="%s" r="%s" fill="%s" stroke="%s" stroke-width="0.6"/>%s%s' % (
		F.number(cy + 4), SKIN, F.number(cy), F.number(radius), SKIN, SKIN_LINE, eyes, cheeks)


def king(suit):
	colour = F.suit_colour(suit)
	rays = "".join('<path d="M%s %s L%s %s" stroke="%s" stroke-width="1.3" stroke-linecap="round"/>' % (
		F.number(36 + 6.6 * F.math.cos(F.math.radians(angle))), F.number(24 - 6.6 * F.math.sin(F.math.radians(angle))),
		F.number(36 + 9 * F.math.cos(F.math.radians(angle))), F.number(24 - 9 * F.math.sin(F.math.radians(angle))), F.ORANGE[200])
		for angle in (15, 52, 90, 128, 165))
	beard = F.mix(F.DUSK, F.CREAM, 0.3)
	return "".join([
		'<path d="M18 40 A18 18 0 0 1 54 40" fill="none" stroke="%s" stroke-width="2"/>' % F.mix(colour, F.CREAM, 0.82),  # the dusk arcs
		'<path d="M22 40 A14 14 0 0 1 50 40" fill="none" stroke="%s" stroke-width="2"/>' % F.mix(colour, F.CREAM, 0.9),
		robe(suit, colour),
		head(),
		'<path d="M29 33 C29 41 33 43.5 36 43.5 C39 43.5 43 41 43 33 C41 36.5 38.5 37 36 37 C33.5 37 31 36.5 29 33 Z" fill="%s"/>' % beard,
		'<path d="M33 36.5 C34.5 35.5 37.5 35.5 39 36.5 C37.5 37.2 34.5 37.2 33 36.5 Z" fill="%s"/>' % beard,  # the moustache
		rays,
		'<path d="M31 24 A5 5 0 0 1 41 24 Z" fill="%s"/>' % F.ORANGE[200],  # the rising sun of the crown
		'<path d="M28.5 24 L43.5 24 L43 27.4 L29 27.4 Z" fill="%s"/>' % F.ORANGE[300],
		'<rect x="34.8" y="24.8" width="2.4" height="1.8" rx="0.5" fill="%s"/>' % F.RED[200],
	])


def queen(suit):
	colour = F.suit_colour(suit)
	hair = F.SKY7 if suit not in F.WARM else F.SKY4
	return "".join([
		'<path d="M27 33 C26 25 30 23.5 36 23.5 C42 23.5 46 25 45 33 L47 44 L25 44 Z" fill="%s"/>' % hair,  # long hair behind
		robe(suit, colour),
		head(),
		'<path d="M29 29.5 C30 25.5 33 24.8 36 24.8 C39 24.8 42 25.5 43 29.5 C40.5 27.4 38 27 36 27 C34 27 31.5 27.4 29 29.5 Z" fill="%s"/>' % hair,
		'<path d="M30 25.5 L31.6 20.5 L33.8 23.6 L36 18.6 L38.2 23.6 L40.4 20.5 L42 25.5 Z" fill="%s"/>' % TRIM,  # the tiara
		'<circle cx="36" cy="22.6" r="1.2" fill="%s"/>' % F.RED[200],
	])


def jack(suit):
	colour = F.suit_colour(suit)
	cap = F.mix(F.DUSK, F.CREAM, 0.12) if suit in F.WARM else F.ROSE
	return "".join([
		robe(suit, colour),
		head(),
		'<path d="M29.4 31 C29.4 34 30 36 31 37 L29.5 37 C28.5 35 28.5 32 29 30 Z M42.6 31 C42.6 34 42 36 41 37 L42.5 37 C43.5 35 43.5 32 43 30 Z" fill="%s"/>' % F.SKY7,
		'<path d="M42.5 22.5 C45.5 18.5 49.5 17.6 53 18.6 C49.8 19.6 47.2 21.8 44.8 25.5 Z" fill="%s"/>' % F.ORANGE[200],  # the feather
		'<path d="M28.3 30 C27.5 22.5 31.5 20.5 36.5 20.5 C41.5 20.5 45.5 22 44.8 28.5 L43.5 27.2 L29.5 27.2 Z" fill="%s"/>' % cap,  # the cap
		'<rect x="28.6" y="26.6" width="15.6" height="2" rx="0.7" fill="%s"/>' % TRIM,
	])


COURTS = {10: jack, 11: queen, 12: king}


def court(rank_index, suit):
	"""A double-ended figure in a framed panel with a gold horizon at the centre."""
	upper = COURTS[rank_index](suit)
	clip = '<clipPath id="half"><rect x="13" y="16" width="46" height="40"/></clipPath>'
	half = '<g clip-path="url(#half)">%s</g>' % upper
	return clip, "".join([
		F.rounded_rect(12.5, 15.5, 47, 81, 2, fill=F.mix(F.CREAM, F.PALE, 0.35), stroke=F.GOLD_LINE),
		half,
		F.rotated_copy(half),
		'<rect x="13" y="55.4" width="46" height="1.2" fill="%s"/>' % F.GOLD_LINE,
	])


def face(rank_index, suit):
	defs, art = "", ""
	if rank_index == 0:
		art = ace(suit)
	elif rank_index >= 10:
		defs, art = court(rank_index, suit)
	else:
		art = pips(rank_index, suit)
	body = frame() + art + F.index(F.RANKS[rank_index], suit)
	return F.document(F.card_title(TITLE, rank_index, suit), F.card_note(TITLE, F.resource_id(rank_index, suit), selected=True), body, defs)


def jester():
	"""The upper half of the joker: a jester in a parti-coloured cap with sun bells, a scalloped gold ruff, a harlequin doublet and a
	marotte (a fool's sceptre with a small sun)."""
	diamonds = "".join('<path d="M%s 44.5 l2.6 4 -2.6 4 -2.6 -4 Z M%s 52.5 l2.6 4 -2.6 4 -2.6 -4 Z" fill="%s"/>' % (F.number(x), F.number(x + 2.6), shade)
		for x, shade in ((21.5, F.mix(F.ROSE, F.CREAM, 0.3)), (49.5, F.mix(F.DUSK, F.CREAM, 0.3))))
	ruff = "".join('<circle cx="%s" cy="42" r="2.3" fill="%s"/>' % (F.number(28 + step * 2.67), TRIM) for step in range(7))
	return "".join([
		'<path d="M18 42 A18 18 0 0 1 54 42" fill="none" stroke="%s" stroke-width="2"/>' % F.mix(F.PURPLE[200], F.CREAM, 0.75),  # the dusk arcs
		'<path d="M22 42 A14 14 0 0 1 50 42" fill="none" stroke="%s" stroke-width="2"/>' % F.mix(F.PURPLE[200], F.CREAM, 0.86),
		'<path d="M15.5 56 L15.5 51 C15.5 45.5 21 42.5 29 41.5 L36 41.5 L36 56 Z" fill="%s"/>' % F.ROSE,
		'<path d="M36 41.5 L43 41.5 C51 42.5 56.5 45.5 56.5 51 L56.5 56 L36 56 Z" fill="%s"/>' % F.DUSK,
		'<g clip-path="url(#doublet)">%s</g>' % diamonds,
		'<path d="M49 56 L52.2 31.5" stroke="%s" stroke-width="1.4" stroke-linecap="round"/>' % F.ORANGE[300],  # the marotte
		'<circle cx="52.5" cy="29.5" r="2.6" fill="%s"/><circle cx="51.8" cy="28.8" r="0.9" fill="%s"/>' % (F.ORANGE[200], F.PALE),
		head(),
		'<path d="M33.5 35.2 C34.8 36.8 37.2 36.8 38.5 35.2" fill="none" stroke="%s" stroke-width="0.9" stroke-linecap="round"/>' % F.RED[400],  # the smile
		ruff,
		'<path d="M29 29 L22 17.5 L31.5 23 L36 12.5 L40.5 23 L50 17.5 L43 29 Z" fill="%s"/>' % F.ROSE,  # the cap: rose on the left
		'<path d="M36 12.5 L40.5 23 L50 17.5 L43 29 L36 29 Z" fill="%s"/>' % F.DUSK,  # and dusk on the right
		'<path d="M28.6 26.6 L43.4 26.6 L43 30 L29 30 Z" fill="%s"/>' % TRIM,
		"".join('<circle cx="%s" cy="%s" r="1.9" fill="%s"/><circle cx="%s" cy="%s" r="0.7" fill="%s"/>' % (x, y, F.ORANGE[200], F.number(x - 0.5),
			F.number(y - 0.5), F.PALE) for x, y in ((22, 17.5), (36, 12.5), (50, 17.5))),
	])


def joker():
	"""A double-ended jester in the courts' framed panel, with JOKER down the left margin and turned at the right, in the index font."""
	clip = ('<clipPath id="half"><rect x="13" y="16" width="46" height="40"/></clipPath>'
		'<clipPath id="doublet"><path d="M15.5 56 L15.5 51 C15.5 45.5 21 42.5 29 41.5 L43 41.5 C51 42.5 56.5 45.5 56.5 51 L56.5 56 Z"/></clipPath>')
	half = '<g clip-path="url(#half)">%s</g>' % jester()
	word = []
	for position, letter in enumerate("JOKER"):
		word += F.bitmap_cells(F.RANK_GLYPHS[letter], 4, 4 + position * 10)
		word += F.bitmap_cells(F.RANK_GLYPHS[letter], 4, 4 + position * 10, flip=True)
	body = "".join([
		frame(),
		F.rounded_rect(12.5, 15.5, 47, 81, 2, fill=F.mix(F.CREAM, F.PALE, 0.35), stroke=F.GOLD_LINE),
		half,
		F.rotated_copy(half),
		'<rect x="13" y="55.4" width="46" height="1.2" fill="%s"/>' % F.GOLD_LINE,
		F.pixels(word, F.DUSK),
	])
	return F.document("Afterglow card face, %s: joker" % TITLE, F.card_note(TITLE, F.JOKER, selected=True), body, clip)


def free_card():
	"""An empty cell: no index and no suit, the gold border, a dashed inner frame where a card may go, and the Afterglow emblem in a gold
	medallion: the sun half risen on a gold horizon under three dusk arcs, its glints on the water. Light, so it never reads as a back."""
	arcs = "".join('<circle cx="36" cy="58" r="%s" fill="%s"/>' % (F.number(radius), colour)
		for radius, colour in ((18, F.mix(F.SKY4, F.CREAM, 0.55)), (14.5, F.mix(F.SKY7, F.CREAM, 0.42)), (11, F.mix(F.SKY7, F.CREAM, 0.22))))
	glints = "".join('<rect x="%s" y="%s" width="%s" height="1.1" rx="0.55" fill="%s" fill-opacity="%s"/>' % (F.number(36 - width / 2), F.number(y),
		F.number(width), F.ORANGE[300], F.number(alpha)) for y, width, alpha in ((61.5, 16, 0.9), (65, 11, 0.7), (68.5, 6, 0.5)))
	stars = "".join('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (F.number(x), F.number(y), F.number(radius), F.ORANGE[200])
		for x, y, radius in ((26, 46, 0.7), (47, 44, 0.8), (42, 40.5, 0.5), (30, 41, 0.5)))
	defs = ('<clipPath id="medallion"><circle cx="36" cy="56" r="20"/></clipPath>'
		'<clipPath id="sky"><rect x="14" y="30" width="44" height="28"/></clipPath>')
	body = "".join([
		frame(),
		F.rounded_rect(8.5, 8.5, 55, 95, 2, stroke=F.mix(F.GOLD_LINE, F.CREAM, 0.45), extra=' stroke-dasharray="2 2"'),
		'<circle cx="36" cy="56" r="20" fill="%s"/>' % F.mix(F.PURPLE[100], F.CREAM, 0.45),
		'<g clip-path="url(#medallion)">',
		'<rect x="14" y="58" width="44" height="22" fill="%s"/>' % F.mix(F.SKY4, F.CREAM, 0.62),
		'<g clip-path="url(#sky)">%s%s<circle cx="36" cy="58" r="7.5" fill="%s"/><ellipse cx="33.8" cy="54.6" rx="2.8" ry="1.5" fill="%s" fill-opacity="0.8"/></g>' % (
			stars, arcs, F.ORANGE[200], F.PALE),
		glints,
		'</g>',
		'<rect x="16" y="57.4" width="40" height="1.3" rx="0.65" fill="%s"/>' % F.ORANGE[300],
		'<circle cx="36" cy="56" r="20" fill="none" stroke="%s" stroke-width="1.2"/>' % F.GOLD_LINE,
		'<circle cx="36" cy="56" r="22.2" fill="none" stroke="%s" stroke-width="0.7"/>' % F.mix(F.GOLD_LINE, F.CREAM, 0.4),
		"".join('<path d="M%s %s l0.9 2.1 2.1 0.9 -2.1 0.9 -0.9 2.1 -0.9 -2.1 -2.1 -0.9 2.1 -0.9 Z" fill="%s"/>' % (x, y - 3, F.ORANGE[200])
			for x, y in ((16, 19), (56, 19), (16, 93), (56, 93))),
	])
	return F.document("Afterglow card face, %s: free cell" % TITLE, F.card_note(TITLE, F.FREE_CARD, selected=True), body, defs)
