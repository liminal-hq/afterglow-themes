#!/usr/bin/env python3
# Afterglow icons: hand-tuned 16 px frames, drawn on the pixel grid, for the icons ReactOS shows small most often.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# Not run on its own: gen_e.py loads this file and calls register() with its own namespace; each icon here then gets a hinted
# svg/ID-16.svg, which render.py uses for the 16 px frame in place of the scripted downscale of svg/16/ID.svg. Every frame is one 16 x 16
# character grid, written out pixel by pixel. The shared shapes (the dusk plate, the page with its fold, the drive) are small helpers;
# the part that makes each icon itself is placed by hand. The output is one 1 x 1 rect per pixel with crisp edges: no anti-aliasing, no
# blur, no ramp and no shadow, the same rules as set E's hinted redraws.
#
# The grid characters:
#   lowercase material letter   the material's base tone (g gold, f light gold, p paper, q paper back, m device front, n device body,
#                               d dusk, r rose, v violet, a glass)
#   uppercase material letter   the same material's baked 16 px edge (its base 60 % of the way to its edge tone)
#   k, K                        the dusk plate: k is the sky ramp for that row, K the plate's horizon rim
#   digits and symbols          flat details, in DETAIL below
#   .                           transparent

# Filled in by register()
COLOURS = {}
KEYLINE_COLOURS = {}  # each material's 16 px edge retuned to the keyline tone, for the frames gen_e.py keylines (KEYLINED_16)
SKY_ROWS = []

ART = {}  # icon id -> 16 rows of 16 characters


def blank():
	return [["."] * 16 for _ in range(16)]


def rows_of(grid):
	return ["".join(row) for row in grid]


def put(grid, left, top, block):
	"""Lay a hand-drawn block over the grid; its '.' cells leave what is under them."""
	for row_index, row in enumerate(block):
		for column_index, character in enumerate(row):
			if character != ".":
				grid[top + row_index][left + column_index] = character
	return grid


def box(grid, left, top, right, bottom, material, round_corners=False):
	"""A face from (left, top) to (right, bottom) inclusive, its outer ring in the material's edge tone."""
	for y in range(top, bottom + 1):
		for x in range(left, right + 1):
			corner = (x in (left, right)) and (y in (top, bottom))
			if corner and round_corners:
				continue
			on_ring = x in (left, right) or y in (top, bottom)
			grid[y][x] = material.upper() if on_ring else material
	if round_corners:  # the pixel inside each cut corner closes the ring
		for x, y in ((left + 1, top + 1), (right - 1, top + 1), (left + 1, bottom - 1), (right - 1, bottom - 1)):
			if grid[y][x] == material:
				grid[y][x] = material.upper()
	return grid


def plate():
	"""The softly raised dusk plate at 16 px: 14 x 14 with cut corners, a horizon rim on the top and left, the sky ramp below."""
	grid = blank()
	for y in range(1, 15):
		for x in range(1, 15):
			if (x in (1, 14)) and (y in (1, 14)):
				continue
			grid[y][x] = "K" if (y == 1 or x == 1) else "k"
	return grid


def page(left=3, right=12, top=1, bottom=14, fold=3):
	"""A page with a dog-ear, edged; the fold in the paper-back tone."""
	grid = blank()
	for y in range(top, bottom + 1):
		for x in range(left, right + 1):
			if y - top < fold and x > right - fold + (y - top):
				continue
			grid[y][x] = "p"
	for y in range(top, bottom + 1):
		for x in range(left, right + 1):
			if grid[y][x] != "p":
				continue
			neighbours = [(x + dx, y + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))]
			if any(not (0 <= nx < 16 and 0 <= ny < 16) or grid[ny][nx] == "." for nx, ny in neighbours):
				grid[y][x] = "P"
	for step in range(fold):
		for x in range(right - fold + 1, right - fold + 2 + step):
			grid[top + step][x] = "Q" if x == right - fold + 1 + step or step == fold - 1 or x == right - fold + 1 else "q"
	return grid


def drive(top=4):
	"""The hard disk at 16: a body behind, a front face, a slot and a gold light."""
	grid = blank()
	box(grid, 2, top, 13, top + 4, "n", True)
	box(grid, 1, top + 2, 14, top + 8, "m", True)
	put(grid, 3, top + 5, ["99999"])
	put(grid, 11, top + 4, ["22", "22"])
	return grid


def art(icon_id):
	def register_art(draw):
		grid = draw()
		rows = rows_of(grid) if isinstance(grid[0], list) else grid
		assert len(rows) == 16 and all(len(row) == 16 for row in rows), icon_id
		ART[icon_id] = rows
		return draw
	return register_art


# ---- the device icons -------------------------------------------------------------------------------------------------------------------------------
# The drive slots and My Computer show the device. The medium alone is kept as cd-disc, floppy-disk, usb-key and ram-module below, and the
# monitor alone as monitor (hinted in gen_e.py).
@art("cd")
def cd_drive():
	return [
		"................",
		"................",
		"...NNNNNNNNNN...",
		".MMMMMMMMMMMMMM.",
		".Mmmmmmmmm2mNNM.",
		".M888888888888M.",
		"..DddddddddddD..",
		"..DddMMMMMMddD..",
		".DdMMm^^mmmMMdD.",
		".DMm^mm--mmmmMD.",
		".DMmmm-55-mmmMD.",
		".DMmmmm--mmm%MD.",
		".DdMMmmmm%%MMdD.",
		".DdddMMMMMMdddD.",
		".DDDDDDDDDDDDDD.",
		"................",
	]


@art("floppy")
def floppy_drive():
	return [
		"................",
		"...NNNNNNNNNN...",
		".MMMMMMMMMMMMMM.",
		".Mmmmmmmmmmm2mM.",
		".M8888888888mmM.",
		".M8VvNNNNvV8mmM.",
		".MmVvNn#NvVmmmM.",
		".MmVvNNNNvVmNNM.",
		".MmVvvvvvvVmNNM.",
		".MVvvvvvvvvVMMM.",
		"..VvPPPPPPvV....",
		"..VvP1111PvV....",
		"..VvPppppPvV....",
		"..VvP111pPvV....",
		"..VVPPPPPPVV....",
		"................",
	]


@art("removable")
def removable_drive():
	return [
		"................",
		"...........NN...",
		"..........NnnN..",
		".........N#n#N..",
		"........NnnnnN..",
		".......GNnnnN...",
		"......GgGNnN....",
		".....Ggff4GN....",
		"....GgfffgG.....",
		"...GgfffggG.....",
		"..GggggggGG.....",
		".GggggggG.......",
		".Gg^gggG........",
		".GgggGG.........",
		"..GGG...........",
		"................",
	]


@art("ramdisk")
def ram_disk_drive():
	return [
		"................",
		"..-.-.-.-.-.-...",
		".1111111111111..",
		".1ddddGGGddddD..",
		".1dddGgggGdddD..",
		".1ddGgggffGddD..",
		".1ddGgg-ffGddD..",
		".1ddGgggggGddD..",
		".1dddGgggGdddD..",
		".1ddddGGGddddD..",
		".1dddddddddddD..",
		".DDDDDDDDDDDDD..",
		"..-.-.-.-.-.-...",
		"..-.-.-.-.-.-...",
		"................",
		"................",
	]


@art("mycomputer")
def my_computer():
	return [
		"................",
		"..........NNNNN.",
		"MMMMMMMMMMNnnnN.",
		"M55555555MN99nN.",
		"M66666666MNnnnN.",
		"M66622666MN99nN.",
		"M77222277MNnnnN.",
		"MMMMMMMMMMNnnnN.",
		"....NN....NnnnN.",
		"..NNNNNN..NnGnN.",
		"..........NnnnN.",
		"..........NNNNN.",
		"................",
		"................",
		"................",
		"................",
	]


# ---- drives ---------------------------------------------------------------------------------------------------------------------------------------
@art("cd-disc")
def cd_disc():
	return [
		"................",
		".....MMMMMM.....",
		"...MMmmmmmmMM...",
		"..M22mmmmmmmmM..",
		"..M2mmmmmmmmmM..",
		".M2mmmm--mmmmmM.",
		".Mmmmm-mm-mmmmM.",
		".Mmmm-m..m-mmmM.",
		".Mmmm-m..m-mmmM.",
		".Mmmmm-mm-mmmmM.",
		".Mmmmmm--mmmm%M.",
		"..Mmmmmmmmmmm%M.",
		"..Mmmmmmmmm%%M..",
		"...MMmmmmmmMM...",
		".....MMMMMM.....",
		"................",
	]


@art("floppy-disk")
def floppy_disk():
	return [
		"................",
		".VVVVNNNNNNVVV..",
		".VvvvNnn=nNvvvV.",
		".VvvvNnn=nNvvvV.",
		".VvvvNNNNNNvvvV.",
		".VvvvvvvvvvvvvV.",
		".VvvvvvvvvvvvvV.",
		".VvPPPPPPPPPPvV.",
		".VvPppppppppPvV.",
		".VvPp111111pPvV.",
		".VvPppppppppPvV.",
		".VvPp11111ppPvV.",
		".VvPppppppppPvV.",
		".VvPppppppppPvV.",
		".VVPPPPPPPPPPVV.",
		"................",
	]


@art("netdrive")
def network_drive():
	grid = drive(1)
	put(grid, 0, 10, [
		".......NN.......",
		"....NNNNNNNN....",
		"GGGG..NNNN..GGGG",
		"GggG..NnnN..GggG",
		"GGGG..NNNN..GGGG",
	])
	return grid


@art("usb-key")
def usb_key():
	return [
		"......NNNN......",
		"......N==N......",
		"......NNNN......",
		".....MMMMMM.....",
		"....MmmmmmmM....",
		"....MmGGGGmM....",
		"....MmGggGmM....",
		"....MmGggGmM....",
		"....MmGggGmM....",
		"....MmGGGGmM....",
		"....MmmmmmmM....",
		"....Mmmm2mmM....",
		"....MmmmmmmM....",
		".....MMMMMM.....",
		"................",
		"................",
	]


@art("ram-module")
def ram_module():
	return [
		"................",
		"................",
		"................",
		"DDDDDDDDDDDDDDDD",
		"DdNNNdNNNdNNNddD",
		"DdNnNdNnNdNnNddD",
		"DdNnNdNnNdNnNddD",
		"DdNNNdNNNdNNNddD",
		"DddddddddddddddD",
		"D2d2d2d2DD2d2d2D",
		"D2d2d2d2DD2d2d2D",
		"DDDDDDDDDDDDDDDD",
		"................",
		"................",
		"................",
		"................",
	]


@art("netdriveoff")
def network_drive_off():
	grid = network_drive()
	put(grid, 9, 9, [
		".RRRRR.",
		"R4rrr4R",
		"Rr4r4rR",
		"Rrr4rrR",
		"Rr4r4rR",
		"R4rrr4R",
		".RRRRR.",
	])
	return grid


# ---- file types -----------------------------------------------------------------------------------------------------------------------------------
def page_with(block, left=5, top=4):
	grid = page()
	return put(grid, left, top, block)


@art("text")
def text_file():
	return page_with(["111111", "......", "111111", "......", "111111", "......", "111111", "......", "1111"], 5, 4)


@art("image")
def image_file():
	return page_with([
		"555555",
		"666622",
		"666622",
		"777777",
		"~77777",
		"~~7~~7",
		"~~~~~~",
	], 5, 5)


@art("program")
def program_file():
	return [
		"................",
		"................",
		"GGGGGGGGGGGGGGGG",
		"GggggggggggggggG",
		"GGGGGGGGGGGGGGGG",
		"MmmmmmmmmmmmmmmM",
		"Mm~mmmmmmmmmmmmM",
		"Mmm~mmmmmmmmmmmM",
		"Mm~mmmmmmmmmmmmM",
		"Mmmmm1111mmmmmmM",
		"MmmmmmmmmmmmmmmM",
		"MMMMMMMMMMMMMMMM",
		"................",
		"................",
		"................",
		"................",
	]


@art("library")
def library_file():
	return page_with([
		"1111..",
		"......",
		"..G.G.",
		".GgggG",
		"Ggg8gg",
		".Gg8gG",
		"Ggggg.",
		".GgGgG",
		"..G.G.",
	], 5, 4)


@art("archive")
def archive_file():
	grid = page()
	put(grid, 6, 1, ["P1", "2.", "1.", "2.", "1.", "2.", "1.", "2."])
	put(grid, 5, 9, ["FFFF", "Ff^F", "Ff^F", "FFFF"])
	grid[1][6] = "P"
	return grid


@art("font")
def font_file():
	return page_with([
		"..~~..",
		"..~~..",
		".~..~.",
		".~..~.",
		".2222.",
		"~....~",
		"~....~",
	], 5, 5)


@art("rtf")
def rich_text_file():
	return page_with(["GGGG..", "......", "111111", "......", "1111..", "......", "111111", "......", "222..."], 5, 4)


@art("audio")
def audio_file():
	return page_with([
		"..2222",
		"..2222",
		"..2..2",
		"..2..2",
		"222.22",
		"222222",
		"22.22.",
	], 5, 5)


@art("video")
def video_file():
	return page_with([
		"080808",
		"888888",
		"882888",
		"882288",
		"882888",
		"888888",
		"080808",
	], 5, 5)


@art("batch")
def batch_file():
	return page_with([
		"888888",
		"828888",
		"882888",
		"828448",
		"888888",
		"......",
		"...GgG",
		"...g8g",
		"...GgG",
	], 5, 4)


@art("regfile")
def registry_file():
	return page_with([
		"1111..",
		"......",
		"..ff..",
		".fggf.",
		"mmggvv",
		"mMmvVv",
		"mmmvvv",
		".mm.v.",
	], 5, 4)


@art("inifile")
def settings_file():
	return page_with(["11.222", "......", "11.22.", "......", "11.222", "......", "11.22."], 5, 4)


@art("html")
def web_page():
	return page_with([
		"1111..",
		"......",
		".MMMM.",
		"M1m1mM",
		"M1111M",
		"M1m1m2",
		"2MMM2.",
		"..22..",
	], 5, 4)


# ---- Start menu and shell -------------------------------------------------------------------------------------------------------------------------
@art("programs")
def programs():
	return [
		"................",
		".MMMMMM..GGGGGG.",
		".MmmmmM..GggggG.",
		".MmmmmM..GggggG.",
		".MmmmmM..GggggG.",
		".MmmmmM..GggggG.",
		".MMMMMM..GGGGGG.",
		"................",
		"................",
		".MMMMMM..MMMMMM.",
		".MmmmmM..MmmmmM.",
		".MmmmmM..MmmmmM.",
		".MmmmmM..MmmmmM.",
		".MmmmmM..MmmmmM.",
		".MMMMMM..MMMMMM.",
		"................",
	]


@art("settings")
def settings():
	return [
		"................",
		"......GGGG......",
		"..GG..GggG..GG..",
		"..GgGGggggGGgG..",
		"...GggggggggG...",
		".GggggGGGGggggG.",
		".GgggG....GgggG.",
		"GggggG....GggggG",
		"GggggG....GggggG",
		".GgggG....GgggG.",
		".GggggGGGGggggG.",
		"...GggggggggG...",
		"..GgGGggggGGgG..",
		"..GG..GggG..GG..",
		"......GGGG......",
		"................",
	]


@art("help")
def help_badge():
	return [
		"................",
		".....GGGGGG.....",
		"...GGggggggGG...",
		"..Gggg3333gggG..",
		"..Ggg33gg33ggG..",
		".Gggggggg33gggG.",
		".Gggggggg33gggG.",
		".Gggggg333ggggG.",
		".Gggggg33gggggG.",
		".Gggggg33gggggG.",
		".Gggggggggggggg.",
		"..Ggggg33ggggG..",
		"..Ggggg33ggggG..",
		"...GGggggggGG...",
		".....GGGGGG.....",
		"................",
	]


@art("run")
def run():
	grid = blank()
	box(grid, 0, 2, 15, 13, "m")
	for x in range(16):
		grid[2][x] = "D"
		grid[3][x] = "d" if 0 < x < 15 else "D"
		grid[4][x] = "D"
	put(grid, 6, 6, ["G...", "GgG.", "GggG", "GgG.", "G..."])
	return grid


@art("shutdown")
def shut_down():
	return [
		"................",
		".......++.......",
		"...+...++...+...",
		"..++...++...++..",
		".++....++....++.",
		".+.....++.....+.",
		"++.....++.....++",
		"++.....++.....++",
		"++............++",
		"++............++",
		".+............+.",
		".++..........++.",
		"..+++......+++..",
		"...++++++++++...",
		".....++++++.....",
		"................",
	]


@art("logoff")
def log_off():
	return [
		"................",
		".MMMMMMM........",
		".M88888M........",
		".MD8888M........",
		".MdD888M........",
		".MddD88M...G....",
		".MdddD8M...GG...",
		".Mddd2DMGGGGgG..",
		".MddddDMGgggggG.",
		".MddddDMGGGGgG..",
		".MddddDM...GG...",
		".MddddDM...G....",
		".MdddDDM........",
		".MddDMMM........",
		".MMMMM..........",
		"................",
	]


# ---- Control Panel and other plated items ---------------------------------------------------------------------------------------------------------
def plated(block, left=3, top=3):
	return put(plate(), left, top, block)


@art("controlpanel")
def control_panel():
	return plated([
		"MMMMMMMMMM",
		"Mm9mm9m9mM",
		"Mm9mm9GGGM",
		"MGGGm9GGGM",
		"MGGGm9m9mM",
		"Mm9mGGG9mM",
		"Mm9mGGG9mM",
		"Mm9mm9m9mM",
		"Mm9mm9m9mM",
		"MMMMMMMMMM",
	])


@art("access")
def accessibility():
	return plated([
		"....GG....",
		"...GggG...",
		"....GG....",
		"MMMMMMMMMM",
		"MmmmmmmmmM",
		"MMMMmmMMMM",
		"...MmmM...",
		"...MmmM...",
		"..MmMMmM..",
		"..MM..MM..",
	])


@art("addhw")
def add_hardware():
	return plated([
		"..-.-.-...",
		"..-.-.-...",
		"MMMMMMMMM.",
		"MmmmmmmmM-",
		"MmGGGGGmM.",
		"MmGgggGmM-",
		"MmGGGGGmM.",
		"MmmmmmmmM-",
		"MMMMMMMMM.",
		"..-.-.-...",
	], 3, 3)


@art("addremove")
def add_remove_programs():
	return plated([
		"..MMMMM...",
		".MmmmmmM..",
		"Mmm---mmM.",
		"Mm-...-mM.",
		"Mm-...-mM.",
		"Mmm---GGGG",
		".MmmmmGg3G",
		"..MMMGG333",
		".....GGg3G",
		"......GGG.",
	])


@art("admintools")
def administrative_tools():
	return plated([
		"........NN",
		".......NnN",
		"......NnN.",
		".....NnN..",
		"....NnN...",
		"...GGN....",
		"..GggG....",
		".GggG.....",
		"GggG......",
		"GGG.......",
	])


@art("console")
def console():
	return plated([
		"MMMMMMMMMM",
		"M88888888M",
		"M82288448M",
		"M82288888M",
		"M82288488M",
		"M88888888M",
		"MMMMMMMMMM",
	], 3, 4)


@art("datetime")
def date_and_time():
	return plated([
		"GGGGGGGG..",
		"GggggggG..",
		"MMMMMMMM..",
		"M1m1m1mM..",
		"MmmmmmPPPP",
		"M1m1mPpp~P",
		"MmmmmPp~~P",
		"MMMMMPpppP",
		".....PPPPP",
	], 3, 3)


@art("display")
def display():
	return plated([
		"MMMMMMMMMM",
		"M55555555M",
		"M66666666M",
		"M66622666M",
		"M77222277M",
		"MMMMMMMMMM",
		"....NN....",
		"..NNNNNN..",
	], 3, 3)


@art("fonts")
def fonts_applet():
	return plated([
		"...MMMM...",
		"...MmmM...",
		"..MmMMmM..",
		"..MmMMmM..",
		".MmM..MmM.",
		".MmGGGGmM.",
		"MmM....MmM",
		"MMM....MMM",
	], 3, 4)


@art("inetsettings")
def internet_settings():
	return plated([
		"..MMM.....",
		".Mm1mM....",
		"Mmm1mmM...",
		"M11111M...",
		"Mmm1m.GGG.",
		".Mm1.GgggG",
		"..MMMGg8gG",
		".....GgggG",
		"......GGG.",
	], 3, 3)


@art("keyboard")
def keyboard():
	return plated([
		"NNNNNNNNNNNN",
		"Nn0n0n0n0n0N",
		"NnnnnnnnnnnN",
		"N0n0n0n0n0nN",
		"NnnnnnnnnnnN",
		"NnnGGGGGGnnN",
		"NNNNNNNNNNNN",
	], 2, 5)


@art("mouse")
def mouse():
	return plated([
		"..GGMM..",
		".GggmmM.",
		"GggggmmM",
		"Gggg1mmM",
		"M1111111",
		"MmmmmmmM",
		"MmmmmmmM",
		"MmmmmmmM",
		".MmmmmM.",
		"..MMMM..",
	], 4, 3)


@art("netconn")
def network_connections():
	return plated([
		"MMMMMMMM..",
		"Mm8mm8mM..",
		"Mm8mm8mM..",
		"MmmmmmmM..",
		"MMMGGMMM..",
		"...GG.....",
		"...GG.....",
		"...GGGGGG.",
		"....GGGGG.",
	], 4, 3)


@art("power")
def power_options():
	return plated([
		"..MMMMMM..",
		".MmmmGmmM.",
		"MmmmGGmmmM",
		"MmmGGmmmmM",
		"MmGGGGGmmM",
		"MmmmGGmmmM",
		"MmmGGmmmmM",
		"MmmGmmmmmM",
		".MmmmmmmM.",
		"..MMMMMM..",
	])


@art("printers")
def printers():
	return plated([
		"...PPPPP....",
		"...PpppP....",
		"NNNNNNNNNNNN",
		"Nnnnnnnnn22N",
		"NnnnnnnnnnnN",
		"NNNPPPPPPNNN",
		"...Pp11pP...",
		"...PppppP...",
		"...PPPPPP...",
	], 2, 3)


@art("regional")
def regional_options():
	return plated([
		"..VVVVVV..",
		".VvvvvvvV.",
		"V22vvvvvvV",
		"V222vvvvvV",
		"Vv2vvv22vV",
		"Vvvvvv22vV",
		"Vvvvvv2vvV",
		"VvvvvvvvvV",
		".VvvvvvvV.",
		"..VVVVVV..",
	])


@art("sound")
def sound_and_audio():
	return plated([
		"....M.....",
		"...MM...2.",
		"MMMmM.2..2",
		"MmmmM..2.2",
		"MmmmM..2.2",
		"MmmmM..2.2",
		"MMMmM.2..2",
		"...MM...2.",
		"....M.....",
	], 3, 4)


@art("system")
def system():
	return plated([
		"..MMMMMM..",
		"..M8888M..",
		"..MmmmmM..",
		"..M1111M..",
		"..MmmmmM..",
		"..M1111M..",
		"..MmmmmM..",
		"..MmGGmM..",
		"..MmGGmM..",
		"..MMMMMM..",
	])


@art("taskbarstart")
def taskbar_and_start_menu():
	return plated([
		"MMMMMMMMMM",
		"MNNNNmmmmM",
		"MNnnNmmmmM",
		"MNnnNmmmmM",
		"MNNNNmmmmM",
		"M88888888M",
		"MGGG88888M",
		"MMMMMMMMMM",
	], 3, 4)


@art("folderopts")
def folder_options():
	return plated([
		"GGG.......",
		"GggGGGG...",
		"FFFFFFFF..",
		"FffffffF..",
		"FffffffF..",
		"FFFFF.....",
		"......NNN.",
		".....NnnnN",
		".....Nn6nN",
		".....NnnnN",
		"......NNN.",
	], 3, 2)


@art("joystick")
def game_controllers():
	return plated([
		"...GGG....",
		"..GgggG...",
		"..GgggG...",
		"...GGG....",
		"....N.....",
		"....N.....",
		"..MMMMMM..",
		".MmmmmrmM.",
		"MMMMMMMMMM",
	], 3, 3)


@art("telephon")
def phone_and_modem():
	return plated([
		"GGGGGGGGGG",
		"GggggggggG",
		"GgGGGGGGgG",
		"GGGMMMMGGG",
		"..MmmmmmM.",
		".Mm1m1m1mM",
		".MmmmmmmmM",
		"Mm1m1m1mmM",
		"MMMMMMMMMM",
	], 3, 4)


@art("usrmgr")
def user_accounts():
	return plated([
		"......NN..",
		".....NnnN.",
		"..GG.NnnN.",
		".GggG.NN..",
		".GggGNNNN.",
		"..GGNnnnnN",
		".MMMMNnnnN",
		"MmmmmMNNN.",
		"MmmmmmM...",
		"MMMMMMM...",
	])


# ---- tray, dialogs and programs ---------------------------------------------------------------------------------------------------------------------
@art("volume")
def volume():
	return [
		"................",
		"......M.........",
		".....MM.....2...",
		"....MmM..2...2..",
		"MMMMmmM...2..2..",
		"MmmmmmM...2...2.",
		"MmmmmmM...2...2.",
		"MmmmmmM...2...2.",
		"MmmmmmM...2...2.",
		"MMMMmmM...2..2..",
		"....MmM..2...2..",
		".....MM.....2...",
		"......M.........",
		"................",
		"................",
		"................",
	]


@art("volumemute")
def volume_muted():
	grid = [list(row) for row in volume()]
	for y in range(16):
		for x in range(8, 16):
			grid[y][x] = "."
	put(grid, 9, 4, [
		"+....+",
		".+..+.",
		"..++..",
		"..++..",
		".+..+.",
		"+....+",
	])
	return grid


@art("clock")
def clock():
	return [
		"................",
		".....MMMMMM.....",
		"...MMmmmmmmMM...",
		"..Mmmmm1mmmmmM..",
		"..Mmmmm~mmmmmM..",
		".Mmmmmm~mmmmmmM.",
		".Mmmmmm~mmmmmmM.",
		".M1mmmmGG~~~m1M.",
		".MmmmmmGGmmmmmM.",
		".MmmmmmmmmmmmmM.",
		".MmmmmmmmmmmmmM.",
		"..Mmmmmm1mmmmM..",
		"..MmmmmmmmmmmM..",
		"...MMmmmmmmMM...",
		".....MMMMMM.....",
		"................",
	]


@art("kbdlayout")
def keyboard_layout():
	grid = blank()
	box(grid, 0, 3, 15, 12, "n")
	put(grid, 2, 5, ["0.0.0.0.0.0", "...........", ".0.0.0.0.0.", "...........", "..GGGGGGG.."])
	return grid


@art("info")
def information():
	return [
		"................",
		".....VVVVVV.....",
		"...VVvvvvvvVV...",
		"..Vvvvv44vvvvV..",
		"..Vvvvv44vvvvV..",
		".VvvvvvvvvvvvvV.",
		".Vvvvvv44vvvvvV.",
		".Vvvvvv44vvvvvV.",
		".Vvvvvv44vvvvvV.",
		".Vvvvvv44vvvvvV.",
		".Vvvvvv44vvvvvV.",
		"..Vvvvv44vvvvV..",
		"..VvvvvvvvvvvV..",
		"...VVvvvvvvVV...",
		".....VVVVVV.....",
		"................",
	]


@art("question")
def question():
	return [
		"................",
		".VVVVVVVVVVVVVV.",
		".Vvvvv4444vvvvV.",
		".Vvvv44vv44vvvV.",
		".Vvvvvvvv44vvvV.",
		".Vvvvvvv44vvvvV.",
		".Vvvvvv44vvvvvV.",
		".Vvvvvv44vvvvvV.",
		".VvvvvvvvvvvvvV.",
		".Vvvvvv44vvvvvV.",
		".VVVVVvvVVVVVVV.",
		".....VvV........",
		".....VV.........",
		".....V..........",
		"................",
		"................",
	]


@art("cmd")
def command_prompt():
	return plated([
		"MMMMMMMMMM",
		"M88888888M",
		"M82888888M",
		"M88288888M",
		"M82884448M",
		"M88888888M",
		"MMMMMMMMMM",
	], 3, 4)


@art("browser")
def internet_browser():
	return plated([
		"...MMM....",
		"..Mm1mM...",
		".Mmm1mmM.2",
		".M11111M2.",
		".Mmm1mmM2.",
		"..Mm1mM2..",
		"2..MMM2...",
		".22222....",
	], 3, 4)


ORDER = list(ART)


def pixels(icon_id, keyline=False):
	"""The rects of one hand-tuned 16 px frame, row by row; with the keyline, every material edge pixel takes its keyline tone."""
	out = []
	for y, row in enumerate(ART[icon_id]):
		for x, character in enumerate(row):
			if character == ".":
				continue
			if keyline and character in KEYLINE_COLOURS:
				colour = KEYLINE_COLOURS[character]
			else:
				colour = SKY_ROWS[y] if character == "k" else COLOURS[character]
			out.append('<rect x="%d" y="%d" width="1" height="1" fill="%s"/>' % (x, y, colour))
	return "".join(out)


def register(gen):
	"""Build the colour table from set E's materials and details, and add each icon to gen_e.py's hinted list."""
	materials = {"g": "gold", "f": "goldl", "p": "paper", "q": "fold", "m": "front", "n": "back", "d": "dusk", "r": "rose", "v": "violet", "a": "glass"}
	for letter, name in materials.items():
		COLOURS[letter] = gen.MATS[name].base
		COLOURS[letter.upper()] = gen.MATS[name].px_edge()
		KEYLINE_COLOURS[letter.upper()] = gen.retune(gen.MATS[name].px_edge())
	COLOURS.update({digit: colour for digit, colour in gen.PXD.items() if digit != "e"})
	COLOURS.update({"K": gen.HORIZON, "~": gen.HORIZON, "+": gen.RED[200], "*": gen.PURPLE[200], "^": gen.ORANGE[400], "%": gen.INDIGO[300],
		"-": gen.VOIDN[300], "=": gen.VOIDN[500], "#": gen.INDIGO[600]})
	SKY_ROWS[:] = [gen.mix(gen.SKY1, gen.SKY7, max(0, min(1, (y - 1) / 13))) for y in range(16)]
	for icon_id in ORDER:
		if icon_id not in gen.HINTED:
			gen.HINTED.append(icon_id)
