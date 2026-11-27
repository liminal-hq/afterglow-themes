#!/usr/bin/env python3
# Afterglow panels: the larger RT_BITMAP pictures ReactOS 0.4.16 shows around its icons, drawn as vector masters at their own pixel size: the
# Taskbar and Start Menu Properties previews (explorer.exe, run as agexplorer.exe), the wizard watermarks and headers, the credential
# prompt's banner, Display Properties' monitor and Task Manager's tray meter.
# Usage: gen_panels.py OUT_DIR [FONT_DIR]   writes OUT_DIR/NAME.svg for every panel in PANELS and OUT_DIR/panels.json, their sizes and keys
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# Every panel is one SVG whose viewBox is the bitmap's own size, so render.py rasterises it 1:1. The icons a panel shows are the icon set's
# own drawings, inlined from gen_e.py (the hand-tuned 16 px frame where a panel shows an icon at 16 px, the 48 px master scaled where it
# shows one larger), and the few words a preview carries ("Start", the clock, the window names) are outlined from DejaVu Sans by
# desktop/dialogs/outline.py, so no font is needed to render a master. The previews follow the Afterglow desktop: the Dusk sky above, the
# near-black taskbar with the gold Start button, dark task buttons and the sunken tray. PANELS gives each panel's size and the form
# strips.py writes it in. Deterministic: no randomness, no clock, no environment input.
import importlib.util
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))


def load(name, path):
	spec = importlib.util.spec_from_file_location(name, path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


E = load("gen_e", os.path.join(HERE, "gen_e.py"))
OUTLINE = load("outline", os.path.join(HERE, "..", "dialogs", "outline.py"))
_n = E._n
SKY1, SKY4, SKY7, HORIZON, DESKTOP = E.SKY1, E.SKY4, E.SKY7, E.HORIZON, E.DESKTOP
GOLD, GOLDL, PALE, CREAM = E.ORANGE[200], E.BRAND_GOLD, E.PALE, E.CREAM
BAR, BAR_LINE, BUTTON, BUTTON_DOWN, WELL = "#0d0e16", E.INDIGO[600], E.INDIGO[700], E.INDIGO[800], "#08080e"
TEXT, TEXT_DARK = E.PAPER[800], E.ORANGE[600]
MAGENTA = (255, 0, 255)

HEAD = """<!--
Afterglow panel: %s

(c) Copyright 2026 Liminal HQ, Scott Morris
SPDX-License-Identifier: Apache-2.0 OR MIT

Drawn by desktop/icons/gen_panels.py at the bitmap's own size; render.py writes it as %s. The icons are the Afterglow icon set's own
drawings and the words are outlined from DejaVu Sans, so no font is needed to render it.
-->
"""


class Panel:
	"""An SVG being built: defs and body, with ids unique to the panel."""

	def __init__(self, name, width, height):
		self.name, self.width, self.height = name, width, height
		self.defs, self.body, self.count = [], [], 0

	def uid(self, kind):
		self.count += 1
		return "%s-%s%d" % (self.name, kind, self.count)

	def gradient(self, stops, x1=0, y1=0, x2=0, y2=1):
		gid = self.uid("g")
		self.defs.append('<linearGradient id="%s" x1="%s" y1="%s" x2="%s" y2="%s">%s</linearGradient>' % (gid, x1, y1, x2, y2, "".join(
			'<stop offset="%s" stop-color="%s"/>' % (_n(offset), colour) for offset, colour in stops)))
		return "url(#%s)" % gid

	def rect(self, x, y, width, height, fill, radius=0, extra=""):
		self.body.append('<rect x="%s" y="%s" width="%s" height="%s"%s fill="%s"%s/>' % (_n(x), _n(y), _n(width), _n(height),
			' rx="%s"' % _n(radius) if radius else "", fill, extra))

	def path(self, d, fill, extra=""):
		self.body.append('<path d="%s" fill="%s"%s/>' % (d, fill, extra))

	def icon(self, icon_id, x, y, size):
		"""An icon of the set: the hand-tuned 16 px frame at 16 where there is one, otherwise its master for that size, scaled to fit."""
		if size == 16 and icon_id in E.HINTED:
			self.body.append('<g transform="translate(%s %s)" shape-rendering="crispEdges">%s</g>' % (_n(x), _n(y), E.hinted(icon_id)))
			return
		profile = 16 if size <= 16 else 32 if size <= 32 else 48
		defs, body = E.build(icon_id, profile, self.uid("i"))
		self.defs.append(defs)
		self.body.append('<g transform="translate(%s %s) scale(%s)">%s</g>' % (_n(x), _n(y), _n(size / 48), body))

	def text(self, words, x, baseline, size, fill, tracking=0.0):
		d, advance = OUTLINE.text_path(FONT, words, size, x, baseline, tracking)
		self.path(d, fill)
		return advance

	def svg(self, title, form):
		return (HEAD % (title, form) + '<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" viewBox="0 0 %d %d">\n<title>%s</title>\n<defs>%s</defs>\n%s\n</svg>\n'
			% (self.width, self.height, self.width, self.height, title, "".join(self.defs), "\n".join(self.body)))


FONT = None


# ---- the Taskbar and Start Menu Properties previews (explorer.exe 145 to 189) -----------------------------------------------------------------
def desk_sky(panel, height):
	panel.rect(0, 0, panel.width, height, panel.gradient([(0, SKY1), (1, SKY4)]))


def taskbar(panel, top):
	panel.rect(0, top, panel.width, panel.height - top, BAR)
	panel.rect(0, top, panel.width, 1, BAR_LINE)


def start_button(panel, x, y):
	"""The gold Start button: the sun on its horizon and the word, dark on gold."""
	panel.rect(x, y, 55, 20, GOLD, 4)
	panel.rect(x, y, 55, 1, GOLDL, 0)
	panel.path("M%s %s a5 5 0 0 1 10 0 Z" % (_n(x + 5), _n(y + 13)), E.ORANGE[500])
	panel.rect(x + 4, y + 13, 12, 1.4, E.ORANGE[500])
	panel.text("Start", x + 19, y + 14.5, 11, TEXT_DARK)


def grip(panel, x, y, height):
	for row in range(int(height // 3)):
		panel.rect(x, y + row * 3, 2, 2, BAR_LINE)


def task_button(panel, x, y, width, icon_id, label, grouped=False, pressed=False):
	panel.rect(x, y, width, 20, BUTTON_DOWN if pressed else BUTTON, 3)
	panel.rect(x + 2, y, width - 4, 1, E.INDIGO[500])
	panel.icon(icon_id, x + 3, y + 2, 16)
	panel.text(label, x + 23, y + 14.5, 11, TEXT)
	if grouped:
		panel.path("M%s %s h7 l-3.5 4 Z" % (_n(x + width - 12), _n(y + 8.5)), TEXT)


def taskbar_preview(panel, lock, group, quick_launch):
	desk_sky(panel, 9)
	taskbar(panel, 9)
	start_button(panel, 3, 12)
	x = 62
	if not lock:
		grip(panel, x, 13, 18)
		x += 6
	if quick_launch:
		for icon_id in ("showdesktop", "explorer"):
			panel.icon(icon_id, x + 2, 14, 16)
			x += 21
		if not lock:
			grip(panel, x + 1, 13, 18)
			x += 6
		x += 4
	if group:
		task_button(panel, x, 12, 150, "folder", "ReactOS Explorer", grouped=True, pressed=True)
		task_button(panel, x + 154, 12, 150, "paint", "lake.bmp - Paint")
	else:
		task_button(panel, x, 12, 150, "mydocs", "My Documents", pressed=True)
		task_button(panel, x + 154, 12, 150, "mymusic", "My Music")


def tray_preview(panel, show_icons, clock, desk):
	desk_sky(panel, 9)
	taskbar(panel, 9)
	parts = []
	if not show_icons:
		parts.append(("chevron", 12))
	else:
		parts.append(("volume", 21))
	parts.append(("trynet", 21))
	if clock:
		parts.append(("clock", 56 if clock == "seconds" else 38))
	if desk:
		parts.append(("showdesktop", 22))
	width = sum(size for _, size in parts) + 8
	x = panel.width - 3 - width
	panel.rect(x, 12, width, 20, WELL, 3)
	panel.rect(x, 31, width, 1, E.INDIGO[600])
	x += 4
	for part, size in parts:
		if part == "chevron":
			panel.path("M%s 18 l-3.5 4 l3.5 4 h2 l-3.5 -4 l3.5 -4 Z M%s 18 l-3.5 4 l3.5 4 h2 l-3.5 -4 l3.5 -4 Z" % (_n(x + 4.5), _n(x + 9)), PALE)
		elif part == "clock":
			panel.text("10:55:48" if clock == "seconds" else "10:55", x + 2, 26.5, 11, PALE)
		else:
			panel.icon(part, x + 2, 14, 16)
		x += size


def autohide_preview(panel):
	"""Auto-hide: only the desktop, and the hidden taskbar's two-pixel edge along the bottom."""
	panel.rect(0, 0, panel.width, panel.height, panel.gradient([(0, SKY1), (1, SKY7)]))
	panel.path("M150 35 a18 18 0 0 1 36 0 Z", GOLD, ' opacity="0.9"')
	panel.rect(0, panel.height - 2, panel.width, 2, BAR_LINE)


def start_preview(panel, modern):
	"""The Start menu over the Dusk desktop: two desktop icons, the taskbar, and the menu open above the Start button."""
	panel.rect(0, 0, 300, 180, panel.gradient([(0, SKY1), (0.6, SKY4), (1, SKY7)]))
	panel.path("M200 166 a34 34 0 0 1 68 0 Z", GOLD, ' opacity="0.85"')
	panel.icon("mycomputer", 6, 6, 16)
	panel.rect(3, 24, 22, 2, TEXT)
	panel.icon("mydocs", 6, 32, 16)
	panel.rect(3, 50, 22, 2, TEXT)
	taskbar(panel, 166)
	panel.rect(2, 168, 34, 11, GOLD, 2.5)
	panel.text("Start", 13, 176.5, 7, TEXT_DARK)
	panel.path("M5 176 a3 3 0 0 1 6 0 Z", E.ORANGE[500])
	if modern:
		panel.rect(4, 26, 150, 140, E.PAPER[900], 3)
		panel.rect(4, 26, 150, 14, panel.gradient([(0, SKY4), (1, SKY7)], 0, 0, 1, 0), 3)
		panel.icon("user", 7, 28, 10)
		panel.rect(20, 31, 40, 3, TEXT)
		panel.rect(80, 40, 74, 112, E.INDIGO[200])
		for row, icon_id in enumerate(("browser", "cmd", "paint", "wordpad", "calc")):
			panel.icon(icon_id, 8, 45 + row * 14, 10)
			panel.rect(21, 48 + row * 14, 46, 3, E.INDIGO[500], 1.5)
		for row, icon_id in enumerate(("mydocs", "mypictures", "mymusic", "mycomputer", "controlpanel", "printers", "help", "search", "run")):
			panel.icon(icon_id, 84, 44 + row * 12, 9)
			panel.rect(96, 47 + row * 12, 44, 3, E.INDIGO[600], 1.5)
		panel.rect(4, 152, 150, 14, E.INDIGO[700], 3)
		panel.icon("logoff", 96, 154, 9)
		panel.icon("shutdown", 124, 154, 9)
	else:
		panel.rect(4, 50, 108, 116, E.PAPER[800], 2)
		panel.rect(4, 50, 14, 116, panel.gradient([(0, DESKTOP), (0.6, SKY1), (1, SKY7)]))
		panel.path("M6 166 a5 5 0 0 1 10 0 Z", GOLD)
		for row, icon_id in enumerate(("programs", "documents", "settings", "search", "help", "run", "logoff", "shutdown")):
			y = 54 + row * 14
			panel.icon(icon_id, 22, y, 11)
			panel.rect(37, y + 4, 50, 3, E.INDIGO[500], 1.5)
			if row < 4:
				panel.path("M106 %s l3 3 l-3 3 Z" % _n(y + 2.5), E.INDIGO[500])


# ---- the wizards (watermarks 164 wide, headers 49 x 49) and the credential banner --------------------------------------------------------------
def watermark(panel, icon_id):
	"""A wizard's left panel: the Dusk sky warming to its horizon, the sun setting on it, and the wizard's icon in a light frame near the top,
	where the stock panels carry theirs."""
	height = panel.height
	panel.rect(0, 0, panel.width, height, panel.gradient([(0, DESKTOP), (0.55, SKY1), (0.8, SKY4), (1, SKY7)]))
	horizon = height - 46
	panel.path("M42 %s a40 40 0 0 1 80 0 Z" % _n(horizon), GOLD)
	panel.path("M58 %s a24 18 0 0 1 48 0 Z" % _n(horizon - 18), GOLDL, ' opacity="0.7"')
	panel.rect(0, horizon, panel.width, height - horizon, panel.gradient([(0, HORIZON), (1, SKY1)]))
	for index in range(4):
		panel.rect(18 + index * 10, horizon + 8 + index * 8, 128 - index * 20, 2, GOLD, 1, ' opacity="%s"' % _n(0.6 - index * 0.12))
	panel.rect(87, 18, 60, 60, E.PAPER[900], 6)
	panel.icon(icon_id, 93, 24, 48)


def header(panel, icon_id):
	panel.rect(0, 0, 49, 49, "#ffffff")
	panel.icon(icon_id, 0.5, 0.5, 48)


def banner(panel, icon_id):
	panel.rect(0, 0, panel.width, panel.height, panel.gradient([(0, DESKTOP), (0.6, SKY1), (1, SKY4)], 0, 0, 1, 0))
	panel.path("M200 60 a44 44 0 0 1 88 0 Z", GOLD, ' opacity="0.9"')
	panel.rect(0, 58, panel.width, 2, GOLDL)
	panel.icon(icon_id, 12, 8, 44)


# ---- Display Properties' monitor (desk.cpl 1001) and Task Manager's tray meter (taskmgr.exe 153) ----------------------------------------------
def monitor_panel(panel):
	"""The monitor every Display Properties page draws its preview in: the screen must be exactly MONITOR_LEFT 20, TOP 8, RIGHT 140,
	BOTTOM 92 (desk.h), which the applet paints over; the bezel, the stand and the foot are the icon set's monitor, and the rest is the
	magenta the applet keys out."""
	panel.rect(0, 0, 160, 120, "#ff00ff")
	panel.rect(64, 98, 32, 12, E.VOIDN[300])
	panel.rect(64, 98, 32, 2, E.VOIDN[400])
	panel.rect(40, 108, 80, 9, E.VOIDN[300], 4)
	panel.rect(40, 108, 80, 2, E.VOIDN[100], 1)
	panel.rect(12, 0, 136, 100, E.INDIGO[200], 7)
	panel.rect(12, 0, 136, 2, E.PAPER[900], 1)
	panel.rect(13, 1, 134, 98, "none", 6, ' stroke="%s" stroke-width="2"' % E.retune(E.INDIGO[700]))
	panel.rect(19, 7, 122, 86, E.INDIGO[700])
	panel.rect(20, 8, 120, 84, E.DARK)
	panel.rect(134, 94, 6, 3, GOLD, 1.5)


def meter_panel(panel):
	"""The tray meter's ground: Task Manager draws the CPU bars over it; the stock grid in Afterglow's dusk and gold."""
	panel.rect(0, 0, 16, 16, E.DARK)
	for y in range(2, 16, 3):
		panel.rect(1, y, 14, 1, E.INDIGO[600])
	for x in range(2, 16, 4):
		panel.rect(x, 1, 1, 14, E.INDIGO[600])


# name: (width, height, form, key, ground, title, draw)
PANELS = {}


def add(name, width, height, title, draw, form="key", key=None, ground=(255, 255, 255)):
	PANELS[name] = (width, height, form, key, ground, title, draw)


add("tb-autohide", 336, 35, "Taskbar preview, auto-hide", autohide_preview)
for _lock in (True, False):
	for _group in (True, False):
		for _ql in (True, False):
			_name = "tb-%s-%s-%s" % ("lock" if _lock else "nolock", "group" if _group else "nogroup", "ql" if _ql else "noql")
			add(_name, 336, 35, "Taskbar preview, %s, %s, %s" % ("locked" if _lock else "unlocked", "grouped" if _group else "not grouped",
				"Quick Launch" if _ql else "no Quick Launch"), (lambda lock, group, ql: lambda panel: taskbar_preview(panel, lock, group, ql))(_lock, _group, _ql))
for _show in (True, False):
	for _clock in ("seconds", "clock", None):
		for _desk in (False, True):
			_name = "tray-%s-%s-%s" % ("show" if _show else "hide", _clock or "noclock", "desk" if _desk else "nodesk")
			add(_name, 336, 35, "Notification area preview, icons %s, %s, %s" % ("shown" if _show else "hidden", _clock or "no clock",
				"Show Desktop" if _desk else "no Show Desktop"), (lambda show, clock, desk: lambda panel: tray_preview(panel, show, clock, desk))(_show, _clock, _desk))
add("start-preview", 300, 180, "Start menu preview", lambda panel: start_preview(panel, True))
add("start-preview-classic", 300, 180, "Classic Start menu preview", lambda panel: start_preview(panel, False))
for _name, _height, _icon in (("wiz-shortcut", 400, "program"), ("wiz-addhw", 400, "addhw"), ("wiz-newdev", 400, "devcard"),
		("wiz-cert", 628, "certificate"), ("wiz-zip", 628, "archive")):
	add(_name, 164, _height, "Wizard watermark", (lambda icon_id: lambda panel: watermark(panel, icon_id))(_icon))
for _name, _icon in (("wizhead-addhw", "addhw"), ("wizhead-newdev", "devcard"), ("wizhead-cert", "certificate"), ("wizhead-zip", "archive")):
	add(_name, 49, 49, "Wizard header", (lambda icon_id: lambda panel: header(panel, icon_id))(_icon))
add("credui-banner", 320, 60, "Credential prompt banner", lambda panel: banner(panel, "key"))
add("desk-monitor", 160, 120, "Display Properties monitor", monitor_panel, key=MAGENTA, ground=(212, 208, 200))
add("taskmgr-meter", 16, 16, "Task Manager tray meter", meter_panel)


def font_path(folder):
	for candidate in ([folder] if folder else []) + ["/usr/share/fonts/TTF", "/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/dejavu"]:
		if candidate and os.path.exists(os.path.join(candidate, "DejaVuSans.ttf")):
			return os.path.join(candidate, "DejaVuSans.ttf")
	sys.exit("gen_panels.py: DejaVuSans.ttf not found; pass its folder as FONT_DIR")


def main():
	global FONT
	if len(sys.argv) not in (2, 3):
		sys.exit("usage: gen_panels.py OUT_DIR [FONT_DIR]")
	FONT = OUTLINE.Font(font_path(sys.argv[2] if len(sys.argv) == 3 else None))
	os.makedirs(sys.argv[1], exist_ok=True)
	for name, (width, height, form, key, ground, title, draw) in PANELS.items():
		panel = Panel(name, width, height)
		draw(panel)
		bits = "a 24-bit bitmap" + (" with magenta keyed out" if key else "")
		with open(os.path.join(sys.argv[1], name + ".svg"), "w") as f:
			f.write(panel.svg(title, "%s, %d x %d" % (bits, width, height)))
	index = {name: {"size": [width, height], "key": list(key) if key else None, "ground": list(ground)} for name, (width, height, _form, key, ground, _title,
		_draw) in PANELS.items()}
	with open(os.path.join(sys.argv[1], "panels.json"), "w") as f:
		f.write(json.dumps(index, indent="\t", sort_keys=True) + "\n")
	print("panels", len(PANELS))


if __name__ == "__main__":
	main()
