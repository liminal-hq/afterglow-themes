// Generate the Afterglow desktop wallpapers, dusk in dark and day in light, from the shared palette
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
// `neutral` is a neutral ramp, `sun` and `glow` are brand hues. In the dark dusk scenes the glow
// runs from the setting sun outwards through its hues in order, so the first hue sits nearest the
// sun and the last tints the open sky and the horizons. The light scenes are the same place in
// daylight on the warm paper ramp: `sky` tints the upper sky, the glow is the sun's light spreading
// from high in the sky, and `hills` tints the horizons with its deeper hue.
export const WALLPAPER_PALETTES = {
	dusk: {
		summary: 'the signature scene: orange, rose and purple over the void',
		daySummary: 'the signature scene by day: a gold sun high over warm paper and lilac hills',
		dark: { neutral: 'void', sun: 'yellow', glow: ['orange', 'red', 'purple'] },
		light: {
			neutral: 'paper',
			sun: 'yellow',
			glow: ['yellow', 'orange'],
			sky: 'orange',
			hills: 'purple',
		},
	},
	indigo: {
		summary: 'deep indigo-black with purple and blue, as in `afterglow-dark`',
		daySummary: 'indigo by day: a gold sun in a lavender and blue sky',
		dark: { neutral: 'indigo', sun: 'orange', glow: ['purple', 'blue'] },
		light: {
			neutral: 'paper',
			sun: 'orange',
			glow: ['orange', 'purple'],
			sky: 'purple',
			hills: 'blue',
		},
	},
	ember: {
		summary: 'a hotter sunset: gold, orange and rose',
		daySummary: 'a hot bright day: gold and orange over rose hills',
		dark: { neutral: 'void', sun: 'yellow', glow: ['yellow', 'orange', 'red'] },
		light: {
			neutral: 'paper',
			sun: 'yellow',
			glow: ['yellow', 'orange'],
			sky: 'yellow',
			hills: 'red',
		},
	},
	aurora: {
		summary: 'a cool polar glow: green, cyan and blue',
		daySummary: 'a cool clear day: a pale sun in cyan and blue over green hills',
		dark: { neutral: 'indigo', sun: 'cyan', glow: ['green', 'cyan', 'blue', 'purple'] },
		light: {
			neutral: 'paper',
			sun: 'yellow',
			glow: ['cyan', 'blue'],
			sky: 'blue',
			hills: 'green',
		},
	},
	graphite: {
		summary: 'a near-neutral slate glow with a faint warm sun',
		daySummary: 'a near-neutral slate day with a soft warm sun',
		dark: { neutral: 'void', sun: 'orange', glow: ['orange', 'gray', 'gray'] },
		light: {
			neutral: 'paper',
			sun: 'orange',
			glow: ['orange', 'gray'],
			sky: 'gray',
			hills: 'gray',
		},
	},
};

// How strongly each part of the dusk scene takes its colour. A glow colour is the horizon sky
// mixed towards the glow hue by `peak * (1 - r) ** falloff`, where r runs from 0 at the sun to 1 at
// the glow's outer edge, so the light fades smoothly and the centre of the screen stays quiet.
// `hueSpan` is how far out the hues travel before the last one takes over. Graphite's glow is
// mostly grey, which reads as a smudge, so it gets less of it.
export const LIGHT = {
	dark: { peak: 0.56, falloff: 2.4, hueSpan: 0.45, skyTint: 0.05, sunLift: 0.2 },
	graphite: { peak: 0.4 },
};

// The daytime scene. The sky is paper tinted with the sky hue, by `skyTop` at the top and
// `skyHorizon` low down, where the air is hazy and brightest. The sun's light is a wash laid over
// the sky: each glow hue lifted `glare` towards paper, at an opacity of
// `peak * (1 - r) ** falloff`. The sun is paper tinted `sunTint` with its hue, the brightest thing
// in the sky, and its halo steps lay the sun colour over the wash at each step's opacity. The
// hills are paper tinted with the deeper `hills` hue, faintest at the back.
export const DAY = {
	skyTop: 0.26,
	skyHorizon: 0.03,
	glare: 0.35,
	peak: 0.7,
	falloff: 1.8,
	hueSpan: 0.55,
	sunTint: 0.1,
	halo: [0.35, 0.55, 0.8],
	hills: [0.16, 0.28, 0.42],
	edge: 0.55,
};

// The dusk scene, in canvas units. The low sun sits in the lower right third, outside the calm
// central 60% (x 768 to 3072, y 432 to 1728) and inside the 4:3 centre crop (x 480 to 3360).
export const SUN = { cx: 2880, cy: 1846, r: 104 };
// The sun's halo, outermost first: each step's radius in sun radii and how far it lifts the glow
export const HALO = [
	{ scale: 2.2, lift: 0.14 },
	{ scale: 1.7, lift: 0.26 },
	{ scale: 1.3, lift: 0.4 },
];
export const GLOW = { cx: 2880, cy: 1846, rx: 4300, ry: 1760, bands: 18, spacing: 1.3 };
// The daytime sun stands high in the upper right, above the calm centre and inside the 4:3 crop,
// and its light spreads from there across the upper sky
export const DAY_SUN = { cx: 2960, cy: 300, r: 112 };
// How far the smooth halo fades out, in sun radii
const DAY_HALO_REACH = 2.6;
export const DAY_GLOW = { cx: 2960, cy: 300, rx: 3400, ry: 2100, bands: 18, spacing: 1.3 };
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

// Every colour a daytime scene uses, resolved from its palette roles
const dayColours = (palette) => {
	const roles = WALLPAPER_PALETTES[palette].light;
	const N = neutrals[roles.neutral];
	const paper = N[900];
	const hues = roles.glow.map((name) => brand[name]);
	const skyTop = mix(paper, brand[roles.sky], DAY.skyTop);
	const horizon = mix(paper, brand[roles.sky], DAY.skyHorizon);
	const sky = SKY_BANDS.slice(0, -1).map((_, i, all) => mix(skyTop, horizon, i / (all.length - 1)));

	const hueAt = (r) => {
		if (hues.length === 1) return hues[0];
		const t = Math.min(r / DAY.hueSpan, 1) * (hues.length - 1);
		const i = Math.min(Math.floor(t), hues.length - 2);
		return mix(hues[i], hues[i + 1], t - i);
	};
	// The sun's light at radius r: a colour and the opacity it is laid over the sky with
	const washAt = (r) => {
		const s = Math.min(r, 1);
		return {
			fill: mix(hueAt(s), paper, DAY.glare),
			alpha: round(DAY.peak * (1 - s) ** DAY.falloff),
		};
	};
	const edges = bandEdges();
	const mids = edges.map((e, k) => round(((k === 0 ? 0 : edges[k - 1]) + e) / 2));
	const wash = mids.map(washAt);
	// The colour a stepped wallpaper shows at a canvas point above the hills
	const skyAt = (y) => sky[SKY_BANDS.findLastIndex((top, i) => i < sky.length && top <= y)];
	const colourAt = (x, y) => {
		const r = Math.hypot((x - DAY_GLOW.cx) / DAY_GLOW.rx, (y - DAY_GLOW.cy) / DAY_GLOW.ry);
		const k = edges.findIndex((e) => r <= e);
		return k === -1 ? skyAt(y) : mix(skyAt(y), wash[k].fill, wash[k].alpha);
	};

	const sunDisc = mix(paper, brand[roles.sun], DAY.sunTint);
	const sheets = DAY.hills.map((t) => {
		const fill = mix(paper, deep[roles.hills], t);
		return { fill, edge: mix(fill, paper, DAY.edge) };
	});
	return {
		skyTop,
		horizon,
		sky,
		edges,
		mids,
		wash,
		centre: washAt(0),
		sheets,
		sunDisc,
		colourAt,
	};
};

// Every colour a scene uses, resolved from its palette roles. `colourAt` is the colour of the sky
// and the glow at a canvas point above the horizons, for the contrast check.
export const sceneColours = (palette, mode) => {
	if (mode === 'light') return dayColours(palette);
	const roles = WALLPAPER_PALETTES[palette][mode];
	const N = neutrals[roles.neutral];
	const light = { ...LIGHT.dark, ...(palette === 'graphite' ? LIGHT.graphite : {}) };
	const hues = roles.glow.map((name) => brand[name]);
	const outer = hues.at(-1);
	const tint = brand[roles.glow.at(-1)];

	// The sky darkens towards the top
	const skyTop = N[900];
	const horizon = mix(N[800], outer, light.skyTint);

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
	const sheetBase = [mix(N[800], tint, 0.1), mix(N[900], tint, 0.05), N[900]];
	const sheets = sheetBase.map((fill, i) => ({
		fill,
		edge: mix(fill, hues[0], HORIZONS[i].edge),
	}));

	const sunDisc = mix(brand[roles.sun], bands[0], light.sunLift);
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
		colourAt: (x, y) => glowAt(Math.hypot((x - GLOW.cx) / GLOW.rx, (y - GLOW.cy) / GLOW.ry)),
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

// An ellipse as a path, so rings can be cut with the even-odd rule
const ellipsePath = (cx, cy, rx, ry) =>
	`M${round(cx - rx)} ${cy}a${rx} ${ry} 0 1 0 ${round(2 * rx)} 0a${rx} ${ry} 0 1 0 ${round(-2 * rx)} 0Z`;

// The daytime sky, the sun's light washed over it and the high sun with its halo
const daySky = (c, smooth, add) => {
	const { cx, cy, rx, ry } = DAY_GLOW;
	if (smooth) {
		add('<defs>');
		add('<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">', 2);
		c.sky.forEach((colour, i) => {
			const mid = (SKY_BANDS[i] + SKY_BANDS[i + 1]) / 2 / HEIGHT;
			add(`<stop offset="${round(i === 0 ? 0 : mid)}" stop-color="${colour}"/>`, 3);
		});
		add('</linearGradient>', 2);
		add('<radialGradient id="light" cx=".5" cy=".5" r=".5">', 2);
		add(`<stop offset="0" stop-color="${c.centre.fill}" stop-opacity="${c.centre.alpha}"/>`, 3);
		c.wash.forEach(({ fill, alpha }, k) =>
			add(`<stop offset="${c.mids[k]}" stop-color="${fill}" stop-opacity="${alpha}"/>`, 3),
		);
		add(`<stop offset="1" stop-color="${c.wash.at(-1).fill}" stop-opacity="0"/>`, 3);
		add('</radialGradient>', 2);
		add('<radialGradient id="halo" cx=".5" cy=".5" r=".5">', 2);
		// A stop at the middle of each stepped halo ring at that ring's strength, out to 2.6 radii
		const reach = DAY_HALO_REACH;
		const rings = [1, ...[...HALO].reverse().map((h) => h.scale)];
		add(`<stop offset="0" stop-color="${c.sunDisc}" stop-opacity="${DAY.halo[2]}"/>`, 3);
		[...DAY.halo].reverse().forEach((alpha, i) => {
			const mid = round((rings[i] + rings[i + 1]) / 2 / reach);
			add(`<stop offset="${mid}" stop-color="${c.sunDisc}" stop-opacity="${alpha}"/>`, 3);
		});
		add(`<stop offset="1" stop-color="${c.sunDisc}" stop-opacity="0"/>`, 3);
		add('</radialGradient>', 2);
		add('</defs>');
		add('');
		add('<!-- Sky: one vertical gradient through the stepped sky colours, brightest low down -->');
		add(`<rect width="${WIDTH}" height="${HEIGHT}" fill="url(#sky)"/>`);
		add('');
		add('<!-- Daylight: one radial wash from the sun, fading out at its edge -->');
		add(`<ellipse cx="${cx}" cy="${cy}" rx="${rx}" ry="${ry}" fill="url(#light)"/>`);
		add('');
		add('<!-- The sun, high in the sky -->');
		add(
			`<circle cx="${DAY_SUN.cx}" cy="${DAY_SUN.cy}" r="${DAY_SUN.r * DAY_HALO_REACH}" fill="url(#halo)"/>`,
		);
	} else {
		add('<!-- Sky: flat bands, brightest low down -->');
		c.sky.forEach((colour, i) =>
			add(
				`<rect y="${SKY_BANDS[i]}" width="${WIDTH}" height="${HEIGHT - SKY_BANDS[i]}" fill="${colour}"/>`,
			),
		);
		add('');
		add('<!-- Daylight: flat rings of light stepping in towards the sun -->');
		for (let k = DAY_GLOW.bands - 1; k >= 0; k--) {
			const outer = ellipsePath(cx, cy, round(rx * c.edges[k]), round(ry * c.edges[k]));
			const inner =
				k === 0 ? '' : ellipsePath(cx, cy, round(rx * c.edges[k - 1]), round(ry * c.edges[k - 1]));
			const { fill, alpha } = c.wash[k];
			add(
				`<path d="${outer}${inner}" fill="${fill}" fill-opacity="${alpha}" fill-rule="evenodd"/>`,
			);
		}
		add('');
		add('<!-- The sun, high in the sky -->');
		// Each step is laid over the one outside it, so its own opacity is what brings the stack up
		// to that step's halo strength
		HALO.forEach(({ scale }, i) => {
			const opacity = i === 0 ? DAY.halo[0] : 1 - (1 - DAY.halo[i]) / (1 - DAY.halo[i - 1]);
			add(
				`<circle cx="${DAY_SUN.cx}" cy="${DAY_SUN.cy}" r="${round(DAY_SUN.r * scale)}" fill="${c.sunDisc}" fill-opacity="${round(opacity)}"/>`,
			);
		});
	}
	add(`<circle cx="${DAY_SUN.cx}" cy="${DAY_SUN.cy}" r="${DAY_SUN.r}" fill="${c.sunDisc}"/>`);
};

export const wallpaperSvg = (id) => {
	const { palette, mode, style } = parseId(id);
	const c = sceneColours(palette, mode);
	const smooth = style === 'smooth';
	const out = [];
	const add = (line, depth = 1) => out.push(`${'\t'.repeat(depth)}${line}`);

	const { summary, daySummary } = WALLPAPER_PALETTES[palette];
	out.push(header(id, (mode === 'dark' ? summary : daySummary).replace(/`/g, ''), style));
	out.push(
		`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${WIDTH} ${HEIGHT}" width="${WIDTH}" height="${HEIGHT}" role="img">`,
	);
	add(`<title>Afterglow ${palette}, ${mode}, ${style}</title>`);

	if (mode === 'light') daySky(c, smooth, add);
	else if (smooth) {
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

	if (mode === 'dark') add('<!-- The low sun, half set behind the back horizon -->');
	if (mode === 'light') {
		// drawn with the daytime sky
	} else if (smooth) {
		add(`<circle cx="${SUN.cx}" cy="${SUN.cy}" r="${SUN.r * 2.6}" fill="url(#halo)"/>`);
	} else {
		HALO.forEach(({ scale }, i) =>
			add(
				`<circle cx="${SUN.cx}" cy="${SUN.cy}" r="${round(SUN.r * scale)}" fill="${c.halo[i]}"/>`,
			),
		);
	}
	if (mode === 'dark') {
		add(`<circle cx="${SUN.cx}" cy="${SUN.cy}" r="${SUN.r}" fill="${c.sunDisc}"/>`);
		add('');
	}

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
