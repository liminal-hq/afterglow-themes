// Prepare a release: set the version everywhere it is written and start the release notes
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

// usage: node scripts/release-prepare.mjs <X.Y.Z | patch | minor | major>
//
// package.json is the source of truth for the version and the release tag must equal it. This
// writes the version into package.json and vscode/package.json, starts docs/releases/<version>.md
// from the notes shape when there is no file (an existing one is never overwritten), and prints
// the steps that follow. It never builds, commits, tags or pushes.

import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

// Every file that writes the version. The browser manifests carry it too, but they are generated,
// so `bun run build` rewrites them.
export const versionFiles = ['package.json', 'vscode/package.json'];

const versionPattern = /^(\d+)\.(\d+)\.(\d+)$/;

export function nextVersion(current, want) {
	const match = versionPattern.exec(current);
	if (!match) throw new Error(`package.json has version "${current}", which is not X.Y.Z`);
	const [major, minor, patch] = match.slice(1).map(Number);
	if (want === 'patch') return `${major}.${minor}.${patch + 1}`;
	if (want === 'minor') return `${major}.${minor + 1}.0`;
	if (want === 'major') return `${major + 1}.0.0`;
	if (!versionPattern.test(want)) {
		throw new Error(`"${want}" is not X.Y.Z, patch, minor or major`);
	}
	return want;
}

// Replace the top-level "version" in a package.json text without touching its formatting
export function setVersion(text, version) {
	const pattern = /^(\t"version": ")[^"]*(",?)$/m;
	if (!pattern.test(text)) throw new Error('no top-level "version" line found');
	return text.replace(pattern, `$1${version}$2`);
}

// The starting point for a version's notes, with the release assets as bundle.mjs names them
export function notesTemplate(version) {
	const v = `v${version}`;
	return `**Afterglow ${version}** is … (one sentence on what the release is about).

## Downloads

Every file is on this page, and \`SHA256SUMS\` covers all of them.

| File | For | Install |
| --- | --- | --- |
| \`afterglow-themes-${v}.zip\` (and the loose \`.json\` files) | OpenCode | \`unzip afterglow-themes-v*.zip -d ~/.config/opencode/themes\`, then \`/themes\` |
| \`afterglow-vscode-${v}.vsix\` | VS Code | \`code --install-extension afterglow-vscode-v*.vsix\` |
| \`afterglow-mc-skins-${v}.zip\` | Midnight Commander | unzip into \`~/.local/share/mc/skins\`, then \`mc -S afterglow\` |
| \`afterglow-claude-code-themes-${v}.zip\` | Claude Code | unzip the \`.json\` files into \`~/.claude/themes\`, then \`/theme\` |
| \`afterglow-tmthemes-${v}.zip\` | Codex, bat and delta | unzip the \`.tmTheme\` files into \`~/.codex/themes\` (bat: its \`themes\` directory, then \`bat cache --build\`) |
| \`afterglow-forgejo-${v}.zip\` | Forgejo | copy the \`.css\` files into \`public/assets/css\`, then list the themes in \`app.ini\` |
| \`<theme>-firefox-${v}.xpi\` | Firefox | load temporarily from \`about:debugging\`; the themes are unsigned |
| \`afterglow-chromium-themes-${v}.zip\` | Chrome and Edge | unzip, then **Load unpacked** on \`chrome://extensions\` |
| \`afterglow-wallpapers-${v}.zip\` | Desktop backgrounds | unzip and set an SVG as the wallpaper |
| \`afterglow-reactos-desktop-${v}.zip\` | ReactOS desktop | unzip and follow its \`README.md\` |
| \`SHA256SUMS\` | Checking downloads | \`sha256sum -c SHA256SUMS --ignore-missing\` |

**ReactOS desktop notice.** The ReactOS desktop files are unofficial: Afterglow is not affiliated with or endorsed by the ReactOS project. A file patched from ReactOS stays under ReactOS's own licences (GPL and LGPL), and the notices come with it. See [docs/desktop-release-assets.md](https://github.com/liminal-hq/afterglow-themes/blob/${v}/docs/desktop-release-assets.md).

## What is new

Keep a sub-section for each target that changed and delete the rest.

### OpenCode

- …

### VS Code

- …

### Midnight Commander

- …

### Claude Code

- …

### Codex, bat and delta

- …

### Forgejo, Firefox, and Chrome and Edge

- …

### ReactOS desktop and wallpapers

- …

## Fixes

- …

## Known limits

- …
`;
}

// Do the work in a directory; returns the lines to print, so tests can run it in a scratch copy
export function prepare(dir, want) {
	const pkgPath = join(dir, 'package.json');
	const current = JSON.parse(readFileSync(pkgPath, 'utf8')).version;
	const next = nextVersion(current, want);
	const lines = [`${current} -> ${next}`];

	for (const file of versionFiles) {
		const path = join(dir, file);
		const text = readFileSync(path, 'utf8');
		const updated = setVersion(text, next);
		if (updated !== text) writeFileSync(path, updated);
	}

	const notes = join(dir, 'docs', 'releases', `${next}.md`);
	if (existsSync(notes)) {
		lines.push(`Kept docs/releases/${next}.md`);
	} else {
		mkdirSync(dirname(notes), { recursive: true });
		writeFileSync(notes, notesTemplate(next));
		lines.push(`Started docs/releases/${next}.md; fill it in before tagging.`);
	}

	lines.push(
		'',
		'Next:',
		`  1. Fill in docs/releases/${next}.md (a lone … line fails the check until it is filled or deleted).`,
		'  2. Run: bun run build && bun run format && bun run validate',
		`  3. Commit on a branch (git switch -c chore/release-v${next}), open a pull request and merge it.`,
		`  4. When asked to release: git tag -s v${next} -m "Afterglow ${next}" && git push origin v${next}`,
	);
	return lines;
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
	const want = process.argv[2];
	if (!want || process.argv.length > 3) {
		console.error('usage: bun run release:prepare <X.Y.Z | patch | minor | major>');
		process.exit(2);
	}
	try {
		console.log(prepare(root, want).join('\n'));
	} catch (error) {
		console.error(error.message);
		process.exit(1);
	}
}
