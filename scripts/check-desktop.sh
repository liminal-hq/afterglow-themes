#!/usr/bin/env bash
# Rebuild the ReactOS visual style and check it against the committed hash and colour scheme files
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT

# Also checks the README pointer preview PNG and the SVG pointer masters against the generator, and draws the pointer set (desktop/pointers/gen-cursors.py, needs Pillow) and compares the 16 files with
# desktop/pointers/SHA256SUMS. With USER32=PATH (a ReactOS 0.4.16 i386 user32.dll, your own copy), it also patches a scratch copy and
# checks the result against the patched hash in desktop/pointers/SHA256SUMS.user32.
#
# Also renders the boot logo (desktop/boot/render.py, needs rsvg-convert and Pillow), compares its two bitmaps with desktop/boot/SHA256SUMS
# and its master and palette with desktop/boot/SHA256SUMS.masters, and checks the docs preview PNG by pixels.
#
# Builds desktop/style twice into scratch folders (the default build, with classic scroll bars, and the --scrollbars build with the
# Afterglow ones), then compares afterglow.msstyles and afterglow-scrollbars.msstyles with desktop/SHA256SUMS
# (the build is reproducible: same sources, same bytes) and each generated .reg file with the one
# committed in desktop/schemes. Needs python3 with numpy, llvm-rc and lld-link. The built style stays
# out of git. Pass a folder to keep the build there; otherwise a temporary one is used and removed.
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root"

for tool in python3 llvm-rc lld-link sha256sum rsvg-convert; do
	command -v "$tool" >/dev/null || { echo "check-desktop: $tool is required" >&2; exit 2; }
done

if [ -n "${1:-}" ]; then
	out=$1
else
	out=$(mktemp -d)
	trap 'rm -rf "$out" "$out-scrollbars"' EXIT
fi

bash desktop/style/build.sh "$out" >/dev/null
bash desktop/style/build.sh "$out-scrollbars" --scrollbars >/dev/null
cp "$out-scrollbars/afterglow.msstyles" "$out/afterglow-scrollbars.msstyles"

status=0
for f in desktop/schemes/*.reg; do
	if ! cmp -s "$f" "$out/schemes/$(basename "$f")"; then
		echo "drift: $f differs from what desktop/style generates"
		status=1
	fi
done
for f in "$out"/schemes/*.reg; do
	[ -f "desktop/schemes/$(basename "$f")" ] || { echo "missing: desktop/schemes/$(basename "$f")"; status=1; }
done

if (cd "$out" && sha256sum --check --quiet "$root/desktop/SHA256SUMS"); then
	echo "afterglow.msstyles and afterglow-scrollbars.msstyles match desktop/SHA256SUMS"
else
	echo "afterglow.msstyles or afterglow-scrollbars.msstyles does not match desktop/SHA256SUMS"
	status=1
fi

python3 desktop/pointers/gen-cursors.py "$out/pointers" >/dev/null
if (cd "$out/pointers" && sha256sum --check --quiet "$root/desktop/pointers/SHA256SUMS"); then
	echo "the 16 Afterglow pointers match desktop/pointers/SHA256SUMS"
else
	echo "the Afterglow pointers do not match desktop/pointers/SHA256SUMS"
	status=1
fi
python3 desktop/pointers/gen-cursors.py "$out/pointers-scratch" --svg "$out/pointers-svg" >/dev/null
if diff -r "$out/pointers-svg" desktop/pointers/svg >/dev/null; then
	echo "the SVG pointer masters in desktop/pointers/svg match the generator"
else
	echo "the SVG pointer masters in desktop/pointers/svg are out of date: run desktop/pointers/gen-cursors.py OUT_DIR --svg desktop/pointers/svg"
	status=1
fi
python3 desktop/pointers/render-preview.py "$out/pointers-preview.png"
# Compared by pixels, not bytes: PNG encoders differ between Pillow and zlib builds.
if python3 - "$out/pointers-preview.png" docs/images/afterglow-pointers.png <<'PY'
import sys
from PIL import Image, ImageChops
fresh, committed = (Image.open(path).convert("RGB") for path in sys.argv[1:3])
sys.exit(0 if fresh.size == committed.size and ImageChops.difference(fresh, committed).getbbox() is None else 1)
PY
then
	echo "the pointer preview docs/images/afterglow-pointers.png matches the generator"
else
	echo "the pointer preview docs/images/afterglow-pointers.png is out of date: run desktop/pointers/render-preview.py docs/images/afterglow-pointers.png"
	status=1
fi
if [ -n "${USER32:-}" ]; then
	if python3 desktop/pointers/patch-user32.py "$USER32" "$out/pointers" "$out/user32-afterglow.dll" >/dev/null; then
		if (cd "$out" && sha256sum --check --quiet "$root/desktop/pointers/SHA256SUMS.user32"); then
			echo "the patched user32.dll matches desktop/pointers/SHA256SUMS.user32"
		else
			echo "the patched user32.dll does not match desktop/pointers/SHA256SUMS.user32"
			status=1
		fi
	else
		echo "patch-user32.py refused or failed on $USER32"
		status=1
	fi
fi

# The boot logo: the master and palette are hashed as they are, and the 4-bit and RLE4 bitmaps are rendered fresh and hashed.
if (cd desktop/boot && sha256sum --check --quiet SHA256SUMS.masters); then
	echo "the boot logo master and palette in desktop/boot match desktop/boot/SHA256SUMS.masters"
else
	echo "the boot logo master or palette changed: if that is intended, run (cd desktop/boot && sha256sum boot-logo.svg palette.json > SHA256SUMS.masters) and render the bitmaps again"
	status=1
fi
python3 desktop/boot/render.py "$out/boot" >/dev/null
if (cd "$out/boot" && sha256sum --check --quiet "$root/desktop/boot/SHA256SUMS"); then
	echo "the boot logo bitmaps match desktop/boot/SHA256SUMS"
else
	echo "a boot logo bitmap does not match desktop/boot/SHA256SUMS: the master or the renderer changed, so look at $out/boot, then record the new hashes with (cd OUT_DIR && sha256sum afterglow-logo-4bit.bmp afterglow-logo-rle4.bmp > desktop/boot/SHA256SUMS)"
	status=1
fi
if python3 - "$out/boot/afterglow-logo-2x.png" docs/images/afterglow-boot-logo.png <<'PY'
import sys
from PIL import Image, ImageChops
fresh, committed = (Image.open(path).convert("RGB") for path in sys.argv[1:3])
sys.exit(0 if fresh.size == committed.size and ImageChops.difference(fresh, committed).getbbox() is None else 1)
PY
then
	echo "the boot logo preview docs/images/afterglow-boot-logo.png matches the renderer"
else
	echo "the boot logo preview docs/images/afterglow-boot-logo.png is out of date: copy afterglow-logo-2x.png from desktop/boot/render.py's output over it"
	status=1
fi

[ "$status" -eq 0 ] && echo "Desktop style and pointers are reproducible."
exit "$status"
