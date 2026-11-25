// Generate the Afterglow desktop wallpapers (one dusk scene, many palettes) from the shared palette
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { mix } from './colour.mjs';
import { brand, deep, neutrals } from './palette.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
export const wallpaperDir = join(root, 'assets', 'wallpapers');

// The canvas every wallpaper is drawn on. Renders scale it to each screen size.
export const WIDTH = 3840;
export const HEIGHT = 2160;
export const MODES = ['dark', 'light'];
export const STYLES = ['stepped', 'smooth'];

// The palettes, each a set of roles named after the shared palette in `scripts/palette.mjs`:
// `neutral` is a neutral ramp, `sun` and `glow` are brand hues. The glow runs from the sun
// outwards through its hues in order, so the first hue sits nearest the sun and the last tints
// the open sky and the paper horizons. Light modes use the warm paper ramp, and tint the
// horizons with the deeper hues that hold contrast on paper.
export const WALLPAPER_PALETTES = {
	dusk: {
		summary: 'the signature scene: orange, rose and purple over the void',
		dark: { neutral: 'void', sun: 'yellow', glow: ['orange', 'red', 'purple'] },
		light: { neutral: 'paper', sun: 'yellow', glow: ['orange', 'red', 'purple'] },
	},
	indigo: {
		summary: 'deep indigo-black with purple and blue, as in `afterglow-dark`',
		dark: { neutral: 'indigo', sun: 'orange', glow: ['purple', 'blue'] },
		light: { neutral: 'paper', sun: 'orange', glow: ['purple', 'blue'] },
	},
	ember: {
		summary: 'a hotter sunset: gold, orange and rose',
		dark: { neutral: 'void', sun: 'yellow', glow: ['yellow', 'orange', 'red'] },
		light: { neutral: 'paper', sun: 'yellow', glow: ['yellow', 'orange', 'red'] },
	},
	aurora: {
		summary: 'a cool polar glow: green, cyan and blue',
		dark: { neutral: 'indigo', sun: 'cyan', glow: ['green', 'cyan', 'blue', 'purple'] },
		light: { neutral: 'paper', sun: 'cyan', glow: ['green', 'cyan', 'blue', 'purple'] },
	},
	graphite: {
		summary: 'a near-neutral slate glow with a faint warm sun',
		dark: { neutral: 'void', sun: 'orange', glow: ['orange', 'gray', 'gray'] },
		light: { neutral: 'paper', sun: 'orange', glow: ['orange', 'gray', 'gray'] },
	},
};

// How strongly each part of the scene takes its colour. A glow colour is the horizon sky mixed
// towards the glow hue by `peak * (1 - r) ** falloff`, where r runs from 0 at the sun to 1 at the
// glow's outer edge, so the light fades smoothly and the centre of the screen stays quiet.
// `hueSpan` is how far out the hues travel before the last one takes over. Graphite's glow is
// mostly grey, and grey darkens paper, so it gets less of it.
export const LIGHT = {
	dark: { peak: 0.56, falloff: 2.4, hueSpan: 0.45, skyTint: 0.05, sunLift: 0.2 },
	light: { peak: 0.46, falloff: 2.3, hueSpan: 0.45, skyTint: 0.04, sunLift: 0.5 },
	graphite: { peak: 0.4 },
};

// The scene, in canvas units. The low sun sits in the lower right third, outside the calm
// central 60% (x 768 to 3072, y 432 to 1728) and inside the 4:3 centre crop (x 480 to 3360).
export const SUN = { cx: 2880, cy: 1846, r: 104 };
// The sun's halo, outermost first: each step's radius in sun radii and how far it lifts the glow
export const HALO = [
	{ scale: 2.2, lift: 0.14 },
	{ scale: 1.7, lift: 0.26 },
	{ scale: 1.3, lift: 0.4 },
];
export const GLOW = { cx: 2880, cy: 1846, rx: 4300, ry: 1760, bands: 18, spacing: 1.3 };
export const SKY_BANDS = [0, 540, 1080, 1520, HEIGHT];
// The calm centre the validator measures, and where a taskbar or a top panel sits
export const CENTRE = { x: [768, 3072], y: [432, 1728] };
export const TASKBAR = 96;

// Three paper horizons, back to front. Each crest is a curve the sheet fills down from, and its
// edge catches a little of the glow.
export const HORIZONS = [
	{
		crest: 'M0 1800C420 1752 960 1748 1500 1800S2500 1862 2960 1846S3600 1768 3840 1772',
		edge: 0.34,
	},
	{ crest: 'M0 1924C600 1878 1240 1934 1900 1950S3000 1888 3840 1926', edge: 0.2 },
	{ crest: 'M0 2046C700 2008 1500 1992 2300 2024S3300 2056 3840 2010', edge: 0.1 },
];

// Small stars for the dark modes, kept to the upper sky and away from the icon column
export const STARS = [
	[2380, 150, 3.5, 0.55],
	[2910, 300, 2.5, 0.4],
	[3260, 120, 4, 0.6],
	[3560, 410, 3, 0.45],
	[3720, 210, 2.5, 0.4],
	[3420, 700, 2.5, 0.3],
	[1820, 90, 2.5, 0.35],
	[1240, 200, 3, 0.4],
	[1560, 360, 2, 0.25],
	[760, 110, 2.5, 0.3],
	[3700, 860, 2, 0.25],
	[3340, 560, 2, 0.25],
];

export const wallpaperId = (palette, mode, style) => `afterglow-${palette}-${mode}-${style}`;

export const wallpaperIds = () =>
	Object.keys(WALLPAPER_PALETTES).flatMap((palette) =>
		MODES.flatMap((mode) => STYLES.map((style) => wallpaperId(palette, mode, style))),
	);

export const parseId = (id) => {
	const match = /^afterglow-([a-z]+)-(dark|light)-(stepped|smooth)$/.exec(id);
	return match && WALLPAPER_PALETTES[match[1]]
		? { palette: match[1], mode: match[2], style: match[3] }
		: null;
};

const round = (v) => Number(v.toFixed(4));

// The glow edge radii, closer together near the sun, as a fraction of the glow ellipse
const bandEdges = () =>
	Array.from({ length: GLOW.bands }, (_, k) => round(((k + 1) / GLOW.bands) ** GLOW.spacing));

// Every colour a scene uses, resolved from its palette roles
export const sceneColours = (palette, mode) => {
	const roles = WALLPAPER_PALETTES[palette][mode];
	const N = neutrals[roles.neutral];
	const light = { ...LIGHT[mode], ...(palette === 'graphite' ? LIGHT.graphite : {}) };
	const hues = roles.glow.map((name) => brand[name]);
	const outer = hues.at(-1);
	const tint = mode === 'dark' ? brand[roles.glow.at(-1)] : deep[roles.glow.at(-1)];

	// The sky darkens (or, on paper, cools) towards the top
	const skyTop = N[mode === 'dark' ? 900 : 800];
	const horizon = mix(N[mode === 'dark' ? 800 : 900], outer, light.skyTint);

	// The hue at radius r, travelling through the glow hues from the sun outwards
	const hueAt = (r) => {
		if (hues.length === 1) return hues[0];
		const t = Math.min(r / light.hueSpan, 1) * (hues.length - 1);
		const i = Math.min(Math.floor(t), hues.length - 2);
		return mix(hues[i], hues[i + 1], t - i);
	};
	// The sky under the glow runs from the horizon colour at the sun to the top colour at the
	// glow's edge, so the outermost band melts into the sky instead of drawing a dome
	const glowAt = (r) => {
		const s = Math.min(r, 1);
		return mix(mix(horizon, skyTop, s ** 1.5), hueAt(s), light.peak * (1 - s) ** light.falloff);
	};

	const edges = bandEdges();
	const mids = edges.map((e, k) => round(((k === 0 ? 0 : edges[k - 1]) + e) / 2));
	const bands = mids.map(glowAt);

	const sky = SKY_BANDS.slice(0, -1).map((_, i, all) => mix(skyTop, horizon, i / (all.length - 1)));

	// Back to front: lighter sheets behind, the darkest in front where the taskbar sits
	const sheetBase =
		mode === 'dark'
			? [mix(N[800], tint, 0.1), mix(N[900], tint, 0.05), N[900]]
			: [mix(N[700], tint, 0.1), mix(N[600], tint, 0.12), mix(N[400], tint, 0.14)];
	const sheets = sheetBase.map((fill, i) => ({
		fill,
		edge: mix(fill, hues[0], HORIZONS[i].edge),
	}));

	const sunDisc = mix(brand[roles.sun], mode === 'dark' ? bands[0] : N[900], light.sunLift);
	// Each halo step is the glow under it lifted a little towards the sun, so it sits softly in
	// the bands rather than drawing a disc of its own
	const halo = HALO.map(({ scale, lift }) => mix(glowAt((SUN.r * scale) / GLOW.ry), sunDisc, lift));

	return {
		skyTop,
		horizon,
		sky,
		edges,
		mids,
		bands,
		centre: glowAt(0),
		sheets,
		sunDisc,
		halo,
		star: N[200],
		glowAt,
	};
};

const header = (id, summary, style) => `<!--
	Afterglow desktop wallpaper ${id}: ${summary}, ${style === 'stepped' ? 'in flat stepped bands' : 'with smooth gradients'}.
	Generated by scripts/build-wallpapers.mjs from the shared palette; edit the generator, not this file.

	(c) Copyright 2026 Liminal HQ, Scott Morris
	SPDX-License-Identifier: Apache-2.0 OR MIT
-->
`;

const ellipse = (k, edges, fill, extra = '') =>
	`<ellipse cx="${GLOW.cx}" cy="${GLOW.cy}" rx="${round(GLOW.rx * edges[k])}" ry="${round(GLOW.ry * edges[k])}" fill="${fill}"${extra}/>`;

export const wallpaperSvg = (id) => {
	const { palette, mode, style } = parseId(id);
	const c = sceneColours(palette, mode);
	const smooth = style === 'smooth';
	const out = [];
	const add = (line, depth = 1) => out.push(`${'\t'.repeat(depth)}${line}`);

	out.push(header(id, WALLPAPER_PALETTES[palette].summary.replace(/`/g, ''), style));
	out.push(
		`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${WIDTH} ${HEIGHT}" width="${WIDTH}" height="${HEIGHT}" role="img">`,
	);
	add(`<title>Afterglow ${palette}, ${mode}, ${style}</title>`);

	if (smooth) {
		add('<defs>');
		add('<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">', 2);
		c.sky.forEach((colour, i) => {
			const mid = (SKY_BANDS[i] + SKY_BANDS[i + 1]) / 2 / HEIGHT;
			add(`<stop offset="${round(i === 0 ? 0 : mid)}" stop-color="${colour}"/>`, 3);
		});
		add('</linearGradient>', 2);
		add('<radialGradient id="glow" cx=".5" cy=".5" r=".5">', 2);
		add(`<stop offset="0" stop-color="${c.centre}"/>`, 3);
		c.bands.forEach((colour, k) => add(`<stop offset="${c.mids[k]}" stop-color="${colour}"/>`, 3));
		add(`<stop offset="1" stop-color="${c.bands.at(-1)}" stop-opacity="0"/>`, 3);
		add('</radialGradient>', 2);
		add('<radialGradient id="halo" cx=".5" cy=".5" r=".5">', 2);
		add(`<stop offset="0" stop-color="${c.halo[2]}"/>`, 3);
		add(`<stop offset=".45" stop-color="${c.halo[1]}" stop-opacity=".7"/>`, 3);
		add(`<stop offset="1" stop-color="${c.halo[0]}" stop-opacity="0"/>`, 3);
		add('</radialGradient>', 2);
		add('</defs>');
		add('');
		add('<!-- Sky: one vertical gradient through the stepped sky colours -->');
		add(`<rect width="${WIDTH}" height="${HEIGHT}" fill="url(#sky)"/>`);
		add('');
		add(
			'<!-- The afterglow: one radial gradient through the stepped band colours, fading out at its edge -->',
		);
		add(
			`<ellipse cx="${GLOW.cx}" cy="${GLOW.cy}" rx="${GLOW.rx}" ry="${GLOW.ry}" fill="url(#glow)"/>`,
		);
	} else {
		add('<!-- Sky: flat bands, darkest at the top -->');
		c.sky.forEach((colour, i) =>
			add(
				`<rect y="${SKY_BANDS[i]}" width="${WIDTH}" height="${HEIGHT - SKY_BANDS[i]}" fill="${colour}"/>`,
			),
		);
		add('');
		add('<!-- The afterglow: flat concentric bands stepping in towards the sun -->');
		for (let k = GLOW.bands - 1; k >= 0; k--) {
			// Neighbouring bands that round to the same colour are drawn once
			if (k < GLOW.bands - 1 && c.bands[k] === c.bands[k + 1]) continue;
			add(ellipse(k, c.edges, c.bands[k]));
		}
	}

	add('');
	if (mode === 'dark') {
		add('<!-- Stars: a few, small, in the upper sky -->');
		add(`<g fill="${c.star}">`);
		for (const [cx, cy, r, o] of STARS)
			add(`<circle cx="${cx}" cy="${cy}" r="${r}" fill-opacity="${o}"/>`, 2);
		add('</g>');
		add('');
	}

	add('<!-- The low sun, half set behind the back horizon -->');
	if (smooth) {
		add(`<circle cx="${SUN.cx}" cy="${SUN.cy}" r="${SUN.r * 2.6}" fill="url(#halo)"/>`);
	} else {
		HALO.forEach(({ scale }, i) =>
			add(
				`<circle cx="${SUN.cx}" cy="${SUN.cy}" r="${round(SUN.r * scale)}" fill="${c.halo[i]}"/>`,
			),
		);
	}
	add(`<circle cx="${SUN.cx}" cy="${SUN.cy}" r="${SUN.r}" fill="${c.sunDisc}"/>`);
	add('');

	add('<!-- Layered paper horizons, back to front; each crest catches a little of the glow -->');
	HORIZONS.forEach(({ crest }, i) => {
		add(`<path d="${crest}V${HEIGHT}H0Z" fill="${c.sheets[i].fill}"/>`);
		add(
			`<path d="${crest}" fill="none" stroke="${c.sheets[i].edge}" stroke-width="${6 - i * 2}" stroke-linecap="round"/>`,
		);
	});
	out.push('</svg>');
	return `${out.join('\n')}\n`;
};

if (process.argv[1] === fileURLToPath(import.meta.url)) {
	// Start clean so a renamed or removed wallpaper never lingers in the output
	rmSync(wallpaperDir, { recursive: true, force: true });
	mkdirSync(wallpaperDir, { recursive: true });
	for (const id of wallpaperIds()) {
		writeFileSync(join(wallpaperDir, `${id}.svg`), wallpaperSvg(id));
		console.log(`wrote assets/wallpapers/${id}.svg`);
	}
}
