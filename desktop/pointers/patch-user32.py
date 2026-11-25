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


def align_up(value, alignment):
	return (value + alignment - 1) // alignment * alignment


def read_cur(path):
	"""The single 32 x 32 image of a .cur file: (hotspot, image bytes, bit count)."""
	with open(path, "rb") as cur_file:
		data = cur_file.read()
	_, kind, count = struct.unpack_from("<HHH", data, 0)
	assert kind == 2 and count == 1, path
	_, _, _, _, hotspot_x, hotspot_y, size, offset = struct.unpack_from("<BBBBHHII", data, 6)
	image = data[offset : offset + size]
	bit_count = struct.unpack_from("<H", image, 14)[0]
	return (hotspot_x, hotspot_y), image, bit_count


def main():
	if len(sys.argv) != 4:
		print("usage: patch-user32.py USER32_IN CURSOR_DIR USER32_OUT", file=sys.stderr)
		sys.exit(2)
	source_path, cursor_dir, output_path = sys.argv[1:]
	if os.path.abspath(source_path) == os.path.abspath(output_path):
		print("patch-user32: the output must be a different file from the input (work on a copy)", file=sys.stderr)
		sys.exit(2)
	with open(source_path, "rb") as source_file:
		pe_bytes = bytearray(source_file.read())
	if len(pe_bytes) != EXPECTED_SIZE or hashlib.sha256(pe_bytes).hexdigest() != EXPECTED_SHA256:
		# An already patched copy is told apart so a caller can skip it.
		if pe_bytes[:2] == b"MZ" and b".agcur" in bytes(pe_bytes[: struct.unpack_from("<I", pe_bytes, 0x3C)[0] + 1024]):
			print("already patched (has an .agcur section); nothing written")
			sys.exit(3)
		print(
			"refusing: %s is not the user32.dll of ReactOS 0.4.16 i386 (expected %d bytes, SHA-256 %s; got %d bytes, %s)"
			% (source_path, EXPECTED_SIZE, EXPECTED_SHA256, len(pe_bytes), hashlib.sha256(pe_bytes).hexdigest()),
			file=sys.stderr,
		)
		sys.exit(4)
	pe_offset = struct.unpack_from("<I", pe_bytes, 0x3C)[0]
	section_count = struct.unpack_from("<H", pe_bytes, pe_offset + 6)[0]
	optional_header_size = struct.unpack_from("<H", pe_bytes, pe_offset + 20)[0]
	optional_header = pe_offset + 24
	assert struct.unpack_from("<H", pe_bytes, optional_header)[0] == 0x10B, "PE32 expected"
	section_alignment, file_alignment = struct.unpack_from("<II", pe_bytes, optional_header + 32)
	size_of_headers = struct.unpack_from("<I", pe_bytes, optional_header + 60)[0]
	section_table = optional_header + optional_header_size
	# Each section is (name, virtual size, virtual address, raw size, raw offset).
	sections = [struct.unpack_from("<8sIIII", pe_bytes, section_table + 40 * i) for i in range(section_count)]
	if section_table + 40 * (section_count + 1) > size_of_headers:
		sys.exit("no room for another section header")
	rsrc_rva = struct.unpack_from("<I", pe_bytes, optional_header + 96 + 8 * 2)[0]
	rsrc_section = next(section for section in sections if section[2] <= rsrc_rva < section[2] + max(section[1], section[3]))
	rsrc_raw = rsrc_section[4] + (rsrc_rva - rsrc_section[2])

	def directory_entries(directory_offset):
		"""The (name or id, target) pairs of one resource directory."""
		named_count, id_count = struct.unpack_from("<HH", pe_bytes, rsrc_raw + directory_offset + 12)
		for i in range(named_count + id_count):
			name, target = struct.unpack_from("<II", pe_bytes, rsrc_raw + directory_offset + 16 + 8 * i)
			yield name, target

	def data_entries(type_id):
		"""id -> file offset of the first language's IMAGE_RESOURCE_DATA_ENTRY."""
		offsets = {}
		for name, type_target in directory_entries(0):
			if name == type_id:
				for resource_id, id_target in directory_entries(type_target & 0x7FFFFFFF):
					if resource_id & 0x80000000:
						continue
					for _, language_target in directory_entries(id_target & 0x7FFFFFFF):
						offsets[resource_id] = rsrc_raw + (language_target & 0x7FFFFFFF)
						break
		return offsets

	group_entries = data_entries(RT_GROUP_CURSOR)
	cursor_entries = data_entries(RT_CURSOR)
	last_section = sections[-1]
	new_rva = align_up(last_section[2] + max(last_section[1], last_section[3]), section_alignment)
	new_raw = align_up(len(pe_bytes), file_alignment)
	# The first cursor of each group, read before anything is moved.
	first_cursor_ids = {}
	for group_ids in GROUPS.values():
		for group_id in group_ids:
			if group_id in group_entries:
				group_rva = struct.unpack_from("<I", pe_bytes, group_entries[group_id])[0]
				group_raw = next(section[4] + (group_rva - section[2]) for section in sections if section[2] <= group_rva < section[2] + max(section[1], section[3]))
				first_cursor_ids[group_id] = struct.unpack_from("<H", pe_bytes, group_raw + 6 + 12)[0]
	new_section = bytearray()
	patched = []
	for name, group_ids in GROUPS.items():
		hotspot, image, bit_count = read_cur(os.path.join(cursor_dir, f"afterglow-{name}.cur"))
		cursor_resource = struct.pack("<HH", *hotspot) + image
		cursor_offset = len(new_section)  # one copy of the image, shared by both group ids
		new_section += cursor_resource + bytes(align_up(len(cursor_resource), 8) - len(cursor_resource))
		for group_id in group_ids:
			if group_id not in group_entries:
				continue
			group_entry = group_entries[group_id]
			first_cursor_id = first_cursor_ids[group_id]
			cursor_entry = cursor_entries[first_cursor_id]
			# new one-entry group: CURSORDIR entry (width, height*2, planes, bit count, bytes, id)
			group_resource = struct.pack("<HHH", 0, 2, 1) + struct.pack("<HHHHIH", 32, 64, 1, bit_count, len(cursor_resource), first_cursor_id)
			group_offset = len(new_section)
			new_section += group_resource + bytes(align_up(len(group_resource), 8) - len(group_resource))
			struct.pack_into("<II", pe_bytes, cursor_entry, new_rva + cursor_offset, len(cursor_resource))
			struct.pack_into("<II", pe_bytes, group_entry, new_rva + group_offset, len(group_resource))
			patched.append((name, group_id, first_cursor_id))
	raw_size = align_up(len(new_section), file_alignment)
	pe_bytes += bytes(new_raw - len(pe_bytes))
	pe_bytes += new_section + bytes(raw_size - len(new_section))
	section_header = struct.pack("<8sIIIIIIHHI", b".agcur", len(new_section), new_rva, raw_size, new_raw, 0, 0, 0, 0, 0x40000040)
	pe_bytes[section_table + 40 * section_count : section_table + 40 * section_count + 40] = section_header
	struct.pack_into("<H", pe_bytes, pe_offset + 6, section_count + 1)
	struct.pack_into("<I", pe_bytes, optional_header + 56, align_up(new_rva + len(new_section), section_alignment))  # SizeOfImage
	# PE checksum: the sum of the 16-bit words with the carry folded back in, plus the file length
	struct.pack_into("<I", pe_bytes, optional_header + 64, 0)
	checksum = 0
	for i in range(0, len(pe_bytes) - (len(pe_bytes) & 1), 2):
		checksum += pe_bytes[i] | (pe_bytes[i + 1] << 8)
		checksum = (checksum & 0xFFFF) + (checksum >> 16)
	checksum = (checksum & 0xFFFF) + (checksum >> 16)
	struct.pack_into("<I", pe_bytes, optional_header + 64, (checksum & 0xFFFF) + len(pe_bytes))
	with open(output_path, "wb") as output_file:
		output_file.write(bytes(pe_bytes))
	print(f"patched {len(patched)} cursor groups; new section {len(new_section)} bytes at RVA {new_rva:#x}")
	for entry in patched:
		print("  %-10s group %5d -> cursor %d" % entry)


if __name__ == "__main__":
	main()
