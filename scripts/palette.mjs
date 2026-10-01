// Liminal HQ Afterglow colour palette, distilled from the liminal-hq GitHub organisation
//
// Sources: liminal-hq.github.io (brand tokens), threshold, cadence, jar, foyer, smdu, waypoint
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

export const STEPS = [100, 200, 300, 400, 500, 600, 700, 800, 900];

// Brand colours as used on liminalhq.ca (the "signature" accents)
export const brand = {
	void: '#050507',
	text: '#e0e0e0',
	textMuted: '#b4bfce',
	orange: '#ffaa40',
	red: '#f43f5e',
	purple: '#a78bfa',
	cyan: '#22d3ee',
	blue: '#60a5fa',
	// Supporting colours that recur across the app and TUI repos
	green: '#2ec66a',
	yellow: '#fbbf24',
	gray: '#94a3b8',
};

// Deeper variants of the same hues that hold 4.5:1 contrast on warm paper (jar #fbfaf6, cadence #5e44cc)
export const deep = {
	orange: '#b45309',
	red: '#be123c',
	purple: '#5e44cc',
	cyan: '#0e7490',
	blue: '#2563eb',
	green: '#15803d',
	yellow: '#a16207',
	gray: '#5a6a80',
};

// Hand-tuned neutral ramps. 100 is the strongest contrast with the background and 900 is the background itself
export const neutrals = {
	void: {
		100: '#f4f4f8',
		200: '#e0e0e0',
		300: '#b4bfce',
		400: '#8d97a8',
		500: '#5a6273',
		600: '#333847',
		700: '#1f2230',
		800: '#12121a',
		900: '#050507',
	},
	indigo: {
		100: '#f1eee6',
		200: '#e4e2ec',
		300: '#b8b6c8',
		400: '#8f8da6',
		500: '#5f5d78',
		600: '#3a384f',
		700: '#2a2840',
		800: '#1a1828',
		900: '#0f0e1a',
	},
	paper: {
		100: '#1c1b20',
		200: '#2b2a33',
		300: '#484554',
		400: '#6b6877',
		500: '#8f8c98',
		600: '#c9c5d0',
		700: '#e6e0eb',
		800: '#f2eff4',
		900: '#fbfaf6',
	},
};
