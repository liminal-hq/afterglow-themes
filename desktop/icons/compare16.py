#!/usr/bin/env python3
# Draw before-and-after sheets of the hand-tuned 16 px frames at 8x: the scripted downscale of svg/16/ID.svg beside the hand-tuned
# svg/ID-16.svg, each on the Dusk desktop colour and on the classic cream window colour, enlarged with nearest-neighbour sampling.
# Usage: compare16.py OUT_PNG [ID ...]   (no ids: every icon whose hand-tuned frame is in hint16_v2.py)
#
# Needs rsvg-convert and Pillow. The text is Pillow's bundled font.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
import importlib.util
import io
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
SVG = os.path.join(HERE, "svg")
SCALE, COLUMNS = 8, 6
GROUNDS = ((9, 14, 42), (212, 208, 200))
BACKGROUND, INK, HEADING = (12, 12, 16), (180, 191, 206), (255, 208, 142)


def hand_tuned_ids():
	spec = importlib.util.spec_from_file_location("hint16_v2", os.path.join(HERE, "hint16_v2.py"))
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return list(module.ART)


def render(path):
	data = subprocess.run(["rsvg-convert", "--format", "png", "--width", "16", "--height", "16", path], check=True, stdout=subprocess.PIPE).stdout
	return Image.open(io.BytesIO(data)).convert("RGBA")


def enlarged(frame, ground):
	tile = Image.new("RGBA", (16, 16), ground + (255,))
	tile.alpha_composite(frame)
	return tile.resize((16 * SCALE, 16 * SCALE), Image.NEAREST)


def main():
	if len(sys.argv) < 2:
		sys.exit("usage: compare16.py OUT_PNG [ID ...]")
	out_path, ids = sys.argv[1], sys.argv[2:] or hand_tuned_ids()
	side = 16 * SCALE
	cell_width, cell_height = 4 * side + 3 * 4 + 24, side + 24
	rows = (len(ids) + COLUMNS - 1) // COLUMNS
	sheet = Image.new("RGBA", (24 + COLUMNS * cell_width, 56 + rows * cell_height), BACKGROUND + (255,))
	draw = ImageDraw.Draw(sheet)
	font, small_font = ImageFont.load_default(size=18), ImageFont.load_default(size=12)
	draw.text((24, 16), "Hand-tuned 16 px frames at 8x · in each cell: before and after on the Dusk desktop, then before and after on cream", font=font,
		fill=HEADING)
	for index, icon_id in enumerate(ids):
		before, after = render(os.path.join(SVG, "16", icon_id + ".svg")), render(os.path.join(SVG, icon_id + "-16.svg"))
		x = 24 + (index % COLUMNS) * cell_width
		y = 56 + (index // COLUMNS) * cell_height
		for position, (frame, ground) in enumerate(((before, GROUNDS[0]), (after, GROUNDS[0]), (before, GROUNDS[1]), (after, GROUNDS[1]))):
			sheet.alpha_composite(enlarged(frame, ground), (x + position * (side + 4), y))
		draw.text((x, y + side + 4), icon_id, font=small_font, fill=INK)
	sheet.convert("RGB").save(out_path, optimize=True)
	print("before and after", len(ids), "icons", sheet.width, "x", sheet.height)


if __name__ == "__main__":
	main()
