# Releasing

A release is a tag `vX.Y.Z` on `main` whose version matches `package.json`. The Release workflow validates, bundles and attaches every asset to a GitHub release. This page covers the steps and the hand-written release notes. The assets themselves are described in [desktop-release-assets.md](desktop-release-assets.md) and in the README's install sections.

## Steps

1. Run `bun run release:prepare <X.Y.Z>` (or `patch`, `minor` or `major`) on a `chore/release-v<version>` branch. It sets the version in `package.json` and `vscode/package.json`, starts `docs/releases/<version>.md` from the notes shape when there is no file (an existing file is never overwritten), and prints the next steps. It never builds, commits, tags or pushes.
2. Run `bun run build`, which writes the version into the generated Firefox and Chromium manifests, then fill in the notes.
3. Run `bun run format` and `bun run validate`, commit, open a pull request and merge it.
4. Tag the merge commit `vX.Y.Z` and push the tag. Publishing to the VS Code Marketplace or Open VSX is a separate manual step.

## Release notes

Each release can have hand-written notes in `docs/releases/<version>.md`: the tag `vX.Y.Z` reads `docs/releases/X.Y.Z.md`. There is no README or index in that directory. The release workflow uses the file as the start of the release body and appends GitHub's generated list of changes under it. A version without a file gets the generated list only.

The notes keep one shape:

- **A bold lead.** The first line is one bold sentence that says what the release is about, such as `**Afterglow 0.4.0** adds …`.
- **`## Downloads`.** A table of every release asset: the file, what it is for and how to install it in one line. The same section carries the ReactOS desktop notice: the files are unofficial, Afterglow is not affiliated with or endorsed by the ReactOS project, and a file patched from ReactOS stays under ReactOS's own licences (GPL and LGPL) with its notices (see [desktop-release-assets.md](desktop-release-assets.md)).
- **`## What is new`.** A `###` sub-section for each target that changed: OpenCode, VS Code, Midnight Commander, Claude Code, Codex, bat and delta, Forgejo, Firefox, and Chrome and Edge, and the ReactOS desktop and wallpapers. Delete the targets that did not change.
- **`## Fixes`.** What was broken and is not any more.
- **`## Known limits`.** What was not checked or does not work yet, such as unsigned Firefox themes or a theme not yet tried in a real tool.

Write in Canadian English, one unwrapped line per paragraph or bullet.

## The check

`bun run check:release-notes` (part of `bun run validate`, so CI and the release workflow run it) checks every `docs/releases/<version>.md`: it is not empty, it opens with a bold lead sentence, it has the four headings above and it has no placeholder left over from the starting shape (a lone `…` line or a `…` in the lead). A version with no notes file passes.

The release workflow warns when the tag has no notes file, and does not fail. Generated notes alone are a valid release, a failed release is costly to redo (the tag has to move) and the notes can be added to the release afterwards, so a missing file is a nudge, not a gate. A file that exists but breaks the shape does fail, in the validation gate before anything is published.
