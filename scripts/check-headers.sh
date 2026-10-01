#!/usr/bin/env bash
# Check every source file has the licence header AGENTS.md requires
#
# (c) Copyright 2026 Liminal HQ, Scott Morris
# SPDX-License-Identifier: Apache-2.0 OR MIT

# Exits 1 and lists offenders if any file is missing an SPDX-License-Identifier line within its
# first few lines; 0 if clean.
set -euo pipefail

cd "$(git rev-parse --show-toplevel 2>/dev/null || dirname "$(dirname "${BASH_SOURCE[0]}")")"

missing=()

while IFS= read -r -d '' f; do
  if ! head -8 "$f" | grep -q "SPDX-License-Identifier"; then
    missing+=("$f")
  # The header is a one-line purpose summary, a blank comment line, then the copyright block, so a
  # file starting directly on "(c) Copyright" skipped the summary.
  elif head -1 "$f" | grep -q "(c) Copyright"; then
    missing+=("$f (missing its purpose summary before the copyright line)")
  fi
done < <(find scripts \( -name "*.mjs" -o -name "*.sh" \) -print0)

if [ "${#missing[@]}" -gt 0 ]; then
  echo "Missing licence header (see AGENTS.md 'Licence and Copyright'):"
  for f in "${missing[@]}"; do
    echo "  $f"
  done
  echo
  echo "${#missing[@]} file(s) missing a header."
  exit 1
fi

echo "All source files have licence headers."
