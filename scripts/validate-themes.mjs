// Validate the generated Afterglow themes against the OpenCode V2 theme schema and check text contrast
//
// The structural rules mirror the schema bundled in OpenCode v2 (`opencode --version`), since the
// published JSON schema for V2 themes is not available yet.
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { readdirSync, readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { contrast } from './colour.mjs';
import { STEPS } from './palette.mjs';

const dir = join(dirname(fileURLToPath(import.meta.url)), '..', 'themes');
const HEX = /^#(?:[\da-f]{3}|[\da-f]{4}|[\da-f]{6}|[\da-f]{8})$/i;
const HUE_REF = /^\$hue\..+\.(?:100|200|300|400|500|600|700|800|900)$/;
const SEMANTIC = ['accent', 'interactive', 'neutral'];
const FEEDBACK = ['error', 'warning', 'success', 'info'];
const ACTIONS = ['primary', 'secondary', 'destructive'];
const SYNTAX = [
	'comment',
	'keyword',
	'function',
	'variable',
	'string',
	'number',
	'type',
	'operator',
	'punctuation',
];
const MARKDOWN = [
	'text',
	'heading',
	'link',
	'linkText',
	'code',
	'blockQuote',
	'emphasis',
	'strong',
	'horizontalRule',
	'listItem',
	'listEnumeration',
	'image',
	'imageText',
	'codeBlock',
];

const required = [
	'text.base',
	'text.muted',
	'text.formfield.base',
	...ACTIONS.map((a) => `text.action.${a}.base`),
	...ACTIONS.map((a) => `background.action.${a}.base`),
	...FEEDBACK.flatMap((f) => [
		`text.feedback.${f}.base`,
		`text.feedback.${f}.muted`,
		`background.feedback.${f}.base`,
	]),
	'background.base',
	'background.raised.base',
	'background.raised.high',
	'background.raised.max',
	'background.formfield.base',
	'border.base',
	'scrollbar.base',
	'diff.text.added',
	'diff.text.removed',
	'diff.text.context',
	'diff.text.hunkHeader',
	'diff.background.added',
	'diff.background.removed',
	'diff.background.context',
	'diff.highlight.added',
	'diff.highlight.removed',
	'diff.lineNumber.text',
	'diff.lineNumber.background.added',
	'diff.lineNumber.background.removed',
	...SYNTAX.map((k) => `syntax.${k}`),
	...MARKDOWN.map((k) => `markdown.${k}`),
];

const isObject = (v) => v && typeof v === 'object' && !Array.isArray(v);
const get = (obj, path) => path.split('.').reduce((o, k) => (isObject(o) ? o[k] : undefined), obj);
const merge = (a, b) => {
	if (!isObject(a) || !isObject(b)) return b === undefined ? a : b;
	const out = { ...a };
	for (const [k, v] of Object.entries(b)) out[k] = k in a ? merge(a[k], v) : v;
	return out;
};

const leaves = (obj, prefix = []) =>
	Object.entries(obj).flatMap(([k, v]) =>
		isObject(v) ? leaves(v, [...prefix, k]) : [[[...prefix, k].join('.'), v]],
	);

let failed = false;
const fail = (name, message) => {
	failed = true;
	console.error(`✗ ${name}: ${message}`);
};

for (const file of readdirSync(dir).filter((f) => f.endsWith('.json'))) {
	const name = file.replace('.json', '');
	const theme = JSON.parse(readFileSync(join(dir, file), 'utf8'));
	const modes = ['light', 'dark'].filter((m) => theme[m]);

	if (!isObject(theme.base)) fail(name, 'missing base');
	if (!modes.length) fail(name, 'theme must provide at least one mode');
	if (!Array.isArray(theme.base?.categorical) || !theme.base.categorical.length)
		fail(name, 'categorical is required');

	for (const mode of modes) {
		const label = `${name} (${mode})`;
		const { hue = {}, ...overrides } = theme[mode];
		const { categorical, ...baseTokens } = theme.base;

		for (const key of SEMANTIC) if (!(key in hue)) fail(label, `missing semantic hue "${key}"`);
		for (const [key, value] of Object.entries(hue)) {
			if (typeof value === 'string') {
				if (!/^\$hue\..+$/.test(value)) fail(label, `hue.${key} alias must reference another hue`);
				continue;
			}
			for (const step of STEPS)
				if (!HEX.test(value?.[step] ?? '')) fail(label, `hue.${key}.${step} is not a hex colour`);
		}
		for (const key of categorical ?? [])
			if (!(key in hue)) fail(label, `categorical hue "${key}" was not found`);

		const tree = merge(baseTokens, overrides);
		const resolve = (value, seen = 0) => {
			if (seen > 10) return undefined;
			if (value === 'transparent' || HEX.test(value)) return value;
			if (typeof value !== 'string' || !value.startsWith('$')) return undefined;
			const path = value.slice(1);
			if (path.startsWith('hue.')) {
				const [, hueName, step] = path.split('.');
				let entry = hue[hueName];
				for (let hops = 0; typeof entry === 'string' && hops < 5; hops++)
					entry = hue[entry.split('.')[1]];
				return isObject(entry) ? resolve(entry[step], seen + 1) : undefined;
			}
			return resolve(get(tree, path) ?? get(tree, `${path}.base`), seen + 1);
		};

		for (const path of required)
			if (get(tree, path) === undefined) fail(label, `missing token ${path}`);
		for (const [path, value] of leaves(tree)) {
			if (path.startsWith('@dialog')) continue;
			if (path.startsWith('syntax.') || path.startsWith('markdown.')) {
				if (!HEX.test(value) && !HUE_REF.test(value))
					fail(label, `${path} must be a hex colour or $hue.<name>.<step>`);
			}
			if (resolve(value) === undefined) fail(label, `${path} -> ${value} does not resolve`);
		}

		// Contrast against the opaque surface (transparent themes are checked against the brand void)
		const bg =
			resolve(tree.background.base) === 'transparent'
				? resolve('$hue.neutral.900')
				: resolve(tree.background.base);
		const checks = [
			['text.base', 4.5],
			['text.muted', 4.5],
			['text.action.primary.base', 4.5],
			['text.feedback.error.base', 4.5],
			['text.feedback.warning.base', 4.5],
			['text.feedback.success.base', 4.5],
			['text.feedback.info.base', 4.5],
			['syntax.comment', 4.5],
			['syntax.keyword', 4.5],
			['syntax.function', 4.5],
			['syntax.string', 4.5],
			['syntax.number', 4.5],
			['syntax.type', 4.5],
			['markdown.heading', 4.5],
			['markdown.link', 4.5],
		];
		for (const [path, min] of checks) {
			const colour = resolve(get(tree, path));
			const ratio = contrast(colour, bg);
			if (ratio < min)
				fail(label, `${path} ${colour} on ${bg} is ${ratio.toFixed(2)}:1 (needs ${min}:1)`);
		}
		console.log(`✓ ${label}`);
	}
}

process.exit(failed ? 1 : 0);
