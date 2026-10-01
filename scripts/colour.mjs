// Small colour helpers for building hue ramps and checking contrast
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

export const toRgb = (hex) => {
	const h = hex.replace('#', '');
	return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
};

export const toHex = (rgb) =>
	`#${rgb.map((v) => Math.round(v).toString(16).padStart(2, '0')).join('')}`;

// Mix `a` towards `b` by `t` (0 keeps `a`, 1 gives `b`)
export const mix = (a, b, t) => {
	const [ar, ag, ab] = toRgb(a);
	const [br, bg, bb] = toRgb(b);
	return toHex([ar + (br - ar) * t, ag + (bg - ag) * t, ab + (bb - ab) * t]);
};

const channel = (v) => {
	const s = v / 255;
	return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
};

export const luminance = (hex) => {
	const [r, g, b] = toRgb(hex);
	return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);
};

export const contrast = (a, b) => {
	const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
	return (hi + 0.05) / (lo + 0.05);
};

// Composite a colour that may carry an alpha channel (`#rrggbbaa`) over an opaque base colour
export const over = (top, base) => {
	if (top.length !== 9) return top;
	const alpha = parseInt(top.slice(7), 16) / 255;
	return mix(base.slice(0, 7), top.slice(0, 7), alpha);
};
