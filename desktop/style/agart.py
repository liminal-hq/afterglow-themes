# Afterglow original: every bitmap in the style, drawn procedurally from the Afterglow palette. Nothing here is traced or derived
# from another visual style. Each function returns a float RGB array (H x W x 3); state frames are stacked top to bottom.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
import numpy as np

from agdraw import CTL, DUSK, KEY, P, canvas, dusk_at, gloss_rows, inner_edge, mix, round_mask, shape, stack, use_scheme

# Caption geometry: the dusk ramp runs across CAP_MID source columns between two fixed margins; the frame bottom uses the same columns
# so its colours line up with the caption above it whatever the window width.
CAP_MARGIN = 8
CAP_MID = 48
CAP_W = CAP_MARGIN * 2 + CAP_MID
CAP_H = 29  # 4 px frame + SM_CYCAPTION 25 (CaptionHeight 24 in the registry), drawn 1:1
CAP_R = 6
STEPPED = False
GOLD_FRAME = 0.4  # how much gold the active frame's inner line carries (0 = none)  # True: seven flat steps (the spike's look); False: a smooth ramp through the same seven stops


def cap_column_colours(active):
	cols = []
	for x in range(CAP_W):
		if not active:
			cols.append(P["raised"])
			continue
		t = (x - CAP_MARGIN + 0.5) / CAP_MID
		t = min(max(t, 0.0), 1.0)
		if STEPPED:
			cols.append(DUSK[min(int(t * 7), 6)])
		else:
			cols.append(dusk_at(t))
	return cols


def caption(active, rounded=True):
	cols = cap_column_colours(active)
	w, h = CAP_W, CAP_H
	a = canvas(w, h)
	m = round_mask(w, h, CAP_R if rounded else 0, "tl tr")
	for x in range(w):
		c = cols[x]
		for y in range(h):
			if not m[y, x]:
				continue
			if y == h - 1:  # the ink line: gold under the title, fading out to the right
				if active:
					t = x / (w - 1)
					a[y, x] = mix(P["ink"], mix(c, P["night"], 0.35), min(1.0, t * 1.25) ** 0.85)
				else:
					a[y, x] = P["raised3"]
			elif y == h - 2:  # darker bottom edge
				a[y, x] = mix(c, P["night"], 0.38)
			elif y <= 1:
				a[y, x] = c
			elif y < h // 2:  # soft upper glow: a flat band a little lighter than the base
				a[y, x] = mix(c, P["white"], 0.05 if active else 0.02)
			else:
				a[y, x] = c
	# outline around the top and sides, and a lighter highlight just inside the top edge
	e = inner_edge(m)
	e[h - 1, :] = False
	e[h - 2, :] = e[h - 2, :] & False
	for y, x in zip(*np.nonzero(e)):
		a[y, x] = mix(cols[x], P["night"], 0.6) if active else P["night"]
	hl = inner_edge(m & ~e)
	hl[h // 2 :, :] = False
	for y, x in zip(*np.nonzero(hl)):
		if y <= CAP_R or y == 1:
			a[y, x] = mix(cols[x], P["white"], 0.26 if active else 0.08)
	if not rounded:
		a[:, 0] = a[:, 1]
		a[:, -1] = a[:, -2]
	return a


def captions():
	return stack([caption(True), caption(False)]), stack([caption(True, False), caption(False, False)])


def frame_side(right):
	frames = []
	for active in (True, False):
		c = DUSK[-1] if (active and right) else DUSK[0] if active else P["raised"]
		outline = mix(c, P["night"], 0.6) if active else P["night"]
		inner = mix(c, P["gold"], GOLD_FRAME) if active else P["panel"]
		row = [outline, c, c, inner]
		if right:
			row = row[::-1]
		f = np.zeros((2, 4, 3))
		f[:, :] = row
		frames.append(f)
	return stack(frames)


def frame_bottom():
	frames = []
	for active in (True, False):
		cols = cap_column_colours(active)
		f = np.zeros((4, CAP_W, 3))
		for x in range(CAP_W):
			c = cols[x]
			outline = mix(c, P["night"], 0.6) if active else P["night"]
			inner = mix(c, P["gold"], GOLD_FRAME) if active else P["panel"]
			f[:, x] = c
			f[3, x] = outline
			if 3 <= x <= CAP_W - 4:
				f[0, x] = inner
		f[:, 0] = [mix(cols[0], P["night"], 0.6) if active else P["night"]] * 4
		f[:, -1] = [mix(cols[-1], P["night"], 0.6) if active else P["night"]] * 4
		frames.append(f)
	return stack(frames)


# ---- caption buttons ------------------------------------------------------------------------------------------------------------------
# Engine states 1..8: normal, hot, pressed, disabled, inactive, inactive hot, inactive pressed, inactive disabled.


def _btn(fill_top, fill_bottom, border, size=16, r=3, shine=None):
	rows = gloss_rows(size, fill_top, fill_bottom, 0.45)
	a, m = shape(size, size, r, None, border, rows=rows)
	if shine is not None:  # one bright row just inside the top border
		inner = m & ~inner_edge(m)
		ys = np.nonzero(inner.any(axis=1))[0]
		a[ys[0], inner[ys[0]]] = shine
	return a


def caption_button_bg(close):
	dark = _btn(mix(P["raised3"], P["white"], 0.04), P["raised2"], P["horizon"], shine=mix(P["raised3"], P["white"], 0.14))
	hot = _btn(mix(DUSK[4], P["white"], 0.18), DUSK[3], mix(P["horizon"], P["white"], 0.35), shine=mix(DUSK[4], P["white"], 0.4))
	pressed = _btn(P["panel"], P["raised2"], P["gold"])
	disabled = _btn(P["raised2"], P["raised2"], P["raised3"])
	inactive = _btn(P["raised2"], P["raised2"], P["raised3"])
	if close:
		normal = _btn(mix(P["rose"], P["white"], 0.12), P["rose_mid"], mix(P["rose_deep"], P["night"], 0.3), shine=P["rose_light"])
		hot = _btn(mix(P["rose"], P["white"], 0.3), P["rose"], P["rose_deep"], shine=mix(P["rose_light"], P["white"], 0.5))
		pressed = _btn(P["rose_deep"], P["rose_mid"], P["gold"])
		disabled = _btn(mix(P["rose_deep"], P["raised2"], 0.6), mix(P["rose_deep"], P["raised2"], 0.6), P["raised3"])
	else:
		normal = dark
	return stack([inset(f) for f in (normal, hot, pressed, disabled, inactive, hot, pressed, disabled)])


BTN_INSET = 2  # the engine gives each caption button SM_CYSIZE - 4 = 20 px; the visible face is 16 px with a clear ring


def inset(f):
	n = f.shape[0] + 2 * BTN_INSET
	out = canvas(n, n)
	out[BTN_INSET : BTN_INSET + f.shape[0], BTN_INSET : BTN_INSET + f.shape[1]] = f
	return out


def glyph_colours():
	g, gp = P["glyph"], P["glyph_pressed"]
	return [g * 0.94, g, gp, mix(P["muted"], P["raised2"], 0.5), P["muted"], g, gp, mix(P["muted"], P["raised2"], 0.6)]


def _glyph(kind):
	g = np.zeros((9, 9), dtype=bool)
	if kind == "min":
		g[6:8, 1:8] = True
	elif kind == "max":
		g[0:2, 0:9] = True
		g[:, 0] = g[:, 8] = True
		g[8, :] = True
	elif kind == "restore":
		g[0:2, 2:9] = True
		g[0:7, 8] = True
		g[6, 6:9] = True
		g[0:3, 2] = True
		g[2:9, 0:7] = False
		g[2:4, 0:7] = True
		g[2:9, 0] = g[2:9, 6] = True
		g[8, 0:7] = True
	elif kind == "close":
		for i in range(9):
			for j in range(9):
				if abs(i - j) <= 0.6 or abs(i + j - 8) <= 0.6 or abs(i - j) == 1 and 1 <= i <= 7 and 1 <= j <= 7 or abs(i + j - 8) == 1 and 1 <= i <= 7 and 1 <= j <= 7:
					g[i, j] = True
		g[0, 1] = g[1, 0] = g[0, 7] = g[1, 8] = g[7, 0] = g[8, 1] = g[7, 8] = g[8, 7] = False
	elif kind == "help":
		pat = ["..####...", ".##..##..", ".....##..", "....##...", "...##....", "...##....", ".........", "...##....", "...##...."]
		for y, row in enumerate(pat):
			for x, ch in enumerate(row):
				g[y, x] = ch == "#"
	return g


def caption_glyphs(kind, close=False):
	frames = []
	for i, c in enumerate(glyph_colours()):
		if close and i in (0, 1):
			c = P["white"]
		f = canvas(9, 9)
		f[_glyph(kind)] = c
		frames.append(f)
	return stack(frames)


# ---- scroll bars ----------------------------------------------------------------------------------------------------------------------
SB = 17  # SM_CXVSCROLL on the guest


def _arrow_mask(direction, n=9):
	g = np.zeros((n, n), dtype=bool)
	# a 7 x 4 chevron-filled triangle, centred
	for k in range(4):
		for j in range(3 - k, 4 + k):
			if direction == "up":
				g[2 + k, 1 + j] = True
			elif direction == "down":
				g[6 - k, 1 + j] = True
			elif direction == "left":
				g[1 + j, 2 + k] = True
			else:
				g[1 + j, 6 - k] = True
	return g


def sb_button_looks():
	track = P["raised"]
	normal = _btn(mix(P["raised3"], P["white"], 0.05), P["raised2"], mix(P["raised3"], P["white"], 0.08), size=SB, r=3)
	hot = _btn(mix(DUSK[2], P["white"], 0.12), DUSK[1], P["horizon"], size=SB, r=3)
	pressed = _btn(P["panel"], P["raised2"], P["gold_down"], size=SB, r=3)
	disabled = _btn(P["raised"], P["raised"], P["raised2"], size=SB, r=3)
	out = []
	for f in (normal, hot, pressed, disabled):
		f = f.copy()
		k = np.all(f == KEY, axis=2)
		f[k] = track
		out.append(f)
	return out


def scroll_arrows():
	looks = sb_button_looks()
	bg, gl = [], []
	glyph_cols = [P["text2"], P["glyph"], P["glyph_pressed"], mix(P["muted"], P["raised"], 0.55)]
	for d in ("up", "down", "left", "right"):
		for s in range(4):
			bg.append(looks[s])
			f = canvas(9, 9)
			f[_arrow_mask(d)] = glyph_cols[s]
			gl.append(f)
	return stack(bg), stack(gl)


def scroll_thumb(vertical):
	track = P["raised"]
	looks = [
		(mix(DUSK[2], P["white"], 0.1), DUSK[1], mix(P["horizon"], P["white"], 0.1)),
		(mix(DUSK[4], P["white"], 0.12), DUSK[3], mix(P["horizon"], P["white"], 0.4)),
		(mix(DUSK[5], P["white"], 0.08), DUSK[4], P["gold"]),
		(P["raised2"], P["raised2"], P["raised3"]),
	]
	frames = []
	L = 24
	for light, base, border in looks:
		f = canvas(SB, L, track) if vertical else canvas(L, SB, track)
		bw, bh = (SB - 4, L - 2) if vertical else (L - 2, SB - 4)
		grad = [mix(light, base, i / max(1, (bw if vertical else bh) - 1)) for i in range(bw if vertical else bh)]
		if vertical:
			body, m = shape(bw, bh, 3, None, border, cols=grad)
		else:
			body, m = shape(bw, bh, 3, None, border, rows=grad)
		ox, oy = (2, 1) if vertical else (1, 2)
		region = f[oy : oy + bh, ox : ox + bw]
		region[m] = body[m]
		frames.append(f)
	return stack(frames)


def scroll_gripper(vertical):
	frames = []
	for c in (P["text2"] * 0.8, P["glyph"] * 0.85, P["grip_pressed"], P["raised3"]):
		if vertical:  # three short horizontal lines
			f = canvas(7, 5)
			f[0, :] = f[2, :] = f[4, :] = c
		else:
			f = canvas(5, 7)
			f[:, 0] = f[:, 2] = f[:, 4] = c
		frames.append(f)
	return stack(frames)


def size_box():
	f = canvas(SB, SB, P["raised"])
	for i in range(3):
		for j in range(3 - i):
			x, y = SB - 4 - j * 4, SB - 4 - i * 4
			f[y : y + 2, x : x + 2] = P["muted"]
			f[y, x] = P["text2"]
	left = f[:, ::-1]
	return stack([f, left])


# Classic Windows scroll bars (the default: the scroll bar art of the Afterglow style stays above, behind --scrollbars). The engine
# draws a window's own scroll bars only through the style's SCROLLBAR class, so the default style carries these classic-looking
# images instead of leaving the class out. The colours are the classic scheme's, the same in every colour scheme.
CL_FACE = np.array([212.0, 208.0, 200.0])
CL_LIGHT = np.array([255.0, 255.0, 255.0])
CL_SHADOW = np.array([128.0, 128.0, 128.0])
CL_DARK = np.array([64.0, 64.0, 64.0])
CL_INK = np.array([0.0, 0.0, 0.0])


def _classic_bevel(w, h, pressed=False):
	"""A classic push button face: raised with two-pixel edges, or flat with a one-pixel shadow outline when pressed."""
	f = canvas(w, h, CL_FACE)
	if pressed:
		f[0, :] = f[-1, :] = f[:, 0] = f[:, -1] = CL_SHADOW
		return f
	f[0, :], f[:, 0] = CL_FACE, CL_FACE
	f[-1, :], f[:, -1] = CL_DARK, CL_DARK
	f[1, 1 : w - 1], f[1 : h - 1, 1] = CL_LIGHT, CL_LIGHT
	f[-2, 1 : w - 1], f[1 : h - 1, -2] = CL_SHADOW, CL_SHADOW
	return f


def classic_scroll_arrows():
	bg, gl = [], []
	for d in ("up", "down", "left", "right"):
		for s in range(4):  # normal, hot, pressed, disabled
			bg.append(_classic_bevel(SB, SB, pressed=(s == 2)))
			f = canvas(9, 9)
			m = _arrow_mask(d)
			if s == 3:  # disabled: shadow grey over a white copy one pixel down and right
				sh = np.zeros_like(m)
				sh[1:, 1:] = m[:-1, :-1]
				f[sh] = CL_LIGHT
				f[m] = CL_SHADOW
			else:
				f[m] = CL_INK
			gl.append(f)
	return stack(bg), stack(gl)


def classic_scroll_thumb(vertical):
	w, h = (SB, 24) if vertical else (24, SB)
	return stack([_classic_bevel(w, h)] * 4)


def classic_scroll_track(pressed=False):
	"""The classic dithered track: a one-pixel checker of the face and white (or of shadow grey and the face while pressed)."""
	a, b = (CL_SHADOW, CL_FACE) if pressed else (CL_FACE, CL_LIGHT)
	f = canvas(2, 2, a)
	f[0, 1] = f[1, 0] = b
	return f


def classic_size_box():
	f = canvas(SB, SB, CL_FACE)
	e = SB - 2
	for d in (3, 7, 11):  # three diagonal ridges: shadow grey with a white edge on the lower-right side
		for x in range(SB):
			for y in range(SB):
				if x <= e and y <= e and x + y == 2 * e - d:
					f[y, x] = CL_SHADOW
				elif x <= e + 1 and y <= e + 1 and x + y == 2 * e - d + 1 and x > 0 and y > 0:
					f[y, x] = CL_LIGHT
	return stack([f, f[:, ::-1]])


# ---- dialog controls (they sit on the classic cream client) ---------------------------------------------------------------------------


def push_button():
	W, H = 18, 21
	navy_edge = mix(CTL[0], P["edge"], 0.45)
	normal = _btn_rect(W, H, P["white"] * 0.97, P["cream_hi"] * 0.985, navy_edge)
	hot = _btn_rect(W, H, P["white"], mix(P["cream_hi"], P["rose_light"], 0.08), CTL[6], ring=mix(P["rose_light"], P["white"], 0.35))
	pressed = _btn_rect(W, H, P["cream_lo"], P["cream"], CTL[0])
	disabled = _btn_rect(W, H, P["cream_hi"], P["cream_hi"], P["edge_dim"])
	default = _btn_rect(W, H, P["white"] * 0.97, P["cream_hi"] * 0.985, navy_edge, ring=P["gold"], ring2=P["gold_light"])
	return stack([normal, hot, pressed, disabled, default])


def _btn_rect(W, H, top, bottom, border, ring=None, ring2=None, r=3):
	rows = gloss_rows(H, top, bottom, 0.5)
	a, m = shape(W, H, r, None, border, rows=rows)
	if ring is not None:
		m2 = m & ~inner_edge(m)
		e2 = inner_edge(m2)
		a[e2] = ring
		if ring2 is not None:
			m3 = m2 & ~e2
			a[inner_edge(m3)] = ring2
	return a


def _tick():
	g = np.zeros((13, 13), dtype=bool)
	pts = [(3, 6), (4, 7), (5, 8), (6, 7), (7, 6), (8, 5), (9, 4)]
	for x, y in pts:
		g[y, x] = g[y - 1, x] = True
	return g


def check_boxes():
	frames = []
	navy_edge = mix(CTL[0], P["edge"], 0.45)
	unchecked = [
		(P["white"], navy_edge),
		(mix(P["white"], P["rose_light"], 0.12), P["rose_mid"]),
		(P["cream_hi"], CTL[0]),
		(P["cream_hi"], P["edge_dim"]),
	]
	checked = [(CTL[1], CTL[0]), (CTL[3], CTL[0]), (CTL[0], P["tile"]), (P["edge_dim"], P["edge_dim"])]
	for fill, border in unchecked:
		frames.append(shape(13, 13, 2, fill, border)[0])
	for i, (fill, border) in enumerate(checked):
		a = shape(13, 13, 2, fill, border)[0]
		a[_tick()] = P["white"] if i == 3 else P["gold"]
		frames.append(a)
	for i, (fill, border) in enumerate(unchecked):
		a = shape(13, 13, 2, fill, border)[0]
		a[4:9, 4:9] = P["edge_dim"] if i == 3 else CTL[1]
		frames.append(a)
	return stack(frames)


def radio_buttons():
	frames = []
	navy_edge = mix(CTL[0], P["edge"], 0.45)
	unchecked = [(P["white"], navy_edge), (mix(P["white"], P["rose_light"], 0.12), P["rose_mid"]), (P["cream_hi"], CTL[0]), (P["cream_hi"], P["edge_dim"])]
	checked = [(CTL[1], CTL[0]), (CTL[3], CTL[0]), (CTL[0], P["tile"]), (P["edge_dim"], P["edge_dim"])]
	dot = round_mask(5, 5, 2.5)
	for fill, border in unchecked:
		frames.append(shape(13, 13, 6.5, fill, border)[0])
	for i, (fill, border) in enumerate(checked):
		a = shape(13, 13, 6.5, fill, border)[0]
		sub = a[4:9, 4:9]
		sub[dot] = P["white"] if i == 3 else P["gold"]
		frames.append(a)
	return stack(frames)


def group_box():
	a, m = shape(10, 10, 3, KEY, P["edge_dim"])
	return a


def drop_button_bg(w=16, h=18):
	looks = [
		(mix(CTL[2], P["white"], 0.12), CTL[1], CTL[0]),
		(mix(CTL[4], P["white"], 0.14), CTL[3], CTL[0]),
		(CTL[0], CTL[0], P["gold_down"]),
		(P["cream_lo"], P["cream_lo"], P["edge_dim"]),
	]
	return stack([_btn_rect(w, h, t, b, e, r=2) for t, b, e in looks])


def chevron_glyphs(direction):
	cols = [P["white"], P["white"], P["gold_light"], P["cream_hi"]]
	out = []
	for c in cols:
		f = canvas(9, 9)
		f[_arrow_mask(direction)] = c
		out.append(f)
	return stack(out)


def tab_item():
	W, H = 14, 20
	edge = mix(CTL[0], P["edge"], 0.6)
	frames = []
	for kind in ("normal", "hot", "selected", "disabled", "focused"):
		if kind == "disabled":
			rows = [P["cream_hi"]] * H
			border = P["edge_dim"]
		elif kind in ("selected", "focused"):
			rows = [P["cream"]] * H
			border = edge
		else:
			rows = gloss_rows(H, P["white"] * 0.97, P["cream_hi"], 0.5)
			border = edge
		a, m = shape(W, H, 3, None, border, corners="tl tr", rows=rows)
		inner = m & ~inner_edge(m)
		if kind == "hot":
			ys = np.nonzero(inner.any(axis=1))[0][:2]
			for y in ys:
				a[y, inner[y]] = P["rose"]
		if kind in ("selected", "focused"):
			ys = np.nonzero(inner.any(axis=1))[0][:2]
			a[ys[0], inner[ys[0]]] = P["gold"]
			a[ys[1], inner[ys[1]]] = P["gold_down"]
			a[H - 1, 1 : W - 1] = P["cream"]  # open at the bottom so it joins the pane
		frames.append(a)
	return stack(frames)


def tab_body():
	return canvas(8, 8, P["cream"])


def progress_bar(vertical=False):
	a, m = shape(12, 12, 2, P["white"], P["edge"])
	a[1, 2:10] = P["cream_hi"]
	return a if not vertical else a.transpose(1, 0, 2)


def progress_chunk(vertical=False):
	h = 12
	rows = [P["gold_light"], P["gold_pale"]] + [P["gold"]] * 5 + [mix(P["gold"], P["gold_down"], 0.5)] * 2 + [P["gold_down"]] * 2 + [P["gold_deep"]]
	a = np.zeros((h, 8, 3))
	for y in range(h):
		a[y, :] = rows[y]
	a[:, -1] = mix(a[:, -1], P["gold_deep"], 0.35)
	return a if not vertical else a.transpose(1, 0, 2)[::-1]


def header_item():
	W, H = 12, 20
	frames = []
	for kind in ("normal", "hot", "pressed"):
		rows = gloss_rows(H, P["white"] * 0.98, P["cream_hi"], 0.5) if kind != "pressed" else [P["cream"]] * H
		a = np.zeros((H, W, 3))
		for y in range(H):
			a[y, :] = rows[y]
		a[:, W - 1] = P["edge_dim"]
		a[2 : H - 3, W - 2] = P["white"]
		base = {"normal": [P["cream_lo"], P["edge_dim"]], "hot": [P["rose_light"], P["rose"]], "pressed": [P["gold_light"], P["gold"]]}[kind]
		a[H - 2, :] = base[0]
		a[H - 1, :] = base[1]
		frames.append(a)
	return stack(frames)


def toolbar_button():
	W = 16
	frames = [canvas(W, W)]  # normal: drawn with BgType None
	frames.append(_btn_rect(W, W, P["white"], mix(P["cream_hi"], P["rose_light"], 0.06), CTL[6]))
	frames.append(_btn_rect(W, W, P["cream_lo"], P["cream"], CTL[0]))
	frames.append(canvas(W, W))
	frames.append(_btn_rect(W, W, mix(P["cream_hi"], CTL[1], 0.06), P["cream_hi"], CTL[1]))
	frames.append(_btn_rect(W, W, P["white"], mix(P["cream_hi"], CTL[1], 0.06), CTL[6]))
	return stack(frames)


def toolbar_separator(vertical=False):
	a = canvas(2, 18)
	a[1:17, 0] = P["edge_dim"]
	a[1:17, 1] = P["white"]
	return a if not vertical else a.transpose(1, 0, 2)


def rebar_gripper():
	a = canvas(4, 4)
	a[1, 1] = P["edge"]
	a[2, 2] = P["white"]
	return a


def status_pane():
	"""A sunken pane outline (shadow on the top and left, light on the bottom and right), so status bars match classic ones."""
	a = canvas(6, 6)
	a[0, :] = P["shadow"]
	a[:, 0] = P["shadow"]
	a[5, 1:] = P["white"]
	a[1:, 5] = P["white"]
	return a


def status_gripper():
	"""Three diagonal ridges in the bottom-right corner, each a light line over a shadow line."""
	a = canvas(12, 12)
	for k in (0, 4, 8):
		for i in range(12 - k):
			x, y = k + i, 11 - i
			if 0 <= x < 12 and 0 <= y < 12:
				a[y, x] = P["white"]
				if x + 1 < 12:
					a[y, x + 1] = P["shadow"]
				if x + 2 < 12:
					a[y, x + 2] = P["shadow"]
	return a


def tree_glyphs():
	frames = []
	for opened in (False, True):
		a, m = shape(9, 9, 1, None, P["edge"], rows=gloss_rows(9, P["white"], P["cream_hi"], 0.5))
		a[4, 2:7] = CTL[0]
		if not opened:
			a[2:7, 4] = CTL[0]
		frames.append(a)
	return stack(frames)


def track():
	a, m = shape(8, 4, 1, P["white"], P["edge"])
	return a


def trackbar_thumb(vertical=False):
	W, H = 11, 19
	looks = [
		(mix(CTL[2], P["white"], 0.12), CTL[1], CTL[0], None),
		(mix(CTL[4], P["white"], 0.14), CTL[3], CTL[0], None),
		(P["gold_light"], P["gold"], P["gold_deep"], None),
		(mix(CTL[2], P["white"], 0.12), CTL[1], P["gold_down"], P["gold_light"]),
		(P["cream_lo"], P["cream_lo"], P["edge_dim"], None),
	]
	frames = [_btn_rect(W, H, t, b, e, ring=r, r=2) for t, b, e, r in looks]
	if vertical:
		frames = [f.transpose(1, 0, 2) for f in frames]
	return stack(frames)


# ---- shell: taskbar, Start button, task buttons, tray ---------------------------------------------------------------------------------


def taskbar_background():
	"""Near-black band, lifting a little towards the top, with a dusk hairline along its top edge (same columns as the caption)."""
	h = 30
	a = np.zeros((h, CAP_W, 3))
	for y in range(2, h):
		a[y, :] = mix(P["raised2"], P["panel"], ((y - 2) / (h - 3)) ** 0.8)
	for x in range(CAP_W):
		t = min(max((x - CAP_MARGIN + 0.5) / CAP_MID, 0), 1)
		a[0, x] = mix(dusk_at(t), P["white"], 0.1)
		a[1, x] = P["night"]
	return a


def taskbar_sizer(side="bottom"):
	"""The taskbar's top edge: a dusk hairline over a near-black line."""
	w = CAP_W
	a = np.zeros((2, w, 3))
	for x in range(w):
		t = min(max((x - CAP_MARGIN + 0.5) / CAP_MID, 0), 1)
		a[0, x] = mix(dusk_at(t), P["white"], 0.08)
		a[1, x] = P["night"]
	if side == "top":
		a = a[::-1]
	elif side in ("left", "right"):
		a = a.transpose(1, 0, 2)
		if side == "right":
			a = a[:, ::-1]
	return a


def start_button():
	W, H = 40, 26
	looks = [
		(mix(P["gold"], P["gold_light"], 0.45), P["gold"], P["gold_deep"], P["gold_pale"], P["gold_down"]),
		(P["gold_light"], mix(P["gold"], P["gold_light"], 0.35), mix(P["gold_deep"], P["gold"], 0.4), P["white"], P["gold"]),
		(P["gold_down"], mix(P["gold_down"], P["gold"], 0.5), mix(P["gold_deep"], P["night"], 0.3), None, P["gold_down"]),
		(P["raised3"], P["raised2"], P["raised"], None, P["raised2"]),
		(mix(P["gold"], P["gold_light"], 0.45), P["gold"], P["gold_deep"], P["gold_pale"], P["gold_down"]),
	]
	frames = []
	for i, (top, bottom, border, shine, foot) in enumerate(looks):
		rows = gloss_rows(H, top, bottom, 0.48)
		a, m = shape(W, H, 10, None, border, corners="tr br", rows=rows)
		inner = m & ~inner_edge(m)
		ys = np.nonzero(inner.any(axis=1))[0]
		if shine is not None:
			a[ys[0], inner[ys[0]]] = shine
		else:  # pressed: a shadow inside the top edge
			a[ys[0], inner[ys[0]]] = mix(border, bottom, 0.3)
		a[ys[-1], inner[ys[-1]]] = foot
		frames.append(a)
	return stack(frames)


def task_button():
	W, H = 20, 24
	looks = {
		"normal": (mix(P["raised3"], P["white"], 0.06), mix(P["raised2"], P["raised3"], 0.4), mix(P["raised3"], P["white"], 0.16), False),
		"hot": (mix(DUSK[1], P["white"], 0.06), mix(DUSK[0], P["raised2"], 0.4), P["horizon"], False),
		"pressed": (P["panel"], P["raised"], P["horizon"], False),
		"disabled": (P["raised"], P["raised"], P["raised2"], False),
		"checked": (mix(DUSK[3], P["white"], 0.08), DUSK[1], mix(P["horizon"], P["white"], 0.2), True),
		"hotchecked": (mix(DUSK[4], P["white"], 0.12), DUSK[2], mix(P["horizon"], P["white"], 0.35), True),
	}
	frames = []
	for top, bottom, border, ink in looks.values():
		a = _btn_rect(W, H, top, bottom, border)
		if ink:  # the active task carries the gold ink line
			a[H - 3, 3 : W - 3] = P["gold"]
			a[H - 2, 4 : W - 4] = P["gold_down"]
		frames.append(a)
	return stack(frames)


def flash_button():
	return _btn_rect(20, 24, mix(P["rose"], P["white"], 0.2), P["rose_mid"], P["rose_deep"])


def tray_background():
	W, H = 12, 30
	rows = [mix(P["raised2"], P["panel2"], (y / (H - 1))) for y in range(H)]
	a, m = shape(W, H, 4, None, None, corners="tl bl", rows=rows)
	e = inner_edge(m)
	e[:, W - 1] = False
	e[0, :] &= np.arange(W) < 5
	e[H - 1, :] &= np.arange(W) < 5
	a[e] = DUSK[1]
	a[0, 4:] = DUSK[1]
	return a


def show_desktop():
	W, H = 8, 26
	looks = [(P["raised"], DUSK[1]), (DUSK[1], DUSK[3]), (P["night"], P["gold"]), (P["raised"], P["raised2"]), (P["raised"], DUSK[1])]
	frames = []
	for fill, line in looks:
		a = np.zeros((H, W, 3))
		a[:, :] = fill
		a[:, 0] = line
		frames.append(a)
	return stack(frames)


def all_art(scheme="Dusk", scrollbars=False):
	"""Name (path inside the style, as the INI names it) to image, drawn in the named colour scheme. scrollbars picks the Afterglow
	scroll bar art; otherwise the scroll bars are the classic Windows ones."""
	use_scheme(scheme)
	cap, maxcap = captions()
	art = {
		"window/caption.bmp": cap,
		"window/caption-max.bmp": maxcap,
		"window/frame-left.bmp": frame_side(False),
		"window/frame-right.bmp": frame_side(True),
		"window/frame-bottom.bmp": frame_bottom(),
		"window/button.bmp": caption_button_bg(False),
		"window/button-close.bmp": caption_button_bg(True),
		"window/glyph-min.bmp": caption_glyphs("min"),
		"window/glyph-max.bmp": caption_glyphs("max"),
		"window/glyph-restore.bmp": caption_glyphs("restore"),
		"window/glyph-close.bmp": caption_glyphs("close", close=True),
		"window/glyph-help.bmp": caption_glyphs("help"),
		"controls/push.bmp": push_button(),
		"controls/check.bmp": check_boxes(),
		"controls/radio.bmp": radio_buttons(),
		"controls/group.bmp": group_box(),
		"controls/drop.bmp": drop_button_bg(),
		"controls/glyph-down.bmp": chevron_glyphs("down"),
		"controls/glyph-up.bmp": chevron_glyphs("up"),
		"controls/glyph-left.bmp": chevron_glyphs("left"),
		"controls/glyph-right.bmp": chevron_glyphs("right"),
		"controls/tab.bmp": tab_item(),
		"controls/page.bmp": tab_body(),
		"controls/progress.bmp": progress_bar(),
		"controls/progress-v.bmp": progress_bar(True),
		"controls/chunk.bmp": progress_chunk(),
		"controls/chunk-v.bmp": progress_chunk(True),
		"controls/header.bmp": header_item(),
		"controls/toolbar.bmp": toolbar_button(),
		"controls/separator.bmp": toolbar_separator(),
		"controls/separator-v.bmp": toolbar_separator(True),
		"controls/gripper.bmp": rebar_gripper(),
		"controls/status-pane.bmp": status_pane(),
		"controls/status-grip.bmp": status_gripper(),
		"controls/tree-glyph.bmp": tree_glyphs(),
		"controls/track.bmp": track(),
		"controls/thumb.bmp": trackbar_thumb(),
		"controls/thumb-v.bmp": trackbar_thumb(True),
		"shell/taskbar.bmp": taskbar_background(),
		"shell/sizer-bottom.bmp": taskbar_sizer("bottom"),
		"shell/sizer-top.bmp": taskbar_sizer("top"),
		"shell/sizer-left.bmp": taskbar_sizer("left"),
		"shell/sizer-right.bmp": taskbar_sizer("right"),
		"shell/start.bmp": start_button(),
		"shell/task.bmp": task_button(),
		"shell/flash.bmp": flash_button(),
		"shell/tray.bmp": tray_background(),
		"shell/show-desktop.bmp": show_desktop(),
	}
	if scrollbars:
		arrows_bg, arrows_gl = scroll_arrows()
		art.update(
			{
				"scroll/arrow.bmp": arrows_bg,
				"scroll/arrow-glyph.bmp": arrows_gl,
				"scroll/thumb-v.bmp": scroll_thumb(True),
				"scroll/thumb-h.bmp": scroll_thumb(False),
				"scroll/grip-v.bmp": scroll_gripper(True),
				"scroll/grip-h.bmp": scroll_gripper(False),
				"scroll/sizebox.bmp": size_box(),
			}
		)
	else:
		arrows_bg, arrows_gl = classic_scroll_arrows()
		art.update(
			{
				"scroll/arrow.bmp": arrows_bg,
				"scroll/arrow-glyph.bmp": arrows_gl,
				"scroll/thumb-v.bmp": classic_scroll_thumb(True),
				"scroll/thumb-h.bmp": classic_scroll_thumb(False),
				"scroll/track.bmp": classic_scroll_track(),
				"scroll/track-pressed.bmp": classic_scroll_track(True),
				"scroll/sizebox.bmp": classic_size_box(),
			}
		)
	return art
