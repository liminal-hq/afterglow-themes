#!/usr/bin/env python3
# Draw the Afterglow for ReactOS CD media as vector masters: three disc compositions, the full-face CD label, the jewel case front insert
# and back tray card, and the mock-up, plus the print pages built from them.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
#   python3 gen_media.py OUT_DIR [FONT_DIR] [--style stepped|smooth]
#
# Draws every piece in two styles, the names the desktop wallpapers use: stepped (flat bands, the retro 16 and 256 colour look of the boot
# logo) and smooth (the same colours as continuous gradients, with a soft glow round the sun). Writes each style's masters to
# OUT_DIR/<style>/ (desktop/cd-media/stepped and desktop/cd-media/smooth in the repository), or only the one --style names: disc.svg (the
# selected composition), alternatives/disc-sunrise.svg, alternatives/disc-horizon.svg, label.svg, jewel-front.svg (the front insert as a
# single sheet), booklet-outside.svg and booklet-inside.svg (the front insert as a folded four-page booklet), jewel-back.svg and mockup.svg. The style changes only the sky, the bands and the glow; the layout, the words and the sizes are the same in both. Each
# piece's sky sits in its own scene group (id ending "scene", data-raster giving the box it covers), which render.py turns into a dithered
# print-resolution image for the smooth PDFs. render.py imports this module for the contact sheet's type. Every length is in millimetres (the viewBox is the artboard in mm). Every colour is an Afterglow palette
# colour: the 16 entries of desktop/boot/palette.json, read here so the two cannot drift, and the few named in EXTRA_COLOURS. All text is
# outlined from Noto Sans (SIL Open Font License, which allows embedding the outlines) in FONT_DIR (default: the first folder holding
# NotoSans-Light.ttf), so no font is needed to render or print a master. Each text path carries data-text (the words) and data-pt (its size
# in points) so the tests can check the wording and the minimum size. Deterministic: no randomness, no clock.
import importlib.util
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
DESKTOP = os.path.dirname(HERE)

# ---- the words: change the version here and run the generator -------------------------------------------------------------------------------
VERSION = "v0.1.0"  # the release on the disc
TITLE = "Afterglow"
SUBTITLE = "FOR REACTOS™"
MEDIA_LINE = "INSTALL AND LIVE CD"
SYSTEM_LINE = "ReactOS 0.4.16 · x86 · 32-bit"
UNOFFICIAL = "Unofficial remaster. Not endorsed by the ReactOS project."
COPYRIGHT = "Copyright © 1996-2026 ReactOS Team & Contributors"
LICENCE_LINE = "ReactOS: GPL-2.0-or-later and others · Afterglow art: Apache-2.0 OR MIT"
REPOSITORY = "github.com/liminal-hq-labs/reactos-liminal"
MAKER = "Liminal HQ Labs"
CONTENTS = (
	("Boot menu entry “ReactOS (Afterglow)”", "the stock “ReactOS” entry stays as the fallback"),
	("Afterglow desktop", "visual style, colour schemes and wallpaper"),
	("Afterglow icons and pointers", None),
	("Afterglow boot logo and logon banner", None),
	("The full ReactOS applications and games", "nothing is trimmed from this build"),
	("The afterfetch command", "also answers to neofetch and fastfetch"),
	("Wine Gecko", "the browser engine, so the Internet Browser works"),
	("LICENSES folder, NOTICE.txt and CHANGES.txt", None),
)
LICENCE_PARAGRAPHS = (
	"Afterglow for ReactOS — unofficial remaster by Liminal HQ Labs. It is not made, endorsed or supported by the ReactOS project. "
	"ReactOS™ is a trademark of the ReactOS project.",
	"ReactOS is free software under the GNU General Public License, version 2 or later, with parts under the LGPL 2.1 and other licences. "
	"The licence texts are in the LICENSES folder on this disc and every change is listed in CHANGES.txt.",
	"The Afterglow art and the remaster’s own scripts are Apache-2.0 OR MIT. Source: " + REPOSITORY + ", with the corresponding "
	"source attached to each release.",
	COPYRIGHT + ". Afterglow © 2026 Liminal HQ, Scott Morris.",
)
# The inside pages of the booklet: the disc's boot menu as rl iso writes it (reactos-liminal isotree.MENU_EDITS) and what the image holds
INSIDE_HEADING = "AFTERGLOW FOR REACTOS™"
INSIDE_STEPS = (
	"Start the computer from this disc, or give it to a virtual machine as its CD.",
	"The menu, “ReactOS (Afterglow) Boot Media”, starts the Live Environment: ReactOS runs from the disc and nothing is installed.",
	"To install, choose “ReactOS (Afterglow) Setup (Text Mode)” and follow Setup. It formats the partition you pick.",
	"Afterwards, start “ReactOS (Afterglow)”. The stock “ReactOS” entry stays in the menu as the fallback.",
)
INSIDE_CONTENTS = (
	"The full ReactOS 0.4.16: every application, game, screen saver and font",
	"The Afterglow visual style, colour schemes and 20 wallpapers",
	"Afterglow icons, pointers, Start button, logon banner and boot logo",
	"afterfetch, from any command prompt",
	"Wine Gecko, so the Internet Browser works",
	"LICENSES, NOTICE.txt and CHANGES.txt",
)
INSIDE_LEGAL = (
	"Unofficial remaster by Liminal HQ Labs. It is not made, endorsed or supported by the ReactOS project. "
	"ReactOS™ is a trademark of the ReactOS project.",
	COPYRIGHT + ". Afterglow © 2026 Liminal HQ, Scott Morris.",
	LICENCE_LINE,
)

# ---- the physical sizes, in mm ---------------------------------------------------------------------------------------------------------------
DISC_RADIUS = 60.0  # a 120 mm disc
DISC_PRINT_OUTER = 59.0  # 118 mm: the usual printable outer diameter of a printable disc
LABEL_RADIUS = 58.5  # 117 mm: the full-face label
HOLE_RADIUS = 20.5  # 41 mm: the label's centre hole and the printable disc's inner limit
STACKING_RING = 16.5  # 33 mm: the clear stacking ring
SPINDLE_RADIUS = 7.5  # 15 mm: the spindle hole
LABEL_BLEED = 3.0  # beyond the label circle and into the hole
SAFE_INNER = 23.0  # text stays 2.5 mm clear of the hole
SAFE_OUTER = 56.0  # and 2.5 mm inside the 117 mm label edge
MIN_POINTS = 6.0  # the smallest type anywhere
POINT = 25.4 / 72  # one point in mm
BOOKLET = 120.0  # the jewel case front insert, square
BOOKLET_BLEED = 2.0
TRAY_WIDTH, TRAY_HEIGHT, SPINE = 150.0, 118.0, 6.0  # the back tray card and its two spines
TRAY_BLEED = 2.0

STYLES = ("stepped", "smooth")  # as the desktop wallpapers name them
GLOW_REACH = 1.45  # the smooth sun's glow, in sun radii
GLOW_OPACITY = 0.45


def load(name, path):
	spec = importlib.util.spec_from_file_location(name, path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


OUTLINE = load("outline", os.path.join(DESKTOP, "dialogs", "outline.py"))

# ---- the palette -----------------------------------------------------------------------------------------------------------------------------
BOOT_PALETTE = [entry["rgb"] for entry in json.load(open(os.path.join(DESKTOP, "boot", "palette.json")))["entries"]]
BACKDROP, NIGHT1, NIGHT2, NIGHT3, NIGHT4, DUSK1, DUSK2, DUSK3, DUSK_ROSE, ROSE1, ROSE2, DEEP_GOLD, GOLD, BRIGHT_GOLD, PALE_GOLD, CREAM = BOOT_PALETTE
SKY_BANDS = [NIGHT1, NIGHT2, NIGHT3, NIGHT4, DUSK1, DUSK2, DUSK3, DUSK_ROSE, ROSE1, ROSE2]  # outermost to innermost, as the boot logo
# Afterglow colours from outside the boot palette: the void 300 text grey of the About banner, the paper and indigo of the icon set, the
# rose horizon and the sun's stepped bands of afterfetch's Afterglow logo (art/palette/afterglow-dusk.toml), and white for the mock-up's sheen.
SOFT_GREY = "#b4bfce"
PAPER = "#fbfaf6"
PAPER_SHADE = "#e4e2ec"
INDIGO_LINE = "#8f8da6"
ROSE_LINE = "#f43f5e"
SUN_STEPS = ("#ffd08e", "#ffbd67", "#ffaa40", "#fca073", "#f995a6")
WHITE = "#ffffff"
EXTRA_COLOURS = (SOFT_GREY, PAPER, PAPER_SHADE, INDIGO_LINE, ROSE_LINE, WHITE) + SUN_STEPS

HEAD = """<?xml version="1.0" encoding="UTF-8"?>
<!--
%s

(c) Copyright 2026 Liminal HQ, Scott Morris
SPDX-License-Identifier: Apache-2.0 OR MIT

%s
-->
"""


def number(value):
	text = ("%.3f" % value).rstrip("0").rstrip(".")
	return "0" if text in ("-0", "") else text


def escape(text):
	return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


# ---- type --------------------------------------------------------------------------------------------------------------------------------------
class Face:
	"""One Noto Sans weight, measuring and outlining text in mm along any baseline a mapper describes."""

	def __init__(self, path):
		self.font = OUTLINE.Font(path)

	def width(self, text, size, tracking=0.0):
		scale = size / self.font.units_per_em
		advances = [self.font.advance(self.font.cmap.get(ord(character), 0)) * scale for character in text]
		return sum(advances) + tracking * (len(text) - 1)

	def outline(self, text, size, mapper, tracking=0.0, start=0.0):
		"""Path data for `text` set at `size` mm. mapper(u, v) places a point u mm along the baseline from its start and v mm above it."""
		scale = size / self.font.units_per_em
		pen = start
		parts = []
		for character in text:
			glyph = self.font.cmap.get(ord(character), 0)
			for contour in self.font.contours(glyph):
				if len(contour) > 1:
					points = [(pen + x * scale, y * scale, on_curve) for x, y, on_curve in contour]
					parts.append(mapped_contour(points, mapper))
			pen += self.font.advance(glyph) * scale + tracking
		return "".join(parts)


def mapped_contour(points, mapper):
	"""One closed quadratic contour as SVG path data, each point placed by mapper (outline.contour_path's walk, with any placement)."""
	def place(point):
		return mapper(point[0], point[1])

	count = len(points)
	start_index = next((i for i, point in enumerate(points) if point[2]), None)
	if start_index is None:
		first = ((points[0][0] + points[1][0]) / 2, (points[0][1] + points[1][1]) / 2, True)
		points = [first] + points[1:] + points[:1]
		start_index = 0
		count = len(points)
	ordered = points[start_index:] + points[:start_index]
	x, y = place(ordered[0])
	out = ["M%s %s" % (number(x), number(y))]
	index = 1
	while index <= count:
		point = ordered[index % count]
		if point[2]:
			x, y = place(point)
			out.append("L%s %s" % (number(x), number(y)))
			index += 1
		else:
			following = ordered[(index + 1) % count]
			if following[2]:
				end = following
				index += 2
			else:
				end = ((point[0] + following[0]) / 2, (point[1] + following[1]) / 2, True)
				index += 1
			control_x, control_y = place(point)
			end_x, end_y = place(end)
			out.append("Q%s %s %s %s" % (number(control_x), number(control_y), number(end_x), number(end_y)))
	out.append("Z")
	return "".join(out)


class Type:
	"""The three weights, and text elements that record their words and size."""

	def __init__(self, font_dir):
		self.light = Face(os.path.join(font_dir, "NotoSans-Light.ttf"))
		self.regular = Face(os.path.join(font_dir, "NotoSans-Regular.ttf"))
		self.medium = Face(os.path.join(font_dir, "NotoSans-Medium.ttf"))

	@staticmethod
	def element(text, points, colour, data):
		if points < MIN_POINTS - 1e-9:
			sys.exit("gen_media.py: %r is set at %.2f pt, under the %.0f pt minimum" % (text, points, MIN_POINTS))
		return '<path data-text="%s" data-pt="%s" fill="%s" d="%s"/>' % (escape(text), number(points), colour, data)

	def straight(self, face, text, points, colour, x, baseline, anchor="start", tracking=0.0):
		size = points * POINT
		width = face.width(text, size, tracking)
		left = x - {"start": 0, "middle": width / 2, "end": width}[anchor]
		data = face.outline(text, size, lambda u, v: (left + u, baseline - v), tracking)
		return self.element(text, points, colour, data)

	def arc(self, face, text, points, colour, centre, radius, side, tracking=0.0, offset_angle=0.0):
		"""Text centred on the top of a circle (reading clockwise, tops outward) or on its bottom (reading anticlockwise, tops inward),
		with its baseline on `radius`. offset_angle turns the text's centre away from the top or bottom, in degrees, clockwise."""
		size = points * POINT
		width = face.width(text, size, tracking)
		centre_x, centre_y = centre
		turn = math.radians(offset_angle)
		if side == "top":
			def mapper(u, v):
				angle = (u - width / 2) / radius + turn
				return centre_x + (radius + v) * math.sin(angle), centre_y - (radius + v) * math.cos(angle)
		else:
			def mapper(u, v):
				angle = (u - width / 2) / radius - turn
				return centre_x + (radius - v) * math.sin(angle), centre_y + (radius - v) * math.cos(angle)
		if width / radius > math.pi * 0.95:
			sys.exit("gen_media.py: %r does not fit on a %.1f mm arc" % (text, radius))
		return self.element(text, points, colour, face.outline(text, size, mapper, tracking))

	def rotated(self, face, text, points, colour, x, y, direction, tracking=0.0, anchor="middle"):
		"""Text running up (direction 'up', reading bottom to top) or down from (x, y), its baseline on the line x."""
		size = points * POINT
		width = face.width(text, size, tracking)
		shift = {"start": 0, "middle": width / 2, "end": width}[anchor]
		if direction == "up":
			def mapper(u, v):
				return x - v, y + shift - u
		else:
			def mapper(u, v):
				return x + v, y - shift + u
		return self.element(text, points, colour, face.outline(text, size, mapper, tracking))

	def paragraph(self, face, text, points, colour, x, top, width, leading):
		"""Greedy word wrap to `width`; returns the text elements and the baseline after the last line."""
		size = points * POINT
		lines, line = [], ""
		for word in text.split(" "):
			attempt = (line + " " + word).strip()
			if face.width(attempt, size) <= width or not line:
				line = attempt
			else:
				lines.append(line)
				line = word
		lines.append(line)
		elements = []
		baseline = top
		for line in lines:
			elements.append(self.straight(face, line, points, colour, x, baseline))
			baseline += leading
		return elements, baseline


# ---- shapes ------------------------------------------------------------------------------------------------------------------------------------
def circle(centre_x, centre_y, radius, fill, extra=""):
	return '<circle cx="%s" cy="%s" r="%s" fill="%s"%s/>' % (number(centre_x), number(centre_y), number(radius), fill, extra)


def ring_path(centre_x, centre_y, outer, inner):
	"""An annulus as one even-odd path."""
	def loop(radius):
		return "M%s %sa%s %s 0 1 0 %s 0a%s %s 0 1 0 %s 0Z" % (number(centre_x - radius), number(centre_y), number(radius), number(radius),
			number(2 * radius), number(radius), number(radius), number(-2 * radius))
	return loop(outer) + loop(inner)


def rect(x, y, width, height, fill, extra=""):
	return '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"%s/>' % (number(x), number(y), number(width), number(height), fill, extra)


def sun(centre_x, centre_y, radius, clip_id):
	"""The Afterglow sun, half set: bright gold with the pale lit cap, clipped to the sky."""
	cap = '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (number(centre_x - radius * 0.09), number(centre_y - radius * 0.56),
		number(radius * 0.69), number(radius * 0.31), PALE_GOLD)
	return '<g clip-path="url(#%s)">%s%s</g>' % (clip_id, circle(centre_x, centre_y, radius, BRIGHT_GOLD), cap)


def sheets(centre_x, horizon, half_width, clip_id):
	"""The boot logo's two horizon sheets under the line: a lit far sheet and a darker near one."""
	return '<g clip-path="url(#%s)">%s%s</g>' % (clip_id,
		'<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (number(centre_x), number(horizon + half_width * 0.075), number(half_width), number(half_width * 0.08), NIGHT4),
		'<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="%s"/>' % (number(centre_x), number(horizon + half_width * 0.11), number(half_width * 0.86), number(half_width * 0.075), NIGHT2))


def horizon_line(x, y, width, thickness=0.35):
	return rect(x, y - thickness / 2, width, thickness, PALE_GOLD)


def stepped_sun(x, y, cell):
	"""afterfetch's Afterglow logo: the 36 x 24 pixel stepped sun on its rose horizon, at `cell` mm a pixel, top left at (x, y)."""
	bands = (
		(SUN_STEPS[0], "M15 6H21V7H24V8H25V9H11V8H12V7H15Z"),
		(SUN_STEPS[1], "M10 9H26V10H27V11H9V10H10Z"),
		(SUN_STEPS[2], "M8 11H28V12H29V13H7V12H8Z"),
		(SUN_STEPS[3], "M7 13H29V15H7Z"),
		(SUN_STEPS[4], "M6 15H30V18H6Z"),
		(ROSE_LINE, "M1 18H35V19H1Z"),
	)
	body = "".join('<path fill="%s" d="%s"/>' % (colour, data) for colour, data in bands)
	return '<g transform="translate(%s %s) scale(%s)" shape-rendering="crispEdges">%s</g>' % (number(x), number(y), number(cell), body)


# ---- the sky, in either style ------------------------------------------------------------------------------------------------------------
def band_middles(edges):
	"""The middle of each band between consecutive edges, as a list one shorter than edges."""
	return [(outer + inner) / 2 for outer, inner in zip(edges, edges[1:])]


def ring_sky(style, centre_x, centre_y, radii, sun_radius, gradient_id):
	"""The dusk bands round a sun at (centre_x, centre_y), radii outermost first as SKY_BANDS. Stepped: a flat circle per band. Smooth: one
	radial gradient through the same colours, each at the middle of its band, fading into the backdrop across the outermost band, with
	the sun's glow over it. Returns (defs, art); the art is not clipped, so the caller clips it to the sky."""
	if style == "stepped":
		return "", "".join(circle(centre_x, centre_y, radius, colour) for radius, colour in zip(radii, SKY_BANDS))
	outer = radii[0]
	middles = band_middles(list(radii) + [sun_radius])
	stops = [(0.0, SKY_BANDS[-1], 1)]
	stops += [(middle / outer, colour, 1) for middle, colour in reversed(list(zip(middles, SKY_BANDS)))]
	stops.append((1.0, BACKDROP, 1))
	defs = radial_gradient(gradient_id, centre_x, centre_y, outer, stops)
	glow_id = gradient_id + "-glow"
	reach = sun_radius * GLOW_REACH
	defs += radial_gradient(glow_id, centre_x, centre_y, reach, ((sun_radius / reach, BRIGHT_GOLD, GLOW_OPACITY), (1.0, BRIGHT_GOLD, 0)))
	size = 2 * outer + 200
	art = rect(centre_x - size / 2, centre_y - size / 2, size, size, "url(#%s)" % gradient_id) + circle(centre_x, centre_y, reach, "url(#%s)" % glow_id)
	return defs, art


def stripe_sky(style, left, width, horizon, heights, sun, gradient_id):
	"""The stepped wallpapers' sky over a level horizon: flat stripes of `heights`, the top one first, down to the horizon (stepped), or
	one vertical gradient through the same colours at the middle of each stripe (smooth), with the sun's glow (sun is centre_x, radius)."""
	top = horizon - sum(heights)
	if style == "stepped":
		stripes = []
		for height, colour in zip(heights, SKY_BANDS):
			stripes.append(rect(left, top, width, height + 0.05, colour))
			top += height
		return "", "".join(stripes)
	edges = [top]
	for height in heights:
		edges.append(edges[-1] + height)
	span = horizon - top
	stops = [(0.0, SKY_BANDS[0], 1)] + [((middle - top) / span, colour, 1) for middle, colour in zip(band_middles(edges), SKY_BANDS)]
	stops.append((1.0, SKY_BANDS[-1], 1))
	defs = ('<linearGradient id="%s" gradientUnits="userSpaceOnUse" x1="0" y1="%s" x2="0" y2="%s">%s</linearGradient>'
		% (gradient_id, number(top), number(horizon), gradient_stops(stops)))
	sun_x, sun_radius = sun
	glow_id = gradient_id + "-glow"
	reach = sun_radius * GLOW_REACH
	defs += radial_gradient(glow_id, sun_x, horizon, reach, ((sun_radius / reach, BRIGHT_GOLD, GLOW_OPACITY), (1.0, BRIGHT_GOLD, 0)))
	art = rect(left, top, width, span, "url(#%s)" % gradient_id) + circle(sun_x, horizon, reach, "url(#%s)" % glow_id)
	return defs, art


def gradient_stops(stops):
	out = []
	for offset, colour, opacity in stops:
		extra = "" if opacity == 1 else ' stop-opacity="%s"' % number(opacity)
		out.append('<stop offset="%s" stop-color="%s"%s/>' % (number(offset), colour, extra))
	return "".join(out)


def radial_gradient(gradient_id, centre_x, centre_y, radius, stops):
	return ('<radialGradient id="%s" gradientUnits="userSpaceOnUse" cx="%s" cy="%s" r="%s">%s</radialGradient>'
		% (gradient_id, number(centre_x), number(centre_y), number(radius), gradient_stops(stops)))


def scene(prefix, box, art):
	"""The sky layer of a piece: what changes between the styles. box is (x, y, width, height), the area the layer must cover in its own
	coordinates, which render.py rasterises for the smooth PDFs."""
	return '<g id="%sscene" data-raster="%s">%s</g>' % (prefix, " ".join(number(value) for value in box), art)


# ---- the disc compositions -----------------------------------------------------------------------------------------------------------------
# Each draws the art around (centre_x, centre_y) bigger than any print area and is clipped by its caller. Each returns (defs, sky, art,
# text): the sky is the backdrop and the bands, the part the style changes; the art is the sun, the sheets and the horizon drawn over it.
def lower_block(kind, centre):
	"""The media, system and legal lines set on bottom arcs, innermost first so they read top to bottom."""
	return [
		kind.arc(kind.medium, MEDIA_LINE, 7.5, BRIGHT_GOLD, centre, 28.6, "bottom", tracking=0.45),
		kind.arc(kind.regular, SYSTEM_LINE + " · " + VERSION, 7.5, CREAM, centre, 33.2, "bottom"),
		kind.arc(kind.regular, UNOFFICIAL, 6.5, SOFT_GREY, centre, 39.4, "bottom"),
		kind.arc(kind.regular, COPYRIGHT, 6.5, SOFT_GREY, centre, 42.9, "bottom"),
		kind.arc(kind.regular, LICENCE_LINE, 6.5, SOFT_GREY, centre, 46.4, "bottom"),
		kind.arc(kind.medium, REPOSITORY, 6.5, PALE_GOLD, centre, 49.9, "bottom"),
		kind.arc(kind.regular, MAKER, 6.5, SOFT_GREY, centre, 53.4, "bottom", tracking=0.3),
	]


def disc_halo(kind, style, centre_x, centre_y, prefix):
	"""B, Halo: the boot logo turned into the disc. The sun sits behind the hub, half set on a horizon through the centre, the dusk bands
	ring it to the rim, and the night below holds the horizon sheets and the small print."""
	sky, night = prefix + "sky", prefix + "night"
	defs = ('<clipPath id="%s"><rect x="%s" y="%s" width="140" height="70"/></clipPath>' % (sky, number(centre_x - 70), number(centre_y - 70))
		+ '<clipPath id="%s"><rect x="%s" y="%s" width="140" height="70"/></clipPath>' % (night, number(centre_x - 70), number(centre_y)))
	radii = (64, 57.5, 53.5, 49.5, 45.5, 41.5, 38, 34.5, 31.5, 28.5)
	sun_radius = 25.5
	band_defs, bands = ring_sky(style, centre_x, centre_y, radii, sun_radius, prefix + "bands")
	backdrop = circle(centre_x, centre_y, 70, BACKDROP) + '<g clip-path="url(#%s)">%s</g>' % (sky, bands)
	art = "".join([
		sun(centre_x, centre_y, sun_radius, sky),
		sheets(centre_x, centre_y, 58, night),
		horizon_line(centre_x - 62, centre_y, 124),
	])
	centre = (centre_x, centre_y)
	text = [
		kind.arc(kind.light, TITLE, 31, CREAM, centre, 46.2, "top"),
		kind.arc(kind.medium, SUBTITLE, 9.5, BRIGHT_GOLD, centre, 39.6, "top", tracking=0.9),
	] + lower_block(kind, centre)
	return defs + band_defs, backdrop, art, text


def disc_sunrise(kind, style, centre_x, centre_y, prefix):
	"""A, Sunrise: the sun rises from the bottom rim and its bands sweep up past the hub; the fine print runs round the top rim, the title
	arches over the hub and the media line sits under the horizon."""
	horizon = centre_y + 40
	sky, night = prefix + "sky", prefix + "night"
	defs = ('<clipPath id="%s"><rect x="%s" y="%s" width="140" height="%s"/></clipPath>' % (sky, number(centre_x - 70), number(centre_y - 70), number(horizon - centre_y + 70))
		+ '<clipPath id="%s"><rect x="%s" y="%s" width="140" height="40"/></clipPath>' % (night, number(centre_x - 70), number(horizon)))
	radii = (104, 92, 81, 71, 62, 53.5, 45.5, 38, 31, 24.5)
	sun_radius = 13
	band_defs, bands = ring_sky(style, centre_x, horizon, radii, sun_radius, prefix + "bands")
	backdrop = circle(centre_x, centre_y, 70, BACKDROP) + '<g clip-path="url(#%s)">%s</g>' % (sky, bands)
	art = "".join([
		sun(centre_x, horizon, sun_radius, sky),
		sheets(centre_x, horizon, 40, night),
		horizon_line(centre_x - 62, horizon, 124),
	])
	centre = (centre_x, centre_y)
	text = [
		kind.arc(kind.regular, UNOFFICIAL, 6.5, SOFT_GREY, centre, 53.4, "top"),
		kind.arc(kind.regular, COPYRIGHT, 6.5, SOFT_GREY, centre, 50.1, "top"),
		kind.arc(kind.regular, LICENCE_LINE, 6.5, SOFT_GREY, centre, 46.8, "top"),
		kind.arc(kind.medium, REPOSITORY + " · " + MAKER, 6.5, PALE_GOLD, centre, 43.5, "top"),
		kind.arc(kind.light, TITLE, 28, CREAM, centre, 32.0, "top"),
		kind.arc(kind.medium, SUBTITLE, 8.5, CREAM, centre, 25.4, "top", tracking=0.8),
		kind.straight(kind.medium, MEDIA_LINE, 7.5, BRIGHT_GOLD, centre_x, horizon + 5.4, "middle", tracking=0.45),
		kind.straight(kind.regular, SYSTEM_LINE + " · " + VERSION, 6.5, CREAM, centre_x, horizon + 9.2, "middle"),
	]
	return defs + band_defs, backdrop, art, text


def disc_horizon(kind, style, centre_x, centre_y, prefix):
	"""C, Horizon: a level horizon below the hub with the stepped sky of the stepped wallpapers above it and the sun setting to the right;
	the wordmark sits straight over the hub and the small print curves under the horizon."""
	horizon = centre_y + 12
	night = prefix + "night"
	sky = prefix + "sky"
	defs = ('<clipPath id="%s"><rect x="%s" y="%s" width="140" height="70"/></clipPath>' % (night, number(centre_x - 70), number(horizon))
		+ '<clipPath id="%s"><rect x="%s" y="%s" width="140" height="%s"/></clipPath>' % (sky, number(centre_x - 70), number(centre_y - 70), number(horizon - centre_y + 70)))
	heights = (24, 10, 8, 7, 6, 6, 5.5, 5.5, 5, 5)  # the top band reaches above the artboard; thinner toward the horizon, like the stepped wallpapers
	sun_x, sun_radius = centre_x + 31, 9.5
	band_defs, stripes = stripe_sky(style, centre_x - 70, 140, horizon, heights, (sun_x, sun_radius), prefix + "bands")
	if style == "smooth":
		stripes = '<g clip-path="url(#%s)">%s</g>' % (sky, stripes)  # the sun's glow stops at the horizon
	backdrop = circle(centre_x, centre_y, 70, BACKDROP) + stripes
	art = "".join([
		sun(sun_x, horizon, sun_radius, sky),
		sheets(centre_x, horizon, 52, night),
		horizon_line(centre_x - 62, horizon, 124),
	])
	centre = (centre_x, centre_y)
	text = [
		kind.straight(kind.light, TITLE, 34, CREAM, centre_x, centre_y - 31.5, "middle"),
		kind.straight(kind.medium, SUBTITLE, 9.5, BRIGHT_GOLD, centre_x, centre_y - 24.6, "middle", tracking=0.9),
	] + lower_block(kind, centre)
	return defs + band_defs, backdrop, art, text


COMPOSITIONS = {"halo": disc_halo, "sunrise": disc_sunrise, "horizon": disc_horizon}
SELECTED = "halo"
NAMES = {"halo": "B · Halo", "sunrise": "A · Sunrise", "horizon": "C · Horizon"}


def guides(centre_x, centre_y, circles, colour=ROSE_LINE):
	"""The guide layer: hairline circles that are never printed (render.py removes the group)."""
	body = "".join('<circle cx="%s" cy="%s" r="%s" data-guide="%s"/>' % (number(centre_x), number(centre_y), number(radius), name) for name, radius in circles)
	cross = '<path d="M%s %sh4M%s %sv4"/>' % (number(centre_x - 2), number(centre_y), number(centre_x), number(centre_y - 2))
	return ('<g id="guides" data-print="no" fill="none" stroke="%s" stroke-width="0.15" stroke-dasharray="1 0.6">%s%s</g>' % (colour, body, cross))


def disc_art(kind, style, composition, centre_x, centre_y, prefix, outer, inner):
	"""A composition clipped to the annulus between inner and outer: returns (defs, body). The sky's scene group covers the square round
	the outer circle."""
	defs, sky, art, text = COMPOSITIONS[composition](kind, style, centre_x, centre_y, prefix)
	clip = prefix + "print"
	defs += '<clipPath id="%s"><path clip-rule="evenodd" d="%s"/></clipPath>' % (clip, ring_path(centre_x, centre_y, outer, inner))
	layer = scene(prefix, (centre_x - outer, centre_y - outer, 2 * outer, 2 * outer), sky)
	body = '<g id="%sart" clip-path="url(#%s)">%s%s<g id="%stext">%s</g></g>' % (prefix, clip, layer, art, prefix, "".join(text))
	return defs, body


def svg(title, note, width, height, defs, body):
	return HEAD % (title, note) + (
		'<svg xmlns="http://www.w3.org/2000/svg" width="%smm" height="%smm" viewBox="0 0 %s %s">\n<title>%s</title>\n<defs>%s</defs>\n%s\n</svg>\n'
		% (number(width), number(height), number(width), number(height), escape(title), defs, body))


STYLE_NOTES = {
	"stepped": "Stepped: the sky is flat bands of the boot logo's colours, the retro 16 and 256 colour look.",
	"smooth": "Smooth: the sky is continuous gradients through the same colours, with a soft glow round the sun.",
}


def disc_master(kind, style, composition):
	defs, body = disc_art(kind, style, composition, 60, 60, "d-", DISC_RADIUS, HOLE_RADIUS)
	circles = (("disc edge 120 mm", DISC_RADIUS), ("printable outer 118 mm", DISC_PRINT_OUTER), ("label 117 mm", LABEL_RADIUS),
		("text safe outer 112 mm", SAFE_OUTER), ("text safe inner 46 mm", SAFE_INNER), ("printable inner and label hole 41 mm", HOLE_RADIUS),
		("stacking ring 33 mm", STACKING_RING), ("spindle hole 15 mm", SPINDLE_RADIUS))
	selected = composition == SELECTED
	title = "Afterglow for ReactOS disc art, %s, %s%s" % (NAMES[composition], style, " (selected)" if selected else " (alternative)")
	note = ("A 120 x 120 mm artboard in mm for a printable disc: the art runs from the 41 mm inner limit out to the 120 mm edge, 1 mm of bleed\n"
		"past the usual 118 mm printable area, and the hub stays clear. Text stays between 46 and 112 mm. The guides group (data-print=\"no\")\n"
		"marks the edge, the printable limits, the label, the text safe area, the stacking ring and the spindle hole, and render.py removes it\n"
		"before any print. Text is outlined from Noto Sans; generated by gen_media.py, so edit the generator, not this file.\n" + STYLE_NOTES[style])
	return svg(title, note, 120, 120, defs, body + "\n" + guides(60, 60, circles))


LABEL_SIZE = 2 * (LABEL_RADIUS + LABEL_BLEED)  # 123 mm


def label_master(kind, style):
	centre = LABEL_SIZE / 2
	defs, body = disc_art(kind, style, SELECTED, centre, centre, "l-", LABEL_RADIUS + LABEL_BLEED, HOLE_RADIUS - LABEL_BLEED)
	circles = (("bleed outer 123 mm", LABEL_RADIUS + LABEL_BLEED), ("label cut 117 mm", LABEL_RADIUS), ("text safe outer 112 mm", SAFE_OUTER),
		("text safe inner 46 mm", SAFE_INNER), ("label hole 41 mm", HOLE_RADIUS), ("bleed inner 35 mm", HOLE_RADIUS - LABEL_BLEED))
	title = "Afterglow for ReactOS CD label, %s, %s, 117 mm full face with 3 mm bleed" % (NAMES[SELECTED], style)
	note = ("A 123 x 123 mm artboard in mm: the 117 mm full-face label with its 41 mm hole, and 3 mm of bleed past the edge and into the hole.\n"
		"Text stays between 46 and 112 mm. The guides group (data-print=\"no\") marks the cut, the bleed and the safe area and is removed\n"
		"before printing; render.py lays the label out on A4 and Letter sheets with crop marks. Generated by gen_media.py.\n" + STYLE_NOTES[style])
	return svg(title, note, LABEL_SIZE, LABEL_SIZE, defs, body + "\n" + guides(centre, centre, circles))


# ---- the jewel case ------------------------------------------------------------------------------------------------------------------------
def jewel_front(kind, style, prefix="f-"):
	"""The 120 mm front insert, in trim coordinates (0 to 120), drawn 2 mm past the trim on every side: the boot logo's scene as the cover."""
	bleed = BOOKLET_BLEED
	horizon = 60.0
	centre_x = BOOKLET / 2
	sky, night = prefix + "sky", prefix + "night"
	defs = ('<clipPath id="%s"><rect x="%s" y="%s" width="%s" height="%s"/></clipPath>' % (sky, number(-bleed), number(-bleed), number(BOOKLET + 2 * bleed), number(horizon + bleed))
		+ '<clipPath id="%s"><rect x="%s" y="%s" width="%s" height="%s"/></clipPath>' % (night, number(-bleed), number(horizon), number(BOOKLET + 2 * bleed), number(BOOKLET - horizon + bleed)))
	radii = (66, 59.5, 53, 46.5, 40, 34, 28.5, 23.5, 19, 15)
	sun_radius = 9.5
	band_defs, bands = ring_sky(style, centre_x, horizon, radii, sun_radius, prefix + "bands")
	defs += band_defs
	layer = scene(prefix, (-bleed, -bleed, BOOKLET + 2 * bleed, BOOKLET + 2 * bleed),
		rect(-bleed, -bleed, BOOKLET + 2 * bleed, BOOKLET + 2 * bleed, BACKDROP) + '<g clip-path="url(#%s)">%s</g>' % (sky, bands))
	art = "".join([
		layer,
		sun(centre_x, horizon, sun_radius, sky),
		sheets(centre_x, horizon, 58, night),
		horizon_line(8, horizon, BOOKLET - 16, 0.3),
	])
	text = [
		kind.straight(kind.medium, MEDIA_LINE, 7.5, BRIGHT_GOLD, 7, 10, tracking=0.45),
		kind.straight(kind.regular, VERSION, 7.5, CREAM, BOOKLET - 7, 10, "end"),
		kind.straight(kind.light, TITLE, 54, CREAM, centre_x, 87, "middle"),
		kind.straight(kind.medium, SUBTITLE, 11, BRIGHT_GOLD, centre_x, 96.5, "middle", tracking=1.3),
		kind.straight(kind.regular, SYSTEM_LINE, 7.5, CREAM, centre_x, 106, "middle"),
		kind.straight(kind.regular, "Unofficial remaster by Liminal HQ Labs · Not endorsed by the ReactOS project", 6.5, SOFT_GREY, centre_x, 113.5, "middle"),
	]
	return defs, art + '<g id="%stext">%s</g>' % (prefix, "".join(text))


def jewel_back(kind, style, prefix="b-"):
	"""The 150 x 118 mm tray card, in trim coordinates, drawn 2 mm past the trim: two 6 mm spines and the 138 mm back between them."""
	bleed = TRAY_BLEED
	left, right = SPINE, TRAY_WIDTH - SPINE
	band_bottom = 24.0
	centre_x = TRAY_WIDTH / 2
	sky, night = prefix + "sky", prefix + "night"
	defs = ('<clipPath id="%s"><rect x="%s" y="%s" width="%s" height="%s"/></clipPath>' % (sky, number(left), number(-bleed), number(right - left), number(band_bottom + bleed))
		+ '<clipPath id="%s"><rect x="%s" y="%s" width="%s" height="12"/></clipPath>' % (night, number(left), number(band_bottom), number(right - left)))
	radii = (66, 58, 50, 43, 36.5, 30.5, 25, 20, 15.5, 11.5)
	sun_radius = 7
	band_defs, bands = ring_sky(style, centre_x, band_bottom, radii, sun_radius, prefix + "bands")
	defs += band_defs
	art = [
		scene(prefix, (-bleed, -bleed, TRAY_WIDTH + 2 * bleed, TRAY_HEIGHT + 2 * bleed),
			rect(-bleed, -bleed, TRAY_WIDTH + 2 * bleed, TRAY_HEIGHT + 2 * bleed, BACKDROP) + '<g clip-path="url(#%s)">%s</g>' % (sky, bands)),
		sun(centre_x, band_bottom, sun_radius, sky),
		sheets(centre_x, band_bottom, 60, night),
		horizon_line(left + 6, band_bottom, right - left - 12, 0.3),
	]
	text = [kind.straight(kind.light, "Afterglow", 24, CREAM, left + 6, 15.5), kind.straight(kind.medium, "FOR REACTOS™", 7.5, BRIGHT_GOLD, left + 7, 21, tracking=0.6)]
	text.append(kind.straight(kind.regular, VERSION, 7.5, CREAM, right - 6, 21, "end"))
	# the contents, like a track list
	column_x = left + 6
	text.append(kind.straight(kind.medium, "WHAT IS ON THIS DISC", 7.5, BRIGHT_GOLD, column_x, 38, tracking=0.45))
	baseline = 45.5
	for index, (item, detail) in enumerate(CONTENTS, 1):
		text.append(kind.straight(kind.medium, "%02d" % index, 7.5, BRIGHT_GOLD, column_x, baseline))
		text.append(kind.straight(kind.regular, item, 7.5, CREAM, column_x + 6.5, baseline))
		if item == "The afterfetch command":
			art.append(stepped_sun(column_x + 6.5 + kind.regular.width(item, 7.5 * POINT) + 1.5, baseline - 3.0, 0.15))
		if detail:
			text.append(kind.straight(kind.regular, detail, 6.5, SOFT_GREY, column_x + 6.5, baseline + 3.3))
			baseline += 7.6
		else:
			baseline += 5.0
	# the licence and credit paragraph
	paragraph_x = 84.0
	text.append(kind.straight(kind.medium, "LICENCES AND CREDITS", 7.5, BRIGHT_GOLD, paragraph_x, 38, tracking=0.45))
	top = 45.5
	for paragraph in LICENCE_PARAGRAPHS:
		elements, top = kind.paragraph(kind.regular, paragraph, 6.5, SOFT_GREY, paragraph_x, top, right - 6 - paragraph_x, 2.95)
		text.extend(elements)
		top += 1.6
	if top > 106:
		sys.exit("gen_media.py: the licence paragraph runs into the foot of the tray card")
	# the foot: the system and the source
	text.append(kind.straight(kind.regular, SYSTEM_LINE, 7.5, CREAM, column_x, 112))
	text.append(kind.straight(kind.medium, REPOSITORY, 6.5, PALE_GOLD, right - 6, 112, "end"))
	art.append(rect(column_x, 106.6, right - left - 12, 0.2, NIGHT4))
	# the spines: the title and the version, reading up the left spine and down the right one
	spine_text = "Afterglow for ReactOS™  ·  " + VERSION
	text.append(kind.rotated(kind.regular, spine_text, 8, CREAM, SPINE / 2 + 1.0, TRAY_HEIGHT / 2, "up", tracking=0.2))
	text.append(kind.rotated(kind.regular, spine_text, 8, CREAM, TRAY_WIDTH - SPINE / 2 - 1.0, TRAY_HEIGHT / 2, "down", tracking=0.2))
	for spine_x in (SPINE / 2, TRAY_WIDTH - SPINE / 2):
		art.append(circle(spine_x, 8, 1.3, BRIGHT_GOLD))
		art.append(circle(spine_x, TRAY_HEIGHT - 8, 1.3, BRIGHT_GOLD))
	return defs, "".join(art) + '<g id="%stext">%s</g>' % (prefix, "".join(text))


# ---- the booklet: the front insert as one sheet folded in half --------------------------------------------------------------------------
# Four 120 mm pages on a 240 x 120 mm sheet. The outside spread is the back cover (page 4) on the left and the front cover (page 1, the front
# insert as drawn by jewel_front) on the right; the inside spread is page 2 on the left and page 3 on the right. Each page is drawn in its
# own trim coordinates (0 to 120) with 2 mm of bleed and clipped at the fold by booklet_spread.
def small_sky(kind, style, prefix, horizon, sun_radius, radii, margin=7.0):
	"""The tray card's sky in miniature over a horizon at `horizon`: the scene, the sun, the sheets and the line. Returns (defs, art)."""
	bleed = BOOKLET_BLEED
	centre_x = BOOKLET / 2
	sky, night = prefix + "sky", prefix + "night"
	defs = ('<clipPath id="%s"><rect x="%s" y="%s" width="%s" height="%s"/></clipPath>' % (sky, number(-bleed), number(-bleed), number(BOOKLET + 2 * bleed), number(horizon + bleed))
		+ '<clipPath id="%s"><rect x="%s" y="%s" width="%s" height="12"/></clipPath>' % (night, number(-bleed), number(horizon), number(BOOKLET + 2 * bleed)))
	band_defs, bands = ring_sky(style, centre_x, horizon, radii, sun_radius, prefix + "bands")
	art = "".join([
		scene(prefix, (-bleed, -bleed, BOOKLET + 2 * bleed, BOOKLET + 2 * bleed),
			rect(-bleed, -bleed, BOOKLET + 2 * bleed, BOOKLET + 2 * bleed, BACKDROP) + '<g clip-path="url(#%s)">%s</g>' % (sky, bands)),
		sun(centre_x, horizon, sun_radius, sky),
		sheets(centre_x, horizon, 58, night),
		horizon_line(margin, horizon, BOOKLET - 2 * margin, 0.3),
	])
	return defs + band_defs, art


def booklet_back_cover(kind, style, prefix):
	"""Page 4, the back cover: a quiet night with a small sun setting on a low horizon, the wordmark, the source and the maker."""
	defs, art = small_sky(kind, style, prefix, 62.0, 4.5, (34, 30, 26.5, 23, 19.5, 16.5, 13.5, 11, 8.5, 6.5), margin=22.0)
	centre_x = BOOKLET / 2
	text = [
		kind.straight(kind.light, TITLE, 22, CREAM, centre_x, 84, "middle"),
		kind.straight(kind.medium, SUBTITLE, 7.5, BRIGHT_GOLD, centre_x, 90.5, "middle", tracking=0.9),
		kind.straight(kind.medium, REPOSITORY, 6.5, PALE_GOLD, centre_x, 104, "middle"),
		kind.straight(kind.regular, MAKER, 6.5, SOFT_GREY, centre_x, 109, "middle", tracking=0.3),
	]
	return defs, art + '<g id="%stext">%s</g>' % (prefix, "".join(text))


def booklet_page_two(kind, style, prefix):
	"""Page 2, the left of the inside spread: the tray card's sky and sun as a small header, then the getting started steps."""
	margin = 7.0
	defs, art = small_sky(kind, style, prefix, 24.0, 7, (66, 58, 50, 43, 36.5, 30.5, 25, 20, 15.5, 11.5))
	text = [
		kind.straight(kind.medium, INSIDE_HEADING, 7.5, BRIGHT_GOLD, margin, 10, tracking=0.45),
		kind.straight(kind.regular, VERSION, 7.5, CREAM, BOOKLET - margin, 10, "end"),
		kind.straight(kind.medium, "GETTING STARTED", 7.5, BRIGHT_GOLD, margin, 42, tracking=0.45),
	]
	baseline = 51.0
	for index, step in enumerate(INSIDE_STEPS, 1):
		text.append(kind.straight(kind.medium, "%02d" % index, 7.5, BRIGHT_GOLD, margin, baseline))
		elements, baseline = kind.paragraph(kind.regular, step, 7.5, CREAM, margin + 7, baseline, BOOKLET - 2 * margin - 7, 3.6)
		text.extend(elements)
		baseline += 5.4
	if baseline > 114:
		sys.exit("gen_media.py: the getting started steps run off page 2")
	return defs, art + '<g id="%stext">%s</g>' % (prefix, "".join(text))


def booklet_page_three(kind, style, prefix):
	"""Page 3, the right of the inside spread: what is on the disc, then the licences, credits and notices, as on the tray card."""
	bleed = BOOKLET_BLEED
	margin = 7.0
	art = [scene(prefix, (-bleed, -bleed, BOOKLET + 2 * bleed, BOOKLET + 2 * bleed), rect(-bleed, -bleed, BOOKLET + 2 * bleed, BOOKLET + 2 * bleed, BACKDROP))]
	text = [kind.straight(kind.medium, "ON THIS DISC", 7.5, BRIGHT_GOLD, margin, 14, tracking=0.45)]
	baseline = 22.0
	for item in INSIDE_CONTENTS:
		art.append(circle(margin + 0.7, baseline - 0.95, 0.65, BRIGHT_GOLD))
		elements, after = kind.paragraph(kind.regular, item, 7.5, CREAM, margin + 3, baseline, BOOKLET - 2 * margin - 3, 3.5)
		text.extend(elements)
		if item.startswith("afterfetch"):
			art.append(stepped_sun(margin + 3 + kind.regular.width(item, 7.5 * POINT) + 1.8, baseline - 3.4, 0.15))
		baseline = after + 1.6
	# the licences and credits sit at the foot of the page: measured once, then set so the source line ends 7 mm above the trim
	def notices(start):
		elements, top = [], start
		for paragraph in INSIDE_LEGAL:
			lines, top = kind.paragraph(kind.regular, paragraph, 6.5, SOFT_GREY, margin, top, BOOKLET - 2 * margin, 2.95)
			elements.extend(lines)
			top += 1.2
		elements.append(kind.straight(kind.medium, REPOSITORY, 6.5, PALE_GOLD, margin, top + 0.6))
		return elements, top + 0.6
	_elements, height = notices(0.0)
	start = BOOKLET - 7.0 - height
	rule_y = start - 15.5
	if rule_y < baseline + 3:
		sys.exit("gen_media.py: the contents run into the notices on page 3")
	art.append(rect(margin, rule_y, BOOKLET - 2 * margin, 0.2, NIGHT4))
	text.append(kind.straight(kind.medium, "LICENCES AND CREDITS", 7.5, BRIGHT_GOLD, margin, rule_y + 8, tracking=0.45))
	elements, _end = notices(start)
	text.extend(elements)
	return "", "".join(art) + '<g id="%stext">%s</g>' % (prefix, "".join(text))


def booklet_spread(kind, style, left, right):
	"""Two pages side by side on the 240 x 120 mm sheet, in sheet trim coordinates: each (draw, prefix) is clipped to its half, the
	outer bleed kept and the two halves meeting at the fold."""
	bleed = BOOKLET_BLEED
	defs, body = [], []
	for (draw, prefix), offset, clip_box in ((left, 0.0, (-bleed, -bleed, BOOKLET + bleed, BOOKLET + 2 * bleed)),
			(right, BOOKLET, (0.0, -bleed, BOOKLET + bleed, BOOKLET + 2 * bleed))):
		page_defs, page_body = draw(kind, style, prefix)
		clip = prefix + "page"
		x, y, width, height = clip_box
		defs.append(page_defs + '<clipPath id="%s"><rect x="%s" y="%s" width="%s" height="%s"/></clipPath>' % (clip, number(x), number(y), number(width), number(height)))
		body.append('<g id="%spage" transform="translate(%s 0)" clip-path="url(#%s)">%s</g>' % (prefix, number(offset), clip, page_body))
	return "".join(defs), "".join(body)


def trim_guides(width, height, folds=()):
	lines = ['<rect x="0" y="0" width="%s" height="%s" data-guide="trim"/>' % (number(width), number(height))]
	lines += ['<path d="M%s 0V%s" data-guide="fold"/>' % (number(x), number(height)) for x in folds]
	return '<g id="guides" data-print="no" fill="none" stroke="%s" stroke-width="0.15" stroke-dasharray="1 0.6">%s</g>' % (ROSE_LINE, "".join(lines))


def jewel_front_master(kind, style):
	defs, body = jewel_front(kind, style)
	size = BOOKLET + 2 * BOOKLET_BLEED
	note = ("The jewel case front insert: a 120 x 120 mm trim with 2 mm of bleed on every side (a 124 x 124 mm artboard in mm, the trim at\n"
		"2 mm in). The guides group marks the trim and is removed before printing. Generated by gen_media.py.\n" + STYLE_NOTES[style])
	content = '<g transform="translate(%s %s)">%s\n%s</g>' % (number(BOOKLET_BLEED), number(BOOKLET_BLEED), body, trim_guides(BOOKLET, BOOKLET))
	return svg("Afterglow for ReactOS jewel case front insert, " + style, note, size, size, defs, content)


BOOKLET_SHEET = 2 * BOOKLET  # the unfolded booklet: two 120 mm pages side by side


def booklet_master(kind, style, side):
	"""One side of the booklet sheet: 240 x 120 mm with 2 mm of bleed (a 244 x 124 mm artboard, the trim at 2 mm in), the fold at
	120 mm. The outside is the back cover and the front cover; the inside is pages 2 and 3, printed on the back of the outside."""
	if side == "outside":
		defs, body = booklet_spread(kind, style, (booklet_back_cover, "bb-"), (jewel_front, "bf-"))
		title = "Afterglow for ReactOS CD booklet, outside (back cover and front cover), " + style
	else:
		defs, body = booklet_spread(kind, style, (booklet_page_two, "bl-"), (booklet_page_three, "br-"))
		title = "Afterglow for ReactOS CD booklet, inside (pages 2 and 3), " + style
	note = ("The front insert as a booklet: one 240 x 120 mm sheet folded in half to 120 x 120 mm pages, with 2 mm of bleed (a 244 x 124 mm\n"
		"artboard in mm, the trim at 2 mm in) and the fold at 120 mm. booklet-outside.svg is the back cover (left) and the front cover\n"
		"(right); booklet-inside.svg is page 2 (left) and page 3 (right), printed on its back, flipping a landscape sheet on the short edge.\n"
		"The guides group marks the trim and the fold and is removed before printing. Generated by gen_media.py.\n" + STYLE_NOTES[style])
	content = '<g transform="translate(%s %s)">%s\n%s</g>' % (number(BOOKLET_BLEED), number(BOOKLET_BLEED), body,
		trim_guides(BOOKLET_SHEET, BOOKLET, (BOOKLET,)))
	return svg(title, note, BOOKLET_SHEET + 2 * BOOKLET_BLEED, BOOKLET + 2 * BOOKLET_BLEED, defs, content)


def jewel_back_master(kind, style):
	defs, body = jewel_back(kind, style)
	note = ("The jewel case back tray card: a 150 x 118 mm trim (6 mm spines on both sides of a 138 mm back) with 2 mm of bleed, on a\n"
		"154 x 122 mm artboard in mm. The guides group marks the trim and the two folds and is removed before printing. Generated by gen_media.py.\n"
		+ STYLE_NOTES[style])
	content = '<g transform="translate(%s %s)">%s\n%s</g>' % (number(TRAY_BLEED), number(TRAY_BLEED), body, trim_guides(TRAY_WIDTH, TRAY_HEIGHT, (SPINE, TRAY_WIDTH - SPINE)))
	return svg("Afterglow for ReactOS jewel case back tray card, " + style, note, TRAY_WIDTH + 2 * TRAY_BLEED, TRAY_HEIGHT + 2 * TRAY_BLEED, defs, content)


# ---- the mock-up -----------------------------------------------------------------------------------------------------------------------------
def disc_object(kind, style, centre_x, centre_y, prefix):
	"""A pressed disc: the printed face, the clear stacking ring and mirror band, the spindle hole, and a soft sheen."""
	defs, face = disc_art(kind, style, SELECTED, centre_x, centre_y, prefix, DISC_PRINT_OUTER, HOLE_RADIUS)
	sheen = prefix + "sheen"
	hub = prefix + "hub"
	defs += ('<linearGradient id="%s" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s" stop-opacity="0"/><stop offset="0.38" stop-color="%s" stop-opacity="0.14"/>'
		'<stop offset="0.46" stop-color="%s" stop-opacity="0"/><stop offset="0.62" stop-color="%s" stop-opacity="0"/><stop offset="0.7" stop-color="%s" stop-opacity="0.08"/>'
		'<stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>') % (sheen, WHITE, WHITE, WHITE, WHITE, WHITE, WHITE)
	defs += ('<linearGradient id="%s" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s"/><stop offset="0.5" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
		% (hub, PAPER_SHADE, INDIGO_LINE, SOFT_GREY))
	body = "".join([
		'<path fill-rule="evenodd" fill="%s" d="%s"/>' % (SOFT_GREY, ring_path(centre_x, centre_y, DISC_RADIUS, SPINDLE_RADIUS)),
		'<path fill-rule="evenodd" fill="url(#%s)" d="%s"/>' % (hub, ring_path(centre_x, centre_y, HOLE_RADIUS, SPINDLE_RADIUS)),
		'<path fill-rule="evenodd" fill="%s" fill-opacity="0.55" d="%s"/>' % (NIGHT2, ring_path(centre_x, centre_y, STACKING_RING + 0.6, STACKING_RING)),
		'<path fill-rule="evenodd" fill="%s" fill-opacity="0.35" d="%s"/>' % (WHITE, ring_path(centre_x, centre_y, SPINDLE_RADIUS + 2.2, SPINDLE_RADIUS)),
		face,
		'<path fill-rule="evenodd" fill="url(#%s)" d="%s"/>' % (sheen, ring_path(centre_x, centre_y, DISC_RADIUS, SPINDLE_RADIUS)),
		'<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-opacity="0.35" stroke-width="0.3"/>' % (number(centre_x), number(centre_y), number(DISC_RADIUS - 0.15), WHITE),
	])
	return defs, body


def mockup_master(kind, style):
	"""The hero picture: the jewel case, the disc with its sheen, and the label on its backing sheet, on a dusk table."""
	width, height = 412.0, 180.0
	defs = ('<radialGradient id="m-glow" cx="0.5" cy="1.05" r="0.75"><stop offset="0" stop-color="%s"/><stop offset="0.45" stop-color="%s"/>'
		'<stop offset="1" stop-color="%s"/></radialGradient>' % (DUSK_ROSE, NIGHT3, BACKDROP))
	defs += '<filter id="m-shadow" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="2.2"/></filter>'
	defs += ('<linearGradient id="m-case" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="%s" stop-opacity="0.18"/><stop offset="0.35" stop-color="%s" stop-opacity="0.04"/>'
		'<stop offset="0.36" stop-color="%s" stop-opacity="0"/><stop offset="1" stop-color="%s" stop-opacity="0.06"/></linearGradient>' % (WHITE, WHITE, WHITE, WHITE))
	body = [rect(0, 0, width, height, "url(#m-glow)")]
	# the jewel case: 142 x 125 mm with the hinge on the left, the front insert under the lid
	case_x, case_y = 16.0, 27.0
	front_defs, front = jewel_front(kind, style, "m-f-")
	defs += front_defs + '<clipPath id="m-trim"><rect x="0" y="0" width="120" height="120"/></clipPath>'
	body.append('<rect x="%s" y="%s" width="142" height="125" rx="1.5" fill="%s" fill-opacity="0.6" filter="url(#m-shadow)" transform="translate(2.5 3)"/>' % (number(case_x), number(case_y), BACKDROP))
	body.append('<rect x="%s" y="%s" width="142" height="125" rx="1.5" fill="%s"/>' % (number(case_x), number(case_y), NIGHT1))
	body.append('<g transform="translate(%s %s)"><g clip-path="url(#m-trim)">%s</g></g>' % (number(case_x + 16), number(case_y + 2.5), front))
	body.append('<rect x="%s" y="%s" width="10" height="125" fill="%s" fill-opacity="0.5"/>' % (number(case_x + 1.5), number(case_y), NIGHT2))
	for offset in (3.5, 8.0):
		body.append('<rect x="%s" y="%s" width="0.4" height="125" fill="%s" fill-opacity="0.25"/>' % (number(case_x + offset), number(case_y), WHITE))
	body.append('<rect x="%s" y="%s" width="142" height="125" rx="1.5" fill="url(#m-case)" stroke="%s" stroke-opacity="0.35" stroke-width="0.4"/>' % (number(case_x), number(case_y), WHITE))
	# the label on its backing sheet, flat, to the right
	sheet_x, sheet_y = 276.0, 15.0
	label_centre = (sheet_x + 64.0, sheet_y + 72.0)
	label_defs, label = disc_art(kind, style, SELECTED, label_centre[0], label_centre[1], "m-l-", LABEL_RADIUS, HOLE_RADIUS)
	defs += label_defs
	body.append('<rect x="%s" y="%s" width="128" height="150" rx="1" fill="%s" fill-opacity="0.6" filter="url(#m-shadow)" transform="translate(2 2.5)"/>' % (number(sheet_x), number(sheet_y), BACKDROP))
	body.append('<rect x="%s" y="%s" width="128" height="150" rx="1" fill="%s"/>' % (number(sheet_x), number(sheet_y), PAPER))
	body.append(label)
	body.append('<path fill="none" stroke="%s" stroke-width="0.25" d="%s"/>' % (PAPER_SHADE, ring_path(label_centre[0], label_centre[1], LABEL_RADIUS + 0.2, HOLE_RADIUS - 0.2)))
	# the disc, over the case's right edge
	disc_centre = (204.0, 90.0)
	disc_defs, disc = disc_object(kind, style, disc_centre[0], disc_centre[1], "m-d-")
	defs += disc_defs
	body.append('<path fill-rule="evenodd" fill="%s" fill-opacity="0.7" filter="url(#m-shadow)" transform="translate(2.5 3.5)" d="%s"/>' % (BACKDROP, ring_path(disc_centre[0], disc_centre[1], DISC_RADIUS, SPINDLE_RADIUS)))
	body.append(disc)
	note = ("The hero picture for the design canvas and the board: a 412 x 180 mm scene in mm, built from the same drawings as the masters\n"
		"(the selected disc with a sheen, the jewel case front under its lid, the label on its backing sheet). Not for print. Generated by gen_media.py.\n"
		+ STYLE_NOTES[style])
	return svg("Afterglow for ReactOS CD media mock-up, " + style, note, width, height, defs, "\n".join(body))


# ---- files ---------------------------------------------------------------------------------------------------------------------------------------
def find_font_dir(argument):
	candidates = [argument] if argument else ["/usr/share/fonts/noto", "/usr/share/fonts/truetype/noto", "/usr/share/fonts/google-noto", "/usr/share/fonts/noto-fonts"]
	for folder in candidates:
		if folder and os.path.exists(os.path.join(folder, "NotoSans-Light.ttf")):
			return folder
	sys.exit("gen_media.py: NotoSans-Light.ttf not found; pass its folder as FONT_DIR")


def masters(kind, style):
	return {
		"disc.svg": disc_master(kind, style, SELECTED),
		"alternatives/disc-sunrise.svg": disc_master(kind, style, "sunrise"),
		"alternatives/disc-horizon.svg": disc_master(kind, style, "horizon"),
		"label.svg": label_master(kind, style),
		"jewel-front.svg": jewel_front_master(kind, style),
		"booklet-outside.svg": booklet_master(kind, style, "outside"),
		"booklet-inside.svg": booklet_master(kind, style, "inside"),
		"jewel-back.svg": jewel_back_master(kind, style),
		"mockup.svg": mockup_master(kind, style),
	}


def parse_style(arguments, program):
	"""Take --style stepped|smooth out of arguments; returns the styles to draw (both when it is absent)."""
	if "--style" not in arguments:
		return list(STYLES)
	index = arguments.index("--style")
	if index + 1 >= len(arguments) or arguments[index + 1] not in STYLES:
		sys.exit("%s: --style takes %s" % (program, " or ".join(STYLES)))
	style = arguments[index + 1]
	del arguments[index:index + 2]
	return [style]


def main():
	arguments = sys.argv[1:]
	styles = parse_style(arguments, "gen_media.py")
	if len(arguments) not in (1, 2):
		sys.exit("usage: gen_media.py OUT_DIR [FONT_DIR] [--style stepped|smooth]")
	out = arguments[0]
	kind = Type(find_font_dir(arguments[1] if len(arguments) == 2 else None))
	count = 0
	for style in styles:
		folder = os.path.join(out, style)
		os.makedirs(os.path.join(folder, "alternatives"), exist_ok=True)
		files = masters(kind, style)
		for name, text in files.items():
			with open(os.path.join(folder, name), "w") as handle:
				handle.write(text)
		count += len(files)
	print("cd media masters", count, "(%s)" % ", ".join(styles))


if __name__ == "__main__":
	main()
