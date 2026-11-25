// Generate the Afterglow Chrome and Edge themes (Chromium theme manifests) from the shared palette
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { toRgb } from './colour.mjs';
import { browserRoles, browserVariants, version } from './browser-roles.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

// Chromium writes a colour as an `[r, g, b]` array
export const rgbArray = (hex) => toRgb(hex);

// Tab-indented JSON with each `[r, g, b]` colour kept on one line so the file stays readable
export const serialiseChromium = (theme) =>
	`${JSON.stringify(theme, null, '\t').replace(/\[\s+(\d+),\s+(\d+),\s+(\d+)\s+\]/g, '[$1, $2, $3]')}\n`;

export const buildChromiumColours = (id) => {
	const r = browserRoles(id);
	const colours = {
		// Window frame and tabs. The selected tab shares the toolbar colour.
		frame: r.frame,
		frame_inactive: r.frameInactive,
		frame_incognito: r.frame,
		frame_incognito_inactive: r.frameInactive,
		background_tab: r.frame,
		background_tab_inactive: r.frame,
		tab_text: r.text,
		tab_background_text: r.mutedText,

		// Toolbar and the address bar
		toolbar: r.toolbar,
		toolbar_button_icon: r.icon,
		bookmark_text: r.text,
		omnibox_background: r.field,
		omnibox_text: r.text,

		// New tab page
		ntp_background: r.surface,
		ntp_text: r.text,
		ntp_link: r.link,
	};
	return Object.fromEntries(Object.entries(colours).map(([key, hex]) => [key, rgbArray(hex)]));
};

export const buildChromiumTheme = (id) => ({
	manifest_version: 3,
	name: browserVariants[id].label,
	version,
	description: `Afterglow by Liminal HQ: ${browserVariants[id].summary}.`,
	theme: { colors: buildChromiumColours(id) },
});

if (process.argv[1] === fileURLToPath(import.meta.url)) {
	rmSync(join(root, 'chromium', 'themes'), { recursive: true, force: true });
	for (const id of Object.keys(browserVariants)) {
		mkdirSync(join(root, 'chromium', 'themes', id), { recursive: true });
		writeFileSync(
			join(root, 'chromium', 'themes', id, 'manifest.json'),
			serialiseChromium(buildChromiumTheme(id)),
		);
		console.log(`wrote chromium/themes/${id}/manifest.json`);
	}
}
