// Validate the Afterglow desktop wallpapers: palette roles, drift, self-contained SVG and contrast
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
	CENTRE,
	GLOW,
	HEIGHT,
	HORIZONS,
	MODES,
	TASKBAR,
	WALLPAPER_PALETTES,
	WIDTH,
	parseId,
	sceneColours,
	wallpaperDir,
	wallpaperIds,
	wallpaperSvg,
} from './build-wallpapers.mjs';
import { contrast } from './colour.mjs';
import { brand, neutrals } from './palette.mjs';

// Desktop icon labels: white (with the usual dark shadow) on a dark wallpaper, and the paper
// theme's text colour on a light one. A taskbar or panel is assumed to carry light text.
const LABEL = { dark: '#ffffff', light: neutrals.paper[100] };
const TASKBAR_TEXT = '#ffffff';

// The y of every point and control point on a crest path (its numbers are x, y pairs)
const crestYs = (crest) =>
	[...crest.matchAll(/-?\d+(?:\.\d+)?/g)].map(Number).filter((_, i) => i % 2 === 1);

// Every role in the palette table names a real neutral ramp or brand hue
export const validatePalettes = () => {
	const errors = [];
	for (const [palette, spec] of Object.entries(WALLPAPER_PALETTES)) {
		if (!/^[a-z]+$/.test(palette)) errors.push(`${palette}: palette names are lower-case words`);
		for (const mode of MODES) {
			const roles = spec[mode];
			if (!roles) {
				errors.push(`${palette}: no ${mode} roles`);
				continue;
			}
			if (!neutrals[roles.neutral])
				errors.push(`${palette}-${mode}: unknown neutral ${roles.neutral}`);
			for (const hue of [roles.sun, ...(roles.glow ?? [])])
				if (!brand[hue] || hue === 'void' || hue.startsWith('text'))
					errors.push(`${palette}-${mode}: unknown hue ${hue}`);
			if (!roles.glow?.length) errors.push(`${palette}-${mode}: the glow needs at least one hue`);
		}
	}
	return errors;
};

// One wallpaper's SVG text: the generated scene, self-contained, in its palette's colours only
export const validateWallpaper = (id, svg) => {
	const errors = [];
	const parsed = parseId(id);
	if (!parsed) return [`${id}: not an afterglow-<palette>-<mode>-<style> name`];
	if (svg !== wallpaperSvg(id))
		errors.push(`${id}: differs from what the palette generates (run bun run build)`);
	if (!svg.includes(`viewBox="0 0 ${WIDTH} ${HEIGHT}"`))
		errors.push(`${id}: canvas is not ${WIDTH}x${HEIGHT}`);
	if (!svg.includes('SPDX-License-Identifier: Apache-2.0 OR MIT'))
		errors.push(`${id}: no licence header`);
	if (/<(image|script|foreignObject|use)\b|href=|@import|url\((?!#)/.test(svg))
		errors.push(`${id}: refers to something outside the file`);
	const defined = new Set([...svg.matchAll(/\bid="([^"]+)"/g)].map((m) => m[1]));
	for (const [, ref] of svg.matchAll(/url\(#([^)]+)\)/g))
		if (!defined.has(ref)) errors.push(`${id}: url(#${ref}) is not defined`);

	const c = sceneColours(parsed.palette, parsed.mode);
	const allowed = new Set(
		[c.skyTop, c.horizon, c.centre, c.star, c.sunDisc, ...c.sky, ...c.bands, ...c.halo]
			.concat(c.sheets.flatMap((s) => [s.fill, s.edge]))
			.map((v) => v.toLowerCase()),
	);
	for (const [hex] of svg.matchAll(/#[\da-f]{6}\b/gi))
		if (!allowed.has(hex.toLowerCase())) errors.push(`${id}: ${hex} is not a palette colour`);
	return errors;
};

// Icon labels in the calm centre and taskbar text over the front horizon keep 4.5:1
export const validateContrast = (palette, mode) => {
	const errors = [];
	const c = sceneColours(palette, mode);
	const label = LABEL[mode];
	let worst = Infinity;
	for (let x = CENTRE.x[0]; x <= CENTRE.x[1]; x += 32)
		for (let y = CENTRE.y[0]; y <= CENTRE.y[1]; y += 32) {
			const r = Math.hypot((x - GLOW.cx) / GLOW.rx, (y - GLOW.cy) / GLOW.ry);
			worst = Math.min(worst, contrast(label, c.glowAt(r)));
		}
	if (worst < 4.5)
		errors.push(`${palette}-${mode}: icon labels reach only ${worst.toFixed(2)}:1 in the centre`);
	const front = c.sheets.at(-1).fill;
	const bar = contrast(TASKBAR_TEXT, front);
	if (bar < 4.5)
		errors.push(`${palette}-${mode}: taskbar text on ${front} is only ${bar.toFixed(2)}:1`);
	// The front sheet covers the whole taskbar strip, and no horizon rises into the calm centre
	if (Math.max(...crestYs(HORIZONS.at(-1).crest)) > HEIGHT - TASKBAR)
		errors.push(`${palette}-${mode}: the front horizon dips into the taskbar strip`);
	if (Math.min(...HORIZONS.flatMap((h) => crestYs(h.crest))) < CENTRE.y[1])
		errors.push(`${palette}-${mode}: a horizon rises into the calm centre`);
	return { errors, label: worst, taskbar: bar };
};

if (process.argv[1] === fileURLToPath(import.meta.url)) {
	let failed = false;
	const report = (name, errors) => {
		if (errors.length) {
			failed = true;
			console.error(`✗ ${name}`);
			for (const e of errors) console.error(`  ${e}`);
		}
	};
	report('wallpaper palettes', validatePalettes());
	const expected = new Set(wallpaperIds().map((id) => `${id}.svg`));
	const present = existsSync(wallpaperDir) ? readdirSync(wallpaperDir) : [];
	report('assets/wallpapers', [
		...[...expected].filter((f) => !present.includes(f)).map((f) => `${f} is missing`),
		...present.filter((f) => !expected.has(f)).map((f) => `${f} is not generated by the palette`),
	]);
	for (const id of wallpaperIds()) {
		const file = join(wallpaperDir, `${id}.svg`);
		if (!existsSync(file)) continue;
		const errors = validateWallpaper(id, readFileSync(file, 'utf8'));
		report(id, errors);
		if (!errors.length) console.log(`✓ ${id}`);
	}
	for (const palette of Object.keys(WALLPAPER_PALETTES))
		for (const mode of MODES) {
			const { errors, label, taskbar } = validateContrast(palette, mode);
			report(`${palette}-${mode} contrast`, errors);
			if (!errors.length)
				console.log(
					`✓ ${palette}-${mode}: icon labels at least ${label.toFixed(2)}:1, taskbar text ${taskbar.toFixed(2)}:1`,
				);
		}
	process.exit(failed ? 1 : 0);
}
