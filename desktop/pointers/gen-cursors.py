#!/usr/bin/env python3
# Draw the Afterglow pointer set procedurally and write it as 32 x 32 ARGB .cur files (and .ani for the two busy pointers):
# a navy body with a soft gold rim, a light highlight and a faint dark halo, so each pointer reads on the dark desktop and on a
# white page. Each one has the footprint and hot spot of the standard ReactOS pointer it replaces. Every shape is defined here as polygons, circles and strokes; nothing is traced from another pointer set.
# Usage: gen-cursors.py OUT_DIR [--sheet PNG]
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
import math
import os
import struct
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

S = 8  # supersampling factor: shapes are drawn at 256 x 256 and reduced to 32 x 32
N = 32
NAVY = (31, 37, 84)  # dusk step 1
NAVY_HI = (88, 94, 150)  # highlight inside the body
GOLD = (255, 170, 64)
GOLD_LIGHT = (255, 208, 142)
ROSE = (244, 63, 94)
INK = (10, 12, 26)
CREAM = (255, 244, 214)


# Each pointer is designed on a roomy 32-unit grid and then placed at the footprint of a standard pointer: XF scales the design
# by k about an anchor (ax, ay) and puts that anchor at (bx, by) in the 32 x 32 image. Rim and halo widths are not scaled.
XF = (1.0, 0.0, 0.0, 0.0, 0.0)


def place(k, ax, ay, bx, by):
	global XF
	XF = (k, ax, ay, bx, by)


def T(x, y):
	k, ax, ay, bx, by = XF
	return bx + (x - ax) * k, by + (y - ay) * k


def L(v):
	return v * XF[0]


def P(pts):
	return [(T(x, y)[0] * S, T(x, y)[1] * S) for x, y in pts]


class Layer:
	"""A supersampled RGBA canvas."""

	def __init__(self):
		self.im = Image.new("RGBA", (N * S, N * S), (0, 0, 0, 0))
		self.d = ImageDraw.Draw(self.im)


def mask_poly(polys, width=0):
	m = Image.new("L", (N * S, N * S), 0)
	d = ImageDraw.Draw(m)
	for poly in polys:
		if poly[0] == "circle":
			_, cx, cy, r = poly
			(cx, cy), r = T(cx, cy), L(r)
			d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=255)
		elif poly[0] == "ring":
			_, cx, cy, r, w = poly
			(cx, cy), r, w = T(cx, cy), L(r), L(w)
			d.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], outline=255, width=int(w * S))
		elif poly[0] == "line":
			_, pts, w = poly
			w = L(w)
			d.line(P(pts), fill=255, width=int(w * S), joint="curve")
			for x, y in (T(*pts[0]), T(*pts[-1])):
				d.ellipse([(x - w / 2) * S, (y - w / 2) * S, (x + w / 2) * S, (y + w / 2) * S], fill=255)
		elif poly[0] == "rrect":
			_, x0, y0, x1, y1, r = poly
			(x0, y0), (x1, y1), r = T(x0, y0), T(x1, y1), L(r)
			d.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=r * S, fill=255)
		else:
			d.polygon(P(poly), fill=255)
	return m


def grow(m, px):
	"""Dilate a supersampled mask by px output pixels."""
	k = int(px * S) * 2 + 1
	return m.filter(ImageFilter.MaxFilter(k if k % 2 else k + 1))


def shrink(m, px):
	k = int(px * S) * 2 + 1
	return m.filter(ImageFilter.MinFilter(k if k % 2 else k + 1))


def compose(body, rim=GOLD, fill=NAVY, highlight=True, extra=None, halo_cut=None):
	"""Body mask -> halo (dark, faint, about 1 px), rim (gold, 1 px), fill (navy) and a light highlight along the upper-left inside edge."""
	out = np.zeros((N * S, N * S, 4), dtype=float)

	def put(mask, colour, alpha=1.0):
		a = np.asarray(mask, dtype=float) / 255.0 * alpha
		for c in range(3):
			out[..., c] = out[..., c] * (1 - a) + colour[c] * a
		out[..., 3] = out[..., 3] * (1 - a) + a

	halo = grow(body, 1.5).filter(ImageFilter.GaussianBlur(S * 0.4))
	if halo_cut is not None:  # keep the halo outside a closed shape (the inside of a ring stays clear)
		halo = Image.fromarray((np.asarray(halo, dtype=float) * (1 - np.asarray(halo_cut, dtype=float) / 255)).astype(np.uint8))
	put(halo, INK, 0.35)
	put(grow(body, 1.0), rim)
	inner = body
	put(inner, fill)
	if highlight:
		# light along the upper-left: the inside edge shifted down-right minus itself
		core = shrink(inner, 0.75)
		shifted = Image.fromarray(np.roll(np.roll(np.asarray(core), int(S * 0.9), 0), int(S * 0.9), 1))
		hl = np.clip(np.asarray(core, dtype=int) - np.asarray(shifted, dtype=int), 0, 255).astype(np.uint8)
		put(Image.fromarray(hl), NAVY_HI, 0.9)
	if extra:
		for mask, colour in extra:
			put(mask, colour)
	return out


def reduce(hi):
	"""Box-filter the supersampled RGBA (straight alpha) down to 32 x 32 with premultiplied averaging."""
	a = hi[..., 3:4]
	pre = hi[..., :3] * a
	pre = pre.reshape(N, S, N, S, 3).mean(axis=(1, 3))
	al = a.reshape(N, S, N, S, 1).mean(axis=(1, 3))
	rgb = np.where(al > 1e-6, pre / np.maximum(al, 1e-6), 0)
	img = np.concatenate([rgb, al * 255], axis=2)
	img = np.clip(np.round(img), 0, 255).astype(np.uint8)
	img[img[..., 3] < 3] = 0
	return img


# ---- shapes ---------------------------------------------------------------------------------------------------------------------------
ARROW = [(2.5, 2.5), (2.5, 22.5), (7.2, 18.2), (10.6, 26.2), (14.0, 24.8), (10.7, 17.0), (17.0, 17.0)]


def arrow_body():
	return mask_poly([ARROW])


def arrow():
	place(0.72, 2.5, 2.5, 2.5, 2.5)  # about 11 x 19, tip and hot spot at (2, 2)
	return compose(arrow_body()), (2, 2)


def help_cursor():
	place(0.62, 18.5, 5.5, 14.5, 3.5)  # a 10 px question mark beside the arrow
	q = mask_poly([("line", [(18.5, 9.0), (19.5, 6.5), (22.5, 5.5), (25.5, 6.5), (26.2, 9.0), (25.0, 11.2), (22.6, 12.6), (22.4, 15.0)], 2.6), ("circle", 22.4, 19.2, 1.6)])
	place(0.72, 2.5, 2.5, 2.5, 2.5)
	return compose(arrow_body(), extra=[(grow(q, 0.8), INK), (q, GOLD)]), (2, 2)


def spinner_masks(cx, cy, r, w, phase):
	ring = mask_poly([("ring", cx, cy, r, w)])
	arc = Image.new("L", (N * S, N * S), 0)
	d = ImageDraw.Draw(arc)
	start = phase * 45 - 90
	(cx, cy), r, w = T(cx, cy), L(r), L(w)
	d.arc([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], start, start + 110, fill=255, width=int(w * S))
	return ring, arc


def working(phase=0):
	place(1.0, 0, 0, 0, 0)  # a 14 px ring at the arrow's foot
	ring, arc = spinner_masks(17.5, 18.0, 5.2, 2.2, phase)
	disc = mask_poly([("circle", 17.5, 18.0, 6.2)])
	place(0.72, 2.5, 2.5, 2.5, 2.5)
	body = arrow_body()
	return compose(body, extra=[(grow(disc, 0.8), INK), (disc, NAVY), (ring, GOLD), (arc, ROSE)]), (2, 2)


def busy(phase=0):
	# The Quill ring: a gold ring on a navy disc, with a rose arc that travels round it.
	place(0.62, 16, 16, 16, 16)  # 16 px across, hot spot in the middle
	disc = mask_poly([("circle", 16, 16, 11.5)])
	ring, arc = spinner_masks(16, 16, 9.0, 3.6, phase)
	nib = mask_poly([("circle", 16, 16, 2.0)])
	return compose(disc, rim=GOLD_LIGHT, highlight=False, extra=[(ring, GOLD), (arc, ROSE), (nib, CREAM)]), (16, 16)


def crosshair():
	place(0.52, 16, 16, 11.5, 11.5)  # 17 x 17, hot spot (11, 11)
	arms = [("rrect", 14.4, 2, 17.6, 12.5, 1.0), ("rrect", 14.4, 19.5, 17.6, 30, 1.0), ("rrect", 2, 14.4, 12.5, 17.6, 1.0), ("rrect", 19.5, 14.4, 30, 17.6, 1.0)]
	dot = mask_poly([("circle", 16, 16, 1.2)])
	return compose(mask_poly(arms), highlight=False, extra=[(dot, GOLD)]), (11, 11)


def ibeam():
	place(0.62, 16, 16, 6.5, 9.5)  # 7 x 16, hot spot (6, 9)
	shape = [("rrect", 14.5, 6, 17.5, 26, 0.8), ("rrect", 11, 4.5, 15.6, 6.8, 1.0), ("rrect", 16.4, 4.5, 21, 6.8, 1.0), ("rrect", 11, 25.2, 15.6, 27.5, 1.0), ("rrect", 16.4, 25.2, 21, 27.5, 1.0)]
	return compose(mask_poly(shape), highlight=False), (6, 9)


def unavailable():
	place(0.75, 16, 16, 12.5, 12.5)  # 20 x 20, hot spot in the middle
	ring = mask_poly([("ring", 16, 16, 11, 3.4)])
	bar = mask_poly([[(8.6, 21.3), (21.3, 8.6), (23.4, 10.7), (10.7, 23.4)]])
	body = Image.fromarray(np.maximum(np.asarray(ring), np.asarray(bar)))
	hole = shrink(mask_poly([("circle", 16, 16, 9.3)]), 0.5)
	return compose(body, rim=INK, fill=ROSE, highlight=False, halo_cut=hole), (12, 12)


def double_arrow(angle):
	"""A two-headed arrow along the x axis, rotated by angle degrees about the centre."""
	pts = [(3, 16), (9, 9.5), (9, 14), (23, 14), (23, 9.5), (29, 16), (23, 22.5), (23, 18), (9, 18), (9, 22.5)]
	t = math.radians(angle)
	place(0.72 if angle % 90 == 0 else 0.62, 16, 16, 15.5, 15.5)  # 21 x 11 straight, 15 x 15 diagonal
	rot = [(16 + (x - 16) * math.cos(t) - (y - 16) * math.sin(t), 16 + (x - 16) * math.sin(t) + (y - 16) * math.cos(t)) for x, y in pts]
	return compose(mask_poly([rot]), highlight=False), (15, 15)


def move():
	place(0.78, 16, 16, 15.5, 15.5)  # 23 x 23
	h = [(3, 16), (8, 11), (8, 14.5), (14.5, 14.5), (14.5, 8), (11, 8), (16, 3), (21, 8), (17.5, 8), (17.5, 14.5), (24, 14.5), (24, 11), (29, 16), (24, 21), (24, 17.5), (17.5, 17.5), (17.5, 24), (21, 24), (16, 29), (11, 24), (14.5, 24), (14.5, 17.5), (8, 17.5), (8, 21)]
	return compose(mask_poly([h]), highlight=False), (15, 15)


def up_arrow():
	place(0.68, 16, 2, 15.5, 5.0)  # 11 x 19, tip and hot spot at (15, 5)
	pts = [(16, 2), (24, 11), (19, 11), (19, 28), (13, 28), (13, 11), (8, 11)]
	return compose(mask_poly([pts]), highlight=True), (15, 5)


def hand():
	place(0.62, 12.3, 2.5, 9.5, 2.5)  # about 14 x 19, fingertip and hot spot at (9, 2)
	parts = [
		("rrect", 10.0, 2.5, 14.6, 20, 2.3),  # index finger
		("rrect", 14.0, 10.0, 18.4, 21, 2.2),
		("rrect", 17.8, 11.0, 22.2, 21, 2.2),
		("rrect", 21.6, 12.5, 25.8, 21, 2.1),
		("rrect", 10.0, 16, 25.8, 26, 4.0),  # palm
		[(10.4, 22.5), (5.5, 16.5), (5.0, 14.8), (6.4, 14.0), (10.6, 17.2)],  # thumb
		("rrect", 11.5, 24, 24.5, 29.5, 1.5),  # wrist
	]
	return compose(mask_poly(parts)), (9, 2)


CURSORS = {
	"arrow": (arrow, "Arrow"),
	"help": (help_cursor, "Help"),
	"working": (working, "AppStarting"),
	"busy": (busy, "Wait"),
	"cross": (crosshair, "Crosshair"),
	"ibeam": (ibeam, "IBeam"),
	"no": (unavailable, "No"),
	"size-ns": (lambda: double_arrow(90), "SizeNS"),
	"size-we": (lambda: double_arrow(0), "SizeWE"),
	"size-nwse": (lambda: double_arrow(45), "SizeNWSE"),
	"size-nesw": (lambda: double_arrow(-45), "SizeNESW"),
	"move": (move, "SizeAll"),
	"up": (up_arrow, "UpArrow"),
	"hand": (hand, "Hand"),
}


# ---- file formats ---------------------------------------------------------------------------------------------------------------------


def cursor_image(img):
	"""BITMAPINFOHEADER + 32-bit BGRA rows (bottom-up) + 1-bit AND mask: the image part of a .cur entry and of an RT_CURSOR resource."""
	h, w = img.shape[:2]
	hdr = struct.pack("<IiiHHIIiiII", 40, w, h * 2, 1, 32, 0, w * h * 4 + h * ((w + 31) // 32) * 4, 0, 0, 0, 0)
	xor = b"".join(img[y, :, [2, 1, 0, 3]].T.astype(np.uint8).tobytes() for y in range(h - 1, -1, -1))
	rows = []
	for y in range(h - 1, -1, -1):
		bits = 0
		for x in range(w):
			if img[y, x, 3] == 0:
				bits |= 1 << (31 - x)
		rows.append(struct.pack(">I", bits))
	return hdr + xor + b"".join(rows)


def cur_file(img, hot):
	data = cursor_image(img)
	return struct.pack("<HHH", 0, 2, 1) + struct.pack("<BBBBHHII", 32, 32, 0, 0, hot[0], hot[1], len(data), 22) + data


def ani_file(frames, hot, rate):
	icons = b"".join(b"icon" + struct.pack("<I", len(c)) + c + (b"\0" if len(c) & 1 else b"") for c in (cur_file(f, hot) for f in frames))
	anih = struct.pack("<9I", 36, len(frames), len(frames), 32, 32, 32, 1, rate, 1)
	body = b"ACON" + b"anih" + struct.pack("<I", 36) + anih + b"LIST" + struct.pack("<I", 4 + len(icons)) + b"fram" + icons
	return b"RIFF" + struct.pack("<I", len(body)) + body


def main():
	out = sys.argv[1]
	sheet = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--sheet" else None
	os.makedirs(out, exist_ok=True)
	images = {}
	for name, (fn, _) in CURSORS.items():
		hi, hot = fn()
		img = reduce(hi)
		images[name] = (img, hot)
		with open(os.path.join(out, f"afterglow-{name}.cur"), "wb") as f:
			f.write(cur_file(img, hot))
	for name, fn in (("working", working), ("busy", busy)):
		frames = []
		for ph in range(8):
			hi, hot = fn(ph)
			frames.append(reduce(hi))
		with open(os.path.join(out, f"afterglow-{name}.ani"), "wb") as f:
			f.write(ani_file(frames, hot, 6))
	if sheet:
		backs = [(9, 14, 42), (255, 255, 255), (212, 208, 200)]
		Z = 4
		cell = N * Z + 12
		W = cell * len(images)
		sh = Image.new("RGB", (W, cell * len(backs)), (60, 60, 60))
		for r, bg in enumerate(backs):
			for c, (name, (img, hot)) in enumerate(images.items()):
				tile = Image.new("RGB", (N, N), bg)
				tile.paste(Image.fromarray(img, "RGBA"), (0, 0), Image.fromarray(img, "RGBA"))
				big = tile.resize((N * Z, N * Z), Image.NEAREST)
				d = ImageDraw.Draw(big)
				hx, hy = hot[0] * Z + Z // 2, hot[1] * Z + Z // 2
				d.line([hx - 3, hy, hx + 3, hy], fill=(0, 200, 0))
				d.line([hx, hy - 3, hx, hy + 3], fill=(0, 200, 0))
				sh.paste(big, (c * cell + 6, r * cell + 6))
		sh.save(sheet)


if __name__ == "__main__":
	main()
