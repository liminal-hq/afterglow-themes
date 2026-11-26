#!/usr/bin/env python3
# Draw the contact sheet of the whole Afterglow system icon set from render.py's PNGs: every icon at 48, 32 and 16 px at true size and its
# 16 px frame at 4x, on the Dusk desktop colour and on the classic cream window colour, grouped as the icon sheet groups them.
# Usage: contact.py RENDER_DIR OUT_PNG
#
# RENDER_DIR is the output of render.py (its png/ folder). The 4x frame is enlarged with nearest-neighbour sampling, so every pixel of the
# 16 px frame shows as a 4 x 4 block. The text is Pillow's bundled font. Needs Pillow.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
import importlib.util
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
GROUNDS = (("Dusk desktop", (9, 14, 42), (180, 191, 206)), ("Classic cream window", (212, 208, 200), (60, 56, 72)))
SHEET_BACKGROUND, HEADING = (12, 12, 16), (255, 208, 142)
COLUMNS, CELL_WIDTH, CELL_HEIGHT, PADDING = 8, 208, 84, 24


def load_groups():
	"""The sheet groups of gen_e.py, each icon listed once (the first group that lists it)."""
	spec = importlib.util.spec_from_file_location("gen_e", os.path.join(HERE, "gen_e.py"))
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	seen, groups = set(), []
	for name, items in module.GROUPS:
		fresh = [(icon_id, label) for icon_id, label in items if icon_id not in seen]
		seen.update(icon_id for icon_id, _ in fresh)
		if fresh:
			groups.append((name, fresh))
	return groups


def frame(render_dir, icon_id, size):
	return Image.open(os.path.join(render_dir, "png", "%s-%d.png" % (icon_id, size))).convert("RGBA")


def panel(render_dir, groups, title, ground, ink, font, small_font):
	rows = sum((len(items) + COLUMNS - 1) // COLUMNS for _, items in groups)
	height = PADDING + 28 + len(groups) * 26 + rows * CELL_HEIGHT + PADDING
	width = PADDING * 2 + COLUMNS * CELL_WIDTH
	image = Image.new("RGBA", (width, height), ground + (255,))
	draw = ImageDraw.Draw(image)
	draw.text((PADDING, PADDING), "%s · 48, 32 and 16 px at 1x, then the 16 px frame at 4x" % title, font=font, fill=ink)
	y = PADDING + 28
	for name, items in groups:
		draw.text((PADDING, y + 4), "%s · %d" % (name, len(items)), font=font, fill=ink)
		y += 26
		for index, (icon_id, label) in enumerate(items):
			x = PADDING + (index % COLUMNS) * CELL_WIDTH
			top = y + (index // COLUMNS) * CELL_HEIGHT
			image.alpha_composite(frame(render_dir, icon_id, 48), (x, top + 8))
			image.alpha_composite(frame(render_dir, icon_id, 32), (x + 54, top + 24))
			image.alpha_composite(frame(render_dir, icon_id, 16), (x + 92, top + 40))
			image.alpha_composite(frame(render_dir, icon_id, 16).resize((64, 64), Image.NEAREST), (x + 116, top))
			draw.text((x, top + 66), label[:30], font=small_font, fill=ink)
		y += (len(items) + COLUMNS - 1) // COLUMNS * CELL_HEIGHT
	return image


def main():
	if len(sys.argv) != 3:
		sys.exit("usage: contact.py RENDER_DIR OUT_PNG")
	render_dir, out_path = sys.argv[1:3]
	groups = load_groups()
	font, small_font = ImageFont.load_default(size=14), ImageFont.load_default(size=11)
	panels = [panel(render_dir, groups, title, ground, ink, font, small_font) for title, ground, ink in GROUNDS]
	total = sum(len(items) for _, items in groups)
	width = max(item.width for item in panels)
	sheet = Image.new("RGBA", (width, 44 + sum(item.height for item in panels) + 8 * len(panels)), SHEET_BACKGROUND + (255,))
	ImageDraw.Draw(sheet).text((PADDING, 14), "Afterglow system icons · %d icons" % total, font=ImageFont.load_default(size=18), fill=HEADING)
	y = 44
	for item in panels:
		sheet.alpha_composite(item, (0, y))
		y += item.height + 8
	sheet.convert("RGB").save(out_path, optimize=True)
	print("contact sheet", total, "icons", sheet.width, "x", sheet.height)


if __name__ == "__main__":
	main()
