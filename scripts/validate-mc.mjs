// Validate the generated Afterglow Midnight Commander skins: keys, colour syntax, contrast and drift
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
	DEFAULT,
	buildSkin,
	buildSkinModel,
	flavours,
	mcVariants,
	skinFile,
	xtermHex,
} from './build-mc.mjs';
import { contrast } from './colour.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const read = (path) => readFileSync(join(root, path), 'utf8');
const requiredKeys = JSON.parse(read('scripts/mc-skin-keys.json'));
const ATTRS = new Set(['bold', 'italic', 'underline', 'reverse', 'blink', 'none']);

// Parse the INI subset mc skins use: `[section]` headings, `key = value` lines and `#` comments
export const parseIni = (text) => {
	const sections = {};
	let current;
	for (const raw of text.split('\n')) {
		const line = raw.trim();
		if (!line || line.startsWith('#')) continue;
		const heading = line.match(/^\[(.+)\]$/);
		if (heading) {
			current = sections[heading[1]] ??= {};
			continue;
		}
		const eq = line.indexOf('=');
		if (eq < 0 || !current) throw new Error(`Cannot parse line: ${raw}`);
		current[line.slice(0, eq).trim()] = line.slice(eq + 1).trim();
	}
	return sections;
};

// Turn an mc colour into hex. Returns undefined for a colour mc would not accept in this flavour.
export const colourToHex = (colour, flavour, surface) => {
	if (colour === DEFAULT) return surface;
	if (flavour === 'truecolor') return /^#[\da-f]{6}$/i.test(colour) ? colour : undefined;
	const index = colour.match(/^color(\d{1,3})$/)?.[1];
	if (index === undefined || Number(index) < 16 || Number(index) > 255) return undefined;
	return xtermHex(Number(index));
};

let failed = false;
const fail = (name, message) => {
	failed = true;
	console.error(`✗ ${name}: ${message}`);
};

// Validate one skin's text against the generator and mc's skin format. Returns the problems found
// and how many contrast pairs were measured.
export const validateSkin = (id, flavour, text, file = skinFile(id, flavour)) => {
	const errors = [];
	const skin = parseIni(text);
	const model = buildSkinModel(id);

	if (text !== buildSkin(id, flavour)) {
		errors.push(`mc/skins/${file} is out of date. Run \`bun run build\`.`);
	}

	for (const [section, keys] of Object.entries(requiredKeys)) {
		if (!skin[section]) {
			errors.push(`section [${section}] is missing`);
			continue;
		}
		for (const key of keys) {
			if (skin[section][key] === undefined || skin[section][key] === '') {
				errors.push(`[${section}] ${key} is missing or empty`);
			}
		}
		for (const key of Object.keys(skin[section])) {
			if (!keys.includes(key) && !(section === 'skin' && key === flavours[flavour].key)) {
				errors.push(`[${section}] ${key} is not a key mc skins define`);
			}
		}
	}
	for (const section of Object.keys(skin)) {
		if (!requiredKeys[section]) errors.push(`[${section}] is not a section mc skins define`);
	}
	if (skin.skin?.[flavours[flavour].key] !== 'true') {
		errors.push(`[skin] ${flavours[flavour].key} must be true`);
	}
	for (const other of Object.values(flavours).filter((f) => f.key !== flavours[flavour].key)) {
		if (skin.skin?.[other.key] !== undefined) errors.push(`[skin] must not set ${other.key}`);
	}

	let pairs = 0;
	for (const [section, items] of Object.entries(model.sections)) {
		for (const [key, item] of Object.entries(items)) {
			const value = skin[section]?.[key];
			if (value === undefined) continue;
			const [fg, bg, attrs, ...extra] = value.split(';');
			if (extra.length) errors.push(`[${section}] ${key} has too many parts (${value})`);
			const fgHex = colourToHex(fg, flavour);
			const surface = colourToHex(bg, flavour, model.baseSurface);
			if (fg === DEFAULT || !fgHex) {
				errors.push(`[${section}] ${key} foreground "${fg}" is not a valid ${flavour} colour`);
			}
			if (!surface) {
				errors.push(`[${section}] ${key} background "${bg}" is not a valid ${flavour} colour`);
			}
			for (const attr of attrs ? attrs.split('+') : []) {
				if (!ATTRS.has(attr)) errors.push(`[${section}] ${key} has an unknown attribute "${attr}"`);
			}
			if (!fgHex || !surface || item.min === 0) continue;
			pairs++;
			const ratio = contrast(fgHex, surface);
			if (ratio < item.min) {
				errors.push(`[${section}] ${key} is ${ratio.toFixed(2)}:1 (needs ${item.min}:1)`);
			}
		}
	}

	if (id !== 'afterglow') {
		if (/;default\b/.test(text))
			errors.push('only the afterglow skin may use the default background');
	} else if (skin.core?._default_?.split(';')[1] !== DEFAULT) {
		errors.push('[core] _default_ must use the default background so transparency shows through');
	}

	return { errors, pairs };
};

const isMain = process.argv[1] === fileURLToPath(import.meta.url);

if (isMain) {
	for (const id of Object.keys(mcVariants)) {
		for (const flavour of Object.keys(flavours)) {
			const file = skinFile(id, flavour);
			const { errors, pairs } = validateSkin(id, flavour, read(`mc/skins/${file}`), file);
			for (const message of errors) fail(`${id} (${flavour})`, message);
			if (!errors.length) console.log(`✓ ${file} (${pairs} contrast pairs)`);
		}
	}
	process.exit(failed ? 1 : 0);
}
