// Generate the Afterglow TextMate .tmTheme files for Codex, bat and delta from the VS Code themes
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { createHash } from 'node:crypto';
import { mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildVscodeTheme } from './build-vscode.mjs';
import { over } from './colour.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

// Codex takes the kebab-case file name as the theme id, so the file names are the ids
export const tmVariants = {
	afterglow: { label: 'Afterglow', file: 'afterglow.tmTheme' },
	'afterglow-dark': { label: 'Afterglow Dark', file: 'afterglow-dark.tmTheme' },
	'afterglow-light': { label: 'Afterglow Light', file: 'afterglow-light.tmTheme' },
};

// A stable UUID per theme (the first 16 bytes of a SHA-1, laid out as a version 5 UUID), so
// rebuilding never changes the file
export const themeUuid = (id) => {
	const bytes = createHash('sha1')
		.update(`liminal-hq/afterglow-themes:${id}`)
		.digest()
		.subarray(0, 16);
	bytes[6] = (bytes[6] & 0x0f) | 0x50;
	bytes[8] = (bytes[8] & 0x3f) | 0x80;
	const hex = bytes.toString('hex');
	return [hex.slice(0, 8), hex.slice(8, 12), hex.slice(12, 16), hex.slice(16, 20), hex.slice(20)]
		.join('-')
		.toUpperCase();
};

export const escapeXml = (text) =>
	text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');

// A rule's scope selector as TextMate writes it: one comma-separated string
export const scopeString = (scope) => [].concat(scope).join(', ');

// The editor-wide colours. They come from the VS Code theme, so the editor and the terminal agree,
// and translucent colours are flattened onto the background because .tmTheme colours are opaque.
export const globalSettings = (vscode) => {
	const colours = vscode.colors;
	const background = colours['editor.background'];
	return {
		background,
		foreground: colours['editor.foreground'],
		caret: colours['editorCursor.foreground'],
		selection: over(colours['editor.selectionBackground'], background),
		lineHighlight: colours['editor.lineHighlightBackground'],
		invisibles: colours['editorWhitespace.foreground'],
		gutter: colours['editorGutter.background'],
		gutterForeground: colours['editorLineNumber.foreground'],
	};
};

// TextMate knows three font styles. VS Code adds `strikethrough`, which a .tmTheme cannot express
// and which syntect (bat, delta and Codex) rejects, so it is dropped.
const TM_FONT_STYLES = ['bold', 'italic', 'underline'];
export const tmFontStyle = (fontStyle) =>
	fontStyle
		.split(/\s+/)
		.filter((style) => TM_FONT_STYLES.includes(style))
		.join(' ');

// The scope rules come straight from the recoloured Dark+ and Light+ token colours. A rule left
// with nothing to set (only a strikethrough) is dropped.
export const scopeRules = (vscode) =>
	vscode.tokenColors.flatMap((rule) => {
		const { fontStyle, ...rest } = rule.settings;
		const settings = {
			...rest,
			...(fontStyle === undefined ? {} : { fontStyle: tmFontStyle(fontStyle) }),
		};
		if (fontStyle !== undefined && rule.settings.foreground === undefined && !settings.fontStyle) {
			return [];
		}
		return [
			{
				...(rule.name === undefined ? {} : { name: rule.name }),
				scope: scopeString(rule.scope ?? ''),
				settings,
			},
		];
	});

const stringEntry = (key, value, depth) => {
	const pad = '\t'.repeat(depth);
	return [`${pad}<key>${escapeXml(key)}</key>`, `${pad}<string>${escapeXml(value)}</string>`];
};

const settingsDict = (settings, depth) => {
	const pad = '\t'.repeat(depth);
	const keys = ['foreground', 'background', 'fontStyle'];
	for (const key of Object.keys(settings)) {
		if (!keys.includes(key)) throw new Error(`A token setting has no .tmTheme equivalent: ${key}`);
	}
	const lines = [`${pad}<dict>`];
	for (const key of keys) {
		if (settings[key] !== undefined) lines.push(...stringEntry(key, settings[key], depth + 1));
	}
	lines.push(`${pad}</dict>`);
	return lines;
};

export const buildTmTheme = (id) => {
	const vscode = buildVscodeTheme(id);
	const global = ['\t\t<dict>', '\t\t\t<key>settings</key>', '\t\t\t<dict>'];
	for (const [key, value] of Object.entries(globalSettings(vscode))) {
		global.push(...stringEntry(key, value, 4));
	}
	global.push('\t\t\t</dict>', '\t\t</dict>');

	const rules = scopeRules(vscode).flatMap((rule) => [
		'\t\t<dict>',
		...(rule.name === undefined ? [] : stringEntry('name', rule.name, 3)),
		...stringEntry('scope', rule.scope, 3),
		'\t\t\t<key>settings</key>',
		...settingsDict(rule.settings, 3),
		'\t\t</dict>',
	]);

	return `${[
		'<?xml version="1.0" encoding="UTF-8"?>',
		'<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">',
		'<plist version="1.0">',
		'<dict>',
		...stringEntry('name', tmVariants[id].label, 1),
		...stringEntry('uuid', themeUuid(id), 1),
		'\t<key>settings</key>',
		'\t<array>',
		...global,
		...rules,
		'\t</array>',
		'</dict>',
		'</plist>',
	].join('\n')}\n`;
};

if (process.argv[1] === fileURLToPath(import.meta.url)) {
	// Start clean so a renamed or removed theme never lingers in the output
	rmSync(join(root, 'tmtheme'), { recursive: true, force: true });
	mkdirSync(join(root, 'tmtheme'), { recursive: true });

	for (const [id, meta] of Object.entries(tmVariants)) {
		writeFileSync(join(root, 'tmtheme', meta.file), buildTmTheme(id));
		console.log(`wrote tmtheme/${meta.file}`);
	}
}
