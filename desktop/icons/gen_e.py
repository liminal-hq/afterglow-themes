#!/usr/bin/env python3
# Afterglow icon set, variant E: every icon drawn in the language of the M1 folder, with hinted 16 px redraws and the sheet.
# The icons added in v2 are drawn in gen_v2.py, the dialog pictures of v3 in gen_v3.py, the full image's art of v4 in gen_v4.py and the
# namespace, registry and dialog art of v5 in gen_v5.py, with this file's Pen and registered here; hint16_v2.py holds the hand-tuned 16 px
# frames.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# The inventory, groups, keylines and sheet layout are the set's own; folders_g.py, beside this file, holds the M1 folder language. The
# folder family is not redrawn: it is imported from folders_g.py and rendered with M1's own tags, so the folders here are exactly M1. Everything else is drawn with the same face model:
# a flat two-tone base from palette tokens, a very gentle top-to-bottom ramp, a lit band on the top and left, a thin inner edge in a darker
# tone of the same hue, and a soft contact shadow. No ink outline anywhere. Deterministic: no randomness, no clock, no environment input.
#
#   python3 gen_e.py OUT_DIR         writes OUT_DIR/icons/ (the masters and profiles) and OUT_DIR/sheet.svg (text stays text)
import colorsys
import importlib.util
import math
import os
import re
import sys
import types

sys.dont_write_bytecode = True  # importing folders_g.py must not leave a cache beside it
HERE = os.path.dirname(os.path.abspath(__file__))
G_PY = os.path.join(HERE, "folders_g.py")


def load_g():
	spec = importlib.util.spec_from_file_location("folders_g", G_PY)
	m = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(m)
	return m


FG = load_g()
M1 = FG.MIXES["M1"]
rect_d, rpoly, mix, _n, contrast = FG.rect_d, FG.rpoly, FG.mix, FG._n, FG.contrast

# ---- palette: Afterglow tokens only ---------------------------------------------------------------------------------------------------------
# Hue ramps follow afterglow-themes/scripts/hues.mjs (dark mode): 100 is the anchor 45 % toward white, 200 the anchor, 300–600 the anchor
# 18, 36, 52 and 67 % toward the void. Neutrals are palette.mjs's ramps; sky, horizon and tile are the Dusk desktop tables (via folders_g.py).
WHITE, VOID_BG = "#ffffff", "#050507"


def ramp(anchor):
	return {100: mix(anchor, WHITE, 0.45), 200: anchor, 300: mix(anchor, VOID_BG, 0.18), 400: mix(anchor, VOID_BG, 0.36), 500: mix(anchor, VOID_BG, 0.52),
		600: mix(anchor, VOID_BG, 0.67)}


ORANGE, RED, PURPLE = ramp("#ffaa40"), ramp("#f43f5e"), ramp("#a78bfa")
VOIDN = {100: "#f4f4f8", 200: "#e0e0e0", 300: "#b4bfce", 400: "#8d97a8", 500: "#5a6273", 600: "#333847", 700: "#1f2230"}
INDIGO = {100: "#f1eee6", 200: "#e4e2ec", 300: "#b8b6c8", 400: "#8f8da6", 500: "#5f5d78", 600: "#3a384f", 700: "#2a2840", 800: "#1a1828"}
PAPER = {800: "#f2eff4", 900: "#fbfaf6"}
BRAND_GOLD, PALE = "#ffd08e", "#ffe7c4"
SKY1, SKY4, SKY7, HORIZON, TILE, DESKTOP = "#1f2554", "#42396c", "#7a4562", "#4a4580", "#0a1230", "#090e2a"
CREAM = "#d4d0c8"

# detail (flat) colours
LINE = INDIGO[400]  # text lines, tracks, ticks on light faces
DARK = INDIGO[800]  # terminal screens, slots, taskbars
GLYPH = PAPER[900]  # light glyphs on rose and violet badges
GLYPH_D = ORANGE[600]  # dark glyphs on gold badges


class Mat:
	"""A surface: base fill, lit tone (band and ramp top), the next ramp step (ramp foot) and the edge tone (darker, same hue)."""

	def __init__(self, name, base, lit, nxt, edge, token):
		self.name, self.base, self.lit, self.nxt, self.edge, self.token = name, base, lit, nxt, edge, token
		self.top = mix(base, lit, 0.3)
		self.bot = mix(base, nxt, 0.18)

	def px_edge(self):
		return mix(self.base, self.edge, 0.6)


MATS = {
	"gold": Mat("gold (back, body, badges, arrows)", ORANGE[200], ORANGE[100], ORANGE[300], ORANGE[500], "orange 200 · lit orange 100 · edge orange 500"),
	"goldl": Mat("gold light (front flap, lit gold faces)", BRAND_GOLD, PALE, ORANGE[200], ORANGE[500], "brand-gold · lit pale · edge orange 500"),
	"paper": Mat("paper (pages)", PAPER[800], PAPER[900], INDIGO[200], INDIGO[700], "paper 800 · lit paper 900 · edge indigo 700"),
	"fold": Mat("paper back (folds, rear pages)", INDIGO[200], INDIGO[100], INDIGO[300], INDIGO[700], "indigo 200 · lit indigo 100 · edge indigo 700"),
	"front": Mat("device front (bezels, lids, keys)", INDIGO[200], PAPER[900], INDIGO[300], INDIGO[700], "indigo 200 · lit paper 900 · edge indigo 700"),
	"back": Mat("device body (stands, bodies, rings)", VOIDN[300], VOIDN[100], VOIDN[400], VOIDN[700], "void 300 · lit void 100 · edge void 700"),
	"dusk": Mat("dusk (handles, dark bodies)", SKY4, HORIZON, SKY1, INDIGO[800], "sky 4 · lit horizon · edge indigo 800"),
	"rose": Mat("rose (error, delete, shut down)", RED[200], RED[100], RED[300], RED[500], "red 200 · lit red 100 · edge red 500"),
	"violet": Mat("violet (question, information, security, globes)", PURPLE[300], PURPLE[200], PURPLE[400], PURPLE[600], "purple 300 · lit purple 200 · edge purple 600"),
	"glass": Mat("glass (lens)", PALE, PAPER[900], BRAND_GOLD, ORANGE[500], "pale · lit paper 900 · edge orange 500"),
}
SKY = ("sky", SKY1, SKY7)  # the brand sky ramp for screens and the plate: a colour, not lighting, so it keeps its own two stops

# ---- the profile by size: edge weight, band, ramp and shadow ---------------------------------------------------------------------------------
PROFILE = {48: dict(edge=0.30, soft=True), 32: dict(edge=0.45, soft=True), 24: dict(edge=0.50, soft=True), 16: dict(edge=0.60, soft=False)}
SHADOW = {"body": 0.30, "tile": 0.30, "lift": 0.20, "flat": 0.0}

# ---- the keyline: set E's own inner edge, opaque and retuned in its own hue so the silhouette reaches 3:1 on cream and on dusk -------------------
# The classic cream window colour has a luminance of about 0.62 and the Dusk desktop about 0.006; an edge of about 0.137 reaches 3:1
# against both. The edge is drawn about 1.5 screen pixels wide, because at 32 px and below one pixel falls between pixels and blurs. Only
# the icons in KEYLINED ship with it, the ones ReactOS shows on light grounds: the drives and My Computer, the icons drawn on a page, the
# Explorer toolbar glyphs on the cream toolbar, and the light objects listed in white file windows. Every other icon's keyline variant is a
# review-only alternative in alternatives/.
KEY_LUMINANCE = 0.137
KEY_WIDTH = {48: 1.5, 32: 1.67, 24: 1.5, 16: 1.5}
KEYLINED_DRIVES = {"hdd", "floppy", "removable", "ramdisk", "mycomputer"}
KEYLINED_PAGES = {"doc", "text", "image", "library", "archive", "font", "rtf", "audio", "video", "batch", "regfile", "inifile", "html", "documents"}
KEYLINED_TOOLBAR = {"back", "forward", "up", "search", "folders", "move", "copy", "copyclip", "cut", "paste", "del", "undo", "views", "properties", "star",
	"mapdrive", "disconnect"}
KEYLINED_LIGHT = {"recycle", "recyclefull", "cd-disc", "floppy-disk", "usb-key", "monitor", "netdrive", "netdriveoff", "program"}
KEYLINED = KEYLINED_DRIVES | KEYLINED_PAGES | KEYLINED_TOOLBAR | KEYLINED_LIGHT
# Their hand-tuned 16 px frames take the keyline tone on their edge pixels only where the frame is below 3:1 on cream without it
KEYLINED_16 = {"removable", "views"} | KEYLINED_PAGES


def luminance_of(colour):
	return FG.lum(colour)


def retune(colour, target=KEY_LUMINANCE):
	"""The same hue and saturation at the lightness whose luminance is the target (KEY_LUMINANCE unless given)."""
	hue, lightness, saturation = colorsys.rgb_to_hls(*(int(colour[index:index + 2], 16) / 255 for index in (1, 3, 5)))
	low, high = 0.0, 1.0
	for _ in range(40):
		middle = (low + high) / 2
		value = "#%02x%02x%02x" % tuple(round(component * 255) for component in colorsys.hls_to_rgb(hue, middle, saturation))
		if luminance_of(value) < target:
			low = middle
		else:
			high = middle
	return "#%02x%02x%02x" % tuple(round(component * 255) for component in colorsys.hls_to_rgb(hue, high, saturation))


EDGE_STROKE = re.compile(r'stroke="(#[0-9a-f]{6})" stroke-width="([0-9.]+)" stroke-opacity="([0-9.]+)"')
UNDER_STROKE = re.compile(r'stroke="(#[0-9a-f]{6})" stroke-opacity="([0-9.]+)" stroke-width="([0-9.]+)"')


def keyline_strokes(body, size):
	"""The keyline laid on a drawing the Pen did not make (the M1 Folders glyph): every soft edge stroke made opaque, retuned and widened
	for the profile, as Pen.edge_paint draws it."""
	factor = KEY_WIDTH[size]
	unit = 48 / size if size < 48 else 1

	def edge(match):
		return 'stroke="%s" stroke-width="%s" stroke-opacity="1"' % (retune(match.group(1)), _n(float(match.group(2)) * factor))

	def under(match):
		widened = float(match.group(3)) + 2 * unit * (factor - 1)
		return 'stroke="%s" stroke-opacity="1" stroke-width="%s"' % (retune(match.group(1)), _n(widened))

	return UNDER_STROKE.sub(under, EDGE_STROKE.sub(edge, body))


# The Folders glyph's tree is a light core on a horizon line; too thin to carry an edge at 24 and 16 px, so with the keyline its core
# takes the keyline tone in its own hue (the horizon line around it already reaches 3:1 on cream, the core then does on Dusk)
TREE_CORE = 'stroke="%s" stroke-width="1.6" stroke-linecap="round"' % FG.TOK["text2"]


def keyline_tree(body):
	return body.replace(TREE_CORE, 'stroke="%s" stroke-width="1.6" stroke-linecap="round"' % retune(FG.TOK["text2"]))


def circ(cx, cy, r):
	return "M%s %s a%s %s 0 1 0 %s 0 a%s %s 0 1 0 %s 0 Z" % (_n(cx - r), _n(cy), _n(r), _n(r), _n(2 * r), _n(r), _n(r), _n(-2 * r))


def ellipse_d(cx, cy, rx, ry):
	return "M%s %s a%s %s 0 1 0 %s 0 a%s %s 0 1 0 %s 0 Z" % (_n(cx - rx), _n(cy), _n(rx), _n(ry), _n(2 * rx), _n(rx), _n(ry), _n(-2 * rx))


def ring(cx, cy, ro, ri):
	return circ(cx, cy, ro) + " " + circ(cx, cy, ri)


def RR(x, y, w, h, r=3):
	return rect_d(x, y, w, h, r)


def poly(pts, r=2):
	return rpoly([(p[0], p[1], p[2] if len(p) > 2 else r) for p in pts])


def rot(pts, a, cx=24, cy=24):
	c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
	return [(cx + (p[0] - cx) * c - (p[1] - cy) * s, cy + (p[0] - cx) * s + (p[1] - cy) * c) + tuple(p[2:]) for p in pts]


def page_d(x, y, w, h, f=10):
	return poly([(x, y, 3), (x + w - f, y, 0.8), (x + w, y + f, 0.8), (x + w, y + h, 3), (x, y + h, 3)])


def fold_d(x, y, w, f=10):
	return poly([(x + w - f, y, 0.5), (x + w - f, y + f - 1.5, 1.5), (x + w - 1.5, y + f, 0.5)], 0.5)


class Pen:
	"""Collects defs with ids unique to one icon and paints faces in the M1 language at one size profile."""

	def __init__(self, pre, size, keyline=False):
		self.pre, self.size, self.n = pre, size, 0
		self.u = 48 / size if size < 48 else 1  # one screen pixel in grid units
		p = PROFILE[size]
		self.op, self.soft = p["edge"], p["soft"]
		self.keyline = keyline  # every material edge drawn as the keyline (see KEYLINED)
		self.defs, self.clips, self.out = {}, {}, []

	def edge_paint(self, m, width):
		"""The edge tone, opacity and width of a material edge: set E's soft inner edge, or the keyline."""
		if self.keyline:
			return retune(m.edge), 1, width * KEY_WIDTH[self.size]
		return m.edge, self.op, width

	def id(self, k):
		self.n += 1
		return "%s-%s%d" % (self.pre, k, self.n)

	def clip(self, d):
		if d not in self.clips:
			cid = self.id("c")
			self.clips[d] = cid
			self.defs[cid] = '<clipPath id="%s"><path d="%s" clip-rule="evenodd"/></clipPath>' % (cid, d)
		return self.clips[d]

	def grad(self, top, bot):
		gid = "%s-g%s%s" % (self.pre, top[1:], bot[1:])
		self.defs[gid] = '<linearGradient id="%s" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (gid, top, bot)
		return "url(#%s)" % gid

	def blur(self, sd):
		fid = "%s-b%s" % (self.pre, str(sd).replace(".", "_"))
		self.defs[fid] = '<filter id="%s" x="-50%%" y="-50%%" width="200%%" height="200%%"><feGaussianBlur stdDeviation="%s"/></filter>' % (fid, sd)
		return "url(#%s)" % fid

	def face(self, d, m, band=True, grad=True, edge=True):
		"""One surface: ramp (or flat base at 16), lit band on the top and left, and a clipped inner edge, so the silhouette never grows."""
		u = self.u
		if m is SKY:
			paint, lit = self.grad(SKY1, SKY7), HORIZON
		else:
			paint = self.grad(m.top, m.bot) if grad and self.soft else m.base
			lit = m.lit
		if band and self.soft:
			cid = self.clip(d)
			s = '<path d="%s" fill="%s" fill-rule="evenodd"/><g clip-path="url(#%s)"><path d="%s" fill="%s" fill-rule="evenodd" transform="translate(%s %s)"/></g>' % (
				d, lit, cid, d, paint, _n(u), _n(u))
		else:
			s = '<path d="%s" fill="%s" fill-rule="evenodd"/>' % (d, paint)
		if edge and m is not SKY:
			cid = self.clip(d)
			edge_colour, opacity, width = self.edge_paint(m, 2 * u)
			s += '<g clip-path="url(#%s)"><path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-opacity="%s"/></g>' % (cid, d, edge_colour, _n(width), _n(opacity))
		self.out.append(s)

	def fill(self, d, colour):
		"""A flat detail: no ramp, band or edge."""
		self.out.append('<path d="%s" fill="%s" fill-rule="evenodd"/>' % (d, colour))

	def sky(self, d):
		self.out.append('<path d="%s" fill="%s"/>' % (d, self.grad(SKY1, SKY7)))

	def line(self, d, colour, w, m=None):
		"""A stroked mark. With a material its edge tone is laid underneath, one screen pixel wider at the profile's edge opacity."""
		if m is not None:
			edge_colour, opacity, width = self.edge_paint(m, 2 * self.u)
			self.out.append('<path d="%s" fill="none" stroke="%s" stroke-opacity="%s" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round"/>' % (
				d, edge_colour, _n(opacity), _n(w + width)))
		self.out.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s" stroke-linecap="round" stroke-linejoin="round"/>' % (d, colour, _n(w)))

	def shadow(self, x0, x1, y, op):
		if self.soft and op:
			self.out.append('<ellipse cx="%s" cy="%s" rx="%s" ry="1.5" fill="%s" opacity="%s" filter="%s"/>' % (
				_n((x0 + x1) / 2 + 1), _n(y + 0.4), _n((x1 - x0) * 0.43), TILE, op, self.blur(1)))

	def raw(self, s):
		self.out.append(s)


G = MATS


def plate(p):
	"""The softly raised dusk plate: M1's Folder Options plate (horizon lit band, sky ramp, contact shadow)."""
	d = RR(5, 5, 38, 38, 8)
	if p.soft:
		p.raw('<ellipse cx="25" cy="43.4" rx="16" ry="1.5" fill="%s" opacity="0.3" filter="%s"/>' % (TILE, p.blur(1)))
		cid = p.clip(d)
		p.raw('<path d="%s" fill="%s"/><g clip-path="url(#%s)"><path d="%s" fill="%s" transform="translate(%s %s)"/></g>' % (d, HORIZON, cid, d, p.grad(SKY1, SKY7), _n(p.u), _n(p.u)))
	else:
		p.raw('<path d="%s" fill="%s"/>' % (d, p.grad(SKY1, SKY7)))


# ---- shared drawings --------------------------------------------------------------------------------------------------------------------------
def monitor(p, x=6, y=6, w=36, h=27, stand=True):
	if stand:
		p.shadow(12, 36, 41.5, SHADOW["body"])
		p.face(RR(19.5, y + h - 2, 9, 7, 1.5), G["back"], band=False)
		p.face(RR(12, 37, 24, 4.5, 2.2), G["back"])
	p.face(RR(x, y, w, h, 3.5), G["front"])
	sx, sy, sw, sh = x + 4, y + 4, w - 8, h - 8
	p.sky(RR(sx, sy, sw, sh, 1.5))
	cx, by, r = sx + sw / 2, sy + sh, min(7, sh * 0.42)
	p.fill("M%s %s a%s %s 0 0 1 %s 0 Z" % (_n(cx - r), _n(by), _n(r), _n(r), _n(2 * r)), ORANGE[200])


def page(p, x=9, y=5, w=30, h=38, f=10, shadow=True):
	if shadow:
		p.shadow(x, x + w, y + h, SHADOW["body"])
	p.face(page_d(x, y, w, h, f), G["paper"])
	p.face(fold_d(x, y, w, f), G["fold"], band=False)


def bars(p, x, y, ws, gap=6, h=2.4, colour=LINE):
	for i, w in enumerate(ws):
		p.fill(RR(x, y + i * gap, w, h, h / 2), colour)


def globe(p, cx, cy, r, m="front", lines=INDIGO[400]):
	p.face(circ(cx, cy, r), G[m])
	lw = 1.6 if r > 11 else 1.4
	p.raw('<g clip-path="url(#%s)">' % p.clip(circ(cx, cy, r - 0.6)))
	p.raw('<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="none" stroke="%s" stroke-width="%s"/>' % (_n(cx), _n(cy), _n(r * 0.45), _n(r), lines, lw))
	p.raw('<path d="M%s %s H%s M%s %s H%s M%s %s H%s" fill="none" stroke="%s" stroke-width="%s"/>' % (
		_n(cx - r), _n(cy), _n(cx + r), _n(cx - r), _n(cy - r * 0.5), _n(cx + r), _n(cx - r), _n(cy + r * 0.5), _n(cx + r), lines, lw))
	p.raw("</g>")


def gear(p, cx, cy, ro, ri, hole, m="gold", n=8):
	p.face(FG.gear_d(cx, cy, ro, ri, n) + " " + circ(cx, cy, hole), G[m])


def bin_(p, full=False):
	p.shadow(13, 35, 42.5, SHADOW["body"])
	if full:
		p.face(poly([(13, 18), (15.5, 6), (26.5, 8), (24.5, 18)], 1.5), G["paper"])
		p.face(poly([(23.5, 17), (29, 7.5), (39, 12), (35, 19)], 1.5), G["goldl"])
	else:
		p.face(RR(18, 6, 12, 7, 2.5), G["front"], band=False)
	p.face(poly([(10.5, 17, 1), (37.5, 17, 1), (35, 42.5, 3), (13, 42.5, 3)]), G["back"])
	for x in (17.5, 22.5, 27.5):
		p.fill(RR(x, 22, 3, 16, 1.5), INDIGO[200])
	p.face(RR(7, 12, 34, 6.5, 2.5), G["front"])


def drive(p, y=13):
	p.face(RR(7, y, 34, 13, 3), G["back"])
	p.face(RR(5, y + 6, 38, 17, 3), G["front"])
	p.fill(RR(10, y + 14.5, 14, 2.6, 1.3), VOIDN[400])
	p.face(RR(32.5, y + 13.5, 6.5, 4.5, 1.6), G["gold"], band=False)


def arrow_small(p, y=37):
	p.face(poly([(17, y - 2, 1.2), (29, y - 2, 0.6), (29, y - 6.5, 1.2), (43, y, 1.8), (29, y + 6.5, 1.2), (29, y + 2, 0.6), (17, y + 2, 1.2)]), G["gold"])


def window(p, x, y, w, h, bar_m, bar_h=8):
	p.face(RR(x, y, w, h, 3), G["front"])
	p.face(poly([(x, y, 3), (x + w, y, 3), (x + w, y + bar_h, 0.01), (x, y + bar_h, 0.01)]), bar_m, band=False)


def keys(p, x0, y0, cols, rows, w=4.6, h=3.4, dx=6.5, dy=5.4, colour=INDIGO[200]):
	for j in range(rows):
		for i in range(cols):
			p.fill(RR(x0 + i * dx, y0 + j * dy, w, h, 1), colour)


# ---- the icons ----------------------------------------------------------------------------------------------------------------------------------
I = {}  # id -> (kind, tier, draw)  kind: "tile", "bare" or "m1" (the folder family from folders_g.py)
M1_NAME = {"folder": "folder", "folderopen": "folder-open", "mydocs": "documents", "network": "network", "folderopts": "folder-options", "folders": "folders-glyph",
	"mypictures": "pictures", "mymusic": "music", "myvideos": "videos", "desktop": "desktop"}


def icon(k, kind, tier):
	def reg(f):
		I[k] = (kind, tier, f)
		return f
	return reg


for _k in M1_NAME:
	I[_k] = ("m1", "lift" if _k == "folders" else "tile" if _k == "folderopts" else "body", None)

# Desktop and shell


@icon("mycomputer", "bare", "body")
def _(p):
	p.shadow(5, 43, 42, SHADOW["body"])
	p.face(RR(29, 9, 14, 33, 3), G["back"])
	for y in (14, 18.5):
		p.fill(RR(32, y, 8, 2.2, 1.1), VOIDN[400])
	p.face(RR(32.5, 34, 4.5, 3.2, 1.2), G["gold"], band=False)
	p.face(RR(13, 31, 7, 6, 1.4), G["back"], band=False)
	p.face(RR(7, 36, 19, 4.5, 2), G["back"])
	p.face(RR(4, 9, 25, 23, 3.2), G["front"])
	p.sky(RR(7.5, 12.5, 18, 16, 1.5))
	p.fill("M%s %s a5.5 5.5 0 0 1 11 0 Z" % (_n(11), _n(28.5)), ORANGE[200])


@icon("browser", "tile", "tile")
def _(p):
	globe(p, 24, 24, 13)
	p.line("M10 34 C18 42 34 33 40 14", ORANGE[200], 3, G["gold"])


@icon("recycle", "bare", "body")
def _(p):
	bin_(p)


@icon("recyclefull", "bare", "body")
def _(p):
	bin_(p, True)


@icon("appmanager", "tile", "tile")
def _(p):
	p.face(RR(11, 19, 26, 18, 2), G["back"])
	p.face(RR(9, 13, 30, 8, 2.2), G["front"])
	p.face(RR(21, 13, 6, 24, 1), G["gold"], band=False)


@icon("cmd", "tile", "tile")
def _(p):
	p.face(RR(9, 11, 30, 26, 3), G["front"])
	p.fill(RR(11.5, 16, 25, 18.5, 1.5), DARK)
	p.line("M15.5 21 L20.5 25 L15.5 29", ORANGE[200], 2.6)
	p.line("M24 29.5 H31", PAPER[900], 2.4)


@icon("readme", "tile", "tile")
def _(p):
	p.face("M24 15 C29 11 33 11 37.5 12 V35 C33 34 29 34 24 38 Z", G["fold"])
	p.face("M24 15 C19 11 15 11 10.5 12 V35 C15 34 19 34 24 38 Z", G["paper"])
	p.face(poly([(30, 11, 0.5), (36, 11, 0.5), (36, 24, 0.3), (33, 21, 0.3), (30, 24, 0.3)], 0.5), G["gold"], band=False)
	for y in (18, 23, 28):
		p.fill(RR(14.5, y, 6, 2, 1), LINE)


@icon("controlpanel", "tile", "tile")
def _(p):
	p.face(RR(10, 10, 28, 28, 3), G["front"])
	for x in (16, 23, 30):
		p.fill(RR(x, 14, 2, 20, 1), VOIDN[400])
	for x, y in ((13.5, 17.5), (20.5, 27), (27.5, 21)):
		p.face(RR(x, y, 7, 4.5, 1.6), G["gold"], band=False)


# Control Panel applets


@icon("access", "tile", "tile")
def _(p):
	p.face(circ(24, 13, 4.2), G["gold"], band=False)
	p.face(poly([(12.5, 19, 1.5), (35.5, 19, 1.5), (35.5, 23, 1.5), (27, 23, 0.8), (27, 29, 0.8), (31, 37, 1.2), (27, 37, 1), (24, 31, 0.8), (21, 37, 1),
		(17, 37, 1.2), (21, 29, 0.8), (21, 23, 0.8), (12.5, 23, 1.5)]), G["front"])


@icon("addhw", "tile", "tile")
def _(p):
	for v in (19, 24, 29):
		p.fill(RR(v - 1.1, 10.5, 2.2, 6, 1.1), VOIDN[300])
		p.fill(RR(v - 1.1, 31.5, 2.2, 6, 1.1), VOIDN[300])
		p.fill(RR(10.5, v - 1.1, 6, 2.2, 1.1), VOIDN[300])
		p.fill(RR(31.5, v - 1.1, 6, 2.2, 1.1), VOIDN[300])
	p.face(RR(14.5, 14.5, 19, 19, 3), G["front"])
	p.face(RR(19.5, 19.5, 9, 9, 1.6), G["gold"], band=False)


@icon("addremove", "tile", "tile")
def _(p):
	p.face(ring(21, 22, 11.5, 2.4), G["front"])
	p.fill(ring(21, 22, 5.2, 2.4), VOIDN[300])
	p.face(circ(33, 33, 7.5), G["gold"])
	p.fill(RR(29.5, 31.9, 7, 2.2, 1.1), GLYPH_D)
	p.fill(RR(31.9, 29.5, 2.2, 7, 1.1), GLYPH_D)


@icon("admintools", "tile", "tile")
def _(p):
	p.face(poly(rot([(22.6, 8.5), (25.4, 8.5), (25.4, 25), (22.6, 25)], 45), 1), G["back"], band=False)
	p.face(poly(rot([(19.8, 7, 1.5), (28.2, 7, 1.5), (26.2, 11, 0.6), (21.8, 11, 0.6)], 45)), G["back"], band=False)
	p.face(poly(rot([(20.5, 24), (27.5, 24), (27.5, 40.5), (20.5, 40.5)], 45), 3), G["gold"])


@icon("console", "tile", "tile")
def _(p):
	p.face(RR(10, 12, 28, 24, 3), G["front"])
	p.fill(RR(12.5, 17.5, 23, 16, 1.5), DARK)
	p.fill(RR(15, 21.5, 5, 9, 1), ORANGE[200])
	p.line("M24.5 23.5 H31.5 M24.5 28.5 H29.5", PAPER[900], 2)


@icon("datetime", "tile", "tile")
def _(p):
	p.face(RR(9, 10, 26, 26, 3), G["front"])
	p.face(poly([(9, 10, 3), (35, 10, 3), (35, 18, 0.01), (9, 18, 0.01)]), G["gold"], band=False)
	for j in range(2):
		for i in range(3):
			p.fill(RR(13 + i * 6.5, 22 + j * 5.5, 3.6, 3, 1), LINE)
	p.face(circ(34, 34, 8.5), G["paper"])
	p.line("M34 29.5 V34 H37.5", HORIZON, 1.8)


@icon("display", "tile", "tile")
def _(p):
	p.face(RR(20.5, 29.5, 7, 5, 1), G["back"], band=False)
	p.face(RR(14.5, 34, 19, 4, 1.6), G["back"])
	p.face(RR(9, 9, 30, 22, 3), G["front"])
	p.sky(RR(12, 12, 24, 16, 1.5))
	p.fill("M18.5 28 a5.5 5.5 0 0 1 11 0 Z", ORANGE[200])


@icon("fonts", "tile", "tile")
def _(p):
	p.face(poly([(13, 37, 1), (21.5, 11, 1.2), (26.5, 11, 1.2), (35, 37, 1), (29.5, 37, 0.8), (27.8, 31.5, 0.5), (20.2, 31.5, 0.5), (18.5, 37, 0.8)]), G["front"])
	p.fill(poly([(22.3, 25, 0.4), (25.7, 25, 0.4), (24, 19.5, 0.4)]), INDIGO[300])
	p.face(RR(19.5, 26.5, 9, 3.4, 1.2), G["gold"], band=False)


@icon("inetsettings", "tile", "tile")
def _(p):
	globe(p, 21, 21, 10.5)
	gear(p, 33, 33, 8.5, 6.4, 2.4)


@icon("keyboard", "tile", "tile")
def _(p):
	p.face(RR(8, 15, 32, 19, 3), G["back"])
	keys(p, 11.5, 18.5, 4, 2, 5, 3.4, 6.8, 5)
	p.face(RR(14, 28.5, 20, 3, 1.2), G["gold"], band=False)


@icon("mouse", "tile", "tile")
def _(p):
	p.face(RR(16, 9, 16, 30, 8), G["front"])
	p.face("M16 21 V17 a8 8 0 0 1 8 -8 V21 Z", G["gold"], band=False)
	p.fill(RR(16.6, 20.4, 14.8, 1.4, 0.7), LINE)
	p.fill(RR(23.4, 9.6, 1.4, 11, 0.7), LINE)


@icon("netconn", "tile", "tile")
def _(p):
	p.line("M24 22 V33 C24 37 28 38 32 38", ORANGE[200], 4, G["gold"])
	p.face(RR(15, 9, 18, 14, 3), G["front"])
	for x in (19.5, 27.5):
		p.fill(RR(x - 1, 13, 2, 6, 1), DARK)


@icon("power", "tile", "tile")
def _(p):
	p.face(circ(24, 24, 14), G["front"])
	p.face(poly([(26.5, 11, 0.6), (17, 26.5, 0.8), (23, 26.5, 0.4), (21.5, 37, 0.6), (31.5, 21, 0.8), (25.5, 21, 0.4)], 0.6), G["gold"], band=False)


@icon("printers", "tile", "tile")
def _(p):
	p.face(RR(16, 9, 16, 12, 1.5), G["paper"], band=False)
	p.face(RR(9, 18, 30, 15, 3), G["back"])
	p.face(RR(15, 28, 18, 11, 1.5), G["paper"])
	p.fill(RR(19, 33, 10, 1.8, 0.9), LINE)
	p.fill(RR(32, 21.5, 3.4, 3, 1), ORANGE[200])


@icon("regional", "tile", "tile")
def _(p):
	p.face(circ(24, 24, 13), G["violet"])
	cid = p.clip(circ(24, 24, 12.4))
	p.raw('<g clip-path="url(#%s)">' % cid)
	p.fill("M15 15 C20 12 23 16 21 19.5 C19 23 15 22 14 19 Z", ORANGE[200])
	p.fill("M27 22 C32 21 35 26 31 33 C27.5 31 26 26 27 22 Z", ORANGE[200])
	p.raw("</g>")


@icon("sound", "tile", "tile")
def _(p):
	p.face(poly([(10.5, 19.5, 1.5), (17, 19.5, 0.8), (25, 13, 1.2), (25, 35, 1.2), (17, 28.5, 0.8), (10.5, 28.5, 1.5)]), G["front"])
	p.line("M29.5 19.5 A6.5 6.5 0 0 1 29.5 28.5", ORANGE[200], 2.8, G["gold"])
	p.line("M33.5 15 A12.5 12.5 0 0 1 33.5 33", ORANGE[200], 2.8, G["gold"])


@icon("system", "tile", "tile")
def _(p):
	p.face(RR(14, 9, 20, 30, 3), G["front"])
	p.fill(RR(17, 13, 14, 3, 1), DARK)
	bars(p, 18, 20, [12, 12], 4.5, 1.8)
	p.face(circ(24, 32, 2.8), G["gold"], band=False)


@icon("taskbarstart", "tile", "tile")
def _(p):
	p.face(RR(9, 11, 30, 26, 3), G["front"])
	p.face(RR(12, 14.5, 12, 13, 1.5), G["back"], band=False)
	p.fill(poly([(9, 30, 0.01), (39, 30, 0.01), (39, 37, 3), (9, 37, 3)]), DARK)
	p.face(RR(11, 31.6, 9, 3.8, 1.3), G["gold"], band=False)


# Explorer toolbar


@icon("back", "bare", "lift")
def _(p):
	p.shadow(5, 43, 41, SHADOW["lift"])
	p.face(poly([(5, 25, 2), (21, 9, 1.8), (21, 17, 0.8), (43, 17, 2), (43, 33, 2), (21, 33, 0.8), (21, 41, 1.8)]), G["gold"])


@icon("forward", "bare", "lift")
def _(p):
	p.shadow(5, 43, 41, SHADOW["lift"])
	p.face(poly([(43, 25, 2), (27, 9, 1.8), (27, 17, 0.8), (5, 17, 2), (5, 33, 2), (27, 33, 0.8), (27, 41, 1.8)]), G["gold"])


@icon("up", "bare", "lift")
def _(p):
	p.shadow(6, 42, 43, SHADOW["lift"])
	p.face(poly([(24, 5, 2), (42, 21, 1.8), (32, 21, 0.8), (32, 33, 2), (16, 33, 2), (16, 21, 0.8), (6, 21, 1.8)]), G["gold"])
	p.face(RR(6, 38, 36, 5, 2), G["front"])


@icon("search", "bare", "lift")
def _(p):
	p.shadow(8, 43, 42.5, SHADOW["lift"])
	p.face(poly(rot([(20.5, 33), (27.5, 33), (27.5, 49), (20.5, 49)], -45, 20, 20), 3.2), G["dusk"])
	p.face(ring(20, 20, 14, 10), G["back"])
	p.face(circ(20, 20, 10), G["glass"], band=False)
	p.line("M14 19 A6.5 6.5 0 0 1 19 14", PAPER[900], 2)


@icon("move", "bare", "lift")
def _(p):
	p.shadow(5, 43, 43.5, SHADOW["lift"])
	p.face(RR(5, 5, 22, 24, 3), G["paper"])
	bars(p, 10, 11, [12, 12, 8], 5, 2)
	arrow_small(p)


@icon("copy", "bare", "lift")
def _(p):
	p.shadow(5, 43, 43.5, SHADOW["lift"])
	p.face(RR(15, 5, 22, 22, 3), G["fold"])
	p.face(RR(5, 11, 22, 18, 3), G["paper"])
	bars(p, 10, 16, [12, 12], 5, 2)
	arrow_small(p)


@icon("del", "bare", "flat")
def _(p):
	p.line("M13 13 L35 35 M35 13 L13 35", RED[200], 5, G["rose"])


@icon("undo", "bare", "flat")
def _(p):
	p.line("M17 21 H29 a9 9 0 0 1 0 18 H16", ORANGE[200], 5, G["gold"])
	p.face(poly([(5, 21, 1.5), (18, 10.5, 1.5), (18, 31.5, 1.5)]), G["gold"], band=False, grad=False)


@icon("views", "bare", "lift")
def _(p):
	p.shadow(5, 43, 41, SHADOW["lift"])
	for y in (7, 19, 31):
		p.face(RR(5, y, 38, 10, 3), G["front"])
		p.fill(RR(9, y + 3, 4, 4, 1), ORANGE[200])
		p.fill(RR(17, y + 4, 21, 2, 1), LINE)


# Drives and folders


@icon("hdd", "bare", "body")
def _(p):
	p.shadow(6, 42, 36, SHADOW["body"])
	drive(p)


@icon("cd", "bare", "body")
def _(p):
	# A slim 5.25 in optical drive seen from a little above: its faceplate (tray mouth, light and eject button) at the top, and its black
	# tray run out toward the viewer with a silver disc seated on it. The disc on the open tray is what says optical, not hard disk.
	p.shadow(6, 42, 42.5, SHADOW["body"])
	p.face(RR(8, 5, 32, 9, 3), G["back"])
	p.face(RR(5, 9, 38, 12, 3), G["front"])
	p.fill(RR(31, 12.2, 3.2, 2.2, 1), ORANGE[200])
	p.face(RR(35, 11.8, 5, 3, 1.1), G["back"], band=False)
	p.fill(RR(8, 16.5, 32, 3.4, 1.5), DARK)
	tray = poly([(9.5, 18, 1), (38.5, 18, 1), (43, 38, 2.5), (43, 42, 2.5), (5, 42, 2.5), (5, 38, 2.5)])
	p.face(tray, G["dusk"])
	p.fill(poly([(5.4, 38.2, 2), (42.6, 38.2, 2), (42.6, 41.6, 2.2), (5.4, 41.6, 2.2)], 1.5), mix(G["dusk"].base, G["dusk"].edge, 0.45))
	p.face(ellipse_d(24, 29, 15.5, 8.4), G["front"], band=False)
	p.fill(ellipse_d(24, 29, 5.2, 2.8), VOIDN[300])
	p.fill(ellipse_d(24, 29, 1.9, 1), SKY1)
	p.line("M11.6 26.4 C13.6 23.6 17.6 22 22 21.7", ORANGE[300], 1.8)
	p.line("M36.4 31.6 C34.4 34.4 30.4 36 26 36.3", INDIGO[300], 1.8)


@icon("floppy", "bare", "body")
def _(p):
	# A 3.5 in floppy drive seen from a little above: the narrow faceplate with its slot, light and eject button, and a floppy disk
	# going into the slot, shutter end first: the disk is in front of the faceplate and its leading edge is lost in the slot.
	p.shadow(6, 42, 42.5, SHADOW["body"])
	p.face(RR(7, 7, 34, 10, 3), G["back"])
	p.face(RR(5, 11, 38, 19, 3), G["front"])
	p.fill(RR(8, 16, 26, 4, 1.4), DARK)
	p.fill(RR(36, 15.6, 3.6, 2.2, 1), ORANGE[200])
	p.face(RR(35, 21.5, 5.5, 3.6, 1.2), G["back"], band=False)
	disk = poly([(10, 18, 0.6), (32, 18, 0.6), (35.5, 42, 2.5), (6.5, 42, 2.5)])
	p.face(disk, G["violet"])
	p.face(poly([(15, 18, 0.3), (26, 18, 0.3), (26.6, 25.5, 1.2), (14.3, 25.5, 1.2)]), G["back"], band=False)
	p.fill(poly([(21.6, 18.6, 0.4), (24.4, 18.6, 0.4), (24.6, 23.6, 0.6), (21.6, 23.6, 0.6)], 0.4), INDIGO[600])
	p.face(poly([(11.2, 30, 1.5), (30.3, 30, 1.5), (31.6, 42, 0.01), (9.9, 42, 0.01)]), G["paper"], band=False)
	p.fill(RR(13.4, 33.4, 15, 2, 1), LINE)
	p.fill(RR(13.2, 37.2, 10, 2, 1), LINE)
	p.fill(RR(8, 16, 26, 2.2, 1.1), DARK)


@icon("netdrive", "bare", "body")
def _(p):
	p.shadow(5, 43, 43, SHADOW["body"])
	p.line("M24 30 V35.5 M11 35.5 H37", VOIDN[300], 2.4, G["back"])
	drive(p, 7)
	p.face(RR(5, 38.5, 12, 4.5, 1.6), G["gold"], band=False)
	p.face(RR(31, 38.5, 12, 4.5, 1.6), G["gold"], band=False)
	p.face(RR(20, 33.5, 8, 4.5, 1.6), G["back"], band=False)


# File types


@icon("doc", "bare", "body")
def _(p):
	page(p)
	p.face(RR(14, 14, 11, 4.5, 1.5), G["gold"], band=False)
	bars(p, 14, 23, [19, 19, 11])


@icon("text", "bare", "body")
def _(p):
	page(p)
	bars(p, 14, 17, [19, 19, 19, 19, 11], 5)


@icon("image", "bare", "body")
def _(p):
	page(p)
	p.sky(RR(13, 17, 22, 20, 1.5))
	cid = p.clip(RR(13, 17, 22, 20, 1.5))
	p.raw('<g clip-path="url(#%s)">' % cid)
	p.fill("M13 37 L20.5 27.5 L26 33 L30 29 L35 35 V37 Z", HORIZON)
	p.raw("</g>")
	p.face(circ(29, 23, 3), G["gold"], band=False)


@icon("program", "bare", "body")
def _(p):
	p.shadow(5, 43, 39, SHADOW["body"])
	window(p, 5, 9, 38, 30, G["gold"])
	p.line("M14.5 24 L20 28 L14.5 32", HORIZON, 2.4)
	p.line("M24.5 32.5 H32.5", LINE, 2.4)


@icon("library", "bare", "body")
def _(p):
	page(p)
	bars(p, 14, 14, [12], 5)
	gear(p, 25, 30.5, 8.5, 6.4, 2.4)


@icon("archive", "bare", "body")
def _(p):
	page(p)
	for i in range(6):
		p.fill(RR(20 + (i % 2) * 4, 7 + i * 4, 4, 4, 0.6), ORANGE[200] if i % 2 else INDIGO[400])
	p.face(RR(19.5, 31, 9, 8, 2), G["goldl"], band=False)
	p.fill(RR(22, 34, 4, 2.2, 1), ORANGE[400])


@icon("font", "bare", "body")
def _(p):
	page(p)
	p.line("M17.5 36 L24 17 L30.5 36", HORIZON, 3)
	p.fill(RR(19.5, 28, 9, 3, 1), ORANGE[200])


@icon("rtf", "bare", "body")
def _(p):
	page(p)
	p.face(RR(14, 13, 15, 5, 1.5), G["gold"], band=False)
	bars(p, 14, 22, [19, 13, 19], 5)
	p.fill(RR(14, 37, 12, 2.4, 1.2), ORANGE[200])


# Dialogs


@icon("question", "bare", "lift")
def _(p):
	p.shadow(9, 41, 43, SHADOW["lift"])
	p.face(poly([(5, 5, 4), (43, 5, 4), (43, 33, 4), (28, 33, 0.8), (17, 43, 0.8), (17, 33, 0.8), (5, 33, 4)]), G["violet"])
	p.line("M19 15 a5 5 0 1 1 8 4 c-2 1.5 -3 2.5 -3 5", GLYPH, 4)
	p.fill(circ(24, 28.5, 2.5), GLYPH)


@icon("warning", "bare", "lift")
def _(p):
	p.shadow(5, 43, 41, SHADOW["lift"])
	p.face(poly([(24, 4, 3.5), (44, 40.5, 3.5), (4, 40.5, 3.5)]), G["gold"])
	p.fill(RR(22, 15, 4, 14, 2), GLYPH_D)
	p.fill(circ(24, 34.2, 2.4), GLYPH_D)


@icon("error", "bare", "lift")
def _(p):
	p.shadow(6, 42, 43, SHADOW["lift"])
	p.face(poly([(17, 5), (31, 5), (43, 17), (43, 31), (31, 43), (17, 43), (5, 31), (5, 17)], 3), G["rose"])
	p.line("M17.5 17.5 L30.5 30.5 M30.5 17.5 L17.5 30.5", GLYPH, 4.5)


@icon("info", "bare", "lift")
def _(p):
	p.shadow(6, 42, 43, SHADOW["lift"])
	p.face(circ(24, 24, 19), G["violet"])
	p.fill(RR(22, 21, 4, 13, 2), GLYPH)
	p.fill(circ(24, 15.2, 2.6), GLYPH)


@icon("shield", "bare", "lift")
def _(p):
	p.shadow(14, 34, 43, SHADOW["lift"])
	p.face("M24 5 L37.5 10 Q39 10.6 39 12.2 V23 C39 33 32 39 24 43 C16 39 9 33 9 23 V12.2 Q9 10.6 10.5 10 Z", G["violet"])
	p.line("M20 23 V20 a4 4 0 0 1 8 0 V23", GLYPH, 2.6)
	p.face(RR(17.5, 23, 13, 10, 2), G["gold"], band=False)
	p.fill(RR(23, 26, 2, 4, 1), GLYPH_D)


# System tray


@icon("volume", "bare", "lift")
def _(p):
	p.shadow(5, 23, 39, SHADOW["lift"])
	p.face(poly([(5, 18.5, 2), (13, 18.5, 0.8), (23, 10, 1.5), (23, 38, 1.5), (13, 29.5, 0.8), (5, 29.5, 2)]), G["front"])
	p.line("M29 18 A8 8 0 0 1 29 30", ORANGE[200], 3, G["gold"])
	p.line("M35 12 A15 15 0 0 1 35 36", ORANGE[200], 3, G["gold"])


@icon("trynet", "bare", "body")
def _(p):
	p.shadow(7, 41, 42.5, SHADOW["body"])
	p.face(RR(15, 6, 26, 18, 3), G["back"])
	p.face(RR(17, 35, 6, 4, 1), G["back"], band=False)
	p.face(RR(12, 38, 16, 4.5, 1.8), G["back"])
	p.face(RR(7, 18, 26, 18, 3), G["front"])
	p.sky(RR(10, 21, 20, 12, 1.5))
	p.fill("M16 33 a4 4 0 0 1 8 0 Z", ORANGE[200])


@icon("kbdlayout", "bare", "body")
def _(p):
	p.shadow(5, 43, 35, SHADOW["body"])
	p.face(RR(5, 13, 38, 22, 3), G["back"])
	keys(p, 8.5, 16.5, 5, 2, 5, 3.4, 6.6, 5)
	p.face(RR(13, 27, 22, 3.4, 1.3), G["gold"], band=False)


@icon("clock", "bare", "body")
def _(p):
	p.shadow(6, 42, 43, SHADOW["body"])
	p.face(circ(24, 24, 19), G["front"])
	for d in ("M24 8.5 V11.5", "M39.5 24 H36.5", "M24 39.5 V36.5", "M8.5 24 H11.5"):
		p.line(d, LINE, 2)
	p.line("M24 13 V24 H32.5", HORIZON, 2.6)
	p.face(circ(24, 24, 3), G["gold"], band=False)


@icon("showdesk", "bare", "body")
def _(p):
	p.shadow(5, 43, 39, SHADOW["body"])
	p.face(RR(5, 9, 38, 30, 3), SKY)
	p.fill("M13 30 a7 7 0 0 1 14 0 Z", ORANGE[200])
	p.fill(poly([(5, 31, 0.01), (43, 31, 0.01), (43, 39, 3), (5, 39, 3)]), DARK)
	p.face(RR(32.5, 32.5, 8, 5, 1.5), G["gold"], band=False)
	p.raw('<g clip-path="url(#%s)"><path d="%s" fill="none" stroke="%s" stroke-width="%s"/></g>' % (p.clip(RR(5, 9, 38, 30, 3)), RR(5, 9, 38, 30, 3), HORIZON, _n(2 * p.u)))


# Start menu


@icon("programs", "bare", "body")
def _(p):
	p.shadow(5, 43, 43, SHADOW["body"])
	for x, y, m in ((5, 5, "front"), (26, 5, "gold"), (5, 26, "front"), (26, 26, "front")):
		p.face(RR(x, y, 17, 17, 3.5), G[m])


@icon("documents", "bare", "body")
def _(p):
	p.shadow(9, 39, 43, SHADOW["body"])
	p.face(RR(15, 5, 24, 30, 3), G["fold"])
	page(p, 9, 11, 24, 32, 8, shadow=False)
	p.face(RR(13.5, 18, 8, 3.5, 1.2), G["gold"], band=False)
	bars(p, 13.5, 25, [14, 14, 8], 5, 2.2)


@icon("settings", "bare", "lift")
def _(p):
	p.shadow(6, 42, 43, SHADOW["lift"])
	gear(p, 24, 24, 19, 14.5, 5.2)


@icon("help", "bare", "lift")
def _(p):
	p.shadow(6, 42, 43, SHADOW["lift"])
	p.face(circ(24, 24, 19), G["gold"])
	p.line("M19 18 a5 5 0 1 1 8 4 c-2 1.5 -3 2.5 -3 5", GLYPH_D, 4)
	p.fill(circ(24, 33, 2.5), GLYPH_D)


@icon("run", "bare", "body")
def _(p):
	p.shadow(5, 43, 39, SHADOW["body"])
	window(p, 5, 9, 38, 30, G["dusk"])
	p.face(poly([(19, 22.5, 1.5), (33, 29, 1.5), (19, 35.5, 1.5)]), G["gold"], band=False)


@icon("shutdown", "bare", "flat")
def _(p):
	p.line("M15 14 a14 14 0 1 0 18 0", RED[200], 5, G["rose"])
	p.line("M24 6 V22", RED[200], 5, G["rose"])


# ---- build: (defs, body) for an icon at a profile -----------------------------------------------------------------------------------------------
def build(k, size, pre=None):
	pre = pre or "e-%s-%d" % (k, size)
	kind, tier, f = I[k]
	if kind == "m1":
		defs, body = FG.icon(M1, M1_NAME[k], size, pre)
		return defs, keyline_tree(keyline_strokes(body, size)) if k in KEYLINED else body
	if kind == "built":
		return f(size, pre)
	p = Pen(pre, size, k in KEYLINED)
	if kind == "tile":
		plate(p)
	f(p)
	return "".join(p.defs.values()), "".join(p.out)


# ---- hinted 16 px: pixel layers, each edged where it meets anything outside itself --------------------------------------------------------------
# Lowercase letters are materials (fill, or their 16 px edge tone on the layer's boundary); digits and other marks are flat detail colours.
PXM = {"g": G["gold"], "f": G["goldl"], "p": G["paper"], "q": G["fold"], "m": G["front"], "n": G["back"], "d": G["dusk"], "r": G["rose"], "v": G["violet"],
	"a": G["glass"]}
PXD = {"1": INDIGO[400], "2": ORANGE[200], "3": ORANGE[600], "4": PAPER[900], "5": SKY1, "6": SKY4, "7": SKY7, "8": DARK, "9": VOIDN[400], "0": INDIGO[200], "e": G["back"].px_edge()}


def px_layers(layers, keyline=False):
	"""The rects of a hinted frame; with the keyline, every edged material pixel takes the keyline tone of its 16 px edge."""
	px = {}
	for rows, edged in layers:
		cells = {(x, y): ch for y, row in enumerate(rows) for x, ch in enumerate(row) if ch != "."}
		for (x, y), ch in cells.items():
			if ch in PXM:
				m = PXM[ch]
				out = any((x + dx, y + dy) not in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
				if edged and out:
					px[(x, y)] = retune(m.px_edge()) if keyline else m.px_edge()
				else:
					px[(x, y)] = m.base
			else:
				px[(x, y)] = PXD[ch]
	return "".join('<rect x="%d" y="%d" width="1" height="1" fill="%s"/>' % (x, y, c) for (x, y), c in sorted(px.items(), key=lambda q: (q[0][1], q[0][0])))


def grid(f):
	"""16 rows from a function (x, y) -> char."""
	return ["".join(f(x, y) for x in range(16)) for y in range(16)]


def put(rows, pts, ch):
	rows = [list(r) for r in rows]
	for x, y in pts:
		rows[y][x] = ch
	return ["".join(r) for r in rows]


BLANK = ["." * 16] * 16

H16 = {}


def page16(x0=3, x1=12, y0=1, y1=14, f=3):
	"""A page with a dog-ear: the page layer and the fold layer."""
	pg = grid(lambda x, y: "p" if x0 <= x <= x1 and y0 <= y <= y1 and not (y - y0 < f and x > x1 - f + (y - y0)) else ".")
	fo = grid(lambda x, y: "q" if y0 <= y < y0 + f and x1 - f + 1 <= x <= x1 - f + 1 + (y - y0) else ".")
	return [(pg, True), (fo, True)]


def detail(spec):
	"""spec: list of (x, y, w, ch) horizontal runs."""
	rows = [list("." * 16) for _ in range(16)]
	for x, y, w, ch in spec:
		for i in range(w):
			rows[y][x + i] = ch
	return (["".join(r) for r in rows], False)


H16["doc"] = page16() + [detail([(5, 5, 4, "2"), (5, 7, 6, "1"), (5, 9, 6, "1"), (5, 11, 4, "1")])]
H16["documents"] = [
	(grid(lambda x, y: "q" if 6 <= x <= 13 and 1 <= y <= 10 else "."), True)] + page16(2, 10, 4, 14, 3) + [detail([(4, 7, 3, "2"), (4, 9, 5, "1"), (4, 11, 5, "1")])]


def octagon(x, y):
	cx = abs(x - 7.5)
	cy = abs(y - 7.5)
	return cx <= 6.5 and cy <= 6.5 and cx + cy <= 10.5


X16 = {4: (4, 5, 10, 11), 5: (5, 6, 9, 10), 6: (6, 7, 8, 9), 7: (7, 8), 8: (7, 8), 9: (6, 7, 8, 9), 10: (5, 6, 9, 10), 11: (4, 5, 10, 11)}
H16["error"] = [(grid(lambda x, y: "r" if octagon(x, y) else "."), True), (grid(lambda x, y: "4" if x in X16.get(y, ()) else "."), False)]


def tri(x, y):
	if not 1 <= y <= 14:
		return False
	half = (y - 1) * 7.0 / 13 + 0.6
	return abs(x - 7.5) <= half


H16["warning"] = [(grid(lambda x, y: "g" if tri(x, y) else "."), True), detail([(7, 5, 2, "3"), (7, 6, 2, "3"), (7, 7, 2, "3"), (7, 8, 2, "3"), (7, 9, 2, "3"), (7, 11, 2, "3"), (7, 12, 2, "3")])]


LENS = ["..eeeee..", ".ennnnne.", "enaa4aane", "ena4aaane", "enaaaaane", "enaaaaane", "enaaaaane", ".ennnnne.", "..eeeee.."]
H16["search"] = [
	(put(BLANK, [(x, y) for x in range(8, 15) for y in range(8, 15) if abs(x - y) <= 1 and x + y >= 18], "d"), True),
	(["." * 16] + ["." + r + "." * 6 for r in LENS] + ["." * 16] * 6, False)]
H16["hdd"] = [(grid(lambda x, y: "n" if 2 <= x <= 13 and 3 <= y <= 7 else "."), True), (grid(lambda x, y: "m" if 1 <= x <= 14 and 5 <= y <= 12 else "."), True),
	detail([(3, 9, 5, "9"), (11, 8, 2, "2"), (11, 9, 2, "2")])]
H16["monitor"] = [
	(grid(lambda x, y: "n" if (6 <= x <= 9 and y == 11) or (4 <= x <= 11 and 12 <= y <= 13) else "."), True),
	(grid(lambda x, y: "m" if 1 <= x <= 14 and 1 <= y <= 11 else "."), True),
	(grid(lambda x, y: ("5" if y <= 4 else "6" if y <= 6 else "7") if 3 <= x <= 12 and 3 <= y <= 8 else "."), False),
	detail([(7, 7, 2, "2"), (6, 8, 4, "2")])]


def bin16(full):
	body = grid(lambda x, y: "n" if 5 <= y <= 14 and (3 + (1 if y >= 10 else 0)) <= x <= (12 - (1 if y >= 10 else 0)) else ".")
	lid = grid(lambda x, y: "m" if 2 <= x <= 13 and 3 <= y <= 4 else ".")
	ribs = detail([(6, y, 1, "0") for y in range(7, 13)] + [(9, y, 1, "0") for y in range(7, 13)])
	if full:
		top = [(grid(lambda x, y: "p" if (y == 0 and 3 <= x <= 5) or (y == 1 and 3 <= x <= 6) or (y == 2 and 4 <= x <= 6) else "."), True),
			(grid(lambda x, y: "f" if (y == 0 and 10 <= x <= 11) or (y == 1 and 9 <= x <= 12) or (y == 2 and 8 <= x <= 12) else "."), True)]
	else:
		top = [(grid(lambda x, y: "m" if (y == 1 and 6 <= x <= 9) or (y == 2 and 6 <= x <= 9) else "."), True)]
	return top + [(body, True), ribs, (lid, True)]


H16["recycle"] = bin16(False)
H16["recyclefull"] = bin16(True)
M1_H16 = {"folder": ("closed", None), "folderopen": ("open", None), "mydocs": ("closed", "documents"), "network": ("closed", "network"),
	"mypictures": ("closed", "pictures"), "mymusic": ("closed", "music"), "myvideos": ("closed", "videos"), "desktop": ("closed", "desktop")}


def hinted(k):
	if k in V16.ART:
		return V16.pixels(k, k in KEYLINED_16)
	if k in M1_H16:
		st, em = M1_H16[k]
		return FG.hint16(M1, st, em)
	return px_layers(H16[k], k in KEYLINED_16)


HINTED = ["folder", "folderopen", "mydocs", "mypictures", "mymusic", "myvideos", "desktop", "network", "doc", "documents", "warning", "error", "search", "hdd", "mycomputer", "monitor", "recycle", "recyclefull"]

# ---- inventory and groups (set D's) ----------------------------------------------------------------------------------------------------------
GROUPS = [
	("Desktop and shell", [("mycomputer", "My Computer"), ("mydocs", "My Documents"), ("network", "My Network Places"), ("browser", "Internet Browser"),
		("recycle", "Recycle Bin (empty)"), ("recyclefull", "Recycle Bin (full)"), ("appmanager", "Applications Manager"), ("cmd", "Command Prompt"),
		("readme", "Read Me"), ("controlpanel", "Control Panel")]),
	("Control Panel applets", [("access", "Accessibility"), ("addhw", "Add Hardware"), ("addremove", "Add/Remove Programs"), ("admintools", "Administrative Tools"),
		("console", "Console"), ("datetime", "Date/Time"), ("display", "Display"), ("folderopts", "Folder Options"), ("fonts", "Fonts"),
		("inetsettings", "Internet Settings"), ("keyboard", "Keyboard"), ("mouse", "Mouse"), ("netconn", "Network Connections"), ("power", "Power Options"),
		("printers", "Printers"), ("regional", "Regional Options"), ("sound", "Sound and Audio"), ("system", "System"), ("taskbarstart", "Taskbar and Start Menu")]),
	("Explorer toolbar", [("back", "Back"), ("forward", "Forward"), ("up", "Up"), ("search", "Search"), ("folders", "Folders"), ("move", "Move to"),
		("copy", "Copy to"), ("del", "Delete"), ("undo", "Undo"), ("views", "Views")]),
	("Drives and folders", [("hdd", "Hard disk"), ("cd", "CD drive"), ("floppy", "Floppy"), ("netdrive", "Network drive"), ("folder", "Folder"),
		("folderopen", "Folder (open)"), ("mydocs", "My Documents"), ("mypictures", "My Pictures"), ("mymusic", "My Music"), ("myvideos", "My Videos"),
		("desktop", "Desktop"), ("network", "My Network Places"), ("mycomputer", "My Computer")]),
	("File types", [("doc", "Document"), ("text", "Text"), ("image", "Image"), ("program", "Program"), ("library", "Library (DLL)"), ("archive", "Archive"),
		("font", "Font"), ("rtf", "Rich text (.RTF)")]),
	("Dialogs", [("question", "Question"), ("warning", "Warning"), ("error", "Error"), ("info", "Information"), ("shield", "Security")]),
	("System tray", [("volume", "Volume"), ("trynet", "Network"), ("kbdlayout", "Keyboard layout"), ("clock", "Clock"), ("showdesk", "Show desktop")]),
	("Start menu", [("programs", "Programs"), ("documents", "Documents"), ("settings", "Settings"), ("search", "Search"), ("help", "Help"), ("run", "Run"),
		("shutdown", "Shut Down")]),
]


def load_module(name):
	spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


V2 = load_module("gen_v2")
V2.register(types.SimpleNamespace(**globals()))
V3 = load_module("gen_v3")  # the dialog pictures added in v3
V3.register(types.SimpleNamespace(**globals()))
V16 = load_module("hint16_v2")  # the hand-tuned 16 px frames
V16.register(types.SimpleNamespace(**globals()))
V4 = load_module("gen_v4")  # the art the full image still showed in stock, with its own hand-tuned 16 px frames
V4.register(types.SimpleNamespace(**globals()))
V5 = load_module("gen_v5")  # the namespace folders, registry values, Go button and dialog pictures the first screens still showed in stock
V5.register(types.SimpleNamespace(**globals()))
# the Explorer toolbar glyphs, which also get a 24 px profile for browseui's 24 px strips, and the Go button, whose 20 px bitmap is drawn from it
TOOLBAR_24 = V2.TOOLBAR_24 + V5.TOOLBAR_24
LABEL = {k: l for _, items in GROUPS for k, l in items}

HEAD = """<!--
Afterglow icons, variant E (the M1 folder language for every icon): %s

(c) Copyright 2026 Liminal HQ, Scott Morris
SPDX-License-Identifier: Apache-2.0 OR MIT
-->
"""


def standalone(body, defs, vb, title, crisp=False):
	sr = ' shape-rendering="crispEdges"' if crisp else ""
	return (HEAD % title + '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d"%s>\n<defs>%s</defs>\n%s\n</svg>\n'
		% (vb, vb, vb, vb, sr, defs, body))


def write_icons(out):
	for sub in ("icons", "icons/32", "icons/24", "icons/16"):
		os.makedirs(os.path.join(out, sub), exist_ok=True)
	n = 0
	for k in I:
		for size, path in ((48, "icons/%s.svg"), (32, "icons/32/%s.svg"), (16, "icons/16/%s.svg")):
			d, b = build(k, size)
			open(os.path.join(out, path % k), "w").write(standalone(b, d, 48, "%s, %s (%s profile)" % (k, LABEL[k], "48 master" if size == 48 else "%d px" % size)))
			n += 1
		if k in TOOLBAR_24:
			d, b = build(k, 24)
			open(os.path.join(out, "icons/24/%s.svg" % k), "w").write(standalone(b, d, 48, "%s, %s (24 px profile)" % (k, LABEL[k])))
			n += 1
	for k in HINTED:
		open(os.path.join(out, "icons/%s-16.svg" % k), "w").write(standalone(hinted(k), "", 16, "%s, %s (hinted 16 px)" % (k, LABEL[k]), True))
		n += 1
	return n


# ---- the sheet ----------------------------------------------------------------------------------------------------------------------------------
BG, CELL, LAB, HD, SUB, DIM = "#0c0c10", "#14161d", "#e0e0e0", "#ffd08e", "#b4bfce", "#7c8796"
FONT = "'DejaVu Sans', sans-serif"
txt = FG.txt


class Syms:
	def __init__(self):
		self.defs, self.syms, self.have = [], [], set()

	def get(self, k, size):
		sid = "%s-%s" % (k, size)
		if sid not in self.have:
			self.have.add(sid)
			if size == "h16":
				self.syms.append('<symbol id="%s" viewBox="0 0 16 16" overflow="visible" shape-rendering="crispEdges">%s</symbol>' % (sid, hinted(k)))
			else:
				d, b = build(k, size, "s-%s-%d" % (k, size))
				self.defs.append(d)
				self.syms.append('<symbol id="%s" viewBox="0 0 48 48" overflow="visible">%s</symbol>' % (sid, b))
		return sid

	def best16(self, k):
		return self.get(k, "h16") if k in HINTED else self.get(k, 16)


def use(sid, x, y, size, extra=""):
	return '<use href="#%s" x="%s" y="%s" width="%s" height="%s"%s/>' % (sid, _n(x), _n(y), size, size, extra)


def write_sheet(syms):
	W = 1712
	out = []
	y = 40
	out.append(txt(40, y + 14, "Afterglow icons · variant E, the M1 folder language for every icon", 30, "#ffffff", weight=600))
	y += 36
	for line in [
		"Every icon drawn the way the chosen M1 folder is drawn: a flat two-tone base from Afterglow tokens (a deeper tone behind, a lighter lit tone in front), a very gentle",
		"top-to-bottom ramp, a 1 px lit band on the top and left, a thin inner edge in a darker tone of the same hue at 30 %, a soft contact shadow and generous radii. No navy ink line,",
		"no extrusion. Symbols and toolbar glyphs only lift; Delete, Undo and Shut Down stay flat. Apps and applets sit on M1's softly raised dusk plate. Sizes are 48, 32 and 16, plus 24 for toolbar glyphs.",
	]:
		y += 20
		out.append(txt(40, y, line, 13, SUB))
	y += 28

	# construction: keylines at 2x and the material table
	out.append(txt(40, y + 14, "Construction · keylines at 2×, the 4 px live area, and the bottom-left shortcut corner (16 × 16) kept clear", 15, HD, weight=600))
	y += 22
	kx = 40
	for k, label, kl in [("doc", "Portrait 32 × 40", '<rect x="16" y="8" width="64" height="80"'), ("cd", "Circle 40 · lift", '<circle cx="48" cy="48" r="40"'),
			("folder", "M1 folder 40 × 32", '<rect x="8" y="16" width="80" height="64"'), ("floppy", "Square 36", '<rect x="12" y="12" width="72" height="72"'),
			("warning", "Badge · lift", '<rect x="8" y="8" width="80" height="80"'), ("browser", "Plate 38, radius 8", '<rect x="10" y="10" width="76" height="76" rx="16"')]:
		out.append('<rect x="%s" y="%s" width="104" height="124" rx="6" fill="%s"/>' % (kx, y, CELL))
		g = "".join('<path d="M%s 0 V96 M0 %s H96" stroke="#262a37" stroke-width="0.5" fill="none"/>' % (i * 2, i * 2) for i in range(0, 49, 4))
		g += '<rect x="0" y="64" width="32" height="32" fill="#f43f5e" opacity="0.12"/>'
		out.append('<g transform="translate(%s %s)"><rect width="96" height="96" fill="%s"/>%s%s%s fill="none" stroke="#f43f5e" stroke-width="1" stroke-dasharray="4 3"/></g>' % (
			kx + 4, y + 4, DESKTOP, g, use(syms.get(k, 48), 0, 0, 96), kl))
		out.append(txt(kx + 52, y + 116, label, 11, SUB, "middle"))
		kx += 116
	px = 40 + 6 * 116 + 12
	out.append(txt(px, y + 12, "Materials · ramp top, base, ramp foot, lit band, edge (drawn at 30 %), 16 px edge", 13, HD, weight=600))
	for i, (key, m) in enumerate(MATS.items()):
		sx, sy = px + (i % 2) * 470, y + 22 + (i // 2) * 21
		for j, c in enumerate([m.top, m.base, m.bot, m.lit, m.edge, m.px_edge()]):
			out.append('<rect x="%s" y="%s" width="16" height="17" fill="%s" stroke="#33384a" stroke-width="1"/>' % (sx + j * 16, sy, c))
		out.append(txt(sx + 102, sy + 12, "%s · %s" % (key, m.token), 10, LAB))
	y += 140

	# proof strip: key icons at 48, 32 and 16 on void, cream and dusk
	keys = ["folder", "mydocs", "doc", "documents", "mycomputer", "hdd", "recycle", "recyclefull", "search", "warning", "error", "info", "browser", "controlpanel",
		"settings", "volume", "shutdown"]
	PW = 92
	out.append(txt(40, y + 14, "Proof strip · 48, 32 and 16 (the hinted redraw where one is drawn, otherwise the 16 profile) on void, cream and dusk", 15, HD, weight=600))
	y += 24
	out.append('<linearGradient id="duskbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (SKY1, SKY4))
	for name, fill, nc in (("void", "#060609", DIM), ("cream", CREAM, "#5a5560"), ("dusk", "url(#duskbg)", SUB)):
		out.append('<rect x="40" y="%d" width="%d" height="72" rx="6" fill="%s"/>' % (y, W - 80, fill))
		out.append(txt(W - 50, y + 66, name, 10, nc, "end"))
		for i, k in enumerate(keys):
			x = 52 + i * PW
			out.append(use(syms.get(k, 48), x, y + 12, 48) + use(syms.get(k, 32), x + 52, y + 8, 32) + use(syms.best16(k), x + 60, y + 46, 16))
		y += 78
	y += 6

	# hinted 16
	out.append(txt(40, y + 14, "Hinted 16 px redraws · 1 px edge at about 60 % baked to a solid tone, no ramp, no shadow · at 1× on void, cream and dusk, and at 4×", 15, HD, weight=600))
	y += 24
	per_row = (W - 104) // 94  # the hinted redraws wrap onto as many rows as they need
	for start in range(0, len(HINTED), per_row):
		out.append('<rect x="40" y="%d" width="%d" height="112" rx="6" fill="%s"/>' % (y, W - 80, CELL))
		for i, k in enumerate(HINTED[start:start + per_row]):
			x = 52 + i * 94
			for j, bg in enumerate(("#060609", CREAM, SKY4)):
				out.append('<rect x="%d" y="%d" width="24" height="24" fill="%s"/>' % (x, y + 10 + j * 28, bg) + use(syms.get(k, "h16"), x + 4, y + 14 + j * 28, 16))
			out.append('<rect x="%d" y="%d" width="72" height="72" fill="%s"/>' % (x + 30, y + 10, CREAM) + use(syms.get(k, "h16"), x + 34, y + 14, 64))
			out.append(txt(x + 66, y + 104, LABEL[k], 10, SUB, "middle"))
		y += 112 + 6
	y += 16

	# groups
	CW, CH, GAP = 200, 88, 4
	for gname, items in GROUPS:
		out.append(txt(40, y + 14, "%s · %d" % (gname, len(items)), 15, HD, weight=600))
		y += 24
		rows = (len(items) + 7) // 8
		for i, (k, label) in enumerate(items):
			cx = 40 + (i % 8) * (CW + GAP)
			cy = y + (i // 8) * (CH + GAP)
			out.append('<rect x="%s" y="%s" width="%s" height="%s" rx="6" fill="%s"/>' % (cx, cy, CW, CH, CELL))
			out.append(use(syms.get(k, 48), cx + (CW - 48) / 2, cy + 8, 48))
			out.append(txt(cx + CW / 2, cy + 74, label, 12, LAB, "middle"))
		y += rows * (CH + GAP) + 16
	H = y + 16
	s = HEAD % "the full sheet" + '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">\n' % (W, H, W, H)
	s += '<title>Afterglow icons, variant E</title>\n<defs>%s\n%s\n</defs>\n<rect width="%d" height="%d" fill="%s"/>\n' % ("".join(syms.defs), "\n".join(syms.syms), W, H, BG)
	s += "\n".join(out) + "\n</svg>\n"
	return s, W, H


def main():
	if len(sys.argv) != 2:
		sys.exit("usage: gen_e.py OUT_DIR")
	out = sys.argv[1]
	n = write_icons(out)
	s, W, H = write_sheet(Syms())
	open(os.path.join(out, "sheet.svg"), "w").write(s)
	print("icons", len(I), "hinted", len(HINTED), "files", n, "groups", len(GROUPS), "listings", sum(len(g[1]) for g in GROUPS), "sheet", W, H)


if __name__ == "__main__":
	sys.exit(main())
