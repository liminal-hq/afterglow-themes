#!/usr/bin/env python3
# Write the vector masters of the three proposed Afterglow card-face directions for ReactOS's Solitaire and Spider Solitaire.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
#   python3 gen_faces.py OUT_DIR [DIRECTION ...]
#
# Writes OUT_DIR/<direction>/NN-<suit>-<rank>.svg for the 52 faces (NN is the cards.dll bitmap), 53-free-cell.svg and 66-joker.svg, for
# each direction named (classic, horizon, pixel; all three when none is). The shared parts are in faces.py and each direction in its own
# module. The proposals replace nothing yet: the back stays card-back-sunset.svg, and render.py and its hashes are untouched.
# Deterministic: no randomness, no clock and no environment input.
import os
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import classic  # noqa: E402
import faces as F  # noqa: E402
import horizon  # noqa: E402
import pixel  # noqa: E402

DIRECTIONS = {module.NAME: module for module in (classic, horizon, pixel)}


def masters(direction):
	"""Every master of a direction as {file name: SVG text}."""
	module = DIRECTIONS[direction]
	files = {}
	for suit in F.SUITS:
		for rank_index in range(13):
			files[F.master_name(rank_index, suit)] = module.face(rank_index, suit)
	files["%02d-free-cell.svg" % F.FREE_CARD] = module.free_card()
	files["%02d-joker.svg" % F.JOKER] = module.joker()
	return files


def main():
	if len(sys.argv) < 2:
		sys.exit("usage: gen_faces.py OUT_DIR [classic|horizon|pixel ...]")
	out = sys.argv[1]
	chosen = sys.argv[2:] or list(DIRECTIONS)
	for direction in chosen:
		if direction not in DIRECTIONS:
			sys.exit("gen_faces.py: unknown direction %s" % direction)
		folder = os.path.join(out, direction)
		os.makedirs(folder, exist_ok=True)
		files = masters(direction)
		for name in sorted(files):
			with open(os.path.join(folder, name), "w") as handle:
				handle.write(files[name])
		print("%s: %d masters" % (direction, len(files)))


if __name__ == "__main__":
	main()
