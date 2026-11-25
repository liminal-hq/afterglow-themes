// Map the shared Afterglow hue ramps onto the roles every browser theme needs
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { toRgb } from './colour.mjs';
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
// How much of the header glow shows through the toolbar and selected tab
export const TOOLBAR_ALPHA = 0.55;

// The translucent fill that looks like `target` when laid over `base`, so the toolbar keeps its
// raised shade over the flat frame but lets the glow behind it show. Solves `base + (fill - base)
// * alpha = target` for each channel.
export const overlayFill = (target, base, alpha) => {
	const [t, b] = [toRgb(target), toRgb(base)];
	const fill = t.map((v, i) => Math.min(255, Math.max(0, Math.round(b[i] + (v - b[i]) / alpha))));
	return `rgba(${fill.join(', ')}, ${alpha})`;
};

export const browserRoles = (id) => {
	const variant = variants[id];
	const H = resolvedHues(variant);
	const N = variant.neutral;
	// A faint wash of the two hues in the corners of the header, as on liminalhq.ca. The light
	// theme stays flat because a tint on paper reads as a stain rather than a glow.
	const glow =
		variant.mode === 'dark'
			? {
					right: { colour: H.accent[200], opacity: 0.14 },
					left: { colour: H.interactive[200], opacity: 0.1 },
				}
			: null;
	return {
		dark: variant.mode === 'dark',
		surface: N[900],
		frame: N[900],
		frameInactive: N[800],
		toolbar: N[800],
		// Firefox only: with a glow the toolbar and selected tab are translucent so it shows through
		toolbarFill: glow ? overlayFill(N[800], N[900], TOOLBAR_ALPHA) : N[800],
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
		glow,
	};
};
