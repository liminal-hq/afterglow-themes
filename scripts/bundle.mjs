// Package the themes into release assets: the JSON files, zip bundles, the .vsix, and SHA256SUMS
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import {
	copyFileSync,
	cpSync,
	existsSync,
	mkdirSync,
	readFileSync,
	readdirSync,
	rmSync,
	writeFileSync,
} from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const out = join(root, 'dist', 'release');
const { version } = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
const themes = readdirSync(join(root, 'themes')).filter((f) => f.endsWith('.json'));

if (!themes.length) throw new Error('No themes found. Run `bun run build` first.');

rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });

for (const file of themes) copyFileSync(join(root, 'themes', file), join(out, file));

const bundle = `afterglow-themes-v${version}.zip`;
execFileSync('zip', ['-q', '-j', join(out, bundle), ...themes.map((f) => join(out, f))]);

// Stage the VS Code extension with only what ships, then package it as a .vsix
if (!existsSync(join(root, 'vscode', 'themes'))) {
	throw new Error('No VS Code themes found. Run `bun run build` first.');
}
const stage = join(root, 'dist', 'vscode-extension');
rmSync(stage, { recursive: true, force: true });
mkdirSync(join(stage, 'upstream'), { recursive: true });
for (const entry of ['package.json', 'README.md', '.vscodeignore', 'images', 'themes']) {
	cpSync(join(root, 'vscode', entry), join(stage, entry), { recursive: true });
}
copyFileSync(join(root, 'vscode', 'upstream', 'NOTICE.md'), join(stage, 'upstream', 'NOTICE.md'));
for (const licence of ['LICENSE-APACHE', 'LICENSE-MIT']) {
	copyFileSync(join(root, licence), join(stage, licence));
}
execFileSync(
	process.execPath,
	[
		join(root, 'node_modules', '@vscode', 'vsce', 'vsce'),
		'package',
		'--no-dependencies',
		'--skip-license',
		'--out',
		join(out, `afterglow-vscode-v${version}.vsix`),
	],
	{ cwd: stage, stdio: 'inherit' },
);

// The Midnight Commander skins ship as their own zip, unpacked straight into mc's skins directory
const skins = readdirSync(join(root, 'mc', 'skins')).filter((f) => f.endsWith('.ini'));
if (!skins.length) throw new Error('No Midnight Commander skins found. Run `bun run build` first.');
execFileSync('zip', [
	'-q',
	'-j',
	join(out, `afterglow-mc-skins-v${version}.zip`),
	...skins.map((f) => join(root, 'mc', 'skins', f)),
	join(root, 'LICENSE-APACHE'),
	join(root, 'LICENSE-MIT'),
]);

// The Claude Code themes ship as a zip to unpack into the Claude Code config directory's themes folder
const claudeThemes = readdirSync(join(root, 'claude', 'themes')).filter((f) => f.endsWith('.json'));
if (!claudeThemes.length)
	throw new Error('No Claude Code themes found. Run `bun run build` first.');
execFileSync('zip', [
	'-q',
	'-j',
	join(out, `afterglow-claude-code-themes-v${version}.zip`),
	...claudeThemes.map((f) => join(root, 'claude', 'themes', f)),
	join(root, 'LICENSE-APACHE'),
	join(root, 'LICENSE-MIT'),
]);

// The TextMate themes ship as a zip for Codex (its themes directory), bat and delta
const tmThemes = readdirSync(join(root, 'tmtheme')).filter((f) => f.endsWith('.tmTheme'));
if (!tmThemes.length) throw new Error('No TextMate themes found. Run `bun run build` first.');
execFileSync('zip', [
	'-q',
	'-j',
	join(out, `afterglow-tmthemes-v${version}.zip`),
	...tmThemes.map((f) => join(root, 'tmtheme', f)),
	join(root, 'LICENSE-APACHE'),
	join(root, 'LICENSE-MIT'),
]);

const sums = readdirSync(out)
	.sort()
	.map(
		(file) =>
			`${createHash('sha256')
				.update(readFileSync(join(out, file)))
				.digest('hex')}  ${file}`,
	);
writeFileSync(join(out, 'SHA256SUMS'), `${sums.join('\n')}\n`);

console.log(`Release assets for v${version} in dist/release:`);
for (const line of sums) console.log(`  ${line}`);
