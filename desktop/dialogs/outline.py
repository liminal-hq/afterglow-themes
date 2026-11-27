#!/usr/bin/env python3
# Turn a line of text into SVG path data from a TrueType font, so the dialog masters carry outlines and need no font to render.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# Standard library only: reads the cmap (format 4), hmtx, loca and glyf tables, and writes each quadratic contour as SVG Q segments.
# Composite glyphs are followed with their offsets (no scaling), which is all DejaVu Sans uses for the characters the masters need.
# Kerning is not applied. The masters are generated with DejaVu Sans, whose licence allows embedding the outlines.
import struct


class Font:
	def __init__(self, path):
		self.data = open(path, "rb").read()
		count = struct.unpack_from(">H", self.data, 4)[0]
		self.tables = {}
		for index in range(count):
			tag, _checksum, offset, length = struct.unpack_from(">4sIII", self.data, 12 + 16 * index)
			self.tables[tag.decode("ascii")] = (offset, length)
		head = self.tables["head"][0]
		self.units_per_em = struct.unpack_from(">H", self.data, head + 18)[0]
		self.long_loca = struct.unpack_from(">h", self.data, head + 50)[0] == 1
		hhea = self.tables["hhea"][0]
		self.metric_count = struct.unpack_from(">H", self.data, hhea + 34)[0]
		self.cmap = self._read_cmap()

	def _read_cmap(self):
		base = self.tables["cmap"][0]
		count = struct.unpack_from(">H", self.data, base + 2)[0]
		for index in range(count):
			platform, encoding, offset = struct.unpack_from(">HHI", self.data, base + 4 + 8 * index)
			table = base + offset
			if (platform, encoding) in ((3, 1), (0, 3)) and struct.unpack_from(">H", self.data, table)[0] == 4:
				segments = struct.unpack_from(">H", self.data, table + 6)[0] // 2
				ends = struct.unpack_from(">%dH" % segments, self.data, table + 14)
				starts = struct.unpack_from(">%dH" % segments, self.data, table + 16 + 2 * segments)
				deltas = struct.unpack_from(">%dh" % segments, self.data, table + 16 + 4 * segments)
				range_base = table + 16 + 6 * segments
				offsets = struct.unpack_from(">%dH" % segments, self.data, range_base)
				mapping = {}
				for segment in range(segments):
					for code in range(starts[segment], ends[segment] + 1):
						if code == 0xFFFF:
							continue
						if offsets[segment] == 0:
							glyph = (code + deltas[segment]) & 0xFFFF
						else:
							at = range_base + 2 * segment + offsets[segment] + 2 * (code - starts[segment])
							glyph = struct.unpack_from(">H", self.data, at)[0]
							glyph = (glyph + deltas[segment]) & 0xFFFF if glyph else 0
						mapping[code] = glyph
				return mapping
		raise ValueError("no Unicode cmap of format 4")

	def advance(self, glyph):
		base = self.tables["hmtx"][0]
		index = min(glyph, self.metric_count - 1)
		return struct.unpack_from(">H", self.data, base + 4 * index)[0]

	def _glyph_range(self, glyph):
		loca = self.tables["loca"][0]
		if self.long_loca:
			start, end = struct.unpack_from(">II", self.data, loca + 4 * glyph)
		else:
			start, end = (value * 2 for value in struct.unpack_from(">HH", self.data, loca + 2 * glyph))
		base = self.tables["glyf"][0]
		return base + start, end - start

	def contours(self, glyph, offset_x=0, offset_y=0):
		"""The glyph's contours as lists of (x, y, on_curve) in font units."""
		start, length = self._glyph_range(glyph)
		if length == 0:
			return []
		contour_count = struct.unpack_from(">h", self.data, start)[0]
		if contour_count < 0:
			return self._composite(start + 10, offset_x, offset_y)
		ends = struct.unpack_from(">%dH" % contour_count, self.data, start + 10)
		point_count = ends[-1] + 1
		at = start + 10 + 2 * contour_count
		instruction_length = struct.unpack_from(">H", self.data, at)[0]
		at += 2 + instruction_length
		flags = []
		while len(flags) < point_count:
			flag = self.data[at]
			at += 1
			flags.append(flag)
			if flag & 8:
				repeat = self.data[at]
				at += 1
				flags.extend([flag] * repeat)
		xs, ys = [], []
		for values, short_bit, same_bit in ((xs, 2, 16), (ys, 4, 32)):
			value = 0
			for flag in flags:
				if flag & short_bit:
					step = self.data[at]
					at += 1
					value += step if flag & same_bit else -step
				elif not flag & same_bit:
					value += struct.unpack_from(">h", self.data, at)[0]
					at += 2
				values.append(value)
		result, first = [], 0
		for end in ends:
			result.append([(xs[i] + offset_x, ys[i] + offset_y, bool(flags[i] & 1)) for i in range(first, end + 1)])
			first = end + 1
		return result

	def _composite(self, at, offset_x, offset_y):
		result = []
		while True:
			flags, glyph = struct.unpack_from(">HH", self.data, at)
			at += 4
			if flags & 1:
				argument_x, argument_y = struct.unpack_from(">hh", self.data, at)
				at += 4
			else:
				argument_x, argument_y = struct.unpack_from(">bb", self.data, at)
				at += 2
			if flags & 8:
				at += 2
			elif flags & 0x40:
				at += 4
			elif flags & 0x80:
				at += 8
			result += self.contours(glyph, offset_x + argument_x, offset_y + argument_y)
			if not flags & 0x20:
				return result


def number(value):
	text = ("%.2f" % value).rstrip("0").rstrip(".")
	return "0" if text in ("-0", "") else text


def contour_path(points, scale, origin_x, origin_y):
	"""One closed quadratic contour as SVG path data, flipping y (font units grow up, SVG down)."""
	def place(point):
		return origin_x + point[0] * scale, origin_y - point[1] * scale

	count = len(points)
	start_index = next((i for i, point in enumerate(points) if point[2]), None)
	if start_index is None:  # all off-curve: start between the first two
		first = ((points[0][0] + points[1][0]) / 2, (points[0][1] + points[1][1]) / 2, True)
		points = [first] + points[1:] + points[:1]
		start_index = 0
		count = len(points)
	ordered = points[start_index:] + points[:start_index]
	x, y = place(ordered[0])
	out = ["M%s %s" % (number(x), number(y))]
	index = 1
	while index <= count:
		point = ordered[index % count]
		if point[2]:
			x, y = place(point)
			out.append("L%s %s" % (number(x), number(y)))
			index += 1
		else:
			following = ordered[(index + 1) % count]
			if following[2]:
				end = following
				index += 2
			else:
				end = ((point[0] + following[0]) / 2, (point[1] + following[1]) / 2, True)
				index += 1
			control_x, control_y = place(point)
			end_x, end_y = place(end)
			out.append("Q%s %s %s %s" % (number(control_x), number(control_y), number(end_x), number(end_y)))
	out.append("Z")
	return "".join(out)


def text_path(font, text, size, x, baseline, tracking=0.0):
	"""SVG path data for `text` set at `size` (the em in SVG units) with its left at x and its baseline at `baseline`. Returns the data and
	the advance width."""
	scale = size / font.units_per_em
	pen_x = x
	parts = []
	for character in text:
		glyph = font.cmap.get(ord(character), 0)
		for contour in font.contours(glyph):
			if len(contour) > 1:
				parts.append(contour_path(contour, scale, pen_x, baseline))
		pen_x += font.advance(glyph) * scale + tracking
	return "".join(parts), pen_x - x - tracking
