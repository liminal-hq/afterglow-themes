# Afterglow original: palette, a small pixel canvas and a BMP writer. Every bitmap in the style is drawn from these primitives.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
import numpy as np


def rgb(h):
	h = h.lstrip("#")
	return np.array([int(h[i : i + 2], 16) for i in (0, 2, 4)], dtype=float)


def hexstr(c):
	c = np.clip(np.round(np.asarray(c, dtype=float)), 0, 255).astype(int)
	return "#%02x%02x%02x" % tuple(c)


def ini_colour(c):
	c = np.clip(np.round(np.asarray(c, dtype=float)), 0, 255).astype(int)
	return "%d %d %d" % tuple(c)


def mix(a, b, t):
	"""Linear mix of two colours: t = 0 gives a, t = 1 gives b."""
	return np.asarray(a, dtype=float) * (1 - t) + np.asarray(b, dtype=float) * t


# ---- palette --------------------------------------------------------------------------------------------------------------------------
# Liminal HQ Afterglow tokens (surfaces, text, brand) and the Quill dusk wallpaper's glow steps.
P = {
	"night": rgb("#050507"),
	"panel": rgb("#0c0c10"),
	"panel2": rgb("#111116"),
	"raised": rgb("#14161d"),
	"raised2": rgb("#1b1e28"),
	"raised3": rgb("#262a37"),
	"tile": rgb("#0a1230"),  # icon tile navy, used for outlines
	"horizon": rgb("#4a4580"),  # front horizon edge in the wallpaper
	"text": rgb("#e0e0e0"),
	"text2": rgb("#b4bfce"),
	"muted": rgb("#7c8796"),
	"white": rgb("#ffffff"),
	"gold": rgb("#ffaa40"),
	"gold_down": rgb("#e89930"),
	"gold_light": rgb("#ffd08e"),
	"gold_pale": rgb("#ffe7c4"),
	"gold_deep": rgb("#b8893a"),
	"ink": rgb("#f0a830"),
	"rose": rgb("#f43f5e"),
	"rose_mid": rgb("#c9354e"),
	"rose_light": rgb("#f995a6"),
	"rose_deep": rgb("#8f2638"),
	# Classic client colours (ReactOS classic scheme): controls on dialogs sit on these.
	"cream": rgb("#d4d0c8"),
	"cream_hi": rgb("#ece9e2"),
	"cream_lo": rgb("#c2bdb2"),
	"shadow": rgb("#808080"),
	"edge": rgb("#7f849c"),  # control outline: a grey with a little dusk in it
	"edge_dim": rgb("#a7a59f"),
	"ink_text": rgb("#0a0c1a"),
}
# Active caption: the wallpaper's seven inner glow steps, navy on the left to rose on the right.
DUSK = [rgb(h) for h in ("#1f2554", "#2a3164", "#35366a", "#42396c", "#523d6c", "#643f68", "#7a4562")]
KEY = np.array([255.0, 0.0, 255.0])  # transparent key colour

# ---- colour schemes -------------------------------------------------------------------------------------------------------------------
# Each colour scheme is data: the seven-step caption ramp (which also drives the frames, scroll thumbs, task buttons, check boxes and the
# taskbar hairline) and the palette entries it replaces. Hex values are the design canvas's palette tables ("Quill ReactOS Afterglow
# Theme Boards": the Caption, Taskbar and Desk parts and the colour boards); Dusk is today's look and stays the default (first).
# Keys: ramp; accent (gold: Start button, ink lines, default ring, tick, pressed rims) with accent_down, accent_light, accent_pale,
# accent_deep and ink; the near-black surfaces night, panel (taskbar), panel2 (tray), raised (inactive caption, scroll track), raised2,
# raised3; horizon (button rims); close (the close button) with close_mid, close_deep, close_light; muted (inactive title), text2
# (scroll glyphs); start_text (the Start label). Entries marked "derived" in SCHEME_NOTES are not on the canvas.
SCHEMES = {
	"Dusk": {
		"ramp": ("#1f2554", "#2a3164", "#35366a", "#42396c", "#523d6c", "#643f68", "#7a4562"),
		"accent": "#ffaa40", "accent_down": "#e89930", "accent_light": "#ffd08e", "accent_pale": "#ffe7c4", "accent_deep": "#b8893a",
		"ink": "#f0a830",
		"night": "#050507", "panel": "#0c0c10", "panel2": "#111116", "raised": "#14161d", "raised2": "#1b1e28", "raised3": "#262a37",
		"horizon": "#4a4580",
		"close": "#f43f5e", "close_mid": "#c9354e", "close_deep": "#8f2638", "close_light": "#f995a6",
		"muted": "#7c8796", "text2": "#b4bfce", "start_text": "#050507",
		"tile": "#0a1230", "desktop": "#090e2a",
	},
	"Ember": {
		"ramp": ("#2b1330", "#4a1838", "#6b213a", "#8c3034", "#a3402c", "#a8472f", "#ab4b3a"),
		"accent": "#f3d58a", "accent_down": "#dcb96a", "accent_light": "#fae7b8", "accent_pale": "#fdf3dc", "accent_deep": "#9c7a36",
		"ink": "#f3d58a",
		"night": "#070404", "panel": "#110c0b", "panel2": "#161010", "raised": "#1c1513", "raised2": "#241b18", "raised3": "#352823",
		"horizon": "#7a3a46",
		"close": "#c41e3a", "close_mid": "#a3182f", "close_deep": "#6e0f20", "close_light": "#ec7d8f",
		"muted": "#968782", "text2": "#cfbfb6", "start_text": "#1a0c08",
	},
	"Aurora": {
		"ramp": ("#0e2238", "#0f3a4c", "#0f5559", "#136466", "#26587a", "#3a4a84", "#4b3d86"),
		"accent": "#7be3c8", "accent_down": "#5ccdb0", "accent_light": "#b4f1e1", "accent_pale": "#dcf9f1", "accent_deep": "#2f8f78",
		"ink": "#7be3c8",
		"night": "#03060c", "panel": "#070b14", "panel2": "#0b111c", "raised": "#0f1520", "raised2": "#151d2b", "raised3": "#202b3d",
		"horizon": "#2f6d82",
		"close": "#d0508f", "close_mid": "#ad3f76", "close_deep": "#74264f", "close_light": "#f0a0c6",
		"muted": "#7b8a9c", "text2": "#b0c4d0", "start_text": "#04201a",
	},
	"Graphite": {
		"ramp": ("#1e2126", "#292c32", "#34373d", "#3f4247", "#48494c", "#504f4e", "#585451"),
		"accent": "#ffaa40", "accent_down": "#e89930", "accent_light": "#ffd08e", "accent_pale": "#ffe7c4", "accent_deep": "#b8893a",
		"ink": "#f0a830",
		"night": "#050506", "panel": "#0d0d0e", "panel2": "#121213", "raised": "#161719", "raised2": "#1d1f22", "raised3": "#2a2d31",
		"horizon": "#5a5d63",
		"close": "#b5473f", "close_mid": "#963a33", "close_deep": "#652621", "close_light": "#e0948d",
		"muted": "#858a91", "text2": "#bfc2c7", "start_text": "#050507",
	},
	# Light schemes: not on the design canvas; written here on the same slots. Each has a pale caption ramp in the hue family of
	# its dark scheme, dark title text (gen.py checks 4.5:1 or better on every ramp step), light surfaces for the taskbar, tray,
	# scroll track and inactive caption, a deeper ink line, dark caption and scroll glyphs, and its dark scheme's ramp for the
	# dialog controls (ctl), so they keep their dark outlines and fills on the cream client.
	"Dusk Light": {
		"ramp": ("#f6dcc8", "#f3d7cc", "#eed2d1", "#e8cfd7", "#e1ccdc", "#d9c9e0", "#d0c6e2"),
		"accent": "#ffaa40", "accent_down": "#e89930", "accent_light": "#ffd08e", "accent_pale": "#ffe7c4", "accent_deep": "#b8893a",
		"ink": "#e08a1e",
		"night": "#6b6380", "panel": "#e4dcec", "panel2": "#efeaf3", "raised": "#e6e1ea", "raised2": "#f6f1ea", "raised3": "#ddd5e3",
		"horizon": "#9a8fb8",
		"close": "#e0607a", "close_mid": "#c94d68", "close_deep": "#9a3048", "close_light": "#f7a8b8",
		"muted": "#5e5870", "text2": "#4a4f66", "start_text": "#050507",
		"title_text": "#1f2554", "title_shadow": "#fbf6f2", "text": "#1f2433",
		"glyph": "#2a2f4a", "glyph_pressed": "#8a5a10", "grip_pressed": "#8a5a10",
		"ctl": "Dusk",
	},
	"Ember Light": {
		"ramp": ("#f7e3d3", "#f5dacb", "#f2d0c2", "#efc6b8", "#ecbdae", "#e8b4a4", "#e4ab9c"),
		"accent": "#e8b85a", "accent_down": "#d4a040", "accent_light": "#f3d58a", "accent_pale": "#fae7b8", "accent_deep": "#9c7a36",
		"ink": "#c98a2a",
		"night": "#7a6058", "panel": "#ecdcd4", "panel2": "#f4ebe6", "raised": "#ede4df", "raised2": "#f8f1ec", "raised3": "#e2d4cc",
		"horizon": "#b88a8e",
		"close": "#c41e3a", "close_mid": "#a3182f", "close_deep": "#6e0f20", "close_light": "#ec7d8f",
		"muted": "#6a5852", "text2": "#5a4640", "start_text": "#1a0c08",
		"title_text": "#2b1330", "title_shadow": "#fdf5ee", "text": "#2b1c18",
		"glyph": "#3a2028", "glyph_pressed": "#7a5a20", "grip_pressed": "#7a5a20",
		"ctl": "Ember",
	},
	"Aurora Light": {
		"ramp": ("#dff3ef", "#d6eef0", "#cfe8ef", "#cde0ee", "#d0d8ee", "#d4d1ec", "#d8cbea"),
		"accent": "#3cc6a4", "accent_down": "#2fae8e", "accent_light": "#7be3c8", "accent_pale": "#b4f1e1", "accent_deep": "#2f8f78",
		"ink": "#2fae8e",
		"night": "#5d6d82", "panel": "#dde5ee", "panel2": "#edf1f6", "raised": "#e4e9ef", "raised2": "#f3f6f9", "raised3": "#d6dee8",
		"horizon": "#7fa6b8",
		"close": "#d0508f", "close_mid": "#ad3f76", "close_deep": "#74264f", "close_light": "#f0a0c6",
		"muted": "#52617a", "text2": "#3e4e62", "start_text": "#04201a",
		"title_text": "#0e2238", "title_shadow": "#f4fbfa", "text": "#142033",
		"glyph": "#1d2a3e", "glyph_pressed": "#1f6e5c", "grip_pressed": "#1f6e5c",
		"ctl": "Aurora",
	},
	"Graphite Light": {
		"ramp": ("#f2f2f3", "#ebebed", "#e4e4e6", "#dededf", "#d8d7d7", "#d2d0ce", "#ccc8c4"),
		"accent": "#ffaa40", "accent_down": "#e89930", "accent_light": "#ffd08e", "accent_pale": "#ffe7c4", "accent_deep": "#b8893a",
		"ink": "#e08a1e",
		"night": "#6a6c70", "panel": "#e2e2e4", "panel2": "#eeeeef", "raised": "#e8e8ea", "raised2": "#f6f6f7", "raised3": "#dadadd",
		"horizon": "#9a9da3",
		"close": "#b5473f", "close_mid": "#963a33", "close_deep": "#652621", "close_light": "#e0948d",
		"muted": "#5c5f66", "text2": "#45484e", "start_text": "#050507",
		"title_text": "#1e2126", "title_shadow": "#fafafa", "text": "#1e2126",
		"glyph": "#2a2d31", "glyph_pressed": "#8a5a10", "grip_pressed": "#8a5a10",
		"ctl": "Graphite",
	},
}
SCHEME_NOTES = (
	"Dark schemes: every value is the design canvas's, except tile (pressed check box outline) and desktop (the Background system "
	"colour), derived for Ember, Aurora and Graphite. Light schemes: written here on the same slots; not on the canvas."
)
# Optional keys and their defaults (the dark schemes use the defaults): title_text (caption text: white), title_shadow (night),
# text (taskbar and clock text: #e0e0e0), glyph (caption and scroll glyphs: white), glyph_pressed (accent_light), grip_pressed
# (accent_pale), ctl (the scheme whose ramp the dialog controls use: the scheme itself).
# Palette entry each scheme key replaces.
_SLOT = {
	"accent": "gold", "accent_down": "gold_down", "accent_light": "gold_light", "accent_pale": "gold_pale", "accent_deep": "gold_deep",
	"ink": "ink", "night": "night", "panel": "panel", "panel2": "panel2", "raised": "raised", "raised2": "raised2", "raised3": "raised3",
	"horizon": "horizon", "close": "rose", "close_mid": "rose_mid", "close_deep": "rose_deep", "close_light": "rose_light",
	"muted": "muted", "text2": "text2", "start_text": "start_text", "tile": "tile", "desktop": "desktop",
	"title_text": "title_text", "title_shadow": "title_shadow", "text": "text", "glyph": "glyph", "glyph_pressed": "glyph_pressed",
	"grip_pressed": "grip_pressed",
}
P["start_text"] = rgb("#050507")
P["desktop"] = rgb("#090e2a")
P["title_text"] = rgb("#ffffff")
P["title_shadow"] = P["night"]
P["glyph"] = rgb("#ffffff")
P["glyph_pressed"] = P["gold_light"]
P["grip_pressed"] = P["gold_pale"]
# The ramp the dialog controls use (check boxes, radios, drop-down and spin buttons, tabs, trackbar thumbs, push button outlines).
CTL = list(DUSK)


def use_scheme(name):
	"""Make the named colour scheme current: P, DUSK and CTL are updated in place, so every drawing function picks it up."""
	s = dict(SCHEMES[name])
	ramp = [rgb(h) for h in s.pop("ramp")]
	ctl_name = s.pop("ctl", name)
	ctl = [rgb(h) for h in SCHEMES[ctl_name]["ramp"]]
	s.setdefault("title_text", "#ffffff")
	s.setdefault("title_shadow", s["night"])
	s.setdefault("text", "#e0e0e0")
	s.setdefault("glyph", "#ffffff")
	s.setdefault("glyph_pressed", s["accent_light"])
	s.setdefault("grip_pressed", s["accent_pale"])
	# Derived where no value is given: the tile navy is the control ramp's first step pressed most of the way to that scheme's night,
	# as Dusk's #0a1230 is; the desktop colour (seen only without a wallpaper) is the first ramp step halfway to night.
	s.setdefault("tile", SCHEMES[ctl_name].get("tile") or hexstr(mix(ctl[0], rgb(SCHEMES[ctl_name]["night"]), 0.6)))
	s.setdefault("desktop", hexstr(mix(ramp[0], rgb(s["night"]), 0.5)))
	for k, v in s.items():
		P[_SLOT[k]] = rgb(v)
	DUSK[:] = ramp
	CTL[:] = ctl


def dusk_at(t):
	"""Smooth colour along the seven dusk stops, t in 0..1."""
	t = min(max(t, 0.0), 1.0) * (len(DUSK) - 1)
	i = min(int(t), len(DUSK) - 2)
	return mix(DUSK[i], DUSK[i + 1], t - i)



# ---- canvas ---------------------------------------------------------------------------------------------------------------------------


def canvas(w, h, c=KEY):
	a = np.zeros((h, w, 3), dtype=float)
	a[:, :] = c
	return a


def round_mask(w, h, r, corners="tl tr bl br"):
	"""Boolean mask of a w x h rectangle with pixel-art rounded corners of radius r (sampled at pixel centres)."""
	m = np.ones((h, w), dtype=bool)
	if r <= 0:
		return m
	cs = corners.split()
	for y in range(h):
		for x in range(w):
			for name, cx, cy in (("tl", r, r), ("tr", w - r, r), ("bl", r, h - r), ("br", w - r, h - r)):
				if name not in cs:
					continue
				px, py = x + 0.5, y + 0.5
				inx = px < cx if name in ("tl", "bl") else px > cx
				iny = py < cy if name in ("tl", "tr") else py > cy
				if inx and iny and (px - cx) ** 2 + (py - cy) ** 2 > r * r + 0.3:
					m[y, x] = False
	return m


def inner_edge(m):
	"""Pixels of mask m that touch the outside (4-neighbourhood): the 1 px outline of a shape."""
	p = np.pad(m, 1, constant_values=False)
	inside = p[1:-1, 1:-1] & p[:-2, 1:-1] & p[2:, 1:-1] & p[1:-1, :-2] & p[1:-1, 2:]
	return m & ~inside


def shape(w, h, r, fill, border=None, corners="tl tr bl br", bg=KEY, rows=None, cols=None):
	"""A rounded rectangle: fill may be a colour, or rows/cols give per-row or per-column fills. Outside the shape is bg."""
	a = canvas(w, h, bg)
	m = round_mask(w, h, r, corners)
	body = np.zeros((h, w, 3))
	if fill is not None:
		body[:, :] = fill
	if rows is not None:
		for y, c in enumerate(rows):
			body[y, :] = c
	if cols is not None:
		for x, c in enumerate(cols):
			body[:, x] = c
	a[m] = body[m]
	if border is not None:
		e = inner_edge(m)
		a[e] = border
	return a, m


def stack(frames, vertical=True):
	return np.concatenate(frames, axis=0 if vertical else 1)


def gloss_rows(h, top, bottom, split=0.5):
	"""Two-band 'glass' fill: the top part a flat lighter colour, then a short ramp to the base. Few colours, no banding."""
	rows = []
	k = max(1, int(round(h * split)))
	for y in range(h):
		if y < k:
			rows.append(top)
		else:
			t = (y - k) / max(1, h - k - 1)
			rows.append(mix(mix(top, bottom, 0.55), bottom, t))
	return rows


# ---- BMP output -----------------------------------------------------------------------------------------------------------------------


def _bmp(w, h, bpp, pal, rows_bytes):
	stride = (len(rows_bytes[0]) + 3) & ~3
	data = b"".join(r + bytes(stride - len(r)) for r in reversed(rows_bytes))  # bottom-up
	palbytes = b"".join(bytes((int(c[2]), int(c[1]), int(c[0]), 0)) for c in pal)
	off = 14 + 40 + len(palbytes)
	hdr = b"BM" + (off + len(data)).to_bytes(4, "little") + bytes(4) + off.to_bytes(4, "little")
	info = (40).to_bytes(4, "little") + w.to_bytes(4, "little", signed=True) + h.to_bytes(4, "little", signed=True)
	info += (1).to_bytes(2, "little") + bpp.to_bytes(2, "little") + bytes(4) + len(data).to_bytes(4, "little")
	info += (2835).to_bytes(4, "little") * 2 + len(pal).to_bytes(4, "little") + bytes(4)
	return hdr + info + palbytes + data


def encode_bmp(a):
	"""Smallest uncompressed BMP that holds the image exactly: 4-bit or 8-bit palette, or 24-bit."""
	a = np.clip(np.round(a), 0, 255).astype(np.uint8)
	h, w = a.shape[:2]
	cols, inv = np.unique(a.reshape(-1, 3), axis=0, return_inverse=True)
	idx = inv.reshape(h, w)
	if len(cols) <= 16:
		rows = []
		for y in range(h):
			r = list(idx[y]) + ([0] if w & 1 else [])
			rows.append(bytes((r[i] << 4) | r[i + 1] for i in range(0, len(r), 2)))
		return _bmp(w, h, 4, cols, rows)
	if len(cols) <= 256:
		return _bmp(w, h, 8, cols, [bytes(idx[y].astype(np.uint8)) for y in range(h)])
	rows = [bytes(a[y, :, ::-1].reshape(-1)) for y in range(h)]
	return _bmp(w, h, 24, [], rows)
