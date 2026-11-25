#!/usr/bin/env bash
# Rebuild the ReactOS visual style and check it against the committed hash and colour scheme files
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT

# Also checks the pointer preview PNGs in docs/images against the generator, and draws the pointer set (desktop/pointers/gen-cursors.py, needs Pillow) and compares the 16 files with
# desktop/pointers/SHA256SUMS. With USER32=PATH (a ReactOS 0.4.16 i386 user32.dll, your own copy), it also patches a scratch copy and
# checks the result against the patched hash in desktop/pointers/SHA256SUMS.user32.
#
# Builds desktop/style twice into scratch folders (the default build, with classic scroll bars, and the --scrollbars build with the
# Afterglow ones), then compares afterglow.msstyles and afterglow-scrollbars.msstyles with desktop/SHA256SUMS
# (the build is reproducible: same sources, same bytes) and each generated .reg file with the one
# committed in desktop/schemes. Needs python3 with numpy, llvm-rc and lld-link. The built style stays
# out of git. Pass a folder to keep the build there; otherwise a temporary one is used and removed.
set -euo pipefail

root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$root"

for tool in python3 llvm-rc lld-link sha256sum; do
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
python3 desktop/pointers/render-preview.py "$out/preview"
# Compared by pixels (RGBA), not bytes: PNG encoders differ between Pillow and zlib builds.
if python3 - "$out/preview" docs/images <<'PY'
import os, sys
from PIL import Image, ImageChops
fresh_root, committed_root = sys.argv[1:3]
fresh_files = sorted(os.path.relpath(os.path.join(d, f), fresh_root) for d, _, fs in os.walk(fresh_root) for f in fs)
committed_files = sorted(os.path.relpath(os.path.join(d, f), committed_root) for d, _, fs in os.walk(committed_root) for f in fs)
bad = [f"unexpected or missing files: {sorted(set(fresh_files) ^ set(committed_files))}"] if fresh_files != committed_files else []
for name in set(fresh_files) & set(committed_files):
	fresh, committed = (Image.open(os.path.join(root, name)).convert("RGBA") for root in (fresh_root, committed_root))
	if fresh.size != committed.size or ImageChops.difference(fresh, committed).getbbox() is not None:
		bad.append(f"{name} differs")
for line in bad:
	print(line)
sys.exit(1 if bad else 0)
PY
then
	echo "the pointer previews in docs/images match the generator"
else
	echo "the pointer previews in docs/images are out of date: run desktop/pointers/render-preview.py docs/images"
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

[ "$status" -eq 0 ] && echo "Desktop style and pointers are reproducible."
exit "$status"
