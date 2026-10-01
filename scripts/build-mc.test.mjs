// Unit tests for the Midnight Commander skin generator: palette rounding, rendering and the INI parser
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import {
	buildSkin,
	buildSkinModel,
	flavours,
	mcVariants,
	nearest256,
	resolveEntry,
	skinFile,
	xtermHex,
} from './build-mc.mjs';
import { contrast } from './colour.mjs';
import { colourToHex, parseIni } from './validate-mc.mjs';

const keys = JSON.parse(readFileSync(new URL('./mc-skin-keys.json', import.meta.url), 'utf8'));

test('xtermHex follows the xterm cube and greyscale ramp', () => {
	assert.equal(xtermHex(16), '#000000');
	assert.equal(xtermHex(21), '#0000ff');
	assert.equal(xtermHex(196), '#ff0000');
	assert.equal(xtermHex(231), '#ffffff');
	assert.equal(xtermHex(232), '#080808');
	assert.equal(xtermHex(255), '#eeeeee');
});

test('nearest256 never returns one of the terminal-defined first 16 colours', () => {
	for (const hex of ['#000000', '#ffffff', '#ff0000', '#050507']) {
		assert.ok(nearest256(hex) >= 16);
	}
	assert.equal(nearest256('#ff0000'), 196);
});

test('nearest256 honours a contrast floor against the background', () => {
	const bg = '#0f0e1a';
	const index = nearest256('#5a6273', bg, 4.5);
	assert.ok(contrast(xtermHex(index), bg) >= 4.5);
});

test('resolveEntry keeps default backgrounds and rounds colours for the 256 flavour', () => {
	const model = buildSkinModel('afterglow');
	const item = model.sections.core._default_;
	assert.deepEqual(resolveEntry(model, item, 'truecolor'), { fg: '#e0e0e0', bg: 'default' });
	const rounded = resolveEntry(model, item, '256');
	assert.match(rounded.fg, /^color\d+$/);
	assert.equal(rounded.bg, 'default');
});

test('only the afterglow skin uses the terminal default background', () => {
	assert.match(buildSkin('afterglow', 'truecolor'), /_default_ = #e0e0e0;default/);
	for (const id of ['afterglow-dark', 'afterglow-light']) {
		for (const flavour of Object.keys(flavours))
			assert.doesNotMatch(buildSkin(id, flavour), /;default/);
	}
});

test('every skin defines every section and key the reference skins do', () => {
	for (const id of Object.keys(mcVariants)) {
		for (const flavour of Object.keys(flavours)) {
			const skin = parseIni(buildSkin(id, flavour));
			for (const [section, names] of Object.entries(keys)) {
				for (const name of names)
					assert.ok(skin[section]?.[name], `${id} ${flavour} [${section}] ${name}`);
			}
		}
	}
});

test('truecolour skins flag truecolors and 256-colour skins flag 256colors', () => {
	assert.equal(parseIni(buildSkin('afterglow-dark', 'truecolor')).skin.truecolors, 'true');
	assert.equal(parseIni(buildSkin('afterglow-dark', '256')).skin['256colors'], 'true');
	assert.doesNotMatch(buildSkin('afterglow-dark', '256'), /#[\da-f]{6}/i);
});

test('skinFile names the 256-colour fallback with a suffix', () => {
	assert.equal(skinFile('afterglow', 'truecolor'), 'afterglow.ini');
	assert.equal(skinFile('afterglow-light', '256'), 'afterglow-light-256.ini');
});

test('parseIni reads sections, ignores comments and keeps values containing equals signs', () => {
	const text =
		'# comment\n[core]\n    _default_ = #fff;#000\n    a = b=c\n\n[skin]\n    description = x\n';
	assert.deepEqual(parseIni(text), {
		core: { _default_: '#fff;#000', a: 'b=c' },
		skin: { description: 'x' },
	});
});

test('colourToHex accepts only colours valid for the flavour', () => {
	assert.equal(colourToHex('#a78bfa', 'truecolor'), '#a78bfa');
	assert.equal(colourToHex('#a78', 'truecolor'), undefined);
	assert.equal(colourToHex('color16', '256'), '#000000');
	assert.equal(colourToHex('color5', '256'), undefined);
	assert.equal(colourToHex('#a78bfa', '256'), undefined);
	assert.equal(colourToHex('default', '256', '#050507'), '#050507');
});
