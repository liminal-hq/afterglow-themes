#!/usr/bin/env python3
# Draw the Afterglow dialog art for ReactOS as vector masters: the About banner and the Shut Down and Log Off dialogs' background, mark and
# button strips.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
#   python3 gen_dialogs.py OUT_DIR [FONT_DIR]
#
# Writes OUT_DIR/about-banner.svg, shutdown-bg.svg, shutdown-mark.svg, shutdown-strip.svg, logoff-strip.svg and
# alternatives/shutdown-strip-mint.svg. Each master is drawn in the bitmap's own pixels (its viewBox is the stock bitmap's size) and sized
# four times larger, so render.py draws it at 4x and box-filters it down, as the logon banner is. The buttons are faces drawn by set E's Pen
# (desktop/icons/gen_e.py) with the keyline, so they are the icon set's materials. The About banner keeps the logon banner A's sky, sun and
# Afterglow wordmark (read from desktop/logon/banner-a.svg, so the two cannot drift) and outlines its two lines of small type from DejaVu
# Sans in FONT_DIR (default: the first folder that holds DejaVuSans.ttf), so no font is needed to render it. Deterministic: no randomness,
# no clock and no environment input other than the font file.
import importlib.util
import os
import re
import sys
import types

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
DESKTOP = os.path.dirname(HERE)
SCALE = 4


def load(name, path):
	spec = importlib.util.spec_from_file_location(name, path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


GEN = load("gen_e", os.path.join(DESKTOP, "icons", "gen_e.py"))
OUTLINE = load("outline", os.path.join(HERE, "outline.py"))
MATS, Pen, RR, circ, poly, mix, retune, _n = GEN.MATS, GEN.Pen, GEN.RR, GEN.circ, GEN.poly, GEN.mix, GEN.retune, GEN._n
ORANGE, RED, PURPLE, INDIGO, VOIDN, PAPER = GEN.ORANGE, GEN.RED, GEN.PURPLE, GEN.INDIGO, GEN.VOIDN, GEN.PAPER
SKY1, SKY4, SKY7, HORIZON, GLYPH, GLYPH_D, PALE, BRAND_GOLD = GEN.SKY1, GEN.SKY4, GEN.SKY7, GEN.HORIZON, GEN.GLYPH, GEN.GLYPH_D, GEN.PALE, GEN.BRAND_GOLD

# The fancy Shut Down and Log Off dialogs paint their labels with a brush of RGB(244, 244, 244) and the title in that colour, and the labels
# in RGB(38, 38, 38): compiled into msgina.dll and shell32.dll, so the panel must stay exactly this grey and the header and footer dark.
PANEL = "#f4f4f4"
HEADER_TOP, HEADER_FOOT = "#1f2554", "#262c5e"  # SKY1 and a step toward SKY4: gentle enough that the mark's own copy of it never shows a seam
FOOTER_TOP, FOOTER_FOOT = "#262c5e", "#161a40"
RULE = "#121741"  # the dark line under the header and over the footer
MINT = GEN.Mat("mint (the canvas's Stand By)", "#7be3c8", "#c4f3e6", "#5cc4a9", "#2f7d69", "mint 200 · lit mint 100 · edge mint 500")

HEAD = """<?xml version="1.0" encoding="UTF-8"?>
<!--
%s

(c) Copyright 2026 Liminal HQ, Scott Morris
SPDX-License-Identifier: Apache-2.0 OR MIT

%s
-->
"""


def document(title, note, width, height, body, defs=""):
	return (HEAD % (title, note) + '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">\n<title>%s</title>\n<defs>%s</defs>\n%s\n</svg>\n'
		% (width * SCALE, height * SCALE, width, height, title, defs, body))


# ---- the Shut Down and Log Off background (312 x 198, msgina.dll 20003 and shell32.dll 500) ------------------------------------------------
def header_gradient(gradient_id, top_y, bottom_y, top, bottom):
	return '<linearGradient id="%s" x1="0" y1="%s" x2="0" y2="%s" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (
		gradient_id, top_y, bottom_y, top, bottom)


def ink_gradient(gradient_id, width):
	return ('<linearGradient id="%s" x1="0" y1="0" x2="%s" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="%s" stop-opacity="0"/>'
		'<stop offset="0.5" stop-color="%s"/><stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>') % (gradient_id, width, ORANGE[200], ORANGE[200], ORANGE[200])


def background():
	"""Rows 0-41 the dusk header, 42 a horizon line, 43 the rule, 44-45 the gold ink line, 46-153 the panel, 154 the rule, 155 a horizon
	line and 156-197 the footer: the stock bitmap's bands, so the dialog's controls land where they always did."""
	defs = header_gradient("head", 0, 42, HEADER_TOP, HEADER_FOOT) + header_gradient("foot", 156, 198, FOOTER_TOP, FOOTER_FOOT) + ink_gradient("ink", 312)
	body = "".join([
		'<rect x="0" y="0" width="312" height="42" fill="url(#head)"/>',
		'<rect x="0" y="42" width="312" height="1" fill="%s"/>' % HORIZON,
		'<rect x="0" y="43" width="312" height="3" fill="%s"/>' % RULE,
		'<rect x="0" y="44" width="312" height="2" fill="url(#ink)"/>',
		'<rect x="0" y="46" width="312" height="108" fill="%s"/>' % PANEL,
		'<rect x="0" y="154" width="312" height="1" fill="%s"/>' % RULE,
		'<rect x="0" y="155" width="312" height="1" fill="%s"/>' % HORIZON,
		'<rect x="0" y="156" width="312" height="42" fill="url(#foot)"/>',
	])
	return document("Afterglow Shut Down and Log Off dialog background", "Master in the bitmap's pixels (312 x 198), drawn at 4x; replaces msgina.dll bitmap 20003 (IDI_DLG_BG) and\nshell32.dll bitmap 500 (IDB_DLG_BG). The panel is RGB(244, 244, 244), the colour the dialogs paint their labels with.",
		312, 198, body, defs)


# ---- the mark in the header's top right (48 x 40, msgina.dll 20002 and shell32.dll 501) ----------------------------------------------------
MARK_TOP = 2  # the mark's control sits two pixels down the header (1 dialog unit at the default font)


def mark():
	"""The Afterglow sun on its horizon, in the boot logo's language: dusk arcs, the gold half sun and the gold ink horizon, over the header's
	own gradient so it sits on the background without a seam."""
	defs = header_gradient("head", -MARK_TOP, 42 - MARK_TOP, HEADER_TOP, HEADER_FOOT)
	defs += ('<linearGradient id="horizon" x1="2" y1="0" x2="46" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="%s" stop-opacity="0"/>'
		'<stop offset="0.5" stop-color="%s"/><stop offset="1" stop-color="%s" stop-opacity="0"/></linearGradient>') % (ORANGE[200], BRAND_GOLD, ORANGE[200])
	defs += '<clipPath id="sky"><rect x="0" y="0" width="48" height="30"/></clipPath>'
	arcs = "".join('<circle cx="24" cy="30" r="%s" fill="%s"/>' % (radius, colour) for radius, colour in ((21, "#2e3468"), (17, SKY4), (13, "#5a3f6c"), (9.5, SKY7)))
	body = "".join([
		'<rect x="0" y="0" width="48" height="40" fill="url(#head)"/>',
		'<g clip-path="url(#sky)">%s<circle cx="24" cy="30" r="7" fill="%s"/><ellipse cx="22" cy="26.6" rx="2.8" ry="1.6" fill="%s" fill-opacity="0.8"/></g>' % (arcs, ORANGE[200], PALE),
		'<rect x="2" y="29.4" width="44" height="1.6" rx="0.8" fill="url(#horizon)"/>',
	])
	return document("Afterglow Shut Down and Log Off dialog mark", "Master in the bitmap's pixels (48 x 40), drawn at 4x; replaces msgina.dll bitmap 20002 (IDI_ROSLOGO_FLAG) and\nshell32.dll bitmap 501 (IDB_REACTOS_FLAG). Its ground is the header gradient of shutdown-bg.svg, two pixels down.",
		48, 40, body, defs)


# ---- the button strips (33 px cells: msgina.dll 20004, 33 x 330, and shell32.dll 502, 33 x 231) ------------------------------------------
CELL = 33


def glyph_power(colour):
	return ('<path d="M17.5 15.5 A10.5 10.5 0 1 0 30.5 15.5" fill="none" stroke="%s" stroke-width="3.8" stroke-linecap="round"/>'
		'<path d="M24 11.5 V24" fill="none" stroke="%s" stroke-width="3.8" stroke-linecap="round"/>') % (colour, colour)


def glyph_restart(colour):
	"""A circular arrow: three quarters of a ring from the top round to the upper right, its head turned back toward the start."""
	return ('<path d="M19.77 15.44 A10 10 0 1 0 32.19 18.76" fill="none" stroke="%s" stroke-width="3.8" stroke-linecap="round"/>'
		'<path d="M29.55 15 L36.48 17.22 L29.28 22.27 Z" fill="%s" stroke="%s" stroke-width="1.4" stroke-linejoin="round"/>') % (colour, colour, colour)


def glyph_sleep(colour):
	return '<path d="M27.5 12.2 A11 11 0 1 0 35.8 27.6 A8.6 8.6 0 0 1 27.5 12.2 Z" fill="%s"/>' % colour


def glyph_switch(colour):
	return ('<path d="M33 18.5 H15.5 M20 13.5 L15 18.5 L20 23.5 M15 29.5 H32.5 M28 24.5 L33 29.5 L28 34.5" fill="none" stroke="%s" stroke-width="3.4" '
		'stroke-linecap="round" stroke-linejoin="round"/>') % colour


def glyph_log_off(colour):
	return ('<path d="M22 13 H15.5 V35 H22" fill="none" stroke="%s" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>'
		'<path d="M20.5 24 H33.5 M28.5 19 L33.5 24 L28.5 29" fill="none" stroke="%s" stroke-width="3.4" stroke-linecap="round" stroke-linejoin="round"/>') % (colour, colour)


def state_material(material, state):
	"""The button's face in a state: pressed is a step darker and flat, focused (the hot state too) a step lighter, disabled greyed."""
	if state == "pressed":
		base = mix(material.base, material.edge, 0.28)
		return GEN.Mat(material.name, base, mix(material.lit, material.edge, 0.28), mix(material.nxt, material.edge, 0.28), material.edge, material.token)
	if state == "focused":
		return GEN.Mat(material.name, mix(material.base, material.lit, 0.35), PAPER[900], material.base, material.edge, material.token)
	if state == "disabled":
		grey = "#c9c9d1"
		return GEN.Mat(material.name, mix(material.base, grey, 0.7), mix(material.lit, grey, 0.7), mix(material.nxt, grey, 0.7), mix(material.edge, "#8a8a96", 0.6), material.token)
	return material


def button(index, prefix, material, glyph, ink, state):
	"""One 33 x 33 cell: the panel grey, then a rounded face of the material drawn by set E's Pen at the 32 px profile with the keyline, and the
	glyph. Pressed moves the glyph down a pixel; focused adds a pale rim inside the edge."""
	pen = Pen("%s%d" % (prefix, index), 32, keyline=True)
	face = state_material(material, state)
	outline = RR(1.5, 1.5, 45, 45, 11)
	pen.face(outline, face, band=state != "pressed")
	if state == "focused":
		pen.raw('<g clip-path="url(#%s)"><path d="%s" fill="none" stroke="%s" stroke-width="4" stroke-opacity="0.85"/></g>' % (pen.clip(RR(4.2, 4.2, 39.6, 39.6, 8.6)), RR(4.2, 4.2, 39.6, 39.6, 8.6), PALE))
	glyph_colour = mix(ink, "#9a9aa6", 0.55) if state == "disabled" else ink
	shift = 1.5 if state == "pressed" else 0
	pen.raw('<g transform="translate(0 %s)">%s</g>' % (_n(shift), glyph(glyph_colour)))
	top = index * CELL
	cell = '<rect x="0" y="%d" width="%d" height="%d" fill="%s"/>' % (top, CELL, CELL, PANEL)
	group = '<g transform="translate(0.5 %s) scale(%s)">%s</g>' % (_n(top + 0.5), _n(32 / 48), "".join(pen.out))
	return "".join(pen.defs.values()), cell + group


def strip(cells, prefix):
	defs, body = [], []
	for index, (material, glyph, ink, state) in enumerate(cells):
		cell_defs, cell_body = button(index, prefix, material, glyph, ink, state)
		defs.append(cell_defs)
		body.append(cell_body)
	return "".join(defs), "".join(body)


def shutdown_cells(sleep_material):
	"""msgina.dll's order (shutdown.c): Shut Down, pressed, focused; Restart, pressed, focused; Sleep, pressed, focused, disabled."""
	cells = []
	for material, glyph, ink in ((MATS["rose"], glyph_power, GLYPH), (MATS["gold"], glyph_restart, GLYPH_D), (sleep_material, glyph_sleep, GLYPH if sleep_material is not MINT else GLYPH_D)):
		for state in ("normal", "pressed", "focused"):
			cells.append((material, glyph, ink, state))
	cells.append((sleep_material, glyph_sleep, GLYPH if sleep_material is not MINT else GLYPH_D, "disabled"))
	return cells


def shutdown_strip(sleep_material, prefix, title, note):
	defs, body = strip(shutdown_cells(sleep_material), prefix)
	return document(title, note, CELL, 10 * CELL, body, defs)


def logoff_strip():
	"""shell32.dll's order (dialogs.cpp): Switch User, pressed, focused; Log Off, pressed, focused; Switch User disabled."""
	cells = [(MATS["violet"], glyph_switch, GLYPH, state) for state in ("normal", "pressed", "focused")]
	cells += [(MATS["gold"], glyph_log_off, GLYPH_D, state) for state in ("normal", "pressed", "focused")]
	cells.append((MATS["violet"], glyph_switch, GLYPH, "disabled"))
	defs, body = strip(cells, "l")
	return document("Afterglow Log Off dialog buttons", "Master in the bitmap's pixels (33 x 231, seven 33 px cells), drawn at 4x; replaces shell32.dll bitmap 502\n(IDB_IMAGE_STRIP): Switch User (violet) and Log Off (gold), normal, pressed and focused, then Switch User disabled.",
		CELL, 7 * CELL, body, defs)


# ---- the About banner (413 x 72, shell32.dll 131) ----------------------------------------------------------------------------------------------
SUBTITLE = "for ReactOS · unofficial remaster, not endorsed by the ReactOS project"
COPYRIGHT = "Copyright © 1996-2026 ReactOS Team & Contributors"


def find_font_dir(argument):
	candidates = [argument] if argument else ["/usr/share/fonts/TTF", "/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu", "/usr/share/fonts/dejavu-sans-fonts"]
	for folder in candidates:
		if folder and os.path.exists(os.path.join(folder, "DejaVuSans.ttf")):
			return folder
	sys.exit("gen_dialogs.py: DejaVuSans.ttf not found; pass its folder as FONT_DIR")


def about_banner(font_dir):
	"""Banner A's sky, halo, sun, dark band, gold ink line and Afterglow wordmark at 4x, with the subtitle that says what it is and is not and
	the ReactOS copyright line in the dark band, both outlined from DejaVu Sans."""
	source = open(os.path.join(DESKTOP, "logon", "banner-a.svg")).read()
	defs = re.search(r"<defs>(.*?)</defs>", source, re.S).group(1)
	scene = re.search(r"</defs>\s*(<rect.*?)\s*<path", source, re.S).group(1)
	wordmark = re.search(r'(<path d="[^"]+" fill="#ffffff"/>)', source).group(1)
	regular = OUTLINE.Font(os.path.join(font_dir, "DejaVuSans.ttf"))
	subtitle, subtitle_width = OUTLINE.text_path(regular, SUBTITLE, 30, 100, 214)
	copyright_line, copyright_width = OUTLINE.text_path(regular, COPYRIGHT, 30, 100, 274)
	if subtitle_width > 1220 or copyright_width > 1452:
		sys.exit("gen_dialogs.py: the banner text no longer fits")
	body = "\n".join([scene, wordmark, '<path d="%s" fill="%s"/>' % (subtitle, BRAND_GOLD), '<path d="%s" fill="%s"/>' % (copyright_line, VOIDN[300])])
	title = "Afterglow About banner: Afterglow for ReactOS, unofficial, with the ReactOS copyright"
	note = ("Master at 4x (1652 x 288); render down to 413 x 72 for shell32.dll bitmap 131 (IDB_REACTOS), the banner of\nthe About box (ShellAbout). The sky, sun and wordmark are logon banner A's; the subtitle and the copyright line are outlined from\nDejaVu Sans (Bitstream Vera / DejaVu font licence, which allows embedding outlines), so no font is needed to render it.")
	return HEAD % (title, note) + '<svg xmlns="http://www.w3.org/2000/svg" width="1652" height="288" viewBox="0 0 1652 288">\n<title>%s</title>\n<defs>%s</defs>\n%s\n</svg>\n' % (title, defs, body)


def main():
	if len(sys.argv) not in (2, 3):
		sys.exit("usage: gen_dialogs.py OUT_DIR [FONT_DIR]")
	out = sys.argv[1]
	os.makedirs(os.path.join(out, "alternatives"), exist_ok=True)
	files = {
		"about-banner.svg": about_banner(find_font_dir(sys.argv[2] if len(sys.argv) == 3 else None)),
		"shutdown-bg.svg": background(),
		"shutdown-mark.svg": mark(),
		"shutdown-strip.svg": shutdown_strip(MATS["violet"], "s", "Afterglow Shut Down dialog buttons (selected)",
			"Master in the bitmap's pixels (33 x 330, ten 33 px cells), drawn at 4x; replaces msgina.dll bitmap 20004\n(IDB_IMAGE_STRIP): Shut Down (rose, power), Restart (gold, the restart arrow), Sleep (violet, the moon), normal, pressed and focused,\nthen Sleep disabled."),
		"logoff-strip.svg": logoff_strip(),
		"alternatives/shutdown-strip-mint.svg": shutdown_strip(MINT, "m", "Afterglow Shut Down dialog buttons, mint Sleep (review only)",
			"Review only, not shipped: the design canvas's friendly-dialog colours (Stand By in mint), in the same layout as\nshutdown-strip.svg."),
	}
	for name, text in files.items():
		with open(os.path.join(out, name), "w") as handle:
			handle.write(text)
	print("dialog masters", len(files))


if __name__ == "__main__":
	main()
