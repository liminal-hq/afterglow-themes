// Validate the generated Afterglow Claude Code themes: file schema, tokens, colour syntax and contrast
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
	baseFor,
	buildClaudeTheme,
	claudeTokens,
	claudeVariants,
	surfaceFor,
} from './build-claude.mjs';
import { contrast } from './colour.mjs';
import { variants } from './hues.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const read = (path) => readFileSync(join(root, path), 'utf8');

export const BASES = [
	'dark',
	'light',
	'dark-daltonized',
	'light-daltonized',
	'dark-ansi',
	'light-ansi',
];
const FIELDS = ['name', 'base', 'overrides'];
const HEX = /^#[\da-f]{6}$/i;

// The colour syntax Claude Code accepts in `overrides`, as checked by its theme loader. Afterglow
// only writes `#rrggbb`, but a theme file edited by hand may use any of these.
export const isClaudeColour = (value) =>
	typeof value === 'string' &&
	(/^rgb\(\s?\d{1,3},\s?\d{1,3},\s?\d{1,3}\s?\)$/.test(value) ||
		/^#[\da-f]{6}$/i.test(value) ||
		/^#[\da-f]{3}$/i.test(value) ||
		/^ansi256\(\d{1,3}\)$/.test(value) ||
		/^ansi:\w+$/.test(value));

// Text and glyphs Claude Code draws on the terminal surface, with the contrast each needs. The
// surface is the variant's neutral 900. A 3:1 floor is only for deliberately dim elements: borders,
// faint separators, the empty part of the usage meter and animation frames of a shimmer.
const onSurface = [
	['text', 4.5],
	['inactive', 4.5],
	['inactiveShimmer', 3],
	['subtle', 3],
	['promptBorder', 3],
	['promptBorderShimmer', 3],
	['claude', 4.5],
	['claudeShimmer', 3],
	['claudeBlue_FOR_SYSTEM_SPINNER', 4.5],
	['claudeBlueShimmer_FOR_SYSTEM_SPINNER', 3],
	['permission', 4.5],
	['permissionShimmer', 3],
	['suggestion', 4.5],
	['remember', 4.5],
	['background', 4.5],
	['planMode', 4.5],
	['ide', 4.5],
	['autoAccept', 4.5],
	['autoAcceptShimmer', 3],
	['skill', 4.5],
	['bashBorder', 4.5],
	['success', 4.5],
	['error', 4.5],
	['warning', 4.5],
	['warningShimmer', 3],
	['merged', 4.5],
	['red_FOR_SUBAGENTS_ONLY', 4.5],
	['blue_FOR_SUBAGENTS_ONLY', 4.5],
	['green_FOR_SUBAGENTS_ONLY', 4.5],
	['yellow_FOR_SUBAGENTS_ONLY', 4.5],
	['purple_FOR_SUBAGENTS_ONLY', 4.5],
	['orange_FOR_SUBAGENTS_ONLY', 4.5],
	['pink_FOR_SUBAGENTS_ONLY', 4.5],
	['cyan_FOR_SUBAGENTS_ONLY', 4.5],
	['professionalBlue', 4.5],
	['chromeYellow', 4.5],
	['clawd_body', 3],
	['fastMode', 4.5],
	['fastModeShimmer', 3],
	['effortUltra', 4.5],
	['briefLabelYou', 4.5],
	['briefLabelClaude', 4.5],
	['rate_limit_fill', 3],
	['rate_limit_empty', 3],
	...['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet'].flatMap((colour) => [
		[`rainbow_${colour}`, 4.5],
		[`rainbow_${colour}_shimmer`, 3],
	]),
];

// Text drawn over a tinted background (diffs, transcript entries and the selection)
const overTokens = [
	...['diffAdded', 'diffRemoved', 'diffAddedDimmed', 'diffRemovedDimmed'].map((bg) => [
		'text',
		bg,
		4.5,
	]),
	['text', 'diffAddedWord', 4.5],
	['text', 'diffRemovedWord', 4.5],
	['text', 'userMessageBackground', 4.5],
	['inactive', 'userMessageBackground', 4.5],
	['text', 'userMessageBackgroundHover', 4.5],
	['inactive', 'userMessageBackgroundHover', 4.5],
	['text', 'composerSidebarBackground', 4.5],
	['inactive', 'composerSidebarBackground', 4.5],
	['text', 'bashMessageBackgroundColor', 4.5],
	['text', 'memoryBackgroundColor', 4.5],
	['text', 'selectionBg', 4.5],
	// Status badges draw the inverse text on a filled colour
	...[
		'claude',
		'permission',
		'suggestion',
		'planMode',
		'autoAccept',
		'success',
		'error',
		'warning',
		'merged',
		'ide',
	].map((bg) => ['inverseText', bg, 4.5]),
];

// Validate one theme's parsed JSON against Claude Code's theme format and the generator. Returns
// the problems found and how many contrast pairs were measured.
export const validateTheme = (id, theme, file = claudeVariants[id].file) => {
	const errors = [];
	const variant = variants[id];

	if (typeof theme !== 'object' || theme === null || Array.isArray(theme)) {
		return { errors: ['the theme must be a JSON object'], pairs: 0 };
	}
	for (const key of Object.keys(theme)) {
		if (!FIELDS.includes(key)) {
			errors.push(`"${key}" is not a field Claude Code reads (name, base, overrides)`);
		}
	}
	if (typeof theme.name !== 'string' || !theme.name) errors.push('name must be a non-empty string');
	else if (theme.name !== claudeVariants[id].label) {
		errors.push(`name must be "${claudeVariants[id].label}"`);
	}
	if (!BASES.includes(theme.base)) errors.push(`base "${theme.base}" is not a built-in preset`);
	else if (theme.base !== baseFor(variant)) {
		errors.push(`base must be "${baseFor(variant)}" for ${id}`);
	}

	const overrides = theme.overrides;
	if (typeof overrides !== 'object' || overrides === null || Array.isArray(overrides)) {
		errors.push('overrides must be an object');
		return { errors, pairs: 0 };
	}

	for (const token of claudeTokens) {
		if (!Object.hasOwn(overrides, token)) errors.push(`token ${token} is not set`);
	}
	for (const [token, value] of Object.entries(overrides)) {
		if (!claudeTokens.includes(token)) {
			errors.push(`${token} is not a token Claude Code defines (it would be ignored)`);
		} else if (!isClaudeColour(value)) {
			errors.push(`${token}: "${value}" is not a colour Claude Code accepts (it would be ignored)`);
		} else if (!HEX.test(value)) {
			errors.push(`${token}: "${value}" must be #rrggbb so contrast can be checked`);
		}
	}

	if (JSON.stringify(theme) !== JSON.stringify(buildClaudeTheme(id))) {
		errors.push(`claude/themes/${file} is out of date. Run \`bun run build\`.`);
	}

	const surface = surfaceFor(id);
	if (overrides.clawd_background !== surface) {
		errors.push(`clawd_background must be the surface colour ${surface}`);
	}

	let pairs = 0;
	const check = (fgToken, bgToken, bg, min) => {
		const fg = overrides[fgToken];
		if (!HEX.test(fg) || !HEX.test(bg)) return;
		pairs++;
		const ratio = contrast(fg, bg);
		if (ratio < min) {
			errors.push(`${fgToken} on ${bgToken} is ${ratio.toFixed(2)}:1 (needs ${min}:1)`);
		}
	};
	for (const [token, min] of onSurface) check(token, 'the surface', surface, min);
	for (const [fg, bg, min] of overTokens) check(fg, bg, overrides[bg], min);

	return { errors, pairs };
};

const isMain = process.argv[1] === fileURLToPath(import.meta.url);

if (isMain) {
	let failed = false;
	for (const [id, meta] of Object.entries(claudeVariants)) {
		let theme;
		try {
			theme = JSON.parse(read(`claude/themes/${meta.file}`));
		} catch (error) {
			console.error(`✗ ${id}: cannot read claude/themes/${meta.file}: ${error.message}`);
			failed = true;
			continue;
		}
		const { errors, pairs } = validateTheme(id, theme, meta.file);
		for (const message of errors) console.error(`✗ ${id}: ${message}`);
		if (errors.length) failed = true;
		else {
			console.log(
				`✓ claude/themes/${meta.file} (${claudeTokens.length} tokens, ${pairs} contrast pairs)`,
			);
		}
	}
	process.exit(failed ? 1 : 0);
}
