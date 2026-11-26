#!/usr/bin/env python3
# Afterglow folder variants G for icon set D: a soft, outline-free open and closed folder after the owner's reference, parameterised on seven axes.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# Derived from ../folder-variants/folders.py (axes, tags, variant tables, sheet layout and the D-now reference row, which is imported from there
# rather than copied). The drawing is new: no ink outline, no extrusion; a darker tone of the fill defines the edge.
#
#   python3 folders_g.py                                   everything: variant-G0..G6, mix-M1..M2, sheet, strip, renders
#   python3 folders_g.py --flap lean-10 --closed lean-half --papers two --tab sloped --edge tinted --surface gradient --depth contact --out DIR
#                                                          one family for any tag combination (unset axes take G1's tags)
#   python3 folders_g.py --variant G3 --edge lit --out DIR  start from a named variant
#   python3 folders_g.py --palette yellow ...              the same drawing in the yellow ramp, for comparison only
#   python3 folders_g.py --list                            the axes, their tags and the variants
import argparse
import base64
import importlib.util
import math
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REF_PNG = "/home/scott/.claude/uploads/cdbcf434-916f-477e-98f8-f3394af87f3b/34ac5b2f-image.png"

# ---- palette: Afterglow tokens only (afterglow-themes scripts/palette.mjs and hues.mjs, the Dusk desktop tables, D's nine) -------------------
TOK = {
	"orange-100": "#ffd096", "orange-200": "#ffaa40", "orange-300": "#d28c36", "orange-400": "#a56f2b", "orange-500": "#7d5422", "orange-600": "#583b1a",
	"brand-gold": "#ffd08e", "pale": "#ffe7c4",
	"yellow-100": "#fddc87", "yellow-200": "#fbbf24", "yellow-300": "#cf9e1f", "yellow-400": "#a27c1a", "yellow-500": "#7b5e15", "yellow-600": "#564211",
	"paper-900": "#fbfaf6", "indigo-100": "#f1eee6", "paper-800": "#f2eff4",
	"void": "#050507", "desktop": "#090e2a", "tile": "#0a1230", "horizon": "#4a4580", "text2": "#b4bfce", "body": "#eef1f8",
	"sky-1": "#1f2554", "sky-4": "#42396c", "sky-7": "#7a4562",
}
WHITE = "#ffffff"


def _rgb(c):
	return [int(c[i:i + 2], 16) for i in (1, 3, 5)]


def mix(a, b, t):
	return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(_rgb(a), _rgb(b)))


def lum(c):
	def ch(v):
		v /= 255
		return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
	r, g, b = [ch(v) for v in _rgb(c)]
	return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
	la, lb = sorted((lum(a), lum(b)), reverse=True)
	return (la + 0.05) / (lb + 0.05)


# Roles -> tokens. Gold is the set's palette; yellow is a comparison only.
PALETTES = {
	"gold": dict(back="orange-200", flap="brand-gold", hl_back="orange-100", hl_flap="pale", edge="orange-500", px_edge="orange-400", px_inner="orange-300",
		under="orange-200", emblem="orange-400", px_emblem="orange-500", cast="orange-600"),
	"yellow": dict(back="yellow-200", flap="yellow-100", hl_back="yellow-100", hl_flap="pale", edge="yellow-500", px_edge="yellow-400", px_inner="yellow-300",
		under="yellow-200", emblem="yellow-400", px_emblem="yellow-500", cast="yellow-600"),
}
COMMON = dict(paper_back="indigo-100", paper_front="paper-900", contact="tile")


def colours(pal):
	c = {k: TOK[v] for k, v in {**PALETTES[pal], **COMMON}.items()}
	# derived: the gentle gradient ends, 30 % toward the highlight at the top and 18 % toward the next ramp step at the bottom
	nxt = TOK["orange-300"] if pal == "gold" else TOK["yellow-300"]
	c["grad_back"] = (mix(c["back"], c["hl_back"], 0.3), mix(c["back"], nxt, 0.18))
	c["grad_flap"] = (mix(c["flap"], c["hl_flap"], 0.35), mix(c["flap"], c["back"], 0.18))
	return c


# ---- the axes ----------------------------------------------------------------------------------------------------------------------------
AXES = {
	"flap": {
		"lean-6": "open front leans right 6°: barely tipped, the calmest open state",
		"lean-8": "8°",
		"lean-10": "10°: a clear but quiet open",
		"lean-12": "12°",
		"lean-13": "13°",
		"lean-16": "16°: the most open of the range",
		"lean-18": "18°: the reference picture's own lean (G0 only)",
	},
	"closed": {
		"straight": "closed front is a plain rounded rectangle",
		"lean-half": "closed front leans at half the open angle, so the pair reads as one folder in two states",
	},
	"papers": {
		"none": "open folder shows the inside of the back sheet",
		"one": "one paper sheet peeking out when open",
		"two": "two sheets, the rear one higher and to the right, as in the reference",
	},
	"tab": {
		"sloped": "long flat tab with a soft S shoulder stepping down to the right (the reference)",
		"step": "a short vertical shoulder of two radius-2 arcs",
		"small": "a narrow, lower tab with a short slope",
	},
	"edge": {
		"tinted": "1 px inner edge at 48 in orange 500 at 30 %: the fill's own darker tone",
		"lit": "no dark edge; a 1 px lighter band on the top and left edges",
		"tinted-lit": "both: the tinted edge plus the lit band",
		"hairline": "nothing at 48; the 1 px tinted edge appears at 32 and 16 only",
	},
	"surface": {
		"flat": "flat two-tone, as the reference",
		"gradient": "a very gentle top-to-bottom ramp plus a thin lighter top edge",
		"cast": "flat two-tone plus a soft shade where the front meets the papers and back",
	},
	"depth": {
		"none": "no depth cue (G0, as the reference)",
		"contact": "a soft contact shadow under the folder",
		"underside": "a slim 2 px darker strip along the bottom of the front (1 px at 16 is the edge)",
		"both": "contact shadow and underside strip",
	},
}
ORDER = ["flap", "closed", "papers", "tab", "edge", "surface", "depth"]

VARIANTS = {
	"G0": dict(flap="lean-18", closed="lean-half", papers="two", tab="sloped", edge="tinted", surface="flat", depth="none"),
	"G1": dict(flap="lean-10", closed="lean-half", papers="two", tab="sloped", edge="tinted", surface="gradient", depth="contact"),
	"G2": dict(flap="lean-6", closed="straight", papers="one", tab="step", edge="lit", surface="flat", depth="underside"),
	"G3": dict(flap="lean-13", closed="lean-half", papers="two", tab="small", edge="tinted-lit", surface="cast", depth="contact"),
	"G4": dict(flap="lean-16", closed="lean-half", papers="none", tab="sloped", edge="hairline", surface="flat", depth="both"),
	"G5": dict(flap="lean-8", closed="straight", papers="two", tab="small", edge="tinted", surface="gradient", depth="underside"),
	"G6": dict(flap="lean-12", closed="lean-half", papers="one", tab="step", edge="lit", surface="cast", depth="contact"),
}
BLURB = {
	"G0": "the reference as drawn, in Afterglow gold, plus only the tinted edge",
	"G1": "reference shape, calmer lean, Mint-like gentle ramp and contact shadow",
	"G2": "squarest and quietest: step tab, straight closed front, lit edge, no dark line",
	"G3": "small tab, two papers, soft inner shade: the most dimensional",
	"G4": "flat as the reference at 48, a hairline only at small sizes, most open",
	"G5": "small tab, straight closed front, ramp and underside strip",
	"G6": "step tab, one paper, lit edge with inner shade",
}
MIXES = {
	"M1": dict(flap="lean-10", closed="lean-half", papers="two", tab="sloped", edge="tinted-lit", surface="gradient", depth="contact"),
	"M2": dict(flap="lean-12", closed="straight", papers="one", tab="step", edge="tinted", surface="flat", depth="both"),
}
MIX_FROM = {
	"M1": "G1 with G3's edge (tinted plus lit): the recommendation",
	"M2": "G6's flap and papers, G2's tab and closed front, G1's edge, G4's depth",
}
ALL = {**VARIANTS, **MIXES}


def tags(cfg):
	return " · ".join("%s: %s" % (a.upper(), cfg[a]) for a in ORDER)


def _n(v):
	return "%g" % round(v, 3)


# ---- geometry on the 48 grid: landscape keyline x 4–44, y 8–40 ------------------------------------------------------------------------------
L, R, T, B = 4, 44, 8, 40
BT = 12  # back body top, below the tab
FT_C, FT_O = 16, 20  # closed and open front tops


def half(v):
	return round(v * 2) / 2


def leans(cfg):
	a = int(cfg["flap"].split("-")[1])
	so = half((B - FT_O) * math.tan(math.radians(a)))
	sc = half((B - FT_C) * math.tan(math.radians(a / 2))) if cfg["closed"] == "lean-half" else 0
	return so, sc


def back_d(cfg, right, bottom=B - 1):
	tab = cfg["tab"]
	top = T + 1 if tab == "small" else T
	rt, rr, rb = 3.5, 3, 3
	d = "M%s %s V%s A%s %s 0 0 1 %s %s " % (_n(L), _n(bottom - rb), _n(top + rt), rt, rt, _n(L + rt), _n(top))
	if tab == "sloped":
		x1, x2 = 15, 23
		d += "H%s C%s %s %s %s %s %s " % (x1, x1 + 3.5, _n(top), x2 - 3.5, BT, x2, BT)
	elif tab == "step":
		x1 = 18
		d += "H%s a2 2 0 0 1 2 2 a2 2 0 0 0 2 2 " % (x1 - 2)
	else:
		x1, x2 = 12, 16
		d += "H%s C%s %s %s %s %s %s " % (x1, x1 + 2, _n(top), x2 - 2, BT, x2, BT)
	d += "H%s A%s %s 0 0 1 %s %s V%s A%s %s 0 0 1 %s %s H%s A%s %s 0 0 1 %s %s Z" % (
		_n(right - rr), rr, rr, _n(right), _n(BT + rr), _n(bottom - rb), rb, rb, _n(right - rb), _n(bottom), _n(L + rb), rb, rb, _n(L), _n(bottom - rb))
	return d


def rpoly(pts):
	"""Closed polygon with rounded corners: pts are (x, y, r), r the cut length along each edge; corners are cubic quarter-rounds."""
	n, segs = len(pts), []
	for i in range(n):
		x, y, r = pts[i]
		px, py, _ = pts[i - 1]
		nx, ny, _ = pts[(i + 1) % n]
		d1, d2 = math.hypot(x - px, y - py), math.hypot(nx - x, ny - y)
		u1, u2 = ((x - px) / d1, (y - py) / d1), ((nx - x) / d2, (ny - y) / d2)
		a = (x - u1[0] * r, y - u1[1] * r)
		b = (x + u2[0] * r, y + u2[1] * r)
		k = 0.55 * r
		segs.append((a, (a[0] + u1[0] * k, a[1] + u1[1] * k), (b[0] - u2[0] * k, b[1] - u2[1] * k), b))
	d = "M%s %s " % (_n(segs[0][0][0]), _n(segs[0][0][1]))
	for i, (a, c1, c2, b) in enumerate(segs):
		if i:
			d += "L%s %s " % (_n(a[0]), _n(a[1]))
		d += "C%s %s %s %s %s %s " % (_n(c1[0]), _n(c1[1]), _n(c2[0]), _n(c2[1]), _n(b[0]), _n(b[1]))
	return d + "Z"


def flap_d(s, top, bl=2):
	return rpoly([(L, B, bl), (L + s, top, 3), (R, top, 3), (R - s, B, 3)])


def rect_d(x, y, w, h, r):
	return rpoly([(x, y, r), (x + w, y, r), (x + w, y + h, r), (x, y + h, r)])


# ---- painting ---------------------------------------------------------------------------------------------------------------------------------
class Ctx:
	"""Collects defs (gradients, clips, filters) with ids unique to one icon (prefix)."""

	def __init__(self, pre, cfg, size, pal="gold"):
		self.pre, self.cfg, self.size, self.n, self.defs, self.clips = pre, cfg, size, 0, {}, {}
		self.c = colours(pal)
		e = cfg["edge"]
		u = 48 / size if size < 48 else 1  # one screen pixel in grid units (1.5 at 32)
		self.u = u
		if size >= 48:
			self.edge = dict(tinted=0.30, lit=0, **{"tinted-lit": 0.30}, hairline=0)[e]
			self.band = e in ("lit", "tinted-lit")
		else:
			self.edge = 0.38 if e in ("tinted", "tinted-lit", "hairline") else 0.26
			self.band = e in ("lit", "tinted-lit")

	def id(self, k):
		self.n += 1
		return "%s-%s%d" % (self.pre, k, self.n)

	def clip(self, d):
		if d not in self.clips:
			cid = self.id("c")
			self.clips[d] = cid
			self.defs[cid] = '<clipPath id="%s"><path d="%s"/></clipPath>' % (cid, d)
		return self.clips[d]

	def grad(self, top, bot):
		gid = "%s-g%s%s" % (self.pre, top[1:], bot[1:])
		self.defs[gid] = '<linearGradient id="%s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (gid, top, bot)
		return "url(#%s)" % gid

	def blur(self, sd):
		fid = "%s-b%s" % (self.pre, str(sd).replace(".", "_"))
		self.defs[fid] = '<filter id="%s" x="-50%%" y="-50%%" width="200%%" height="200%%"><feGaussianBlur stdDeviation="%s"/></filter>' % (fid, sd)
		return "url(#%s)" % fid

	def face(self, d, fill, hl=None, grad=None, edge=True, edge_op=None, k=1.0):
		"""One surface: fill (or gentle ramp), optional lit band (top-left, or top only for the ramp), optional tinted inner edge."""
		cfg, u = self.cfg, self.u / k
		paint = self.grad(*grad) if grad and cfg["surface"] == "gradient" else fill
		band = None
		if hl and self.band:
			band = (u, u)
		elif hl and grad and cfg["surface"] == "gradient":
			band = (0, u)
		if band:
			cid = self.clip(d)
			out = '<path d="%s" fill="%s"/><g clip-path="url(#%s)"><path d="%s" fill="%s" transform="translate(%s %s)"/></g>' % (d, hl, cid, d, paint, _n(band[0]), _n(band[1]))
		else:
			out = '<path d="%s" fill="%s"/>' % (d, paint)
		op = self.edge if edge_op is None else edge_op
		if edge and op:
			cid = self.clip(d)
			out += '<g clip-path="url(#%s)"><path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-opacity="%s"/></g>' % (cid, d, self.c["edge"], _n(2 * u), op)
		return out


def folder(ctx, state="closed", emblem=None, k=1.0, shadow=True):
	"""The folder in the 48 grid. k is the scale it will be drawn at (edges keep one screen pixel)."""
	cfg, c = ctx.cfg, ctx.c
	so, sc = leans(cfg)
	s, top = (sc, FT_C) if state == "closed" else (so, FT_O)
	right = R - s - (1 if s else 0)
	bd = back_d(cfg, right)
	out = ""
	if shadow and cfg["depth"] in ("contact", "both"):
		out += '<ellipse cx="%s" cy="%s" rx="%s" ry="1.5" fill="%s" opacity="0.3" filter="%s"/>' % (_n((L + R) / 2 + 1), _n(B + 0.4), _n((R - L) * 0.43), c["contact"], ctx.blur(1))
	out += ctx.face(bd, c["back"], c["hl_back"], c["grad_back"], k=k)
	if state == "open" and cfg["papers"] != "none":
		pe = 0.2 if ctx.edge else 0
		if cfg["papers"] == "two":
			out += ctx.face(rect_d(9, 14, right - 3 - 9, B - 16, 1.5), c["paper_back"], edge_op=pe if ctx.edge else 0.0, k=k)
			out += ctx.face(rect_d(7, 16, right - 6 - 7, B - 18, 1.5), c["paper_front"], edge_op=pe if ctx.edge else 0.0, k=k)
		else:
			out += ctx.face(rect_d(8, 15, right - 4 - 8, B - 17, 1.5), c["paper_front"], edge_op=pe if ctx.edge else 0.0, k=k)
	fd = flap_d(s, top, 0.8 if cfg["flap"] == "lean-18" else 2)
	if cfg["surface"] == "cast":
		cid = ctx.clip(bd)
		out += '<g clip-path="url(#%s)"><path d="%s" fill="%s" opacity="0.32" filter="%s" transform="translate(0 -0.5)"/></g>' % (cid, fd, c["cast"], ctx.blur(1.3))
	out += ctx.face(fd, c["flap"], c["hl_flap"], c["grad_flap"], k=k)
	if cfg["depth"] in ("underside", "both"):
		cid = ctx.clip(fd)
		out += '<g clip-path="url(#%s)"><rect x="%s" y="%s" width="%s" height="%s" fill="%s"/></g>' % (cid, L, _n(B - 2 * ctx.u / k if ctx.size < 48 else B - 2), R - L, 4, c["under"])
		if ctx.edge:  # keep the edge over the strip
			out += '<g clip-path="url(#%s)"><path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-opacity="%s"/></g>' % (cid, fd, c["edge"], _n(2 * ctx.u / k), ctx.edge)
	if emblem:
		out += EMBLEMS[emblem](c["emblem"], c["flap"], 30 + (s / 2 if state == "closed" else 0), 28.5)
	return out


# ---- emblems for the special folders: embossed in the gold's darker tone on the front, right of the overlay corner -------------------------------
def E_documents(e, f, cx, cy):
	pg = rpoly([(cx - 5, cy - 7, 0.8), (cx + 2, cy - 7, 0.3), (cx + 5, cy - 4, 0.3), (cx + 5, cy + 7, 0.8), (cx - 5, cy + 7, 0.8)])
	return ('<path d="%s" fill="%s"/>' % (pg, e) + '<path d="M%s %s V%s H%s Z" fill="%s"/>' % (_n(cx + 2), _n(cy - 7), _n(cy - 4), _n(cx + 5), mix(e, f, 0.5))
		+ "".join('<rect x="%s" y="%s" width="%s" height="1.6" rx="0.4" fill="%s"/>' % (_n(cx - 3), _n(cy + dy), w, f) for dy, w in ((-1.5, 6), (1.8, 6), (5, 4))))


def E_pictures(e, f, cx, cy):
	return ('<path d="%s" fill="%s"/>' % (rect_d(cx - 7, cy - 6, 14, 12, 1.5), e) + '<path d="%s" fill="%s"/>' % (rect_d(cx - 5.4, cy - 4.4, 10.8, 8.8, 0.6), f)
		+ '<path d="M%s %s L%s %s L%s %s L%s %s L%s %s Z" fill="%s"/>' % (_n(cx - 5.4), _n(cy + 4.4), _n(cx - 2), _n(cy), _n(cx + 0.5), _n(cy + 2.4), _n(cx + 2.5), _n(cy + 0.6), _n(cx + 5.4), _n(cy + 4.4), e)
		+ '<circle cx="%s" cy="%s" r="1.5" fill="%s"/>' % (_n(cx + 2.4), _n(cy - 1.8), e))


def E_music(e, f, cx, cy):
	return ('<path d="M%s %s L%s %s V%s L%s %s Z" fill="%s"/>' % (_n(cx - 3.6), _n(cy - 4.5), _n(cx + 5.2), _n(cy - 7), _n(cy - 4.2), _n(cx - 3.6), _n(cy - 1.7), e)
		+ '<rect x="%s" y="%s" width="1.7" height="10" fill="%s"/><rect x="%s" y="%s" width="1.7" height="10" fill="%s"/>' % (_n(cx - 3.6), _n(cy - 4.5), e, _n(cx + 3.5), _n(cy - 7), e)
		+ '<ellipse cx="%s" cy="%s" rx="2.6" ry="2" transform="rotate(-20 %s %s)" fill="%s"/>' % (_n(cx - 5), _n(cy + 5.3), _n(cx - 5), _n(cy + 5.3), e)
		+ '<ellipse cx="%s" cy="%s" rx="2.6" ry="2" transform="rotate(-20 %s %s)" fill="%s"/>' % (_n(cx + 2.1), _n(cy + 2.8), _n(cx + 2.1), _n(cy + 2.8), e))


def E_videos(e, f, cx, cy):
	t = '<path d="%s" fill="%s"/>' % (rect_d(cx - 7, cy - 5.5, 14, 11, 1.5), e)
	t += "".join('<rect x="%s" y="%s" width="1.6" height="1.4" rx="0.3" fill="%s"/>' % (_n(cx - 5.6 + i * 3.2), _n(cy + dy), f) for i in range(4) for dy in (-4.6, 3.2))
	return t + '<path d="M%s %s V%s L%s %s Z" fill="%s"/>' % (_n(cx - 1.8), _n(cy - 2.6), _n(cy + 2.6), _n(cx + 2.8), _n(cy), f)


def E_desktop(e, f, cx, cy):
	return ('<path d="%s" fill="%s"/>' % (rect_d(cx - 7, cy - 6.5, 14, 10, 1.2), e) + '<path d="%s" fill="%s"/>' % (rect_d(cx - 5.4, cy - 4.9, 10.8, 6.8, 0.5), f)
		+ '<rect x="%s" y="%s" width="2.6" height="2.4" fill="%s"/>' % (_n(cx - 1.3), _n(cy + 3.4), e) + '<path d="%s" fill="%s"/>' % (rect_d(cx - 4.5, cy + 5.4, 9, 1.8, 0.7), e))


def E_network(e, f, cx, cy):
	return ('<circle cx="%s" cy="%s" r="6.8" fill="%s"/>' % (_n(cx), _n(cy), e)
		+ '<ellipse cx="%s" cy="%s" rx="2.9" ry="6.8" fill="none" stroke="%s" stroke-width="1.3"/>' % (_n(cx), _n(cy), f)
		+ '<path d="M%s %s H%s M%s %s H%s M%s %s H%s" stroke="%s" stroke-width="1.3" fill="none"/>' % (
			_n(cx - 6.8), _n(cy), _n(cx + 6.8), _n(cx - 5.6), _n(cy - 3.4), _n(cx + 5.6), _n(cx - 5.6), _n(cy + 3.4), _n(cx + 5.6), f)
		)


EMBLEMS = {"documents": E_documents, "pictures": E_pictures, "music": E_music, "videos": E_videos, "desktop": E_desktop, "network": E_network}

# 16 px emblems, X = emblem tone, . = front colour; 4 rows at y 8–11, right-aligned to x 12, clear of the 8 × 8 overlay corner (x 0–7, y 8–15)
PX_EMBLEMS = {
	"documents": ["XX..", "XXX.", "X..X", "XXXX"],
	"pictures": ["....X", ".X...", "XXX.X", "XXXXX"],
	"music": [".XXXX", ".X..X", "XX.XX", "XX.XX"],
	"videos": ["X.X.X", "XXXXX", "XXXXX", "X.X.X"],
	"desktop": ["XXXXX", "X...X", "XXXXX", ".XXX."],
	"network": [".XXX.", "XX.XX", "XX.XX", ".XXX."],
}
SPECIALS = ["documents", "pictures", "music", "videos", "desktop", "network"]
SPECIAL_NAMES = {"documents": "My Documents (235)", "pictures": "My Pictures (236)", "music": "My Music (237)", "videos": "My Videos (238)",
	"desktop": "Desktop (35)", "network": "My Network Places (18)", "folder-options": "Folder Options", "folders-glyph": "Folders (toolbar)"}


def gear_d(cx, cy, ro=8, ri=6, n=8):
	pts = []
	for i in range(n):
		a = math.radians(i * 360 / n)
		for da, r in ((-15, ri), (-9, ro), (9, ro), (15, ri)):
			b = a + math.radians(da)
			pts.append((cx + r * math.cos(b), cy + r * math.sin(b), 0.6))
	return rpoly(pts)


def folder_options(ctx):
	c = ctx.c
	plate = rect_d(5, 5, 38, 38, 8)
	sky = ctx.grad(TOK["sky-1"], TOK["sky-7"])
	cid = ctx.clip(plate)
	out = '<ellipse cx="25" cy="43.4" rx="16" ry="1.5" fill="%s" opacity="0.3" filter="%s"/>' % (c["contact"], ctx.blur(1))
	out += '<path d="%s" fill="%s"/><g clip-path="url(#%s)"><path d="%s" fill="%s" transform="translate(%s %s)"/></g>' % (plate, TOK["horizon"], cid, plate, sky, _n(ctx.u), _n(ctx.u))
	k = 0.62
	out += '<g transform="translate(9.5 9.5) scale(%s)">%s</g>' % (k, folder(ctx, "closed", k=k, shadow=False))
	g = gear_d(34, 33.5)
	out += ctx.face(g, TOK["body"], edge_op=0.45) + '<circle cx="34" cy="33.5" r="2.4" fill="%s"/>' % TOK["sky-4"]
	return out


def folders_glyph(ctx):
	tree = "M9 16.5 V38 M9 24 H22 M9 38 H22"
	out = '<path d="%s" fill="none" stroke="%s" stroke-width="3.6" stroke-linecap="round"/><path d="%s" fill="none" stroke="%s" stroke-width="1.6" stroke-linecap="round"/>' % (
		tree, TOK["horizon"], tree, TOK["text2"])
	k = 0.4
	sub = Ctx(ctx.pre + "m", dict(ctx.cfg, edge="tinted"), ctx.size)
	sub.c = ctx.c
	sub.edge = 0.4
	for tx, ty in ((1.4, -0.4), (22.4, 14.6), (22.4, 28.6)):
		out += '<g transform="translate(%s %s) scale(%s)">%s</g>' % (_n(tx), _n(ty), k, folder(sub, "closed", k=k, shadow=False))
	ctx.defs.update(sub.defs)
	return out


def icon(cfg, name, size, pre, pal="gold"):
	"""(defs, body) for one icon of the family at one profile (48 master, 32)."""
	ctx = Ctx(pre, cfg, size, pal)
	if name == "folder":
		b = folder(ctx)
	elif name == "folder-open":
		b = folder(ctx, "open")
	elif name in EMBLEMS:
		b = folder(ctx, emblem=name)
	elif name == "folder-options":
		b = folder_options(ctx)
	else:
		b = folders_glyph(ctx)
	return "".join(ctx.defs.values()), b


# ---- hinted 16 px: pixels, crisp, 1 px tinted edge, no shadow, no gradient ----------------------------------------------------------------------
def hint16(cfg, state="closed", emblem=None, pal="gold"):
	c = colours(pal)
	a = int(cfg["flap"].split("-")[1])
	tab = cfg["tab"]
	grid = {}

	def fill(layer, x0, x1, y):
		for x in range(x0, x1 + 1):
			grid[(x, y)] = layer

	so = max(1, round(5 * math.tan(math.radians(a))))
	sc = 0  # a half lean is under one pixel over seven rows: the closed folder is upright at 16
	s, ft = (sc, 7) if state == "closed" else (so, 8)
	br = 14 - s
	# back: tab then body
	if tab == "sloped":
		fill(0, 2, 5, 3)
		fill(0, 1, 7, 4)
	elif tab == "step":
		fill(0, 2, 6, 3)
		fill(0, 1, 6, 4)
	else:
		fill(0, 2, 4, 4)
	for y in range(5, 14):
		fill(0, 1, br - (1 if y == 5 else 0), y)
	if state == "open" and cfg["papers"] != "none":
		if cfg["papers"] == "two":
			for y in range(6, 13):
				fill(1, 3, br - 2, y)
			for y in range(7, 13):
				fill(2, 2, br - 4, y)
		else:
			for y in range(6, 13):
				fill(2, 2, br - 3, y)
	rows = 13 - ft
	for y in range(ft, 14):
		sh = round(s * (13 - y) / rows) if rows else 0
		x0, x1 = 1 + sh, 14 - s + sh
		if y == ft:
			x0, x1 = x0 + 1, x1 - 1
		if y == 13:
			x0, x1 = x0 + 1, x1 - 1
		fill(3, x0, x1, y)
	fills = {0: c["back"], 1: c["paper_back"], 2: c["paper_front"], 3: c["flap"]}
	px = {}
	for (x, y), l in grid.items():
		nb = [grid.get(p) for p in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1))]
		if any(n is None for n in nb):
			px[(x, y)] = c["px_edge"]
		elif l == 3 and grid.get((x, y - 1)) in (0, 1, 2):
			px[(x, y)] = c["px_inner"]
		else:
			px[(x, y)] = fills[l]
	if emblem and state == "closed":
		art = PX_EMBLEMS[emblem]
		ox = 13 - len(art[0])
		for j, row in enumerate(art):
			for i, ch in enumerate(row):
				if ch == "X":
					px[(ox + i, 8 + j)] = c["px_emblem"]
	return "".join('<rect x="%d" y="%d" width="1" height="1" fill="%s"/>' % (x, y, col) for (x, y), col in sorted(px.items(), key=lambda p: (p[0][1], p[0][0])))


# ---- output ----------------------------------------------------------------------------------------------------------------------------------
HEAD = """<!--
Afterglow icons, variant D, folder variants G: %s

(c) Copyright 2026 Liminal HQ, Scott Morris
SPDX-License-Identifier: Apache-2.0 OR MIT
-->
"""
FAMILY = ["folder", "folder-open"] + SPECIALS + ["folder-options", "folders-glyph"]
FILE = {"folder": "folder", "folder-open": "folder-open", "documents": "my-documents", "pictures": "my-pictures", "music": "my-music", "videos": "my-videos",
	"desktop": "desktop", "network": "network-places", "folder-options": "folder-options", "folders-glyph": "folders-glyph"}


def standalone(body, defs, vb, title, crisp=False):
	sr = ' shape-rendering="crispEdges"' if crisp else ""
	return (HEAD % title + '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d"%s>\n<defs>%s</defs>\n%s\n</svg>\n'
		% (vb, vb, vb, vb, sr, defs, body))


def write_family(cfg, out, label, pal="gold"):
	os.makedirs(out, exist_ok=True)
	t = tags(cfg)
	for k in FAMILY:
		d, b = icon(cfg, k, 48, "%s-%s" % (label, k), pal)
		open(os.path.join(out, FILE[k] + ".svg"), "w").write(standalone(b, d, 48, "%s %s, 48 master (%s)" % (label, FILE[k], t)))
		if k in ("folder", "folder-open") or k in SPECIALS:
			d, b = icon(cfg, k, 32, "%s-%s-32" % (label, k), pal)
			open(os.path.join(out, FILE[k] + "-32.svg"), "w").write(standalone(b, d, 48, "%s %s, 32 px profile (%s)" % (label, FILE[k], t)))
			h = hint16(cfg, "open" if k == "folder-open" else "closed", k if k in SPECIALS else None, pal)
			open(os.path.join(out, FILE[k] + "-16.svg"), "w").write(standalone(h, "", 16, "%s %s, hinted 16 px (%s)" % (label, FILE[k], t), True))


# ---- the D-now reference, drawn by ../folder-variants/folders.py ---------------------------------------------------------------------------------
def load_fv():
	p = os.path.join(HERE, "..", "folder-variants", "folders.py")
	spec = importlib.util.spec_from_file_location("folders_f", p)
	m = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(m)
	return m


# ---- the sheet -------------------------------------------------------------------------------------------------------------------------------
BG, CELL, LAB, HD, SUB, DIM = "#0c0c10", "#14161d", "#e0e0e0", "#ffd08e", "#b4bfce", "#7c8796"
PANELS = [("void", TOK["void"]), ("desktop", TOK["desktop"]), ("dusk sky", "url(#skybg)"), ("paper", TOK["paper-900"])]
FONT = "'DejaVu Sans', sans-serif"


def txt(x, y, s, size=12, fill=LAB, anchor="start", weight=400, fam=FONT):
	if not s:
		return ""
	s = s.replace("&", "&amp;").replace("<", "&lt;")
	return '<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" fill="%s" text-anchor="%s">%s</text>' % (_n(x), _n(y), fam, size, weight, fill, anchor, s)


def use(k, x, y, size):
	return '<use href="#%s" x="%d" y="%d" width="%d" height="%d"/>' % (k, x, y, size, size)


class Syms:
	def __init__(self):
		self.defs, self.syms, self.have = [], [], set()

	def add(self, sid, vb, body, defs=""):
		if sid in self.have:
			return sid
		self.have.add(sid)
		self.defs.append(defs)
		self.syms.append('<symbol id="%s" viewBox="0 0 %d %d" overflow="visible">%s</symbol>' % (sid, vb, vb, body))
		return sid

	def g(self, label, cfg, k, size, pal="gold"):
		"""symbol id for icon k of a G family at 48/32 (vector) or 16 (hinted)."""
		sid = "%s-%s-%d%s" % (label, k, size, "" if pal == "gold" else "-" + pal)
		if sid in self.have:
			return sid
		if size == 16:
			return self.add(sid, 16, hint16(cfg, "open" if k == "folder-open" else "closed", k if k in SPECIALS else None, pal))
		d, b = icon(cfg, k, size, sid, pal)
		return self.add(sid, 48, b, d)


def arrow(size):
	"""The shortcut overlay as ReactOS places it: 16 × 16 at 48, 11 × 11 at 32, 8 × 8 at 16 (bottom-left), as a stand-in drawing."""
	n = {48: 16, 32: 11, 16: 8}[size]
	s = n / 11
	return ('<g transform="translate(0 %s) scale(%s)"><rect x="0.5" y="0.5" width="10" height="10" fill="#ffffff" stroke="#000000" stroke-width="1"/>'
		'<path d="M3 8.5 C3 5.5 4.5 4 7 4 M5.2 2.2 L7.6 4 L5.2 5.8" fill="none" stroke="#000000" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/></g>') % (_n(size - n), _n(s))


def ref_image(x, y, size, href):
	"""The reference picture placed so its folder spans the same 40-of-48 width and sits on the same bottom line as ours."""
	sc = size / 48 * 40 / 727
	ix, iy = x + size / 48 * 4 - 58 * sc, y + size / 48 * 40 - 548 * sc
	return '<image href="%s" x="%s" y="%s" width="%s" height="%s"/>' % (href, _n(ix), _n(iy), _n(852 * sc), _n(620 * sc))


def write_sheet(fv, syms, ref_t, ref_o):
	W = 1880
	out = []
	y = 40
	out.append(txt(40, y + 14, "Afterglow icons · variant D · folder variants G", 30, "#ffffff", weight=600))
	y += 36
	for line in [
		"After the owner's reference: a soft open folder with a gold back sheet, cream papers and a lighter front flap leaning right, rounded, no ink outline. Colours are Afterglow tokens only:",
		"back orange 200 #ffaa40, front brand-gold #ffd08e, papers paper 900 #fbfaf6 and indigo 100 #f1eee6, edge orange 500 #7d5422 at 30 %. The closed folder is the hero (ReactOS shows it",
		"almost everywhere, at 48, 32 and 16); the open folder is secondary. 24 px is not used by ReactOS and is not shown. Pick per axis, e.g. \"flap of G3, edge of G2, depth of G4\".",
	]:
		y += 20
		out.append(txt(40, y, line, 13, SUB))
	y += 22
	col = [40, 960]
	yy = [y, y]
	for i, a in enumerate(ORDER):
		cc = 0 if i < 4 else 1
		out.append(txt(col[cc], yy[cc] + 14, a.upper(), 13, HD, weight=600))
		yy[cc] += 18
		for tag, why in AXES[a].items():
			out.append(txt(col[cc] + 12, yy[cc] + 12, tag, 11, "#ffffff", weight=600))
			out.append(txt(col[cc] + 100, yy[cc] + 12, why, 11, SUB))
			yy[cc] += 16
		yy[cc] += 8
	y = max(yy) + 14
	# column heads
	X96 = 330
	PX = X96 + 2 * 104 + 12
	PW = 296
	out.append(txt(40, y + 12, "Variant and tags", 12, HD, weight=600))
	out.append(txt(X96 + 48, y + 12, "Closed · 96", 11, HD, "middle", 600))
	out.append(txt(X96 + 152, y + 12, "Open · 96", 11, HD, "middle", 600))
	for j, (nm, _) in enumerate(PANELS):
		out.append(txt(PX + j * (PW + 8) + PW / 2, y + 12, "on %s · closed 48 32 16 · open 48 32 16" % nm, 11, HD, "middle", 600))
	y += 22

	def row(label, kind, cfg, y):
		H = 112
		out.append('<rect x="40" y="%d" width="%d" height="%d" rx="6" fill="%s"/>' % (y, W - 80, H, CELL))
		name = {"ref": "Reference", "d": "D now"}.get(kind, label)
		out.append(txt(52, y + 26, name, 20, {"ref": "#8fd3ff", "d": "#f88296"}.get(kind, "#ffffff"), weight=700))
		if kind == "ref":
			lines = ["The owner's picture at the same scale (folder 40", "of 48 wide). Its yellows are illustration only;", "the G colours are Afterglow tokens."]
		elif kind == "d":
			lines = ["Today's set D folder: navy outline, extrusion,", "tab box stacked on the back. Shown for scale."]
		else:
			lines = ["FLAP %s · CLOSED %s" % (cfg["flap"], cfg["closed"]), "PAPERS %s · TAB %s" % (cfg["papers"], cfg["tab"]),
				"EDGE %s · SURFACE %s" % (cfg["edge"], cfg["surface"]), "DEPTH %s" % cfg["depth"]]
			bl = BLURB.get(label) or MIX_FROM[label]
			cut = bl.rfind(" ", 0, 52) if len(bl) > 52 else len(bl)
			lines += [bl[:cut], bl[cut:].strip()]
		for i, l in enumerate(lines):
			out.append(txt(52, y + 44 + i * 13, l, 10.5, SUB if (kind == "g" and i < 4) or kind != "g" else "#8c96a6"))
		# 96 cells on the dusk desktop
		for i, k in enumerate(("folder", "folder-open")):
			cx = X96 + i * 104
			out.append('<rect x="%d" y="%d" width="96" height="96" rx="4" fill="%s"/>' % (cx, y + 8, TOK["desktop"]))
			if kind == "ref":
				if k == "folder-open":
					out.append('<g><clipPath id="rc96"><rect x="%d" y="%d" width="96" height="96"/></clipPath><g clip-path="url(#rc96)">%s</g></g>' % (cx, y + 8, ref_image(cx, y + 8, 96, ref_o)))
				else:
					out.append(txt(cx + 48, y + 60, "(not drawn)", 10, DIM, "middle"))
			elif kind == "d":
				out.append(use("D-%s-48" % {"folder": "folder", "folder-open": "folder-open"}[k], cx, y + 8, 96))
			else:
				out.append(use(syms.g(label, cfg, k, 48), cx, y + 8, 96))
		for j, (_, bg) in enumerate(PANELS):
			bx = PX + j * (PW + 8)
			out.append('<rect x="%d" y="%d" width="%d" height="96" rx="5" fill="%s"/>' % (bx, y + 8, PW, bg))
			x = bx + 10
			for k in ("folder", "folder-open"):
				for s in (48, 32, 16):
					yy0 = y + 8 + (96 - s) // 2 + (8 if s < 48 else 0)
					if kind == "ref":
						if k == "folder-open":
							cid = "rcl%d%d" % (j, s)
							out.append('<clipPath id="%s"><rect x="%d" y="%d" width="%d" height="%d"/></clipPath><g clip-path="url(#%s)">%s</g>' % (cid, x, yy0, s, s, cid, ref_image(x, yy0, s, ref_t)))
					elif kind == "d":
						out.append(use("D-%s-%s" % (k, "h16" if s == 16 and k == "folder" else s if s != 32 else 48), x, yy0, s))
					else:
						out.append(use(syms.g(label, cfg, k, s), x, yy0, s))
					x += s + 8
				x += 8
		return y + H + 6

	fvsyms = []
	fam = fv.d_family()
	for k in ("folder", "folder-open"):
		for s in (48, 16):
			d, b = fv.build(fam[k][0], fam[k][1], "d-now", s, "D-%s-%d" % (k, s))
			syms.add("D-%s-%d" % (k, s), 48, b, d)
	syms.add("D-folder-h16", 16, fv.d_hint16())
	y = row("Ref", "ref", None, y)
	y = row("D", "d", None, y)
	for label, cfg in ALL.items():
		if label == "M1":
			y += 6
			out.append(txt(40, y + 14, "Mixes · tags taken from different variants, to show the axes compose", 15, HD, weight=600))
			y += 24
		y = row(label, "g", cfg, y)

	# specials and the overlay corner
	y += 14
	out.append(txt(40, y + 14, "Special folders (closed, emblem on the front, clear of the shortcut corner) · Folder Options · Folders glyph · shortcut overlay test", 15, HD, weight=600))
	y += 22
	out.append(txt(40, y + 12, "Each cell: 48, then the hinted 16 below. On the dusk desktop, then on paper. Last column: closed 48, 32 and hinted 16 with ReactOS's shortcut arrow (16 × 16, 11 × 11, 8 × 8, bottom-left).", 11, SUB))
	y += 22
	items = SPECIALS + ["folder-options", "folders-glyph"]
	SX = 120
	for j, nm in enumerate(items):
		out.append(txt(SX + 30 + j * 64, y + 10, {"documents": "Docs", "pictures": "Pictures", "music": "Music", "videos": "Videos", "desktop": "Desktop", "network": "Network",
			"folder-options": "Options", "folders-glyph": "Folders"}[nm], 10, HD, "middle", 600))
		out.append(txt(SX + 556 + 30 + j * 64, y + 10, {"documents": "Docs", "pictures": "Pictures", "music": "Music", "videos": "Videos", "desktop": "Desktop", "network": "Network",
			"folder-options": "Options", "folders-glyph": "Folders"}[nm], 10, HD, "middle", 600))
	out.append(txt(SX + 1112 + 80, y + 10, "Shortcut overlay · desktop and paper", 10, HD, "middle", 600))
	y += 16
	for label, cfg in ALL.items():
		out.append('<rect x="40" y="%d" width="%d" height="84" rx="6" fill="%s"/>' % (y, W - 80, CELL))
		out.append(txt(52, y + 46, label, 18, "#ffffff", weight=700))
		for pj, bg in enumerate((TOK["desktop"], TOK["paper-900"])):
			bx = SX + pj * 556
			out.append('<rect x="%d" y="%d" width="%d" height="76" rx="5" fill="%s"/>' % (bx, y + 4, 8 * 64 + 16, bg))
			for j, nm in enumerate(items):
				x = bx + 8 + j * 64
				out.append(use(syms.g(label, cfg, nm, 48), x, y + 6, 48))
				if nm in SPECIALS:
					out.append(use(syms.g(label, cfg, nm, 16), x + 16, y + 58, 16))
		for pj, bg in enumerate((TOK["desktop"], TOK["paper-900"])):
			bx = SX + 1112 + pj * 170
			out.append('<rect x="%d" y="%d" width="160" height="76" rx="5" fill="%s"/>' % (bx, y + 4, bg))
			for s, dx in ((48, 8), (32, 70), (16, 116)):
				yy0 = y + 6 + (48 - s)
				out.append(use(syms.g(label, cfg, "folder", s), bx + dx, yy0, s))
				out.append('<svg x="%d" y="%d" width="%d" height="%d" viewBox="0 0 %d %d">%s</svg>' % (bx + dx, yy0, s, s, s, s, arrow(s)))
		y += 90

	# palette
	y += 14
	out.append(txt(40, y + 14, "Palette by role (Afterglow tokens) · and the yellow ramp for comparison", 15, HD, weight=600))
	y += 24
	c = colours("gold")
	roles = [("back", "orange 200", c["back"]), ("front flap", "brand-gold", c["flap"]), ("paper, front", "paper 900", c["paper_front"]), ("paper, rear", "indigo 100", c["paper_back"]),
		("edge (30 %)", "orange 500", c["edge"]), ("16 px edge", "orange 400", c["px_edge"]), ("16 px inner", "orange 300", c["px_inner"]), ("lit, back", "orange 100", c["hl_back"]),
		("lit, front", "pale", c["hl_flap"]), ("emblem", "orange 400", c["emblem"]), ("cast shade", "orange 600", c["cast"]), ("contact", "tile", c["contact"])]
	for i, (role, tok, hx) in enumerate(roles):
		x = 40 + i * 150
		out.append('<rect x="%d" y="%d" width="28" height="28" rx="3" fill="%s" stroke="#33384a" stroke-width="1"/>' % (x, y, hx))
		out.append(txt(x + 34, y + 10, role, 10, "#ffffff", weight=600))
		out.append(txt(x + 34, y + 22, "%s %s" % (tok, hx), 9.5, SUB))
	y += 42
	# folder-likeness comparison: recommended M1 in gold and in yellow, beside two of D's other icons for colour context
	out.append('<rect x="40" y="%d" width="%d" height="96" rx="6" fill="%s"/>' % (y, W - 80, CELL))
	for pj, bg in enumerate((TOK["desktop"], TOK["paper-900"])):
		bx = 52 + pj * 470
		out.append('<rect x="%d" y="%d" width="456" height="84" rx="5" fill="%s"/>' % (bx, y + 6, bg))
		x = bx + 10
		for pal in ("gold", "yellow"):
			for k in ("folder", "documents", "folder-open"):
				out.append(use(syms.g("M1", MIXES["M1"], k, 48, pal), x, y + 12, 48))
				x += 56
			out.append(use(syms.g("M1", MIXES["M1"], "folder", 16, pal), x, y + 28, 16))
			x += 40
	out.append(txt(1000, y + 30, "Left three of each panel: gold (orange 200 + brand-gold), the set's palette.", 11, SUB))
	out.append(txt(1000, y + 46, "Right three: the yellow ramp (yellow 200 #fbbf24 + yellow 100 #fddc87), a palette", 11, SUB))
	out.append(txt(1000, y + 62, "hue the set does not use for objects. Gold reads as a folder; yellow is the", 11, SUB))
	out.append(txt(1000, y + 78, "more traditional manila. Shown only for comparison; nothing departs from gold.", 11, SUB))
	y += 112
	out.append(txt(40, y + 12, "Recommended: M1 (FLAP lean-10 · CLOSED lean-half · PAPERS two · TAB sloped · EDGE tinted-lit · SURFACE gradient · DEPTH contact). Nearest the picture: G0. See notes.md.", 12, SUB))
	y += 30
	return doc(W, y, "the G folder sheet", syms, out)


def doc(W, H, title, syms, body):
	return (HEAD % title + '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">\n' % (W, H, W, H)
		+ '<defs><linearGradient id="skybg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>\n%s\n%s\n</defs>\n'
		% (TOK["sky-1"], TOK["sky-7"], "".join(syms.defs), "\n".join(syms.syms)) + '<rect width="%d" height="%d" fill="%s"/>\n' % (W, H, BG) + "\n".join(body) + "\n</svg>\n")


def write_strip(fv, syms):
	labs = list(ALL.items())
	cw = 150
	W = 40 + (len(labs) + 1) * cw + 20
	out = [txt(40, 32, "Closed folder, the hero · D now and G0–G6, M1, M2 · 48, 32, hinted 16 and the 16 at 4× · open 48 below · on the dusk desktop and on paper", 15, HD, weight=600)]
	for r, bg in enumerate((TOK["desktop"], TOK["paper-900"])):
		y0 = 48 + r * 196
		out.append('<rect x="30" y="%d" width="%d" height="186" rx="6" fill="%s"/>' % (y0, W - 50, bg))
		ink = "#ffffff" if r == 0 else "#1c1b20"
		for i, (label, cfg) in enumerate([("D", None)] + labs):
			x = 40 + i * cw
			if cfg is None:
				out.append(use("D-folder-48", x, y0 + 8, 48) + use("D-folder-48", x + 54, y0 + 24, 32) + use("D-folder-h16", x + 92, y0 + 40, 16))
				out.append('<g transform="translate(%d %d) scale(4)"><use href="#D-folder-h16" width="16" height="16"/></g>' % (x + 2, y0 + 62))
				out.append(use("D-folder-open-48", x + 74, y0 + 74, 48))
			else:
				out.append(use(syms.g(label, cfg, "folder", 48), x, y0 + 8, 48) + use(syms.g(label, cfg, "folder", 32), x + 54, y0 + 24, 32)
					+ use(syms.g(label, cfg, "folder", 16), x + 92, y0 + 40, 16))
				out.append('<g transform="translate(%d %d) scale(4)"><use href="#%s" width="16" height="16"/></g>' % (x + 2, y0 + 62, syms.g(label, cfg, "folder", 16)))
				out.append(use(syms.g(label, cfg, "folder-open", 48), x + 74, y0 + 74, 48) + use(syms.g(label, cfg, "folder-open", 16), x + 124, y0 + 106, 16))
			out.append(txt(x + 60, y0 + 176, "D now" if cfg is None else label, 12, ink, "middle", 700))
	return doc(W, 48 + 2 * 196 + 6, "closed folder strip", syms, out)


def render(svg, png, zoom=1):
	subprocess.run(["rsvg-convert", "-z", str(zoom), svg, "-o", png], check=True)


def outline_text(path):
	"""Text to paths through Inkscape, keeping the SPDX comment in front."""
	src = open(path).read()
	head = src[:src.index("-->") + 4]
	tmp = path + ".tmp.svg"
	subprocess.run(["inkscape", path, "--export-text-to-path", "--export-plain-svg", "--export-filename=" + tmp], check=True, capture_output=True)
	body = open(tmp).read()
	if body.startswith("<?xml"):
		body = body[body.index("?>") + 2:].lstrip()
	if not body.startswith("<!--"):  # Inkscape usually keeps the comment; put it back only if it did not
		body = head + body
	open(path, "w").write(body)
	os.remove(tmp)


def build_all(outline=True):
	fv = load_fv()
	for label, cfg in VARIANTS.items():
		write_family(cfg, os.path.join(HERE, "variant-" + label), label)
	for label, cfg in MIXES.items():
		write_family(cfg, os.path.join(HERE, "mix-" + label), label)
	raw = open(REF_PNG, "rb").read()
	ref_o = "data:image/png;base64," + base64.b64encode(raw).decode()
	tpath = os.path.join(HERE, ".ref-t.png")
	subprocess.run(["magick", REF_PNG, "-fuzz", "6%", "-fill", "none", "-draw", "color 2,2 floodfill", tpath], check=True)
	ref_t = "data:image/png;base64," + base64.b64encode(open(tpath, "rb").read()).decode()
	os.remove(tpath)
	syms = Syms()
	open(os.path.join(HERE, "sheet.svg"), "w").write(write_sheet(fv, syms, ref_t, ref_o))
	open(os.path.join(HERE, "strip.svg"), "w").write(write_strip(fv, Syms() if False else syms))
	for name in ("sheet", "strip"):
		p = os.path.join(HERE, name + ".svg")
		if outline and shutil.which("inkscape"):
			outline_text(p)
		render(p, os.path.join(HERE, name + ".png"))


def main():
	ap = argparse.ArgumentParser(description="Afterglow folder variants G for icon set D.")
	for a in ORDER:
		ap.add_argument("--" + a, choices=list(AXES[a]))
	ap.add_argument("--variant", choices=list(ALL))
	ap.add_argument("--palette", choices=list(PALETTES), default="gold")
	ap.add_argument("--out", help="write one family here instead of building everything")
	ap.add_argument("--no-outline", action="store_true", help="keep sheet text as text (faster)")
	ap.add_argument("--list", action="store_true")
	args = ap.parse_args()
	if args.list:
		for a in ORDER:
			print(a.upper())
			for t, why in AXES[a].items():
				print("  %-11s %s" % (t, why))
		for k, v in ALL.items():
			print("%s  %s" % (k, tags(v)))
		return
	if args.out or args.variant or any(getattr(args, a) for a in ORDER) or args.palette != "gold":
		cfg = dict(VARIANTS["G1"])
		cfg.update(ALL.get(args.variant, {}))
		cfg.update({a: getattr(args, a) for a in ORDER if getattr(args, a)})
		out = args.out or os.path.join(os.getcwd(), "folder-" + "-".join(cfg[a] for a in ORDER))
		write_family(cfg, out, args.variant or "custom", args.palette)
		print("wrote", out, "·", tags(cfg))
		return
	build_all(not args.no_outline)
	print("variants", len(VARIANTS), "mixes", len(MIXES), "icons per family", len(FAMILY))


if __name__ == "__main__":
	sys.exit(main())
