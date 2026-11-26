// Package the themes into release assets: the JSON files, zip bundles, the .vsix, the desktop zips and SHA256SUMS
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
	mkdtempSync,
	readFileSync,
	readdirSync,
	rmSync,
	writeFileSync,
} from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join, relative, resolve } from 'node:path';
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

// The Forgejo themes and the instance avatar ship as a zip for the custom directory's public/assets
const forgejoThemes = readdirSync(join(root, 'forgejo', 'themes')).filter((f) =>
	f.endsWith('.css'),
);
if (!forgejoThemes.length) throw new Error('No Forgejo themes found. Run `bun run build` first.');
execFileSync('zip', [
	'-q',
	'-j',
	join(out, `afterglow-forgejo-v${version}.zip`),
	...forgejoThemes.map((f) => join(root, 'forgejo', 'themes', f)),
	join(root, 'forgejo', 'avatar', 'forgejo-instance.svg'),
	join(root, 'LICENSE-APACHE'),
	join(root, 'LICENSE-MIT'),
]);

// A Firefox theme is an .xpi (a zip with the manifest and images at its root), one per theme. These
// are unsigned, so release Firefox only loads them as temporary add-ons until they are signed.
const firefoxThemes = readdirSync(join(root, 'firefox', 'themes'));
if (!firefoxThemes.length) throw new Error('No Firefox themes found. Run `bun run build` first.');
for (const id of firefoxThemes) {
	execFileSync('zip', ['-q', '-r', join(out, `${id}-firefox-v${version}.xpi`), '.'], {
		cwd: join(root, 'firefox', 'themes', id),
	});
}

// The Chrome and Edge themes ship as one zip of three folders, each loadable unpacked
const chromiumThemes = readdirSync(join(root, 'chromium', 'themes'));
if (!chromiumThemes.length) throw new Error('No Chromium themes found. Run `bun run build` first.');
execFileSync(
	'zip',
	[
		'-q',
		'-r',
		join(out, `afterglow-chromium-themes-v${version}.zip`),
		...chromiumThemes,
		// Chromium writes a theme cache next to the manifest when a theme is loaded unpacked
		'-x',
		'*.pak',
	],
	{ cwd: join(root, 'chromium', 'themes') },
);

// The desktop wallpapers ship as a zip of the SVG sources
const wallpapers = readdirSync(join(root, 'assets', 'wallpapers')).filter((f) =>
	f.endsWith('.svg'),
);
if (!wallpapers.length) throw new Error('No wallpapers found. Run `bun run build` first.');
execFileSync('zip', [
	'-q',
	'-j',
	join(out, `afterglow-wallpapers-v${version}.zip`),
	...wallpapers.map((f) => join(root, 'assets', 'wallpapers', f)),
	join(root, 'LICENSE-APACHE'),
	join(root, 'LICENSE-MIT'),
]);

// The ReactOS desktop zip needs python3 (numpy and Pillow), llvm-rc, lld-link and rsvg-convert. CI and releases
// require them; AFTERGLOW_SKIP_REACTOS=1 skips this one zip, with a warning, for a local run without them.
if (process.env.AFTERGLOW_SKIP_REACTOS === '1') {
	console.warn('warning: AFTERGLOW_SKIP_REACTOS=1, so the ReactOS desktop zip is not built.');
} else {
	buildReactosDesktop();
}

function buildReactosDesktop() {
	const missing = ['python3', 'llvm-rc', 'lld-link', 'rsvg-convert'].filter((tool) => {
		try {
			execFileSync('which', [tool], { stdio: 'ignore' });
			return false;
		} catch {
			return true;
		}
	});
	if (missing.length) {
		throw new Error(
			`The ReactOS desktop zip needs ${missing.join(', ')} on the PATH (python3 with numpy and Pillow, ` +
				'the LLVM tools llvm-rc and lld-link, and rsvg-convert). Install them, or set AFTERGLOW_SKIP_REACTOS=1 to skip ' +
				'that zip for a local run.',
		);
	}
	const desktop = join(root, 'desktop');
	const scratch = mkdtempSync(join(tmpdir(), 'afterglow-reactos-'));
	try {
		const name = `afterglow-reactos-desktop-v${version}`;
		const stage = join(scratch, name);
		mkdirSync(stage, { recursive: true });

		// Both builds keep the file name afterglow.msstyles, which is the name the style registry entries use,
		// so they live in separate folders: style/ has the classic scroll bars, style-scrollbars/ the Afterglow ones.
		execFileSync('bash', [join(desktop, 'style', 'build.sh'), join(scratch, 'build')], {
			stdio: 'ignore',
		});
		execFileSync(
			'bash',
			[join(desktop, 'style', 'build.sh'), join(scratch, 'build-scrollbars'), '--scrollbars'],
			{ stdio: 'ignore' },
		);
		mkdirSync(join(stage, 'style'));
		mkdirSync(join(stage, 'style-scrollbars'));
		copyFileSync(
			join(scratch, 'build', 'afterglow.msstyles'),
			join(stage, 'style', 'afterglow.msstyles'),
		);
		copyFileSync(
			join(scratch, 'build-scrollbars', 'afterglow.msstyles'),
			join(stage, 'style-scrollbars', 'afterglow.msstyles'),
		);

		// The eight colour schemes and the script that applies one
		cpSync(join(desktop, 'schemes'), join(stage, 'schemes'), { recursive: true });
		mkdirSync(join(stage, 'install'));
		copyFileSync(
			join(desktop, 'install', 'afterglow-original.reg'),
			join(stage, 'install', 'afterglow-original.reg'),
		);

		// The pointers are drawn here, not committed. The user32.dll patch tool ships; a patched binary never does.
		const pointers = join(stage, 'pointers');
		execFileSync('python3', [join(desktop, 'pointers', 'gen-cursors.py'), pointers], {
			stdio: 'ignore',
		});
		for (const file of [
			'afterglow-pointers.reg',
			'patch-user32.py',
			'SHA256SUMS',
			'SHA256SUMS.user32',
		]) {
			copyFileSync(join(desktop, 'pointers', file), join(pointers, file));
		}
		// The SVG masters are reference art beside the raster pointers
		cpSync(join(desktop, 'pointers', 'svg'), join(pointers, 'svg'), { recursive: true });

		// The logon banner and bar: the SVG masters, the two BMPs rendered from them and their hashes. The patch into
		// agmsgina.dll is not here; it happens in the reactos-liminal build.
		const logon = join(stage, 'logon');
		execFileSync('python3', [join(desktop, 'logon', 'render.py'), logon], { stdio: 'ignore' });
		for (const file of [
			'banner-a.svg',
			'banner-b.svg',
			'bar.svg',
			'SHA256SUMS',
			'SHA256SUMS.masters',
		]) {
			copyFileSync(join(desktop, 'logon', file), join(logon, file));
		}

		// The boot logo: the SVG master and palette, the bitmaps and previews rendered from them and the hash lists. The patch into
		// the kernel is not here; it happens in the reactos-liminal build.
		const boot = join(stage, 'boot');
		execFileSync('python3', [join(desktop, 'boot', 'render.py'), boot], { stdio: 'ignore' });
		for (const file of ['boot-logo.svg', 'palette.json', 'SHA256SUMS', 'SHA256SUMS.masters']) {
			copyFileSync(join(desktop, 'boot', file), join(boot, file));
		}

		// The Start orb and menu banner: the SVG masters, the two resource-ready DIBs and PNG previews rendered from them and the hash
		// lists. The patch into explorer.exe is not here; it happens in the reactos-liminal build.
		const startArt = join(stage, 'start');
		execFileSync('python3', [join(desktop, 'start', 'render.py'), startArt], { stdio: 'ignore' });
		for (const file of ['orb.svg', 'banner.svg', 'SHA256SUMS', 'SHA256SUMS.masters']) {
			copyFileSync(join(desktop, 'start', file), join(startArt, file));
		}

		// The icon set and the shortcut arrow: the .ico and PNG renders drawn here, the SVG masters they come from, and the id map
		const icons = join(stage, 'icons');
		execFileSync('python3', [join(desktop, 'icons', 'render.py'), icons], { stdio: 'ignore' });
		rmSync(join(icons, 'afterglow-icons-sheet.png'));
		rmSync(join(icons, 'afterglow-arrow-preview.png'));
		cpSync(join(desktop, 'icons', 'svg'), join(icons, 'svg'), { recursive: true });
		cpSync(join(desktop, 'icons', 'arrow'), join(icons, 'arrow'), { recursive: true });
		for (const file of ['map.json', 'SHA256SUMS', 'SHA256SUMS.masters']) {
			copyFileSync(join(desktop, 'icons', file), join(icons, file));
		}

		mkdirSync(join(stage, 'docs'));
		// desktop/SHA256SUMS names the two builds for the check script; here they sit in folders
		const styleSums = ['style', 'style-scrollbars'].map(
			(dir) =>
				`${createHash('sha256')
					.update(readFileSync(join(stage, dir, 'afterglow.msstyles')))
					.digest('hex')}  ${dir}/afterglow.msstyles`,
		);
		writeFileSync(join(stage, 'SHA256SUMS'), `${styleSums.join('\n')}\n`);
		// The docs are written for the repository layout. In the zip, desktop/ is the root and docs/ sits
		// beside pointers/, so the links that cross out of desktop/ are rewritten to the zip layout.
		mkdirSync(join(stage, 'docs', 'images'));
		copyFileSync(
			join(root, 'docs', 'images', 'afterglow-pointers.png'),
			join(stage, 'docs', 'images', 'afterglow-pointers.png'),
		);
		copyFileSync(
			join(root, 'docs', 'images', 'afterglow-logon-banner.png'),
			join(stage, 'docs', 'images', 'afterglow-logon-banner.png'),
		);
		copyFileSync(
			join(root, 'docs', 'images', 'afterglow-boot-logo.png'),
			join(stage, 'docs', 'images', 'afterglow-boot-logo.png'),
		);
		copyFileSync(
			join(root, 'docs', 'images', 'afterglow-start.png'),
			join(stage, 'docs', 'images', 'afterglow-start.png'),
		);
		for (const image of [
			'afterglow-icons.png',
			'afterglow-icons-contact.png',
			'afterglow-arrow.png',
			'afterglow-console-palettes.png',
			'afterglow-console-before-after.png',
			'afterglow-selection-menu.png',
		]) {
			copyFileSync(join(root, 'docs', 'images', image), join(stage, 'docs', 'images', image));
		}
		const readme = readFileSync(join(desktop, 'README.md'), 'utf8').replaceAll(
			'](../docs/',
			'](docs/',
		);
		writeFileSync(join(stage, 'README.md'), readme);
		copyFileSync(join(desktop, 'PROVENANCE.md'), join(stage, 'PROVENANCE.md'));
		for (const doc of [
			'reactos-desktop-colour-schemes.md',
			'reactos-desktop-pointers.md',
			'reactos-desktop-logon.md',
			'reactos-desktop-boot.md',
			'reactos-desktop-start.md',
			'reactos-desktop-icons.md',
		]) {
			const text = readFileSync(join(root, 'docs', doc), 'utf8').replaceAll(
				'](../desktop/',
				'](../',
			);
			writeFileSync(join(stage, 'docs', doc), text);
		}
		checkLinks(stage);
		for (const licence of ['LICENSE-APACHE', 'LICENSE-MIT']) {
			copyFileSync(join(root, licence), join(stage, licence));
		}

		execFileSync('zip', ['-q', '-r', join(out, `${name}.zip`), name], { cwd: scratch });
	} finally {
		rmSync(scratch, { recursive: true, force: true });
	}
}

// Fail when a markdown file in the staged zip links to a file that is not in the zip
function checkLinks(dir) {
	const files = [];
	const walk = (d) => {
		for (const entry of readdirSync(d, { withFileTypes: true })) {
			const full = join(d, entry.name);
			if (entry.isDirectory()) walk(full);
			else if (entry.name.endsWith('.md')) files.push(full);
		}
	};
	walk(dir);
	const broken = [];
	for (const file of files) {
		const text = readFileSync(file, 'utf8');
		for (const match of text.matchAll(/!?\[[^\]]*\]\(([^)\s]+)[^)]*\)/g)) {
			const target = match[1].split('#')[0];
			if (!target || /^([a-z][a-z0-9+.-]*:|\/\/)/i.test(target)) continue;
			const resolved = resolve(dirname(file), decodeURIComponent(target));
			if (relative(dir, resolved).startsWith('..') || !existsSync(resolved)) {
				broken.push(`${relative(dir, file)} -> ${target}`);
			}
		}
	}
	if (broken.length) {
		throw new Error(
			`Links in the ReactOS desktop zip that do not resolve inside it:\n  ${broken.join('\n  ')}`,
		);
	}
}

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
