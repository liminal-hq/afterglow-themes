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

SUPERSAMPLE = 8  # supersampling factor: shapes are drawn at 256 x 256 and reduced to 32 x 32
CURSOR_SIZE = 32
HIRES = CURSOR_SIZE * SUPERSAMPLE
NAVY = (31, 37, 84)  # dusk step 1
NAVY_HI = (88, 94, 150)  # highlight inside the body
GOLD = (255, 170, 64)
GOLD_LIGHT = (255, 208, 142)
ROSE = (244, 63, 94)
INK = (10, 12, 26)
CREAM = (255, 244, 214)


# Each pointer is designed on a roomy 32-unit grid and then placed at the footprint of a standard pointer: PLACEMENT scales the
# design by scale about an anchor (anchor_x, anchor_y) and puts that anchor at (target_x, target_y) in the 32 x 32 image. Rim and
# halo widths are not scaled.
PLACEMENT = (1.0, 0.0, 0.0, 0.0, 0.0)


def set_placement(scale, anchor_x, anchor_y, target_x, target_y):
	global PLACEMENT
	PLACEMENT = (scale, anchor_x, anchor_y, target_x, target_y)


def point_transform(x, y):
	"""A design point in image units (32 x 32) under the current placement."""
	scale, anchor_x, anchor_y, target_x, target_y = PLACEMENT
	return target_x + (x - anchor_x) * scale, target_y + (y - anchor_y) * scale


def scale_length(length):
	return length * PLACEMENT[0]


def polygon_points(points):
	"""Design points as supersampled pixel coordinates."""
	pixels = []
	for x, y in points:
		image_x, image_y = point_transform(x, y)
		pixels.append((image_x * SUPERSAMPLE, image_y * SUPERSAMPLE))
	return pixels


class Layer:
	"""A supersampled RGBA canvas."""

	def __init__(self):
		self.image = Image.new("RGBA", (HIRES, HIRES), (0, 0, 0, 0))
		self.draw = ImageDraw.Draw(self.image)


def circle_box(centre_x, centre_y, radius):
	"""The supersampled bounding box of a circle given in image units."""
	return [
		(centre_x - radius) * SUPERSAMPLE,
		(centre_y - radius) * SUPERSAMPLE,
		(centre_x + radius) * SUPERSAMPLE,
		(centre_y + radius) * SUPERSAMPLE,
	]


def mask_from_shapes(shapes):
	"""Draw shapes into one supersampled 8-bit mask. A shape is a polygon (a list of points), ("circle", x, y, radius), ("ring", x, y,
	radius, stroke_width), ("line", points, stroke_width) with round caps, or ("rrect", left, top, right, bottom, corner_radius)."""
	mask = Image.new("L", (HIRES, HIRES), 0)
	draw = ImageDraw.Draw(mask)
	for shape in shapes:
		if shape[0] == "circle":
			_, centre_x, centre_y, radius = shape
			(centre_x, centre_y), radius = point_transform(centre_x, centre_y), scale_length(radius)
			draw.ellipse(circle_box(centre_x, centre_y, radius), fill=255)
		elif shape[0] == "ring":
			_, centre_x, centre_y, radius, stroke_width = shape
			(centre_x, centre_y), radius, stroke_width = point_transform(centre_x, centre_y), scale_length(radius), scale_length(stroke_width)
			draw.ellipse(circle_box(centre_x, centre_y, radius), outline=255, width=int(stroke_width * SUPERSAMPLE))
		elif shape[0] == "line":
			_, points, stroke_width = shape
			stroke_width = scale_length(stroke_width)
			draw.line(polygon_points(points), fill=255, width=int(stroke_width * SUPERSAMPLE), joint="curve")
			for x, y in (point_transform(*points[0]), point_transform(*points[-1])):
				draw.ellipse(circle_box(x, y, stroke_width / 2), fill=255)
		elif shape[0] == "rrect":
			_, left, top, right, bottom, corner_radius = shape
			(left, top), (right, bottom), corner_radius = point_transform(left, top), point_transform(right, bottom), scale_length(corner_radius)
			draw.rounded_rectangle([left * SUPERSAMPLE, top * SUPERSAMPLE, right * SUPERSAMPLE, bottom * SUPERSAMPLE], radius=corner_radius * SUPERSAMPLE, fill=255)
		else:
			draw.polygon(polygon_points(shape), fill=255)
	return mask


def grow_mask(mask, pixels):
	"""Dilate a supersampled mask by pixels output pixels."""
	kernel_size = int(pixels * SUPERSAMPLE) * 2 + 1
	return mask.filter(ImageFilter.MaxFilter(kernel_size if kernel_size % 2 else kernel_size + 1))


def shrink_mask(mask, pixels):
	"""Erode a supersampled mask by pixels output pixels."""
	kernel_size = int(pixels * SUPERSAMPLE) * 2 + 1
	return mask.filter(ImageFilter.MinFilter(kernel_size if kernel_size % 2 else kernel_size + 1))


def compose(body, rim=GOLD, fill=NAVY, highlight=True, extra=None, halo_cut=None):
	"""Body mask -> halo (dark, faint, about 1 px), rim (gold, 1 px), fill (navy) and a light highlight along the upper-left inside edge."""
	canvas = np.zeros((HIRES, HIRES, 4), dtype=float)

	def blend_layer(mask, colour, opacity=1.0):
		alpha = np.asarray(mask, dtype=float) / 255.0 * opacity
		for channel in range(3):
			canvas[..., channel] = canvas[..., channel] * (1 - alpha) + colour[channel] * alpha
		canvas[..., 3] = canvas[..., 3] * (1 - alpha) + alpha

	halo = grow_mask(body, 1.5).filter(ImageFilter.GaussianBlur(SUPERSAMPLE * 0.4))
	if halo_cut is not None:  # keep the halo outside a closed shape (the inside of a ring stays clear)
		halo = Image.fromarray((np.asarray(halo, dtype=float) * (1 - np.asarray(halo_cut, dtype=float) / 255)).astype(np.uint8))
	blend_layer(halo, INK, 0.35)
	blend_layer(grow_mask(body, 1.0), rim)
	blend_layer(body, fill)
	if highlight:
		# light along the upper-left: the inside edge shifted down-right minus itself
		core = shrink_mask(body, 0.75)
		shift = int(SUPERSAMPLE * 0.9)
		shifted = Image.fromarray(np.roll(np.roll(np.asarray(core), shift, 0), shift, 1))
		highlight_mask = np.clip(np.asarray(core, dtype=int) - np.asarray(shifted, dtype=int), 0, 255).astype(np.uint8)
		blend_layer(Image.fromarray(highlight_mask), NAVY_HI, 0.9)
	if extra:
		for mask, colour in extra:
			blend_layer(mask, colour)
	return canvas


def downsample(supersampled):
	"""Box-filter the supersampled RGBA (straight alpha) down to 32 x 32 with premultiplied averaging."""
	alpha = supersampled[..., 3:4]
	premultiplied = supersampled[..., :3] * alpha
	premultiplied = premultiplied.reshape(CURSOR_SIZE, SUPERSAMPLE, CURSOR_SIZE, SUPERSAMPLE, 3).mean(axis=(1, 3))
	mean_alpha = alpha.reshape(CURSOR_SIZE, SUPERSAMPLE, CURSOR_SIZE, SUPERSAMPLE, 1).mean(axis=(1, 3))
	rgb = np.where(mean_alpha > 1e-6, premultiplied / np.maximum(mean_alpha, 1e-6), 0)
	pixels = np.concatenate([rgb, mean_alpha * 255], axis=2)
	pixels = np.clip(np.round(pixels), 0, 255).astype(np.uint8)
	pixels[pixels[..., 3] < 3] = 0
	return pixels


# ---- shapes ---------------------------------------------------------------------------------------------------------------------------
ARROW = [(2.5, 2.5), (2.5, 22.5), (7.2, 18.2), (10.6, 26.2), (14.0, 24.8), (10.7, 17.0), (17.0, 17.0)]


def arrow_body():
	return mask_from_shapes([ARROW])


def arrow():
	set_placement(0.72, 2.5, 2.5, 2.5, 2.5)  # about 11 x 19, tip and hot spot at (2, 2)
	return compose(arrow_body()), (2, 2)


def help_cursor():
	set_placement(0.62, 18.5, 5.5, 14.5, 3.5)  # a 10 px question mark beside the arrow
	question_mark = mask_from_shapes([("line", [(18.5, 9.0), (19.5, 6.5), (22.5, 5.5), (25.5, 6.5), (26.2, 9.0), (25.0, 11.2), (22.6, 12.6), (22.4, 15.0)], 2.6), ("circle", 22.4, 19.2, 1.6)])
	set_placement(0.72, 2.5, 2.5, 2.5, 2.5)
	return compose(arrow_body(), extra=[(grow_mask(question_mark, 0.8), INK), (question_mark, GOLD)]), (2, 2)


def spinner_masks(centre_x, centre_y, radius, stroke_width, phase):
	"""The ring and the 110 degree arc that travels round it, one mask each; phase counts eighths of a turn."""
	ring = mask_from_shapes([("ring", centre_x, centre_y, radius, stroke_width)])
	arc = Image.new("L", (HIRES, HIRES), 0)
	draw = ImageDraw.Draw(arc)
	start_angle = phase * 45 - 90
	(centre_x, centre_y), radius, stroke_width = point_transform(centre_x, centre_y), scale_length(radius), scale_length(stroke_width)
	draw.arc(circle_box(centre_x, centre_y, radius), start_angle, start_angle + 110, fill=255, width=int(stroke_width * SUPERSAMPLE))
	return ring, arc


def working(phase=0):
	set_placement(1.0, 0, 0, 0, 0)  # a 14 px ring at the arrow's foot
	ring, arc = spinner_masks(17.5, 18.0, 5.2, 2.2, phase)
	disc = mask_from_shapes([("circle", 17.5, 18.0, 6.2)])
	set_placement(0.72, 2.5, 2.5, 2.5, 2.5)
	body = arrow_body()
	return compose(body, extra=[(grow_mask(disc, 0.8), INK), (disc, NAVY), (ring, GOLD), (arc, ROSE)]), (2, 2)


def busy(phase=0):
	# The Quill ring: a gold ring on a navy disc, with a rose arc that travels round it.
	set_placement(0.62, 16, 16, 16, 16)  # 16 px across, hot spot in the middle
	disc = mask_from_shapes([("circle", 16, 16, 11.5)])
	ring, arc = spinner_masks(16, 16, 9.0, 3.6, phase)
	nib = mask_from_shapes([("circle", 16, 16, 2.0)])
	return compose(disc, rim=GOLD_LIGHT, highlight=False, extra=[(ring, GOLD), (arc, ROSE), (nib, CREAM)]), (16, 16)


def crosshair():
	set_placement(0.52, 16, 16, 11.5, 11.5)  # 17 x 17, hot spot (11, 11)
	arms = [("rrect", 14.4, 2, 17.6, 12.5, 1.0), ("rrect", 14.4, 19.5, 17.6, 30, 1.0), ("rrect", 2, 14.4, 12.5, 17.6, 1.0), ("rrect", 19.5, 14.4, 30, 17.6, 1.0)]
	centre_dot = mask_from_shapes([("circle", 16, 16, 1.2)])
	return compose(mask_from_shapes(arms), highlight=False, extra=[(centre_dot, GOLD)]), (11, 11)


def ibeam():
	set_placement(0.62, 16, 16, 6.5, 9.5)  # 7 x 16, hot spot (6, 9)
	shapes = [("rrect", 14.5, 6, 17.5, 26, 0.8), ("rrect", 11, 4.5, 15.6, 6.8, 1.0), ("rrect", 16.4, 4.5, 21, 6.8, 1.0), ("rrect", 11, 25.2, 15.6, 27.5, 1.0), ("rrect", 16.4, 25.2, 21, 27.5, 1.0)]
	return compose(mask_from_shapes(shapes), highlight=False), (6, 9)


def unavailable():
	set_placement(0.75, 16, 16, 12.5, 12.5)  # 20 x 20, hot spot in the middle
	ring = mask_from_shapes([("ring", 16, 16, 11, 3.4)])
	slash = mask_from_shapes([[(8.6, 21.3), (21.3, 8.6), (23.4, 10.7), (10.7, 23.4)]])
	body = Image.fromarray(np.maximum(np.asarray(ring), np.asarray(slash)))
	inner_hole = shrink_mask(mask_from_shapes([("circle", 16, 16, 9.3)]), 0.5)
	return compose(body, rim=INK, fill=ROSE, highlight=False, halo_cut=inner_hole), (12, 12)


def double_arrow(angle):
	"""A two-headed arrow along the x axis, rotated by angle degrees about the centre."""
	points = [(3, 16), (9, 9.5), (9, 14), (23, 14), (23, 9.5), (29, 16), (23, 22.5), (23, 18), (9, 18), (9, 22.5)]
	radians = math.radians(angle)
	set_placement(0.72 if angle % 90 == 0 else 0.62, 16, 16, 15.5, 15.5)  # 21 x 11 straight, 15 x 15 diagonal
	rotated = [(16 + (x - 16) * math.cos(radians) - (y - 16) * math.sin(radians), 16 + (x - 16) * math.sin(radians) + (y - 16) * math.cos(radians)) for x, y in points]
	return compose(mask_from_shapes([rotated]), highlight=False), (15, 15)


def move():
	set_placement(0.78, 16, 16, 15.5, 15.5)  # 23 x 23
	outline = [(3, 16), (8, 11), (8, 14.5), (14.5, 14.5), (14.5, 8), (11, 8), (16, 3), (21, 8), (17.5, 8), (17.5, 14.5), (24, 14.5), (24, 11), (29, 16), (24, 21), (24, 17.5), (17.5, 17.5), (17.5, 24), (21, 24), (16, 29), (11, 24), (14.5, 24), (14.5, 17.5), (8, 17.5), (8, 21)]
	return compose(mask_from_shapes([outline]), highlight=False), (15, 15)


def up_arrow():
	set_placement(0.68, 16, 2, 15.5, 5.0)  # 11 x 19, tip and hot spot at (15, 5)
	points = [(16, 2), (24, 11), (19, 11), (19, 28), (13, 28), (13, 11), (8, 11)]
	return compose(mask_from_shapes([points]), highlight=True), (15, 5)


def hand():
	set_placement(0.62, 12.3, 2.5, 9.5, 2.5)  # about 14 x 19, fingertip and hot spot at (9, 2)
	shapes = [
		("rrect", 10.0, 2.5, 14.6, 20, 2.3),  # index finger
		("rrect", 14.0, 10.0, 18.4, 21, 2.2),
		("rrect", 17.8, 11.0, 22.2, 21, 2.2),
		("rrect", 21.6, 12.5, 25.8, 21, 2.1),
		("rrect", 10.0, 16, 25.8, 26, 4.0),  # palm
		[(10.4, 22.5), (5.5, 16.5), (5.0, 14.8), (6.4, 14.0), (10.6, 17.2)],  # thumb
		("rrect", 11.5, 24, 24.5, 29.5, 1.5),  # wrist
	]
	return compose(mask_from_shapes(shapes)), (9, 2)


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


def cursor_image(pixels):
	"""BITMAPINFOHEADER + 32-bit BGRA rows (bottom-up) + 1-bit AND mask: the image part of a .cur entry and of an RT_CURSOR resource."""
	height, width = pixels.shape[:2]
	header = struct.pack("<IiiHHIIiiII", 40, width, height * 2, 1, 32, 0, width * height * 4 + height * ((width + 31) // 32) * 4, 0, 0, 0, 0)
	colour_rows = b"".join(pixels[y, :, [2, 1, 0, 3]].T.astype(np.uint8).tobytes() for y in range(height - 1, -1, -1))
	mask_rows = []
	for y in range(height - 1, -1, -1):
		bits = 0
		for x in range(width):
			if pixels[y, x, 3] == 0:
				bits |= 1 << (31 - x)
		mask_rows.append(struct.pack(">I", bits))
	return header + colour_rows + b"".join(mask_rows)


def cur_file(pixels, hotspot):
	data = cursor_image(pixels)
	return struct.pack("<HHH", 0, 2, 1) + struct.pack("<BBBBHHII", 32, 32, 0, 0, hotspot[0], hotspot[1], len(data), 22) + data


def ani_file(frames, hotspot, rate):
	"""An animated cursor: a RIFF ACON with one .cur per frame; rate is in jiffies (1/60 s) per frame."""
	frame_chunks = b"".join(
		b"icon" + struct.pack("<I", len(cur)) + cur + (b"\0" if len(cur) & 1 else b"") for cur in (cur_file(frame, hotspot) for frame in frames)
	)
	header = struct.pack("<9I", 36, len(frames), len(frames), 32, 32, 32, 1, rate, 1)
	body = b"ACON" + b"anih" + struct.pack("<I", 36) + header + b"LIST" + struct.pack("<I", 4 + len(frame_chunks)) + b"fram" + frame_chunks
	return b"RIFF" + struct.pack("<I", len(body)) + body


def main():
	out_dir = sys.argv[1]
	sheet_path = sys.argv[3] if len(sys.argv) > 3 and sys.argv[2] == "--sheet" else None
	os.makedirs(out_dir, exist_ok=True)
	images = {}
	for name, (draw_cursor, _) in CURSORS.items():
		supersampled, hotspot = draw_cursor()
		pixels = downsample(supersampled)
		images[name] = (pixels, hotspot)
		with open(os.path.join(out_dir, f"afterglow-{name}.cur"), "wb") as cur_out:
			cur_out.write(cur_file(pixels, hotspot))
	for name, draw_cursor in (("working", working), ("busy", busy)):
		frames = []
		for frame_index in range(8):
			supersampled, hotspot = draw_cursor(frame_index)
			frames.append(downsample(supersampled))
		with open(os.path.join(out_dir, f"afterglow-{name}.ani"), "wb") as ani_out:
			ani_out.write(ani_file(frames, hotspot, 6))
	if sheet_path:
		backgrounds = [(9, 14, 42), (255, 255, 255), (212, 208, 200)]
		zoom = 4
		cell = CURSOR_SIZE * zoom + 12
		sheet = Image.new("RGB", (cell * len(images), cell * len(backgrounds)), (60, 60, 60))
		for row, background in enumerate(backgrounds):
			for column, (name, (pixels, hotspot)) in enumerate(images.items()):
				tile = Image.new("RGB", (CURSOR_SIZE, CURSOR_SIZE), background)
				tile.paste(Image.fromarray(pixels, "RGBA"), (0, 0), Image.fromarray(pixels, "RGBA"))
				enlarged = tile.resize((CURSOR_SIZE * zoom, CURSOR_SIZE * zoom), Image.NEAREST)
				draw = ImageDraw.Draw(enlarged)
				hotspot_x, hotspot_y = hotspot[0] * zoom + zoom // 2, hotspot[1] * zoom + zoom // 2
				draw.line([hotspot_x - 3, hotspot_y, hotspot_x + 3, hotspot_y], fill=(0, 200, 0))
				draw.line([hotspot_x, hotspot_y - 3, hotspot_x, hotspot_y + 3], fill=(0, 200, 0))
				sheet.paste(enlarged, (column * cell + 6, row * cell + 6))
		sheet.save(sheet_path)


if __name__ == "__main__":
	main()
