#!/usr/bin/env python3
# Afterglow icons v4: the art the full ReactOS image still showed in stock once the compact image's art was drawn: the programs and
# applets the compact image trims away (Management Console, Program Manager, SnapShot, the console programs, OpenGL and WineD3D, Bluetooth),
# the User Accounts lists, the Remote Desktop dialog pictures, the screen savers and the taskbar's Show Desktop button.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# Not run on its own: gen_e.py loads this file after hint16_v2.py and calls register() with its own namespace, so every icon here is drawn
# by set E's Pen with the same materials, profiles, plate and contact shadows. Programs and applets sit on the dusk plate. The pictures and
# screen savers sit on the grey dialog face or a white file list, so they ship with the keyline. The Show Desktop button sits on the dark
# taskbar, where the light bezel alone reaches 3:1, so it does not. The four icons ReactOS asks for only at 16 px (the three User Accounts
# list icons and the Show Desktop button) also get a hand-tuned 16 px frame, added to hint16_v2.py's table. Deterministic: no randomness,
# no clock, no environment input.
import math

# Filled in by register(): the helpers and colours of gen_e.py, under the names set E uses.
SHARED = ("MATS", "SKY", "SHADOW", "ORANGE", "RED", "PURPLE", "INDIGO", "VOIDN", "PAPER", "PALE", "BRAND_GOLD", "SKY1", "SKY4", "SKY7", "HORIZON",
	"DARK", "LINE", "GLYPH", "GLYPH_D", "RR", "poly", "rot", "circ", "ring", "ellipse_d", "page", "window", "gear", "globe", "keys", "_n", "mix")

ICONS = []  # (id, kind, tier, draw, label, group, keyline)
NEW_GROUP_AFTER = ("Screen savers", "Dialog pictures")  # the new sheet group, and the group it follows


def icon(icon_id, kind, tier, label, group, keyline=None):
	"""Register a drawing. Bare icons ship with the keyline unless keyline is False; tiles never do."""
	def register_draw(draw):
		ICONS.append((icon_id, kind, tier, draw, label, group, kind == "bare" if keyline is None else keyline))
		return draw
	return register_draw


# ---- shared drawings ----------------------------------------------------------------------------------------------------------------------------
def person(pen, centre_x, top, scale, head="gold", body="violet"):
	"""A head and shoulders: the round head over a bust whose shoulders are rounded, set E's user."""
	radius = 6.2 * scale
	head_y = top + radius
	pen.face(circ(centre_x, head_y, radius), MATS[head], band=False)
	shoulder_top = head_y + radius + 1.6 * scale
	half = 11 * scale
	bottom = shoulder_top + 13 * scale
	pen.face("M%s %s C%s %s %s %s %s %s C%s %s %s %s %s %s V%s H%s Z" % (
		_n(centre_x - half), _n(bottom),
		_n(centre_x - half), _n(shoulder_top + 3 * scale), _n(centre_x - 5 * scale), _n(shoulder_top), _n(centre_x), _n(shoulder_top),
		_n(centre_x + 5 * scale), _n(shoulder_top), _n(centre_x + half), _n(shoulder_top + 3 * scale), _n(centre_x + half), _n(bottom),
		_n(bottom), _n(centre_x - half)), MATS[body])


def cross_badge(pen, centre_x, centre_y, radius):
	pen.face(circ(centre_x, centre_y, radius), MATS["rose"], band=False)
	arm = radius * 0.42
	pen.line("M%s %s L%s %s M%s %s L%s %s" % (_n(centre_x - arm), _n(centre_y - arm), _n(centre_x + arm), _n(centre_y + arm), _n(centre_x + arm),
		_n(centre_y - arm), _n(centre_x - arm), _n(centre_y + arm)), GLYPH, max(1.8, radius * 0.36))


def terminal(pen, x, y, width, height):
	"""A text-mode window: the light bezel, a dusk title strip and the dark screen. Returns the screen's box."""
	pen.face(RR(x, y, width, height, 3), MATS["front"])
	pen.face(poly([(x, y, 3), (x + width, y, 3), (x + width, y + 6, 0.01), (x, y + 6, 0.01)]), MATS["dusk"], band=False)
	screen = (x + 2.5, y + 8.5, width - 5, height - 11)
	pen.fill(RR(*screen, 1.4), DARK)
	return screen


def screen_monitor(pen, motif):
	"""A screen saver: the monitor on its stand, its screen the dark of a saver at night, then the saver's own motif clipped to the screen."""
	pen.shadow(10, 38, 43, SHADOW["body"])
	pen.face(RR(20.5, 32, 7, 6, 1.2), MATS["back"], band=False)
	pen.face(RR(13, 37.5, 22, 4.5, 2), MATS["back"])
	pen.face(RR(5, 6, 38, 29, 3.5), MATS["front"])
	screen = RR(8.5, 9.5, 31, 22, 1.5)
	pen.fill(screen, DARK)
	pen.raw('<g clip-path="url(#%s)">' % pen.clip(screen))
	motif(pen)
	pen.raw("</g>")


def small_monitor(pen, x, y, width, height, stand=True):
	"""A monitor for a dialog picture: bezel, the dusk sky screen and its stand. Returns the screen's box."""
	if stand:
		centre = x + width / 2
		pen.face(RR(centre - 3, y + height - 1.5, 6, 5, 1), MATS["back"], band=False)
		pen.face(RR(centre - 8.5, y + height + 3, 17, 4, 1.8), MATS["back"])
	pen.face(RR(x, y, width, height, 3), MATS["front"])
	screen = (x + 3, y + 3, width - 6, height - 6)
	pen.sky(RR(*screen, 1.4))
	return screen


def sparkle_d(centre_x, centre_y, outer, inner):
	points = []
	for index in range(8):
		angle = math.radians(-90 + index * 45)
		radius = outer if index % 2 == 0 else inner
		points.append((centre_x + radius * math.cos(angle), centre_y + radius * math.sin(angle), 0.5))
	return poly(points)


# ---- programs ---------------------------------------------------------------------------------------------------------------------------------------
@icon("mmc", "tile", "tile", "Management Console", "Programs")
def draw_management_console(pen):
	"""A console window with its scope tree down the left and the snap-in's gear on the right."""
	window(pen, 9, 10, 30, 26, MATS["dusk"], 6.5)
	pen.fill(RR(11.5, 19, 9.5, 14.5, 1), PAPER[800])
	for row, (indent, length) in enumerate(((0, 5.5), (2, 4.5), (2, 4.5), (4, 3))):
		y = 21 + row * 3.2
		pen.fill(RR(13 + indent, y, 1.6, 1.6, 0.6), ORANGE[200] if row == 1 else INDIGO[400])
		pen.fill(RR(15.2 + indent, y + 0.3, length - 1.2, 1, 0.5), LINE)
	gear(pen, 30.5, 26.5, 7, 5.3, 2)


@icon("progman", "tile", "tile", "Program Manager", "Programs")
def draw_program_manager(pen):
	"""Program Manager: its window, one group window open with program icons in it, and two groups minimised along the bottom."""
	window(pen, 8, 9, 32, 30, MATS["dusk"], 6.5)
	pen.face(RR(11, 18, 20, 12.5, 1.8), MATS["paper"], band=False)
	pen.fill(RR(11, 18, 20, 2.6, 1.4), HORIZON)
	for index, colour in enumerate((ORANGE[200], PURPLE[300], ORANGE[200])):
		pen.fill(RR(13.2 + index * 5.8, 23, 3.8, 3.8, 1), colour)
	for x in (12, 21.5):
		pen.face(RR(x, 32.5, 7.5, 4, 1.2), MATS["gold"], band=False)


@icon("snapshot", "tile", "tile", "SnapShot", "Programs")
def draw_snapshot(pen):
	"""A camera with a gold crop frame over its lens: a picture of the screen, cropped."""
	pen.face(RR(15, 13, 8, 4.5, 1.4), MATS["back"], band=False)
	pen.face(RR(8.5, 15.5, 31, 20.5, 3.5), MATS["front"])
	pen.fill(RR(33, 18.5, 3.4, 2.4, 1), ORANGE[200])
	pen.face(ring(24, 26, 8.4, 5.6), MATS["back"], band=False)
	pen.face(circ(24, 26, 5.6), SKY, band=False)
	pen.fill(circ(22, 24, 1.6), PALE)
	pen.line("M13 18 V13 H18 M30 39 H35 V34", ORANGE[200], 2.4, MATS["gold"])


@icon("console-app", "tile", "tile", "Console program", "Programs")
def draw_console_program(pen):
	"""The icon a console program without one of its own takes in its title bar and the taskbar: a text-mode window with lines of text and
	the gold block cursor."""
	x, y, width, height = terminal(pen, 9, 10, 30, 28)
	for row, length in enumerate((14, 10, 16)):
		pen.fill(RR(x + 2.5, y + 2.5 + row * 4, length, 1.8, 0.9), INDIGO[300])
	pen.fill(RR(x + 2.5, y + 14.5, 4, 2.8, 0.6), ORANGE[200])


@icon("telnet", "tile", "tile", "Telnet", "Programs")
def draw_telnet(pen):
	"""A text-mode window with its prompt, and the violet globe of the remote host."""
	x, y, width, height = terminal(pen, 8, 9, 27, 25)
	pen.line("M%s %s L%s %s L%s %s" % (_n(x + 3), _n(y + 4), _n(x + 6.5), _n(y + 7), _n(x + 3), _n(y + 10)), ORANGE[200], 2.2)
	pen.fill(RR(x + 9, y + 9, 7, 2, 1), PAPER[900])
	globe(pen, 33, 32, 7.5, "violet", PURPLE[100])


# ---- Control Panel applets ----------------------------------------------------------------------------------------------------------------------
@icon("openglcfg", "tile", "tile", "OpenGL Configuration", "Control Panel applets")
def draw_opengl(pen):
	"""A lit block: the solid OpenGL draws, with a gold top face catching the light."""
	half = 12
	top = 11.5
	middle = 24
	pen.face(poly([(middle, top, 1.4), (middle + half, top + 6.5, 1.4), (middle + half, top + 21.5, 1.4), (middle, top + 28, 1.4),
		(middle - half, top + 21.5, 1.4), (middle - half, top + 6.5, 1.4)]), MATS["violet"], band=False)
	pen.face(poly([(middle, top + 0.6, 1), (middle + half - 0.8, top + 6.5, 0.8), (middle, top + 12.6, 0.8), (middle - half + 0.8, top + 6.5, 0.8)]),
		MATS["goldl"], band=False)
	pen.fill(poly([(middle + 0.4, top + 13.4, 0.6), (middle + half - 0.8, top + 7.4, 0.6), (middle + half - 0.8, top + 21, 0.8),
		(middle + 0.4, top + 27, 0.6)]), PURPLE[400])
	pen.line("M%s %s V%s" % (_n(middle), _n(top + 13.2), _n(top + 27.4)), PURPLE[200], 1)


@icon("wined3dcfg", "tile", "tile", "WineD3D Options", "Control Panel applets")
def draw_wined3d(pen):
	"""A block behind, for Direct3D, and a wine glass in front, for Wine."""
	middle, top, half = 29, 10, 9
	pen.face(poly([(middle, top, 1.2), (middle + half, top + 5, 1.2), (middle + half, top + 16, 1.2), (middle, top + 21, 1.2), (middle - half, top + 16, 1.2),
		(middle - half, top + 5, 1.2)]), MATS["front"], band=False)
	pen.fill(poly([(middle, top + 0.6, 0.8), (middle + half - 0.7, top + 5, 0.6), (middle, top + 9.6, 0.6), (middle - half + 0.7, top + 5, 0.6)]), PAPER[900])
	pen.fill(poly([(middle + 0.4, top + 10.4, 0.5), (middle + half - 0.7, top + 5.8, 0.5), (middle + half - 0.7, top + 15.6, 0.6),
		(middle + 0.4, top + 20.2, 0.5)]), INDIGO[300])
	bowl = "M12 14 H28 C28 23 25 28 20 28 C15 28 12 23 12 14 Z"
	pen.face(bowl, MATS["front"], band=False)
	pen.face("M13.1 19 H26.9 C26.4 24.2 23.8 27 20 27 C16.2 27 13.6 24.2 13.1 19 Z", MATS["rose"], band=False, edge=False)
	pen.face(RR(18.8, 27.5, 2.4, 7, 1), MATS["front"], band=False)
	pen.face(RR(14, 33.5, 12, 3.4, 1.6), MATS["front"])


@icon("bluetooth", "tile", "tile", "Bluetooth", "Control Panel applets")
def draw_bluetooth(pen):
	"""The Bluetooth rune in light paper on a violet rounded shield."""
	pen.face("M24 9 C32 9 35 14 35 24 C35 34 32 39 24 39 C16 39 13 34 13 24 C13 14 16 9 24 9 Z", MATS["violet"])
	pen.line("M18.5 18.5 L29 28.5 L23.6 33.5 V14.5 L29 19.5 L18.5 29.5", GLYPH, 2.6)


# ---- User Accounts (usrmgr.cpl) ----------------------------------------------------------------------------------------------------------------
@icon("user", "bare", "body", "User account", "Dialog pictures")
def draw_user(pen):
	pen.shadow(11, 37, 43, SHADOW["body"])
	person(pen, 24, 6, 1.35)


@icon("user-locked", "bare", "body", "User account (disabled)", "Dialog pictures")
def draw_user_disabled(pen):
	pen.shadow(9, 39, 43, SHADOW["body"])
	person(pen, 21, 6, 1.35, "back", "back")
	cross_badge(pen, 35.5, 34.5, 8)


@icon("group", "bare", "body", "Group", "Dialog pictures")
def draw_group(pen):
	pen.shadow(5, 43, 43, SHADOW["body"])
	person(pen, 31, 5, 1.1, "back", "dusk")
	person(pen, 18, 10, 1.15, "gold", "violet")


# ---- Remote Desktop Connection's dialog (mstsc.exe) -------------------------------------------------------------------------------------------
@icon("rdp-logon", "bare", "body", "Remote Desktop, logon settings", "Dialog pictures")
def draw_rdp_logon(pen):
	pen.shadow(5, 43, 43, SHADOW["body"])
	small_monitor(pen, 5, 5, 26, 20)
	person(pen, 32, 15, 0.95)


@icon("rdp-connection", "bare", "body", "Remote Desktop, connection settings", "Dialog pictures")
def draw_rdp_connection(pen):
	page(pen, 7, 5, 26, 34, 8)
	x, y, width, height = small_monitor(pen, 11.5, 17, 17, 13, stand=False)
	pen.fill("M%s %s a3.2 3.2 0 0 1 6.4 0 Z" % (_n(x + width / 2 - 3.2), _n(y + height)), ORANGE[200])
	pen.face(poly([(31.5, 25, 1), (38.5, 25, 1), (38.5, 32, 0.6), (43, 32, 1), (35, 41.5, 1.2), (27, 32, 1), (31.5, 32, 0.6)]), MATS["gold"])


@icon("rdp-display", "bare", "body", "Remote Desktop, display size", "Dialog pictures")
def draw_rdp_display(pen):
	pen.shadow(9, 39, 43, SHADOW["body"])
	x, y, width, height = small_monitor(pen, 5, 6, 38, 28)
	pen.line("M14.5 20 H33.5", ORANGE[200], 2.4)
	for tip, sign in ((12.5, 1), (35.5, -1)):
		pen.fill(poly([(tip, 20, 0.5), (tip + sign * 5, 16.4, 0.5), (tip + sign * 5, 23.6, 0.5)], 0.5), ORANGE[200])


@icon("rdp-colours", "bare", "body", "Remote Desktop, colours", "Dialog pictures")
def draw_rdp_colours(pen):
	pen.shadow(9, 39, 43, SHADOW["body"])
	x, y, width, height = small_monitor(pen, 5, 6, 38, 28)
	band = width / 4
	for index, colour in enumerate((RED[200], ORANGE[200], BRAND_GOLD, PURPLE[300])):
		pen.fill(RR(x + index * band, y + height - 9, band + 0.05, 9, 0.01), colour)
	pen.raw('<path d="%s" fill="none" stroke="%s" stroke-width="%s"/>' % (RR(x, y, width, height, 1.4), HORIZON, _n(pen.u)))


# ---- screen savers -------------------------------------------------------------------------------------------------------------------------------
def motif_3dtext(pen):
	letter = [(13, 28.5), (19, 12.5), (23, 12.5), (29, 28.5), (25.5, 28.5), (24.2, 24.8), (17.8, 24.8), (16.5, 28.5)]
	pen.fill(poly([(x + 2.4, y + 1.6, 0.6) for x, y in letter], 0.6), ORANGE[500])
	pen.fill(poly([(x, y, 0.6) for x, y in letter], 0.6), ORANGE[200])
	pen.fill(poly([(19, 21.6, 0.3), (23, 21.6, 0.3), (21, 16, 0.3)], 0.3), DARK)
	pen.fill(circ(33.5, 15, 1.2), PURPLE[300])


def motif_blank(pen):
	pen.fill(circ(35.5, 28, 1.1), ORANGE[500])


def motif_butterflies(pen):
	for side in (-1, 1):
		pen.fill("M24 20 C%s 11 %s 12 %s 18 C%s 22 %s 21 24 21 Z" % (_n(24 + side * 4), _n(24 + side * 12), _n(24 + side * 11), _n(24 + side * 10),
			_n(24 + side * 5)), PURPLE[300])
		pen.fill("M24 21.5 C%s 22 %s 25 %s 28 C%s 30 %s 27 24 23 Z" % (_n(24 + side * 4), _n(24 + side * 9), _n(24 + side * 8), _n(24 + side * 5),
			_n(24 + side * 2)), RED[200])
	pen.fill(RR(23.2, 15.5, 1.6, 12, 0.8), ORANGE[200])
	pen.line("M23.6 16 L21.5 12.5 M24.4 16 L26.5 12.5", ORANGE[200], 0.9)


def motif_circles(pen):
	for (centre_x, centre_y, radius), colour in (((19, 18, 7), ORANGE[200]), ((29, 19, 6), PURPLE[300]), ((23.5, 25, 5), RED[200])):
		pen.raw('<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="2"/>' % (_n(centre_x), _n(centre_y), _n(radius), colour))


def motif_cylfrac(pen):
	for index in range(6):
		width = 26 - index * 4.2
		height = 17 - index * 2.8
		colour = (PURPLE[300], HORIZON, PURPLE[300], ORANGE[300], ORANGE[200], BRAND_GOLD)[index]
		pen.raw('<ellipse cx="24" cy="%s" rx="%s" ry="%s" fill="none" stroke="%s" stroke-width="1.6"/>' % (_n(20.5 + index * 0.5), _n(width / 2),
			_n(height / 2), colour))


def motif_logon(pen):
	pen.sky(RR(8.5, 9.5, 31, 22, 1.5))
	pen.fill("M18 26 a6 6 0 0 1 12 0 Z", ORANGE[200])
	pen.fill(RR(8.5, 26, 31, 1.4, 0.01), BRAND_GOLD)
	pen.fill(RR(8.5, 27.4, 31, 5, 0.01), mix(SKY1, DARK, 0.5))


def motif_matrix(pen):
	for column, (start, length) in enumerate(((11, 4), (16, 3), (10, 5), (14, 4), (12, 3), (17, 3), (11, 4))):
		x = 11 + column * 4.2
		for step in range(length):
			y = start + step * 3.6
			pen.fill(RR(x, y, 1.8, 2.4, 0.5), BRAND_GOLD if step == length - 1 else ORANGE[400] if step < length - 2 else ORANGE[200])


def motif_maze(pen):
	walls = "M11 12 H37 V29 H11 Z M15.5 12 V20 M15.5 24 V29 M20 16 H29 M20 16 V25 M24.5 20 V29 M29 12 V20 M33 16 V25 H29"
	pen.raw('<path d="%s" fill="none" stroke="%s" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>' % (walls, INDIGO[200]))
	pen.fill(circ(22.2, 26.8, 1.5), ORANGE[200])


def motif_ssstars(pen):
	pen.fill(ellipse_d(26, 21, 11, 6.5), PURPLE[500])
	pen.fill(ellipse_d(27, 20.5, 6, 3.5), PURPLE[400])
	pen.fill(sparkle_d(25, 20.5, 8, 1.6), BRAND_GOLD)
	pen.fill(circ(25, 20.5, 1.8), PAPER[900])
	pen.fill(circ(13, 14, 0.8), PAPER[900])
	pen.fill(circ(35, 27, 0.8), PAPER[900])


def motif_starfield(pen):
	for index in range(12):
		angle = math.radians(index * 30 + 12)
		for step, (distance, radius) in enumerate(((5, 0.6), (10, 0.9), (15, 1.3))):
			if (index + step) % 2:
				continue
			x = 24 + distance * math.cos(angle)
			y = 20.5 + distance * 0.7 * math.sin(angle)
			pen.fill(circ(x, y, radius), PAPER[900] if step else INDIGO[300])
	pen.fill(circ(24, 20.5, 1), BRAND_GOLD)


for saver_id, saver_label, saver_motif in (
	("scr-3dtext", "3D Text", motif_3dtext),
	("scr-blank", "Blank screen", motif_blank),
	("scr-butterflies", "Butterflies", motif_butterflies),
	("scr-circles", "Circles", motif_circles),
	("scr-cylfrac", "Cylinder fractal", motif_cylfrac),
	("scr-logon", "Logon", motif_logon),
	("scr-matrix", "Matrix", motif_matrix),
	("scr-maze", "Maze", motif_maze),
	("scr-ssstars", "Space stars", motif_ssstars),
	("scr-starfield", "Starfield", motif_starfield),
):
	def draw_saver(pen, motif=saver_motif):
		screen_monitor(pen, motif)
	ICONS.append((saver_id, "bare", "body", draw_saver, saver_label, "Screen savers", True))


# ---- the taskbar's Show Desktop button --------------------------------------------------------------------------------------------------------
@icon("showdesktop", "bare", "lift", "Show Desktop button", "System tray", keyline=False)
def draw_show_desktop(pen):
	"""A light-framed desktop with the sun on its horizon, and a window slid down and aside at its corner: the desktop shown."""
	pen.shadow(5, 43, 43, SHADOW["lift"])
	pen.face(RR(4, 6, 34, 28, 3.5), MATS["front"])
	pen.sky(RR(7.5, 9.5, 27, 21, 1.5))
	pen.fill("M14 30.5 a6 6 0 0 1 12 0 Z", ORANGE[200])
	pen.face(RR(26, 23, 18, 15, 2.5), MATS["paper"])
	pen.face(poly([(26, 23, 2.5), (44, 23, 2.5), (44, 27.5, 0.01), (26, 27.5, 0.01)]), MATS["gold"], band=False)


# ---- the hand-tuned 16 px frames --------------------------------------------------------------------------------------------------------------
# hint16_v2.py's characters: lowercase a material's base, uppercase its 16 px edge, digits and symbols flat details (2 orange 200, 5 to 7
# the sky, 8 dark, 4 paper 900, + red 200), . transparent.
ART16 = {
	"user": [
		"................",
		"................",
		"......GGGG......",
		".....GggggG.....",
		".....GggggG.....",
		".....GggggG.....",
		"......GGGG......",
		"................",
		".....VVVVVV.....",
		"....VvvvvvvV....",
		"...VvvvvvvvvV...",
		"...VvvvvvvvvV...",
		"...VvvvvvvvvV...",
		"...VvvvvvvvvV...",
		"...VVVVVVVVVV...",
		"................",
	],
	"user-locked": [
		"................",
		"....NNNN........",
		"...NnnnnN.......",
		"...NnnnnN.......",
		"...NnnnnN.......",
		"....NNNN........",
		"................",
		"...NNNNNN.......",
		"..NnnnnnnN......",
		".NnnnnnnnnN.....",
		".NnnnnnnnnRRRR..",
		".NnnnnnnnR4rr4R.",
		".NnnnnnnnRr44rR.",
		".NNNNNNNNRr44rR.",
		".........R4rr4R.",
		"..........RRRR..",
	],
	"group": [
		"................",
		"..........NNNN..",
		".........NnnnnN.",
		".........NnnnnN.",
		".....GGGG.NNNN..",
		"....GggggG......",
		"....GggggG.DDDD.",
		"....GggggGDddddD",
		".....GGGG.DddddD",
		"...VVVVVVVVddddD",
		"..VvvvvvvvvVdddD",
		".VvvvvvvvvvvVddD",
		".VvvvvvvvvvvVDDD",
		".VvvvvvvvvvvV...",
		".VVVVVVVVVVVV...",
		"................",
	],
	"showdesktop": [
		"................",
		"................",
		"................",
		".MMMMMMMMMMMM...",
		".M5555555555M...",
		".M5555555555M...",
		".M6666666666M...",
		".M6662226666M...",
		".M7722222GGGGGGG",
		".M7722222GgggggG",
		".MMMMMMMMPpppppP",
		".........PpppppP",
		".........PpppppP",
		".........PPPPPPP",
		"................",
		"................",
	],
}


def register(gen):
	"""Bind set E's helpers, add every new icon to gen_e.py's inventory and a new sheet group, give the light-ground pictures the keyline and
	add the four hand-tuned 16 px frames to hint16_v2.py's table."""
	globals().update({name: getattr(gen, name) for name in SHARED})
	new_group, after = NEW_GROUP_AFTER
	names = [name for name, _ in gen.GROUPS]
	gen.GROUPS.insert(names.index(after) + 1, (new_group, []))
	listings = {name: items for name, items in gen.GROUPS}
	for icon_id, kind, tier, draw, label, group, keyline in ICONS:
		gen.I[icon_id] = (kind, tier, draw)
		listings[group].append((icon_id, label))
		if keyline:
			gen.KEYLINED.add(icon_id)
	for icon_id, rows in ART16.items():
		assert len(rows) == 16 and all(len(row) == 16 for row in rows), icon_id
		gen.V16.ART[icon_id] = rows
		gen.HINTED.append(icon_id)
		if icon_id in gen.KEYLINED:
			gen.KEYLINED_16.add(icon_id)
