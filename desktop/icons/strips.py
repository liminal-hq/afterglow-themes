#!/usr/bin/env python3
# The toolbar strips and small bitmaps ReactOS programs load as RT_BITMAP resources, composed from the icon set's own frames, cell by cell.
# Imported by render.py, which calls write(OUT_DIR, frames) after it has rendered every icon; each strip is written as OUT_DIR/bmp/NAME.bmp.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# A strip is a row of square cells, each cell one icon's frame at the cell size: the hand-tuned or 16 px profile at 16, the 24 px profile
# at 24 and the 32 px profile at 32 (the masters render.py already draws). It is written in one of two forms, the one the program that
# loads it can draw:
#   alpha  32-bit BI_RGB with straight alpha, bottom-up rows, an info header with no image size or resolution (the comctl32 standard strips,
#          Device Manager's toolbar, the help viewer and Internet Explorer: their image lists are 32-bit and keep the alpha)
#   key    24-bit BI_RGB, the cell composited over the cream dialog face and every pixel under half cover set to the key colour the program
#          masks with (Service Manager RGB(255, 0, 128), the image viewer white, the security page and certificate pictures magenta),
#          or with no key at all over the white list the cell sits on (Device Manager's root, added with no mask)
# A pixel of the art that happens to equal the key is moved one step off it, so the mask never punches a hole in a glyph. A cell may lay a
# second icon's 16 px frame at its bottom left, as an overlay (the certificate pictures' error and warning marks). Deterministic: the bytes
# depend only on the rendered frames.
import struct

from PIL import Image

CREAM = (212, 208, 200)
WHITE = (255, 255, 255)
# name: (cell size, [cell icon ids or (icon id, overlay id)], form, key colour or None, ground)
STRIPS = {
	"std-small": (16, ["cut", "copyclip", "paste", "undo", "redo", "del", "doc", "folderopen", "floppy-disk", "printpreview", "properties", "help", "search",
		"search", "printer"], "alpha", None, None),
	"view-small": (16, ["view-large", "view-small", "view-list", "views", "sortname", "views", "clock", "programs", "up", "mapdrive", "disconnect",
		"newfolder"], "alpha", None, None),
	"hist-small": (16, ["back", "forward", "star", "star", "folders"], "alpha", None, None),
	"devmgr-toolbar": (16, ["properties", "search", "check", "minus", "install", "uninstall"], "alpha", None, None),
	"devmgr-root": (16, ["mycomputer"], "key", None, WHITE),
	"hh-tree": (16, ["doc", "folder", "folderopen"], "alpha", None, None),
	"hh-toolbar": (24, ["del", "refresh", "home", "refresh", "folders", "views"], "alpha", None, None),
	"ie-toolbar": (32, ["back", "forward", "del", "refresh", "home", "printer"], "alpha", None, None),
	"aclui-principals": (16, ["user", "group", "group"], "key", (255, 0, 255), CREAM),
	"cert": (32, ["certificate"], "key", (255, 0, 255), CREAM),
	"cert-error": (32, [("certificate", "error")], "key", (255, 0, 255), CREAM),
	"cert-warning": (32, [("certificate", "warning")], "key", (255, 0, 255), CREAM),
}
STRIPS["std-large"] = (24,) + STRIPS["std-small"][1:]
STRIPS["view-large"] = (24,) + STRIPS["view-small"][1:]
STRIPS["hist-large"] = (24,) + STRIPS["hist-small"][1:]
# Service Manager's and the image viewer's toolbars are one 16 x 16 bitmap per button
for _name, _icon in (("prop", "properties"), ("refresh", "refresh"), ("export", "move"), ("create", "plus"), ("delete", "minus"), ("start", "play"),
		("stop", "stopsq"), ("pause", "pause"), ("restart", "refresh")):
	STRIPS["servman-" + _name] = (16, [_icon], "key", (255, 0, 128), CREAM)
for _name, _icon in (("prev", "back"), ("next", "forward"), ("fit", "fit"), ("realsize", "image"), ("slideshow", "play"), ("zoomin", "zoomin"),
		("zoomout", "zoomout"), ("rotcw", "rotcw"), ("rotccw", "rotccw"), ("rotcwsave", "rotcw"), ("rotccwsave", "rotccw"), ("delete", "del"),
		("print", "printer"), ("saveas", "floppy-disk"), ("modify", "paint"), ("help", "help")):
	STRIPS["shimgvw-" + _name] = (16, [_icon], "key", WHITE, CREAM)


def icons_used():
	"""Every icon id a strip draws, with the sizes it needs."""
	used = set()
	for size, cells, *_ in STRIPS.values():
		for cell in cells:
			if isinstance(cell, tuple):
				used.add((cell[0], size))
				used.add((cell[1], 16))
			else:
				used.add((cell, size))
	return used


def compose(frames, name):
	"""The strip as one RGBA image: each cell's frame, and any overlay's 16 px frame at the cell's bottom left."""
	size, cells, *_ = STRIPS[name]
	strip = Image.new("RGBA", (size * len(cells), size), (0, 0, 0, 0))
	for index, cell in enumerate(cells):
		icon, overlay = cell if isinstance(cell, tuple) else (cell, None)
		strip.alpha_composite(frames[icon, size], (index * size, 0))
		if overlay:
			strip.alpha_composite(frames[overlay, 16], (index * size, size - 16))
	return strip


def nudge(pixel, key):
	"""A pixel of the art that equals the key, moved one step off it in its first channel."""
	if key is not None and pixel == key:
		return (pixel[0] - 1 if pixel[0] else 1,) + pixel[1:]
	return pixel


def bitmap(strip, form, key, ground):
	"""The strip as a .bmp: 32-bit straight alpha, or 24-bit over the ground with the uncovered pixels set to the key."""
	width, height = strip.size
	rows = []
	for y in range(height - 1, -1, -1):
		row = bytearray()
		for x in range(width):
			red, green, blue, alpha = strip.getpixel((x, y))
			if form == "alpha":
				row += bytes((blue, green, red, alpha))
				continue
			if key is not None and alpha < 128:
				red, green, blue = key
			else:
				red, green, blue = nudge(tuple(round((channel * alpha + under * (255 - alpha)) / 255) for channel, under in zip((red, green, blue), ground)), key)
			row += bytes((blue, green, red))
		row += bytes(-len(row) % 4)
		rows.append(bytes(row))
	bits = 32 if form == "alpha" else 24
	pixels = b"".join(rows)
	info = struct.pack("<IiiHHIIiiII", 40, width, height, 1, bits, 0, 0, 0, 0, 0, 0)
	return b"BM" + struct.pack("<IHHI", 14 + len(info) + len(pixels), 0, 0, 14 + len(info)) + info + pixels


def write(bmp_dir, frames):
	"""Write every strip to bmp_dir/NAME.bmp. frames maps (icon id, size) to the RGBA frame."""
	for name, (size, cells, form, key, ground) in STRIPS.items():
		with open("%s/%s.bmp" % (bmp_dir, name), "wb") as f:
			f.write(bitmap(compose(frames, name), form, key, ground))
