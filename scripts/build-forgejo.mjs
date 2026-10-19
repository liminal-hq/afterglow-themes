// Generate the Afterglow Forgejo themes from the shared palette
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { createHash } from 'node:crypto';
import { mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { mix } from './colour.mjs';
import { resolvedHues, variants } from './hues.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

// `name` is what Forgejo's theme picker shows (through the `[ui]` THEMES setting) and the file name
// is `theme-<name>.css`. Each variant starts from one of Forgejo's own themes, so everything
// Afterglow does not recolour (syntax highlighting, diffs, alerts, badges) still follows Forgejo.
export const forgejoVariants = {
	afterglow: { file: 'theme-afterglow.css', base: 'forgejo-dark', label: 'Afterglow' },
	'afterglow-dark': {
		file: 'theme-afterglow-dark.css',
		base: 'forgejo-dark',
		label: 'Afterglow Dark',
	},
	'afterglow-light': {
		file: 'theme-afterglow-light.css',
		base: 'forgejo-light',
		label: 'Afterglow Light',
	},
};

// Follows the operating system: the signature theme in dark mode and the paper theme in light mode
export const forgejoAuto = {
	file: 'theme-afterglow-auto.css',
	label: 'Afterglow (auto)',
	light: 'afterglow-light',
	dark: 'afterglow',
};

// Forgejo's dark themes grade their greys on a `--steel-*` ramp from 900 (darkest) to 100, and its
// light themes on a `--zinc-*` ramp from 50 (lightest) to 900. Both have a half step between each pair.
const levels = (from, to) => {
	const out = [];
	for (let level = from; level <= to; level += 50) out.push(level);
	return out;
};
export const STEEL_LEVELS = levels(100, 900);
export const ZINC_LEVELS = levels(50, 900);

// Where each Afterglow neutral step lands on a Forgejo ramp; the half steps blend their neighbours.
// Dark: step N sits on steel N, so 900 is the void and 100 the brightest text. Light: 50 is the
// card colour one step darker than the page, so the page itself (neutral 900) stands alone.
const steelAnchors = {
	100: 100,
	200: 200,
	300: 300,
	400: 400,
	500: 500,
	600: 600,
	700: 700,
	800: 800,
	900: 900,
};
const zincAnchors = {
	50: 800,
	100: 700,
	200: 600,
	300: 500,
	400: 400,
	600: 300,
	800: 200,
	900: 100,
};

const rampOn = (levelsList, anchors, neutral) => {
	const known = Object.keys(anchors)
		.map(Number)
		.sort((a, b) => a - b);
	return Object.fromEntries(
		levelsList.map((level) => {
			if (anchors[level] !== undefined) return [level, neutral[anchors[level]]];
			const below = [...known].reverse().find((k) => k < level);
			const above = known.find((k) => k > level);
			const t = (level - below) / (above - below);
			return [level, mix(neutral[anchors[below]], neutral[anchors[above]], t)];
		}),
	);
};

export const ALPHAS = [10, 20, 30, 40, 50, 60, 70, 80, 90];
const alphaHex = (percent) =>
	Math.round((percent / 100) * 255)
		.toString(16)
		.padStart(2, '0');

// Forgejo spells the primary colour as a ramp: seven steps towards `dark` and seven towards `light`,
// plus the same colour at nine transparencies. In a dark theme "dark" means lighter and "light"
// means darker, so each steps from the primary away from or towards the page colour.
const primaryRamp = (primary, page, mode) => {
	const away = mode === 'dark' ? '#ffffff' : '#000000';
	const towards = mode === 'dark' ? page : '#ffffff';
	const dark = [0.12, 0.24, 0.36, 0.48, 0.6, 0.72, 0.84];
	const light = [0.18, 0.32, 0.46, 0.58, 0.7, 0.82, 0.92];
	const out = {};
	dark.forEach((t, i) => (out[`--color-primary-dark-${i + 1}`] = mix(primary, away, t)));
	light.forEach((t, i) => (out[`--color-primary-light-${i + 1}`] = mix(primary, towards, t)));
	for (const percent of ALPHAS)
		out[`--color-primary-alpha-${percent}`] = `${primary}${alphaHex(percent)}`;
	return out;
};

// The brand colour is the primary colour, as it is in Forgejo's own themes: links, buttons and
// the active tab. That is the variant's accent, orange for `afterglow` and purple for the others,
// the same hue Claude Code uses for its brand marks.
export const buildForgejoOverrides = (id) => {
	const variant = variants[id];
	const dark = variant.mode === 'dark';
	const N = variant.neutral;
	const primary = resolvedHues(variant).accent[200];
	const overrides = {};

	if (dark) {
		for (const [level, colour] of Object.entries(rampOn(STEEL_LEVELS, steelAnchors, N))) {
			overrides[`--steel-${level}`] = colour;
		}
	} else {
		for (const [level, colour] of Object.entries(rampOn(ZINC_LEVELS, zincAnchors, N))) {
			overrides[`--zinc-${level}`] = colour;
		}
		// Forgejo's light themes paint the page, inputs and toggles pure white
		overrides['--color-body'] = N[900];
		overrides['--color-input-background'] = N[900];
		overrides['--color-input-toggle-background'] = N[900];
		overrides['--color-selection-bg'] = primary;
	}

	overrides['--color-primary'] = primary;
	// Text on a primary fill (a button) is the page colour: near-black on orange, paper on deep purple
	overrides['--color-primary-contrast'] = N[900];
	Object.assign(overrides, primaryRamp(primary, N[900], variant.mode));
	// The body text is the brand's #e0e0e0 and not the brightest step
	if (dark) overrides['--color-text'] = N[200];
	return overrides;
};

export const buildForgejoCss = (id) => {
	const meta = forgejoVariants[id];
	const lines = Object.entries(buildForgejoOverrides(id)).map(
		([name, value]) => `\t${name}: ${value};`,
	);
	return `/* ${meta.label} for Forgejo: generated by afterglow-themes (scripts/build-forgejo.mjs), do not edit. */
@import './theme-${meta.base}.css';

:root {
${lines.join('\n')}
}
`;
};

export const buildForgejoAutoCss =
	() => `/* Afterglow for Forgejo, following the operating system: generated by afterglow-themes (scripts/build-forgejo.mjs), do not edit. */
@import './${forgejoVariants[forgejoAuto.light].file}' (prefers-color-scheme: light);
@import './${forgejoVariants[forgejoAuto.dark].file}' (prefers-color-scheme: dark);
`;

export const forgejoFiles = () => ({
	...Object.fromEntries(
		Object.entries(forgejoVariants).map(([id, meta]) => [meta.file, buildForgejoCss(id)]),
	),
	[forgejoAuto.file]: buildForgejoAutoCss(),
});

if (process.argv[1] === fileURLToPath(import.meta.url)) {
	// Start clean so a renamed or removed theme never lingers in the output
	rmSync(join(root, 'forgejo', 'themes'), { recursive: true, force: true });
	mkdirSync(join(root, 'forgejo', 'themes'), { recursive: true });

	for (const [file, css] of Object.entries(forgejoFiles())) {
		writeFileSync(join(root, 'forgejo', 'themes', file), css);
		console.log(`wrote forgejo/themes/${file}`);
	}
}

// The avatar Forgejo shows next to "Signed by" on commits the instance signs itself (merges made in
// the web UI). Forgejo draws it from the signing email's hash, so a stylesheet swaps the picture
// for requests carrying that hash, in both the hash forms Forgejo has used.
export const TEMPLATE_MARKER = 'afterglow-forgejo-instance-avatar';

export const emailHashes = (email) => {
	const address = email.trim().toLowerCase();
	return ['md5', 'sha256'].map((algorithm) => createHash(algorithm).update(address).digest('hex'));
};

// Forgejo lets browsers keep a static file for six hours, so the picture's URL carries a hash of its
// content and a redrawn avatar is fetched again straight away.
export const avatarVersion = (svg) => createHash('sha256').update(svg).digest('hex').slice(0, 8);

export const avatarTemplate = (email, version) => `<style>
	/* ${TEMPLATE_MARKER}: the Afterglow picture for the instance's own signature (afterglow-themes, forgejo/avatar). */
${emailHashes(email)
	.map((hash) => `	img[src*="/avatar/${hash}"]`)
	.join(',\n')} {
		content: url(/assets/img/forgejo-instance.svg?v=${version});
	}
</style>
`;
