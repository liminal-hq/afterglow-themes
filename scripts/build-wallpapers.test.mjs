// Unit tests for the desktop wallpaper generator and validator, including bad input
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
	MODES,
	STYLES,
	WALLPAPER_PALETTES,
	parseId,
	sceneColours,
	wallpaperIds,
	wallpaperSvg,
} from './build-wallpapers.mjs';
import { luminance } from './colour.mjs';
import { validateContrast, validatePalettes, validateWallpaper } from './validate-wallpapers.mjs';

const ids = wallpaperIds();

test('every palette has a dark and a light scene in both styles', () => {
	assert.equal(ids.length, Object.keys(WALLPAPER_PALETTES).length * MODES.length * STYLES.length);
	assert.equal(new Set(ids).size, ids.length);
	assert.deepEqual(parseId('afterglow-dusk-dark-smooth'), {
		palette: 'dusk',
		mode: 'dark',
		style: 'smooth',
	});
	assert.equal(parseId('afterglow-nope-dark-smooth'), null);
	assert.equal(parseId('afterglow-dusk-dim-smooth'), null);
});

test('the generated wallpapers pass their validators', () => {
	assert.deepEqual(validatePalettes(), []);
	for (const id of ids) assert.deepEqual(validateWallpaper(id, wallpaperSvg(id)), [], id);
	for (const palette of Object.keys(WALLPAPER_PALETTES))
		for (const mode of MODES) assert.deepEqual(validateContrast(palette, mode).errors, []);
});

test('a hand-edited colour or an outside reference is caught', () => {
	const id = 'afterglow-dusk-dark-stepped';
	const svg = wallpaperSvg(id);
	const recoloured = svg.replace(sceneColours('dusk', 'dark').sunDisc, '#ff00ff');
	assert.match(validateWallpaper(id, recoloured).join('\n'), /#ff00ff is not a palette colour/);
	const linked = svg.replace('</svg>', '<image href="https://example.com/a.png"/></svg>');
	assert.match(validateWallpaper(id, linked).join('\n'), /outside the file/);
});

test('the glow is brightest at the sun and fades out', () => {
	for (const palette of Object.keys(WALLPAPER_PALETTES)) {
		const { bands, skyTop } = sceneColours(palette, 'dark');
		assert.ok(luminance(bands[0]) > luminance(bands.at(-1)), palette);
		assert.ok(luminance(bands.at(-1)) - luminance(skyTop) < 0.002, palette);
	}
});
