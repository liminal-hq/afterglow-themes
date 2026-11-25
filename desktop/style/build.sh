#!/usr/bin/env bash
# Build the Afterglow ReactOS visual style (eight colour schemes, one size): draw the bitmaps and write the INI and resource script
# (gen.py), compile the resources with llvm-rc and link a resource-only x86 DLL with lld-link (/Brepro: no timestamp, so the same
# sources give the same bytes). No other visual style is read or fetched.
# Usage: build.sh OUT_DIR [--schemes] [--scrollbars]   (the result is OUT_DIR/afterglow.msstyles; --schemes also refreshes
# desktop/schemes/*.reg; --scrollbars themes the scroll bars too, otherwise they stay the shell's own classic ones)
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT
set -eu
here=$(cd "$(dirname "$0")" && pwd)
B=${1:?usage: build.sh OUT_DIR [--schemes] [--scrollbars]}
shift
schemes= scrollbars=
for a in "$@"; do
	case "$a" in
	--schemes) schemes=1 ;;
	--scrollbars) scrollbars=--scrollbars ;;
	*) echo "build.sh: unknown option $a" >&2; exit 2 ;;
	esac
done
rm -rf "$B"
mkdir -p "$B"
python3 "$here/gen.py" "$B" ${PREVIEW:+--preview "$PREVIEW"} $scrollbars
(
	cd "$B"
	llvm-rc /FO afterglow.res afterglow.rc
	lld-link /dll /noentry /machine:x86 /nodefaultlib /Brepro /out:afterglow.msstyles afterglow.res
)
ls -l "$B/afterglow.msstyles"
sha256sum "$B/afterglow.msstyles"
if [ -n "$schemes" ]; then
	for f in "$B"/schemes/*.reg; do cp "$f" "$here/../schemes/"; done
fi
