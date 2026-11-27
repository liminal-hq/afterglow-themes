#!/usr/bin/env python3
# Afterglow icons v6: the art the ReactOS 0.4.16 desktop still loaded in stock after v5: the Folder Options dialog (its General tab
# pictures and the file types its File Types list shows), Device Manager's device classes and problem overlays, the Applications
# Manager's toolbar and categories, the Mouse Keys tray states, the dialog pictures of the inner Control Panel pages, and the toolbar
# glyphs the standard toolbar strips and the programs' own strips are composed from (desktop/icons/strips.py).
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# Not run on its own: gen_e.py loads this file after gen_v5.py and calls register() with its own namespace, so every icon here is drawn
# by set E's Pen with the same materials, profiles and contact shadows. Every icon here is a bare object on a light ground (a dialog face,
# a white list, a cream toolbar), so each ships with the keyline. The glyphs and the icons the Applications Manager asks for at 24 px get
# a 24 px profile (TOOLBAR_24). The Mouse Keys states and the Device Manager overlays are shown only at 16 px, so they have hand-tuned
# 16 px frames. Deterministic: no randomness, no clock, no environment input.
import math

# Filled in by register(): the helpers and colours of gen_e.py, under the names set E uses.
SHARED = ("MATS", "SKY", "SHADOW", "ORANGE", "RED", "PURPLE", "INDIGO", "VOIDN", "PAPER", "PALE", "BRAND_GOLD", "SKY1", "SKY4", "SKY7", "HORIZON",
	"DARK", "LINE", "GLYPH", "GLYPH_D", "RR", "poly", "rot", "circ", "ring", "ellipse_d", "page", "page_d", "fold_d", "window", "gear", "bars",
	"_n", "mix", "FG", "M1", "Pen")

ICONS = []  # (id, kind, tier, draw, label, group)
GROUPS = [("Folder Options pictures", "Namespaces and the registry"), ("Devices", "Folder Options pictures"), ("Toolbar glyphs", "Devices"),
	("Mouse Keys", "Toolbar glyphs")]  # the new sheet groups, each after the one named
# The 24 px profiles: every new glyph, and the existing icons the Applications Manager (24 px only) and the 24 px strips ask for.
TOOLBAR_24_EXISTING = ["logoff", "settings", "programs", "wusa", "folder", "folderopen", "star", "audio", "console-app", "readme", "admintools", "calc",
	"sol", "paint", "browser", "library", "doc", "appmanager", "video", "display", "help", "floppy-disk", "clock", "image", "del", "user", "group",
	"mycomputer", "printer", "properties"]
TOOLBAR_24 = []  # filled from ICONS below: the glyphs, then TOOLBAR_24_EXISTING


def icon(icon_id, kind, tier, label, group, toolbar=False):
	def register_draw(draw):
		ICONS.append((icon_id, kind, tier, draw, label, group))
		if toolbar:
			TOOLBAR_24.append(icon_id)
		return draw
	return register_draw


def glyph(icon_id, label):
	"""A toolbar glyph: bare, lifted, keylined, with a 24 px profile."""
	return icon(icon_id, "bare", "lift", label, "Toolbar glyphs", toolbar=True)


# ---- shared drawings ----------------------------------------------------------------------------------------------------------------------------
def mini_window(pen, x, y, width, height, bar="dusk"):
	"""A small window: light frame, a title strip and a white client area. Returns the client box."""
	pen.face(RR(x, y, width, height, 2.5), MATS["front"])
	pen.face(poly([(x, y, 2.5), (x + width, y, 2.5), (x + width, y + 5.5, 0.01), (x, y + 5.5, 0.01)]), MATS[bar], band=False)
	client = (x + 2, y + 7.5, width - 4, height - 9.5)
	pen.fill(RR(*client, 1), PAPER[900])
	return client


def mini_folder(pen, x, y, scale=1.0):
	"""A small gold folder for a dialog picture: the back with its tab, and the lighter front."""
	pen.face(poly([(x, y, 1), (x + 5 * scale, y, 1), (x + 6.5 * scale, y + 1.8 * scale, 0.5), (x + 12 * scale, y + 1.8 * scale, 1),
		(x + 12 * scale, y + 9 * scale, 1), (x, y + 9 * scale, 1)]), MATS["gold"], band=False)
	pen.face(RR(x, y + 3 * scale, 12 * scale, 6 * scale, 1), MATS["goldl"], band=False)


def pointer_d(tip_x, tip_y, scale=1.0):
	points = [(0, 0, 0.5), (0, 19, 0.8), (4.6, 14.8, 0.5), (8, 22.4, 0.8), (11.4, 20.9, 0.8), (8, 13.4, 0.5), (14, 13.4, 0.8)]
	return poly([(tip_x + px * scale, tip_y + py * scale, corner * scale) for px, py, corner in points])


def hand_d(x, y, s=1.0):
	"""The link-select hand: the pointing finger up, three folded fingers and the thumb, on the pointer grid."""
	points = [(4, 0, 2), (8, 0, 2), (8, 8, 0.6), (11.5, 7, 1.6), (15, 8, 1.6), (18, 9.5, 1.6), (18.5, 17, 3), (15, 24, 2), (6, 24, 2), (0.5, 15, 1.5),
		(1.5, 12.5, 1.2), (4, 14, 0.8)]
	return poly([(x + px * s, y + py * s, corner * s) for px, py, corner in points])


def card_body(pen, port=None):
	"""An expansion card seen face on: the dusk board with its chips, the gold edge connector along the bottom and the steel bracket at
	the left, where the port is."""
	pen.shadow(6, 44, 42.5, SHADOW["body"])
	for index in range(7):
		pen.face(RR(17 + index * 3.6, 35, 2.2, 5.5, 0.6), MATS["gold"], band=False)
	pen.face(RR(9, 11, 35, 26, 3), MATS["dusk"])
	pen.face(RR(4, 7, 7, 33, 1.6), MATS["back"])
	if port == "display":
		pen.face(circ(31, 22, 8.2), MATS["front"])
		pen.fill(circ(31, 22, 5.6), DARK)
		for angle in (0, 120, 240):
			blade = rot([(31, 21, 0.5), (36, 19.5, 1.2), (35.5, 22.5, 1), (31, 23, 0.5)], angle, 31, 22)
			pen.fill(poly(blade, 0.6), INDIGO[400])
		pen.fill(circ(31, 22, 1.8), ORANGE[200])
		pen.fill(RR(5.5, 14, 4, 9, 1), DARK)
		pen.fill(RR(5.5, 26, 4, 6, 1.4), DARK)
	elif port == "net":
		pen.face(RR(26, 15, 13, 12, 2), MATS["goldl"], band=False)
		pen.fill(RR(15, 16, 7, 7, 1), INDIGO[200])
		pen.fill(poly([(5.4, 16, 0.4), (9.6, 16, 0.4), (9.6, 23, 0.4), (8.6, 23, 0.4), (8.6, 25, 0.4), (6.4, 25, 0.4), (6.4, 23, 0.4), (5.4, 23, 0.4)], 0.4), DARK)
		pen.fill(circ(32.5, 21, 1.8), ORANGE[300])
	else:
		pen.face(RR(16, 15, 10, 10, 1.4), MATS["back"], band=False)
		pen.face(RR(29, 15, 10, 10, 1.4), MATS["back"], band=False)
		pen.fill(RR(16, 28.5, 23, 2.2, 1.1), INDIGO[400])


def badge(pen, centre_x, centre_y, radius, material, mark):
	"""A round badge carrying a plus, minus, cross, check or question mark."""
	pen.face(circ(centre_x, centre_y, radius), MATS[material], band=False)
	ink = GLYPH_D if material in ("gold", "goldl") else GLYPH
	arm = radius * 0.5
	width = max(1.8, radius * 0.38)
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
	elif mark == "question":
		scale = radius / 19
		pen.line("M%s %s a%s %s 0 1 1 %s %s c%s %s %s %s %s %s" % (_n(centre_x - 5 * scale), _n(centre_y - 6 * scale), _n(5 * scale), _n(5 * scale),
			_n(8 * scale), _n(4 * scale), _n(-2 * scale), _n(1.5 * scale), _n(-3 * scale), _n(2.5 * scale), _n(-3 * scale), _n(5 * scale)), ink, width)
		pen.fill(circ(centre_x, centre_y + 9 * scale, max(1.1, 2.5 * scale)), ink)
	elif mark == "bang":
		pen.fill(RR(centre_x - width / 2, centre_y - arm * 1.3, width, arm * 1.7, width / 2), ink)
		pen.fill(circ(centre_x, centre_y + arm * 1.05, width * 0.6), ink)


def arrow_d(cx, cy, length, head, shaft, angle):
	"""A straight arrow centred on (cx, cy), pointing at `angle` degrees (0 is right)."""
	half = length / 2
	points = [(cx - half, cy - shaft / 2, 1), (cx + half - head, cy - shaft / 2, 0.5), (cx + half - head, cy - head * 0.9, 1),
		(cx + half, cy, 1.4), (cx + half - head, cy + head * 0.9, 1), (cx + half - head, cy + shaft / 2, 0.5), (cx - half, cy + shaft / 2, 1)]
	return poly(rot(points, angle, cx, cy))


def curved_arrow(pen, cx, cy, radius, start, sweep, material="gold", width=5):
	"""A gold arc with an arrowhead at its end: start and sweep in degrees, clockwise when sweep is positive."""
	end = start + sweep
	x0, y0 = cx + radius * math.cos(math.radians(start)), cy + radius * math.sin(math.radians(start))
	x1, y1 = cx + radius * math.cos(math.radians(end)), cy + radius * math.sin(math.radians(end))
	large = 1 if abs(sweep) > 180 else 0
	direction = 1 if sweep > 0 else 0
	pen.line("M%s %s A%s %s 0 %d %d %s %s" % (_n(x0), _n(y0), _n(radius), _n(radius), large, direction, _n(x1), _n(y1)), MATS[material].base, width,
		MATS[material])
	tangent = end + (90 if sweep > 0 else -90)
	head = 6.2
	tip = (x1 + head * 0.9 * math.cos(math.radians(tangent)), y1 + head * 0.9 * math.sin(math.radians(tangent)))
	left = (x1 + head * math.cos(math.radians(tangent + 120)) * 0.95, y1 + head * math.sin(math.radians(tangent + 120)) * 0.95)
	right = (x1 + head * math.cos(math.radians(tangent - 120)) * 0.95, y1 + head * math.sin(math.radians(tangent - 120)) * 0.95)
	pen.face(poly([tip + (1,), left + (1,), right + (1,)]), MATS[material], band=False, grad=False)


def doc_page(pen, x=9, y=5, width=30, height=38, fold=10):
	pen.shadow(x, x + width, y + height, SHADOW["body"])
	pen.face(page_d(x, y, width, height, fold), MATS["paper"])
	pen.face(fold_d(x, y, width, fold), MATS["fold"], band=False)


def magnifier(pen, cx, cy, radius, handle=True):
	if handle:
		pen.face(poly(rot([(cx - 3, cy + radius + 1), (cx + 3, cy + radius + 1), (cx + 3, cy + radius + 13), (cx - 3, cy + radius + 13)], -45, cx, cy), 2.6),
			MATS["dusk"])
	pen.face(ring(cx, cy, radius, radius - 3.6), MATS["back"])
	pen.face(circ(cx, cy, radius - 3.6), MATS["glass"], band=False)


# ---- Folder Options (shell32.dll 182 to 187, and the File Types list) ---------------------------------------------------------------------------
FO = "Folder Options pictures"


def folder_grid(pen, x, y, columns, rows, step=9):
	for row in range(rows):
		for column in range(columns):
			mini_folder(pen, x + column * step, y + row * 8.5, 0.62)


@icon("fo-tasks", "bare", "body", "Show common tasks in folders", FO)
def draw_fo_tasks(pen):
	"""A folder window with its task pane: gold task links in a lit panel down the left, the folders beside it."""
	pen.shadow(5, 43, 42, SHADOW["body"])
	cx, cy, cw, ch = mini_window(pen, 4, 7, 40, 34)
	pen.fill(RR(cx + 1, cy + 1, 12, ch - 2, 1.2), PALE)
	for row in range(3):
		pen.fill(RR(cx + 3, cy + 4 + row * 5.5, 8, 2, 1), ORANGE[300] if row == 0 else ORANGE[200])
	folder_grid(pen, cx + 15.5, cy + 3, 2, 2)


@icon("fo-classic", "bare", "body", "Use Windows classic folders", FO)
def draw_fo_classic(pen):
	"""The same folder window without the task pane: only the folders."""
	pen.shadow(5, 43, 42, SHADOW["body"])
	cx, cy, cw, ch = mini_window(pen, 4, 7, 40, 34)
	folder_grid(pen, cx + 3.5, cy + 3, 3, 2, 10.5)


@icon("fo-samewindow", "bare", "body", "Open each folder in the same window", FO)
def draw_fo_same_window(pen):
	"""One window: the folder opened inside it, shown by the gold arrow turning back into the same window."""
	pen.shadow(5, 43, 42, SHADOW["body"])
	cx, cy, cw, ch = mini_window(pen, 4, 7, 40, 34)
	mini_folder(pen, cx + 4, cy + 6, 1.0)
	curved_arrow(pen, 30, 28, 6.5, 200, 250, width=3.2)


@icon("fo-newwindow", "bare", "body", "Open each folder in its own window", FO)
def draw_fo_new_window(pen):
	"""Two windows: the folder in the back one opens in a window of its own in front."""
	pen.shadow(5, 43, 43, SHADOW["body"])
	cx, cy, cw, ch = mini_window(pen, 3, 4, 28, 23)
	mini_folder(pen, cx + 3, cy + 3, 0.8)
	cx, cy, cw, ch = mini_window(pen, 17, 18, 27, 24, "gold")
	mini_folder(pen, cx + 6, cy + 4, 1.0)


@icon("fo-singleclick", "bare", "lift", "Single-click to open an item", FO)
def draw_fo_single_click(pen):
	"""An item whose name is underlined like a link, and the link hand over it: one click opens it."""
	pen.shadow(4, 44, 43, SHADOW["lift"])
	mini_folder(pen, 4, 6, 1.3)
	pen.fill(RR(4, 23, 18, 2.4, 1.2), INDIGO[400])
	pen.fill(RR(4, 27, 18, 1.6, 0.8), ORANGE[300])
	pen.line("M30 15 V9 M25.5 16.5 L22 13 M34.5 16.5 L38 13", ORANGE[200], 2, MATS["gold"])
	pen.face(hand_d(24, 19, 0.95), MATS["paper"])


@icon("fo-doubleclick", "bare", "lift", "Double-click to open an item", FO)
def draw_fo_double_click(pen):
	"""An item, and the arrow pointer on it with two click rings: two clicks open it."""
	pen.shadow(4, 44, 43, SHADOW["lift"])
	mini_folder(pen, 5, 6, 1.4)
	pen.fill(RR(4, 23, 20, 2.4, 1.2), INDIGO[400])
	pen.raw('<circle cx="24" cy="20" r="4.5" fill="none" stroke="%s" stroke-width="1.8"/>' % ORANGE[300])
	pen.raw('<circle cx="24" cy="20" r="8.5" fill="none" stroke="%s" stroke-width="1.8"/>' % ORANGE[200])
	pen.face(pointer_d(24, 20, 1.0), MATS["dusk"], band=False)


@icon("certificate", "bare", "body", "Certificate", FO)
def draw_certificate(pen):
	"""A certificate: a landscape page with text lines and a rose seal with gold ribbons at the bottom right."""
	pen.shadow(4, 44, 40, SHADOW["body"])
	pen.face(RR(4, 8, 40, 29, 3), MATS["paper"])
	pen.fill(RR(9, 13, 22, 2.6, 1.3), ORANGE[300])
	bars(pen, 9, 19, [26, 20, 14], 4.4, 2)
	for dx in (-3.2, 3.2):
		pen.face(poly([(34 + dx - 2.2, 31, 0.5), (34 + dx + 2.2, 31, 0.5), (34 + dx + 2.2, 44, 0.3), (34 + dx, 41.5, 0.3), (34 + dx - 2.2, 44, 0.3)], 0.4),
			MATS["gold"], band=False)
	pen.face(circ(34, 29, 6.5), MATS["rose"])
	pen.raw('<circle cx="34" cy="29" r="3.8" fill="none" stroke="%s" stroke-width="1.3"/>' % RED[100])


@icon("eventlog", "bare", "body", "Event log", FO)
def draw_event_log(pen):
	"""An event log: a page of entries, each led by its kind: violet information, gold warning, rose error."""
	doc_page(pen)
	for row, colour in enumerate((PURPLE[300], ORANGE[200], RED[200], PURPLE[300])):
		y = 17 + row * 6
		pen.fill(circ(16, y + 1.2, 2.3), colour)
		pen.fill(RR(21, y, 13 if row % 2 else 11, 2.4, 1.2), LINE)


@icon("xmlfile", "bare", "body", "XML document", FO)
def draw_xml_file(pen):
	"""A marked-up page: violet angle brackets around a gold slash."""
	doc_page(pen)
	pen.line("M19 20 L13.5 26 L19 32 M29 20 L34.5 26 L29 32", PURPLE[400], 3)
	pen.line("M26.5 18.5 L21.5 33.5", ORANGE[300], 3)


# ---- Devices (setupapi.dll and the hardware pages) ----------------------------------------------------------------------------------------------
DEV = "Devices"


@icon("devcard", "bare", "body", "Expansion card", DEV)
def draw_device_card(pen):
	card_body(pen)


@icon("devdisplay", "bare", "body", "Display adapter", DEV)
def draw_display_adapter(pen):
	card_body(pen, "display")


@icon("devnetcard", "bare", "body", "Network adapter", DEV)
def draw_network_adapter(pen):
	card_body(pen, "net")


@icon("devmouse", "bare", "body", "Mouse", DEV)
def draw_device_mouse(pen):
	"""A mouse seen from above, its cable curling away: the device, not the applet."""
	pen.shadow(13, 35, 44, SHADOW["body"])
	pen.line("M24 9 C24 4 31 2 37 5", VOIDN[300], 2.4, MATS["back"])
	pen.face(RR(13, 8, 22, 35, 11), MATS["front"])
	pen.face("M13 22 V19 a11 11 0 0 1 11 -11 V22 Z", MATS["gold"], band=False)
	pen.fill(RR(13.8, 21.3, 20.4, 1.5, 0.7), LINE)
	pen.fill(RR(23.3, 8.8, 1.5, 13, 0.7), LINE)


@icon("printer", "bare", "body", "Printer", DEV, toolbar=True)
def draw_printer(pen):
	"""A printer: the paper standing in its feed, the light body with its gold light, and a printed page coming out of the front."""
	pen.shadow(4, 44, 43, SHADOW["body"])
	pen.face(RR(13, 5, 22, 14, 1.5), MATS["paper"], band=False)
	pen.face(RR(4, 15, 40, 18, 4), MATS["back"])
	pen.fill(RR(9, 27.5, 30, 2.6, 1.3), DARK)
	pen.fill(RR(36, 19.5, 4, 3, 1.2), ORANGE[200])
	pen.face(RR(11, 29, 26, 14, 1.5), MATS["paper"])
	bars(pen, 15, 33, [18, 12], 4.4, 2)


@icon("devunknown", "bare", "body", "Unknown device", DEV)
def draw_unknown_device(pen):
	"""A device nobody has named: a plain grey box, and a violet question badge."""
	pen.shadow(4, 40, 41, SHADOW["body"])
	pen.face(RR(5, 12, 30, 26, 3.5), MATS["back"])
	pen.fill(RR(9, 31, 12, 2.4, 1.2), VOIDN[400])
	badge(pen, 32, 15, 10.5, "violet", "question")


def overlay(pen, material, mark):
	"""A problem overlay: a small badge in the bottom-left third, where Device Manager lays it over the class icon."""
	badge(pen, 9, 39, 8.6, material, mark)


@icon("ovl-warning", "bare", "flat", "Overlay, device problem", DEV)
def draw_overlay_warning(pen):
	pen.face(poly([(9, 28, 1.6), (19, 46, 1.6), (-1, 46, 1.6)]), MATS["gold"], band=False)
	pen.fill(RR(8, 33.5, 2.2, 7, 1.1), GLYPH_D)
	pen.fill(circ(9.1, 43.2, 1.4), GLYPH_D)


@icon("ovl-error", "bare", "flat", "Overlay, device disabled", DEV)
def draw_overlay_error(pen):
	overlay(pen, "rose", "minus")


@icon("ovl-info", "bare", "flat", "Overlay, device note", DEV)
def draw_overlay_info(pen):
	overlay(pen, "violet", "question")


# ---- toolbar glyphs ------------------------------------------------------------------------------------------------------------------------------
@glyph("refresh", "Refresh")
def draw_refresh(pen):
	pen.shadow(6, 42, 43, SHADOW["lift"])
	curved_arrow(pen, 24, 24, 14, 200, 130)
	curved_arrow(pen, 24, 24, 14, 20, 130)


@glyph("home", "Home")
def draw_home(pen):
	pen.shadow(6, 42, 43, SHADOW["lift"])
	pen.face(RR(10, 21, 28, 20, 2), MATS["front"])
	pen.face(poly([(24, 5, 2), (44, 23, 2), (4, 23, 2)]), MATS["rose"])
	pen.face(RR(20, 28, 8, 13, 1.4), MATS["gold"], band=False)


@glyph("redo", "Redo")
def draw_redo(pen):
	pen.line("M31 21 H19 a9 9 0 0 0 0 18 H32", ORANGE[200], 5, MATS["gold"])
	pen.face(poly([(43, 21, 1.5), (30, 10.5, 1.5), (30, 31.5, 1.5)]), MATS["gold"], band=False, grad=False)


@glyph("printpreview", "Print preview")
def draw_print_preview(pen):
	pen.shadow(5, 43, 43.5, SHADOW["lift"])
	pen.face(RR(5, 4, 26, 34, 3), MATS["paper"])
	bars(pen, 10, 10, [16, 16, 10], 5, 2.2)
	magnifier(pen, 30, 28, 10)


@glyph("view-large", "Large icons")
def draw_view_large(pen):
	pen.shadow(5, 43, 43, SHADOW["lift"])
	for x, y, m in ((5, 5, "gold"), (26, 5, "front"), (5, 26, "front"), (26, 26, "front")):
		pen.face(RR(x, y, 17, 17, 3.5), MATS[m])


@glyph("view-small", "Small icons")
def draw_view_small(pen):
	pen.shadow(5, 43, 43, SHADOW["lift"])
	for row in range(2):
		for column in range(2):
			x, y = 5 + column * 20, 8 + row * 18
			pen.face(RR(x, y, 9, 9, 2), MATS["gold" if row == column == 0 else "front"])
			pen.fill(RR(x + 11.5, y + 3.3, 6, 2.4, 1.2), LINE)


@glyph("view-list", "List")
def draw_view_list(pen):
	pen.shadow(5, 43, 43, SHADOW["lift"])
	for column in range(2):
		for row in range(3):
			x, y = 5 + column * 20, 6 + row * 13
			pen.face(RR(x, y, 8, 8, 2), MATS["gold" if row == column == 0 else "front"])
			pen.fill(RR(x + 10, y + 2.8, 8, 2.4, 1.2), LINE)


@glyph("sortname", "Sort by name")
def draw_sort_name(pen):
	pen.shadow(5, 43, 43, SHADOW["lift"])
	pen.line("M7 23 L12.5 7 L18 23 M9 17.5 H16", HORIZON, 3)
	pen.line("M7 28 H18 L7 42 H18", HORIZON, 3)
	pen.face(arrow_d(33, 24, 34, 9, 5, 90), MATS["gold"])


@glyph("newfolder", "New folder")
def draw_new_folder(pen):
	pen.shadow(4, 40, 42, SHADOW["body"])
	pen.face(poly([(4, 10, 2), (17, 10, 2), (20.5, 14, 1), (38, 14, 2), (38, 40, 2.5), (4, 40, 2.5)]), MATS["gold"])
	pen.face(RR(4, 19, 34, 21, 2.5), MATS["goldl"])
	badge(pen, 36, 13, 8.5, "violet", "plus")


@glyph("play", "Play")
def draw_play(pen):
	pen.shadow(9, 41, 42, SHADOW["lift"])
	pen.face(poly([(11, 6, 3), (41, 24, 3), (11, 42, 3)]), MATS["gold"])


@glyph("stopsq", "Stop")
def draw_stop_square(pen):
	pen.shadow(8, 40, 42, SHADOW["lift"])
	pen.face(RR(8, 8, 32, 32, 4), MATS["rose"])


@glyph("pause", "Pause")
def draw_pause(pen):
	pen.shadow(9, 39, 42, SHADOW["lift"])
	for x in (10, 27):
		pen.face(RR(x, 7, 11, 34, 3), MATS["gold"])


@glyph("plus", "Add")
def draw_plus(pen):
	pen.shadow(6, 42, 43, SHADOW["lift"])
	pen.face(poly([(19, 5, 2), (29, 5, 2), (29, 19, 0.5), (43, 19, 2), (43, 29, 2), (29, 29, 0.5), (29, 43, 2), (19, 43, 2), (19, 29, 0.5), (5, 29, 2), (5, 19, 2),
		(19, 19, 0.5)]), MATS["gold"])


@glyph("minus", "Remove")
def draw_minus(pen):
	pen.shadow(6, 42, 35, SHADOW["lift"])
	pen.face(RR(5, 19, 38, 10, 2), MATS["rose"])


@glyph("zoomin", "Zoom in")
def draw_zoom_in(pen):
	pen.shadow(8, 43, 42.5, SHADOW["lift"])
	magnifier(pen, 20, 20, 14)
	pen.line("M14.5 20 H25.5 M20 14.5 V25.5", HORIZON, 3)


@glyph("zoomout", "Zoom out")
def draw_zoom_out(pen):
	pen.shadow(8, 43, 42.5, SHADOW["lift"])
	magnifier(pen, 20, 20, 14)
	pen.line("M14.5 20 H25.5", HORIZON, 3)


@glyph("rotcw", "Rotate clockwise")
def draw_rotate_clockwise(pen):
	pen.shadow(6, 42, 43, SHADOW["lift"])
	pen.face(RR(13, 17, 18, 24, 2.5), MATS["paper"])
	curved_arrow(pen, 26, 22, 14, 200, 120)


@glyph("rotccw", "Rotate anticlockwise")
def draw_rotate_anticlockwise(pen):
	pen.shadow(6, 42, 43, SHADOW["lift"])
	pen.face(RR(17, 17, 18, 24, 2.5), MATS["paper"])
	curved_arrow(pen, 22, 22, 14, -20, -120)


@glyph("fit", "Best fit")
def draw_best_fit(pen):
	pen.shadow(5, 43, 43, SHADOW["lift"])
	pen.face(RR(5, 8, 38, 32, 3), MATS["front"])
	pen.sky(RR(9, 12, 30, 24, 1.5))
	pen.line("M14 17 L20 22 M34 17 L28 22 M14 31 L20 26 M34 31 L28 26", ORANGE[200], 2.6)


@glyph("check", "Check")
def draw_check(pen):
	pen.line("M8 25 L19 36 L40 11", ORANGE[200], 6, MATS["gold"])


@glyph("down", "Down")
def draw_down(pen):
	pen.shadow(6, 42, 43, SHADOW["lift"])
	pen.face(poly([(24, 43, 2), (42, 27, 1.8), (32, 27, 0.8), (32, 10, 2), (16, 10, 2), (16, 27, 0.8), (6, 27, 1.8)]), MATS["gold"])
	pen.face(RR(6, 4, 36, 5, 2), MATS["front"])


@glyph("key", "Key")
def draw_key(pen):
	pen.shadow(6, 42, 43, SHADOW["lift"])
	pen.face(poly(rot([(22, 21.5), (44, 21.5), (44, 27), (40, 27), (40, 31), (35.5, 31), (35.5, 27), (22, 27)], 40, 24, 24), 1), MATS["gold"])
	pen.face(ring(16, 16, 10, 4), MATS["goldl"])


def package(pen):
	pen.shadow(6, 42, 43, SHADOW["body"])
	pen.face(RR(6, 18, 36, 24, 3), MATS["gold"])
	pen.face(RR(4, 14, 40, 8, 2.2), MATS["goldl"])
	pen.fill(RR(21, 14, 6, 28, 0.6), ORANGE[300])


@glyph("install", "Install")
def draw_install(pen):
	package(pen)
	pen.face(arrow_d(24, 12, 20, 9, 6, 90), MATS["violet"])


@glyph("uninstall", "Uninstall")
def draw_uninstall(pen):
	package(pen)
	badge(pen, 36, 12, 9, "rose", "minus")


@glyph("flask", "Science")
def draw_flask(pen):
	pen.shadow(8, 40, 43, SHADOW["body"])
	body = poly([(19, 5, 1.5), (29, 5, 1.5), (29, 18, 1), (40, 38, 3), (37, 43, 3), (11, 43, 3), (8, 38, 3), (19, 18, 1)])
	pen.face(body, MATS["paper"])
	pen.raw('<g clip-path="url(#%s)">' % pen.clip(body))
	pen.face(RR(4, 29, 40, 16, 0.01), MATS["violet"], band=False, edge=False)
	pen.raw("</g>")
	pen.fill(circ(20, 35, 2), PURPLE[100])
	pen.fill(circ(27, 38, 1.5), PURPLE[100])
	pen.face(RR(17, 3, 14, 4, 1.5), MATS["back"], band=False)


@glyph("dot", "Default item")
def draw_dot(pen):
	pen.face(circ(24, 24, 9), MATS["gold"])


def crescent_d(cx, cy, r, hx, hy, hr):
	"""A crescent: the disc (cx, cy, r) less the disc (hx, hy, hr), as one outline: the outer arc, then the inner arc back."""
	distance = math.hypot(hx - cx, hy - cy)
	along = (distance * distance + r * r - hr * hr) / (2 * distance)
	half = math.sqrt(r * r - along * along)
	ux, uy = (hx - cx) / distance, (hy - cy) / distance
	mx, my = cx + along * ux, cy + along * uy
	p1 = (mx - half * uy, my + half * ux)
	p2 = (mx + half * uy, my - half * ux)
	return "M%s %s A%s %s 0 1 1 %s %s A%s %s 0 0 0 %s %s Z" % (_n(p1[0]), _n(p1[1]), _n(r), _n(r), _n(p2[0]), _n(p2[1]), _n(hr), _n(hr), _n(p1[0]), _n(p1[1]))


def sheet(pen, landscape):
	pen.shadow(6, 42, 43, SHADOW["body"])
	if landscape:
		pen.face(RR(4, 11, 40, 28, 3), MATS["paper"])
		pen.line("M15 33 L22 16 L29 33 M17.5 27 H26.5", HORIZON, 3)
	else:
		pen.face(RR(10, 4, 28, 40, 3), MATS["paper"])
		pen.line("M17 32 L24 15 L31 32 M19.5 26 H28.5", HORIZON, 3)


@glyph("portrait", "Portrait")
def draw_portrait(pen):
	sheet(pen, False)


@glyph("landscape", "Landscape")
def draw_landscape(pen):
	sheet(pen, True)


@glyph("sleep", "Hibernate")
def draw_sleep(pen):
	pen.shadow(6, 42, 43, SHADOW["lift"])
	pen.face(crescent_d(22, 24, 18, 32, 17, 15), MATS["violet"])
	pen.line("M33 30 H41 L33 39 H41", ORANGE[200], 2.6, MATS["gold"])


# ---- Mouse Keys (stobject.dll 440 to 449): the tray states, a mouse with each button free, selected or held ------------------------------------
MK = "Mouse Keys"
MOUSE_KEYS = [  # (id, label, left, right): None free, "active" selected for the next click, "down" held
	("mk-off", "Mouse Keys off", None, None),
	("mk-none", "Mouse Keys, no button", None, None),
	("mk-l", "Mouse Keys, left selected", "active", None),
	("mk-l-down", "Mouse Keys, left held", "down", None),
	("mk-r", "Mouse Keys, right selected", None, "active"),
	("mk-r-down", "Mouse Keys, right held", None, "down"),
	("mk-lr", "Mouse Keys, both selected", "active", "active"),
	("mk-lr-down", "Mouse Keys, both held", "down", "down"),
	("mk-l-r-down", "Mouse Keys, left selected, right held", "active", "down"),
	("mk-r-l-down", "Mouse Keys, right selected, left held", "down", "active"),
]


def mouse_keys(pen, left, right, off=False):
	pen.shadow(10, 38, 44, SHADOW["body"])
	pen.face(RR(10, 4, 28, 40, 14), MATS["front"])
	for side, state in (("left", left), ("right", right)):
		if not state:
			continue
		if side == "left":
			d = "M10 21 V18 a14 14 0 0 1 14 -14 V21 Z"
		else:
			d = "M38 21 V18 a14 14 0 0 0 -14 -14 V21 Z"
		pen.face(d, MATS["gold" if state == "down" else "goldl"], band=False)
		if state == "active":
			pen.raw('<path d="%s" fill="none" stroke="%s" stroke-width="2.4" stroke-dasharray="3 2.4"/>' % (d, ORANGE[400]))
	pen.fill(RR(10.8, 20.3, 26.4, 1.5, 0.7), LINE)
	pen.fill(RR(23.3, 4.8, 1.5, 16, 0.7), LINE)
	if off:
		badge(pen, 34, 35, 9.5, "rose", "minus")


def mouse_keys_draw(left, right, off):
	return lambda pen: mouse_keys(pen, left, right, off)


for _id, _label, _left, _right in MOUSE_KEYS:
	ICONS.append((_id, "bare", "body", mouse_keys_draw(_left, _right, _id == "mk-off"), _label, MK))


def mouse_keys_16(left, right, off):
	"""The 16 px frame: the shell in the device-front edge, each button filled gold when held and pale gold with a dotted rim when selected."""
	rows = [list(row) for row in [
		"................",
		".....MMMMMM.....",
		"....MmmmMmmM....",
		"...MmmmmMmmmM...",
		"...MmmmmMmmmM...",
		"...MmmmmMmmmM...",
		"...MMMMMMMMMM...",
		"...MmmmmmmmmM...",
		"...MmmmmmmmmM...",
		"...MmmmmmmmmM...",
		"...MmmmmmmmmM...",
		"...MmmmmmmmmM...",
		"....MmmmmmmM....",
		".....MMMMMM.....",
		"................",
		"................",
	]]
	cells = {"left": [(x, y) for y in range(2, 6) for x in range(4, 8) if rows[y][x] == "m"],
		"right": [(x, y) for y in range(2, 6) for x in range(9, 13) if rows[y][x] == "m"]}
	for side, state in (("left", left), ("right", right)):
		for x, y in cells[side]:
			if state == "down":
				rows[y][x] = "g"
			elif state == "active":
				rows[y][x] = "f" if (x + y) % 2 else "2"
	if off:
		for x, y in ((9, 10), (10, 10), (11, 10), (12, 10), (13, 10), (14, 10), (9, 11), (10, 11), (11, 11), (12, 11), (13, 11), (14, 11), (10, 9), (11, 9),
				(12, 9), (13, 9), (10, 12), (11, 12), (12, 12), (13, 12)):
			rows[y][x] = "r"
		for x in range(10, 14):
			rows[10][x] = "4"
			rows[11][x] = "4"
	return ["".join(row) for row in rows]


ART16 = {_id: mouse_keys_16(_left, _right, _id == "mk-off") for _id, _label, _left, _right in MOUSE_KEYS}
ART16.update({
	"ovl-warning": [
		"................", "................", "................", "................", "................", "................", "................",
		"................", "...G............", "..GgG...........", "..G3G...........", ".Gg3gG..........", ".Gg3gG..........", "GggggggG........",
		"Ggg3gggG........", "GGGGGGGG........"],
	"ovl-error": [
		"................", "................", "................", "................", "................", "................", "................",
		"................", "................", "..RRRR..........", ".RrrrrR.........", "Rrrrrrrr........", "R444444R........", "Rrrrrrrr........",
		".RrrrrR.........", "..RRRR.........."],
	"ovl-info": [
		"................", "................", "................", "................", "................", "................", "................",
		"................", "................", "..VVVV..........", ".Vv44vV.........", "Vvvvv4vV........", "Vvvv4vvV........", "Vvvvvvvv........",
		".Vvv4vV.........", "..VVVV.........."],
})


def register(gen):
	"""Bind set E's helpers, add every new icon to gen_e.py's inventory and the new sheet groups, give them the keyline and add the hand-tuned
	16 px frames to hint16_v2.py's table."""
	globals().update({name: getattr(gen, name) for name in SHARED})
	names = [name for name, _ in gen.GROUPS]
	for new_group, after in GROUPS:
		names = [name for name, _ in gen.GROUPS]
		gen.GROUPS.insert(names.index(after) + 1, (new_group, []))
	listings = {name: items for name, items in gen.GROUPS}
	for icon_id, kind, tier, draw, label, group in ICONS:
		gen.I[icon_id] = (kind, tier, draw)
		listings[group].append((icon_id, label))
		gen.KEYLINED.add(icon_id)
	for icon_id, rows in ART16.items():
		assert len(rows) == 16 and all(len(row) == 16 for row in rows), icon_id
		gen.V16.ART[icon_id] = rows
		gen.HINTED.append(icon_id)
		gen.KEYLINED_16.add(icon_id)
	for icon_id in TOOLBAR_24_EXISTING:
		if icon_id not in TOOLBAR_24:
			TOOLBAR_24.append(icon_id)
