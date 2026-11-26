#!/usr/bin/env python3
# Afterglow icons v2: the programs, applets, shell items, drives, file types, toolbar glyphs and tray states set E did not draw.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# Not run on its own: gen_e.py loads this file and calls register() with its own namespace, so every icon here is drawn by set E's Pen
# with the same materials, profiles, plate, keylines and contact shadows, and gen_e.py still writes every master and the sheet. The new
# special folders (Favourites, Recent, Programs) add their emblems to folders_g.py's emblem tables, so they are the M1 folder exactly.
# Deterministic: no randomness, no clock, no environment input.
import math

# Filled in by register(): the helpers and colours of gen_e.py, under the names set E uses.
SHARED = ("FG", "M1", "MATS", "SKY", "SHADOW", "ORANGE", "RED", "PURPLE", "VOIDN", "INDIGO", "PAPER", "BRAND_GOLD", "PALE", "SKY1", "SKY4", "SKY7",
	"HORIZON", "DARK", "LINE", "GLYPH", "GLYPH_D", "RR", "poly", "rot", "circ", "ring", "page", "bars", "globe", "gear", "drive", "window", "keys",
	"arrow_small", "mix", "_n", "Pen", "plate", "monitor", "ellipse_d")

ICONS = []  # (id, kind, tier, draw, label, group)
NEW_GROUP_AFTER = ("Programs", "Desktop and shell")  # the one new sheet group, and the group it follows


def icon(icon_id, kind, tier, label, group):
	def register_draw(draw):
		ICONS.append((icon_id, kind, tier, draw, label, group))
		return draw
	return register_draw


# ---- shared drawings ----------------------------------------------------------------------------------------------------------------------------
def cube(pen, centre_x, centre_y, half_width, material):
	"""An isometric block: the silhouette is one face (so it takes the edge), then the lit top and the shaded right side are laid flat on it."""
	height = half_width * 1.15
	top_y = centre_y - height
	points = [(centre_x, top_y - half_width * 0.5), (centre_x + half_width, top_y), (centre_x + half_width, top_y + height),
		(centre_x, top_y + height + half_width * 0.5), (centre_x - half_width, top_y + height), (centre_x - half_width, top_y)]
	pen.face(poly([(x, y, 1.2) for x, y in points]), material, band=False)
	pen.fill(poly([(centre_x, top_y - half_width * 0.5 + 0.6, 0.8), (centre_x + half_width - 0.9, top_y, 0.6), (centre_x, top_y + half_width * 0.5 - 0.3, 0.6),
		(centre_x - half_width + 0.9, top_y, 0.6)]), material.lit)
	pen.fill(poly([(centre_x + 0.4, top_y + half_width * 0.5 + 0.3, 0.4), (centre_x + half_width - 0.9, top_y + 0.6, 0.6),
		(centre_x + half_width - 0.9, top_y + height - 0.4, 0.8), (centre_x + 0.4, top_y + height + half_width * 0.5 - 0.9, 0.6)]), mix(material.base, material.edge, 0.3))


def star_d(centre_x, centre_y, outer, inner, corner=0.9):
	points = []
	for index in range(10):
		angle = math.radians(-90 + index * 36)
		radius = outer if index % 2 == 0 else inner
		points.append((centre_x + radius * math.cos(angle), centre_y + radius * math.sin(angle), corner if index % 2 == 0 else corner * 0.5))
	return poly(points)


def bolt_d(scale=1.0, offset_x=0.0, offset_y=0.0):
	points = [(26.5, 11), (17, 26.5), (23, 26.5), (21.5, 37), (31.5, 21), (25.5, 21)]
	return poly([(offset_x + 24 + (x - 24) * scale, offset_y + 24 + (y - 24) * scale, 0.5) for x, y in points], 0.5)


def badge(pen, centre_x, centre_y, radius, material, mark):
	"""A small round badge at the right of an object, clear of the shortcut corner: plus, minus, cross, check or eject."""
	pen.face(circ(centre_x, centre_y, radius), material, band=False)
	ink = GLYPH_D if material is MATS["gold"] or material is MATS["goldl"] else GLYPH
	arm = radius * 0.5
	width = max(1.8, radius * 0.36)
	if mark == "plus":
		pen.line("M%s %s H%s M%s %s V%s" % (_n(centre_x - arm), _n(centre_y), _n(centre_x + arm), _n(centre_x), _n(centre_y - arm), _n(centre_y + arm)), ink, width)
	elif mark == "minus":
		pen.line("M%s %s H%s" % (_n(centre_x - arm), _n(centre_y), _n(centre_x + arm)), ink, width)
	elif mark == "cross":
		arm *= 0.85
		pen.line("M%s %s L%s %s M%s %s L%s %s" % (_n(centre_x - arm), _n(centre_y - arm), _n(centre_x + arm), _n(centre_y + arm), _n(centre_x + arm), _n(centre_y - arm),
			_n(centre_x - arm), _n(centre_y + arm)), ink, width)
	elif mark == "check":
		pen.line("M%s %s L%s %s L%s %s" % (_n(centre_x - arm), _n(centre_y + 0.2), _n(centre_x - arm * 0.25), _n(centre_y + arm * 0.75), _n(centre_x + arm),
			_n(centre_y - arm * 0.7)), ink, width)
	elif mark == "eject":
		pen.fill(poly([(centre_x, centre_y - arm * 1.05, 0.4), (centre_x + arm, centre_y + arm * 0.15, 0.4), (centre_x - arm, centre_y + arm * 0.15, 0.4)], 0.4), ink)
		pen.fill(RR(centre_x - arm, centre_y + arm * 0.45, 2 * arm, arm * 0.5, 0.4), ink)


def card(pen, centre_x, centre_y, angle, material, corner=3):
	outline = rot([(centre_x - 9, centre_y - 13), (centre_x + 9, centre_y - 13), (centre_x + 9, centre_y + 13), (centre_x - 9, centre_y + 13)], angle, centre_x, centre_y)
	pen.face(poly(outline, corner), MATS[material])
	return outline


def clipboard(pen, x, y, width, height):
	"""A gold board with a paper sheet and a steel clip."""
	pen.face(RR(x, y, width, height, 3), MATS["goldl"])
	pen.face(RR(x + 3, y + 5, width - 6, height - 8, 1.5), MATS["paper"], band=False)
	pen.face(RR(x + width / 2 - 6, y - 2.5, 12, 6.5, 2.2), MATS["back"])
	pen.fill(RR(x + width / 2 - 2.5, y - 1, 5, 2, 1), VOIDN[500])


def speaker(pen):
	pen.shadow(5, 23, 39, SHADOW["lift"])
	pen.face(poly([(5, 18.5, 2), (13, 18.5, 0.8), (23, 10, 1.5), (23, 38, 1.5), (13, 29.5, 0.8), (5, 29.5, 2)]), MATS["front"])


def flash_stick(pen, x, y, scale=1.0):
	"""A removable flash drive standing up: steel plug at the top, light body, gold label and a lit diode."""
	def box(left, top, width, height, corner):
		return RR(x + left * scale, y + top * scale, width * scale, height * scale, corner * scale)
	pen.face(box(4.5, 0, 11, 9, 1.5), MATS["back"], band=False)
	pen.fill(box(7, 2.5, 2.4, 2.4, 0.4), VOIDN[500])
	pen.fill(box(10.6, 2.5, 2.4, 2.4, 0.4), VOIDN[500])
	pen.face(box(0, 7.5, 20, 28, 4), MATS["front"])
	pen.face(box(4, 14, 12, 12, 2), MATS["gold"], band=False)
	pen.fill(box(8.5, 29.5, 3, 3, 1.5), ORANGE[200])


def network_drive(pen):
	pen.shadow(5, 43, 43, SHADOW["body"])
	pen.line("M24 30 V35.5 M11 35.5 H37", VOIDN[300], 2.4, MATS["back"])
	drive(pen, 7)
	pen.face(RR(5, 38.5, 12, 4.5, 1.6), MATS["gold"], band=False)
	pen.face(RR(20, 33.5, 8, 4.5, 1.6), MATS["back"], band=False)


def battery(pen, level=None, charging=False, fault=False):
	"""The tray battery: a light shell, a dark well, and a gold charge filled to level fifths (rose at one fifth and below)."""
	pen.shadow(5, 41, 35.5, SHADOW["lift"])
	pen.face(RR(39.5, 19.5, 4, 10, 1.6), MATS["back"], band=False)
	pen.face(RR(4, 13, 37, 23, 4), MATS["front"])
	pen.fill(RR(8, 17, 29, 15, 2), DARK)
	if level:
		fill_width = 29 * level / 5
		pen.face(RR(8, 17, fill_width, 15, 2), MATS["rose"] if level <= 1 else MATS["gold"], band=False)
	if charging:
		pen.line("M26 12.5 L18.5 25 H25 L21.5 36.5", GLYPH, 2.6)
		pen.face(bolt_d(0.62, -1.5, 0.5), MATS["goldl"], band=False)
	if fault:
		pen.line("M17 19.5 L28 29.5 M28 19.5 L17 29.5", RED[200], 3.2)


def folder_with(size, prefix, extra):
	"""The M1 closed folder from folders_g.py with a Pen drawing laid over it (same size profile, its own prefix)."""
	folder_defs, folder_body = FG.icon(M1, "folder", size, prefix)
	pen = Pen(prefix + "x", size)
	extra(pen)
	return folder_defs + "".join(pen.defs.values()), folder_body + "".join(pen.out)


# ---- programs ---------------------------------------------------------------------------------------------------------------------------------------
@icon("calc", "tile", "tile", "Calculator", "Programs")
def draw_calculator(pen):
	pen.face(RR(13, 8.5, 22, 31, 3), MATS["front"])
	pen.fill(RR(15.8, 11.5, 16.4, 7, 1.2), DARK)
	pen.fill(RR(23.5, 14, 6.5, 2.2, 1.1), ORANGE[200])
	for row in range(3):
		for column in range(3):
			pen.fill(RR(16.2 + column * 5.6, 21.5 + row * 5.6, 4.2, 3.8, 1), INDIGO[300])
	pen.face(RR(27.4, 32.7, 4.2, 3.8, 1), MATS["gold"], band=False, edge=False)


@icon("paint", "tile", "tile", "Paint", "Programs")
def draw_paint(pen):
	pen.face(RR(9.5, 10, 24, 22, 2.5), MATS["paper"])
	pen.fill("M13 26 C14 19 20 16 24 19 C27 21.5 22 25 26 27.5 C28 29 22 30 16.5 29 C14.2 28.6 12.8 27.5 13 26 Z", PURPLE[300])
	pen.fill(circ(25.5, 15.8, 2.6), RED[200])
	pivot = (32, 22)
	handle = rot([(30, 9), (34, 9), (34, 21.5), (30, 21.5)], 40, *pivot)
	pen.face(poly(handle, 1.8), MATS["dusk"])
	ferrule = rot([(29.6, 21), (34.4, 21), (34.4, 26.5), (29.6, 26.5)], 40, *pivot)
	pen.face(poly(ferrule, 0.8), MATS["back"], band=False)
	tip = rot([(29.6, 26, 0.5), (34.4, 26, 0.5), (32, 34, 1.2)], 40, *pivot)
	pen.face(poly(tip), MATS["gold"], band=False)


@icon("regedit", "tile", "tile", "Registry Editor", "Programs")
def draw_registry_editor(pen):
	cube(pen, 17.5, 31, 7.5, MATS["front"])
	cube(pen, 31, 31, 7.5, MATS["violet"])
	cube(pen, 24.2, 20.5, 7.5, MATS["gold"])


@icon("taskmgr", "tile", "tile", "Task Manager", "Programs")
def draw_task_manager(pen):
	window(pen, 9, 10, 30, 28, MATS["dusk"], 7)
	pen.fill(RR(12, 20, 24, 15, 1.5), DARK)
	for x in (18, 24, 30):
		pen.fill(RR(x - 0.4, 20.5, 0.8, 14, 0.4), INDIGO[700])
	pen.line("M13.5 31 L18 27.5 L21.5 30 L26 23.5 L29.5 27 L34.5 24", ORANGE[200], 2.2)


@icon("wordpad", "tile", "tile", "WordPad", "Programs")
def draw_wordpad(pen):
	pen.face(RR(10, 8.5, 22, 30, 2.5), MATS["paper"])
	pen.face(RR(13.5, 12.5, 10, 4, 1.4), MATS["gold"], band=False)
	bars(pen, 13.5, 20, [15, 15, 10, 13], 4.4, 2)
	body = rot([(32.5, 12), (37, 12), (37, 33), (32.5, 33)], 28, 34.75, 22.5)
	pen.face(poly(body, 1.6), MATS["dusk"])
	nib = rot([(32.5, 33, 0.4), (37, 33, 0.4), (34.75, 39.5, 0.8)], 28, 34.75, 22.5)
	pen.face(poly(nib), MATS["gold"], band=False)


@icon("charmap", "tile", "tile", "Character Map", "Programs")
def draw_character_map(pen):
	pen.face(RR(9, 9, 26, 26, 3), MATS["front"])
	for row in range(3):
		for column in range(3):
			pen.fill(RR(12.5 + column * 7, 12.5 + row * 7, 5, 5, 1), INDIGO[300])
	pen.face(RR(24, 23, 15, 16, 2.5), MATS["gold"])
	pen.line("M27.5 35.5 L31.5 26 L35.5 35.5 M29 32 H34", GLYPH_D, 2)


@icon("clipbrd", "tile", "tile", "Clipboard Viewer", "Programs")
def draw_clipboard_viewer(pen):
	clipboard(pen, 12, 11, 24, 28)
	bars(pen, 18, 21, [12, 12, 8], 4.6, 2)


@icon("winmine", "tile", "tile", "Minesweeper", "Programs")
def draw_minesweeper(pen):
	pen.face(RR(9, 9, 30, 30, 3), MATS["front"])
	pen.line("M24 12.5 V35.5 M12.5 24 H35.5 M16 16 L32 32 M32 16 L16 32", SKY4, 2.4)
	pen.face(circ(24, 24, 7.5), MATS["dusk"])
	pen.fill(circ(21.6, 21.6, 1.9), PAPER[900])


@icon("sol", "tile", "tile", "Solitaire", "Programs")
def draw_solitaire(pen):
	back_card = card(pen, 20.5, 23, -12, "violet")
	pen.raw('<g clip-path="url(#%s)">' % pen.clip(poly(back_card, 3)))
	for index in range(-3, 4):
		pen.line("M%s 6 L%s 40" % (_n(10 + index * 6), _n(30 + index * 6)), PURPLE[200], 1.2)
	pen.raw("</g>")
	card(pen, 27.5, 25, 9, "paper")
	pen.fill("M27.5 31 C21 26 22.5 19.5 27.5 22.5 C32.5 19.5 34 26 27.5 31 Z", RED[200])


@icon("spider", "tile", "tile", "Spider Solitaire", "Programs")
def draw_spider_solitaire(pen):
	card(pen, 20.5, 23, -12, "violet")
	card(pen, 27.5, 25, 9, "paper")
	legs = "M22 20 L25 23 M21 25 L25 25 M22 30 L25 27 M33 20 L30 23 M34 25 L30 25 M33 30 L30 27"
	pen.line(legs, SKY1, 1.5)
	pen.fill(circ(27.5, 25, 3.6), SKY1)
	pen.fill(circ(27.5, 20.4, 2), SKY1)
	pen.fill(circ(26.4, 24, 0.9), ORANGE[200])


@icon("osk", "tile", "tile", "On-Screen Keyboard", "Programs")
def draw_on_screen_keyboard(pen):
	pen.face(RR(20.5, 30, 7, 5, 1), MATS["back"], band=False)
	pen.face(RR(14.5, 34, 19, 4, 1.6), MATS["back"])
	pen.face(RR(8, 9, 32, 23, 3), MATS["front"])
	pen.sky(RR(11, 12, 26, 17, 1.5))
	keys(pen, 13, 14.5, 4, 2, 4.4, 3, 6.2, 4.6, INDIGO[200])
	pen.fill(RR(16, 24.2, 16, 2.6, 1), ORANGE[200])


@icon("magnify", "tile", "tile", "Magnifier", "Programs")
def draw_magnifier(pen):
	handle = rot([(19, 30), (25, 30), (25, 44), (19, 44)], -45, 20, 20)
	pen.face(poly(handle, 2.8), MATS["dusk"])
	pen.face(ring(21, 21, 12.5, 9), MATS["back"])
	pen.face(circ(21, 21, 9), MATS["glass"], band=False)
	pen.line("M16.5 21 H25.5 M21 16.5 V25.5", ORANGE[500], 2.6)


@icon("mstsc", "tile", "tile", "Remote Desktop Connection", "Programs")
def draw_remote_desktop(pen):
	pen.face(RR(20.5, 30, 7, 5, 1), MATS["back"], band=False)
	pen.face(RR(14.5, 34, 19, 4, 1.6), MATS["back"])
	pen.face(RR(8, 9, 32, 23, 3), MATS["front"])
	pen.sky(RR(11, 12, 26, 17, 1.5))
	pen.face(RR(14, 15.5, 13, 10, 1.4), MATS["front"], band=False)
	pen.fill(RR(14, 15.5, 13, 3, 1.4), HORIZON)
	pen.line("M27 20 C31 20 33 18 33.5 14.5", ORANGE[200], 2.2)
	pen.fill(poly([(30.5, 15.5, 0.4), (33.6, 11.5, 0.4), (36.5, 15.5, 0.4)], 0.4), ORANGE[200])


@icon("mplay32", "tile", "tile", "Media Player", "Programs")
def draw_media_player(pen):
	pen.face(RR(9, 9, 30, 30, 3), MATS["front"])
	pen.sky(RR(12, 12, 24, 17, 1.5))
	pen.face(poly([(20.5, 15, 1), (29.5, 20.5, 1), (20.5, 26, 1)]), MATS["gold"], band=False)
	pen.fill(RR(12, 32, 24, 3, 1.5), INDIGO[300])
	pen.fill(RR(12, 32, 13, 3, 1.5), ORANGE[200])


@icon("sndrec32", "tile", "tile", "Sound Recorder", "Programs")
def draw_sound_recorder(pen):
	pen.line("M15.5 23 C15.5 34 32.5 34 32.5 23 M24 31.5 V37.5", VOIDN[300], 2.4, MATS["back"])
	pen.face(RR(17, 36, 14, 3.6, 1.5), MATS["back"])
	pen.face(RR(18.5, 8.5, 11, 20, 5.5), MATS["front"])
	for y in (13, 16.5, 20):
		pen.fill(RR(21, y, 6, 1.6, 0.8), INDIGO[400])
	pen.face(circ(34.5, 12.5, 3.8), MATS["rose"], band=False)


@icon("eventvwr", "tile", "tile", "Event Viewer", "Programs")
def draw_event_viewer(pen):
	pen.face(RR(10, 8.5, 28, 31, 3), MATS["paper"])
	pen.fill(RR(10, 8.5, 28, 6, 3), HORIZON)
	pen.fill(RR(10, 11.5, 28, 3, 0.01), HORIZON)
	for row, colour in enumerate((PURPLE[300], ORANGE[200], RED[200], PURPLE[300])):
		y = 19 + row * 5.2
		pen.fill(circ(15, y + 1, 1.8), colour)
		pen.fill(RR(19, y, 15 - (row % 2) * 4, 2, 1), LINE)


@icon("msconfig", "tile", "tile", "System Configuration", "Programs")
def draw_system_configuration(pen):
	pen.face(RR(9.5, 8.5, 22, 29, 2.5), MATS["paper"])
	for row in range(3):
		y = 13.5 + row * 7
		pen.fill(RR(13, y, 4.5, 4.5, 1), INDIGO[300])
		pen.fill(RR(20, y + 1.3, 8, 2, 1), LINE)
	pen.line("M13.6 15.8 L15.2 17.4 L18.6 13.2 M13.6 22.8 L15.2 24.4 L18.6 20.2", HORIZON, 1.6)
	gear(pen, 32, 32.5, 8.2, 6.2, 2.4)


@icon("dxdiag", "tile", "tile", "ReactX Diagnostic", "Programs")
def draw_reactx_diagnostic(pen):
	pen.face(circ(21.5, 21.5, 12.5), MATS["violet"])
	sparkle = [(21.5 + radius * math.cos(math.radians(-90 + index * 45)), 21.5 + radius * math.sin(math.radians(-90 + index * 45)), 0.6)
		for index, radius in enumerate((8.5, 2.6) * 4)]
	pen.face(poly(sparkle), MATS["goldl"], band=False)
	handle = rot([(33.5, 37), (37.5, 37), (37.5, 44.5), (33.5, 44.5)], -45, 33, 33)
	pen.face(poly(handle, 1.8), MATS["dusk"])
	pen.face(ring(32, 32, 6.8, 4.4), MATS["back"], band=False)
	pen.face(circ(32, 32, 4.4), MATS["glass"], band=False)


@icon("servman", "tile", "tile", "Service Manager", "Programs")
def draw_service_manager(pen):
	for y in (9, 18.5, 28):
		pen.face(RR(9, y, 26, 8, 2.4), MATS["front"])
		pen.fill(RR(12, y + 2.5, 3, 3, 1), ORANGE[200])
		pen.fill(RR(17.5, y + 3, 13, 2, 1), LINE)
	gear(pen, 33.5, 32.5, 8.2, 6.2, 2.4)


@icon("devmgmt", "tile", "tile", "Device Manager", "Programs")
def draw_device_manager(pen):
	pen.face(RR(16, 27, 6, 4.5, 1), MATS["back"], band=False)
	pen.face(RR(11, 30.5, 16, 3.6, 1.4), MATS["back"])
	pen.face(RR(8, 9, 26, 19.5, 3), MATS["front"])
	pen.sky(RR(10.8, 11.8, 20.4, 13.9, 1.4))
	for offset in (-3, 0, 3):
		pen.fill(RR(32.6 + offset - 0.8, 24.5, 1.6, 3.5, 0.8), VOIDN[300])
		pen.fill(RR(32.6 + offset - 0.8, 37.5, 1.6, 3.5, 0.8), VOIDN[300])
	pen.face(RR(26.5, 27, 12.5, 12, 2), MATS["gold"])
	pen.fill(RR(30, 30.5, 5.4, 5, 1), ORANGE[400])


@icon("utilman", "tile", "tile", "Utility Manager", "Programs")
def draw_utility_manager(pen):
	pen.face(circ(21, 12.5, 3.8), MATS["gold"], band=False)
	pen.face(poly([(10.5, 18, 1.4), (31.5, 18, 1.4), (31.5, 21.6, 1.4), (23.8, 21.6, 0.8), (23.8, 27, 0.8), (27.4, 34.5, 1.1), (23.8, 34.5, 1), (21, 29, 0.8),
		(18.2, 34.5, 1), (14.6, 34.5, 1.1), (18.2, 27, 0.8), (18.2, 21.6, 0.8), (10.5, 21.6, 1.4)]), MATS["front"])
	gear(pen, 32.5, 32.5, 7.6, 5.8, 2.2)


@icon("wusa", "tile", "tile", "Update installer", "Programs")
def draw_update_installer(pen):
	pen.face(RR(10, 17, 28, 21, 2.5), MATS["back"])
	pen.face(RR(8.5, 13, 31, 7, 2.2), MATS["front"])
	pen.fill(RR(21.5, 13, 5, 25, 0.6), mix(VOIDN[300], VOIDN[400], 0.5))
	pen.face(poly([(20.5, 7, 1), (27.5, 7, 1), (27.5, 15, 0.5), (32, 15, 1), (24, 23.5, 1.2), (16, 15, 1), (20.5, 15, 0.5)]), MATS["gold"])


def draw_explorer(size, prefix):
	def lens(pen):
		handle = rot([(35, 36.5), (39.5, 36.5), (39.5, 46), (35, 46)], -45, 34, 34)
		pen.face(poly(handle, 2), MATS["dusk"])
		pen.face(ring(32.5, 30.5, 9, 6.4), MATS["back"])
		pen.face(circ(32.5, 30.5, 6.4), MATS["glass"], band=False)
	return folder_with(size, prefix, lens)


ICONS.append(("explorer", "built", "body", draw_explorer, "ReactOS Explorer", "Programs"))


# ---- Control Panel applets ----------------------------------------------------------------------------------------------------------------------
@icon("joystick", "tile", "tile", "Game Controllers", "Control Panel applets")
def draw_game_controllers(pen):
	pen.line("M24 29 L24 17", VOIDN[300], 3.4, MATS["back"])
	pen.face(poly([(13, 29, 2.5), (35, 29, 2.5), (38, 38, 2.5), (10, 38, 2.5)]), MATS["front"])
	pen.face(circ(24, 14.5, 5.5), MATS["gold"])
	pen.face(circ(32, 33.2, 2.2), MATS["rose"], band=False, edge=False)


@icon("telephon", "tile", "tile", "Phone and Modem", "Control Panel applets")
def draw_phone_and_modem(pen):
	pen.face(poly([(15, 20, 2.5), (33, 20, 2.5), (37.5, 37, 3), (10.5, 37, 3)]), MATS["front"])
	for row in range(3):
		for column in range(3):
			pen.fill(RR(18.5 + column * 4.2, 24 + row * 3.8, 2.6, 2.2, 0.8), INDIGO[400])
	pen.face("M9 17 C9 10.5 39 10.5 39 17 L39 19.5 Q39 21 37.5 21 L32.5 21 Q31 21 31 19.5 L31 17.5 C27 16 21 16 17 17.5 L17 19.5 Q17 21 15.5 21 "
		"L10.5 21 Q9 21 9 19.5 Z", MATS["gold"])


@icon("usrmgr", "tile", "tile", "User Accounts", "Control Panel applets")
def draw_user_accounts(pen):
	pen.face(circ(29.5, 15.5, 4.8), MATS["back"], band=False)
	pen.face("M20.5 31 C20.5 25 25 22 29.5 22 C34 22 38.5 25 38.5 31 V32 H20.5 Z", MATS["back"])
	pen.face(circ(19.5, 19.5, 5.6), MATS["gold"], band=False)
	pen.face("M9 37 C9 30 14 26.5 19.5 26.5 C25 26.5 30 30 30 37 V38 H9 Z", MATS["front"])


# ---- shell and Start menu -----------------------------------------------------------------------------------------------------------------------
def emblem_star(emblem, flap, centre_x, centre_y):
	return '<path d="%s" fill="%s"/>' % (star_d(centre_x, centre_y + 0.5, 7.6, 3.3, 0.9), emblem)


def emblem_clock(emblem, flap, centre_x, centre_y):
	return ('<circle cx="%s" cy="%s" r="6.8" fill="%s"/>' % (_n(centre_x), _n(centre_y), emblem)
		+ '<path d="M%s %s V%s H%s" fill="none" stroke="%s" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>' % (
			_n(centre_x), _n(centre_y - 4.2), _n(centre_y), _n(centre_x + 3.4), flap))


def emblem_grid(emblem, flap, centre_x, centre_y):
	return "".join('<path d="%s" fill="%s"/>' % (FG.rect_d(centre_x + dx, centre_y + dy, 5.8, 5.8, 1.2), emblem) for dx in (-6.6, 0.8) for dy in (-6.6, 0.8))


# 16 px emblems in folders_g.py's form: X is the emblem tone, . the front colour, four rows at y 8 to 11, right-aligned to x 12
NEW_EMBLEMS = {
	"favourites": (emblem_star, ["..X..", "XXXXX", ".XXX.", "XX.XX"]),
	"recent": (emblem_clock, [".XXX.", "XX.XX", "XX..X", ".XXX."]),
	"programs": (emblem_grid, ["XX.XX", "XX.XX", ".....", "XX.XX"]),
}
NEW_FOLDERS = [("favorites", "favourites", "Favourites", "Start menu"), ("recent", "recent", "Recent", "Drives and folders"),
	("programsfolder", "programs", "Programs folder", "Drives and folders")]


@icon("logoff", "bare", "lift", "Log Off", "Start menu")
def draw_log_off(pen):
	pen.shadow(7, 41, 43, SHADOW["lift"])
	pen.face(RR(9, 5, 22, 38, 3), MATS["front"])
	pen.fill(RR(13, 9, 14, 30, 1.5), DARK)
	pen.face(poly([(13, 9, 1.5), (24, 12.5, 1), (24, 41.5, 1), (13, 39, 1.5)]), MATS["dusk"], band=False)
	pen.fill(circ(21.5, 27, 1.4), ORANGE[200])
	pen.face(poly([(25, 22.5, 1), (33, 22.5, 0.5), (33, 17.5, 1), (43, 26, 1.6), (33, 34.5, 1), (33, 29.5, 0.5), (25, 29.5, 1)]), MATS["gold"])


# ---- drives -------------------------------------------------------------------------------------------------------------------------------------
@icon("removable", "bare", "body", "Removable drive", "Drives and folders")
def draw_removable_drive(pen):
	# A USB flash drive laid on the diagonal, plug up and to the right: a gold body with a light label panel, a lit activity light and a
	# key ring hole, and the steel USB plug with its two windows. On the slant and in gold it is not the upright USB key media icon, and
	# nothing about it is a drive box.
	pen.shadow(4, 34, 43.5, SHADOW["body"])

	def slant(points, corner):
		# drawn upright about (24, 24), then turned 45 degrees and moved so the whole stick sits in the live area
		return poly([(x - 1.6, y + 0.8) for x, y in rot(points, 45)], corner)

	pen.face(slant([(18.5, 0), (29.5, 0), (29.5, 14), (18.5, 14)], 1.2), MATS["back"])
	for hole_x in (20.8, 24.8):
		pen.fill(slant([(hole_x, 2.5), (hole_x + 2.4, 2.5), (hole_x + 2.4, 5.5), (hole_x, 5.5)], 0.4), VOIDN[500])
	pen.fill(slant([(20, 9), (28, 9), (28, 13.5), (20, 13.5)], 0.6), VOIDN[400])
	pen.face(slant([(15, 12), (33, 12), (33, 44), (15, 44)], 5), MATS["gold"])
	pen.fill(slant([(19, 17), (29, 17), (29, 33), (19, 33)], 2.2), MATS["goldl"].base)
	pen.fill(slant([(22.2, 19.5), (25.8, 19.5), (25.8, 23.5), (22.2, 23.5)], 1.8), PAPER[900])
	pen.fill(slant([(21.8, 37.2), (26.2, 37.2), (26.2, 41.2), (21.8, 41.2)], 2.2), ORANGE[500])


@icon("ramdisk", "bare", "body", "RAM disk", "Drives and folders")
def draw_ram_disk(pen):
	# A memory chip used as a drive: a black chip package with its legs, seen from a little above, and a gold disk platter with a lit
	# sector printed on its lid. The chip says memory and the platter says disk; one chip, not a module, so it is not the RAM module icon.
	pen.shadow(6, 42, 42, SHADOW["body"])
	for index in range(7):
		pen.face(RR(10 + index * 4.4, 7.5, 2.6, 6, 0.8), MATS["back"], band=False)
	for index in range(7):
		pen.face(RR(10 + index * 4.4, 32, 2.6, 9, 0.8), MATS["back"], band=False)
	pen.face(RR(6, 11, 36, 25, 3.5), MATS["dusk"])
	pen.fill(RR(6.6, 30.5, 34.8, 5, 3), mix(MATS["dusk"].base, MATS["dusk"].edge, 0.45))
	pen.fill(circ(10.8, 15.6, 1.5), HORIZON)
	pen.face(ellipse_d(24, 21.5, 9.5, 7.2), MATS["gold"])
	pen.fill("M24 21.5 L24 14.3 A9.5 7.2 0 0 1 33.5 21.5 Z", PALE)
	pen.fill(ellipse_d(24, 21.5, 2.4, 1.8), MATS["dusk"].base)


# ---- the media on their own ---------------------------------------------------------------------------------------------------------------------
# The drive icons (cd, floppy, removable, ramdisk) and My Computer show the device. The medium or part alone is kept here under its own id, for
# media, storage and hardware lists.
@icon("cd-disc", "bare", "lift", "CD disc", "Drives and folders")
def draw_cd_disc(pen):
	pen.shadow(7, 41, 43, SHADOW["lift"])
	pen.face(ring(24, 24, 19, 3.2), MATS["front"])
	pen.fill(ring(24, 24, 9.5, 3.2), VOIDN[300])
	pen.line("M9.5 19 A15 15 0 0 1 19 9.5", ORANGE[300], 2.2)
	pen.line("M38.5 29 A15 15 0 0 1 29 38.5", INDIGO[300], 2.2)


@icon("floppy-disk", "bare", "body", "Floppy disk", "Drives and folders")
def draw_floppy_disk(pen):
	pen.shadow(7, 41, 41, SHADOW["body"])
	pen.face(poly([(7, 7, 3), (36, 7, 1.5), (41, 12, 1.5), (41, 41, 3), (7, 41, 3)]), MATS["violet"])
	pen.face(poly([(15, 7, 0.4), (32, 7, 0.4), (32, 19, 1.5), (15, 19, 1.5)]), MATS["back"], band=False)
	pen.fill(RR(25, 9.5, 4, 7, 1), INDIGO[600])
	pen.face(poly([(12.5, 41, 0.01), (12.5, 26, 2), (35.5, 26, 2), (35.5, 41, 0.01)]), MATS["paper"], band=False)
	bars(pen, 16, 30.5, [16, 11], 4.5, 2)


@icon("monitor", "bare", "body", "Monitor", "Desktop and shell")
def draw_monitor(pen):
	monitor(pen)


@icon("usb-key", "bare", "body", "USB key", "Drives and folders")
def draw_usb_key(pen):
	pen.shadow(14, 34, 43, SHADOW["body"])
	flash_stick(pen, 14, 6.5)


@icon("ram-module", "bare", "body", "RAM module", "Drives and folders")
def draw_ram_module(pen):
	pen.shadow(5, 43, 36, SHADOW["body"])
	pen.face(poly([(5, 13, 2.5), (43, 13, 2.5), (43, 35, 1), (26, 35, 0.5), (26, 33, 0.5), (22, 33, 0.5), (22, 35, 0.5), (5, 35, 1)]), MATS["dusk"])
	for index in range(3):
		pen.face(RR(8.5 + index * 11.5, 16.5, 8.5, 11, 1.4), MATS["back"], band=False)
	for index in range(14):
		x = 7 + index * 2.5 + (2.5 if index >= 7 else 0)
		pen.fill(RR(x, 30.5, 1.5, 3.6, 0.5), ORANGE[200])


@icon("netdriveoff", "bare", "body", "Network drive (not connected)", "Drives and folders")
def draw_network_drive_off(pen):
	network_drive(pen)
	badge(pen, 37, 37.5, 7, MATS["rose"], "cross")


# ---- file types ---------------------------------------------------------------------------------------------------------------------------------
@icon("audio", "bare", "body", "Audio file", "File types")
def draw_audio_file(pen):
	page(pen)
	pen.face(poly([(19, 21, 0.6), (31.5, 17.5, 0.6), (31.5, 21.5, 0.4), (19, 25, 0.4)], 0.5), MATS["gold"], band=False)
	pen.fill(RR(19, 21, 2.4, 13, 0.6), ORANGE[300])
	pen.fill(RR(29.1, 17.5, 2.4, 13, 0.6), ORANGE[300])
	pen.face(circ(17.3, 34.2, 3.4), MATS["gold"], band=False)
	pen.face(circ(27.4, 30.7, 3.4), MATS["gold"], band=False)


@icon("video", "bare", "body", "Video file", "File types")
def draw_video_file(pen):
	page(pen)
	pen.fill(RR(13, 18, 22, 18, 2), DARK)
	for index in range(5):
		pen.fill(RR(15 + index * 4.2, 19.6, 2.2, 1.8, 0.5), INDIGO[400])
		pen.fill(RR(15 + index * 4.2, 32.6, 2.2, 1.8, 0.5), INDIGO[400])
	pen.face(poly([(20.5, 23, 0.8), (28.5, 27, 0.8), (20.5, 31, 0.8)]), MATS["gold"], band=False)


@icon("batch", "bare", "body", "Batch file", "File types")
def draw_batch_file(pen):
	page(pen)
	pen.fill(RR(13, 17, 22, 15, 2), DARK)
	pen.line("M16.5 21.5 L20 24.5 L16.5 27.5", ORANGE[200], 2)
	pen.line("M22.5 28 H28", PAPER[900], 2)
	gear(pen, 30, 35, 6.4, 4.8, 1.8)


@icon("regfile", "bare", "body", "Registry file", "File types")
def draw_registry_file(pen):
	page(pen)
	bars(pen, 14, 14, [12], 5)
	cube(pen, 21, 32, 5.2, MATS["front"])
	cube(pen, 29.5, 32, 5.2, MATS["violet"])
	cube(pen, 25.2, 25, 5.2, MATS["gold"])


@icon("inifile", "bare", "body", "Settings file (.ini, .inf)", "File types")
def draw_settings_file(pen):
	page(pen)
	for row in range(4):
		y = 16.5 + row * 5.5
		pen.fill(RR(14, y, 7, 2.2, 1.1), LINE)
		pen.fill(RR(23.5, y, 9.5 - (row % 2) * 4, 2.2, 1.1), ORANGE[200])


@icon("html", "bare", "body", "Web page", "File types")
def draw_web_page(pen):
	page(pen)
	bars(pen, 14, 14, [12], 5)
	globe(pen, 24.5, 29, 8)
	pen.line("M15 35.5 C20 40 30 36 34 23", ORANGE[200], 2.2, MATS["gold"])


# ---- Explorer toolbar ---------------------------------------------------------------------------------------------------------------------------
@icon("cut", "bare", "lift", "Cut", "Explorer toolbar")
def draw_cut(pen):
	pen.shadow(7, 41, 43, SHADOW["lift"])
	pen.line("M18 30 L31 5.5", VOIDN[300], 4.6, MATS["back"])
	pen.line("M30 30 L17 5.5", VOIDN[300], 4.6, MATS["back"])
	pen.face(ring(14, 35, 7.6, 3.4), MATS["gold"])
	pen.face(ring(34, 35, 7.6, 3.4), MATS["gold"])
	pen.fill(circ(24, 17.3, 1.6), VOIDN[500])


@icon("copyclip", "bare", "lift", "Copy", "Explorer toolbar")
def draw_copy(pen):
	pen.shadow(7, 41, 43.5, SHADOW["lift"])
	pen.face(RR(17, 5, 22, 27, 3), MATS["fold"])
	pen.face(RR(9, 13, 22, 30, 3), MATS["paper"])
	bars(pen, 14, 20, [12, 12, 8], 5, 2)


@icon("paste", "bare", "lift", "Paste", "Explorer toolbar")
def draw_paste(pen):
	pen.shadow(6, 42, 43.5, SHADOW["lift"])
	clipboard(pen, 6, 8, 26, 34)
	pen.face(RR(21, 20, 20, 23, 2.5), MATS["paper"])
	bars(pen, 25, 26, [12, 12, 8], 4.8, 2)


@icon("properties", "bare", "lift", "Properties", "Explorer toolbar")
def draw_properties(pen):
	pen.shadow(6, 42, 43, SHADOW["lift"])
	pen.face(RR(6, 5, 32, 36, 3), MATS["front"])
	pen.fill(RR(6, 5, 32, 7, 3), HORIZON)
	pen.fill(RR(6, 9, 32, 3, 0.01), HORIZON)
	for row in range(4):
		y = 16.5 + row * 5.6
		pen.fill(RR(10, y, 8, 2.2, 1.1), LINE)
		pen.fill(RR(21, y, 12 - (row % 2) * 4, 2.2, 1.1), INDIGO[300])
	badge(pen, 37, 37, 6.5, MATS["gold"], "check")


@icon("star", "bare", "lift", "Favourites", "Explorer toolbar")
def draw_favourites_glyph(pen):
	pen.shadow(7, 41, 42, SHADOW["lift"])
	pen.face(star_d(24, 25, 19.5, 8.6, 2.6), MATS["gold"])


@icon("mapdrive", "bare", "lift", "Map network drive", "Explorer toolbar")
def draw_map_drive(pen):
	network_drive(pen)
	badge(pen, 37, 37.5, 7, MATS["gold"], "plus")


@icon("disconnect", "bare", "lift", "Disconnect network drive", "Explorer toolbar")
def draw_disconnect_drive(pen):
	network_drive(pen)
	badge(pen, 37, 37.5, 7, MATS["rose"], "minus")


# ---- system tray --------------------------------------------------------------------------------------------------------------------------------
@icon("volumemute", "bare", "lift", "Volume (muted)", "System tray")
def draw_volume_muted(pen):
	speaker(pen)
	pen.line("M29 18 L41 30 M41 18 L29 30", RED[200], 3.6, MATS["rose"])


def draw_battery_level(level):
	def draw(pen):
		battery(pen, level)
	return draw


def draw_battery_charging(level):
	def draw(pen):
		battery(pen, level, charging=True)
	return draw


for battery_level in range(6):
	ICONS.append(("battery%d" % battery_level, "bare", "lift", draw_battery_level(battery_level), "Battery, %d of 5" % battery_level, "System tray"))
for battery_level in range(5):
	ICONS.append(("charging%d" % battery_level, "bare", "lift", draw_battery_charging(battery_level), "Charging, %d of 5" % battery_level, "System tray"))


@icon("batteryerror", "bare", "lift", "Battery fault", "System tray")
def draw_battery_fault(pen):
	battery(pen, fault=True)


@icon("acpower", "bare", "lift", "Mains power", "System tray")
def draw_mains_power(pen):
	pen.shadow(9, 39, 43, SHADOW["lift"])
	pen.line("M24 31 V36 C24 40 28 42 33 42 H41", VOIDN[300], 3, MATS["back"])
	pen.fill(RR(16.5, 4.5, 3.4, 9, 1.4), VOIDN[300])
	pen.fill(RR(28.1, 4.5, 3.4, 9, 1.4), VOIDN[300])
	pen.face(poly([(11, 12, 2.5), (37, 12, 2.5), (37, 21, 2), (31, 30, 2.5), (17, 30, 2.5), (11, 21, 2)]), MATS["gold"])
	pen.face(bolt_d(0.42, 0, -3.5), MATS["goldl"], band=False)


@icon("hotplug", "bare", "lift", "Safely remove hardware", "System tray")
def draw_safely_remove(pen):
	pen.shadow(8, 40, 43, SHADOW["lift"])
	flash_stick(pen, 8, 5.5, 0.92)
	badge(pen, 35, 34.5, 7.5, MATS["gold"], "eject")


@icon("hotplugerror", "bare", "lift", "Hardware removal problem", "System tray")
def draw_safely_remove_problem(pen):
	pen.shadow(8, 40, 43, SHADOW["lift"])
	flash_stick(pen, 8, 5.5, 0.92)
	badge(pen, 35, 34.5, 7.5, MATS["rose"], "cross")


# ---- registration -------------------------------------------------------------------------------------------------------------------------------
TOOLBAR_24 = ["back", "forward", "up", "search", "folders", "move", "copy", "del", "undo", "views", "folderopts", "cut", "copyclip", "paste", "properties",
	"star", "mapdrive", "disconnect"]


def register(gen):
	"""Bind set E's helpers, add the new emblems to the folder family, and add every new icon to gen_e.py's inventory and sheet groups."""
	globals().update({name: getattr(gen, name) for name in SHARED})
	for emblem_name, (draw, pixels) in NEW_EMBLEMS.items():
		FG.EMBLEMS[emblem_name] = draw
		FG.PX_EMBLEMS[emblem_name] = pixels
	for icon_id, emblem_name, label, group in NEW_FOLDERS:
		gen.M1_NAME[icon_id] = emblem_name
		gen.M1_H16[icon_id] = ("closed", emblem_name)
		gen.I[icon_id] = ("m1", "body", None)
		gen.HINTED.append(icon_id)
	new_group, after = NEW_GROUP_AFTER
	names = [name for name, _ in gen.GROUPS]
	gen.GROUPS.insert(names.index(after) + 1, (new_group, []))
	listings = {name: items for name, items in gen.GROUPS}
	for icon_id, emblem_name, label, group in NEW_FOLDERS:
		listings[group].append((icon_id, label))
	for icon_id, kind, tier, draw, label, group in ICONS:
		gen.I[icon_id] = (kind, tier, draw)
		listings[group].append((icon_id, label))
