#!/usr/bin/env python3
# Afterglow icons v3: the dialog pictures ReactOS still drew in stock art (mouse and keyboard settings, the Hardware tab, the Start menu
# customize dialog, the Network Connections item and its tray states).
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# Not run on its own: gen_e.py loads this file after gen_v2.py and calls register() with its own namespace, so every icon here is drawn by
# set E's Pen with the same materials, profiles, plate and contact shadows. The pictures sit on the grey dialog face or a white file list,
# so every bare one ships with the keyline (register() adds them to gen_e.py's KEYLINED set); the one plated picture keeps the dusk plate,
# which already stands out on grey. Deterministic: no randomness, no clock, no environment input.

# Filled in by register(): the helpers and colours of gen_e.py, under the names set E uses.
SHARED = ("MATS", "SHADOW", "ORANGE", "RED", "INDIGO", "VOIDN", "PAPER", "HORIZON", "DARK", "LINE", "GLYPH", "GLYPH_D", "RR", "poly", "rot", "circ",
	"ring", "keys", "_n", "mix")

ICONS = []  # (id, kind, tier, draw, label, group)
NEW_GROUP_AFTER = ("Dialog pictures", "Dialogs")  # the new sheet group, and the group it follows


def icon(icon_id, kind, tier, label, group="Dialog pictures"):
	def register_draw(draw):
		ICONS.append((icon_id, kind, tier, draw, label, group))
		return draw
	return register_draw


# ---- shared drawings ----------------------------------------------------------------------------------------------------------------------------
def pointer_d(tip_x, tip_y, scale=1.0):
	"""The arrow pointer, tip at the top left: the shape of the Afterglow arrow pointer, drawn on the icon grid."""
	points = [(0, 0, 0.5), (0, 19, 0.8), (4.6, 14.8, 0.5), (8, 22.4, 0.8), (11.4, 20.9, 0.8), (8, 13.4, 0.5), (14, 13.4, 0.8)]
	return poly([(tip_x + x * scale, tip_y + y * scale, corner * scale) for x, y, corner in points])


def pointer(pen, tip_x, tip_y, scale=1.0, material="dusk"):
	pen.face(pointer_d(tip_x, tip_y, scale), MATS[material], band=False)


def mouse(pen, x, y, width, height, lit=None, cable=True):
	"""A mouse seen from above: the light shell, the parting line between the two buttons, and the primary button in gold."""
	middle = x + width / 2
	button_bottom = y + height * 0.42
	if cable:
		pen.line("M%s %s C%s %s %s %s %s %s" % (_n(middle), _n(y + 0.5), _n(middle), _n(y - 3.5), _n(middle + 6), _n(y - 4.5), _n(middle + 9), _n(y - 2.5)),
			VOIDN[300], 2, MATS["back"])
	pen.face(RR(x, y, width, height, width / 2), MATS["front"])
	radius = width / 2
	if lit == "left":
		pen.face("M%s %s V%s A%s %s 0 0 1 %s %s V%s Z" % (_n(x), _n(button_bottom), _n(y + radius), _n(radius), _n(radius), _n(middle), _n(y),
			_n(button_bottom)), MATS["gold"], band=False)
	elif lit == "right":
		pen.face("M%s %s V%s A%s %s 0 0 0 %s %s V%s Z" % (_n(x + width), _n(button_bottom), _n(y + radius), _n(radius), _n(radius), _n(middle), _n(y),
			_n(button_bottom)), MATS["gold"], band=False)
	pen.fill(RR(x + 0.8, button_bottom - 0.7, width - 1.6, 1.4, 0.7), LINE)
	pen.fill(RR(middle - 0.7, y + 0.8, 1.4, button_bottom - y - 1.2, 0.7), LINE)


def key_cap(pen, x, y, size, material="front"):
	"""A keyboard key seen a little from above: the cap's face over a deeper skirt."""
	pen.face(RR(x, y + size * 0.16, size, size * 0.9, size * 0.2), MATS["back"])
	pen.face(RR(x + size * 0.1, y, size * 0.8, size * 0.78, size * 0.16), MATS[material], band=False)


def monitors(pen):
	"""Two networked computers: a back monitor up and to the right, a front one with the dusk screen, its stand, and the link between them."""
	pen.face(RR(18, 5, 24, 17, 3), MATS["back"])
	pen.fill(RR(21, 8, 18, 11, 1.4), VOIDN[400])
	pen.face(RR(13.5, 33.5, 6, 4, 1), MATS["back"], band=False)
	pen.face(RR(9, 37, 15, 4.5, 1.8), MATS["back"])
	pen.face(RR(5, 15, 26, 19.5, 3), MATS["front"])
	pen.sky(RR(8, 18, 20, 13.5, 1.5))
	pen.fill("M13.5 31.5 a4.5 4.5 0 0 1 9 0 Z", ORANGE[200])


def lights(pen, sending, receiving):
	"""The activity badge at the bottom right: a dark well with the send and receive lights, gold when lit."""
	pen.face(RR(29.5, 31.5, 14, 9, 2.6), MATS["dusk"])
	for centre_x, lit in ((33.8, sending), (39.2, receiving)):
		pen.fill(circ(centre_x, 36, 2.1), ORANGE[200] if lit else INDIGO[500])


def badge_cross(pen, centre_x, centre_y, radius):
	pen.face(circ(centre_x, centre_y, radius), MATS["rose"], band=False)
	arm = radius * 0.42
	pen.line("M%s %s L%s %s M%s %s L%s %s" % (_n(centre_x - arm), _n(centre_y - arm), _n(centre_x + arm), _n(centre_y + arm), _n(centre_x + arm),
		_n(centre_y - arm), _n(centre_x - arm), _n(centre_y + arm)), GLYPH, max(1.8, radius * 0.36))


# ---- mouse and keyboard settings (main.cpl) ---------------------------------------------------------------------------------------------------
@icon("mouse-left", "bare", "body", "Mouse, primary button left")
def draw_mouse_left(pen):
	pen.shadow(14, 34, 43.5, SHADOW["body"])
	mouse(pen, 13, 9, 22, 34, "left")


@icon("mouse-right", "bare", "body", "Mouse, primary button right")
def draw_mouse_right(pen):
	pen.shadow(14, 34, 43.5, SHADOW["body"])
	mouse(pen, 13, 9, 22, 34, "right")


@icon("mouse-wheel", "bare", "body", "Mouse wheel")
def draw_mouse_wheel(pen):
	pen.shadow(8, 30, 43.5, SHADOW["body"])
	mouse(pen, 8, 9, 20, 34)
	pen.face(RR(15.5, 12, 5, 9, 2.5), MATS["gold"], band=False)
	pen.face(poly([(37, 6, 1), (44, 15, 1), (30, 15, 1)]), MATS["gold"], band=False)
	pen.face(poly([(30, 33, 1), (44, 33, 1), (37, 42, 1)]), MATS["gold"], band=False)
	pen.fill(RR(35.8, 16.5, 2.4, 15, 1.2), INDIGO[400])


@icon("mouse-speed", "bare", "lift", "Pointer speed")
def draw_pointer_speed(pen):
	pen.shadow(18, 42, 43, SHADOW["lift"])
	for y, start in ((13, 9), (20.5, 5), (28, 9)):
		pen.line("M%s %s H%s" % (_n(start), _n(y), 17), ORANGE[200], 2.6, MATS["gold"])
	pointer(pen, 20, 6, 1.55)


@icon("mouse-trails", "bare", "lift", "Pointer trails")
def draw_pointer_trails(pen):
	pen.shadow(14, 42, 43, SHADOW["lift"])
	pointer(pen, 6, 5, 1.2, "fold")
	pointer(pen, 14, 9, 1.2, "front")
	pointer(pen, 22, 13, 1.3)


@icon("mouse-hide", "bare", "lift", "Hide the pointer while typing")
def draw_hide_pointer(pen):
	pen.shadow(5, 43, 43, SHADOW["lift"])
	pen.face(RR(5, 8, 38, 19, 3), MATS["paper"])
	pen.fill(RR(10, 15.5, 12, 3.4, 1.7), LINE)
	pen.fill(RR(24.5, 13, 2.4, 9, 1.2), HORIZON)
	pointer(pen, 27, 19, 1.05, "fold")


@icon("mouse-snap", "bare", "lift", "Snap the pointer to the default button")
def draw_snap_to(pen):
	pen.shadow(5, 43, 43, SHADOW["lift"])
	pen.face(RR(5, 9, 38, 17, 3.5), MATS["front"])
	pen.fill(RR(8.5, 12.5, 31, 10, 2.2), ORANGE[200])
	pen.fill(RR(10.5, 14.5, 27, 6, 1.6), MATS["front"].base)
	pen.fill(RR(15, 16.4, 18, 2.2, 1.1), LINE)
	pointer(pen, 23, 17, 1.15)


@icon("mouse-locate", "bare", "lift", "Show where the pointer is")
def draw_locate_pointer(pen):
	pen.shadow(6, 42, 43, SHADOW["lift"])
	pen.face(ring(22, 22, 18, 15.2), MATS["gold"], band=False)
	pen.face(ring(22, 22, 10.6, 7.8), MATS["gold"], band=False)
	pointer(pen, 22, 22, 1.0)


@icon("clicklock", "bare", "lift", "ClickLock")
def draw_click_lock(pen):
	pen.shadow(9, 39, 43.5, SHADOW["lift"])
	pen.line("M16 22 V15 a8 8 0 0 1 16 0 V22", VOIDN[300], 4.2, MATS["back"])
	pen.face(RR(10, 21, 28, 21, 4), MATS["gold"])
	pen.fill(circ(24, 29.5, 2.8), GLYPH_D)
	pen.fill(RR(22.8, 30, 2.4, 6.5, 1.2), GLYPH_D)


@icon("kbd-delay", "bare", "body", "Key repeat delay")
def draw_repeat_delay(pen):
	pen.shadow(5, 33, 41, SHADOW["body"])
	key_cap(pen, 5, 10, 28)
	pen.fill(RR(13, 16, 12, 2.6, 1.3), LINE)
	pen.face(circ(34.5, 33, 9), MATS["paper"])
	pen.line("M34.5 27.6 V33 H38.8", HORIZON, 2.2)


@icon("kbd-rate", "bare", "body", "Key repeat rate")
def draw_repeat_rate(pen):
	pen.shadow(5, 43, 42, SHADOW["body"])
	for index, material in enumerate(("fold", "front", "front")):
		key_cap(pen, 5 + index * 9.5, 8 + index * 8, 19, material)
	pen.fill(RR(27.5, 29.5, 10, 2.4, 1.2), ORANGE[200])


# ---- System Properties, Hardware tab (sysdm.cpl) -----------------------------------------------------------------------------------------------
@icon("hwprofile", "tile", "tile", "Hardware profiles")
def draw_hardware_profiles(pen):
	for offset in (17, 22, 27):
		pen.fill(RR(offset - 1.1, 9.5, 2.2, 5, 1.1), VOIDN[300])
		pen.fill(RR(9.5, offset - 1.1, 5, 2.2, 1.1), VOIDN[300])
	pen.face(RR(12.5, 12.5, 19, 19, 3), MATS["front"])
	pen.face(RR(17.5, 17.5, 9, 9, 1.6), MATS["violet"], band=False)
	pen.face(circ(32, 26.5, 4.2), MATS["gold"], band=False)
	pen.face("M24.5 38.5 C24.5 33.5 28 31 32 31 C36 31 39.5 33.5 39.5 38.5 V39 H24.5 Z", MATS["gold"])


# ---- Customize Classic Start Menu (explorer.exe) ----------------------------------------------------------------------------------------------
@icon("startmenu", "bare", "body", "Start menu")
def draw_start_menu(pen):
	pen.shadow(9, 41, 43, SHADOW["body"])
	pen.face(RR(9, 5, 32, 37, 3), MATS["front"])
	pen.face(poly([(9, 5, 3), (17, 5, 0.01), (17, 42, 0.01), (9, 42, 3)]), MATS["dusk"], band=False)
	pen.fill(RR(11.6, 9, 2.8, 22, 1.4), HORIZON)
	pen.fill(circ(13, 36.5, 2.4), ORANGE[200])
	for row in range(5):
		y = 9.5 + row * 6.4
		if row == 2:
			pen.fill(RR(19, y - 1.6, 19.5, 6, 1.6), ORANGE[200])
		pen.fill(RR(21, y, 3.2, 3, 1), INDIGO[300] if row != 2 else ORANGE[500])
		pen.fill(RR(26.5, y + 0.4, 10 - (row % 2) * 3, 2.2, 1.1), LINE if row != 2 else ORANGE[500])


# ---- Network Connections and its tray icon (netshell.dll) -------------------------------------------------------------------------------------
@icon("lan", "bare", "body", "Network connection")
def draw_connection(pen):
	pen.shadow(5, 43, 42, SHADOW["body"])
	monitors(pen)


@icon("lanoff", "bare", "body", "Network connection (unplugged)")
def draw_connection_off(pen):
	pen.shadow(5, 43, 42, SHADOW["body"])
	monitors(pen)
	badge_cross(pen, 36.5, 35.5, 7)


@icon("lantrans", "bare", "body", "Network connection (sending)")
def draw_connection_sending(pen):
	pen.shadow(5, 43, 42, SHADOW["body"])
	monitors(pen)
	lights(pen, True, False)


@icon("lanrec", "bare", "body", "Network connection (receiving)")
def draw_connection_receiving(pen):
	pen.shadow(5, 43, 42, SHADOW["body"])
	monitors(pen)
	lights(pen, False, True)


@icon("lanboth", "bare", "body", "Network connection (sending and receiving)")
def draw_connection_both(pen):
	pen.shadow(5, 43, 42, SHADOW["body"])
	monitors(pen)
	lights(pen, True, True)


# ---- programs the Start menu shows ----------------------------------------------------------------------------------------------------------
@icon("fontsub", "tile", "tile", "Font Substitutes Editor", "Programs")
def draw_font_substitutes(pen):
	pen.face(RR(9, 9, 18, 18, 2.5), MATS["paper"])
	pen.line("M13 23.5 L18 12.5 L23 23.5 M14.8 19.8 H21.2", HORIZON, 2.2)
	pen.face(RR(23, 23, 16, 16, 2.5), MATS["gold"])
	pen.line("M27 35 L31 26.5 L35 35 M28.4 32 H33.6", GLYPH_D, 2)
	pen.line("M30.5 12.5 C34.5 12.5 36 14.5 36 18.5", PAPER[900], 2.2)
	pen.fill(poly([(33, 17.5, 0.4), (39, 17.5, 0.4), (36, 21.5, 0.4)], 0.4), PAPER[900])
	pen.line("M17.5 35.5 C13.5 35.5 12 33.5 12 29.5", PAPER[900], 2.2)
	pen.fill(poly([(9, 30.5, 0.4), (15, 30.5, 0.4), (12, 26.5, 0.4)], 0.4), PAPER[900])


# ---- registration -------------------------------------------------------------------------------------------------------------------------------
def register(gen):
	"""Bind set E's helpers, add every new icon to gen_e.py's inventory and a new sheet group, and give the bare pictures the keyline."""
	globals().update({name: getattr(gen, name) for name in SHARED})
	new_group, after = NEW_GROUP_AFTER
	names = [name for name, _ in gen.GROUPS]
	gen.GROUPS.insert(names.index(after) + 1, (new_group, []))
	listings = {name: items for name, items in gen.GROUPS}
	for icon_id, kind, tier, draw, label, group in ICONS:
		gen.I[icon_id] = (kind, tier, draw)
		listings[group].append((icon_id, label))
		if kind == "bare":
			gen.KEYLINED.add(icon_id)
