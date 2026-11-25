#!/usr/bin/env python3
# Draw the Afterglow pointer set procedurally and write it as 32 x 32 ARGB .cur files (and .ani for the two busy pointers):
# a navy body with a soft gold rim, a light highlight and a faint dark halo, so each pointer reads on the dark desktop and on a
# white page. Each one has the footprint and hot spot of the standard ReactOS pointer it replaces. Every shape is defined here as polygons, circles and strokes; nothing is traced from another pointer set.
# Usage: gen-cursors.py OUT_DIR [--sheet PNG] [--svg SVG_DIR]
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
	radius, stroke_width), ("arc", x, y, radius, stroke_width, start_degrees, end_degrees), ("line", points, stroke_width) with round caps, or ("rrect", left, top, right, bottom, corner_radius)."""
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
		elif shape[0] == "arc":
			_, centre_x, centre_y, radius, stroke_width, start_angle, end_angle = shape
			(centre_x, centre_y), radius, stroke_width = point_transform(centre_x, centre_y), scale_length(radius), scale_length(stroke_width)
			draw.arc(circle_box(centre_x, centre_y, radius), start_angle, end_angle, fill=255, width=int(stroke_width * SUPERSAMPLE))
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
# Each pointer is a spec: the body shapes with their placement, the colours, and the extra layers drawn over the body. The raster path
# (draw) and the SVG path (svg_document) both read the same spec, so the two never disagree about a shape. A layer is a dict with
# "placement" (as for set_placement), "shapes" (as for mask_from_shapes), "colour", and optionally "grow" (dilate by that many pixels
# before painting, or erode if negative) and "spin" (the layer turns round the ring in the animated SVG).
IDENTITY = (1.0, 0, 0, 0, 0)
ARROW_PLACEMENT = (0.72, 2.5, 2.5, 2.5, 2.5)
ARROW = [(2.5, 2.5), (2.5, 22.5), (7.2, 18.2), (10.6, 26.2), (14.0, 24.8), (10.7, 17.0), (17.0, 17.0)]
SPINNER_ARC_DEGREES = 110


def layer(placement, shapes, colour=None, grow=0, spin=False):
	return {"placement": placement, "shapes": shapes, "colour": colour, "grow": grow, "spin": spin}


def spec(body_placement, body_shapes, hotspot, rim=GOLD, fill=NAVY, highlight=True, extras=(), halo_cut=None):
	return {"body": layer(body_placement, body_shapes), "hotspot": hotspot, "rim": rim, "fill": fill, "highlight": highlight, "extras": list(extras), "halo_cut": halo_cut}


def layer_mask(item):
	set_placement(*item["placement"])
	mask = mask_from_shapes(item["shapes"])
	if item["grow"] > 0:
		mask = grow_mask(mask, item["grow"])
	elif item["grow"] < 0:
		mask = shrink_mask(mask, -item["grow"])
	return mask


def draw(pointer):
	"""A spec as a supersampled RGBA canvas and its hot spot."""
	extras = [(layer_mask(item), item["colour"]) for item in pointer["extras"]]
	halo_cut = layer_mask(pointer["halo_cut"]) if pointer["halo_cut"] else None
	body = layer_mask(pointer["body"])
	return compose(body, rim=pointer["rim"], fill=pointer["fill"], highlight=pointer["highlight"], extra=extras, halo_cut=halo_cut), pointer["hotspot"]


def spinner(centre_x, centre_y, radius, stroke_width, phase, placement):
	"""The ring and the 110 degree arc that travels round it; phase counts eighths of a turn."""
	start_angle = phase * 45 - 90
	return layer(placement, [("ring", centre_x, centre_y, radius, stroke_width)], GOLD), layer(placement, [("arc", centre_x, centre_y, radius, stroke_width, start_angle, start_angle + SPINNER_ARC_DEGREES)], ROSE, spin=True)


def arrow_spec():
	return spec(ARROW_PLACEMENT, [ARROW], (2, 2))  # about 11 x 19, tip and hot spot at (2, 2)


def help_spec():
	question_mark = [("line", [(18.5, 9.0), (19.5, 6.5), (22.5, 5.5), (25.5, 6.5), (26.2, 9.0), (25.0, 11.2), (22.6, 12.6), (22.4, 15.0)], 2.6), ("circle", 22.4, 19.2, 1.6)]
	placement = (0.62, 18.5, 5.5, 14.5, 3.5)  # a 10 px question mark beside the arrow
	return spec(ARROW_PLACEMENT, [ARROW], (2, 2), extras=[layer(placement, question_mark, INK, grow=0.8), layer(placement, question_mark, GOLD)])


def working_spec(phase=0):
	ring, arc = spinner(17.5, 18.0, 5.2, 2.2, phase, IDENTITY)  # a 14 px ring at the arrow's foot
	disc = [("circle", 17.5, 18.0, 6.2)]
	return spec(ARROW_PLACEMENT, [ARROW], (2, 2), extras=[layer(IDENTITY, disc, INK, grow=0.8), layer(IDENTITY, disc, NAVY), ring, arc])


def busy_spec(phase=0):
	# The Quill ring: a gold ring on a navy disc, with a rose arc that travels round it.
	placement = (0.62, 16, 16, 16, 16)  # 16 px across, hot spot in the middle
	ring, arc = spinner(16, 16, 9.0, 3.6, phase, placement)
	nib = layer(placement, [("circle", 16, 16, 2.0)], CREAM)
	return spec(placement, [("circle", 16, 16, 11.5)], (16, 16), rim=GOLD_LIGHT, highlight=False, extras=[ring, arc, nib])


def crosshair_spec():
	placement = (0.52, 16, 16, 11.5, 11.5)  # 17 x 17, hot spot (11, 11)
	arms = [("rrect", 14.4, 2, 17.6, 12.5, 1.0), ("rrect", 14.4, 19.5, 17.6, 30, 1.0), ("rrect", 2, 14.4, 12.5, 17.6, 1.0), ("rrect", 19.5, 14.4, 30, 17.6, 1.0)]
	return spec(placement, arms, (11, 11), highlight=False, extras=[layer(placement, [("circle", 16, 16, 1.2)], GOLD)])


def ibeam_spec():
	placement = (0.62, 16, 16, 6.5, 9.5)  # 7 x 16, hot spot (6, 9)
	shapes = [("rrect", 14.5, 6, 17.5, 26, 0.8), ("rrect", 11, 4.5, 15.6, 6.8, 1.0), ("rrect", 16.4, 4.5, 21, 6.8, 1.0), ("rrect", 11, 25.2, 15.6, 27.5, 1.0), ("rrect", 16.4, 25.2, 21, 27.5, 1.0)]
	return spec(placement, shapes, (6, 9), highlight=False)


def unavailable_spec():
	placement = (0.75, 16, 16, 12.5, 12.5)  # 20 x 20, hot spot in the middle
	body = [("ring", 16, 16, 11, 3.4), [(8.6, 21.3), (21.3, 8.6), (23.4, 10.7), (10.7, 23.4)]]  # the ring and the slash
	return spec(placement, body, (12, 12), rim=INK, fill=ROSE, highlight=False, halo_cut=layer(placement, [("circle", 16, 16, 9.3)], grow=-0.5))


def double_arrow_spec(angle):
	"""A two-headed arrow along the x axis, rotated by angle degrees about the centre."""
	points = [(3, 16), (9, 9.5), (9, 14), (23, 14), (23, 9.5), (29, 16), (23, 22.5), (23, 18), (9, 18), (9, 22.5)]
	radians = math.radians(angle)
	placement = (0.72 if angle % 90 == 0 else 0.62, 16, 16, 15.5, 15.5)  # 21 x 11 straight, 15 x 15 diagonal
	rotated = [(16 + (x - 16) * math.cos(radians) - (y - 16) * math.sin(radians), 16 + (x - 16) * math.sin(radians) + (y - 16) * math.cos(radians)) for x, y in points]
	return spec(placement, [rotated], (15, 15), highlight=False)


def move_spec():
	placement = (0.78, 16, 16, 15.5, 15.5)  # 23 x 23
	outline = [(3, 16), (8, 11), (8, 14.5), (14.5, 14.5), (14.5, 8), (11, 8), (16, 3), (21, 8), (17.5, 8), (17.5, 14.5), (24, 14.5), (24, 11), (29, 16), (24, 21), (24, 17.5), (17.5, 17.5), (17.5, 24), (21, 24), (16, 29), (11, 24), (14.5, 24), (14.5, 17.5), (8, 17.5), (8, 21)]
	return spec(placement, [outline], (15, 15), highlight=False)


def up_arrow_spec():
	placement = (0.68, 16, 2, 15.5, 5.0)  # 11 x 19, tip and hot spot at (15, 5)
	points = [(16, 2), (24, 11), (19, 11), (19, 28), (13, 28), (13, 11), (8, 11)]
	return spec(placement, [points], (15, 5))


def hand_spec():
	placement = (0.62, 12.3, 2.5, 9.5, 2.5)  # about 14 x 19, fingertip and hot spot at (9, 2)
	shapes = [
		("rrect", 10.0, 2.5, 14.6, 20, 2.3),  # index finger
		("rrect", 14.0, 10.0, 18.4, 21, 2.2),
		("rrect", 17.8, 11.0, 22.2, 21, 2.2),
		("rrect", 21.6, 12.5, 25.8, 21, 2.1),
		("rrect", 10.0, 16, 25.8, 26, 4.0),  # palm
		[(10.4, 22.5), (5.5, 16.5), (5.0, 14.8), (6.4, 14.0), (10.6, 17.2)],  # thumb
		("rrect", 11.5, 24, 24.5, 29.5, 1.5),  # wrist
	]
	return spec(placement, shapes, (9, 2))


def drawn(spec_function):
	return lambda *phase: draw(spec_function(*phase))


working = drawn(working_spec)
busy = drawn(busy_spec)

# name: (spec function, ReactOS cursor name); the animated pointers take a phase (eighths of a turn)
SPECS = {
	"arrow": (arrow_spec, "Arrow"),
	"help": (help_spec, "Help"),
	"working": (working_spec, "AppStarting"),
	"busy": (busy_spec, "Wait"),
	"cross": (crosshair_spec, "Crosshair"),
	"ibeam": (ibeam_spec, "IBeam"),
	"no": (unavailable_spec, "No"),
	"size-ns": (lambda: double_arrow_spec(90), "SizeNS"),
	"size-we": (lambda: double_arrow_spec(0), "SizeWE"),
	"size-nwse": (lambda: double_arrow_spec(45), "SizeNWSE"),
	"size-nesw": (lambda: double_arrow_spec(-45), "SizeNESW"),
	"move": (move_spec, "SizeAll"),
	"up": (up_arrow_spec, "UpArrow"),
	"hand": (hand_spec, "Hand"),
}
CURSORS = {name: (drawn(spec_function), cursor_name) for name, (spec_function, cursor_name) in SPECS.items()}
ANIMATED = {"working": working_spec, "busy": busy_spec}


# ---- SVG masters ----------------------------------------------------------------------------------------------------------------------
# The same specs as scalable art in the pointer's own 32 x 32 pixel grid. These are idealised: the rim, halo and highlight are
# expressed with strokes and translucent layers, not the morphological filters and box reduction the raster uses, so they are close to
# the .cur images but not pixel-identical. The shipped files stay the raster output.
HALO_LAYERS = ((1.75, 0.12), (1.4, 0.12), (1.1, 0.12))  # (pixels beyond the edge, opacity): a stepped stand-in for the blurred halo
HIGHLIGHT_SHIFT = int(SUPERSAMPLE * 0.9) / SUPERSAMPLE
SVG_FRAME_SECONDS = 0.1  # 6 jiffies per frame, as in the .ani files


def hex_colour(colour):
	return "#{:02x}{:02x}{:02x}".format(*colour)


def number(value):
	text = f"{value:.3f}".rstrip("0").rstrip(".")
	return "0" if text in ("", "-0") else text


def shape_svg(shape, placement, colour, grow=0.0, erode_to=None):
	"""One shape as an SVG element in image units. grow widens it by that many pixels (a stroke of the same colour); erode_to is a
	colour to stroke the outline with, 0.75 px in, to shrink a filled shape."""
	scale, anchor_x, anchor_y, target_x, target_y = placement

	def at(x, y):
		return target_x + (x - anchor_x) * scale, target_y + (y - anchor_y) * scale

	def pair(x, y):
		return f"{number(at(x, y)[0])} {number(at(x, y)[1])}"

	paint = f'fill="{colour}"'
	if grow > 0:
		paint += f' stroke="{colour}" stroke-width="{number(grow * 2)}" stroke-linejoin="round"'
	if erode_to:
		paint += f' stroke="{erode_to}" stroke-width="1.5" stroke-linejoin="round"'
	kind = shape[0] if isinstance(shape[0], str) else "polygon"
	if kind == "polygon":
		return f'<path d="M{"L".join(pair(x, y) for x, y in shape)}Z" {paint}/>'
	if kind == "circle":
		_, centre_x, centre_y, radius = shape
		return f'<circle cx="{number(at(centre_x, centre_y)[0])}" cy="{number(at(centre_x, centre_y)[1])}" r="{number(max(radius * scale + (0 if erode_to else grow), 0))}" {paint if erode_to else f'fill="{colour}"'}/>'
	if kind == "rrect":
		_, left, top, right, bottom, corner = shape
		(left, top), (right, bottom) = at(left, top), at(right, bottom)
		pad = 0 if erode_to else grow
		return f'<rect x="{number(left - pad)}" y="{number(top - pad)}" width="{number(right - left + 2 * pad)}" height="{number(bottom - top + 2 * pad)}" rx="{number(corner * scale + pad)}" {f"fill=\"{colour}\"" if not erode_to else paint}/>'
	# Strokes. PIL draws ring and arc widths inward from the radius, so the centre line sits half a width inside it.
	assert not erode_to, "only filled shapes are eroded"
	if kind == "ring":
		_, centre_x, centre_y, radius, width = shape
		width, radius = width * scale, radius * scale
		return f'<circle cx="{number(at(centre_x, centre_y)[0])}" cy="{number(at(centre_x, centre_y)[1])}" r="{number(radius - width / 2)}" fill="none" stroke="{colour}" stroke-width="{number(width + 2 * grow)}"/>'
	if kind == "arc":
		_, centre_x, centre_y, radius, width, start, end = shape
		width, radius = width * scale, radius * scale
		x0, y0 = at(centre_x, centre_y)
		middle = radius - width / 2
		ends = [(x0 + middle * math.cos(math.radians(angle)), y0 + middle * math.sin(math.radians(angle))) for angle in (start, end)]
		return f'<path d="M{number(ends[0][0])} {number(ends[0][1])}A{number(middle)} {number(middle)} 0 0 1 {number(ends[1][0])} {number(ends[1][1])}" fill="none" stroke="{colour}" stroke-width="{number(width + 2 * grow)}"/>'
	assert kind == "line", kind
	_, points, width = shape
	return f'<polyline points="{" ".join(pair(x, y) for x, y in points)}" fill="none" stroke="{colour}" stroke-width="{number(width * scale + 2 * grow)}" stroke-linecap="round" stroke-linejoin="round"/>'


def shapes_svg(item, colour, grow=0.0, erode_to=None):
	return [shape_svg(shape, item["placement"], colour, grow, erode_to) for shape in item["shapes"]]


def svg_document(name, cursor_name, pointer, animated=False, frame=None):
	"""A pointer spec as an SVG file. animated turns the travelling arc with SMIL; frame (for a still) is only used in the title."""
	body, ink = pointer["body"], hex_colour(INK)
	out = []
	add = lambda line, depth=1: out.append("\t" * depth + line)
	title = f"Afterglow pointer: {cursor_name}" + (f", frame {frame}" if frame is not None else "") + (", animated" if animated else "")
	hotspot_x, hotspot_y = pointer["hotspot"]
	out.append(f"""<!--
	{title}. Idealised vector master of afterglow-{name}.cur, drawn in the pointer's own 32 x 32 pixel grid; the shipped pointer is the raster file.
	Hot spot at ({hotspot_x}, {hotspot_y}). Generated by desktop/pointers/gen-cursors.py from the shapes the raster is drawn from; edit the generator, not this file.

	(c) Copyright 2026 Liminal HQ, Scott Morris
	SPDX-License-Identifier: Apache-2.0 OR MIT
-->""")
	out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CURSOR_SIZE} {CURSOR_SIZE}" width="{CURSOR_SIZE * 8}" height="{CURSOR_SIZE * 8}" role="img" data-hotspot="{hotspot_x},{hotspot_y}">')
	add(f"<title>{title}</title>")
	add(f"<desc>Hot spot at pixel ({hotspot_x}, {hotspot_y}) of the 32 x 32 grid.</desc>")
	masks = []
	if pointer["halo_cut"] or pointer["highlight"]:
		masks.append("<defs>")
		if pointer["halo_cut"]:
			masks.append('\t<mask id="outside-hole" maskUnits="userSpaceOnUse" x="0" y="0" width="32" height="32">')
			masks.append('\t\t<rect width="32" height="32" fill="#fff"/>')
			masks.extend("\t\t" + element for element in shapes_svg(pointer["halo_cut"], "#000", pointer["halo_cut"]["grow"]))
			masks.append("\t</mask>")
		if pointer["highlight"]:
			masks.append('\t<mask id="core" maskUnits="userSpaceOnUse" x="-8" y="-8" width="48" height="48">')
			masks.extend("\t\t" + element for element in shapes_svg(body, "#fff", erode_to="#000"))
			masks.append("\t</mask>")
			masks.append('\t<mask id="upper-left" maskUnits="userSpaceOnUse" x="0" y="0" width="32" height="32">')
			masks.append('\t\t<rect width="32" height="32" fill="#000"/>')
			masks.append('\t\t<g mask="url(#core)"><rect x="-8" y="-8" width="48" height="48" fill="#fff"/></g>')
			masks.append(f'\t\t<g transform="translate({number(HIGHLIGHT_SHIFT)} {number(HIGHLIGHT_SHIFT)})"><g mask="url(#core)"><rect x="-8" y="-8" width="48" height="48" fill="#000"/></g></g>')
			masks.append("\t</mask>")
		masks.append("</defs>")
		out.extend("\t" + line for line in masks)
	cut = ' mask="url(#outside-hole)"' if pointer["halo_cut"] else ""
	add(f'<g id="halo" fill="{ink}"{cut}>')
	for reach, opacity in HALO_LAYERS:
		add(f'<g opacity="{opacity}">', 2)
		out.extend("\t\t\t" + element for element in shapes_svg(body, hex_colour(INK), reach))
		add("</g>", 2)
	add("</g>")
	add(f'<g id="rim">')
	out.extend("\t\t" + element for element in shapes_svg(body, hex_colour(pointer["rim"]), 1.0))
	add("</g>")
	add('<g id="body">')
	out.extend("\t\t" + element for element in shapes_svg(body, hex_colour(pointer["fill"])))
	add("</g>")
	if pointer["highlight"]:
		add(f'<rect id="highlight" width="32" height="32" fill="{hex_colour(NAVY_HI)}" opacity="0.9" mask="url(#upper-left)"/>')
	for index, item in enumerate(pointer["extras"]):
		elements = shapes_svg(item, hex_colour(item["colour"]), item["grow"])
		if animated and item["spin"]:
			centre = point_through(item["placement"], *item["shapes"][0][1:3])
			turns = ";".join(f"{step * 45} {number(centre[0])} {number(centre[1])}" for step in range(8))
			add('<g id="travelling-arc">')
			out.extend("\t\t" + element for element in elements)
			add(f'\t<animateTransform attributeName="transform" type="rotate" values="{turns}" dur="{number(8 * SVG_FRAME_SECONDS)}s" calcMode="discrete" repeatCount="indefinite"/>')
			add("</g>")
		else:
			out.extend("\t" + element for element in elements)
	out.append("</svg>")
	return "\n".join(out) + "\n"


def point_through(placement, x, y):
	scale, anchor_x, anchor_y, target_x, target_y = placement
	return target_x + (x - anchor_x) * scale, target_y + (y - anchor_y) * scale


def svg_files():
	"""The SVG masters as {relative path: text}: one per pointer, an animated one for each busy pointer, and the 8 frames of those."""
	files = {}
	for name, (spec_function, cursor_name) in SPECS.items():
		files[f"afterglow-{name}.svg"] = svg_document(name, cursor_name, spec_function())
	for name, spec_function in ANIMATED.items():
		cursor_name = SPECS[name][1]
		files[f"afterglow-{name}-animated.svg"] = svg_document(name, cursor_name, spec_function(0), animated=True)
		for frame in range(8):
			files[f"frames/afterglow-{name}-{frame}.svg"] = svg_document(name, cursor_name, spec_function(frame), frame=frame)
	return files


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
	options = sys.argv[2:]
	sheet_path = options[options.index("--sheet") + 1] if "--sheet" in options else None
	svg_dir = options[options.index("--svg") + 1] if "--svg" in options else None
	if svg_dir:
		for relative, text in svg_files().items():
			os.makedirs(os.path.dirname(os.path.join(svg_dir, relative)), exist_ok=True)
			with open(os.path.join(svg_dir, relative), "w") as svg_out:
				svg_out.write(text)
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
