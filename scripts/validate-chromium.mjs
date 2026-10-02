// Validate the generated Afterglow Chrome and Edge themes: manifest shape, colour keys and contrast
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { browserVariants, version } from './browser-roles.mjs';
import { buildChromiumTheme } from './build-chromium.mjs';
import { contrast, toHex } from './colour.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

// Every colour key Chromium's theme loader accepts that Afterglow sets, from
// `kOverwritableColorTable` in `chrome/browser/themes/browser_theme_pack.cc`
export const chromiumKeys = JSON.parse(
	readFileSync(join(root, 'scripts', 'chromium-theme-keys.json'), 'utf8'),
);

export const isRgb = (value) =>
	Array.isArray(value) &&
	value.length === 3 &&
	value.every((v) => Number.isInteger(v) && v >= 0 && v <= 255);

const pairs = [
	['tab_text', 'toolbar', 4.5],
	['tab_background_text', 'background_tab', 4.5],
	['tab_background_text', 'frame', 4.5],
	['tab_background_text', 'frame_inactive', 4.5],
	['toolbar_button_icon', 'toolbar', 3],
	['bookmark_text', 'toolbar', 4.5],
	['omnibox_text', 'omnibox_background', 4.5],
	['ntp_text', 'ntp_background', 4.5],
	['ntp_link', 'ntp_background', 4.5],
];

export const validateChromiumTheme = (id, manifest) => {
	const errors = [];
	if (typeof manifest !== 'object' || manifest === null || Array.isArray(manifest)) {
		return { errors: ['the manifest must be a JSON object'], measured: 0 };
	}
	if (manifest.manifest_version !== 3) errors.push('manifest_version must be 3');
	if (manifest.name !== browserVariants[id].label) {
		errors.push(`name must be "${browserVariants[id].label}"`);
	}
	if (manifest.version !== version) errors.push(`version must match package.json (${version})`);

	const colours = manifest.theme?.colors;
	if (typeof colours !== 'object' || colours === null || Array.isArray(colours)) {
		errors.push('theme.colors must be an object');
		return { errors, measured: 0 };
	}
	for (const key of chromiumKeys) {
		if (!Object.hasOwn(colours, key)) errors.push(`colour ${key} is not set`);
	}
	for (const [key, value] of Object.entries(colours)) {
		if (!chromiumKeys.includes(key)) errors.push(`${key} is not a colour key Chromium reads`);
		else if (!isRgb(value)) errors.push(`${key}: ${JSON.stringify(value)} must be [r, g, b]`);
	}
	if (JSON.stringify(manifest) !== JSON.stringify(buildChromiumTheme(id))) {
		errors.push(`chromium/themes/${id}/manifest.json is out of date. Run \`bun run build\`.`);
	}

	let measured = 0;
	for (const [fg, bg, min] of pairs) {
		if (!isRgb(colours[fg]) || !isRgb(colours[bg])) continue;
		measured++;
		const ratio = contrast(toHex(colours[fg]), toHex(colours[bg]));
		if (ratio < min) errors.push(`${fg} on ${bg} is ${ratio.toFixed(2)}:1 (needs ${min}:1)`);
	}
	return { errors, measured };
};

if (process.argv[1] === fileURLToPath(import.meta.url)) {
	let failed = false;
	for (const id of Object.keys(browserVariants)) {
		const path = `chromium/themes/${id}/manifest.json`;
		let manifest;
		try {
			manifest = JSON.parse(readFileSync(join(root, path), 'utf8'));
		} catch (error) {
			console.error(`✗ ${id}: cannot read ${path}: ${error.message}`);
			failed = true;
			continue;
		}
		const { errors, measured } = validateChromiumTheme(id, manifest);
		for (const message of errors) console.error(`✗ ${id}: ${message}`);
		if (errors.length) failed = true;
		else console.log(`✓ ${path} (${chromiumKeys.length} colours, ${measured} contrast pairs)`);
	}
	process.exit(failed ? 1 : 0);
}
