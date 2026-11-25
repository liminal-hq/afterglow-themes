#!/usr/bin/env python3
# Render a preview sheet of the Afterglow pointers for the README: every pointer enlarged 4x with nearest-neighbour on the dark
# desktop colour and on cream, then a row at true size on each. The two animated pointers also show a second frame. The pointers
# come from gen-cursors.py, so the sheet is always the set that file draws. The PNG has no text and no metadata, so its pixels
# are the same on every machine (check-desktop.sh compares pixels, not file bytes, since PNG encoders differ).
# Usage: render-preview.py OUT_PNG
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
import importlib.util
import os
import sys

from PIL import Image

DARK_BACKGROUND = (5, 5, 7)  # #050507
CREAM_BACKGROUND = (255, 244, 214)
ZOOM = 4
COLUMNS = 8
SECOND_FRAME = 3  # the animated pointers' second frame, a quarter turn on from the first
PADDING = 8


def load_generator():
	"""gen-cursors.py has a hyphen in its name, so it is loaded by path."""
	path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen-cursors.py")
	spec = importlib.util.spec_from_file_location("gen_cursors", path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


def draw_pointers(generator):
	"""Each pointer as 32 x 32 RGBA pixels, in the order of CURSORS, followed by the second frame of each animated pointer."""
	pointers = [generator.downsample(draw_cursor()[0]) for draw_cursor, _ in generator.CURSORS.values()]
	pointers.append(generator.downsample(generator.working(SECOND_FRAME)[0]))
	pointers.append(generator.downsample(generator.busy(SECOND_FRAME)[0]))
	return pointers


def paste_pointer(sheet, pointer, left, top, background, zoom):
	tile = Image.new("RGB", (32, 32), background)
	image = Image.fromarray(pointer, "RGBA")
	tile.paste(image, (0, 0), image)
	if zoom > 1:
		tile = tile.resize((32 * zoom, 32 * zoom), Image.NEAREST)
	sheet.paste(tile, (left, top))


def render_sheet(pointers):
	cell = 32 * ZOOM + PADDING
	rows_per_background = -(-len(pointers) // COLUMNS)
	true_size_cell = 32 + PADDING
	width = max(COLUMNS * cell, len(pointers) * true_size_cell) + PADDING
	enlarged_height = rows_per_background * cell
	height = PADDING + 2 * enlarged_height + 2 * true_size_cell
	sheet = Image.new("RGB", (width, height), DARK_BACKGROUND)
	top = PADDING
	for background in (DARK_BACKGROUND, CREAM_BACKGROUND):
		band_height = enlarged_height
		sheet.paste(Image.new("RGB", (width, band_height), background), (0, top - PADDING // 2))
		for index, pointer in enumerate(pointers):
			row, column = divmod(index, COLUMNS)
			paste_pointer(sheet, pointer, PADDING + column * cell, top + row * cell, background, ZOOM)
		top += band_height
	for background in (DARK_BACKGROUND, CREAM_BACKGROUND):
		sheet.paste(Image.new("RGB", (width, true_size_cell), background), (0, top - PADDING // 2))
		for index, pointer in enumerate(pointers):
			paste_pointer(sheet, pointer, PADDING + index * true_size_cell, top, background, 1)
		top += true_size_cell
	return sheet


def main():
	if len(sys.argv) != 2:
		print("usage: render-preview.py OUT_PNG", file=sys.stderr)
		sys.exit(2)
	sheet = render_sheet(draw_pointers(load_generator()))
	sheet.save(sys.argv[1], optimize=True)


if __name__ == "__main__":
	main()
