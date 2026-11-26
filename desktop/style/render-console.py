#!/usr/bin/env python3
# Render the console colour preview: for each colour scheme, its 16 console colours as swatches and a sample prompt in the scheme's
# default screen colours. The colours come from agconsole.py, so the sheet is always what the registry files set.
# Usage: render-console.py OUT_PNG
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
import os
import sys

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here)

from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from agconsole import console_colours  # noqa: E402
from agdraw import SCHEMES, use_scheme  # noqa: E402

SWATCH = 26
GAP = 4
PADDING = 12
ROW_HEIGHT = 96
CELL = 8  # text is placed in fixed cells, so it reads as a console
SHEET_BACKGROUND = (24, 24, 28)


def whole(colour):
	return tuple(int(round(value)) for value in colour)


def draw_text(draw, font, origin, text, colour):
	for index, character in enumerate(text):
		draw.text((origin[0] + index * CELL, origin[1]), character, font=font, fill=colour)


def main():
	out = sys.argv[1]
	font = ImageFont.load_default(size=12)
	width = PADDING * 2 + 66 * CELL
	sheet = Image.new("RGB", (width, ROW_HEIGHT * len(SCHEMES)), SHEET_BACKGROUND)
	draw = ImageDraw.Draw(sheet)
	for row, name in enumerate(SCHEMES):
		use_scheme(name)
		table, screen, _ = console_colours(name)
		top = row * ROW_HEIGHT
		background = whole(table[screen >> 4])
		foreground = whole(table[screen & 15])
		strip_width = 16 * (SWATCH + GAP) - GAP
		draw.rectangle([4, top + 6, width - 5, top + ROW_HEIGHT - 6], fill=background)
		for index, colour in enumerate(table):
			left = PADDING + index * (SWATCH + GAP)
			draw.rectangle([left, top + 14, left + SWATCH - 1, top + 14 + SWATCH - 1], fill=whole(colour), outline=foreground if index == screen >> 4 else None)
		draw_text(draw, font, (PADDING, top + 48), f"C:\\> color {screen:02X}    {name}", foreground)
		draw_text(draw, font, (PADDING, top + 64), "C:\\> dir", foreground)
		for index, label in enumerate(("blue", "green", "cyan", "red", "magenta", "yellow")):
			hue = whole(table[(1, 2, 3, 4, 5, 6)[index] + (8 if index % 2 else 0)])
			draw_text(draw, font, (PADDING + 11 * CELL + index * 9 * CELL, top + 64), label, hue)
	sheet.save(out)


main()
