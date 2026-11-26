# Afterglow icon sheet, variant D (best practice, light 3D): variant A's 48-grid art with a systematic depth pass, the 16 px hinted set and the sheet.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# Derived from gen_a.py. The icon drawings below are A's, unchanged; the depth pass (gradient ramps, lit-edge highlight, slim extrusion,
# contact shadow, per-size profiles) is applied by build() so every icon follows the same rules.
import math
import os
import sys

OUT = sys.argv[1]
os.makedirs(OUT + "/icons", exist_ok=True)

# ---- palette: nine colours, all from the Afterglow tokens ------------------------------------------------------------------------------
INK = "#0a1230"  # outline, the icon tile navy
BODY = "#eef1f8"  # light body
SHADE = "#b4bfce"  # body, second step (text2)
DUSK = "#42396c"  # dusk purple, detail and screens
HOR = "#4a4580"  # horizon violet
GOLD = "#ffaa40"  # the one accent
GOLDL = "#ffd08e"  # gold, light step
PALE = "#ffe7c4"  # glass, highlights
ROSE = "#f43f5e"  # destructive or error only
TILE_TOP = "#1f2554"
TILE_BOT = "#7a4562"

HEAD = """<!--
Afterglow icon sheet, variant D (best practice, light 3D): %s

(c) Copyright 2026 Liminal HQ, Scott Morris
SPDX-License-Identifier: Apache-2.0 OR MIT
-->
"""
DEFS = (
	'<linearGradient id="dusk" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>'
	% (TILE_TOP, TILE_BOT)
)


# ---- drawing helpers: one outline weight (2), round joins, radii 1 / 2 / 8 ----------------------------------------------------------------
def R(x, y, w, h, r=2, f=BODY, s=INK, sw=2):
	st = ' stroke="%s" stroke-width="%s"' % (s, sw) if s else ""
	return '<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s"%s/>' % (x, y, w, h, r, f, st)


def P(d, f=BODY, s=INK, sw=2):
	st = ' stroke="%s" stroke-width="%s"' % (s, sw) if s else ""
	return '<path d="%s" fill="%s"%s/>' % (d, f, st)


def Ci(cx, cy, r, f=BODY, s=INK, sw=2):
	st = ' stroke="%s" stroke-width="%s"' % (s, sw) if s else ""
	return '<circle cx="%s" cy="%s" r="%s" fill="%s"%s/>' % (cx, cy, r, f, st)


def Lk(d, c=INK, sw=2):
	return '<path d="%s" fill="none" stroke="%s" stroke-width="%s"/>' % (d, c, sw)


def Th(d, c, w=4):
	"""A heavy symbol stroke: ink casing one pixel wider each side than the coloured core."""
	return Lk(d, INK, w + 2) + Lk(d, c, w)


def tile(inner):
	return '<rect x="5" y="5" width="38" height="38" rx="8" fill="url(#dusk)" stroke="%s" stroke-width="2"/>' % HOR + inner


def gear(cx, cy, ro=9, f=GOLD, n=8):
	tw = 4 if ro < 13 else 8
	t = ""
	for i in range(n):
		t += '<rect x="%s" y="%s" width="%s" height="%s" rx="1" transform="rotate(%s %s %s)" fill="%s" stroke="%s" stroke-width="2"/>' % (
			cx - tw / 2, cy - ro, tw, ro, i * 360 / n, cx, cy, f, INK)
	t += Ci(cx, cy, ro - 3 if ro < 13 else ro - 5, f) + Ci(cx, cy, max(2, (ro - 3) / 3.4), INK, None)
	return t


def page(x=9, y=5, w=30, h=38, f=BODY):
	d = "M%s %s V%s a2 2 0 0 1 2-2 H%s L%s %s V%s a2 2 0 0 1 -2 2 H%s a2 2 0 0 1 -2-2 Z" % (
		x, y + h - 2, y + 2, x + w - 12, x + w, y + 12, y + h - 2, x + 2)
	fold = "M%s %s V%s a2 2 0 0 0 2 2 H%s Z" % (x + w - 12, y, y + 10, x + w)
	return P(d, f) + P(fold, SHADE)


def lines(x, y, ws, gap=6, c=DUSK):
	return "".join(Lk("M%s %s H%s" % (x, y + i * gap, x + w), c) for i, w in enumerate(ws))


def globe(cx, cy, r, f=BODY):
	return (Ci(cx, cy, r, f) + '<ellipse cx="%s" cy="%s" rx="%s" ry="%s" fill="none" stroke="%s" stroke-width="2"/>' % (cx, cy, r // 2.2, r, INK)
		+ Lk("M%s %s H%s" % (cx - r, cy, cx + r)))


def folder(open_=False, fill=GOLDL, front=GOLD):
	back = R(5, 11, 18, 10, 2, fill) + R(5, 17, 38, 26, 2, fill)
	if open_:
		return R(5, 11, 18, 10, 2, fill) + R(5, 17, 38, 14, 2, fill) + P("M11 25 H43 L37 43 H5 Z", front)
	return back + R(5, 23, 38, 20, 2, front)


def arrow_r(x0=5, yc=25, h=16):
	return P("M%s %s H21 V%s L43 %s L21 %s V%s H%s Z" % (x0, yc - 4, yc - 10, yc, yc + 10, yc + 4, x0), GOLD)


def bin_(full=False):
	t = ""
	if full:
		t += P("M13 13 L15 3 L27 5 L25 13 Z", BODY) + P("M25 13 L29 5 L39 9 L35 15 Z", GOLD)
	t += P("M11 17 L13 41 a2 2 0 0 0 2 2 H33 a2 2 0 0 0 2-2 L37 17 Z", SHADE)
	t += R(7, 11, 34, 6, 2, BODY)
	t += Lk("M19 23 V37") + Lk("M24 23 V37") + Lk("M29 23 V37")
	if not full:
		t += R(19, 5, 10, 6, 2, BODY)
	return t


def monitor(sx=7, sy=7, sw_=34, sh=26, base=True):
	t = R(sx, sy, sw_, sh, 2, BODY) + R(sx + 4, sy + 4, sw_ - 8, sh - 8, 1, DUSK)
	t += P("M%s %s a7 7 0 0 1 14 0 Z" % (sx + 10, sy + sh - 4), GOLD, None)
	if base:
		t += R(19, 33, 10, 4, 1, SHADE) + R(13, 37, 22, 4, 1, BODY)
	return t


def drive_body():
	return R(5, 15, 38, 20, 2, BODY) + R(5, 15, 38, 8, 2, SHADE) + Lk("M9 29 H25") + R(33, 27, 6, 4, 1, GOLD)


def disc(cx=24, cy=24, r=19):
	return (Ci(cx, cy, r, BODY) + Ci(cx, cy, 10, DUSK) + Ci(cx, cy, 3, INK, None)
		+ Lk("M%s %s A14 14 0 0 1 %s %s" % (cx - 14, cy - 6, cx - 6, cy - 14), GOLD, 2))


def magnifier():
	return Lk("M29 29 L40 40", INK, 8) + Lk("M29 29 L40 40", DUSK, 4) + Ci(20, 20, 13, PALE) + Lk("M13 19 A8 8 0 0 1 19 13", GOLD, 2)


def ks(cols, y0, x0=17, step=8, h=4, w=6, f=DUSK):
	return "".join(R(x0 + i * step, y0, w, h, 1, f, None) for i in range(cols))


I = {}  # id -> (kind, svg fragment)  kind: "tile" or "bare"


def add(k, kind, frag):
	I[k] = (kind, frag)


# ---- Desktop and shell ----------------------------------------------------------------------------------------------------------------
add("mycomputer", "bare", monitor())
add("mydocs", "bare", R(15, 5, 22, 20, 2, BODY) + Lk("M19 11 H33") + Lk("M19 17 H33") + folder())
add("network", "bare", Th("M24 15 V25 M11 25 H37 M11 25 V33 M37 25 V33", SHADE, 2) + R(15, 5, 18, 10, 2, BODY) + R(17, 7, 14, 6, 1, DUSK, None)
	+ R(5, 33, 14, 10, 2, BODY) + R(7, 35, 10, 6, 1, DUSK, None) + R(29, 33, 14, 10, 2, BODY) + R(31, 35, 10, 6, 1, GOLD, None))
add("browser", "tile", Ci(24, 24, 13) + '<ellipse cx="24" cy="24" rx="6" ry="13" fill="none" stroke="%s" stroke-width="2"/>' % INK
	+ Lk("M11 24 H37") + Lk("M10 34 C18 42 34 32 40 14", GOLD, 3))
add("recycle", "bare", bin_())
add("recyclefull", "bare", bin_(True))
add("appmanager", "tile", R(11, 20, 26, 16, 1, BODY) + R(9, 14, 30, 6, 1, SHADE) + R(21, 14, 6, 22, 0, GOLD))
add("cmd", "tile", R(9, 11, 30, 26, 2, BODY) + R(11, 17, 26, 18, 1, INK, None) + Lk("M15 21 L21 25 L15 29", GOLD, 3) + Lk("M24 30 H31", BODY))
add("readme", "tile", P("M24 15 C19 11 15 11 11 12 V35 C15 34 19 34 24 38 Z") + P("M24 15 C29 11 33 11 37 12 V35 C33 34 29 34 24 38 Z")
	+ P("M30 12 V23 L33 20 L36 23 V12 Z", GOLD, None) + Lk("M15 18 H20 M15 23 H20 M15 28 H20", DUSK))
add("controlpanel", "tile", R(10, 10, 28, 28, 2, BODY) + Lk("M17 14 V34 M25 14 V34 M33 14 V34") + R(14, 18, 6, 4, 1, GOLD)
	+ R(22, 28, 6, 4, 1, GOLD) + R(30, 22, 6, 4, 1, GOLD))

# ---- Control Panel applets (all tiles) ------------------------------------------------------------------------------------------------
add("access", "tile", Ci(24, 13, 4, GOLD) + P("M13 19 H35 V23 H27 V29 L31 37 H27 L24 31 L21 37 H17 L21 29 V23 H13 Z"))
add("addhw", "tile", Lk("M19 11 V15 M24 11 V15 M29 11 V15 M19 33 V37 M24 33 V37 M29 33 V37 M11 19 H15 M11 24 H15 M11 29 H15 M33 19 H37 M33 24 H37 M33 29 H37")
	+ R(15, 15, 18, 18, 2, BODY) + R(20, 20, 8, 8, 1, GOLD))
add("addremove", "tile", disc(22, 24, 11).replace('r="10"', 'r="5"').replace('r="3"', 'r="2"').replace("A14 14 0 0 1", "A8 8 0 0 1")
	+ Ci(33, 33, 7, GOLD) + Lk("M30 33 H36 M33 30 V36"))
add("admintools", "tile", '<g transform="rotate(45 24 24)">' + R(21, 20, 6, 18, 3, BODY) + Ci(24, 16, 7, GOLD) + R(22, 7, 4, 8, 0, DUSK, None) + "</g>")
add("console", "tile", R(10, 12, 28, 24, 2, BODY) + R(12, 18, 24, 16, 1, INK, None) + R(15, 23, 6, 8, 0, GOLD, None) + Lk("M25 23 H33 M25 29 H31", BODY))
add("datetime", "tile", R(10, 10, 26, 26, 2, BODY) + P("M10 18 V12 a2 2 0 0 1 2-2 H34 a2 2 0 0 1 2 2 V18 Z", GOLD)
	+ ks(3, 23, 14, 7, 3, 4) + ks(3, 29, 14, 7, 3, 4) + Ci(34, 34, 8, BODY) + Lk("M34 29 V34 H38"))
add("display", "tile", monitor(9, 10, 30, 20, False) + R(21, 30, 6, 4, 1, SHADE) + R(15, 34, 18, 3, 1, BODY))
add("folderopts", "tile", R(10, 14, 12, 8, 2, GOLDL) + R(10, 18, 28, 18, 2, GOLDL) + R(10, 24, 28, 12, 2, GOLD) + gear(33, 32, 8, BODY))
add("fonts", "tile", P("M13 37 L22 11 H26 L35 37 H30 L28 31 H20 L18 37 Z") + R(22, 25, 4, 3, 0, GOLD, None))
add("inetsettings", "tile", globe(22, 22, 10) + gear(33, 33, 8, GOLD))
add("keyboard", "tile", R(8, 15, 32, 18, 2, BODY) + ks(4, 19, 12, 7, 3, 5) + ks(4, 24, 12, 7, 3, 5) + R(14, 29, 20, 2, 0, GOLD, None))
add("mouse", "tile", R(16, 9, 16, 30, 8, BODY) + P("M16 21 V17 a8 8 0 0 1 8-8 V21 Z", GOLD) + Lk("M16 21 H32"))
add("netconn", "tile", R(15, 9, 18, 14, 2, BODY) + Lk("M19 13 V17 M24 13 V17 M29 13 V17") + R(20, 23, 8, 14, 0, GOLD) + Lk("M24 37 V40"))
add("power", "tile", Ci(24, 24, 14, BODY) + P("M26 11 L17 26 H23 L22 37 L32 21 H25 Z", GOLD))
add("printers", "tile", R(16, 9, 16, 10, 1, SHADE) + R(9, 19, 30, 14, 2, BODY) + R(15, 29, 18, 10, 1, PALE) + Lk("M19 34 H29", DUSK) + R(32, 22, 3, 3, 0, GOLD, None))
add("regional", "tile", Ci(24, 24, 13, DUSK) + P("M16 15 C20 12 22 16 20 19 C18 22 15 21 15 18 Z", GOLD, None) + P("M27 22 C32 21 34 26 30 32 C27 30 26 26 27 22 Z", GOLD, None)
	+ Ci(24, 24, 13, "none"))
add("sound", "tile", P("M11 20 H17 L25 13 V35 L17 28 H11 Z") + Lk("M29 19 A8 8 0 0 1 29 29", GOLD, 3) + Lk("M33 14 A14 14 0 0 1 33 34", GOLD, 3))
add("system", "tile", R(14, 9, 20, 30, 2, BODY) + R(17, 13, 14, 3, 0, INK, None) + Lk("M18 20 H30 M18 24 H30") + Ci(24, 32, 3, GOLD))
add("taskbarstart", "tile", R(9, 11, 30, 26, 2, BODY) + R(11, 15, 11, 14, 1, SHADE, None) + R(9, 29, 30, 8, 0, INK, None) + R(11, 31, 9, 4, 1, GOLD, None))

# ---- Explorer toolbar ----------------------------------------------------------------------------------------------------------------
add("back", "bare", P("M5 25 L21 9 V17 H43 V33 H21 V41 Z", GOLD))
add("forward", "bare", P("M43 25 L27 9 V17 H5 V33 H27 V41 Z", GOLD))
add("up", "bare", P("M25 5 L43 21 H33 V33 H17 V21 H7 Z", GOLD) + R(7, 39, 34, 4, 1, BODY))
add("search", "bare", magnifier())
add("folders", "bare", Th("M11 15 V39 M11 25 H23 M11 39 H23", SHADE, 2) + R(5, 5, 16, 10, 2, GOLDL) + R(23, 19, 20, 10, 2, GOLDL) + R(23, 33, 20, 10, 2, GOLDL))
add("move", "bare", R(5, 5, 22, 24, 2, BODY) + Lk("M10 12 H22 M10 18 H22", DUSK) + P("M17 35 H29 V31 L43 37 L29 43 V39 H17 Z", GOLD))
add("copy", "bare", R(15, 5, 22, 22, 2, SHADE) + R(5, 11, 22, 18, 2, BODY) + Lk("M10 18 H22 M10 24 H22", DUSK) + P("M17 35 H29 V31 L43 37 L29 43 V39 H17 Z", GOLD))
add("del", "bare", Th("M13 13 L35 35 M35 13 L13 35", ROSE))
add("undo", "bare", Th("M17 21 H29 a9 9 0 0 1 0 18 H15", GOLD) + P("M5 21 L17 11 V31 Z", GOLD))
add("views", "bare", R(5, 7, 38, 10, 2, BODY) + R(5, 19, 38, 10, 2, BODY) + R(5, 31, 38, 10, 2, BODY) + R(9, 10, 4, 4, 0, GOLD, None)
	+ R(9, 22, 4, 4, 0, GOLD, None) + R(9, 34, 4, 4, 0, GOLD, None) + Lk("M17 12 H37 M17 24 H37 M17 36 H37", DUSK))

# ---- Drives and folders --------------------------------------------------------------------------------------------------------------
add("hdd", "bare", drive_body())
add("cd", "bare", disc())
add("floppy", "bare", R(7, 7, 34, 34, 2, DUSK) + R(15, 7, 16, 12, 1, SHADE) + R(24, 9, 4, 8, 0, INK, None) + R(13, 25, 22, 16, 1, BODY) + Lk("M17 31 H31 M17 36 H27", DUSK))
add("netdrive", "bare", Th("M24 29 V35 M11 35 H37 M11 35 V41 M37 35 V41", SHADE, 2) + R(5, 9, 38, 20, 2, BODY) + R(5, 9, 38, 8, 2, SHADE) + Lk("M9 23 H25")
	+ R(33, 21, 6, 4, 1, GOLD) + R(5, 41, 12, 2, 0, GOLD, None) + R(31, 41, 12, 2, 0, GOLD, None))
add("folder", "bare", folder())
add("folderopen", "bare", folder(True))

# ---- File types ----------------------------------------------------------------------------------------------------------------------
add("doc", "bare", page() + lines(15, 23, [14, 14, 8]) + R(15, 15, 10, 4, 1, GOLD, None))
add("text", "bare", page() + lines(15, 17, [18, 18, 18, 10], 5))
add("image", "bare", page() + R(13, 17, 22, 20, 0, DUSK, None) + P("M13 37 L21 27 L27 33 L31 29 L35 37 Z", HOR, None) + Ci(29, 22, 3, GOLD, None))
add("program", "bare", R(5, 9, 38, 30, 2, BODY) + P("M5 17 V11 a2 2 0 0 1 2-2 H41 a2 2 0 0 1 2 2 V17 Z", GOLD) + Lk("M15 24 L21 28 L15 32", DUSK) + Lk("M25 33 H33", DUSK))
add("library", "bare", page() + gear(26, 31, 8, GOLD))
add("archive", "bare", page() + "".join(R(22 + (i % 2) * 4, 7 + i * 4, 4, 4, 0, GOLD if i % 2 else INK, None) for i in range(6)) + R(21, 31, 6, 6, 1, GOLDL))
add("font", "bare", page() + Lk("M17 35 L24 15 L31 35", INK, 3) + R(20, 27, 8, 3, 0, GOLD, None))
add("rtf", "bare", page() + R(15, 13, 18, 5, 1, GOLD, None) + lines(15, 23, [18, 12, 18], 5) + Lk("M15 38 H27", GOLD, 2))

# ---- Dialogs -------------------------------------------------------------------------------------------------------------------------
add("question", "bare", P("M7 5 H41 a2 2 0 0 1 2 2 V31 a2 2 0 0 1 -2 2 H27 L17 43 V33 H7 a2 2 0 0 1 -2-2 V7 a2 2 0 0 1 2-2 Z", HOR)
	+ Th("M19 15 a5 5 0 1 1 8 4 c-2 1.5 -3 2.5 -3 5", BODY) + Ci(24, 28, 2.5, BODY, None))
add("warning", "bare", P("M22 5 Q24 3 26 5 L43 37 Q44 41 40 41 H8 Q4 41 5 37 Z", GOLD) + Lk("M24 16 V29", INK, 4) + Ci(24, 35, 2.5, INK, None))
add("error", "bare", P("M17 5 H31 L43 17 V31 L31 43 H17 L5 31 V17 Z", ROSE) + Lk("M17 17 L31 31 M31 17 L17 31", BODY, 4))
add("info", "bare", Ci(24, 24, 19, HOR) + Lk("M24 22 V33", BODY, 4) + Ci(24, 15, 2.5, BODY, None))
add("shield", "bare", P("M24 5 L39 11 V23 C39 33 32 39 24 43 C16 39 9 33 9 23 V11 Z", HOR) + R(18, 23, 12, 10, 1, GOLD) + Lk("M20 23 V20 a4 4 0 0 1 8 0 V23", BODY, 3))

# ---- System tray ---------------------------------------------------------------------------------------------------------------------
add("volume", "bare", P("M5 19 H13 L23 10 V38 L13 29 H5 Z") + Th("M29 18 A8 8 0 0 1 29 30", GOLD, 3) + Th("M35 12 A15 15 0 0 1 35 36", GOLD, 3))
add("trynet", "bare", R(15, 7, 26, 18, 2, SHADE) + R(7, 19, 26, 18, 2, BODY) + R(11, 23, 18, 10, 1, DUSK, None) + R(15, 27, 4, 3, 0, GOLD, None)
	+ R(13, 39, 14, 4, 1, BODY))
add("kbdlayout", "bare", R(5, 13, 38, 22, 2, BODY) + ks(5, 17, 9, 7, 3, 5) + ks(5, 22, 9, 7, 3, 5) + R(13, 28, 22, 3, 0, GOLD, None))
add("clock", "bare", Ci(24, 24, 19, BODY) + Lk("M24 12 V24 H33") + Ci(24, 24, 3, GOLD))
add("showdesk", "bare", R(5, 9, 38, 30, 2, DUSK) + P("M13 29 a7 7 0 0 1 14 0 Z", GOLD, None) + R(5, 31, 38, 8, 0, INK, None) + R(33, 32, 8, 6, 1, GOLD, None))

# ---- Start menu ----------------------------------------------------------------------------------------------------------------------
add("programs", "bare", R(5, 5, 17, 17, 2, BODY) + R(26, 5, 17, 17, 2, GOLD) + R(5, 26, 17, 17, 2, BODY) + R(26, 26, 17, 17, 2, BODY))
add("documents", "bare", R(15, 5, 24, 30, 2, SHADE) + R(9, 11, 24, 32, 2, BODY) + Lk("M14 20 H28 M14 26 H28 M14 32 H22", DUSK) + R(14, 15, 8, 3, 0, GOLD, None))
add("settings", "bare", gear(24, 24, 19, GOLD, 8))
add("help", "bare", Ci(24, 24, 19, GOLD) + Th("M19 18 a5 5 0 1 1 8 4 c-2 1.5 -3 2.5 -3 5", INK, 3) + Ci(24, 33, 2.5, INK, None))
add("run", "bare", R(5, 9, 38, 30, 2, BODY) + P("M5 17 V11 a2 2 0 0 1 2-2 H41 a2 2 0 0 1 2 2 V17 Z", DUSK) + P("M19 23 L33 29 L19 35 Z", GOLD))
add("shutdown", "bare", Th("M15 14 a14 14 0 1 0 18 0", ROSE) + Th("M24 6 V24", ROSE))

# ---- 16 px hinted variants (1 px outline centred on pixel centres) ------------------------------------------------------------------------
def r16(x, y, w, h, f, s=INK):
	st = ' stroke="%s" stroke-width="1"' % s if s else ""
	return '<rect x="%s" y="%s" width="%s" height="%s" fill="%s"%s/>' % (x, y, w, h, f, st)


def p16(d, f, s=INK):
	st = ' stroke="%s" stroke-width="1" stroke-linejoin="round"' % s if s else ""
	return '<path d="%s" fill="%s"%s/>' % (d, f, st)


H16 = {
	"folder": p16("M1.5 13.5 V3.5 H6.5 L8.5 5.5 H14.5 V13.5 Z", GOLDL) + r16(1.5, 7.5, 13, 6, GOLD),
	"doc": p16("M3.5 1.5 H10.5 L13.5 4.5 V14.5 H3.5 Z", BODY) + p16("M10.5 1.5 V4.5 H13.5", SHADE) + r16(5, 8, 6, 1, DUSK, None) + r16(5, 11, 6, 1, DUSK, None),
	"warning": p16("M8 1.5 L14.5 13.5 H1.5 Z", GOLD) + r16(7, 5, 2, 5, INK, None) + r16(7, 11, 2, 1, INK, None),
	"error": p16("M5.5 1.5 H10.5 L14.5 5.5 V10.5 L10.5 14.5 H5.5 L1.5 10.5 V5.5 Z", ROSE)
		+ '<path d="M5.5 5.5 L10.5 10.5 M10.5 5.5 L5.5 10.5" stroke="%s" stroke-width="2" fill="none"/>' % BODY,
	"recyclefull": p16("M5.5 4.5 L6.5 0.5 H10.5 L10.5 4.5", GOLD) + p16("M3.5 5.5 L4.5 14.5 H11.5 L12.5 5.5", SHADE) + r16(2.5, 3.5, 11, 2, BODY)
		+ r16(6, 7, 1, 5, INK, None) + r16(9, 7, 1, 5, INK, None),
	"hdd": r16(1.5, 4.5, 13, 8, SHADE) + r16(3, 9, 5, 1, INK, None) + r16(10, 8, 3, 2, GOLD, None),
	"search": '<circle cx="6.5" cy="6.5" r="4" fill="%s" stroke="%s" stroke-width="1"/>' % (PALE, INK)
		+ '<path d="M9.5 9.5 L13.5 13.5" stroke="%s" stroke-width="3" stroke-linecap="round"/><path d="M9.5 9.5 L13.5 13.5" stroke="%s" stroke-width="1" stroke-linecap="round"/>' % (INK, DUSK),
	"mycomputer": r16(1.5, 1.5, 13, 9, BODY) + r16(3, 3, 10, 6, DUSK, None) + r16(6, 6, 4, 2, GOLD, None) + r16(5.5, 12.5, 5, 2, BODY),
}



# ---- the one drawing change from A: the full bin's papers sit 2 px lower, so the raised face still clears the top edge by 2 px -------------
I["recyclefull"] = ("bare", I["recyclefull"][1].replace("M13 13 L15 3 L27 5 L25 13 Z", "M13 15 L15 5 L27 7 L25 15 Z").replace(
	"M25 13 L29 5 L39 9 L35 15 Z", "M25 15 L29 7 L39 11 L35 17 Z"))

# ---- depth pass ------------------------------------------------------------------------------------------------------------------------
import re
import xml.etree.ElementTree as ET


def _rgb(c):
	return [int(c[i:i + 2], 16) for i in (1, 3, 5)]


def mix(a, b, t):
	return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(_rgb(a), _rgb(b)))


WHITE = "#ffffff"
# Side (extrusion) tone for each A colour: the next step down its own ramp, no new hues.
SIDE = {BODY: SHADE, SHADE: "#8692a8", GOLDL: "#e39c48", GOLD: "#c4741c", PALE: "#e6c08a", DUSK: "#2a2350", HOR: "#2f2b5c", ROSE: "#a8243e", INK: INK}
RAMP = [BODY, SHADE, GOLDL, GOLD, PALE, DUSK, HOR, ROSE]
TILE_SIDE = "#4a2a44"  # the plate's extrusion: TILE_BOT stepped down
TILE_HL = "#6e68a8"  # the plate's lit edge: horizon stepped up


def lit(c):
	return mix(c, WHITE, 0.35)


def low(c):
	return mix(c, SIDE[c], 0.2)


def hl(c):
	return mix(c, WHITE, 0.6)


def gid(c):
	return "g" + c[1:]


# One two-stop ramp per surface colour, upper left (lit) to lower right; Microsoft's default gradient angle is 120 degrees.
GRADS = "".join(
	'<linearGradient id="%s" x1="0" y1="0" x2="0.6" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (gid(c), lit(c), low(c))
	for c in RAMP)
SOFT = '<filter id="soft" x="-30%" y="-300%" width="160%" height="700%"><feGaussianBlur stdDeviation="1"/></filter>'
DEFS_D = DEFS + GRADS + SOFT

# Tiers: solid bodies extrude; symbols and toolbar glyphs only lift (ramp, lit edge, light shadow); stroke-only marks stay flat.
FLAT = {"del", "undo", "shutdown"}
LIFT = {"cd", "back", "forward", "up", "search", "folders", "move", "copy", "views", "question", "warning", "error", "info", "shield", "volume", "settings", "help"}


def tier(k):
	if I[k][0] == "tile":
		return "tile"
	return "flat" if k in FLAT else "lift" if k in LIFT else "solid"


# Per-size profiles. raise and ext are in 48-grid units; at 24 px every value halves to whole pixels.
PROF = {
	48: dict(raise_=2, ext=(2, 4), steps=4, hl=True, shadow=True),
	24: dict(raise_=2, ext=(2, 4), steps=4, hl=False, shadow=True),
	16: dict(raise_=0, ext=(3, 3), steps=3, hl=False, shadow=False),
}
SHADOW_OP = {"solid": 0.35, "tile": 0.35, "lift": 0.22}


def path_pts(d):
	toks = re.findall(r"[A-Za-z]|-?(?:\d+\.?\d*|\.\d+)", d)
	i, cx, cy, sx, sy, cmd, pts = 0, 0.0, 0.0, 0.0, 0.0, "M", []

	def num():
		nonlocal i
		i += 1
		return float(toks[i - 1])

	while i < len(toks):
		if toks[i].isalpha():
			cmd = toks[i]
			i += 1
		C, rel = cmd.upper(), cmd.islower()
		ox, oy = (cx, cy) if rel else (0.0, 0.0)
		if C == "Z":
			cx, cy = sx, sy
			continue
		if C in "ML":
			cx, cy = num() + ox, num() + oy
			if C == "M":
				sx, sy = cx, cy
				cmd = "l" if rel else "L"
		elif C == "H":
			cx = num() + ox
		elif C == "V":
			cy = num() + oy
		elif C in "CQ":
			for _ in range(3 if C == "C" else 2):
				px, py = num() + ox, num() + oy
				pts.append((px, py))
			cx, cy = px, py
		elif C == "A":
			for _ in range(5):
				num()
			cx, cy = num() + ox, num() + oy
		pts.append((cx, cy))
	return pts


def _rot(pts, tr):
	m = re.match(r"rotate\(([-\d.]+) ([-\d.]+) ([-\d.]+)\)", tr or "")
	if not m:
		return pts
	a, ox, oy = [float(v) for v in m.groups()]
	c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
	return [(ox + (x - ox) * c - (y - oy) * s, oy + (x - ox) * s + (y - oy) * c) for x, y in pts]


def bbox(e, tr=None):
	a, t = e.attrib, e.tag
	f = lambda n: float(a.get(n, 0))
	if t == "g":
		bs = [bbox(c, a.get("transform")) for c in e]
		return (min(b[0] for b in bs), min(b[1] for b in bs), max(b[2] for b in bs), max(b[3] for b in bs))
	if t == "rect":
		pts = [(f("x"), f("y")), (f("x") + f("width"), f("y") + f("height")), (f("x"), f("y") + f("height")), (f("x") + f("width"), f("y"))]
	elif t in ("circle", "ellipse"):
		rx = f("r") or f("rx")
		ry = f("r") or f("ry")
		pts = [(f("cx") - rx, f("cy") - ry), (f("cx") + rx, f("cy") + ry), (f("cx") - rx, f("cy") + ry), (f("cx") + rx, f("cy") - ry)]
	else:
		pts = path_pts(a["d"])
	pts = _rot(_rot(pts, a.get("transform")), tr)
	h = float(a.get("stroke-width", 0)) / 2 if a.get("stroke") else 0
	return (min(p[0] for p in pts) - h, min(p[1] for p in pts) - h, max(p[0] for p in pts) + h, max(p[1] for p in pts) + h)


def ser(e, **kw):
	e = ET.fromstring(ET.tostring(e))
	for n, v in kw.items():
		n = n.replace("_", "-")
		if v is None:
			e.attrib.pop(n, None)
		else:
			e.set(n, str(v))
	return ET.tostring(e, encoding="unicode")


def build(k, size, prefix=""):
	"""Return (defs, body) for icon k at a size profile."""
	p = PROF[size]
	kind, frag = I[k]
	tr = tier(k)
	if tr == "flat":
		return "", frag
	pre = "%s%s-%d" % (prefix, k, size)
	els = list(ET.fromstring("<g>" + frag + "</g>"))
	defs, n = [], [0]

	def face(e, grouped=False):
		if e.tag == "g":
			return "<g%s>%s</g>" % ("".join(' %s="%s"' % kv for kv in e.attrib.items()), "".join(face(c, True) for c in e))
		c = e.get("fill")
		if c not in RAMP:
			return ser(e)
		x0, y0, x1, y1 = bbox(e)
		big = x1 - x0 >= 10 and y1 - y0 >= 10
		if not (p["hl"] and big and e.get("stroke") == INK and not e.get("transform") and not grouped):
			return ser(e, fill="url(#%s)" % gid(c))
		n[0] += 1
		cid = "%s-c%d" % (pre, n[0])
		bare = dict(stroke=None, stroke_width=None)
		defs.append('<clipPath id="%s">%s</clipPath>' % (cid, ser(e, fill="#000", **bare)))
		return (ser(e, fill=hl(c), **bare) + '<g clip-path="url(#%s)"><g transform="translate(2 2)">%s</g></g>' % (cid, ser(e, fill="url(#%s)" % gid(c), **bare))
			+ ser(e, fill="none"))

	content = "".join(face(e) for e in els)
	sil, edge = [], INK
	if tr == "tile":
		plate = ET.fromstring('<rect x="5" y="5" width="38" height="38" rx="8" fill="url(#dusk)" stroke="%s" stroke-width="2"/>' % HOR)
		pl = ser(plate)
		if p["hl"]:
			n[0] += 1
			cid = "%s-c%d" % (pre, n[0])
			defs.append('<clipPath id="%s">%s</clipPath>' % (cid, ser(plate, fill="#000", stroke=None, stroke_width=None)))
			pl = (ser(plate, fill=TILE_HL, stroke=None, stroke_width=None) + '<g clip-path="url(#%s)"><g transform="translate(2 2)">%s</g></g>' % (cid, ser(plate, stroke=None, stroke_width=None))
				+ ser(plate, fill="none"))
		content = pl + content
		sil, edge = [plate], HOR
	elif tr == "solid":
		sil = [e for e in els if e.get("stroke")]
	extr = ""
	dx, dy = (p["ext"] if sil else (0, 0))
	rz = p["raise_"] if sil else 0
	if sil:
		ink = side = ""
		for e in sil:
			fc = e.get("fill")
			if fc and fc != "none":
				ink += ser(e, fill=edge, stroke=edge)
				side += ser(e, fill=TILE_SIDE if tr == "tile" else SIDE.get(fc, INK), stroke=None, stroke_width=None)
			else:
				ink += ser(e, stroke=edge)
				if e.get("stroke") != INK:
					side += ser(e, stroke=SIDE.get(e.get("stroke"), INK))
		defs.append('<g id="%s-xi">%s</g><g id="%s-xs">%s</g>' % (pre, ink, pre, side))
		st = p["steps"]
		for layer in ("xi", "xs"):
			for i in range(1, st + 1):
				extr += '<use href="#%s-%s" transform="translate(%g %g)"/>' % (pre, layer, dx * i / st, dy * i / st)
	shadow = ""
	if p["shadow"]:
		bs = [bbox(e) for e in (sil or els)]
		x0, x1, y1 = min(b[0] for b in bs), max(b[2] for b in bs) + dx, max(b[3] for b in bs) + dy - rz
		rx = (x1 - x0) * 0.42
		shadow = '<ellipse cx="%g" cy="%g" rx="%g" ry="1.6" fill="%s" opacity="%s" filter="url(#soft)"/>' % ((x0 + x1) / 2 + 1, min(y1 - 0.5, 45.5), rx, INK, SHADOW_OP[tr])
	body = shadow + ('<g transform="translate(0 %d)">%s%s</g>' % (-rz, extr, content) if rz else extr + content)
	return "".join(defs), body


# ---- 16 px hinted redraws: A's drawings; solids gain a 1 px lower-right edge in their side tone ------------------------------------------
def edge16(svg):
	out = ""
	for e in ET.fromstring("<g>" + svg + "</g>"):
		fc = e.get("fill")
		if e.get("stroke") and fc in SIDE:
			s = SIDE[fc]
			out += '<g transform="translate(1 1)">%s</g>' % ser(e, fill=s, stroke=s)
	return out + svg


H16D = {k: (edge16(v) if tier(k) == "solid" else v) for k, v in H16.items()}


def symbol(k, body, vb=48):
	return '<symbol id="%s" viewBox="0 0 %d %d" overflow="visible">%s</symbol>' % (k, vb, vb, body)


def standalone(body, defs="", vb=48, title=""):
	return (HEAD % title + '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" stroke-linejoin="round" stroke-linecap="round">\n<defs>%s%s</defs>\n%s\n</svg>\n'
		% (vb, vb, vb, vb, DEFS_D, defs, body))

LABEL = {}
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
		("folderopen", "Folder (open)"), ("mycomputer", "My Computer")]),
	("File types", [("doc", "Document"), ("text", "Text"), ("image", "Image"), ("program", "Program"), ("library", "Library (DLL)"), ("archive", "Archive"),
		("font", "Font"), ("rtf", "Rich text (.RTF)")]),
	("Dialogs", [("question", "Question"), ("warning", "Warning"), ("error", "Error"), ("info", "Information"), ("shield", "Security")]),
	("System tray", [("volume", "Volume"), ("trynet", "Network"), ("kbdlayout", "Keyboard layout"), ("clock", "Clock"), ("showdesk", "Show desktop")]),
	("Start menu", [("programs", "Programs"), ("documents", "Documents"), ("settings", "Settings"), ("search", "Search"), ("help", "Help"), ("run", "Run"),
		("shutdown", "Shut Down")]),
]

# individual files: 48 master, the 24 and 16 profiles, the hinted 16 redraws
for sub in ("24", "16"):
	os.makedirs("%s/icons/%s" % (OUT, sub), exist_ok=True)
for k in I:
	for size, path in ((48, "%s/icons/%s.svg"), (24, "%s/icons/24/%s.svg"), (16, "%s/icons/16/%s.svg")):
		d, b = build(k, size)
		open(path % (OUT, k), "w").write(standalone(b, d, 48, "%s (%s profile)" % (k, size)))
for k, b in H16D.items():
	open("%s/icons/%s-16.svg" % (OUT, k), "w").write(standalone(b, "", 16, k + " (16 px hinted)"))

# ---- the sheet ----------------------------------------------------------------------------------------------------------------------------
W = 1712
CW, CH, GAP = 200, 88, 4
BG, CELL, LAB, HD = "#0c0c10", "#14161d", "#e0e0e0", "#ffd08e"
CREAM = "#d4d0c8"
VOID = "#060609"
out = []
sdefs, syms = [], []
for k in I:
	for size, sid in ((48, k), (24, k + "-24"), (16, k + "-16")):
		d, b = build(k, size)
		sdefs.append(d)
		syms.append(symbol(sid, b))
for k, b in H16D.items():
	syms.append(symbol(k + "-h16", b, 16))
	syms.append(symbol(k + "-a16", H16[k], 16))


def txt(x, y, s, size=12, fill=LAB, anchor="start", weight=400, fam="Inter, 'DejaVu Sans', sans-serif"):
	s = s.replace("&", "&amp;").replace("<", "&lt;")
	return '<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" fill="%s" text-anchor="%s">%s</text>' % (x, y, fam, size, weight, fill, anchor, s)


def use(k, x, y, size=48, extra=""):
	return '<use href="#%s" x="%s" y="%s" width="%s" height="%s"%s/>' % (k, x, y, size, size, extra)


y = 40
out.append(txt(40, y + 14, "Afterglow icons · variant D, best practice in light 3D", 30, "#ffffff", weight=600))
y += 36
for line in [
	"Variant A's grid, keylines, 2 px outline, radii, palette and metaphors, with one systematic depth pass: light from the upper left, one two-stop ramp per surface, a 1 px lit edge,",
	"a slim lower-right extrusion on solid bodies (4 px deep, 2 px across at 48), a soft contact shadow, and a raised dusk plate for apps. Symbols only lift; stroke-only marks stay flat.",
	"Depth halves to whole pixels at 24, drops to a 1 px lower-right edge at 16, and the eight hinted 16 px redraws keep A's crisp drawing plus that edge. No translucency, no reflections.",
]:
	y += 20
	out.append(txt(40, y, line, 13, "#b4bfce"))
y += 28

# construction: keylines and the depth anatomy at 2x
out.append(txt(40, y, "Construction · keylines at 2×, face raised 2 px, extrusion and shadow in the bottom margin", 15, HD, weight=600))
y += 14
kx = 40
for k, label, shape in [("doc", "Portrait 32 × 40", "p"), ("cd", "Circle 40 · lift", "c"), ("folder", "Landscape 40 × 32", "l"), ("floppy", "Square 36", "s"),
		("warning", "Badge · lift", "n"), ("browser", "Plate 40, radius 8", "t")]:
	out.append('<rect x="%s" y="%s" width="104" height="124" rx="6" fill="%s"/>' % (kx, y, CELL))
	gx, gy = kx + 4, y + 4
	g = ""
	for i in range(0, 49, 4):
		g += '<path d="M%s 0 V96 M0 %s H96" stroke="#262a37" stroke-width="0.5" fill="none"/>' % (i * 2, i * 2)
	lift = 0 if tier(k) == "lift" else -4
	kl = {"p": '<rect x="16" y="%d" width="64" height="80"' % (8 + lift), "c": '<circle cx="48" cy="48" r="40"', "l": '<rect x="8" y="%d" width="80" height="64"' % (16 + lift),
		"s": '<rect x="12" y="%d" width="72" height="72"' % (12 + lift), "t": '<rect x="8" y="%d" width="80" height="80" rx="16"' % (8 + lift),
		"n": '<rect x="8" y="8" width="80" height="80"'}[shape]
	kl += ' fill="none" stroke="%s" stroke-width="1" stroke-dasharray="4 3"/>' % ROSE
	out.append('<g transform="translate(%s %s)"><rect width="96" height="96" fill="#090e2a"/>%s%s%s</g>' % (gx, gy, g, use(k, 0, 0, 96), kl))
	out.append(txt(kx + 52, y + 116, label, 11, "#b4bfce", "middle"))
	kx += 116
# light key and ramps
px = 40 + 6 * 116 + 24
out.append(txt(px, y + 14, "Ramps · lit stop, A's colour, low stop, side, lit edge", 13, HD, weight=600))
for i, c in enumerate(RAMP):
	sx, sy = px + (i % 4) * 172, y + 28 + (i // 4) * 40
	for j, cc in enumerate([lit(c), c, low(c), SIDE[c], hl(c)]):
		out.append('<rect x="%s" y="%s" width="20" height="28" fill="%s" stroke="#4a4580" stroke-width="1"/>' % (sx + j * 20, sy, cc))
	out.append(txt(sx + 106, sy + 12, {BODY: "body", SHADE: "shade", GOLDL: "gold light", GOLD: "gold", PALE: "pale", DUSK: "dusk", HOR: "horizon", ROSE: "rose"}[c], 11))
	out.append(txt(sx + 106, sy + 25, c, 10, "#7c8796", fam="'DejaVu Sans Mono', monospace"))
lx, ly = px, y + 112
out.append('<path d="M%s %s L%s %s" stroke="%s" stroke-width="2" fill="none"/><path d="M%s %s l-1 -7 l7 1 z" fill="%s"/>' % (lx + 22, ly + 22, lx + 6, ly + 6, GOLD, lx + 4, ly + 4, GOLD))
out.append(txt(lx + 34, ly + 10, "One light, upper left. Ramp 120°-ish, extrusion (2, 4), shadow offset 1 right. Plate: %s to %s, side %s, lit edge %s." % (TILE_TOP, TILE_BOT, TILE_SIDE, TILE_HL), 11, "#b4bfce"))
out.append(txt(lx + 34, ly + 25, "Shadow: ink ellipse, ry 1.6, blur 1, 35 % under solids and plates, 22 % under symbols. Ink stays flat.", 11, "#b4bfce"))
y += 144

# proof strips: void, cream, dusk
keys = ["folder", "doc", "warning", "error", "hdd", "mycomputer", "recyclefull", "search", "clock", "browser", "controlpanel", "cmd", "volume", "settings", "shutdown"]
PW = 52
stripw = len(keys) * PW + 16
rowh = 130


def strip(x0, y0, fill, name, namec):
	r = ['<rect x="%s" y="%s" width="%s" height="%s" rx="6" fill="%s"/>' % (x0, y0, stripw, rowh, fill)]
	r.append(txt(x0 + stripw - 10, y0 + 124, name, 10, namec, "end"))
	for i, k in enumerate(keys):
		x = x0 + 10 + i * PW
		s16 = k + "-h16" if k in H16D else k + "-16"
		r.append(use(k, x, y0 + 6, 48) + use(k, x + 8, y0 + 58, 32) + use(k + "-24", x, y0 + 96, 24) + use(s16, x + 28, y0 + 100, 16))
	return "".join(r)


out.append(txt(40, y + 14, "Proof strip · 48, 32, then 24 and 16 (hinted where drawn) on void, cream and dusk", 15, HD, weight=600))
y += 26
out.append(strip(40, y, VOID, "void", "#7c8796") + strip(40 + stripw + 16, y, CREAM, "cream", "#5a5560"))
y += rowh + 10
out.append('<linearGradient id="duskbg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/></linearGradient>' % (TILE_TOP, DUSK))
out.append(strip(40, y, "url(#duskbg)", "dusk", "#b4bfce"))
sx = 40 + stripw + 16
out.append('<rect x="%s" y="%s" width="%s" height="%s" rx="6" fill="%s"/>' % (sx, y, W - 40 - sx, rowh, CELL))
out.append(txt(sx + 12, y + 18, "State variants", 12, HD, weight=600))
st = [("normal", "folder", ""), ("open", "folderopen", ""), ("disabled", "folder", ' opacity="0.35"'), ("selected", "folder", "sel"), ("full", "recyclefull", ""), ("tile", "controlpanel", ""), ("lift", "info", ""), ("flat", "del", "")]
for i, (nm, k, ex) in enumerate(st):
	x = sx + 16 + i * 98
	if ex == "sel":
		out.append('<rect x="%s" y="%s" width="56" height="56" rx="4" fill="%s"/>' % (x - 4, y + 32, HOR))
		out.append(use(k, x, y + 36, 48))
	else:
		out.append(use(k, x, y + 36, 48, ex))
	out.append(txt(x + 24, y + 108, nm, 10, "#b4bfce", "middle"))
y += rowh + 10

# 16 px: A hinted, D 16 profile, D hinted
out.append('<rect x="40" y="%s" width="%s" height="112" rx="6" fill="%s"/>' % (y, W - 80, CELL))
out.append(txt(52, y + 18, "16 px: A's hinted redraw, D's 16 profile (scaled master, depth cut to a 1 px lower-right step), and D's hinted redraw (A's pixels plus a 1 px side-tone edge on solids)", 12, HD, weight=600))
for i, k in enumerate(H16D):
	x = 52 + i * 204
	for j, (sid, lab, bgc) in enumerate(((k + "-a16", "A hinted", None), (k + "-16", "D profile", None), (k + "-h16", "D hinted", None), (k + "-h16", "on cream", CREAM))):
		yy = y + 30 + (j % 2) * 26
		xx = x + (j // 2) * 98
		if bgc:
			out.append('<rect x="%s" y="%s" width="20" height="20" fill="%s"/>' % (xx - 2, yy - 2, bgc))
		out.append(use(sid, xx, yy, 16) + txt(xx + 24, yy + 12, lab, 10, "#7c8796"))
	out.append(txt(x, y + 100, k, 10, "#b4bfce"))
y += 112 + 22

# groups
for gname, items in GROUPS:
	out.append(txt(40, y + 14, "%s · %d" % (gname, len(items)), 15, HD, weight=600))
	y += 24
	rows = (len(items) + 7) // 8
	for i, (k, label) in enumerate(items):
		cx = 40 + (i % 8) * (CW + GAP)
		cy = y + (i // 8) * (CH + GAP)
		out.append('<rect x="%s" y="%s" width="%s" height="%s" rx="6" fill="%s"/>' % (cx, cy, CW, CH, CELL))
		out.append(use(k, cx + (CW - 48) / 2, cy + 8, 48))
		out.append(txt(cx + CW / 2, cy + 74, label, 12, LAB, "middle"))
	y += rows * (CH + GAP) + 16
H = y + 16
sheet = (HEAD % "the full sheet" + '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d" stroke-linejoin="round" stroke-linecap="round">\n'
	% (W, H, W, H))
sheet += '<title>Afterglow icons, variant D (best practice, light 3D)</title>\n<defs>%s\n%s\n%s\n</defs>\n<rect width="%d" height="%d" fill="%s"/>\n' % (DEFS_D, "".join(sdefs), "\n".join(syms), W, H, BG)
sheet += "\n".join(out) + "\n</svg>\n"
open(OUT + "/sheet.svg", "w").write(sheet)
print("icons", len(I), "hinted", len(H16D), "groups", len(GROUPS), "listings", sum(len(g[1]) for g in GROUPS), "size", W, H)
