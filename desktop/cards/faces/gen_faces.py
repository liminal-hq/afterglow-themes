#!/usr/bin/env python3
# Write the vector masters of the Afterglow card faces for ReactOS's Solitaire and Spider Solitaire, and of the two review-only alternatives.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
#   python3 gen_faces.py OUT_DIR                 the selected set (classic.py): OUT_DIR/NN-<suit>-<rank>.svg, 53-free-cell.svg, 66-joker.svg
#   python3 gen_faces.py --alternatives OUT_DIR  the alternatives: OUT_DIR/horizon/ and OUT_DIR/pixel/, the same 54 names each
#
# NN is the cards.dll bitmap the master replaces: 1 to 52 for the faces (suit order clubs, diamonds, hearts, spades, ace to king), 53 for
# FreeCard and 66 for the Joker. The selected masters are committed in desktop/cards/faces and hashed in desktop/cards/SHA256SUMS.masters;
# the alternatives (desktop/cards/alternatives/faces/horizon.py and pixel.py) are not committed as SVGs, and their hashes are in
# desktop/cards/alternatives/faces/SHA256SUMS, so they are written again identically. Deterministic: no randomness, no clock and no
# environment input.
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "alternatives", "faces"))
import classic  # noqa: E402
import faces as F  # noqa: E402
import horizon  # noqa: E402
import pixel  # noqa: E402

SELECTED = classic
ALTERNATIVES = {module.NAME: module for module in (horizon, pixel)}
DIRECTIONS = {SELECTED.NAME: SELECTED, **ALTERNATIVES}


def masters(module):
	"""Every master of a direction as {file name: SVG text}."""
	files = {}
	for suit in F.SUITS:
		for rank_index in range(13):
			files[F.master_name(rank_index, suit)] = module.face(rank_index, suit)
	files["%02d-free-cell.svg" % F.FREE_CARD] = module.free_card()
	files["%02d-joker.svg" % F.JOKER] = module.joker()
	return files


def write(folder, files):
	os.makedirs(folder, exist_ok=True)
	for name in sorted(files):
		with open(os.path.join(folder, name), "w") as handle:
			handle.write(files[name])


def main():
	arguments = sys.argv[1:]
	if arguments[:1] == ["--alternatives"] and len(arguments) == 2:
		for name, module in ALTERNATIVES.items():
			write(os.path.join(arguments[1], name), masters(module))
			print("%s: 54 masters" % name)
	elif len(arguments) == 1 and not arguments[0].startswith("-"):
		write(arguments[0], masters(SELECTED))
		print("card faces: 54 masters")
	else:
		sys.exit("usage: gen_faces.py OUT_DIR | gen_faces.py --alternatives OUT_DIR")


if __name__ == "__main__":
	main()
