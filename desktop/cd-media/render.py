#!/usr/bin/env python3
# Lay the Afterglow for ReactOS CD media masters out on print pages and render the PDFs and previews.
# Usage: render.py OUT_DIR
#
# Reads the committed masters beside this script, removes each one's guides group (data-print="no") and inlines what is left, so the PDFs
# are vector (rsvg-convert -f pdf) and need no font. Writes to OUT_DIR:
#   disc-art.pdf                         the selected disc for a printable disc (120 x 120 mm page, no marks)
#   disc-label-single.pdf                one label on a page cut to it, with bleed and crop marks
#   disc-label-A4.pdf, -Letter.pdf       two labels a page, where LABEL_SHEETS puts them, with crop marks and the hole punch ring
#   disc-label-single-A4.pdf, -Letter    one label in the top position of the same sheet
#   disc-label-plain-A4.pdf, -Letter     two labels for plain paper, with the cut circles and a compass centre drawn on
#   jewel-case-front.pdf, -A4, -Letter   the front insert, on a page cut to it and on A4 and Letter, with crop marks
#   jewel-case-back.pdf, -A4, -Letter    the tray card, the same, with the spine folds marked
#   png/*.png                            each master at 150 dpi without its guides, and with them (*-guides.png)
#   preview.png                          the mock-up, 2400 px wide
#   contact-sheet.png                    every part at its actual proportions, side by side
# Needs rsvg-convert. The contact sheet's captions are outlined with gen_media.py's type when Noto Sans is installed and are left out
# otherwise; nothing else needs a font.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
import importlib.util
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))

# Where the labels sit on a sheet: the page size and each label's centre, in mm from the top left. Two-up full-face CD label sheets put
# their labels near these points, but every product differs a little: measure your sheet (or its template) and change the centres here.
LABEL_SHEETS = {
	"A4": ((210.0, 297.0), ((105.0, 74.25), (105.0, 222.75))),
	"Letter": ((215.9, 279.4), ((107.95, 69.85), (107.95, 209.55))),
}
MARK_COLOUR = "#090e2a"  # the darkest Afterglow colour, for crop and fold marks
CUT_COLOUR = "#fff3de"  # cream, for the cut lines drawn on the plain-paper labels
PUNCH_COLOUR = "#ffd08e"  # pale gold, for the hole punch ring
MARK_GAP, MARK_LENGTH, MARK_WIDTH = 1.5, 4.0, 0.2  # crop marks start 1.5 mm past the bleed and run 4 mm
LABEL_RADIUS, HOLE_RADIUS, LABEL_BLEED = 58.5, 20.5, 3.0


def load(name, path):
	spec = importlib.util.spec_from_file_location(name, path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module


def number(value):
	text = ("%.3f" % value).rstrip("0").rstrip(".")
	return "0" if text in ("-0", "") else text


class Master:
	"""A master without its guides: its size in mm and its defs and body, with every id given a new prefix so masters can share a page."""

	def __init__(self, name, prefix=None):
		text = open(os.path.join(HERE, name)).read()
		text = strip_guides(text)
		view = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', text)
		self.width, self.height = float(view.group(1)), float(view.group(2))
		self.defs = re.search(r"<defs>(.*?)</defs>", text, re.S).group(1)
		self.body = re.search(r"</defs>\n(.*)\n</svg>", text, re.S).group(1)
		if prefix:
			for old in sorted(set(re.findall(r'id="([a-z]+-)', self.defs + self.body))):
				self.defs = self.defs.replace('id="%s' % old, 'id="%s%s' % (prefix, old)).replace("url(#%s" % old, "url(#%s%s" % (prefix, old))
				self.body = self.body.replace('id="%s' % old, 'id="%s%s' % (prefix, old)).replace("url(#%s" % old, "url(#%s%s" % (prefix, old))


def strip_guides(text):
	"""Remove the guides group, which holds only circles, rects and paths, so the first closing tag after it is its own."""
	stripped = re.sub(r'<g id="guides" data-print="no".*?</g>', "", text, flags=re.S)
	if 'id="guides"' in stripped or ' data-guide="' in stripped:
		sys.exit("render.py: a guides group was left in a print file")
	return stripped


def page(width, height, defs, body):
	return ('<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
		'width="%smm" height="%smm" viewBox="0 0 %s %s">\n<defs>%s</defs>\n<rect width="100%%" height="100%%" fill="#ffffff"/>\n%s\n</svg>\n'
		% (number(width), number(height), number(width), number(height), defs, body))


def crop_marks(left, top, width, height, bleed):
	"""Corner marks on the trim lines, starting MARK_GAP past the bleed."""
	near, far = bleed + MARK_GAP, bleed + MARK_GAP + MARK_LENGTH
	right, bottom = left + width, top + height
	lines = []
	for x, y, sign_x, sign_y in ((left, top, -1, -1), (right, top, 1, -1), (left, bottom, -1, 1), (right, bottom, 1, 1)):
		lines.append("M%s %sH%s" % (number(x + sign_x * near), number(y), number(x + sign_x * far)))
		lines.append("M%s %sV%s" % (number(x), number(y + sign_y * near), number(y + sign_y * far)))
	return '<path fill="none" stroke="%s" stroke-width="%s" d="%s"/>' % (MARK_COLOUR, number(MARK_WIDTH), "".join(lines))


def fold_marks(left, top, height, bleed, folds):
	near, far = bleed + MARK_GAP, bleed + MARK_GAP + MARK_LENGTH
	lines = []
	for x in folds:
		lines.append("M%s %sV%s" % (number(left + x), number(top - near), number(top - far)))
		lines.append("M%s %sV%s" % (number(left + x), number(top + height + near), number(top + height + far)))
	return '<path fill="none" stroke="%s" stroke-width="%s" stroke-dasharray="1 0.7" d="%s"/>' % (MARK_COLOUR, number(MARK_WIDTH), "".join(lines))


def ring(centre_x, centre_y, radius, colour, dash=None, width=0.15):
	extra = ' stroke-dasharray="%s"' % dash if dash else ""
	return '<circle cx="%s" cy="%s" r="%s" fill="none" stroke="%s" stroke-width="%s"%s/>' % (number(centre_x), number(centre_y), number(radius), colour, number(width), extra)


def label_at(centre_x, centre_y, plain):
	"""One label placed by its centre: the art, the crop marks round its 117 mm square, and the hole punch ring. The plain-paper version
	adds solid cut circles and a compass centre."""
	half = LABEL_RADIUS + LABEL_BLEED
	parts = ['<use xlink:href="#label" href="#label" x="%s" y="%s"/>' % (number(centre_x - half), number(centre_y - half))]
	parts.append(crop_marks(centre_x - LABEL_RADIUS, centre_y - LABEL_RADIUS, 2 * LABEL_RADIUS, 2 * LABEL_RADIUS, LABEL_BLEED))
	if plain:
		parts.append(ring(centre_x, centre_y, LABEL_RADIUS, CUT_COLOUR, width=0.2))
		parts.append(ring(centre_x, centre_y, HOLE_RADIUS, CUT_COLOUR, width=0.2))
		parts.append('<path fill="none" stroke="%s" stroke-width="0.15" d="M%s %sh6M%s %sv6"/>' % (MARK_COLOUR, number(centre_x - 3), number(centre_y), number(centre_x), number(centre_y - 3)))
	else:
		parts.append(ring(centre_x, centre_y, HOLE_RADIUS, PUNCH_COLOUR, dash="0.8 0.6"))
	return "".join(parts)


def label_defs():
	label = Master("label.svg")
	return label.defs + '<g id="label">%s</g>' % label.body


def piece_page(master, trim_width, trim_height, bleed, page_size=None, top=None, folds=()):
	"""A front insert or tray card on a page: cut to the piece and its marks, or centred across a sheet, near its top."""
	margin = bleed + MARK_GAP + MARK_LENGTH + 2
	if page_size is None:
		width, height = trim_width + 2 * margin, trim_height + 2 * margin
		left, top_edge = margin, margin
	else:
		width, height = page_size
		left = (width - trim_width) / 2
		top_edge = top
	body = '<g transform="translate(%s %s)">%s</g>' % (number(left - bleed), number(top_edge - bleed), master.body)
	body += crop_marks(left, top_edge, trim_width, trim_height, bleed)
	if folds:
		body += fold_marks(left, top_edge, trim_height, bleed, folds)
	return page(width, height, master.defs, body)


def convert(svg_path, out_path, file_format, extra=()):
	try:
		subprocess.run(["rsvg-convert", "--format", file_format, *extra, "--output", out_path, svg_path], check=True)
	except FileNotFoundError:
		sys.exit("render.py: rsvg-convert is required (the librsvg2-bin package)")


def write(folder, name, text):
	path = os.path.join(folder, name)
	with open(path, "w") as handle:
		handle.write(text)
	return path


def contact_sheet():
	"""Every part at its actual proportions: the three discs, the label with its bleed, the front insert and the tray card."""
	try:
		generator = load("gen_media", os.path.join(HERE, "gen_media.py"))
		kind = generator.Type(generator.find_font_dir(None))
	except SystemExit:
		generator, kind = None, None
	items = (
		("disc.svg", "B · Halo, disc", 15, 30, True),
		("alternatives/disc-sunrise.svg", "A · Sunrise, disc", 150, 30, False),
		("alternatives/disc-horizon.svg", "C · Horizon, disc", 285, 30, False),
		("label.svg", "CD label, 117 mm with 3 mm bleed", 15, 182, False),
		("jewel-front.svg", "Jewel case front, 120 mm with 2 mm bleed", 153, 182, False),
		("jewel-back.svg", "Tray card, 150 x 118 mm with 2 mm bleed", 292, 182, False),
	)
	width, height = 461.0, 322.0
	defs, body = [], ['<rect width="%s" height="%s" fill="#fbfaf6"/>' % (number(width), number(height))]
	for index, (name, caption, x, y, selected) in enumerate(items):
		master = Master(name, "c%d" % index)
		defs.append(master.defs)
		body.append('<g transform="translate(%s %s)">%s</g>' % (number(x), number(y), master.body))
		if kind:
			caption_x = x
			if selected:
				badge_width = kind.medium.width("SELECTED", 9 * generator.POINT, 0.4) + 4
				body.append('<rect x="%s" y="%s" width="%s" height="5.2" rx="2.6" fill="%s"/>' % (number(x), number(y - 10.2), number(badge_width), generator.BRIGHT_GOLD))
				body.append(kind.straight(kind.medium, "SELECTED", 9, generator.BACKDROP, x + 2, y - 6.4, tracking=0.4))
				caption_x = x + badge_width + 2.5
			body.append(kind.straight(kind.regular, caption, 12, generator.BACKDROP, caption_x, y - 5.6))
	if kind:
		body.append(kind.straight(kind.light, "Afterglow for ReactOS · CD media · " + generator.VERSION, 22, generator.BACKDROP, 15, 16.5))
	return '<svg xmlns="http://www.w3.org/2000/svg" width="%smm" height="%smm" viewBox="0 0 %s %s"><defs>%s</defs>%s</svg>\n' % (
		number(width), number(height), number(width), number(height), "".join(defs), "".join(body))


def render(out_dir):
	work = os.path.join(out_dir, "svg")
	previews = os.path.join(out_dir, "png")
	os.makedirs(work, exist_ok=True)
	os.makedirs(previews, exist_ok=True)

	disc = Master("disc.svg")
	convert(write(work, "disc-art.svg", page(disc.width, disc.height, disc.defs, disc.body)), os.path.join(out_dir, "disc-art.pdf"), "pdf")

	defs = label_defs()
	side = 2 * (LABEL_RADIUS + LABEL_BLEED + MARK_GAP + MARK_LENGTH + 2)
	convert(write(work, "disc-label-single.svg", page(side, side, defs, label_at(side / 2, side / 2, False))), os.path.join(out_dir, "disc-label-single.pdf"), "pdf")
	for sheet, ((width, height), centres) in LABEL_SHEETS.items():
		sticker = "".join(label_at(x, y, False) for x, y in centres)
		convert(write(work, "disc-label-%s.svg" % sheet, page(width, height, defs, sticker)), os.path.join(out_dir, "disc-label-%s.pdf" % sheet), "pdf")
		single = label_at(centres[0][0], centres[0][1], False)
		convert(write(work, "disc-label-single-%s.svg" % sheet, page(width, height, defs, single)), os.path.join(out_dir, "disc-label-single-%s.pdf" % sheet), "pdf")
		plain = "".join(label_at(x, y, True) for x, y in centres)
		convert(write(work, "disc-label-plain-%s.svg" % sheet, page(width, height, defs, plain)), os.path.join(out_dir, "disc-label-plain-%s.pdf" % sheet), "pdf")

	front, back = Master("jewel-front.svg"), Master("jewel-back.svg")
	pieces = (("jewel-case-front", front, 120.0, 120.0, 2.0, ()), ("jewel-case-back", back, 150.0, 118.0, 2.0, (6.0, 144.0)))
	for name, master, trim_width, trim_height, bleed, folds in pieces:
		convert(write(work, name + ".svg", piece_page(master, trim_width, trim_height, bleed, folds=folds)), os.path.join(out_dir, name + ".pdf"), "pdf")
		for sheet, ((width, height), _centres) in LABEL_SHEETS.items():
			text = piece_page(master, trim_width, trim_height, bleed, (width, height), 25.0, folds)
			convert(write(work, "%s-%s.svg" % (name, sheet), text), os.path.join(out_dir, "%s-%s.pdf" % (name, sheet)), "pdf")

	for name in ("disc", "alternatives/disc-sunrise", "alternatives/disc-horizon", "label", "jewel-front", "jewel-back"):
		base = os.path.basename(name)
		master = Master(name + ".svg")
		clean = write(work, base + "-print.svg", page(master.width, master.height, master.defs, master.body).replace('<rect width="100%" height="100%" fill="#ffffff"/>', ""))
		convert(clean, os.path.join(previews, base + ".png"), "png", ("--dpi-x", "150", "--dpi-y", "150"))
		convert(os.path.join(HERE, name + ".svg"), os.path.join(previews, base + "-guides.png"), "png", ("--dpi-x", "150", "--dpi-y", "150"))
	convert(os.path.join(HERE, "mockup.svg"), os.path.join(out_dir, "preview.png"), "png", ("--width", "2400", "--keep-aspect-ratio"))
	convert(write(work, "contact-sheet.svg", contact_sheet()), os.path.join(out_dir, "contact-sheet.png"), "png", ("--width", "2400", "--keep-aspect-ratio"))


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit("usage: render.py OUT_DIR")
	render(sys.argv[1])
