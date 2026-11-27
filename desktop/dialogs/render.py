#!/usr/bin/env python3
# Render the Afterglow dialog masters to the exact bitmaps ReactOS loads, plus a preview of the dialogs for the docs.
# Usage: render.py OUT_DIR
#
# Each master is drawn by rsvg-convert at four times its bitmap and a box filter averages every 4 x 4 block into one pixel, then it is
# written as a 24-bit uncompressed bottom-up BMP with no dates, resolution or colour profile, like the stock bitmaps it replaces (all 24-bit,
# so no palette is needed): about-banner.bmp (413 x 72, shell32.dll 131), shutdown-bg.bmp (312 x 198, msgina.dll 20003 and shell32.dll 500),
# shutdown-mark.bmp (48 x 40, msgina.dll 20002 and shell32.dll 501), shutdown-strip.bmp (33 x 330, msgina.dll 20004) and logoff-strip.bmp
# (33 x 231, shell32.dll 502). The About box's line under the banner (shell32.dll 138) is the logon bar, desktop/logon's afterglow-bar.bmp.
# afterglow-dialogs-preview.png puts them together at 2x: the Shut Down and Log Off dialogs with the buttons where the dialog draws them and
# the About banner over the bar, with no text, so it depends only on the masters. Needs rsvg-convert and Pillow.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
import io
import os
import struct
import subprocess
import sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SCALE = 4
# name, master, bitmap width and height
TARGETS = (
	("about-banner", "about-banner.svg", 413, 72),
	("shutdown-bg", "shutdown-bg.svg", 312, 198),
	("shutdown-mark", "shutdown-mark.svg", 48, 40),
	("shutdown-strip", "shutdown-strip.svg", 33, 330),
	("logoff-strip", "logoff-strip.svg", 33, 231),
)
# Where the dialogs put things at the default font (MS Shell Dlg 8 at 96 dpi: a dialog unit is 1.5 px across and 1.625 px down)
MARK_AT = (264, 2)
SHUTDOWN_BUTTONS_AT = ((54, 75), (140, 75), (225, 75))  # msgina.dll IDD_SHUTDOWN_FANCY: Sleep, Shut Down, Restart
LOGOFF_BUTTONS_AT = ((83, 75), (198, 75))  # shell32.dll IDD_LOG_OFF_FANCY: Switch User, Log Off


def rasterise(path, width, height):
	"""The master at 4x as 8-bit RGB. Fails when any pixel is see-through: a BMP has nothing to blend it with."""
	try:
		result = subprocess.run(["rsvg-convert", "--format", "png", "--width", str(width), "--height", str(height), path], check=True, stdout=subprocess.PIPE)
	except FileNotFoundError:
		sys.exit("render.py: rsvg-convert is required (the librsvg2-bin package)")
	image = Image.open(io.BytesIO(result.stdout)).convert("RGBA")
	if image.getchannel("A").getextrema() != (255, 255):
		sys.exit(f"render.py: {os.path.basename(path)} has transparent pixels, and a dialog bitmap cannot")
	return image.convert("RGB")


def bmp24(image):
	"""A 24-bit BI_RGB BMP, rows bottom-up and padded to four bytes, with a zeroed pixel density and no colour table."""
	width, height = image.size
	pad = b"\0" * (-width * 3 % 4)
	pixels = image.tobytes()
	rows = []
	for y in range(height - 1, -1, -1):
		row = pixels[y * width * 3 : (y + 1) * width * 3]
		rows.append(b"".join(row[x : x + 3][::-1] for x in range(0, len(row), 3)) + pad)
	data = b"".join(rows)
	header = struct.pack("<2sIHHI", b"BM", 14 + 40 + len(data), 0, 0, 14 + 40)
	info = struct.pack("<IiiHHIIiiII", 40, width, height, 1, 24, 0, len(data), 0, 0, 0, 0)
	return header + info + data


def dialog(background, mark, strip, places, cells):
	"""A dialog as ReactOS draws it: the background, the mark at the top right and one strip cell per button."""
	picture = background.copy()
	picture.paste(mark, MARK_AT)
	for (x, y), cell in zip(places, cells):
		picture.paste(strip.crop((0, cell * 33, 33, cell * 33 + 33)), (x, y))
	return picture


def render(out_dir):
	os.makedirs(out_dir, exist_ok=True)
	images = {}
	for name, master, width, height in TARGETS:
		big = rasterise(os.path.join(HERE, master), width * SCALE, height * SCALE)
		small = big.resize((width, height), Image.BOX)
		with open(os.path.join(out_dir, f"{name}.bmp"), "wb") as f:
			f.write(bmp24(small))
		images[name] = small
	bar = rasterise(os.path.join(HERE, "..", "logon", "bar.svg"), 413 * SCALE, 5 * SCALE).resize((413, 5), Image.BOX)
	# Shut Down: Sleep, Shut Down (focused, the default button) and Restart (cells 6, 2 and 3); Log Off: Switch User as ReactOS shows it,
	# disabled, and Log Off focused (cells 6 and 5)
	shutdown = dialog(images["shutdown-bg"], images["shutdown-mark"], images["shutdown-strip"], SHUTDOWN_BUTTONS_AT, (6, 2, 3))
	logoff = dialog(images["shutdown-bg"], images["shutdown-mark"], images["logoff-strip"], LOGOFF_BUTTONS_AT, (6, 5))
	pad = 12
	width = pad * 3 + 312 * 2
	height = pad * 4 + 198 + 77
	preview = Image.new("RGB", (width, height), (212, 208, 200))
	preview.paste(shutdown, (pad, pad))
	preview.paste(logoff, (pad * 2 + 312, pad))
	preview.paste(images["about-banner"], (pad, pad * 2 + 198))
	preview.paste(bar, (pad, pad * 2 + 198 + 72))
	preview.resize((width * 2, height * 2), Image.NEAREST).save(os.path.join(out_dir, "afterglow-dialogs-preview.png"), optimize=False)


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit("usage: render.py OUT_DIR")
	render(sys.argv[1])
