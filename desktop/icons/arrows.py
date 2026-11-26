#!/usr/bin/env python3
# Afterglow shortcut-arrow overlay variants: the shell32 group 30 replacement, parameterised on six axes, with composite proofs and the sheet.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# The overlay is a full-size 32-bit alpha frame (16, 32 and 48) that ReactOS composites over the target icon at (0, 0). Only the
# bottom-left box carries art: 8 x 8 at 16, 11 x 11 at 32 and 16 x 16 at 48. The 48 and 32 frames are vector; the 16 frame is drawn
# pixel by pixel from hand-made masks and glyph maps, so it stays crisp. Deterministic: no randomness, no timestamps.
#
#   python3 arrows.py                                       everything: variant-A0..A8, proofs, sheet, strip
#   python3 arrows.py --glyph curved --badge disc --edge tinted --colour neutral --depth lift --size fill --out DIR
#                                                           one overlay family for any tag combination (unset axes take A1's tags)
#   python3 arrows.py --variant A4 --badge disc --out DIR   start from a named variant
#   python3 arrows.py --list                                the axes, their tags and the variants
#   python3 arrows.py --no-outline                          keep sheet text as text (faster)
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "..", "d-best-practice-3d")
M1 = os.path.join(D, "folder-variants-g", "mix-M1")

# ---- palette: Afterglow tokens only (afterglow-themes scripts/palette.mjs and hues.mjs, the Dusk desktop tables, set D's nine) ----------
TOK = {
	"paper": "#fbfaf6", "indigo-100": "#f1eee6", "indigo-200": "#e4e2ec", "indigo-400": "#8f8da6", "indigo-500": "#5f5d78",
	"void": "#050507", "desktop": "#090e2a", "tile": "#0a1230", "sky-1": "#1f2554", "dusk": "#42396c", "horizon": "#4a4580", "sky-7": "#7a4562",
	"gold": "#ffaa40", "gold-light": "#ffd08e", "pale": "#ffe7c4", "orange-300": "#d28c36", "orange-400": "#a56f2b", "orange-500": "#7d5422",
	"red-100": "#f995a6", "red-400": "#9e2a3f", "red-500": "#782131", "text2": "#b4bfce", "body": "#eef1f8", "purple-deep": "#5e44cc",
	"green": "#2ec66a", "blue-deep": "#2563eb", "yellow": "#fbbf24", "yellow-100": "#fddc87", "yellow-400": "#a27c1a", "void-600": "#333847",
}
T = TOK
WHITE, BLACK = "#ffffff", "#000000"  # stock stand-in only


def _rgb(c):
	return [int(c[i:i + 2], 16) for i in (1, 3, 5)]


def hexc(rgb):
	return "#%02x%02x%02x" % tuple(max(0, min(255, round(v))) for v in rgb)


def mix(a, b, t):
	return hexc([x + (y - x) * t for x, y in zip(_rgb(a), _rgb(b))])


def lum(c):
	def ch(v):
		v /= 255
		return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
	r, g, b = [ch(v) for v in _rgb(c)]
	return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
	la, lb = sorted((lum(a), lum(b)), reverse=True)
	return (la + 0.05) / (lb + 0.05)


def _n(v):
	s = ("%.3f" % v).rstrip("0").rstrip(".")
	return "0" if s in ("-0", "") else s


# ---- the axes ----------------------------------------------------------------------------------------------------------------------------
AXES = {
	"glyph": {
		"straight": "classic straight diagonal arrow, shaft and a filled, softened head pointing up-right",
		"curved": "curved 'return' arrow: rises from the bottom-left, bends right, filled head pointing right",
		"chevron": "a single heavy chevron pointing right, no shaft",
		"link": "two interlocked chain links on the diagonal",
		"tail": "a short arrow leaving a small origin dot (the tail): 'from here to there'",
	},
	"badge": {
		"none": "no plate; the glyph floats on its own halo, edge or shadow",
		"disc": "a round plate",
		"rsquare": "a rounded square plate, radius about a fifth of its side",
		"squircle": "a soft squircle (superellipse) plate, between the square and the disc",
	},
	"edge": {
		"tinted": "1 px inner edge in a darker tone of the plate's own hue (or under a floating glyph)",
		"halo": "1 px light-or-dark outline outside the plate (or glyph) in the opposite tone, for contrast on any ground",
		"shadow": "no edge; a soft drop shadow only",
	},
	"colour": {
		"neutral": "light: paper plate, dusk-navy glyph (sky 1)",
		"cream-dusk": "dark: dusk plate (#42396c), paper glyph",
		"gold-navy": "dark: tile-navy plate, gold glyph (orange 200)",
		"rose": "dark: sky-1 plate, rose glyph (red 100)",
	},
	"depth": {
		"flat": "flat fill",
		"gradient": "a gentle top-to-bottom ramp on the plate, lit at the top",
		"lift": "a slim, soft contact shadow under the plate",
	},
	"size": {
		"fill": "the glyph fills the plate, inset about a fifth",
		"pad": "a smaller glyph with more plate around it (at 16 px the plate is too small for this to differ)",
	},
}
ORDER = ["glyph", "badge", "edge", "colour", "depth", "size"]

VARIANTS = {
	"A1": dict(glyph="straight", badge="disc", edge="tinted", colour="neutral", depth="lift", size="fill"),
	"A2": dict(glyph="curved", badge="rsquare", edge="halo", colour="cream-dusk", depth="gradient", size="pad"),
	"A3": dict(glyph="chevron", badge="none", edge="halo", colour="gold-navy", depth="flat", size="fill"),
	"A4": dict(glyph="straight", badge="squircle", edge="halo", colour="gold-navy", depth="lift", size="pad"),
	"A5": dict(glyph="link", badge="squircle", edge="tinted", colour="neutral", depth="flat", size="pad"),
	"A6": dict(glyph="tail", badge="disc", edge="halo", colour="rose", depth="gradient", size="fill"),
	"A7": dict(glyph="straight", badge="none", edge="shadow", colour="cream-dusk", depth="flat", size="fill"),
	"A8": dict(glyph="curved", badge="squircle", edge="tinted", colour="neutral", depth="gradient", size="fill"),
}
NAMES = {
	"A0": "Stock (stand-in)",
	"A1": "Paper coin",
	"A2": "Dusk tile, return",
	"A3": "Floating chevron",
	"A4": "Gold on navy chip",
	"A5": "Link chip",
	"A6": "Rose tail",
	"A7": "Floating paper arrow",
	"A8": "Paper chip, return",
}
BLURB = {
	"A0": "my stand-in of the classic Windows-style overlay: white box, black frame, black curved arrow; 48 is the 32 stretched",
	"A1": "paper disc, dusk-navy straight arrow, indigo tinted edge, slim lift; the calmest legible-everywhere option",
	"A2": "dusk rounded square with a paper return arrow, a paper halo and a gentle ramp: a tiny app tile",
	"A3": "no plate: a gold chevron on a navy halo; hides the least of the icon",
	"A4": "navy squircle, small gold arrow, paper halo, lift: the set's gold accent as the marker",
	"A5": "paper squircle with a chain link: says 'linked' rather than 'go'",
	"A6": "sky-1 disc, rose arrow leaving a dot, paper halo, gentle ramp",
	"A7": "no plate: a paper arrow on a soft shadow; the lightest touch",
	"A8": "paper squircle, dusk-navy return arrow, tinted edge, gentle ramp: the stock idea redrawn in Afterglow",
}

# colour roles: plate, plate ramp (top, bottom), glyph, tinted edge (colour, opacity), halo for a plate, edge under a floating glyph
SCHEMES = {
	"neutral": dict(plate=T["paper"], ramp=(T["paper"], T["indigo-200"]), glyph=T["sky-1"], edge=(T["indigo-500"], 0.75),
		halo=(T["tile"], 0.6), gedge=(T["indigo-400"], 0.0)),
	"cream-dusk": dict(plate=T["dusk"], ramp=(T["horizon"], T["sky-1"]), glyph=T["paper"], edge=(T["tile"], 0.7),
		halo=(T["paper"], 0.9), gedge=(T["indigo-500"], 0.85)),
	"gold-navy": dict(plate=T["tile"], ramp=(T["sky-1"], T["tile"]), glyph=T["gold"], edge=(T["horizon"], 0.9),
		halo=(T["paper"], 0.9), gedge=(T["orange-500"], 0.85)),
	"rose": dict(plate=T["sky-1"], ramp=(T["horizon"], T["tile"]), glyph=T["red-100"], edge=(T["tile"], 0.7),
		halo=(T["paper"], 0.9), gedge=(T["red-500"], 0.85)),
}
SHADOW = T["tile"]

BOX = {48: 16, 32: 11, 16: 8}  # ReactOS: the overlay's art box at each frame size, bottom-left


def tags(cfg):
	return " · ".join(cfg[a] for a in ORDER)


def halo_colour(cfg):
	"""A floating glyph's halo takes the plate colour; a plate's halo takes the opposite tone."""
	s = SCHEMES[cfg["colour"]]
	if cfg["badge"] == "none":
		return (s["plate"], 0.9)
	return s["halo"]


# ---- vector frames (48, 32, and an unhinted 16 for reference) --------------------------------------------------------------------------
def superellipse(x, y, w, p=4.0, steps=48):
	import math
	cx, cy, r = x + w / 2, y + w / 2, w / 2
	pts = []
	for i in range(steps):
		t = 2 * math.pi * i / steps
		c, s = math.cos(t), math.sin(t)
		pts.append((cx + r * (abs(c) ** (2 / p)) * (1 if c >= 0 else -1), cy + r * (abs(s) ** (2 / p)) * (1 if s >= 0 else -1)))
	return "M" + " L".join("%s %s" % (_n(a), _n(b)) for a, b in pts) + " Z"


def plate_path(shape, x, y, w):
	if shape == "disc":
		r = w / 2
		return "M%s %s a%s %s 0 1 0 %s 0 a%s %s 0 1 0 %s 0 Z" % (_n(x), _n(y + r), _n(r), _n(r), _n(w), _n(r), _n(r), _n(-w))
	if shape == "squircle":
		return superellipse(x, y, w, 4.0)
	r = w * 0.2
	return "M%s %s H%s A%s %s 0 0 1 %s %s V%s A%s %s 0 0 1 %s %s H%s A%s %s 0 0 1 %s %s V%s A%s %s 0 0 1 %s %s Z" % (
		_n(x + r), _n(y), _n(x + w - r), _n(r), _n(r), _n(x + w), _n(y + r), _n(y + w - r), _n(r), _n(r), _n(x + w - r), _n(y + w),
		_n(x + r), _n(r), _n(r), _n(x), _n(y + w - r), _n(y + r), _n(r), _n(r), _n(x + r), _n(y))


def glyph_parts(glyph, cx, cy, cw):
	"""(kind, d) in box coordinates: 'line' is stroked with the glyph width, 'fill' is a filled, round-joined shape."""
	P = lambda u, v: "%s %s" % (_n(cx + u * cw), _n(cy + v * cw))  # noqa: E731
	if glyph == "straight":
		return [("line", "M%s L%s" % (P(0.04, 0.96), P(0.72, 0.28))), ("fill", "M%s L%s L%s Z" % (P(0.36, 0.02), P(0.98, 0.02), P(0.98, 0.64)))]
	if glyph == "curved":
		return [("line", "M%s V%s C%s %s %s" % (P(0.1, 0.98), "%s" % _n(cy + 0.72 * cw), P(0.1, 0.46), P(0.26, 0.4), P(0.56, 0.4))),
			("fill", "M%s L%s L%s Z" % (P(0.54, 0.06), P(0.98, 0.4), P(0.54, 0.74)))]
	if glyph == "chevron":
		return [("chev", "M%s L%s L%s" % (P(0.3, 0.08), P(0.72, 0.5), P(0.3, 0.92)))]
	if glyph == "tail":
		return [("dot", P(0.12, 0.88)), ("line", "M%s L%s" % (P(0.44, 0.56), P(0.74, 0.26))),
			("fill", "M%s L%s L%s Z" % (P(0.42, 0.02), P(0.98, 0.02), P(0.98, 0.58)))]
	if glyph == "link":
		return [("linkA", (cx, cy, cw)), ("linkB", (cx, cy, cw))]
	raise ValueError(glyph)


def glyph_svg(glyph, cx, cy, cw, w, colour, opacity=1.0, extra=0.0, filt=""):
	"""Draw the glyph; extra widens every stroke (used for halos and edges under the glyph)."""
	op = '' if opacity >= 1 else ' opacity="%s"' % _n(opacity)
	out = []
	for kind, d in glyph_parts(glyph, cx, cy, cw):
		if kind == "line":
			out.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round"/>' % (d, colour, _n(w + extra)))
		elif kind == "chev":
			out.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round"/>' % (d, colour, _n(w * 1.25 + extra)))
		elif kind == "fill":
			out.append('<path d="%s" fill="%s" stroke="%s" stroke-width="%s" stroke-linejoin="round"/>' % (d, colour, colour, _n(min(w * 0.55, 0.6 + cw / 20) + extra)))
		elif kind == "dot":
			x, y = d.split()
			out.append('<circle cx="%s" cy="%s" r="%s" fill="%s"/>' % (x, y, _n(w * 0.75 + extra / 2), colour))
		elif kind in ("linkA", "linkB"):
			x, y, c = d
			mx, my = x + c / 2, y + c / 2
			L, H = c * 0.72, c * 0.4
			off = -c * 0.22 if kind == "linkA" else c * 0.22
			out.append('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="none" stroke="%s" stroke-width="%s" transform="rotate(-45 %s %s)"/>' % (
				_n(mx + off - L / 2), _n(my - H / 2), _n(L), _n(H), _n(H / 2), colour, _n(w * 0.8 + extra), _n(mx), _n(my)))
	return '<g%s%s>%s</g>' % (op, filt, "".join(out))


def vector(cfg, S, uid):
	"""One overlay frame of size S as SVG (defs, body)."""
	n = BOX[S]
	k = n / 16
	s = SCHEMES[cfg["colour"]]
	defs, body = [], []
	halo = cfg["edge"] == "halo"
	bw = n - 1
	bx, by = 0, S - n + (1 if halo else 0)
	if cfg["badge"] == "none":
		inset = 0.16 if cfg["size"] == "fill" else 0.26
		w = {48: 2.2, 32: 1.6, 16: 1.3}[S] * (1 if cfg["size"] == "fill" else 0.9)
	else:
		inset = {"fill": 0.19, "pad": 0.27 if S == 48 else 0.23}[cfg["size"]] + (0.03 if cfg["badge"] == "disc" else 0)
		inset -= 0.05 if cfg["glyph"] == "link" else 0
		w = {48: 2.0, 32: 1.5, 16: 1.15}[S] * (1 if cfg["size"] == "fill" else 0.9)
	cx, cy, cw = bx + bw * inset, by + bw * inset, bw * (1 - 2 * inset)
	blur = '<filter id="%s-b" x="-50%%" y="-50%%" width="200%%" height="200%%"><feGaussianBlur stdDeviation="%s"/></filter>' % (uid, _n(0.7 * k + 0.15))
	if cfg["badge"] == "none":
		g = cfg["glyph"]
		if cfg["edge"] == "shadow" or cfg["depth"] == "lift":
			defs.append(blur)
			body.append('<g transform="translate(%s %s)">%s</g>' % (_n(0.5 * k + 0.2), _n(0.8 * k + 0.3),
				glyph_svg(g, cx, cy, cw, w, SHADOW, 0.8, 1.0 * k, ' filter="url(#%s-b)"' % uid)))
		if halo:
			hc, ho = halo_colour(cfg)
			body.append(glyph_svg(g, cx, cy, cw, w, hc, ho, 2 * max(1.0, 1.2 * k)))
		if cfg["edge"] == "tinted":
			ec, eo = s["gedge"]
			body.append(glyph_svg(g, cx, cy, cw, w, ec, eo or 0.7, 1.2))
		fill = s["glyph"]
		if cfg["depth"] == "gradient":
			defs.append('<linearGradient id="%s-g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (
				uid, mix(fill, T["paper"], 0.3), mix(fill, T["tile"], 0.12)))
		body.append(glyph_svg(g, cx, cy, cw, w, fill))
		return "".join(defs), "".join(body)
	pd = plate_path(cfg["badge"], bx, by, bw)
	if cfg["depth"] == "lift" or cfg["edge"] == "shadow":
		defs.append(blur)
		body.append('<path d="%s" fill="%s" opacity="%s" transform="translate(%s %s)" filter="url(#%s-b)"/>' % (
			pd, SHADOW, "0.45" if cfg["edge"] == "shadow" else "0.38", _n(0.55 * k + 0.15), _n(0.9 * k + 0.2), uid))
	if halo:
		hc, ho = s["halo"]
		body.append('<path d="%s" fill="none" stroke="%s" stroke-opacity="%s" stroke-width="2"/>' % (pd, hc, _n(ho)))
	if cfg["depth"] == "gradient":
		t, b = s["ramp"]
		defs.append('<linearGradient id="%s-g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (uid, t, b))
		body.append('<path d="%s" fill="url(#%s-g)"/>' % (pd, uid))
	else:
		body.append('<path d="%s" fill="%s"/>' % (pd, s["plate"]))
	if cfg["edge"] == "tinted":
		ec, eo = s["edge"]
		body.append('<path d="%s" fill="none" stroke="%s" stroke-opacity="%s" stroke-width="1"/>' % (plate_path(cfg["badge"], bx + 0.5, by + 0.5, bw - 1), ec, _n(eo)))
	if cfg["depth"] == "gradient":  # the lit top edge of the M1 language: a lighter inner line on the upper half only
		defs.append('<clipPath id="%s-t"><rect x="%s" y="%s" width="%s" height="%s"/></clipPath>' % (uid, _n(bx), _n(by), _n(bw), _n(bw * 0.4)))
		body.append('<path d="%s" fill="none" stroke="%s" stroke-opacity="0.45" stroke-width="1" clip-path="url(#%s-t)"/>' % (
			plate_path(cfg["badge"], bx + (1.5 if cfg["edge"] == "tinted" else 0.5), by + (1.5 if cfg["edge"] == "tinted" else 0.5),
				bw - (3 if cfg["edge"] == "tinted" else 1)), T["paper"] if cfg["colour"] != "neutral" else WHITE, uid))
	body.append(glyph_svg(cfg["glyph"], cx, cy, cw, w, s["glyph"]))
	return "".join(defs), "".join(body)


# ---- the hinted 16 px frame: masks and glyph maps placed pixel by pixel ----------------------------------------------------------------
# '#' full, 'o' 75 %, '+' 50 %, '-' 25 %, '.' empty
COV = {"#": 1.0, "o": 0.75, "+": 0.5, "-": 0.25, ".": 0.0}
PLATE7 = {
	"disc": [".+###+.", "+#####+", "#######", "#######", "#######", "+#####+", ".+###+."],
	"squircle": ["-o###o-", "o#####o", "#######", "#######", "#######", "o#####o", "-o###o-"],
	"rsquare": ["+#####+", "#######", "#######", "#######", "#######", "#######", "+#####+"],
}
# without a halo the plate takes the whole 8 x 8 box, so the glyph gets a 6 x 6 interior (a slim lift does not fit at 16)
PLATE8 = {
	"disc": [".+####+.", "+######+", "########", "########", "########", "########", "+######+", ".+####+."],
	"squircle": ["-o####o-", "o######o", "########", "########", "########", "########", "o######o", "-o####o-"],
	"rsquare": ["+######+", "########", "########", "########", "########", "########", "########", "+######+"],
}
GLYPH5 = {
	"straight": ["..###", "...##", "..#.#", ".#...", "#...."],
	"curved": ["...#.", ".####", "#..#.", "#....", "#...."],
	"chevron": [".#...", "..#+.", "...##", "..#+.", ".#..."],
	"link": ["...##", "..#.#", ".#.#.", "#.#..", "##..."],
	"tail": ["..###", "...##", "..#.#", ".....", "#...."],
}
GLYPH6 = {
	"straight": ["...###", "....##", "...#.#", "..#...", ".#....", "#....."],
	"curved": ["....#.", "..####", ".#..#.", "#.....", "#.....", "#....."],
	"chevron": ["##....", ".##...", "..##..", "..##..", ".##...", "##...."],
	"link": ["...+##", "..+#.#", ".+#.#+", "+#.#+.", "#.#+..", "##+..."],
	"tail": ["...###", "....##", "...#.#", "..#...", "......", "#....."],
}


class Canvas:
	"""16 x 16 RGBA in floats, painted with source-over."""

	def __init__(self, n=16):
		self.n = n
		self.px = [[(0.0, 0.0, 0.0, 0.0) for _ in range(n)] for _ in range(n)]

	def put(self, x, y, colour, a):
		if a <= 0 or not (0 <= x < self.n and 0 <= y < self.n):
			return
		r, g, b = _rgb(colour)
		R, G, B, A = self.px[y][x]
		oa = a + A * (1 - a)
		if oa <= 0:
			return
		mixc = lambda s, d: (s * a + d * A * (1 - a)) / oa  # noqa: E731
		self.px[y][x] = (mixc(r, R), mixc(g, G), mixc(b, B), oa)

	def svg_rects(self):
		out = []
		for y in range(self.n):
			x = 0
			while x < self.n:
				p = self.px[y][x]
				if p[3] < 0.004:
					x += 1
					continue
				c, a = hexc(p[:3]), round(p[3], 3)
				x2 = x + 1
				while x2 < self.n and self.px[y][x2][3] >= 0.004 and hexc(self.px[y][x2][:3]) == c and round(self.px[y][x2][3], 3) == a:
					x2 += 1
				op = "" if a >= 0.999 else ' fill-opacity="%s"' % _n(a)
				out.append('<rect x="%d" y="%d" width="%d" height="1" fill="%s"%s/>' % (x, y, x2 - x, c, op))
				x = x2
		return "".join(out)

	def image(self):
		im = Image.new("RGBA", (self.n, self.n))
		im.putdata([(round(p[0]), round(p[1]), round(p[2]), round(p[3] * 255)) for row in self.px for p in row])
		return im


def _mask(rows, ox, oy):
	return {(ox + x, oy + y): COV[ch] for y, r in enumerate(rows) for x, ch in enumerate(r) if COV[ch] > 0}


def _ring(m, box):
	"""Pixels outside mask m but inside box that touch a solid mask pixel: 4-neighbours at 1, diagonals at 0.5."""
	x0, y0, x1, y1 = box
	ring = {}
	for (x, y), c in m.items():
		if c < 0.75:
			continue
		for dx, dy, wgt in ((1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1), (1, 1, .5), (1, -1, .5), (-1, 1, .5), (-1, -1, .5)):
			p = (x + dx, y + dy)
			if x0 <= p[0] <= x1 and y0 <= p[1] <= y1 and m.get(p, 0) < 0.75:
				ring[p] = max(ring.get(p, 0), wgt * (1 - m.get(p, 0)))
	return ring


def hint16(cfg):
	cv = Canvas()
	s = SCHEMES[cfg["colour"]]
	box = (0, 8, 7, 15)
	if cfg["badge"] == "none":
		rows = GLYPH6[cfg["glyph"]] if cfg["size"] == "fill" else GLYPH5[cfg["glyph"]]
		gm = _mask(rows, 0, 16 - len(rows))
		if cfg["edge"] == "shadow" or cfg["depth"] == "lift":
			for (x, y), c in gm.items():
				cv.put(x + 1, y + 1 if y < 15 else y, SHADOW, 0.5 * c)
		if cfg["edge"] == "halo":
			hc, ho = halo_colour(cfg)
			for p, c in _ring(gm, box).items():
				cv.put(p[0], p[1], hc, ho * c)
			for p, c in gm.items():
				cv.put(p[0], p[1], hc, ho)
		if cfg["edge"] == "tinted":
			ec, eo = s["gedge"]
			for p, c in _ring(gm, box).items():
				cv.put(p[0], p[1], ec, (eo or 0.7) * c * 0.8)
		for (x, y), c in gm.items():
			col = s["glyph"]
			if cfg["depth"] == "gradient":
				col = mix(col, T["paper"], 0.25 * (1 - (y - 10) / 5))
			cv.put(x, y, col, c)
		return cv
	halo = cfg["edge"] == "halo"
	big = cfg["edge"] == "tinted"
	oy = 9 if halo else 8
	pw = 8 if big else 7
	pm = _mask((PLATE8 if big else PLATE7)[cfg["badge"]], 0, oy)
	if cfg["edge"] == "shadow":
		for (x, y), c in pm.items():
			if c >= 0.75:
				cv.put(x + 1, y + 1, SHADOW, 0.32)
	if halo:
		hc, ho = s["halo"]
		for p, c in _ring(pm, box).items():
			cv.put(p[0], p[1], hc, ho * c)
		for p, c in pm.items():  # under the soft corners
			if c < 1:
				cv.put(p[0], p[1], hc, ho * 0.8)
	for (x, y), c in pm.items():
		col = s["plate"]
		if cfg["depth"] == "gradient":  # at 16 the ramp only lifts the top row and settles the bottom row
			t, b = s["ramp"]
			col = t if y == oy else (b if y == oy + pw - 1 else mix(t, b, 0.5) if y == oy + pw - 2 else s["plate"])
		cv.put(x, y, col, c)
	if cfg["edge"] == "tinted":
		ec, eo = s["edge"]
		for (x, y), c in pm.items():
			edge = any(pm.get((x + dx, y + dy), 0) < 0.75 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) or x in (0, pw - 1) or y in (oy, oy + pw - 1)
			if edge:
				light = lum(s["plate"]) > 0.5
				cv.put(x, y, ec, eo * (0.8 if light else 0.85) * (1 if c >= 1 else 0.7))
	if cfg["depth"] == "gradient" and cfg["edge"] != "tinted":  # lit top: a lighter row inside the plate's top edge
		for x in range(2, 5):
			cv.put(x, oy + 1, T["paper"] if cfg["colour"] != "neutral" else WHITE, 0.22)
	if big:
		gm = _mask(GLYPH6[cfg["glyph"]], 1, oy + 1) if cfg["size"] == "fill" else _mask(GLYPH5[cfg["glyph"]], 2, oy + 1)
	else:
		gm = _mask(GLYPH5[cfg["glyph"]], 1, oy + 1)
	for (x, y), c in gm.items():
		cv.put(x, y, s["glyph"], c)
	return cv


# ---- the stock stand-in (A0): my own drawing of the classic Windows-style overlay, not a copied bitmap ---------------------------------------
def stock_vector(S):
	"""White box, black 1 px frame, black curved arrow with a big head. At 48 ReactOS stretches the 32 frame, so the 48 here is the 32 scaled."""
	inner = ('<rect x="0.5" y="0.5" width="10" height="10" fill="%s" stroke="%s" stroke-width="1"/>'
		'<path d="M2.6 9 V7.2 C2.6 5.4 3.8 4.6 5.6 4.6" fill="none" stroke="%s" stroke-width="1.6" stroke-linecap="round"/>'
		'<path d="M5.2 2 L8.6 4.6 L5.2 7.2 Z" fill="%s" stroke="%s" stroke-width="0.6" stroke-linejoin="round"/>') % (WHITE, BLACK, BLACK, BLACK, BLACK)
	if S == 32:
		return "", '<g transform="translate(0 21)">%s</g>' % inner
	if S == 48:
		return "", '<g transform="translate(0 32) scale(%s)">%s</g>' % (_n(16 / 11), inner)
	return "", '<g transform="translate(0 8) scale(%s)">%s</g>' % (_n(8 / 11), inner)


def stock16():
	cv = Canvas()
	rows = ["########", "#......#", "#...#..#", "#.####.#", "#.#.#..#", "#.#....#", "#.#....#", "########"]
	for y, r in enumerate(rows):
		for x, ch in enumerate(r):
			cv.put(x, 8 + y, BLACK if ch == "#" else WHITE, 1)
	return cv


# ---- writing one family ---------------------------------------------------------------------------------------------------------------------
def head(title):
	return "<!--\nAfterglow shortcut-arrow overlay: %s\n\n(c) Copyright 2026 Liminal HQ, Scott Morris\nSPDX-License-Identifier: Apache-2.0 OR MIT\n-->\n" % title


def svg_doc(title, S, defs, body, extra=""):
	return head(title) + '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d"%s>\n<defs>%s</defs>\n%s\n</svg>\n' % (S, S, S, S, extra, defs, body)


def frames(label, cfg):
	"""{name: (svg text, size)} for one family; cfg None means the stock stand-in."""
	out = {}
	desc = "stock stand-in" if cfg is None else "%s (%s)" % (label, tags(cfg))
	for S in (48, 32, 16):
		d, b = stock_vector(S) if cfg is None else vector(cfg, S, "%s-%d" % (label, S))
		out["arrow-%d.svg" % S] = (svg_doc("%s, %d px frame%s" % (desc, S, ", unhinted vector reference" if S == 16 else ""), S, d, b), S)
	cv = stock16() if cfg is None else hint16(cfg)
	out["arrow-16-hinted.svg"] = (svg_doc("%s, hinted 16 px frame (pixel drawing)" % desc, 16, "", cv.svg_rects(), ' shape-rendering="crispEdges"'), 16)
	return out, cv


def render(svg, png, zoom=1.0, w=None):
	args = ["rsvg-convert"] + (["-w", str(w), "-h", str(w)] if w else ["-z", str(zoom)]) + [svg, "-o", png]
	subprocess.run(args, check=True)


def write_family(cfg, out, label):
	os.makedirs(out, exist_ok=True)
	fr, cv = frames(label, cfg)
	for name, (text, S) in fr.items():
		p = os.path.join(out, name)
		open(p, "w").write(text)
		if name != "arrow-16.svg":  # the ICO frames: 48, 32 and the hinted 16
			render(p, os.path.join(out, name.replace(".svg", ".png").replace("-hinted", "")), w=S)
	return fr, cv


# ---- icon library for composites: symbols with prefixed ids ---------------------------------------------------------------------------------
ICONS = [  # key, label, 48 master, 32 source (48 viewBox rendered at 32), hinted or 16 profile
	("folder", "M1 folder", os.path.join(M1, "folder.svg"), os.path.join(M1, "folder-32.svg"), os.path.join(M1, "folder-16.svg")),
	("doc", "Document", os.path.join(D, "icons/doc.svg"), os.path.join(D, "icons/doc.svg"), os.path.join(D, "icons/doc-16.svg")),
	("computer", "My Computer", os.path.join(D, "icons/mycomputer.svg"), os.path.join(D, "icons/mycomputer.svg"), os.path.join(D, "icons/mycomputer-16.svg")),
	("hdd", "Hard disk", os.path.join(D, "icons/hdd.svg"), os.path.join(D, "icons/hdd.svg"), os.path.join(D, "icons/hdd-16.svg")),
	("app", "App tile", os.path.join(D, "icons/cmd.svg"), os.path.join(D, "icons/cmd.svg"), os.path.join(D, "icons/16/cmd.svg")),
	("bin", "Recycle Bin", os.path.join(D, "icons/recycle.svg"), os.path.join(D, "icons/recycle.svg"), os.path.join(D, "icons/16/recycle.svg")),
]


def strip_svg(text, prefix):
	"""Inner markup and viewBox of an SVG file, ids prefixed so many can live in one document."""
	text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
	text = re.sub(r"<\?xml.*?\?>", "", text)
	m = re.search(r"<svg([^>]*)>(.*)</svg>", text, flags=re.S)
	attrs, inner = m.group(1), m.group(2)
	vb = re.search(r'viewBox="([^"]+)"', attrs).group(1)
	keep = " ".join(re.findall(r'(?:stroke-linejoin|stroke-linecap|shape-rendering)="[^"]+"', attrs))
	inner = re.sub(r'id="([^"]+)"', lambda mm: 'id="%s-%s"' % (prefix, mm.group(1)), inner)
	inner = re.sub(r"url\(#([^)]+)\)", lambda mm: "url(#%s-%s)" % (prefix, mm.group(1)), inner)
	inner = re.sub(r'href="#([^"]+)"', lambda mm: 'href="#%s-%s"' % (prefix, mm.group(1)), inner)
	defs = "".join(re.findall(r"<defs>(.*?)</defs>", inner, flags=re.S))
	inner = re.sub(r"<defs>.*?</defs>", "", inner, flags=re.S)
	return vb, inner, defs, keep


class Lib:
	def __init__(self):
		self.defs, self.syms, self.have = [], [], set()

	def add(self, sid, text):
		if sid in self.have:
			return sid
		self.have.add(sid)
		vb, inner, defs, keep = strip_svg(text, sid)
		self.defs.append(defs)
		self.syms.append('<symbol id="%s" viewBox="%s" overflow="visible"><g %s>%s</g></symbol>' % (sid, vb, keep, inner))
		return sid

	def file(self, sid, path):
		return self.add(sid, open(path).read())

	def block(self):
		return "".join(self.defs) + "".join(self.syms)


def use(sid, x, y, size):
	return '<use href="#%s" x="%s" y="%s" width="%s" height="%s"/>' % (sid, _n(x), _n(y), size, size)


# ---- stock ReactOS stand-in icons (my own simple drawings, labelled as stand-ins) -------------------------------------------------------------
INK = "#1f2230"  # void 700


def stock_icon(k):
	o = 'stroke="%s" stroke-width="1.5" stroke-linejoin="round"' % INK
	if k == "folder":
		b = ('<path d="M4 12 H18 L21 15 H43 V40 H4 Z" fill="%s" %s/><path d="M4 19 H43 V40 H4 Z" fill="%s" %s/>' % (T["yellow"], o, T["yellow-100"], o))
	elif k == "doc":
		b = ('<path d="M10 4 H30 L39 13 V44 H10 Z" fill="%s" %s/><path d="M30 4 V13 H39" fill="%s" %s/>' % (WHITE, o, T["indigo-200"], o)
			+ "".join('<path d="M15 %d H34" stroke="%s" stroke-width="1.5"/>' % (y, T["indigo-400"]) for y in (20, 25, 30, 35)))
	elif k == "computer":
		b = ('<rect x="6" y="5" width="36" height="28" fill="%s" %s/><rect x="10" y="9" width="28" height="20" fill="%s"/>'
			'<path d="M16 33 H32 L34 40 H14 Z" fill="%s" %s/><rect x="8" y="40" width="32" height="5" fill="%s" %s/>') % (
			T["indigo-100"], o, T["blue-deep"], T["text2"], o, T["indigo-100"], o)
	elif k == "hdd":
		b = ('<rect x="5" y="16" width="38" height="18" rx="1" fill="%s" %s/><path d="M5 28 H43" stroke="%s"/><rect x="34" y="30" width="5" height="2" fill="%s"/>') % (
			T["text2"], o, T["indigo-400"], T["green"])
	elif k == "app":
		b = ('<rect x="5" y="7" width="38" height="34" fill="%s" %s/><rect x="5.75" y="7.75" width="36.5" height="6" fill="%s"/>'
			'<rect x="10" y="18" width="10" height="8" fill="%s"/>') % (T["body"], o, T["blue-deep"], T["text2"])
	else:
		b = ('<path d="M10 12 H38 L35 44 H13 Z" fill="%s" %s/><rect x="8" y="8" width="32" height="5" fill="%s" %s/>'
			'<path d="M19 18 V39 M24 18 V39 M29 18 V39" stroke="%s" stroke-width="1.5"/>') % (T["text2"], o, T["body"], o, T["indigo-500"])
	return svg_doc("stock ReactOS stand-in, %s (my own drawing, not a ReactOS bitmap)" % k, 48, "", b)


# ---- raster helpers for pixel-true 16 px composites ------------------------------------------------------------------------------------------
class Raster:
	def __init__(self, tmp):
		self.tmp, self.cache = tmp, {}

	def icon16(self, path):
		if path not in self.cache:
			png = os.path.join(self.tmp, "i%d.png" % len(self.cache))
			render(path, png, w=16)
			self.cache[path] = Image.open(png).convert("RGBA")
		return self.cache[path]


def comp16(icon, arrow_img, ground, blend=None):
	"""Source-over: ground, icon, overlay. blend=(colour, t) mimics ILD_BLEND50 selection on the icon only."""
	g = Image.new("RGBA", (16, 16), tuple(_rgb(ground)) + (255,))
	ic = icon.copy()
	ic.alpha_composite(arrow_img)
	if blend:
		col, t = blend
		over = Image.new("RGBA", (16, 16), tuple(_rgb(col)) + (255,))
		mixd = Image.blend(ic, over, t)
		mixd.putalpha(ic.getchannel("A"))
		ic = mixd
	g.alpha_composite(ic)
	return g


def pixels_svg(im, x, y, z):
	"""A raster as zoomed rects (merged runs), for the 8x views in the sheet."""
	out = []
	w, h = im.size
	data = im.load()
	for yy in range(h):
		xx = 0
		while xx < w:
			c = data[xx, yy][:3]
			x2 = xx + 1
			while x2 < w and data[x2, yy][:3] == c:
				x2 += 1
			out.append('<rect x="%s" y="%s" width="%s" height="%s" fill="%s"/>' % (_n(x + xx * z), _n(y + yy * z), _n((x2 - xx) * z), _n(z), hexc(c)))
			xx = x2
	return '<g shape-rendering="crispEdges">%s</g>' % "".join(out)


# ---- the sheet -------------------------------------------------------------------------------------------------------------------------------
BG, CELL, LAB, HD, SUB, DIM = "#0c0c10", "#14161d", "#e0e0e0", "#ffd08e", "#b4bfce", "#7c8796"
FONT = "'DejaVu Sans', sans-serif"
GROUNDS = [("void desktop", T["desktop"]), ("dusk sky", "url(#skybg)"), ("paper", T["paper"])]
SKY = '<linearGradient id="skybg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1f2554"/><stop offset="0.55" stop-color="#42396c"/><stop offset="1" stop-color="#7a4562"/></linearGradient>'
CHECK = ('<pattern id="check" width="8" height="8" patternUnits="userSpaceOnUse"><rect width="8" height="8" fill="#6b6877"/>'
	'<rect width="4" height="4" fill="#8f8c98"/><rect x="4" y="4" width="4" height="4" fill="#8f8c98"/></pattern>')


def txt(x, y, s, size=12, fill=LAB, anchor="start", weight=400):
	if not s:
		return ""
	s = s.replace("&", "&amp;").replace("<", "&lt;")
	return '<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" fill="%s" text-anchor="%s">%s</text>' % (_n(x), _n(y), FONT, size, weight, fill, anchor, s)


def rect(x, y, w, h, fill, r=0, extra=""):
	return '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s"%s/>' % (_n(x), _n(y), _n(w), _n(h), _n(r), fill, extra)


class Build:
	def __init__(self, tmp):
		self.lib = Lib()
		self.ras = Raster(tmp)
		self.fams = {}  # label -> (frames, canvas, cfg)
		for k, _, p48, p32, p16 in ICONS:
			self.lib.file("ic-%s-48" % k, p48)
			self.lib.file("ic-%s-32" % k, p32)
			self.lib.file("ic-%s-16" % k, p16)
			self.lib.add("st-%s" % k, stock_icon(k))

	def family(self, label, cfg):
		if label not in self.fams:
			out = os.path.join(HERE, "variant-" + label)
			fr, cv = write_family(cfg, out, label) if cfg else self._stock(out)
			for name, (text, S) in fr.items():
				if name != "arrow-16.svg":
					self.lib.add("ar-%s-%d" % (label, S), text)
			self.fams[label] = (fr, cv, cfg)
		return self.fams[label]

	def _stock(self, out):
		os.makedirs(out, exist_ok=True)
		fr, cv = frames("A0", None)
		for name, (text, S) in fr.items():
			open(os.path.join(out, name), "w").write(text)
			if name != "arrow-16.svg":
				render(os.path.join(out, name), os.path.join(out, name.replace(".svg", ".png").replace("-hinted", "")), w=S)
		return fr, cv

	def icon_with_arrow(self, label, k, S, x, y, stock=False):
		ic = "st-%s" % k if stock else "ic-%s-%d" % (k, S)
		return use(ic, x, y, S) + use("ar-%s-%d" % (label, S), x, y, S)

	def zoom16(self, label, k, ground, x, y, z=8, blend=None, crop=None):
		icon = self.ras.icon16([i for i in ICONS if i[0] == k][0][4])
		im = comp16(icon, self.fams[label][1].image(), ground, blend)
		return pixels_svg(im.crop(crop) if crop else im, x, y, z)

	def panel(self, label, x, y, ground, w, stock=False):
		"""Six icons at 48, 32 and 16 on one ground."""
		o = [rect(x, y, w, 136, ground, 6)]
		step = (w - 24) / 6
		for i, (k, *_r) in enumerate(ICONS):
			cx = x + 12 + step * i + (step - 48) / 2
			o.append(self.icon_with_arrow(label, k, 48, cx, y + 10, stock))
			if stock:
				o.append(use("st-%s" % k, cx + 8, y + 66, 32) + use("ar-%s-32" % label, cx + 8, y + 66, 32))
				o.append(use("st-%s" % k, cx + 16, y + 108, 16) + use("ar-%s-16" % label, cx + 16, y + 108, 16))
			else:
				o.append(self.icon_with_arrow(label, k, 32, cx + 8, y + 66))
				o.append(self.icon_with_arrow(label, k, 16, cx + 16, y + 108))
		return "".join(o)


def write_sheet(b, labels):
	W = 1880
	o = []
	y = 40
	o.append(txt(40, y + 14, "Afterglow · shortcut-arrow overlay · variants A1–A8", 30, "#ffffff", weight=600))
	for line in [
		"ReactOS draws one overlay, shell32 group 30, composited at (0, 0) over the target icon: art in the bottom-left 8 × 8 at 16, 11 × 11 at 32 and 16 × 16 at 48 (stock has no 48 frame and",
		"stretches the 32). Each variant below ships real 48, 32 and hinted 16 frames. Axes: GLYPH · BADGE · EDGE · COLOUR · DEPTH · SIZE; tags mix freely through arrows.py. Colours are Afterglow",
		"tokens only. Icons: the M1 closed folder and set D's document, My Computer, hard disk, app tile (Command Prompt plate) and Recycle Bin. Grounds: the void desktop, the dusk sky and paper.",
	]:
		y += 20
		o.append(txt(40, y + 14, line, 13, SUB))
	y += 46
	# column headings
	PX, PW = 492, 344
	o.append(txt(40, y, "Variant · tags", 12, HD, weight=600))
	o.append(txt(290, y, "Alone · 48, 32 at 4× · 16 at 8×", 11, HD, weight=600))
	for i, (gname, _) in enumerate(GROUNDS):
		o.append(txt(PX + i * (PW + 12) + PW / 2, y, "On the %s · 48, 32, 16" % gname, 12, HD, "middle", 600))
	o.append(txt(1566 + 132, y, "16 px folder, lower-left 12 × 12 at 8×", 12, HD, "middle", 600))
	y += 12
	for label in labels:
		fr, cv, cfg = b.fams[label]
		o.append(rect(30, y, W - 60, 156, CELL, 8))
		o.append(txt(44, y + 30, label, 22, "#ffffff", weight=700))
		o.append(txt(92, y + 29, NAMES[label], 14, HD, weight=600))
		if cfg:
			for j, a in enumerate(ORDER):
				o.append(txt(44, y + 52 + j * 15, "%s" % a.upper(), 10, DIM, weight=600))
				o.append(txt(110, y + 52 + j * 15, cfg[a], 11, LAB))
		else:
			for j, line in enumerate(["white box, black 1 px frame,", "black curved arrow (my drawing,", "not a ReactOS or Microsoft", "bitmap). 48 is the 32 stretched,", "as ReactOS does today."]):
				o.append(txt(44, y + 52 + j * 15, line, 11, SUB))
		# overlay alone, on a half-dark, half-light split behind a checker
		ax = 290
		for S, z, w in ((48, 4, 64), (32, 4, 44), (16, 8, 64)):
			n = BOX[S]
			o.append('<g><rect x="%d" y="%d" width="%d" height="%d" fill="url(#check)"/>' % (ax, y + 14, w, w))
			o.append(rect(ax, y + 14 + w, w, 10, T["desktop"]) + rect(ax + w / 2, y + 14 + w, w / 2, 10, T["paper"]))
			o.append('<svg x="%d" y="%d" width="%d" height="%d" viewBox="0 %d %d %d" overflow="hidden"><use href="#ar-%s-%d" x="0" y="0" width="%d" height="%d"/></svg></g>' % (
				ax, y + 14, w, w, S - n, n, n, label, S, S, S))
			o.append(txt(ax + w / 2, y + 102, "%d" % S, 10, DIM, "middle"))
			ax += w + 6
		for i, (gname, g) in enumerate(GROUNDS):
			o.append(b.panel(label, PX + i * (PW + 12), y + 10, g, PW))
		o.append(b.zoom16(label, "folder", T["desktop"], 1580, y + 14, 8, crop=(0, 4, 12, 16)) + b.zoom16(label, "folder", T["paper"], 1580 + 106, y + 14, 8, crop=(0, 4, 12, 16)))
		o.append(txt(1580 + 48, y + 126, "void", 10, DIM, "middle") + txt(1580 + 154, y + 126, "paper", 10, DIM, "middle"))
		y += 164
	# stock stand-in icons
	y += 24
	o.append(txt(40, y, "On stock ReactOS icons (stand-ins: my own simple drawings of the classic folder, document, computer, disk, window and bin; not ReactOS bitmaps)", 15, HD, weight=600))
	y += 12
	cols = 3
	cw = (W - 60 - (cols - 1) * 12) / cols
	for idx, label in enumerate(labels):
		cx = 30 + (idx % cols) * (cw + 12)
		cy = y + (idx // cols) * 168
		o.append(rect(cx, cy, cw, 160, CELL, 8))
		o.append(txt(cx + 12, cy + 20, "%s · %s" % (label, NAMES[label]), 12, HD, weight=600))
		o.append(b.panel(label, cx + 10, cy + 24, T["desktop"], cw - 20, stock=True))
	y += 3 * 168 + 24
	# desktop at Shell Icon Size 48, and Details view at 16
	o.append(txt(40, y, "In use · the desktop at Shell Icon Size 48, and a Details view at 16 (100 % scale) with one selected row (50 % blend with the highlight, as ILD_BLEND50 draws it)", 15, HD, weight=600))
	y += 12
	labels_d = [("folder", "Projects"), ("doc", "Readme"), ("app", "Console"), ("hdd", "Drive C"), ("computer", "My Computer")]
	for idx, label in enumerate(labels):
		cx = 30 + (idx % cols) * (cw + 12)
		cy = y + (idx // cols) * 236
		o.append(rect(cx, cy, cw, 228, CELL, 8))
		o.append(txt(cx + 12, cy + 20, "%s · %s" % (label, NAMES[label]), 12, HD, weight=600))
		# desktop
		o.append(rect(cx + 10, cy + 28, cw - 20, 92, "url(#skybg)", 4))
		step = (cw - 20) / 5
		for i, (k, name) in enumerate(labels_d):
			ix = cx + 10 + step * i + (step - 48) / 2
			o.append(b.icon_with_arrow(label, k, 48, ix, cy + 36))
			o.append(txt(ix + 25, cy + 101, name, 11, "#0a1230", "middle"))
			o.append(txt(ix + 24, cy + 100, name, 11, "#ffffff", "middle"))
		# details view
		dx, dy = cx + 10, cy + 128
		o.append(rect(dx, dy, cw - 20, 92, T["paper"], 4))
		o.append(rect(dx, dy, cw - 20, 18, T["indigo-100"], 4) + rect(dx, dy + 14, cw - 20, 4, T["indigo-100"]))
		for t, tx in (("Name", 30), ("Type", 230), ("Size", 360)):
			o.append(txt(dx + tx, dy + 13, t, 10, T["indigo-500"]))
		rows = [("folder", "Projects"), ("doc", "Readme.txt"), ("app", "Console"), ("hdd", "Drive C")]
		for r, (k, name) in enumerate(rows):
			ry = dy + 22 + r * 17
			sel = r == 1
			if sel:
				o.append(rect(dx + 26, ry, 150, 16, T["purple-deep"]))
			o.append(b.zoom16(label, k, T["paper"], dx + 8, ry, 1, (T["purple-deep"], 0.5) if sel else None))
			o.append(txt(dx + 30, ry + 12, name + " - Shortcut", 11, "#ffffff" if sel else "#1c1b20"))
			o.append(txt(dx + 230, ry + 12, "Shortcut", 11, "#484554"))
			o.append(txt(dx + 360, ry + 12, "1 KB", 11, "#484554"))
	y += 3 * 236 + 20
	o.append(txt(40, y, "Recommended: A8 (curved · squircle · tinted · neutral · gradient · fill); optional --depth lift at 48 and 32. Runner-up: A8 with --glyph straight (A1's arrow). Reasons and contrast in notes.md.", 13, SUB))
	H = y + 30
	return (head("the variant sheet (A0 stock stand-in, A1–A8)") +
		'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n<defs>%s%s%s</defs>\n%s\n%s\n</svg>\n' % (
			W, H, W, H, SKY, CHECK, b.lib.block(), rect(0, 0, W, H, BG), "\n".join(o)))


def write_strip(b, labels):
	W = 60 + len(labels) * 196
	o = [txt(30, 34, "Shortcut overlays side by side · the M1 folder at 48 on the void desktop and paper · then the 16 px at 8× on both", 15, HD, weight=600)]
	for i, label in enumerate(labels):
		x = 30 + i * 196
		o.append(rect(x, 50, 186, 250, CELL, 8))
		o.append(txt(x + 93, 74, "%s · %s" % (label, NAMES[label]), 12, "#ffffff", "middle", 600))
		o.append(rect(x + 10, 86, 80, 70, T["desktop"], 4) + rect(x + 96, 86, 80, 70, T["paper"], 4))
		o.append(b.icon_with_arrow(label, "folder", 48, x + 26, 96) + b.icon_with_arrow(label, "folder", 48, x + 112, 96))
		o.append(b.zoom16(label, "folder", T["desktop"], x + 7, 166, 7, crop=(0, 4, 12, 16)) + b.zoom16(label, "folder", T["paper"], x + 95, 166, 7, crop=(0, 4, 12, 16)))
		o.append(txt(x + 93, 266, "16 px, lower-left 12 × 12 at 7×", 9, DIM, "middle"))
		cfg = b.fams[label][2]
		o.append(txt(x + 93, 284, ("%s · %s · %s" % (cfg["glyph"], cfg["badge"], cfg["edge"])) if cfg else "stock stand-in", 9, DIM, "middle"))
		o.append(txt(x + 93, 296, ("%s · %s · %s" % (cfg["colour"], cfg["depth"], cfg["size"])) if cfg else "", 9, DIM, "middle"))
	H = 316
	return (head("comparison strip") + '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n<defs>%s%s</defs>\n%s\n%s\n</svg>\n' % (
		W, H, W, H, SKY, b.lib.block(), rect(0, 0, W, H, BG), "\n".join(o)))


def write_proof(b, label):
	"""Per-variant composite proof: six icons on three grounds at 48, 32 and 16, then every 16 px composite at 8x on void and paper."""
	W = 1180
	o = [txt(30, 34, "%s · %s · %s" % (label, NAMES[label], tags(b.fams[label][2]) if b.fams[label][2] else "stock stand-in"), 16, HD, weight=600)]
	for i, (gname, g) in enumerate(GROUNDS):
		o.append(txt(30 + i * 380 + 176, 60, gname, 11, SUB, "middle"))
		o.append(b.panel(label, 30 + i * 380, 68, g, 352))
	y = 226
	o.append(txt(30, y, "16 px composites at 8× (pixel-true, as ReactOS composites them) · void desktop above, paper below", 12, SUB))
	for gi, g in enumerate((T["desktop"], T["paper"])):
		for i, (k, *_r) in enumerate(ICONS):
			o.append(b.zoom16(label, k, g, 30 + i * 190, y + 12 + gi * 140, 8))
	H = y + 12 + 2 * 140 + 10
	return (head("composite proof, %s" % label) + '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d">\n<defs>%s%s</defs>\n%s\n%s\n</svg>\n' % (
		W, H, W, H, SKY, b.lib.block(), rect(0, 0, W, H, BG), "\n".join(o)))


def outline_text(path):
	"""Text to paths through Inkscape, keeping the SPDX comment in front."""
	src = open(path).read()
	hd = src[:src.index("-->") + 4]
	tmp = path + ".tmp.svg"
	subprocess.run(["inkscape", path, "--export-text-to-path", "--export-plain-svg", "--export-filename=" + tmp], check=True, capture_output=True)
	body = open(tmp).read()
	os.remove(tmp)
	if body.startswith("<?xml"):
		body = body[body.index("?>") + 2:].lstrip()
	if not body.startswith("<!--"):
		body = hd + "\n" + body
	open(path, "w").write(body)


# ---- contrast table ----------------------------------------------------------------------------------------------------------------------
GROUND_C = [("gold back", T["gold"]), ("gold flap", T["gold-light"]), ("paper", T["paper"]), ("desktop", T["desktop"]), ("app plate", T["dusk"])]


def over(c, a, g):
	return mix(g, c, a)


def contrast_rows():
	rows = []
	for label, cfg in VARIANTS.items():
		s = SCHEMES[cfg["colour"]]
		if cfg["badge"] == "none":
			hc, ho = halo_colour(cfg)
			outer = (lambda g, hc=hc, ho=ho: over(hc, ho, g)) if cfg["edge"] == "halo" else (lambda g: g)
			body = s["glyph"]
			inner = "glyph on halo %.1f" % contrast(s["glyph"], hc) if cfg["edge"] == "halo" else "glyph only"
		else:
			body = s["plate"]
			if cfg["edge"] == "halo":
				hc, ho = s["halo"]
				outer = lambda g, hc=hc, ho=ho: over(hc, ho, g)  # noqa: E731
			elif cfg["edge"] == "tinted":
				ec, eo = s["edge"]
				outer = lambda g, ec=ec, eo=eo, p=s["plate"]: over(ec, eo, p)  # noqa: E731
			else:
				outer = lambda g, p=s["plate"]: p  # noqa: E731
			inner = "glyph on plate %.1f" % contrast(s["glyph"], s["plate"])
		cells = []
		for gname, g in GROUND_C:
			cells.append("%.1f / %.1f" % (contrast(body, g), contrast(outer(g), g)))
		rows.append((label, inner, cells))
	return rows


def print_contrast():
	print("| Variant | Inside | " + " | ".join(g for g, _ in GROUND_C) + " |")
	print("| --- | --- | " + " | ".join("---" for _ in GROUND_C) + " |")
	for label, inner, cells in contrast_rows():
		print("| %s | %s | %s |" % (label, inner, " | ".join(cells)))


def build_all(outline=True):
	tmp = tempfile.mkdtemp(prefix="arrows-")
	try:
		b = Build(tmp)
		labels = ["A0"] + list(VARIANTS)
		b.family("A0", None)
		for label, cfg in VARIANTS.items():
			b.family(label, cfg)
		pdir = os.path.join(HERE, "proofs")
		os.makedirs(pdir, exist_ok=True)
		jobs = [(os.path.join(HERE, "sheet.svg"), write_sheet(b, labels), 1), (os.path.join(HERE, "strip.svg"), write_strip(b, labels), 1)]
		for label in labels:
			jobs.append((os.path.join(pdir, "proof-%s.svg" % label), write_proof(b, label), 2))
		for path, text, z in jobs:
			open(path, "w").write(text)
			if outline and shutil.which("inkscape"):
				outline_text(path)
			render(path, path[:-4] + ".png", z)
	finally:
		shutil.rmtree(tmp)


def main():
	ap = argparse.ArgumentParser(description="Afterglow shortcut-arrow overlay variants.")
	for a in ORDER:
		ap.add_argument("--" + a, choices=list(AXES[a]))
	ap.add_argument("--variant", choices=list(VARIANTS))
	ap.add_argument("--out", help="write one family here instead of building everything")
	ap.add_argument("--no-outline", action="store_true", help="keep sheet text as text (faster)")
	ap.add_argument("--list", action="store_true")
	ap.add_argument("--contrast", action="store_true", help="print the contrast table")
	args = ap.parse_args()
	if args.list:
		for a in ORDER:
			print(a.upper())
			for t, why in AXES[a].items():
				print("  %-11s %s" % (t, why))
		for k, v in VARIANTS.items():
			print("%s  %s  (%s)" % (k, tags(v), NAMES[k]))
		return
	if args.contrast:
		print_contrast()
		return
	if args.out or args.variant or any(getattr(args, a) for a in ORDER):
		cfg = dict(VARIANTS["A1"])
		cfg.update(VARIANTS.get(args.variant, {}))
		cfg.update({a: getattr(args, a) for a in ORDER if getattr(args, a)})
		out = args.out or os.path.join(os.getcwd(), "arrow-" + "-".join(cfg[a] for a in ORDER))
		write_family(cfg, out, args.variant or "custom")
		print("wrote", out, "·", tags(cfg))
		return
	build_all(not args.no_outline)
	print("variants", len(VARIANTS), "plus the A0 stock stand-in")


if __name__ == "__main__":
	sys.exit(main())
