// Generate the Afterglow Firefox themes (WebExtension theme manifests) from the shared palette
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { browserRoles, browserVariants, version } from './browser-roles.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

// Firefox identifies an add-on by this id, so it must stay the same from release to release
export const firefoxId = (id) => `${id}@liminalhq.ca`;

export const buildFirefoxColours = (id) => {
	const r = browserRoles(id);
	return {
		// Window frame and tabs. The selected tab shares the toolbar colour.
		frame: r.frame,
		frame_inactive: r.frameInactive,
		tab_background_text: r.mutedText,
		tab_selected: r.toolbar,
		tab_text: r.text,
		tab_line: r.accent,
		tab_loading: r.accent,

		// Toolbar and the address bar
		toolbar: r.toolbar,
		toolbar_text: r.text,
		toolbar_top_separator: r.border,
		toolbar_bottom_separator: r.border,
		toolbar_vertical_separator: r.border,
		toolbar_field: r.field,
		toolbar_field_text: r.text,
		toolbar_field_border: r.border,
		toolbar_field_focus: r.field,
		toolbar_field_text_focus: r.strongText,
		toolbar_field_border_focus: r.focus,
		toolbar_field_highlight: r.selection,
		toolbar_field_highlight_text: r.strongText,
		bookmark_text: r.text,
		icons: r.icon,
		icons_attention: r.accent,
		button_background_hover: r.hover,
		button_background_active: r.pressed,

		// Menus, panels and the sidebar
		popup: r.raised,
		popup_text: r.text,
		popup_border: r.border,
		popup_highlight: r.selection,
		popup_highlight_text: r.strongText,
		sidebar: r.raised,
		sidebar_text: r.text,
		sidebar_border: r.border,
		sidebar_highlight: r.selection,
		sidebar_highlight_text: r.strongText,

		// New tab page
		ntp_background: r.surface,
		ntp_text: r.text,
		ntp_card_background: r.raised,
	};
};

export const buildFirefoxTheme = (id) => ({
	manifest_version: 2,
	name: browserVariants[id].label,
	version,
	description: `Afterglow by Liminal HQ: ${browserVariants[id].summary}.`,
	author: 'Liminal HQ, Scott Morris',
	homepage_url: 'https://github.com/liminal-hq/afterglow-themes',
	browser_specific_settings: { gecko: { id: firefoxId(id), strict_min_version: '115.0' } },
	theme: {
		colors: buildFirefoxColours(id),
		properties: { color_scheme: browserRoles(id).dark ? 'dark' : 'light' },
	},
});

if (process.argv[1] === fileURLToPath(import.meta.url)) {
	// Start clean so a renamed or removed theme never lingers in the output
	rmSync(join(root, 'firefox', 'themes'), { recursive: true, force: true });
	for (const id of Object.keys(browserVariants)) {
		mkdirSync(join(root, 'firefox', 'themes', id), { recursive: true });
		writeFileSync(
			join(root, 'firefox', 'themes', id, 'manifest.json'),
			`${JSON.stringify(buildFirefoxTheme(id), null, '\t')}\n`,
		);
		console.log(`wrote firefox/themes/${id}/manifest.json`);
	}
}
