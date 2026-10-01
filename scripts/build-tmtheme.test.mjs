// Unit tests for the .tmTheme generator, the plist parser and the validator, including bad input
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import {
	buildTmTheme,
	escapeXml,
	globalSettings,
	scopeRules,
	scopeString,
	themeUuid,
	tmFontStyle,
	tmVariants,
} from './build-tmtheme.mjs';
import { buildVscodeTheme } from './build-vscode.mjs';
import { parsePlist, parseXml, validateTmTheme } from './validate-tmtheme.mjs';

const ids = Object.keys(tmVariants);
const errorsFor = (id, edit) => validateTmTheme(id, edit(buildTmTheme(id))).errors.join('\n');

test('escapeXml escapes the characters XML reserves', () => {
	assert.equal(escapeXml('a & b < c > d'), 'a &amp; b &lt; c &gt; d');
});

test('scopeString joins scope lists the way TextMate writes them', () => {
	assert.equal(scopeString(['a', 'b.c']), 'a, b.c');
	assert.equal(scopeString('a'), 'a');
});

test('themeUuid is a stable, distinct, upper-case v5-style UUID per theme', () => {
	const uuids = ids.map(themeUuid);
	assert.equal(new Set(uuids).size, ids.length);
	for (const uuid of uuids) {
		assert.match(uuid, /^[\dA-F]{8}-[\dA-F]{4}-5[\dA-F]{3}-[89AB][\dA-F]{3}-[\dA-F]{12}$/);
	}
	assert.equal(themeUuid('afterglow'), themeUuid('afterglow'));
});

test('tmFontStyle keeps the three TextMate styles and drops strikethrough', () => {
	assert.equal(tmFontStyle('bold italic underline strikethrough'), 'bold italic underline');
	assert.equal(tmFontStyle('strikethrough'), '');
	assert.equal(tmFontStyle(''), '');
});

test('the global settings are opaque and come from the VS Code editor colours', () => {
	const vscode = buildVscodeTheme('afterglow-dark');
	const globals = globalSettings(vscode);
	assert.equal(globals.background, vscode.colors['editor.background']);
	assert.equal(globals.caret, vscode.colors['editorCursor.foreground']);
	for (const [key, value] of Object.entries(globals)) assert.match(value, /^#[\da-f]{6}$/, key);
});

test('the scope rules follow the VS Code token colours, minus strikethrough-only rules', () => {
	for (const id of ids) {
		const vscode = buildVscodeTheme(id);
		const rules = scopeRules(vscode);
		const struckOnly = vscode.tokenColors.filter(
			(rule) =>
				rule.settings.foreground === undefined && !tmFontStyle(rule.settings.fontStyle ?? ''),
		);
		assert.equal(rules.length, vscode.tokenColors.length - struckOnly.length, id);
		for (const rule of rules) assert.ok(!/strikethrough/.test(rule.settings.fontStyle ?? ''));
	}
});

test('the signature theme keeps the void background and orange caret, and shares the dark syntax roles', () => {
	const signature = buildTmTheme('afterglow');
	assert.match(signature, /<key>background<\/key>\s*<string>#050507<\/string>/);
	assert.match(signature, /<key>caret<\/key>\s*<string>#ffaa40<\/string>/);
	assert.match(signature, /<string>constant\.language<\/string>[\s\S]*?#a78bfa/);
});

test('the committed files match the generator', () => {
	for (const id of ids) {
		const file = new URL(`../tmtheme/${tmVariants[id].file}`, import.meta.url);
		assert.equal(readFileSync(file, 'utf8'), buildTmTheme(id), id);
	}
});

test('parsePlist reads dicts, arrays, entities and attributes on the root', () => {
	const text =
		'<?xml version="1.0"?>\n<!DOCTYPE plist PUBLIC "x" "y">\n<plist version="1.0"><dict><key>a</key><string>1 &amp; 2 &lt; &#65;</string><key>b</key><array><string>x</string></array></dict></plist>';
	assert.deepEqual(parsePlist(text), { a: '1 & 2 < A', b: ['x'] });
});

test('parseXml rejects mismatched, unclosed and stray markup', () => {
	assert.throws(() => parseXml('<plist><dict></plist>'), /does not match/);
	assert.throws(() => parseXml('<plist><dict>'), /never closed/);
	assert.throws(() => parseXml('<plist><string>a < b</string></plist>'), /stray/);
	assert.throws(() => parseXml('<plist><string>a & b</string></plist>'), /invalid entity/);
	assert.throws(() => parseXml('<dict></dict>'), /single <plist> root/);
	assert.throws(() => parseXml('<plist></plist>junk'), /outside the root/);
});

test('parsePlist rejects duplicate keys, orphan keys and unsupported types', () => {
	const wrap = (body) => `<plist><dict>${body}</dict></plist>`;
	assert.throws(
		() => parsePlist(wrap('<key>a</key><string>1</string><key>a</key><string>2</string>')),
		/duplicate key/,
	);
	assert.throws(() => parsePlist(wrap('<key>a</key>')), /key without a value/);
	assert.throws(
		() => parsePlist(wrap('<key>a</key><integer>1</integer>')),
		/not used in a .tmTheme/,
	);
});

test('validateTmTheme accepts the generated themes and measures contrast', () => {
	for (const id of ids) {
		const { errors, pairs } = validateTmTheme(id, buildTmTheme(id));
		assert.deepEqual(errors, []);
		assert.ok(pairs > 50);
	}
});

test('validateTmTheme reports text that is not a plist', () => {
	assert.match(
		validateTmTheme('afterglow', '<plist><dict>').errors.join(),
		/not a well-formed plist/,
	);
	assert.match(validateTmTheme('afterglow', '').errors.join(), /not a well-formed plist/);
});

test('validateTmTheme reports a missing global setting', () => {
	assert.match(
		errorsFor('afterglow', (text) =>
			text.replace(/\t+<key>caret<\/key>\n\t+<string>[^<]*<\/string>\n/, ''),
		),
		/global setting caret is missing/,
	);
});

test('validateTmTheme reports a colour that is not #rrggbb', () => {
	assert.match(
		errorsFor('afterglow', (text) => text.replace('#e0e0e0', 'rgb(224,224,224)')),
		/is not a #rrggbb colour/,
	);
	assert.match(
		errorsFor('afterglow', (text) =>
			text.replace('<string>#a78bfa</string>', '<string>#a78bfa80</string>'),
		),
		/foreground "#a78bfa80" is not a #rrggbb colour/,
	);
});

test('validateTmTheme reports a foreground without enough contrast', () => {
	assert.match(
		errorsFor('afterglow', (text) =>
			text.replace('<string>#a78bfa</string>', '<string>#1f2230</string>'),
		),
		/foreground is [\d.]+:1 \(needs 4.5:1\)/,
	);
});

test('validateTmTheme reports an unknown font style and an unknown setting', () => {
	assert.match(
		errorsFor('afterglow', (text) =>
			text.replace('<string>italic</string>', '<string>strikethrough</string>'),
		),
		/unknown fontStyle "strikethrough"/,
	);
	assert.match(
		errorsFor('afterglow', (text) => text.replace('<key>fontStyle</key>', '<key>fontStyles</key>')),
		/unknown setting fontStyles/,
	);
});

test('validateTmTheme reports a scope that the VS Code theme has and the file lacks', () => {
	assert.match(
		errorsFor('afterglow', (text) =>
			text.replace('<string>constant.language</string>', '<string>constant.lang</string>'),
		),
		/scopes missing from the VS Code theme: constant\.language/,
	);
});

test('validateTmTheme reports a wrong name, a bad UUID and drift', () => {
	assert.match(
		errorsFor('afterglow', (text) =>
			text.replace('<string>Afterglow</string>', '<string>Other</string>'),
		),
		/name must be "Afterglow"/,
	);
	assert.match(
		errorsFor('afterglow', (text) =>
			text.replace(/<string>[\dA-F-]{36}<\/string>/, '<string>nope</string>'),
		),
		/uuid "nope"/,
	);
	assert.match(
		errorsFor('afterglow', (text) => `${text}\n`),
		/out of date/,
	);
});
