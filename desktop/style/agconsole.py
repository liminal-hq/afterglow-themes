# Afterglow console colours: the 16-colour table, the default screen and popup colours, and the registry text that sets them, all drawn
# from the scheme palette in agdraw.py. Only the hues the palette has no slot for (green, cyan, blue, magenta, and a red or yellow where the
# slot is too dark) are written here, in CONSOLE_HUES.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
import numpy as np

from agdraw import P, hexstr, mix, rgb

# ReactOS's console (consrv) numbers the table in the Windows order: 0 black, 1 blue, 2 green, 3 aqua, 4 red, 5 purple, 6 yellow, 7 white
# (light grey), then the same eight bright. A hue is (normal, bright). Dark schemes: a lit terminal on the scheme's navy-tinted night, so
# every colour is lit to 4.5:1 or better on it. Light schemes: ink on the scheme's paper, ScreenColors 0xF0 (index 15 is the paper and
# index 0 the ink), every hue dark enough for 4.5:1 on the paper. "red" and "yellow" fall back to the scheme's close and accent slots.
CONSOLE_HUES = {
	"Dusk": {"blue": ("#7f95f2", "#a9b8ff"), "green": ("#86cf9a", "#b0efc0"), "cyan": ("#62c6d6", "#98e6f0"), "magenta": ("#c98be6", "#e4b8f8")},
	"Ember": {
		"red": ("#ee5f5b", "#ff9a94"), "blue": ("#7d93e0", "#a8b8f4"), "green": ("#a6c96a", "#c8e592"),
		"cyan": ("#5cc1b8", "#92e0d8"), "magenta": ("#d278b5", "#ec9fd2"),
	},
	"Aurora": {
		"red": ("#ef6a8a", "#ff9fb6"), "yellow": ("#e8d27a", "#f6e8a6"), "blue": ("#7a98f0", "#a8bcff"), "green": ("#6fdc9a", "#a0f0bc"),
		"cyan": ("#5bc4e6", "#92e0f6"), "magenta": ("#cf7fd0", "#e8a8e8"),
	},
	"Graphite": {
		"red": ("#e8605a", "#ff9a94"), "blue": ("#7f98d8", "#a8bcf0"), "green": ("#8ec97a", "#b4e6a2"),
		"cyan": ("#5fc3c9", "#94e2e6"), "magenta": ("#c58ac4", "#e2b0e0"),
	},
	"Dusk Light": {
		"red": ("#a8203c", "#c42a4a"), "yellow": ("#8a5a10", "#946412"), "blue": ("#2c46b0", "#3a58c8"), "green": ("#1f6e3c", "#257a49"),
		"cyan": ("#14687c", "#1a7489"), "magenta": ("#8a3a9e", "#a048b8"),
	},
	"Ember Light": {
		"red": ("#a8182f", "#c42238"), "yellow": ("#7a5010", "#8e6014"), "blue": ("#34489e", "#445cb8"), "green": ("#456a1c", "#507420"),
		"cyan": ("#126a68", "#187670"), "magenta": ("#92307a", "#aa4094"),
	},
	"Aurora Light": {
		"red": ("#a8306c", "#c03c80"), "yellow": ("#745a0c", "#886a10"), "blue": ("#2c4aa8", "#3c5cc0"), "green": ("#176a4c", "#1d7a5a"),
		"cyan": ("#0e6580", "#14748f"), "magenta": ("#843a9c", "#9c48b6"),
	},
	"Graphite Light": {
		"red": ("#a8322c", "#c03c36"), "yellow": ("#7a5410", "#8e6414"), "blue": ("#34489c", "#4458b4"), "green": ("#2e6a24", "#3a7e30"),
		"cyan": ("#186a74", "#1c7882"), "magenta": ("#82388a", "#9848a2"),
	},
}
ORDER = ("black", "blue", "green", "cyan", "red", "magenta", "yellow", "white")
MIN_CONTRAST = 4.5


def luminance(colour):
	colour = np.asarray(colour, dtype=float) / 255
	colour = np.where(colour <= 0.03928, colour / 12.92, ((colour + 0.055) / 1.055) ** 2.4)
	return 0.2126 * colour[0] + 0.7152 * colour[1] + 0.0722 * colour[2]


def contrast(first, second):
	lighter, darker = sorted((luminance(first), luminance(second)), reverse=True)
	return (lighter + 0.05) / (darker + 0.05)


def is_light(name):
	return name.endswith("Light")


def console_colours(name):
	"""The scheme's 16 console colours as RGB arrays (index 0..15) and its ScreenColors and PopupColors bytes. The scheme must be the
	current one (agdraw.use_scheme)."""
	hues = CONSOLE_HUES[name]
	light = is_light(name)
	if light:
		paper = P["raised2"]
		ink = P["text"]
		normal = {"black": ink, "white": P["text2"]}
		bright = {"black": P["muted"], "white": paper}
		yellow_default = ("glyph_pressed", None)
	else:
		night = P["tile"]
		normal = {"black": night, "white": mix(P["text"], P["gold_pale"], 0.3)}
		bright = {"black": P["muted"], "white": mix(P["white"], P["gold_pale"], 0.35)}
		yellow_default = ("gold", "gold_light")
	for hue in ("blue", "green", "cyan", "red", "magenta", "yellow"):
		if hue in hues:
			normal[hue], bright[hue] = (rgb(h) for h in hues[hue])
		elif hue == "red":
			normal[hue], bright[hue] = P["rose"], P["rose_light"]
		elif hue == "yellow":
			normal[hue], bright[hue] = P[yellow_default[0]], P[yellow_default[1]]
	table = [normal[hue] for hue in ORDER] + [bright[hue] for hue in ORDER]
	# Dark: the off-white on the night (attribute 0x07). Light: ink on the paper (0xF0). Popups (the history and command lists): the
	# night on the pale gold (0xE0) for dark, and the paper on the ink (0x0F, inverse video) for light.
	screen = 0xF0 if light else 0x07
	popup = 0x0F if light else 0xE0
	return table, screen, popup


def console_checks(name, table, screen, popup):
	"""Every colour that is text on the screen background must reach 4.5:1 on it; returns {index: ratio} and fails otherwise."""
	background = table[screen >> 4]
	ratios = {i: contrast(c, background) for i, c in enumerate(table) if i != screen >> 4}
	popup_ratio = contrast(table[popup & 15], table[popup >> 4])
	if popup_ratio < MIN_CONTRAST:
		raise SystemExit(f"{name}: popup colours reach only {popup_ratio:.2f}:1")
	worst = min(ratios.values())
	if worst < MIN_CONTRAST:
		low = {i: round(r, 2) for i, r in ratios.items() if r < MIN_CONTRAST}
		raise SystemExit(f"{name}: console colours below {MIN_CONTRAST}:1 on the screen background: {low}")
	return ratios


def dword(value):
	return f"dword:{value:08x}"


def bgr(colour):
	r, g, b = (int(round(v)) for v in colour)
	return (b << 16) | (g << 8) | r


def console_reg_lines(name):
	"""The [HKCU\\Console] section for a scheme, as lines (without a trailing blank)."""
	table, screen, popup = console_colours(name)
	console_checks(name, table, screen, popup)
	lines = ["[HKEY_CURRENT_USER\\Console]"]
	lines += [f'"ColorTable{i:02d}"={dword(bgr(c))}' for i, c in enumerate(table)]
	lines += [f'"ScreenColors"={dword(screen)}', f'"PopupColors"={dword(popup)}']
	return lines


def console_comment(name):
	table, screen, popup = console_colours(name)
	return "; Console colours: " + " ".join(hexstr(c) for c in table)
