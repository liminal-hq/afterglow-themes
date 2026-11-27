#!/usr/bin/env python3
# Afterglow icons v5: the art the ReactOS desktop still showed in stock on the first screens a visitor opens: the NT Object Namespace and
# System Registry folders in My Computer and what is inside them, Registry Editor's value icons, the Explorer address bar's Go button, the
# Run dialog's neighbours in the file-operation dialogs, and the "(None)" entry of the wallpaper list.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# Not run on its own: gen_e.py loads this file after gen_v4.py and calls register() with its own namespace, so every icon here is drawn
# by set E's Pen with the same materials, profiles and contact shadows, and the two folders are the M1 folder with an embossed emblem, as
# the special folders of set E and v2 are. Every icon here sits on a light ground (the white file list, the cream toolbar, a grey dialog),
# so the bare ones ship with the keyline. Registry Editor asks for its value icons only at 16 px, and the NT objects show at 16 px in the
# tree and the List view, so each bare icon has a hand-tuned 16 px frame. The Go button is a 20 px bitmap, rendered from its 24 px
# profile. Deterministic: no randomness, no clock, no environment input.
import math

# Filled in by register(): the helpers and colours of gen_e.py, under the names set E uses.
SHARED = ("MATS", "SHADOW", "ORANGE", "RED", "PURPLE", "INDIGO", "PAPER", "DARK", "LINE", "GLYPH", "GLYPH_D", "RR", "poly", "rot", "circ", "ring",
	"page", "bars", "_n", "FG")

ICONS = []  # (id, kind, tier, draw, label, group, keyline)
NEW_GROUP = ("Namespaces and the registry", "Screen savers")  # the new sheet group, and the group it follows
TOOLBAR_24 = ["go"]  # drawn with a 24 px profile too; render.py makes the 20 px Go bitmap from it


def icon(icon_id, kind, tier, label, group, keyline=None):
	"""Register a drawing. Bare icons ship with the keyline unless keyline is False; tiles never do."""
	def register_draw(draw):
		ICONS.append((icon_id, kind, tier, draw, label, group, kind == "bare" if keyline is None else keyline))
		return draw
	return register_draw


# ---- the two folders: the M1 folder with an embossed emblem ------------------------------------------------------------------------------------
def emblem_namespace(emblem, flap, centre_x, centre_y):
	"""A hierarchy: one node over a bar that branches to two nodes, for the NT Object Namespace."""
	parts = [FG.rect_d(centre_x - 2.7, centre_y - 7.2, 5.4, 4.6, 1.2), FG.rect_d(centre_x - 0.8, centre_y - 3, 1.6, 2.8, 0.3),
		FG.rect_d(centre_x - 6.4, centre_y - 0.8, 12.8, 1.7, 0.6), FG.rect_d(centre_x - 5.9, centre_y, 1.6, 3, 0.3),
		FG.rect_d(centre_x + 4.3, centre_y, 1.6, 3, 0.3), FG.rect_d(centre_x - 7.8, centre_y + 2.6, 5.4, 4.6, 1.2),
		FG.rect_d(centre_x + 2.4, centre_y + 2.6, 5.4, 4.6, 1.2)]
	return "".join('<path d="%s" fill="%s"/>' % (part, emblem) for part in parts)


def cube_d(centre_x, centre_y, radius):
	"""A cube seen from a corner: the pointy-top hexagon of its outline."""
	half = radius * math.sqrt(3) / 2
	points = [(centre_x, centre_y - radius), (centre_x + half, centre_y - radius / 2), (centre_x + half, centre_y + radius / 2), (centre_x, centre_y + radius),
		(centre_x - half, centre_y + radius / 2), (centre_x - half, centre_y - radius / 2)]
	return "M" + " L".join("%s %s" % (_n(x), _n(y)) for x, y in points) + " Z"


def cube_seams(centre_x, centre_y, radius):
	"""The three inner edges of a cube's outline: from its centre to the top-left, top-right and bottom corners."""
	half = radius * math.sqrt(3) / 2
	return "M%s %s L%s %s M%s %s L%s %s M%s %s L%s %s" % (_n(centre_x), _n(centre_y), _n(centre_x - half), _n(centre_y - radius / 2), _n(centre_x),
		_n(centre_y), _n(centre_x + half), _n(centre_y - radius / 2), _n(centre_x), _n(centre_y), _n(centre_x), _n(centre_y + radius))


def emblem_registry(emblem, flap, centre_x, centre_y):
	"""Registry Editor's three stacked cubes, embossed: one on two, each with its seams in the flap's tone."""
	out = ""
	for dx, dy in ((-3.7, 3.1), (3.7, 3.1), (0, -3.3)):
		x, y = centre_x + dx, centre_y + dy
		out += '<path d="%s" fill="%s" stroke="%s" stroke-width="0.9" stroke-linejoin="round"/>' % (cube_d(x, y, 4.1), emblem, flap)
		out += '<path d="%s" fill="none" stroke="%s" stroke-width="0.9" stroke-linecap="round"/>' % (cube_seams(x, y, 4.1), flap)
	return out


# 16 px emblems in folders_g.py's form: X is the emblem tone, . the front colour, four rows at y 8 to 11, right-aligned to x 12
NEW_EMBLEMS = {
	"namespace": (emblem_namespace, ["..X..", "XXXXX", "X...X", "XX.XX"]),
	"registry": (emblem_registry, [".XX..", ".XX..", "XX.XX", "XX.XX"]),
}
NEW_FOLDERS = [("ntnamespace", "namespace", "NT Object Namespace"), ("regkey", "registry", "System Registry (registry key)")]


# ---- what the two folders hold ------------------------------------------------------------------------------------------------------------------
@icon("ntobject", "bare", "body", "NT object", NEW_GROUP[0])
def draw_nt_object(pen):
	"""A kernel object: one cube seen from a corner, as Registry Editor draws its cubes: the top lit gold, the left face light, the right
	face violet."""
	centre_x, centre_y, radius = 26, 21, 15
	half = radius * math.sqrt(3) / 2
	top = (centre_x, centre_y - radius)
	upper_right = (centre_x + half, centre_y - radius / 2)
	lower_right = (centre_x + half, centre_y + radius / 2)
	bottom = (centre_x, centre_y + radius)
	lower_left = (centre_x - half, centre_y + radius / 2)
	upper_left = (centre_x - half, centre_y - radius / 2)
	centre = (centre_x, centre_y)
	pen.shadow(centre_x - half, centre_x + half, centre_y + radius + 1.5, SHADOW["body"])
	pen.face(poly([upper_left + (1.6,), centre + (0.6,), bottom + (1.6,), lower_left + (1.6,)]), MATS["front"])
	pen.face(poly([centre + (0.6,), upper_right + (1.6,), lower_right + (1.6,), bottom + (1.6,)]), MATS["violet"])
	pen.face(poly([top + (1.6,), upper_right + (1.6,), centre + (0.6,), upper_left + (1.6,)]), MATS["goldl"])


@icon("ntdevice", "bare", "body", "NT device", NEW_GROUP[0])
def draw_nt_device(pen):
	"""A device object: a chip, its dark body on gold legs, with a light die and the pin-one mark."""
	pen.shadow(14, 38, 39.5, SHADOW["body"])
	for offset in (0, 5.5, 11, 16.4):
		pen.face(RR(19 + offset - 1.2, 5.5, 2.4, 6, 0.8), MATS["gold"], band=False)
		pen.face(RR(19 + offset - 1.2, 32.5, 2.4, 6, 0.8), MATS["gold"], band=False)
		pen.face(RR(9.5, 13.6 + offset - 1.2, 6, 2.4, 0.8), MATS["gold"], band=False)
		pen.face(RR(36.5, 13.6 + offset - 1.2, 6, 2.4, 0.8), MATS["gold"], band=False)
	pen.face(RR(14, 10, 24, 24, 3.5), MATS["dusk"])
	pen.face(RR(19.5, 15.5, 13, 13, 2), MATS["goldl"], band=False)
	pen.fill(circ(22.6, 18.6, 1.3), DARK)


@icon("ntport", "bare", "body", "NT port", NEW_GROUP[0])
def draw_nt_port(pen):
	"""A port object: a socket, the light faceplate with a dark keyed opening and the gold contacts along its top."""
	pen.shadow(16, 42, 33.5, SHADOW["body"])
	pen.face(RR(15, 6, 28, 26, 4), MATS["front"])
	opening = poly([(19.5, 11, 1.5), (38.5, 11, 1.5), (38.5, 22.5, 1.2), (34, 22.5, 0.6), (34, 27, 1.2), (24, 27, 1.2), (24, 22.5, 0.6), (19.5, 22.5, 1.2)])
	pen.fill(opening, DARK)
	for x in (22.5, 26.5, 30.5, 34.5):
		pen.fill(RR(x - 0.9, 12, 1.8, 5, 0.6), ORANGE[200])


def value_tile(pen, tab):
	"""A registry value: a light card with a coloured tab down its left, clear of the shortcut corner."""
	pen.shadow(9, 43, 33.5, SHADOW["body"])
	pen.face(RR(8, 7, 35, 25, 4), MATS["paper"])
	pen.face(poly([(8, 7, 4), (15, 7, 0.01), (15, 32, 0.01), (8, 32, 4)]), MATS[tab], band=False)


@icon("regstring", "bare", "body", "Registry value, string", NEW_GROUP[0])
def draw_registry_string(pen):
	"""A string value: the card with a gold tab and the letters a and b."""
	value_tile(pen, "gold")
	pen.line("M20.5 16.5 H25 a2.5 2.5 0 0 1 2.5 2.5 V27 M27.5 21 H22.5 a2.8 2.8 0 0 0 0 5.6 H27.5", DARK, 2.4)
	pen.line("M32 11.5 V27 M32 19 H35 a3.5 3.5 0 0 1 3.5 3.5 V23.5 a3.5 3.5 0 0 1 -3.5 3.5 H32", DARK, 2.4)


@icon("regbinary", "bare", "body", "Registry value, binary", NEW_GROUP[0])
def draw_registry_binary(pen):
	"""A binary value: the card with a violet tab and the digits 0 and 1."""
	value_tile(pen, "violet")
	pen.raw('<rect x="19.5" y="12.2" width="7.6" height="14.6" rx="3.8" fill="none" stroke="%s" stroke-width="2.4"/>' % DARK)
	pen.line("M32 15 L35 12.2 V27 M31.5 27 H38.5", DARK, 2.4)


# ---- dialogs ---------------------------------------------------------------------------------------------------------------------------------------
@icon("none", "bare", "lift", "None", "Dialog pictures")
def draw_none(pen):
	"""No picture: a paper disc in a rose ring, struck through from the top left."""
	pen.shadow(6, 42, 43, SHADOW["lift"])
	pen.face(circ(24, 24, 19), MATS["paper"], band=False)
	pen.face(ring(24, 24, 19, 13.4), MATS["rose"])
	slash = rot([(9, 21), (39, 21), (39, 27), (9, 27)], 45)
	pen.raw('<g clip-path="url(#%s)">' % pen.clip(circ(24, 24, 14)))
	pen.face(poly(slash, 0.01), MATS["rose"], band=False, edge=False)
	pen.raw("</g>")


@icon("delpermanent", "bare", "body", "Delete permanently", "Dialog pictures")
def draw_delete_permanently(pen):
	"""A paper shredder: a page with its lines feeds into the slot of a dusk housing with a rose light, and comes out below as cut strips
	of uneven length. The file goes for good, not to the Recycle Bin."""
	pen.shadow(15, 37, 44, SHADOW["body"])
	strips = (9.5, 12, 8.5, 11.5, 10)
	for index, length in enumerate(strips):
		pen.face(RR(16.5 + index * 4.1, 30, 3.4, length + 2, 1), MATS["paper"], band=False)
	pen.face(poly([(13, 4, 2.5), (29, 4, 0.6), (36, 11, 0.6), (36, 24, 0.01), (13, 24, 0.01)]), MATS["paper"])
	pen.face(poly([(29, 4, 0.4), (29, 10.5, 1.2), (35.5, 11, 0.4)], 0.4), MATS["fold"], band=False)
	bars(pen, 17, 12, [10, 14, 14], 4.4)
	pen.face(RR(7, 21, 36, 11, 3.5), MATS["dusk"])
	pen.fill(RR(11, 22.6, 28, 2, 1), DARK)
	pen.fill(circ(38, 28, 1.7), RED[200])


# ---- the Explorer address bar's Go button ---------------------------------------------------------------------------------------------------------
@icon("go", "bare", "lift", "Go", "Explorer toolbar")
def draw_go(pen):
	"""Go to the address: a gold arrow on a violet disc, a button rather than the bare Forward arrow beside it."""
	pen.shadow(6, 42, 43, SHADOW["lift"])
	pen.face(circ(24, 24, 19), MATS["violet"])
	pen.face(poly([(12.5, 20.5, 1.2), (24, 20.5, 0.6), (24, 13, 1.2), (36.5, 24, 1.6), (24, 35, 1.2), (24, 27.5, 0.6), (12.5, 27.5, 1.2)]), MATS["goldl"],
		band=False, edge=False)  # the disc carries the silhouette, so the arrow keeps no edge that would brown it at 20 px


# ---- the hand-tuned 16 px frames --------------------------------------------------------------------------------------------------------------
# hint16_v2.py's characters: lowercase a material's base, uppercase its 16 px edge, digits and symbols flat details (2 orange 200, 8 dark,
# 4 paper 900, 1 indigo 400), . transparent.
ART16 = {
	"ntobject": [
		"................",
		".......FF.......",
		".....FFffFF.....",
		"...FFffffffFF...",
		"..FffffffffffF..",
		"..MFFffffffFFV..",
		"..MmmFFffFFvvV..",
		"..MmmmmFFvvvvV..",
		"..MmmmmmvvvvvV..",
		"..MmmmmmvvvvvV..",
		"..MmmmmmvvvvvV..",
		"..MmmmmmvvvvvV..",
		"...MMmmmvvvVV...",
		".....MMmvVV.....",
		".......MV.......",
		"................",
	],
	"ntdevice": [
		"................",
		".....G.G.G.G....",
		".....G.G.G.G....",
		"....DDDDDDDDD...",
		"..GGDdddddddDGG.",
		"....DdfffffdD...",
		"..GGDdf8fffdDGG.",
		"....DdfffffdD...",
		"..GGDdfffffdDGG.",
		"....DdfffffdD...",
		"..GGDdddddddDGG.",
		"....DDDDDDDDD...",
		".....G.G.G.G....",
		".....G.G.G.G....",
		"................",
		"................",
	],
	"ntport": [
		"................",
		"................",
		"..MMMMMMMMMMMMM.",
		"..MmmmmmmmmmmmM.",
		"..Mm888888888mM.",
		"..Mm828282828mM.",
		"..Mm888888888mM.",
		"..Mm888888888mM.",
		"..Mmm8888888mmM.",
		"..Mmmm88888mmmM.",
		"..MmmmmmmmmmmmM.",
		"..MMMMMMMMMMMMM.",
		"................",
		"................",
		"................",
		"................",
	],
	"regstring": [
		"................",
		"................",
		".PPPPPPPPPPPPPP.",
		".PGGppppppppppP.",
		".Pggpppppp8pppP.",
		".Pggpppppp8pppP.",
		".Pggpp88pp888pP.",
		".Pggpppp8p8pp8P.",
		".Pggpp888p8pp8P.",
		".Pggp8pp8p8pp8P.",
		".Pggpp888p888pP.",
		".PGGppppppppppP.",
		".PPPPPPPPPPPPPP.",
		"................",
		"................",
		"................",
	],
	"regbinary": [
		"................",
		"................",
		".PPPPPPPPPPPPPP.",
		".PVVppppppppppP.",
		".Pvvpp88ppp8ppP.",
		".Pvvp8pp8p88ppP.",
		".Pvvp8pp8pp8ppP.",
		".Pvvp8pp8pp8ppP.",
		".Pvvp8pp8pp8ppP.",
		".Pvvp8pp8pp8ppP.",
		".Pvvpp88pp888pP.",
		".PVVppppppppppP.",
		".PPPPPPPPPPPPPP.",
		"................",
		"................",
		"................",
	],
	"none": [
		"......RRRR......",
		"....RRrrrrRR....",
		"...RrrrrrrrrR...",
		"..Rrr444444rrR..",
		".Rrrrr444444rrR.",
		".Rr4rrr444444rR.",
		"Rrr44rrr44444rrR",
		"Rrr444rrr4444rrR",
		"Rrr4444rrr444rrR",
		"Rrr44444rrr44rrR",
		".Rr444444rrr4rR.",
		".Rrr444444rrrrR.",
		"..Rrr444444rrR..",
		"...RrrrrrrrrR...",
		"....RRrrrrRR....",
		"......RRRR......",
	],
	"delpermanent": [
		"................",
		"...PPPPPPQ......",
		"...PppppppQ.....",
		"...Pp1111pP.....",
		"...PpppppppP....",
		"...Pp11111pP....",
		"..DDDDDDDDDDDD..",
		"..D8888888888D..",
		"..DddddddddrdD..",
		"..DddddddddddD..",
		"..DDDDDDDDDDDD..",
		"....P.P.P.P.P...",
		"....P.P.P.P.P...",
		"....P.P...P.P...",
		"......P...P.....",
		"................",
	],
}


def register(gen):
	"""Bind set E's helpers, add the two emblems to the folder family, add every new icon to gen_e.py's inventory and a new sheet group,
	give the bare icons the keyline and add their hand-tuned 16 px frames to hint16_v2.py's table."""
	globals().update({name: getattr(gen, name) for name in SHARED})
	for emblem_name, (draw, pixels) in NEW_EMBLEMS.items():
		FG.EMBLEMS[emblem_name] = draw
		FG.PX_EMBLEMS[emblem_name] = pixels
	new_group, after = NEW_GROUP
	names = [name for name, _ in gen.GROUPS]
	gen.GROUPS.insert(names.index(after) + 1, (new_group, []))
	listings = {name: items for name, items in gen.GROUPS}
	for icon_id, emblem_name, label in NEW_FOLDERS:
		gen.M1_NAME[icon_id] = emblem_name
		gen.M1_H16[icon_id] = ("closed", emblem_name)
		gen.I[icon_id] = ("m1", "body", None)
		gen.HINTED.append(icon_id)
		listings[new_group].append((icon_id, label))
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
