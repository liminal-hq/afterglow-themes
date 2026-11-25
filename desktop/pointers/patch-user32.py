#!/usr/bin/env python3
# Make the Afterglow pointers the system pointers of a ReactOS 0.4.16 guest by replacing the cursor resources in a COPY of user32.dll.
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
#
# Why: ReactOS 0.4.16 never reads the pointer scheme in HKCU\Control Panel\Cursors (user32's User32SetupDefaultCursors
# has "FIXME load system cursor scheme", SPI_SETCURSORS is unimplemented and SetSystemCursor cannot replace a loaded cursor), so
# the system pointers always come from user32.dll's own RT_GROUP_CURSOR resources at boot.
#
# How: the new cursor images go into a new section appended to the file; each pointer's RT_GROUP_CURSOR resource is pointed at
# a new one-entry group, and that entry's RT_CURSOR resource at the new image. Nothing else in the file moves. The PE checksum is
# recomputed.
#
# Safety: this is a tool, not a patched binary. It reads a COPY of user32.dll that the caller supplies, never edits it in place and
# writes a separate output file. It only accepts the user32.dll of ReactOS 0.4.16 for i386 (1,604,096 bytes, SHA-256 below, as found
# in the 0.4.16 install ISO and in a fresh install); any other build (another version, architecture or an already patched file)
# is refused, because the section layout and cursor ids were checked against that one file only. A patched user32.dll is ReactOS
# code (LGPL-2.1) with Afterglow pointers added: do not publish or redistribute it, patch your own copy on your own demo disk.
# Usage: patch-user32.py USER32_IN CURSOR_DIR USER32_OUT
# Exit codes: 0 patched; 2 usage; 3 the input is already patched; 4 the input is not the expected user32.dll
import hashlib
import os
import struct
import sys

EXPECTED_SIZE = 1604096
EXPECTED_SHA256 = "8ddd64afb96b576f899e3d73ea3a44355474f6c74a3ccd3ff75caa696b711958"

RT_CURSOR, RT_GROUP_CURSOR = 1, 12
# Group resource ids (the OCR_* values, and the numbered copies user32.rc also carries) -> cursor file.
GROUPS = {
	"arrow": (32512, 100),
	"ibeam": (32513, 101),
	"busy": (32514, 102),
	"cross": (32515, 103),
	"up": (32516, 104),
	"size-nwse": (32642, 105),
	"size-nesw": (32643, 106),
	"size-we": (32644, 107),
	"size-ns": (32645, 108),
	"move": (32646, 109),
	"no": (32648, 110),
	"working": (32650, 111),
	"help": (32651, 112),
	"hand": (32649, 114),
}


def align(v, a):
	return (v + a - 1) // a * a


def read_cur(path):
	"""The single 32 x 32 image of a .cur file: (hotspot, image bytes, bit count)."""
	d = open(path, "rb").read()
	reserved, typ, count = struct.unpack_from("<HHH", d, 0)
	assert typ == 2 and count == 1, path
	w, h, _, _, hx, hy, size, off = struct.unpack_from("<BBBBHHII", d, 6)
	img = d[off : off + size]
	bpp = struct.unpack_from("<H", img, 14)[0]
	return (hx, hy), img, bpp


def main():
	if len(sys.argv) != 4:
		print("usage: patch-user32.py USER32_IN CURSOR_DIR USER32_OUT", file=sys.stderr)
		sys.exit(2)
	src, curdir, dst = sys.argv[1:]
	if os.path.abspath(src) == os.path.abspath(dst):
		print("patch-user32: the output must be a different file from the input (work on a copy)", file=sys.stderr)
		sys.exit(2)
	b = bytearray(open(src, "rb").read())
	if len(b) != EXPECTED_SIZE or hashlib.sha256(b).hexdigest() != EXPECTED_SHA256:
		# An already patched copy is told apart so a caller can skip it.
		if b[:2] == b"MZ" and b".agcur" in bytes(b[: struct.unpack_from("<I", b, 0x3C)[0] + 1024]):
			print("already patched (has an .agcur section); nothing written")
			sys.exit(3)
		print(
			"refusing: %s is not the user32.dll of ReactOS 0.4.16 i386 (expected %d bytes, SHA-256 %s; got %d bytes, %s)"
			% (src, EXPECTED_SIZE, EXPECTED_SHA256, len(b), hashlib.sha256(b).hexdigest()),
			file=sys.stderr,
		)
		sys.exit(4)
	pe = struct.unpack_from("<I", b, 0x3C)[0]
	nsec = struct.unpack_from("<H", b, pe + 6)[0]
	optsz = struct.unpack_from("<H", b, pe + 20)[0]
	opt = pe + 24
	assert struct.unpack_from("<H", b, opt)[0] == 0x10B, "PE32 expected"
	salign, falign = struct.unpack_from("<II", b, opt + 32)
	soh = struct.unpack_from("<I", b, opt + 60)[0]
	st = opt + optsz
	secs = [struct.unpack_from("<8sIIII", b, st + 40 * i) for i in range(nsec)]
	if st + 40 * (nsec + 1) > soh:
		sys.exit("no room for another section header")
	rsrc_rva = struct.unpack_from("<I", b, opt + 96 + 8 * 2)[0]
	rs = next(s for s in secs if s[2] <= rsrc_rva < s[2] + max(s[1], s[3]))
	rsrc_raw = rs[4] + (rsrc_rva - rs[2])

	def entries(dir_off):
		named, ids = struct.unpack_from("<HH", b, rsrc_raw + dir_off + 12)
		for i in range(named + ids):
			name, target = struct.unpack_from("<II", b, rsrc_raw + dir_off + 16 + 8 * i)
			yield name, target

	def data_entries(type_id):
		"""id -> file offset of the first language's IMAGE_RESOURCE_DATA_ENTRY."""
		out = {}
		for name, target in entries(0):
			if name == type_id:
				for rid, t2 in entries(target & 0x7FFFFFFF):
					if rid & 0x80000000:
						continue
					for _, t3 in entries(t2 & 0x7FFFFFFF):
						out[rid] = rsrc_raw + (t3 & 0x7FFFFFFF)
						break
		return out

	groups = data_entries(RT_GROUP_CURSOR)
	cursors = data_entries(RT_CURSOR)
	last = secs[-1]
	new_rva = align(last[2] + max(last[1], last[3]), salign)
	new_raw = align(len(b), falign)
	# The first cursor of each group, read before anything is moved.
	firsts = {}
	for ids in GROUPS.values():
		for gid in ids:
			if gid in groups:
				g_rva = struct.unpack_from("<I", b, groups[gid])[0]
				g_raw = next(s[4] + (g_rva - s[2]) for s in secs if s[2] <= g_rva < s[2] + max(s[1], s[3]))
				firsts[gid] = struct.unpack_from("<H", b, g_raw + 6 + 12)[0]
	blob = bytearray()
	patched = []
	for name, ids in GROUPS.items():
		hot, img, bpp = read_cur(os.path.join(curdir, f"afterglow-{name}.cur"))
		cur = struct.pack("<HH", *hot) + img
		c_off = len(blob)  # one copy of the image, shared by both group ids
		blob += cur + bytes(align(len(cur), 8) - len(cur))
		for gid in ids:
			if gid not in groups:
				continue
			gde = groups[gid]
			first_id = firsts[gid]
			cde = cursors[first_id]
			# new one-entry group: CURSORDIR entry (width, height*2, planes, bit count, bytes, id)
			grp = struct.pack("<HHH", 0, 2, 1) + struct.pack("<HHHHIH", 32, 64, 1, bpp, len(cur), first_id)
			g_off = len(blob)
			blob += grp + bytes(align(len(grp), 8) - len(grp))
			struct.pack_into("<II", b, cde, new_rva + c_off, len(cur))
			struct.pack_into("<II", b, gde, new_rva + g_off, len(grp))
			patched.append((name, gid, first_id))
	raw_size = align(len(blob), falign)
	b += bytes(new_raw - len(b))
	b += blob + bytes(raw_size - len(blob))
	hdr = struct.pack("<8sIIIIIIHHI", b".agcur", len(blob), new_rva, raw_size, new_raw, 0, 0, 0, 0, 0x40000040)
	b[st + 40 * nsec : st + 40 * nsec + 40] = hdr
	struct.pack_into("<H", b, pe + 6, nsec + 1)
	struct.pack_into("<I", b, opt + 56, align(new_rva + len(blob), salign))  # SizeOfImage
	# PE checksum
	struct.pack_into("<I", b, opt + 64, 0)
	csum = 0
	for i in range(0, len(b) - (len(b) & 1), 2):
		csum += b[i] | (b[i + 1] << 8)
		csum = (csum & 0xFFFF) + (csum >> 16)
	csum = (csum & 0xFFFF) + (csum >> 16)
	struct.pack_into("<I", b, opt + 64, (csum & 0xFFFF) + len(b))
	open(dst, "wb").write(bytes(b))
	print(f"patched {len(patched)} cursor groups; new section {len(blob)} bytes at RVA {new_rva:#x}")
	for p in patched:
		print("  %-10s group %5d -> cursor %d" % p)


if __name__ == "__main__":
	main()
