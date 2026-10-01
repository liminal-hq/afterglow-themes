// Build the Afterglow hue ramps and describe the three shared theme variants
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { mix } from './colour.mjs';
import { STEPS, brand, deep, neutrals } from './palette.mjs';

export const HUES = ['gray', 'red', 'orange', 'yellow', 'green', 'cyan', 'blue', 'purple'];

// Dark ramps run light (100) to dark (900) and light ramps run dark (100) to light (900).
// The brand colour sits on step 200 in both so token references behave the same in either mode.
export const ramp = (anchor, mode, surface) => {
	const lift = mode === 'dark' ? '#ffffff' : '#000000';
	const t =
		mode === 'dark'
			? [0.45, 0, 0.18, 0.36, 0.52, 0.67, 0.8, 0.9, 0.96]
			: [0.35, 0, 0.22, 0.42, 0.58, 0.72, 0.84, 0.92, 0.97];
	return Object.fromEntries(
		STEPS.map((step, i) => [
			step,
			i === 0 ? mix(anchor, lift, t[0]) : i === 1 ? anchor : mix(anchor, surface, t[i]),
		]),
	);
};

// The eight base hue ramps for a mode, fading towards that mode's background
export const baseHues = (mode, neutral) => {
	const anchors = mode === 'dark' ? brand : deep;
	return Object.fromEntries(HUES.map((name) => [name, ramp(anchors[name], mode, neutral[900])]));
};

// The same ramps plus the `accent`, `interactive` and `neutral` hues resolved to real colours
export const resolvedHues = (variant) => {
	const base = baseHues(variant.mode, variant.neutral);
	return {
		...base,
		accent: base[variant.accent],
		interactive: base[variant.interactive],
		neutral: variant.neutral,
	};
};

// What each variant is made of, shared by every generator
export const variants = {
	// The signature theme: the liminalhq.ca void with brand orange and purple
	afterglow: { mode: 'dark', neutral: neutrals.void, accent: 'orange', interactive: 'purple' },
	'afterglow-dark': {
		mode: 'dark',
		neutral: neutrals.indigo,
		accent: 'purple',
		interactive: 'blue',
	},
	'afterglow-light': {
		mode: 'light',
		neutral: neutrals.paper,
		accent: 'purple',
		interactive: 'blue',
	},
};
