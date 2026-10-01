// Unit tests for the Claude Code theme generator and validator, including bad-input cases
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import {
	baseFor,
	buildClaudeOverrides,
	buildClaudeTheme,
	claudeTokens,
	claudeVariants,
	surfaceFor,
} from './build-claude.mjs';
import { variants } from './hues.mjs';
import { isClaudeColour, validateTheme } from './validate-claude.mjs';

const ids = Object.keys(claudeVariants);
const fresh = (id) => structuredClone(buildClaudeTheme(id));
const errorsFor = (id, edit) => {
	const theme = fresh(id);
	edit(theme);
	return validateTheme(id, theme).errors.join('\n');
};

test('the token list has no duplicates and covers the rainbow, subagent and diff groups', () => {
	assert.equal(new Set(claudeTokens).size, claudeTokens.length);
	for (const token of [
		'claude',
		'diffAdded',
		'pink_FOR_SUBAGENTS_ONLY',
		'rainbow_violet_shimmer',
	]) {
		assert.ok(claudeTokens.includes(token), token);
	}
});

test('every variant sets exactly the known tokens, in the token list order', () => {
	for (const id of ids) {
		assert.deepEqual(Object.keys(buildClaudeOverrides(id)), claudeTokens, id);
	}
});

test('every colour is a #rrggbb hex that Claude Code accepts', () => {
	for (const id of ids) {
		for (const [token, value] of Object.entries(buildClaudeOverrides(id))) {
			assert.match(value, /^#[\da-f]{6}$/, `${id} ${token}`);
			assert.ok(isClaudeColour(value));
		}
	}
});

test('dark variants start from the dark preset and the light variant from the light one', () => {
	assert.equal(buildClaudeTheme('afterglow').base, 'dark');
	assert.equal(buildClaudeTheme('afterglow-dark').base, 'dark');
	assert.equal(buildClaudeTheme('afterglow-light').base, 'light');
	assert.equal(baseFor(variants['afterglow-light']), 'light');
});

test('theme names are what /theme shows and file names are the slugs', () => {
	assert.deepEqual(
		ids.map((id) => [buildClaudeTheme(id).name, claudeVariants[id].file]),
		[
			['Afterglow', 'afterglow.json'],
			['Afterglow Dark', 'afterglow-dark.json'],
			['Afterglow Light', 'afterglow-light.json'],
		],
	);
});

test('the brand accent follows the variant: orange for afterglow, purple for the others', () => {
	assert.equal(buildClaudeOverrides('afterglow').claude, '#ffaa40');
	assert.equal(buildClaudeOverrides('afterglow-dark').claude, '#a78bfa');
	assert.equal(buildClaudeOverrides('afterglow-light').claude, '#5e44cc');
});

test('the mascot background is the terminal surface in every variant', () => {
	for (const id of ids) assert.equal(buildClaudeOverrides(id).clawd_background, surfaceFor(id));
});

test('the committed files match the generator', () => {
	for (const id of ids) {
		const file = new URL(`../claude/themes/${claudeVariants[id].file}`, import.meta.url);
		assert.deepEqual(JSON.parse(readFileSync(file, 'utf8')), buildClaudeTheme(id), id);
	}
});

test('isClaudeColour accepts the syntax Claude Code accepts and nothing else', () => {
	for (const ok of ['#a78bfa', '#fff', 'rgb(1,2,3)', 'rgb( 1, 2, 3 )', 'ansi256(42)', 'ansi:red']) {
		assert.ok(isClaudeColour(ok), ok);
	}
	for (const bad of ['a78bfa', '#a78b', '#a78bfaff', 'rgba(1,2,3,1)', 'red', '', 42, null]) {
		assert.ok(!isClaudeColour(bad), String(bad));
	}
});

test('validateTheme accepts the generated themes', () => {
	for (const id of ids) {
		const { errors, pairs } = validateTheme(id, fresh(id));
		assert.deepEqual(errors, []);
		assert.ok(pairs > 50);
	}
});

test('validateTheme rejects a theme that is not an object', () => {
	assert.match(validateTheme('afterglow', []).errors.join(), /must be a JSON object/);
	assert.match(validateTheme('afterglow', null).errors.join(), /must be a JSON object/);
});

test('validateTheme reports a missing token', () => {
	assert.match(
		errorsFor('afterglow', (theme) => delete theme.overrides.diffAdded),
		/token diffAdded is not set/,
	);
});

test('validateTheme reports an unknown token', () => {
	assert.match(
		errorsFor('afterglow', (theme) => (theme.overrides.notAToken = '#ffffff')),
		/notAToken is not a token Claude Code defines/,
	);
});

test('validateTheme reports an unknown field and a bad base', () => {
	assert.match(
		errorsFor('afterglow', (theme) => (theme.extends = 'dark')),
		/"extends" is not a field Claude Code reads/,
	);
	assert.match(
		errorsFor('afterglow', (theme) => (theme.base = 'solarized')),
		/base "solarized" is not a built-in preset/,
	);
	assert.match(
		errorsFor('afterglow-light', (theme) => (theme.base = 'dark')),
		/base must be "light"/,
	);
});

test('validateTheme reports a colour Claude Code would ignore', () => {
	assert.match(
		errorsFor('afterglow', (theme) => (theme.overrides.error = 'rose')),
		/error: "rose" is not a colour Claude Code accepts/,
	);
});

test('validateTheme asks for hex so contrast can be measured', () => {
	assert.match(
		errorsFor('afterglow', (theme) => (theme.overrides.error = 'rgb(244,63,94)')),
		/error: "rgb\(244,63,94\)" must be #rrggbb/,
	);
});

test('validateTheme reports low-contrast text on the surface', () => {
	assert.match(
		errorsFor('afterglow-dark', (theme) => (theme.overrides.text = '#1a1828')),
		/text on the surface is [\d.]+:1 \(needs 4.5:1\)/,
	);
});

test('validateTheme reports low-contrast text on a tinted background', () => {
	assert.match(
		errorsFor('afterglow-dark', (theme) => (theme.overrides.diffAdded = '#44ff44')),
		/text on diffAdded is [\d.]+:1/,
	);
});

test('validateTheme keeps the 3:1 floor for dim elements and no lower', () => {
	assert.match(
		errorsFor('afterglow-dark', (theme) => (theme.overrides.promptBorder = '#2a2840')),
		/promptBorder on the surface is [\d.]+:1 \(needs 3:1\)/,
	);
});

test('validateTheme reports drift from the generator', () => {
	assert.match(
		errorsFor('afterglow', (theme) => (theme.overrides.text = '#ffffff')),
		/out of date/,
	);
});
