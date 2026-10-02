// Validate the generated Afterglow Firefox themes: manifest shape, colour keys and contrast
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { browserVariants, version } from './browser-roles.mjs';
import { buildFirefoxTheme, firefoxId } from './build-firefox.mjs';
import { contrast } from './colour.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

// Every colour key Firefox reads in `theme.colors`, from the MDN theme manifest reference
export const firefoxKeys = JSON.parse(
	readFileSync(join(root, 'scripts', 'firefox-theme-keys.json'), 'utf8'),
);
const HEX = /^#[\da-f]{6}$/i;

// Text and icons with the background each sits on and the contrast it needs. 3:1 is only for
// non-text elements: icons, borders and the selected-tab line.
const pairs = [
	['tab_text', 'tab_selected', 4.5],
	['tab_background_text', 'frame', 4.5],
	['tab_background_text', 'frame_inactive', 4.5],
	['tab_line', 'toolbar', 3],
	['toolbar_text', 'toolbar', 4.5],
	['bookmark_text', 'toolbar', 4.5],
	['icons', 'toolbar', 3],
	['icons_attention', 'toolbar', 3],
	['toolbar_text', 'button_background_hover', 4.5],
	['toolbar_text', 'button_background_active', 4.5],
	['toolbar_field_text', 'toolbar_field', 4.5],
	['toolbar_field_text_focus', 'toolbar_field_focus', 4.5],
	['toolbar_field_border', 'toolbar', 1.2],
	['toolbar_field_border_focus', 'toolbar_field_focus', 3],
	['toolbar_field_highlight_text', 'toolbar_field_highlight', 4.5],
	['popup_text', 'popup', 4.5],
	['popup_highlight_text', 'popup_highlight', 4.5],
	['sidebar_text', 'sidebar', 4.5],
	['sidebar_highlight_text', 'sidebar_highlight', 4.5],
	['ntp_text', 'ntp_background', 4.5],
	['ntp_text', 'ntp_card_background', 4.5],
];

// Validate one theme's parsed manifest. Returns the problems found and the contrast pairs measured.
export const validateFirefoxTheme = (id, manifest) => {
	const errors = [];
	if (typeof manifest !== 'object' || manifest === null || Array.isArray(manifest)) {
		return { errors: ['the manifest must be a JSON object'], measured: 0 };
	}
	if (manifest.manifest_version !== 2) errors.push('manifest_version must be 2');
	if (manifest.name !== browserVariants[id].label) {
		errors.push(`name must be "${browserVariants[id].label}"`);
	}
	if (manifest.version !== version) errors.push(`version must match package.json (${version})`);
	if (manifest.browser_specific_settings?.gecko?.id !== firefoxId(id)) {
		errors.push(`browser_specific_settings.gecko.id must be ${firefoxId(id)}`);
	}
	if (!['dark', 'light'].includes(manifest.theme?.properties?.color_scheme)) {
		errors.push('theme.properties.color_scheme must be "dark" or "light"');
	}

	const colours = manifest.theme?.colors;
	if (typeof colours !== 'object' || colours === null || Array.isArray(colours)) {
		errors.push('theme.colors must be an object');
		return { errors, measured: 0 };
	}
	for (const key of firefoxKeys) {
		if (!Object.hasOwn(colours, key)) errors.push(`colour ${key} is not set`);
	}
	for (const [key, value] of Object.entries(colours)) {
		if (!firefoxKeys.includes(key)) errors.push(`${key} is not a colour key Firefox reads`);
		else if (typeof value !== 'string' || !HEX.test(value)) {
			errors.push(`${key}: "${value}" must be #rrggbb`);
		}
	}
	if (JSON.stringify(manifest) !== JSON.stringify(buildFirefoxTheme(id))) {
		errors.push(`firefox/themes/${id}/manifest.json is out of date. Run \`bun run build\`.`);
	}

	let measured = 0;
	for (const [fg, bg, min] of pairs) {
		if (!HEX.test(colours[fg]) || !HEX.test(colours[bg])) continue;
		measured++;
		const ratio = contrast(colours[fg], colours[bg]);
		if (ratio < min) errors.push(`${fg} on ${bg} is ${ratio.toFixed(2)}:1 (needs ${min}:1)`);
	}
	return { errors, measured };
};

if (process.argv[1] === fileURLToPath(import.meta.url)) {
	let failed = false;
	for (const id of Object.keys(browserVariants)) {
		const path = `firefox/themes/${id}/manifest.json`;
		let manifest;
		try {
			manifest = JSON.parse(readFileSync(join(root, path), 'utf8'));
		} catch (error) {
			console.error(`✗ ${id}: cannot read ${path}: ${error.message}`);
			failed = true;
			continue;
		}
		const { errors, measured } = validateFirefoxTheme(id, manifest);
		for (const message of errors) console.error(`✗ ${id}: ${message}`);
		if (errors.length) failed = true;
		else console.log(`✓ ${path} (${firefoxKeys.length} colours, ${measured} contrast pairs)`);
	}
	process.exit(failed ? 1 : 0);
}
