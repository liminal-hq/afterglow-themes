// Validate the generated Afterglow Forgejo themes: variable names, imports, colour syntax and contrast
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
	buildForgejoOverrides,
	forgejoAuto,
	forgejoFiles,
	forgejoVariants,
} from './build-forgejo.mjs';
import { contrast, over } from './colour.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const read = (path) => readFileSync(join(root, path), 'utf8');

// Forgejo's own variables for each mode, read from the themes in the Forgejo binary
export const forgejoBase = JSON.parse(read('scripts/forgejo-theme-variables.json'));

const HEX = /^#[\da-f]{6}([\da-f]{2})?$/i;

// Which Forgejo mode a variant starts from
const modeOf = (id) => (forgejoVariants[id].base === 'forgejo-dark' ? 'dark' : 'light');

// A variable's final value once the theme's overrides are laid over Forgejo's, following `var()`
// references through both. Returns null when a reference cannot be resolved to a hex colour.
export const resolveVariable = (id, name, overrides = buildForgejoOverrides(id), depth = 0) => {
	if (depth > 12) return null;
	const value = overrides[name] ?? forgejoBase[modeOf(id)][name];
	if (value === undefined) return null;
	const reference = /^var\((--[\w-]+)\)$/.exec(value.trim());
	if (reference) return resolveVariable(id, reference[1], overrides, depth + 1);
	return HEX.test(value.trim()) ? value.trim() : null;
};

// What text must hold against the surfaces it is drawn on. The surfaces are Forgejo's names for the
// page, a box, the header, a menu, a card, an input and a code block.
const SURFACES = [
	'--color-body',
	'--color-box-header',
	'--color-box-body',
	'--color-nav-bg',
	'--color-footer',
	'--color-menu',
	'--color-card',
	'--color-input-background',
	'--color-markup-code-block',
];
const TEXTS = [
	['--color-text', 4.5],
	['--color-text-light', 4.5],
	['--color-text-light-1', 4.5],
	['--color-text-light-2', 4.5],
	// The placeholder and secondary text are the dimmest text Forgejo draws as text
	['--color-text-light-3', 4.5],
	// Links, the active tab and primary buttons' outlines are the primary colour on a surface
	['--color-primary', 4.5],
];

// Validate one theme's CSS text against the generator. Returns the problems found and how many
// contrast pairs were measured.
export const validateTheme = (id, css, file = forgejoVariants[id].file) => {
	const errors = [];
	const meta = forgejoVariants[id];
	const mode = modeOf(id);

	if (!css.includes(`@import './theme-${meta.base}.css';`)) {
		errors.push(
			`must import Forgejo's ${meta.base} theme first, so it inherits everything it keeps`,
		);
	}
	const block = /:root \{([^}]*)\}/.exec(css);
	if (!block) errors.push('has no :root block');
	// Contrast is measured on what the file says, so a hand edit cannot slip past
	const written = {};
	for (const line of (block?.[1] ?? '')
		.split('\n')
		.map((l) => l.trim())
		.filter(Boolean)) {
		const match = /^(--[\w-]+): ([^;]+);$/.exec(line);
		if (!match) {
			errors.push(`cannot read the line "${line}"`);
			continue;
		}
		const [, name, value] = match;
		written[name] = value;
		if (forgejoBase[mode][name] === undefined) {
			errors.push(`${name} is not a variable Forgejo defines (it would do nothing)`);
		} else if (!HEX.test(value)) {
			errors.push(`${name}: "${value}" must be #rrggbb or #rrggbbaa so contrast can be checked`);
		}
	}

	if (css !== forgejoFiles()[file]) {
		errors.push(`forgejo/themes/${file} is out of date. Run \`bun run build\`.`);
	}

	let pairs = 0;
	const check = (fg, bg, min, label) => {
		const front = resolveVariable(id, fg, written);
		const back = resolveVariable(id, bg, written);
		if (!front || !back) {
			errors.push(`${label}: cannot resolve ${front ? bg : fg} to a colour`);
			return;
		}
		const page = back.slice(0, 7);
		pairs++;
		const ratio = contrast(over(front, page), page);
		if (ratio < min) errors.push(`${label} is ${ratio.toFixed(2)}:1 (needs ${min}:1)`);
	};
	for (const [text, min] of TEXTS) {
		for (const surface of SURFACES) check(text, surface, min, `${text} on ${surface}`);
	}
	// A secondary fill (a quiet button or a label) carries the body text, never a link
	check('--color-text', '--color-secondary', 4.5, '--color-text on --color-secondary');
	check('--color-primary-contrast', '--color-primary', 4.5, 'text on the primary colour');
	check('--color-text', '--color-hover', 4.5, '--color-text on --color-hover');
	check('--color-input-text', '--color-input-background', 4.5, 'typed text on an input');
	return { errors, pairs };
};

// The auto file picks between two others by the operating system's setting
export const validateAuto = (css) => {
	const errors = [];
	const light = forgejoVariants[forgejoAuto.light].file;
	const dark = forgejoVariants[forgejoAuto.dark].file;
	if (!css.includes(`@import './${light}' (prefers-color-scheme: light);`)) {
		errors.push(`must import ${light} for light mode`);
	}
	if (!css.includes(`@import './${dark}' (prefers-color-scheme: dark);`)) {
		errors.push(`must import ${dark} for dark mode`);
	}
	if (css !== forgejoFiles()[forgejoAuto.file]) {
		errors.push(`forgejo/themes/${forgejoAuto.file} is out of date. Run \`bun run build\`.`);
	}
	return errors;
};

const isMain = process.argv[1] === fileURLToPath(import.meta.url);

if (isMain) {
	let failed = false;
	for (const [id, meta] of Object.entries(forgejoVariants)) {
		let css;
		try {
			css = read(`forgejo/themes/${meta.file}`);
		} catch (error) {
			console.error(`✗ ${id}: cannot read forgejo/themes/${meta.file}: ${error.message}`);
			failed = true;
			continue;
		}
		const { errors, pairs } = validateTheme(id, css, meta.file);
		for (const message of errors) console.error(`✗ ${id}: ${message}`);
		if (errors.length) failed = true;
		else console.log(`✓ forgejo/themes/${meta.file} (${pairs} contrast pairs)`);
	}
	let autoErrors;
	try {
		autoErrors = validateAuto(read(`forgejo/themes/${forgejoAuto.file}`));
	} catch (error) {
		autoErrors = [`cannot read forgejo/themes/${forgejoAuto.file}: ${error.message}`];
	}
	for (const message of autoErrors) console.error(`✗ auto: ${message}`);
	if (autoErrors.length) failed = true;
	else console.log(`✓ forgejo/themes/${forgejoAuto.file}`);
	process.exit(failed ? 1 : 0);
}
