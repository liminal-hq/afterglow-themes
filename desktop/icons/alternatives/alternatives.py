#!/usr/bin/env python3
# Review-only alternatives to Afterglow icons: keyline variants that reach 3:1 against both the classic cream window colour and the Dusk
# desktop colour. Nothing here ships until the owner picks. (The device redraws of the drive icons and My Computer were picked and ship.)
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
#   python3 alternatives.py                  rewrite the masters in this folder (keyline/, with 32/ and 16/ profiles and
#                                            hinted ID-16.svg frames where the icon has one)
#   python3 alternatives.py --review OUT_PNG render every frame at 16, 32 and 48 px and draw the review sheet: current against each
#                                            alternative at 1x and 4x, on cream and on dusk, with the measured contrast (needs rsvg-convert)
#
# The keyline variant of an icon is
# the icon itself with every material edge (the clipped inner edge set E draws at 30 to 60 %) made opaque and retuned, in its own hue, to
# a luminance of about 0.137: cream is about 0.62 and dusk about 0.006, and that band is the one that reaches 3:1 against both. Plated
# icons also get that rim on the plate. A hinted 16 px frame gets the same retune on its outer ring of pixels.
#
# Contrast is measured as in WCAG 2 against the ground, at the edge of the icon's main silhouette (pixels of at least 50 % alpha, so the
# soft contact shadow is left out). Each pixel on the silhouette's outer ring is scored with the stronger of itself and the pixel just
# inside it, because an anti-aliased curve leaves the outermost pixel part ground and the eye finds the edge one pixel in; the icon's
# score is the median over the ring, and the sheet shows the worst of its 48, 32 and 16 px frames.
import colorsys
import importlib.util
import io
import math
import os
import re
import subprocess
import sys
import types

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ICONS = os.path.dirname(HERE)
GROUNDS = (("cream", (212, 208, 200)), ("dusk", (9, 14, 42)))
TARGET = 3.0
KEY_LUMINANCE = 0.137

def load_module(name, path):
	spec = importlib.util.spec_from_file_location(name, path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


gen = load_module("gen_e", os.path.join(ICONS, "gen_e.py"))
MATS, RR, poly, circ, ring, rot, _n, FG = gen.MATS, gen.RR, gen.poly, gen.circ, gen.ring, gen.rot, gen._n, gen.FG


# ---- colour -----------------------------------------------------------------------------------------------------------------------------------
def rgb(colour):
	return tuple(int(colour[index:index + 2], 16) for index in (1, 3, 5))


def luminance(value):
	def channel(component):
		component /= 255
		return component / 12.92 if component <= 0.03928 else ((component + 0.055) / 1.055) ** 2.4
	red, green, blue = (channel(component) for component in value)
	return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast(first, second):
	high, low = sorted((first, second), reverse=True)
	return (high + 0.05) / (low + 0.05)


def retune(colour, target=KEY_LUMINANCE):
	"""The same hue and saturation at the lightness whose luminance is the target (KEY_LUMINANCE unless given)."""
	hue, lightness, saturation = colorsys.rgb_to_hls(*(component / 255 for component in rgb(colour)))
	low, high = 0.0, 1.0
	for _ in range(40):
		middle = (low + high) / 2
		value = tuple(round(component * 255) for component in colorsys.hls_to_rgb(hue, middle, saturation))
		if luminance(value) < target:
			low = middle
		else:
			high = middle
	return "#%02x%02x%02x" % tuple(round(component * 255) for component in colorsys.hls_to_rgb(hue, high, saturation))


# The dusk plate's rim is set a little lighter: on dusk it is the edge, and on cream the plate's dark body carries the contrast
PLATE_LUMINANCE = 0.19
PLATE_KEY = retune(gen.HORIZON, PLATE_LUMINANCE)
# The keyline's width in screen pixels by profile: one pixel at 48 lands on the grid, but at 32 and below it falls between pixels and
# blurs, so it is drawn wider there
KEY_WIDTH = {48: 1.5, 32: 1.67, 24: 1.5, 16: 1.5}
# At 16 px the plate's rim covers both of its edge pixels, so it takes a luminance that reaches 3:1 on both grounds by itself
PLATE_KEY_16 = retune(gen.HORIZON, 0.15)


# Hand-tuned 16 px frames for keyline variants whose scripted 16 px frame is too thin to carry a keyline
KEYLINE_16 = {
	"views": [
		"................",
		"................",
		".MMMMMMMMMMMMMM.",
		".Mm22m1111111mM.",
		".MMMMMMMMMMMMMM.",
		"................",
		".MMMMMMMMMMMMMM.",
		".Mm22m1111111mM.",
		".MMMMMMMMMMMMMM.",
		"................",
		".MMMMMMMMMMMMMM.",
		".Mm22m1111111mM.",
		".MMMMMMMMMMMMMM.",
		"................",
		"................",
		"................",
	],
	"kbdlayout": [
		"................",
		"................",
		"................",
		"NNNNNNNNNNNNNNNN",
		"NnnnnnnnnnnnnnnN",
		"Nn0n0n0n0n0n0nnN",
		"NnnnnnnnnnnnnnnN",
		"Nnn0n0n0n0n0n0nN",
		"NnnnnnnnnnnnnnnN",
		"NnnGGGGGGGGGnnnN",
		"NnnnnnnnnnnnnnnN",
		"NNNNNNNNNNNNNNNN",
		"................",
		"................",
		"................",
		"................",
	],
	"folders": [
		"................",
		".GGG............",
		".FFFFFF.........",
		".FffffF.........",
		".FFFFFF.........",
		"...~............",
		"...~....GGG.....",
		"...~....FFFFFF..",
		"...~~~~~FffffF..",
		"...~....FFFFFF..",
		"...~............",
		"...~....GGG.....",
		"...~....FFFFFF..",
		"...~~~~~FffffF..",
		"........FFFFFF..",
		"................",
	],
}


# ---- building and the keyline -------------------------------------------------------------------------------------------------------------------
def build_current(icon_id, size, prefix):
	return gen.build(icon_id, size, prefix)


EDGE_STROKE = re.compile(r'stroke="(#[0-9a-f]{6})" stroke-width="([0-9.]+)" stroke-opacity="([0-9.]+)"')
UNDER_STROKE = re.compile(r'stroke="(#[0-9a-f]{6})" stroke-opacity="([0-9.]+)" stroke-width="([0-9.]+)"')


def keyline_body(body, size, plated):
	"""Every material edge opaque, retuned and widened for the profile; a plated icon also gets the rim on its plate."""
	factor = KEY_WIDTH[size]
	unit = 48 / size if size < 48 else 1
	rim_colour = PLATE_KEY_16 if size == 16 else PLATE_KEY

	def edge(match):
		return 'stroke="%s" stroke-width="%s" stroke-opacity="1"' % (retune(match.group(1)), _n(float(match.group(2)) * factor))

	def under(match):
		widened = float(match.group(3)) + 2 * unit * (factor - 1)
		return 'stroke="%s" stroke-opacity="1" stroke-width="%s"' % (retune(match.group(1)), _n(widened))

	body = EDGE_STROKE.sub(edge, body)
	body = UNDER_STROKE.sub(under, body)
	# a rim drawn as a horizon stroke (Show desktop's screen) is the plate's rim
	body = body.replace('fill="none" stroke="%s" stroke-width="%s"/>' % (gen.HORIZON, _n(2 * unit)),
		'fill="none" stroke="%s" stroke-width="%s"/>' % (rim_colour, _n(2 * unit * factor)))
	if plated:
		plate = RR(5, 5, 38, 38, 8)
		rim = '<clipPath id="kp%d"><path d="%s"/></clipPath><g clip-path="url(#kp%d)"><path d="%s" fill="none" stroke="%s" stroke-width="%s"/></g>' % (
			size, plate, size, plate, rim_colour, _n(2 * unit * factor))
		for marker in ('<path d="%s" fill="%s"' % (plate, gen.HORIZON), '<path d="%s" fill="%s"' % (FG.rect_d(5, 5, 38, 38, 8), FG.TOK["horizon"]),
				'<path d="%s" fill="url(' % plate):
			if marker in body:
				start = body.index(marker)
				end = body.index("</g>", start) + 4 if "url(" not in marker else body.index("/>", start) + 2
				body = body[:end] + rim + body[end:]
				break
		else:
			raise SystemExit("alternatives.py: no plate found to rim")
	return body


def keyline_pixels(rects):
	"""A hinted frame with its outer ring of pixels retuned to the keyline band."""
	cells = {(int(x), int(y)): colour for x, y, colour in re.findall(r'<rect x="(\d+)" y="(\d+)" width="1" height="1" fill="(#[0-9a-f]{6})"/>', rects)}
	out = []
	for (x, y), colour in sorted(cells.items(), key=lambda item: (item[0][1], item[0][0])):
		outer = any((x + dx, y + dy) not in cells for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
		target = PLATE_LUMINANCE if luminance(rgb(colour)) < 0.08 else KEY_LUMINANCE  # dark faces (plates, dusk) take the lighter rim
		out.append('<rect x="%d" y="%d" width="1" height="1" fill="%s"/>' % (x, y, retune(colour, target) if outer else colour))
	return "".join(out)


def device_pixels(icon_id, grids):
	colours = {}
	for letter, name in {"g": "gold", "f": "goldl", "p": "paper", "m": "front", "n": "back", "d": "dusk", "v": "violet"}.items():
		colours[letter], colours[letter.upper()] = MATS[name].base, MATS[name].px_edge()
	colours.update({digit: colour for digit, colour in gen.PXD.items() if digit != "e"})
	colours.update({"-": gen.VOIDN[300], "=": gen.INDIGO[600], "~": gen.HORIZON})
	return "".join('<rect x="%d" y="%d" width="1" height="1" fill="%s"/>' % (x, y, colours[character])
		for y, row in enumerate(grids[icon_id]) for x, character in enumerate(row) if character != ".")


def is_plated(icon_id):
	return gen.I[icon_id][0] == "tile" or icon_id == "folderopts"


# ---- writing ---------------------------------------------------------------------------------------------------------------------------------------
def variants():
	"""(folder, id, title, build(size) -> (defs, body), hinted() -> rects or None) for every alternative."""
	out = []
	for icon_id in gen.I:
		if icon_id in KEYLINE_16:
			hinted = lambda icon_id=icon_id: keyline_pixels(device_pixels(icon_id, KEYLINE_16))
		elif icon_id in gen.HINTED:
			hinted = lambda icon_id=icon_id: keyline_pixels(gen.hinted(icon_id))
		else:
			hinted = None
		out.append(("keyline", icon_id, "%s, keyline (review only)" % gen.LABEL[icon_id],
			lambda size, icon_id=icon_id: (lambda built: (built[0], keyline_body(built[1], size, is_plated(icon_id))))(build_current(icon_id, size, "al-%s-%d" % (icon_id, size))),
			hinted))
	return out


def write_masters():
	count = 0
	for folder, icon_id, title, build, hinted in variants():
		for size, path in ((48, "%s.svg"), (32, "32/%s.svg"), (16, "16/%s.svg")):
			os.makedirs(os.path.join(HERE, folder, os.path.dirname(path)), exist_ok=True)
			defs, body = build(size)
			profile = "48 master" if size == 48 else "%d px" % size
			with open(os.path.join(HERE, folder, path % icon_id), "w") as handle:
				handle.write(gen.standalone(body, defs, 48, "%s, %s (%s)" % (icon_id, title, profile)))
			count += 1
		if hinted:
			with open(os.path.join(HERE, folder, "%s-16.svg" % icon_id), "w") as handle:
				handle.write(gen.standalone(hinted(), "", 16, "%s, %s (hinted 16 px)" % (icon_id, title), True))
			count += 1
	return count


# ---- the review sheet -------------------------------------------------------------------------------------------------------------------------------
def rasterise(path, size):
	data = subprocess.run(["rsvg-convert", "--format", "png", "--width", str(size), "--height", str(size), path], check=True, stdout=subprocess.PIPE).stdout
	from PIL import Image
	return Image.open(io.BytesIO(data)).convert("RGBA")


def frames(folder, icon_id):
	"""48, 32 and 16 px frames: folder None is the shipped icon."""
	base = os.path.join(ICONS, "svg") if folder is None else os.path.join(HERE, folder)
	hinted = os.path.join(base, icon_id + "-16.svg")
	return {48: rasterise(os.path.join(base, icon_id + ".svg"), 48), 32: rasterise(os.path.join(base, "32", icon_id + ".svg"), 32),
		16: rasterise(hinted if os.path.exists(hinted) else os.path.join(base, "16", icon_id + ".svg"), 16)}


def measure(image, ground):
	"""The contrast of the main silhouette's edge against the ground (see the header)."""
	width, height = image.size
	pixels = image.load()
	shape = {(x, y) for y in range(height) for x in range(width) if pixels[x, y][3] >= 128}
	ground_luminance = luminance(ground)

	def score(x, y):
		red, green, blue, alpha = pixels[x, y]
		share = alpha / 255
		return contrast(luminance(tuple(component * share + base * (1 - share) for component, base in zip((red, green, blue), ground))), ground_luminance)

	steps = ((1, 0), (-1, 0), (0, 1), (0, -1))
	values = []
	for x, y in shape:
		outside = [(dx, dy) for dx, dy in steps if (x + dx, y + dy) not in shape]
		if not outside:
			continue
		best = score(x, y)
		for dx, dy in outside:
			inner = (x - dx, y - dy)
			if inner in shape:
				best = max(best, score(*inner))
		values.append(best)
	values.sort()
	return values[len(values) // 2]


def worst(sizes, ground):
	return min(measure(sizes[size], ground) for size in (48, 32, 16))


def option_tile(sizes, ground):
	"""One option on one ground: 48, 32 and 16 px at 1x, then the 16 px frame at 4x."""
	from PIL import Image
	tile = Image.new("RGBA", (178, 72), ground + (255,))
	tile.alpha_composite(sizes[48], (4, 12))
	tile.alpha_composite(sizes[32], (56, 20))
	tile.alpha_composite(sizes[16], (92, 28))
	tile.alpha_composite(sizes[16].resize((64, 64), Image.NEAREST), (112, 4))
	return tile.convert("RGB")


def review(out_path):
	from PIL import Image, ImageDraw, ImageFont
	font, small, heading = ImageFont.load_default(size=13), ImageFont.load_default(size=11), ImageFont.load_default(size=20)
	ink, dim, gold, bad, good = (224, 224, 224), (124, 135, 150), (255, 208, 142), (244, 63, 94), (134, 239, 172)
	scores = {}
	for icon_id in gen.I:
		sizes = frames(None, icon_id)
		scores[icon_id] = sizes, {name: worst(sizes, ground) for name, ground in GROUNDS}
	below = [icon_id for icon_id in gen.I if min(scores[icon_id][1].values()) < TARGET]
	option_width, block_height, margin = 236, 182, 24
	pair_width = 2 * option_width + 150
	width = margin * 2 + 3 * pair_width
	keyline_rows = (len(below) + 2) // 3
	height = 160 + 30 + keyline_rows * block_height + 30
	sheet = Image.new("RGB", (width, height), (12, 12, 16))
	draw = ImageDraw.Draw(sheet)
	draw.text((margin, 18), "Afterglow icon alternatives · review only, nothing here ships until picked", font=heading, fill=gold)
	lines = [
		"Each option: 48, 32 and 16 px at 1x, then the 16 px frame at 4x; on the classic cream window colour (top) and the Dusk desktop colour (bottom).",
		"Number: WCAG 2 contrast of the main silhouette's edge against the ground, the worst of the 48, 32 and 16 px frames. 3:1 is the target for",
		"graphical objects; green meets it. Keyline: the same icon with its",
		"material edges made opaque and retuned in their own hue to the luminance band that reaches 3:1 on both grounds; plates get the rim too.",
	]
	for index, line in enumerate(lines):
		draw.text((margin, 50 + index * 17), line, font=small, fill=dim)

	def option(x, y, name, folder, icon_id, highlight):
		sizes = scores[icon_id][0] if folder is None else frames(folder, icon_id)
		draw.text((x, y), name, font=small, fill=gold if highlight else ink)
		for band, (ground_name, ground) in enumerate(GROUNDS):
			top = y + 16 + band * 76
			sheet.paste(option_tile(sizes, ground), (x, top))
			value = worst(sizes, ground)
			draw.text((x + 184, top + 28), "%.1f:1" % value, font=font, fill=good if value >= TARGET else bad)

	y = 140
	draw.text((margin, y), "Every icon below 3:1 on either ground: current and keyline (%d icons)" % len(below), font=font, fill=gold)
	y += 30
	for index, icon_id in enumerate(below):
		x = margin + (index % 3) * pair_width
		top = y + (index // 3) * block_height
		draw.text((x, top + 18), gen.LABEL[icon_id][:20], font=font, fill=ink)
		draw.text((x, top + 36), icon_id, font=small, fill=dim)
		option(x + 140, top, "current", None, icon_id, False)
		option(x + 140 + option_width, top, "keyline", "keyline", icon_id, True)
	sheet.save(out_path, optimize=True)
	report = {icon_id: scores[icon_id][1] for icon_id in gen.I}
	return len(below), len(below), report


def main():
	if len(sys.argv) == 3 and sys.argv[1] == "--review":
		rows, below, report = review(sys.argv[2])
		print("review sheet", rows, "icons,", below, "below 3:1")
		for name, _ in GROUNDS:
			ranked = sorted(report.items(), key=lambda item: item[1][name])
			print(name, "worst:", ", ".join("%s %.2f" % (icon_id, values[name]) for icon_id, values in ranked[:12]))
			print(name, "below 3:1:", sum(1 for values in report.values() if values[name] < TARGET))
	elif len(sys.argv) == 1:
		print("alternative masters", write_masters())
	else:
		sys.exit("usage: alternatives.py [--review OUT_PNG]")


if __name__ == "__main__":
	main()
