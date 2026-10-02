// Map the shared Afterglow hue ramps onto the roles every browser theme needs
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { resolvedHues, variants } from './hues.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

export const { version } = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));

// Labels and ids shared by the Firefox and Chromium packages
export const browserVariants = {
	afterglow: { label: 'Afterglow', summary: 'the void with the orange accent' },
	'afterglow-dark': { label: 'Afterglow Dark', summary: 'solid deep indigo-black' },
	'afterglow-light': { label: 'Afterglow Light', summary: 'warm paper' },
};

// Browsers draw their own chrome on one opaque surface, so there is no see-through variant.
// Step meanings match the other themes: neutral 900 is the page surface, 800 a raised surface,
// 200 body text, 400 muted text, and a hue's step 200 is its main colour. The frame (the strip
// behind the tabs) is the page surface and the selected tab joins the toolbar, so the active tab
// reads as one piece with the bar under it.
export const browserRoles = (id) => {
	const variant = variants[id];
	const H = resolvedHues(variant);
	const N = variant.neutral;
	return {
		dark: variant.mode === 'dark',
		surface: N[900],
		frame: N[900],
		frameInactive: N[800],
		toolbar: N[800],
		field: N[900],
		raised: N[800],
		text: N[200],
		strongText: N[100],
		mutedText: N[400],
		icon: N[300],
		border: N[600],
		hover: N[700],
		pressed: N[600],
		accent: H.accent[200],
		link: H.interactive[200],
		focus: H.interactive[200],
		selection: H.interactive[600],
	};
};
