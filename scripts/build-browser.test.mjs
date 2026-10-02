// Unit tests for the Firefox and Chromium theme generators and validators, including bad input
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { browserRoles, browserVariants, version } from './browser-roles.mjs';
import { buildChromiumTheme, rgbArray, serialiseChromium } from './build-chromium.mjs';
import { buildFirefoxTheme, firefoxId } from './build-firefox.mjs';
import { toHex } from './colour.mjs';
import { chromiumKeys, isRgb, validateChromiumTheme } from './validate-chromium.mjs';
import { firefoxKeys, validateFirefoxTheme } from './validate-firefox.mjs';

const ids = Object.keys(browserVariants);
const firefoxErrors = (id, edit) => {
	const manifest = structuredClone(buildFirefoxTheme(id));
	edit(manifest);
	return validateFirefoxTheme(id, manifest).errors.join('\n');
};
const chromiumErrors = (id, edit) => {
	const manifest = structuredClone(buildChromiumTheme(id));
	edit(manifest);
	return validateChromiumTheme(id, manifest).errors.join('\n');
};

test('the generated themes pass their validators', () => {
	for (const id of ids) {
		assert.deepEqual(validateFirefoxTheme(id, buildFirefoxTheme(id)).errors, [], id);
		assert.deepEqual(validateChromiumTheme(id, buildChromiumTheme(id)).errors, [], id);
	}
});

test('each theme sets exactly the known colour keys', () => {
	for (const id of ids) {
		assert.deepEqual(
			Object.keys(buildFirefoxTheme(id).theme.colors).sort(),
			[...firefoxKeys].sort(),
		);
		assert.deepEqual(
			Object.keys(buildChromiumTheme(id).theme.colors).sort(),
			[...chromiumKeys].sort(),
		);
	}
});

test('Firefox ids are distinct and the colour scheme follows the variant', () => {
	assert.equal(new Set(ids.map(firefoxId)).size, ids.length);
	assert.equal(buildFirefoxTheme('afterglow').theme.properties.color_scheme, 'dark');
	assert.equal(buildFirefoxTheme('afterglow-dark').theme.properties.color_scheme, 'dark');
	assert.equal(buildFirefoxTheme('afterglow-light').theme.properties.color_scheme, 'light');
});

test('both manifests carry the package version', () => {
	for (const id of ids) {
		assert.equal(buildFirefoxTheme(id).version, version);
		assert.equal(buildChromiumTheme(id).version, version);
	}
});

test('the selected tab joins the toolbar and the frame is the page surface', () => {
	for (const id of ids) {
		const { colors } = buildFirefoxTheme(id).theme;
		assert.equal(colors.tab_selected, colors.toolbar);
		assert.equal(colors.frame, browserRoles(id).surface);
	}
});

test('Chromium colours are [r, g, b] arrays that match the Firefox hex colours', () => {
	for (const id of ids) {
		const chromium = buildChromiumTheme(id).theme.colors;
		const firefox = buildFirefoxTheme(id).theme.colors;
		for (const value of Object.values(chromium)) assert.ok(isRgb(value));
		assert.equal(toHex(chromium.toolbar), firefox.toolbar);
		assert.equal(toHex(chromium.tab_text), firefox.tab_text);
	}
});

test('rgbArray and serialiseChromium round-trip and keep colours on one line', () => {
	assert.deepEqual(rgbArray('#ffaa40'), [255, 170, 64]);
	const text = serialiseChromium(buildChromiumTheme('afterglow'));
	assert.match(text, /"frame": \[5, 5, 7\]/);
	assert.deepEqual(JSON.parse(text), buildChromiumTheme('afterglow'));
});

test('the Firefox validator rejects an unknown key, a bad colour and a missing key', () => {
	assert.match(
		firefoxErrors('afterglow', (m) => (m.theme.colors.made_up = '#000000')),
		/made_up is not a colour key/,
	);
	assert.match(
		firefoxErrors('afterglow', (m) => (m.theme.colors.toolbar = 'red')),
		/toolbar: "red" must be #rrggbb/,
	);
	assert.match(
		firefoxErrors('afterglow', (m) => delete m.theme.colors.popup),
		/colour popup is not set/,
	);
});

test('the Firefox validator rejects low contrast and a wrong id', () => {
	assert.match(
		firefoxErrors('afterglow', (m) => (m.theme.colors.toolbar_text = '#12121a')),
		/toolbar_text on toolbar/,
	);
	assert.match(
		firefoxErrors('afterglow', (m) => (m.browser_specific_settings.gecko.id = 'x@y')),
		/gecko.id must be/,
	);
});

test('the Chromium validator rejects an unknown key, a bad colour and low contrast', () => {
	assert.match(
		chromiumErrors('afterglow', (m) => (m.theme.colors.made_up = [0, 0, 0])),
		/made_up is not a colour key/,
	);
	assert.match(
		chromiumErrors('afterglow', (m) => (m.theme.colors.toolbar = '#123456')),
		/toolbar: "#123456" must be \[r, g, b\]/,
	);
	assert.match(
		chromiumErrors('afterglow', (m) => (m.theme.colors.tab_text = [18, 18, 26])),
		/tab_text on toolbar/,
	);
});
