// Validate the generated Afterglow .tmTheme files: plist syntax, global settings, colours, scopes, contrast
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { buildTmTheme, scopeRules, tmVariants } from './build-tmtheme.mjs';
import { buildVscodeTheme } from './build-vscode.mjs';
import { contrast } from './colour.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const read = (path) => readFileSync(join(root, path), 'utf8');

const HEX = /^#[\da-f]{6}$/i;
const UUID = /^[\dA-F]{8}-[\dA-F]{4}-[\dA-F]{4}-[\dA-F]{4}-[\dA-F]{12}$/;
const FONT_STYLES = new Set(['bold', 'italic', 'underline']);

// Keys every theme must set in its global settings. `gutter` and `gutterForeground` are the Sublime
// Text additions that bat and delta also read.
export const REQUIRED_GLOBALS = [
	'background',
	'foreground',
	'caret',
	'selection',
	'lineHighlight',
	'invisibles',
	'gutter',
	'gutterForeground',
];

const ENTITY = /&(?:amp|lt|gt|quot|apos|#\d+|#x[\da-f]+);/gi;
const decode = (text) =>
	text
		.replace(/&#x([\da-f]+);/gi, (_, hex) => String.fromCodePoint(parseInt(hex, 16)))
		.replace(/&#(\d+);/g, (_, dec) => String.fromCodePoint(Number(dec)))
		.replace(/&lt;/g, '<')
		.replace(/&gt;/g, '>')
		.replace(/&quot;/g, '"')
		.replace(/&apos;/g, "'")
		.replace(/&amp;/g, '&');

// Parse the XML subset property lists use into a tree of `{ tag, children, text }`. It is strict on
// purpose: mismatched or unclosed tags, stray `<` or `&` and anything after the root are errors.
export const parseXml = (text) => {
	const document = { tag: '#document', children: [], text: '' };
	const stack = [document];
	const token =
		/<!--[\s\S]*?-->|<\?[\s\S]*?\?>|<!DOCTYPE[^>]*>|<(\/?)([A-Za-z][\w-]*)(?:\s+[\w:-]+="[^"]*")*\s*(\/?)>|<|[^<]+/gy;
	let match;
	while ((match = token.exec(text)) !== null) {
		const [whole, closing, tag, selfClosing] = match;
		const top = stack.at(-1);
		if (whole.startsWith('<!') || whole.startsWith('<?')) continue;
		if (whole === '<') throw new Error('stray "<" or a malformed tag');
		if (!tag) {
			if (whole.replace(ENTITY, '').includes('&')) {
				throw new Error(`invalid entity in "${whole.trim()}"`);
			}
			if (stack.length === 1 && whole.trim()) throw new Error('text outside the root element');
			top.text += decode(whole);
		} else if (closing) {
			if (top.tag !== tag) throw new Error(`</${tag}> does not match <${top.tag}>`);
			stack.pop();
		} else {
			const node = { tag, children: [], text: '' };
			top.children.push(node);
			if (!selfClosing) stack.push(node);
		}
	}
	if (stack.length > 1) throw new Error(`<${stack.at(-1).tag}> is never closed`);
	if (document.children.length !== 1 || document.children[0].tag !== 'plist') {
		throw new Error('the document must have a single <plist> root');
	}
	return document.children[0];
};

// Convert a parsed plist value to plain JS. Dicts become objects and reject duplicate keys.
export const plistValue = (node) => {
	switch (node.tag) {
		case 'string':
			return node.text;
		case 'array':
			return node.children.map(plistValue);
		case 'dict': {
			const result = {};
			if (node.children.length % 2) throw new Error('a <dict> has a key without a value');
			for (let i = 0; i < node.children.length; i += 2) {
				const [key, value] = [node.children[i], node.children[i + 1]];
				if (key.tag !== 'key') throw new Error(`expected <key> in a <dict>, found <${key.tag}>`);
				if (Object.hasOwn(result, key.text)) throw new Error(`duplicate key "${key.text}"`);
				result[key.text] = plistValue(value);
			}
			return result;
		}
		default:
			throw new Error(`<${node.tag}> is not used in a .tmTheme`);
	}
};

export const parsePlist = (text) => {
	const plist = parseXml(text);
	if (plist.children.length !== 1) throw new Error('<plist> must hold exactly one value');
	return plistValue(plist.children[0]);
};

// Validate one theme's text against the .tmTheme format, the VS Code theme it derives from and the
// generator. Returns the problems found and how many contrast pairs were measured.
export const validateTmTheme = (id, text, file = tmVariants[id].file) => {
	const errors = [];
	let theme;
	try {
		theme = parsePlist(text);
	} catch (error) {
		return { errors: [`not a well-formed plist: ${error.message}`], pairs: 0 };
	}

	if (typeof theme !== 'object' || Array.isArray(theme)) {
		return { errors: ['the top level must be a <dict>'], pairs: 0 };
	}
	if (theme.name !== tmVariants[id].label) errors.push(`name must be "${tmVariants[id].label}"`);
	if (!UUID.test(theme.uuid ?? '')) errors.push(`uuid "${theme.uuid}" is not an upper-case UUID`);
	if (!Array.isArray(theme.settings) || theme.settings.length < 2) {
		errors.push('settings must be an array of the global settings followed by scope rules');
		return { errors, pairs: 0 };
	}

	const [first, ...rules] = theme.settings;
	if (first.scope !== undefined) {
		errors.push('the first settings entry must be the global one, without a scope');
	}
	const globals = first.settings ?? {};
	for (const key of REQUIRED_GLOBALS) {
		if (globals[key] === undefined) errors.push(`global setting ${key} is missing`);
	}
	for (const [key, value] of Object.entries(globals)) {
		if (!HEX.test(value)) errors.push(`global ${key}: "${value}" is not a #rrggbb colour`);
	}

	const background = globals.background;
	let pairs = 0;
	const check = (label, fg, bg, min) => {
		if (!HEX.test(fg) || !HEX.test(bg)) return;
		pairs++;
		const ratio = contrast(fg, bg);
		if (ratio < min) errors.push(`${label} is ${ratio.toFixed(2)}:1 (needs ${min}:1)`);
	};
	check('foreground on background', globals.foreground, background, 4.5);
	check('foreground on selection', globals.foreground, globals.selection, 4.5);
	check('foreground on lineHighlight', globals.foreground, globals.lineHighlight, 4.5);
	check('caret on background', globals.caret, background, 3);
	check('gutterForeground on gutter', globals.gutterForeground, globals.gutter, 3);

	rules.forEach((rule, index) => {
		const where = `rule ${index + 1} (${rule.scope ?? 'no scope'})`;
		if (typeof rule.scope !== 'string' || !rule.scope) errors.push(`${where} has no scope`);
		const settings = rule.settings;
		if (typeof settings !== 'object' || settings === null || Array.isArray(settings)) {
			errors.push(`${where} has no settings dict`);
			return;
		}
		for (const key of Object.keys(settings)) {
			if (!['foreground', 'background', 'fontStyle'].includes(key)) {
				errors.push(`${where} has the unknown setting ${key}`);
			}
		}
		if (settings.foreground !== undefined) {
			if (!HEX.test(settings.foreground)) {
				errors.push(`${where} foreground "${settings.foreground}" is not a #rrggbb colour`);
			} else {
				check(`${where} foreground`, settings.foreground, background, 4.5);
			}
		}
		if (settings.background !== undefined && !HEX.test(settings.background)) {
			errors.push(`${where} background "${settings.background}" is not a #rrggbb colour`);
		}
		for (const style of (settings.fontStyle ?? '').split(/\s+/).filter(Boolean)) {
			if (!FONT_STYLES.has(style)) errors.push(`${where} has the unknown fontStyle "${style}"`);
		}
	});

	// The scopes and their styles must be the ones the VS Code theme has, in the same order
	const expected = scopeRules(buildVscodeTheme(id)).map((rule) => ({
		scope: rule.scope,
		foreground: rule.settings.foreground,
		fontStyle: rule.settings.fontStyle,
	}));
	const actual = rules.map((rule) => ({
		scope: rule.scope,
		foreground: rule.settings?.foreground,
		fontStyle: rule.settings?.fontStyle,
	}));
	if (JSON.stringify(actual) !== JSON.stringify(expected)) {
		const missing = expected.filter((rule) => !actual.some((have) => have.scope === rule.scope));
		errors.push(
			missing.length
				? `scopes missing from the VS Code theme: ${missing.map((rule) => rule.scope).join(' | ')}`
				: 'the scope rules differ from the VS Code theme',
		);
	}

	if (text !== buildTmTheme(id)) {
		errors.push(`tmtheme/${file} is out of date. Run \`bun run build\`.`);
	}

	return { errors, pairs };
};

const isMain = process.argv[1] === fileURLToPath(import.meta.url);

if (isMain) {
	let failed = false;
	for (const [id, meta] of Object.entries(tmVariants)) {
		let text;
		try {
			text = read(`tmtheme/${meta.file}`);
		} catch (error) {
			console.error(`✗ ${id}: cannot read tmtheme/${meta.file}: ${error.message}`);
			failed = true;
			continue;
		}
		const { errors, pairs } = validateTmTheme(id, text, meta.file);
		for (const message of errors) console.error(`✗ ${id}: ${message}`);
		if (errors.length) failed = true;
		else console.log(`✓ tmtheme/${meta.file} (${pairs} contrast pairs)`);
	}
	process.exit(failed ? 1 : 0);
}
