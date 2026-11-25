// Unit tests for the desktop wallpaper generator and validator, including bad input
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
	DAY_SUN,
	HORIZONS,
	MODES,
	SUN,
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

test('the light scenes are daytime: a high sun, a bright sky and no stars', () => {
	const backCrest = Math.min(
		...[...HORIZONS[0].crest.matchAll(/-?\d+(?:\.\d+)?/g)].map(Number).filter((_, i) => i % 2),
	);
	assert.ok(DAY_SUN.cy + DAY_SUN.r * 2.6 < backCrest / 2, 'the sun stands in the upper sky');
	assert.ok(SUN.cy - SUN.r < backCrest + 200, 'the dusk sun still sits on the horizon');
	for (const palette of Object.keys(WALLPAPER_PALETTES)) {
		const day = sceneColours(palette, 'light');
		const dusk = sceneColours(palette, 'dark');
		// The sky brightens towards the horizon, the sun outshines the sky around it, and the day
		// sky is far brighter than the dusk one
		assert.ok(luminance(day.horizon) > luminance(day.skyTop), palette);
		assert.ok(luminance(day.sunDisc) > luminance(day.colourAt(DAY_SUN.cx, DAY_SUN.cy)), palette);
		assert.ok(luminance(day.skyTop) > 0.6 && luminance(dusk.skyTop) < 0.05, palette);
		assert.ok(day.wash[0].alpha > day.wash.at(-1).alpha, palette);
		for (const style of STYLES) {
			const svg = wallpaperSvg(`afterglow-${palette}-light-${style}`);
			assert.ok(!svg.includes('Stars'), palette);
			assert.match(svg, new RegExp(`cx="${DAY_SUN.cx}" cy="${DAY_SUN.cy}" r="${DAY_SUN.r}"`));
		}
	}
});
