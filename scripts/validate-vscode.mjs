// Validate the generated Afterglow VS Code themes: colour keys, scope coverage, contrast and manifest
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { existsSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildVscodeTheme, vscodeVariants } from './build-vscode.mjs';
import { contrast, over } from './colour.mjs';
import { variants } from './hues.mjs';
import { parseJsonc } from './jsonc.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const read = (path) => readFileSync(join(root, path), 'utf8');
const validKeys = new Set(JSON.parse(read('scripts/vscode-colour-keys.json')));
const HEX = /^#(?:[\da-f]{6}|[\da-f]{8})$/i;

let failed = false;
let failures = 0;
const fail = (name, message) => {
	failed = true;
	failures++;
	console.error(`✗ ${name}: ${message}`);
};

// Foreground and background pairs the UI draws together, with the contrast each needs
const pairs = [
	['foreground', 'editor.background', 4.5],
	['editor.foreground', 'editor.background', 4.5],
	['editorLineNumber.foreground', 'editor.background', 3],
	['editorLineNumber.activeForeground', 'editor.background', 4.5],
	['descriptionForeground', 'editor.background', 4.5],
	['textLink.foreground', 'editor.background', 4.5],
	['editorError.foreground', 'editor.background', 4.5],
	['editorWarning.foreground', 'editor.background', 4.5],
	['editorInfo.foreground', 'editor.background', 4.5],
	['tab.activeForeground', 'tab.activeBackground', 4.5],
	['tab.inactiveForeground', 'tab.inactiveBackground', 4.5],
	['sideBar.foreground', 'sideBar.background', 4.5],
	['sideBarSectionHeader.foreground', 'sideBarSectionHeader.background', 4.5],
	['activityBar.foreground', 'activityBar.background', 4.5],
	['activityBar.inactiveForeground', 'activityBar.background', 3],
	['titleBar.activeForeground', 'titleBar.activeBackground', 4.5],
	['statusBar.foreground', 'statusBar.background', 4.5],
	['statusBarItem.remoteForeground', 'statusBarItem.remoteBackground', 4.5],
	['badge.foreground', 'badge.background', 4.5],
	['activityBarBadge.foreground', 'activityBarBadge.background', 4.5],
	['button.foreground', 'button.background', 4.5],
	['button.secondaryForeground', 'button.secondaryBackground', 4.5],
	['input.foreground', 'input.background', 4.5],
	['input.placeholderForeground', 'input.background', 4.5],
	['dropdown.foreground', 'dropdown.background', 4.5],
	['list.activeSelectionForeground', 'list.activeSelectionBackground', 4.5],
	['list.inactiveSelectionForeground', 'list.inactiveSelectionBackground', 4.5],
	['menu.foreground', 'menu.background', 4.5],
	['menu.selectionForeground', 'menu.selectionBackground', 4.5],
	['quickInput.foreground', 'quickInput.background', 4.5],
	['editorSuggestWidget.foreground', 'editorSuggestWidget.background', 4.5],
	['editorHoverWidget.statusBarBackground', 'editorHoverWidget.background', 1],
	['notifications.foreground', 'notifications.background', 4.5],
	['panelTitle.activeForeground', 'panel.background', 4.5],
	['panelTitle.inactiveForeground', 'panel.background', 4.5],
	['terminal.foreground', 'terminal.background', 4.5],
	['statusBar.debuggingForeground', 'statusBar.debuggingBackground', 4.5],
	['statusBar.noFolderForeground', 'statusBar.noFolderBackground', 4.5],
	['statusBarItem.prominentForeground', 'statusBarItem.prominentBackground', 4.5],
	['statusBarItem.errorForeground', 'statusBarItem.errorBackground', 4.5],
	['statusBarItem.warningForeground', 'statusBarItem.warningBackground', 4.5],
	['tab.hoverForeground', 'tab.hoverBackground', 4.5],
	['list.hoverForeground', 'list.hoverBackground', 4.5],
	['list.highlightForeground', 'list.activeSelectionBackground', 4.5],
	['list.invalidItemForeground', 'editor.background', 4.5],
	['textPreformat.foreground', 'textCodeBlock.background', 4.5],
	['editorInlayHint.foreground', 'editorInlayHint.background', 4.5],
	['peekViewTitleDescription.foreground', 'peekViewTitle.background', 4.5],
	['gitDecoration.untrackedResourceForeground', 'sideBar.background', 4.5],
	// Text drawn over translucent highlights is checked against the highlight over the editor
	['editor.foreground', 'editor.selectionBackground', 4.5],
	['editor.foreground', 'editor.findMatchBackground', 4.5],
	['editor.foreground', 'editor.lineHighlightBackground', 4.5],
	['editor.foreground', 'editor.wordHighlightStrongBackground', 4.5],
	['terminal.foreground', 'terminal.selectionBackground', 4.5],
	// Deliberately dim elements (disabled, ghost, ignored and inactive) are held to a 3:1 floor
	['disabledForeground', 'editor.background', 3],
	['editorGhostText.foreground', 'editor.background', 3],
	['editorCodeLens.foreground', 'editor.background', 3],
	['titleBar.inactiveForeground', 'titleBar.inactiveBackground', 3],
	['tab.unfocusedInactiveForeground', 'tab.inactiveBackground', 3],
	['gitDecoration.ignoredResourceForeground', 'sideBar.background', 3],
	...[
		'Red',
		'Green',
		'Yellow',
		'Blue',
		'Magenta',
		'Cyan',
		'White',
		'BrightRed',
		'BrightGreen',
		'BrightYellow',
		'BrightBlue',
		'BrightMagenta',
		'BrightCyan',
		'BrightWhite',
	].map((name) => [`terminal.ansi${name}`, 'terminal.background', 4.5]),
	['terminal.ansiBrightBlack', 'terminal.background', 3],
];

const upstreamRules = (id) => {
	const dark = variants[id].mode === 'dark';
	return ['vs', 'plus'].flatMap(
		(part) =>
			parseJsonc(read(`vscode/upstream/${dark ? 'dark' : 'light'}_${part}.json`)).tokenColors,
	);
};

for (const [id, meta] of Object.entries(vscodeVariants)) {
	const failuresBefore = failures;
	const theme = JSON.parse(read(`vscode/themes/${meta.file}`));
	const expected = buildVscodeTheme(id);

	if (JSON.stringify(theme) !== JSON.stringify(expected)) {
		fail(id, `vscode/themes/${meta.file} is out of date. Run \`bun run build\`.`);
	}

	for (const [key, value] of Object.entries(theme.colors)) {
		if (!validKeys.has(key)) fail(id, `colors.${key} is not a VS Code colour key`);
		if (!HEX.test(value)) fail(id, `colors.${key} is not a 6 or 8 digit hex colour (${value})`);
	}

	const upstream = upstreamRules(id);
	if (theme.tokenColors.length !== upstream.length) {
		fail(id, `tokenColors has ${theme.tokenColors.length} rules, expected ${upstream.length}`);
	}
	theme.tokenColors.forEach((rule, i) => {
		const scopes = JSON.stringify(rule.scope ?? null);
		if (scopes !== JSON.stringify(upstream[i]?.scope ?? null)) {
			fail(id, `tokenColors[${i}] scopes differ from Dark+/Light+`);
		}
		const fg = rule.settings.foreground;
		if (fg !== undefined && !HEX.test(fg))
			fail(id, `tokenColors[${i}] foreground ${fg} is not hex`);
	});

	const bg = theme.colors['editor.background'];
	const seen = new Set();
	for (const rule of theme.tokenColors) {
		const fg = rule.settings.foreground;
		if (fg === undefined || seen.has(fg)) continue;
		seen.add(fg);
		const ratio = contrast(fg, bg);
		if (ratio < 4.5) fail(id, `syntax ${fg} on ${bg} is ${ratio.toFixed(2)}:1 (needs 4.5:1)`);
	}

	for (const [foreground, background, min] of pairs) {
		const [fg, bgc] = [theme.colors[foreground], theme.colors[background]];
		if (fg === undefined || bgc === undefined) {
			fail(id, `missing ${fg === undefined ? foreground : background} for a contrast check`);
			continue;
		}
		const surface = over(bgc, bg);
		const ratio = contrast(over(fg, surface), surface);
		if (ratio < min) {
			fail(id, `${foreground} on ${background} is ${ratio.toFixed(2)}:1 (needs ${min}:1)`);
		}
	}

	if (failures === failuresBefore) {
		console.log(
			`✓ ${meta.label} (${Object.keys(theme.colors).length} colours, ${seen.size} syntax colours)`,
		);
	}
}

// The extension manifest must list every theme and agree with the root package version
const manifestFailuresBefore = failures;
const manifest = JSON.parse(read('vscode/package.json'));
const rootVersion = JSON.parse(read('package.json')).version;
if (manifest.version !== rootVersion) {
	fail('manifest', `version ${manifest.version} does not match package.json ${rootVersion}`);
}
for (const [id, meta] of Object.entries(vscodeVariants)) {
	const entry = manifest.contributes?.themes?.find((t) => t.path === `./themes/${meta.file}`);
	if (!entry) fail('manifest', `contributes.themes is missing ${id}`);
	else if (entry.label !== meta.label || entry.uiTheme !== meta.uiTheme) {
		fail('manifest', `contributes.themes entry for ${id} has the wrong label or uiTheme`);
	}
}
for (const file of [manifest.icon, 'README.md']) {
	if (file && !existsSync(join(root, 'vscode', file)))
		fail('manifest', `vscode/${file} is missing`);
}
if (failures === manifestFailuresBefore)
	console.log(`✓ vscode/package.json (v${manifest.version})`);

process.exit(failed ? 1 : 0);
