#!/usr/bin/env bash
# Rebuild the ReactOS visual style and check it against the committed hash and colour scheme files
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT

# Builds desktop/style into a scratch folder, then compares afterglow.msstyles with desktop/SHA256SUMS
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
	trap 'rm -rf "$out"' EXIT
fi

bash desktop/style/build.sh "$out" >/dev/null

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
	echo "afterglow.msstyles matches desktop/SHA256SUMS"
else
	echo "afterglow.msstyles does not match desktop/SHA256SUMS"
	status=1
fi

[ "$status" -eq 0 ] && echo "Desktop style is reproducible."
exit "$status"
