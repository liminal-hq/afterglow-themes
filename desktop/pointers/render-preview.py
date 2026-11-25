#!/usr/bin/env python3
# Render the Afterglow pointer previews for the READMEs, with nearest-neighbour scaling by whole numbers only, so every pixel of the
# 32 x 32 art is an exact 8 x 8 block: a dark sheet and a cream sheet (each narrow enough that GitHub shows it at full size), a
# small true-size image, and one transparent 8x PNG per pointer, plus a frame strip for each animated pointer. The pointers come from
# gen-cursors.py, so the images are always the set that file draws. Alpha is composited as straight alpha (the art is stored that way),
# so the cream sheet shows the pointers' own faint dark halo and nothing else. The PNGs have no text and no metadata, so their pixels
# are the same on every machine (check-desktop.sh compares pixels, not file bytes, since PNG encoders differ).
# Usage: render-preview.py OUT_DIR   (writes pointers-dark.png, pointers-cream.png, pointers-true-size.png and pointers/NAME.png)
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
import importlib.util
import os
import sys

import numpy as np
from PIL import Image

DARK_BACKGROUND = (5, 5, 7)  # #050507
CREAM_BACKGROUND = (255, 244, 214)
ZOOM = 8
COLUMNS = 3  # 3 x (28 x 8 + 2 x 8) + 8 = 736 px wide, under the width GitHub shows at full size
PADDING = 16
SECOND_FRAME = 3  # the animated pointers' second frame, a quarter turn on from the first
FRAMES = 8  # the frames of each animated pointer, as gen-cursors.py writes them
VISIBLE = 28  # every pointer fits in the top left 28 x 28 pixels of its 32 x 32 image
TRUE_SIZE_PADDING = 8

# File names, in the order of gen-cursors.py CURSORS, then the two second frames.
NAMES = ["arrow", "help", "working", "busy", "crosshair", "text", "unavailable", "resize-vertical", "resize-horizontal", "resize-diagonal-down", "resize-diagonal-up", "move", "up-arrow", "hand"]
SHEET_NAMES = NAMES + ["working-frame-2", "busy-frame-2"]


def load_generator():
	"""gen-cursors.py has a hyphen in its name, so it is loaded by path."""
	path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen-cursors.py")
	spec = importlib.util.spec_from_file_location("gen_cursors", path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


def draw_pointers(generator):
	"""Each pointer as 32 x 32 RGBA pixels, in the order of NAMES, followed by the second frame of each animated pointer."""
	assert len(NAMES) == len(generator.CURSORS)
	pointers = [generator.downsample(draw_cursor()[0]) for draw_cursor, _ in generator.CURSORS.values()]
	pointers.append(generator.downsample(generator.working(SECOND_FRAME)[0]))
	pointers.append(generator.downsample(generator.busy(SECOND_FRAME)[0]))
	return pointers


def animation_frames(generator, draw_cursor):
	return [generator.downsample(draw_cursor(index)[0]) for index in range(FRAMES)]


def enlarge(image, zoom):
	"""Whole-number nearest-neighbour scaling: no resampling, so edges stay hard."""
	return image.resize((image.width * zoom, image.height * zoom), Image.NEAREST)


def pointer_image(pointer):
	return Image.fromarray(pointer, "RGBA")


def paste_pointer(sheet, pointer, left, top, zoom):
	"""Straight-alpha composite onto what is already in the sheet, then the enlargement of the whole tile."""
	image = pointer_image(pointer)
	if zoom > 1:
		image = enlarge(image, zoom)
	sheet.paste(image, (left, top), image)


def render_sheet(pointers, background):
	cell = VISIBLE * ZOOM + PADDING
	rows = -(-len(pointers) // COLUMNS)
	sheet = Image.new("RGB", (COLUMNS * cell + PADDING, rows * cell + PADDING), background)
	for index, pointer in enumerate(pointers):
		row, column = divmod(index, COLUMNS)
		cropped = pointer[:VISIBLE, :VISIBLE]
		paste_pointer(sheet, cropped, PADDING + column * cell, PADDING + row * cell, ZOOM)
	return sheet


def render_true_size(pointers):
	cell = 32 + TRUE_SIZE_PADDING
	width = len(pointers) * cell + TRUE_SIZE_PADDING
	sheet = Image.new("RGB", (width, 2 * cell), DARK_BACKGROUND)
	for row, background in enumerate((DARK_BACKGROUND, CREAM_BACKGROUND)):
		sheet.paste(Image.new("RGB", (width, cell), background), (0, row * cell))
		for index, pointer in enumerate(pointers):
			paste_pointer(sheet, pointer, TRUE_SIZE_PADDING + index * cell, row * cell + TRUE_SIZE_PADDING // 2, 1)
	return sheet


def render_strip(frames):
	"""Frames side by side at 8x on a transparent background, so the whole turn can be inspected."""
	strip = Image.new("RGBA", (len(frames) * 32 * ZOOM, 32 * ZOOM), (0, 0, 0, 0))
	for index, frame in enumerate(frames):
		strip.paste(enlarge(pointer_image(frame), ZOOM), (index * 32 * ZOOM, 0))
	return strip


def save_png(image, path):
	"""A deterministic, lossless, small PNG: palette mode when the image has 256 colours or fewer, whatever its alpha."""
	array = np.asarray(image.convert("RGBA"))
	flat = array.reshape(-1, 4)
	colours, inverse = np.unique(flat, axis=0, return_inverse=True)
	opaque = image.mode == "RGB"
	if len(colours) <= 256:
		palette_image = Image.fromarray(inverse.reshape(array.shape[:2]).astype(np.uint8), "P")
		palette_image.putpalette([int(value) for colour in colours for value in colour[:3]])
		if not opaque:
			palette_image.info["transparency"] = bytes(int(colour[3]) for colour in colours)
		image = palette_image
	image.save(path, optimize=True, compress_level=9)


def render_all(generator):
	"""Every image as {relative path: PIL image}."""
	pointers = draw_pointers(generator)
	images = {
		"pointers-dark.png": render_sheet(pointers, DARK_BACKGROUND),
		"pointers-cream.png": render_sheet(pointers, CREAM_BACKGROUND),
		"pointers-true-size.png": render_true_size(pointers),
	}
	for name, pointer in zip(SHEET_NAMES, pointers):
		if name.endswith("-frame-2"):
			continue
		images[f"pointers/{name}.png"] = enlarge(pointer_image(pointer), ZOOM)
	images["pointers/working-frames.png"] = render_strip(animation_frames(generator, generator.working))
	images["pointers/busy-frames.png"] = render_strip(animation_frames(generator, generator.busy))
	return images


def main():
	if len(sys.argv) != 2:
		print("usage: render-preview.py OUT_DIR", file=sys.stderr)
		sys.exit(2)
	out_dir = sys.argv[1]
	os.makedirs(os.path.join(out_dir, "pointers"), exist_ok=True)
	for relative, image in render_all(load_generator()).items():
		save_png(image, os.path.join(out_dir, relative))


if __name__ == "__main__":
	main()
