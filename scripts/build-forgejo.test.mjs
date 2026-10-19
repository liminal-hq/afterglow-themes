// Unit tests for the Forgejo theme generator and validator, including bad-input cases
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
	ALPHAS,
	avatarTemplate,
	avatarVersion,
	buildForgejoCss,
	buildForgejoOverrides,
	emailHashes,
	forgejoAuto,
	forgejoFiles,
	forgejoVariants,
	STEEL_LEVELS,
	TEMPLATE_MARKER,
	ZINC_LEVELS,
} from './build-forgejo.mjs';
import { forgejoBase, resolveVariable, validateAuto, validateTheme } from './validate-forgejo.mjs';

const ids = Object.keys(forgejoVariants);
const errorsFor = (id, edit) => validateTheme(id, edit(buildForgejoCss(id))).errors.join('\n');

test('there is one theme per Afterglow variant, and an auto theme that picks between two of them', () => {
	assert.deepEqual(ids, ['afterglow', 'afterglow-dark', 'afterglow-light']);
	assert.ok(forgejoVariants[forgejoAuto.light]);
	assert.ok(forgejoVariants[forgejoAuto.dark]);
	assert.equal(Object.keys(forgejoFiles()).length, ids.length + 1);
});

test('every override is a variable Forgejo defines and a hex colour', () => {
	for (const id of ids) {
		const mode = forgejoVariants[id].base === 'forgejo-dark' ? 'dark' : 'light';
		for (const [name, value] of Object.entries(buildForgejoOverrides(id))) {
			assert.ok(forgejoBase[mode][name] !== undefined, `${id} ${name}`);
			assert.match(value, /^#[\da-f]{6}([\da-f]{2})?$/, `${id} ${name}`);
		}
	}
});

test('dark variants grade the steel ramp and the light variant the zinc ramp, every level', () => {
	for (const id of ['afterglow', 'afterglow-dark']) {
		const overrides = buildForgejoOverrides(id);
		for (const level of STEEL_LEVELS) assert.ok(overrides[`--steel-${level}`], `${id} ${level}`);
		assert.equal(overrides['--zinc-50'], undefined);
	}
	const light = buildForgejoOverrides('afterglow-light');
	for (const level of ZINC_LEVELS) assert.ok(light[`--zinc-${level}`], `light ${level}`);
	assert.equal(light['--steel-100'], undefined);
});

test('the neutral steps land on the ramp, with the void as the darkest steel', () => {
	const signature = buildForgejoOverrides('afterglow');
	assert.equal(signature['--steel-900'], '#050507');
	assert.equal(signature['--steel-800'], '#12121a');
	assert.equal(signature['--color-text'], '#e0e0e0');
	const light = buildForgejoOverrides('afterglow-light');
	assert.equal(light['--color-body'], '#fbfaf6');
	assert.equal(light['--zinc-900'], '#1c1b20');
});

test('the primary colour is the accent, and the ramp has every step and transparency', () => {
	assert.equal(buildForgejoOverrides('afterglow')['--color-primary'], '#ffaa40');
	assert.equal(buildForgejoOverrides('afterglow-dark')['--color-primary'], '#a78bfa');
	assert.equal(buildForgejoOverrides('afterglow-light')['--color-primary'], '#5e44cc');
	for (const id of ids) {
		const overrides = buildForgejoOverrides(id);
		for (let step = 1; step <= 7; step++) {
			assert.ok(overrides[`--color-primary-dark-${step}`]);
			assert.ok(overrides[`--color-primary-light-${step}`]);
		}
		for (const percent of ALPHAS) assert.ok(overrides[`--color-primary-alpha-${percent}`]);
	}
});

test('a dark theme lightens its "dark" steps and a light theme darkens them', () => {
	const luminance = (hex) =>
		[1, 3, 5].reduce((sum, at) => sum + parseInt(hex.slice(at, at + 2), 16), 0);
	for (const id of ['afterglow', 'afterglow-dark']) {
		const o = buildForgejoOverrides(id);
		assert.ok(luminance(o['--color-primary-dark-4']) > luminance(o['--color-primary']), id);
		assert.ok(luminance(o['--color-primary-light-4']) < luminance(o['--color-primary']), id);
	}
	const o = buildForgejoOverrides('afterglow-light');
	assert.ok(luminance(o['--color-primary-dark-4']) < luminance(o['--color-primary']));
	assert.ok(luminance(o['--color-primary-light-4']) > luminance(o['--color-primary']));
});

test('each theme starts from the matching Forgejo theme, and the auto theme follows the system', () => {
	assert.match(buildForgejoCss('afterglow'), /@import '\.\/theme-forgejo-dark\.css';/);
	assert.match(buildForgejoCss('afterglow-dark'), /@import '\.\/theme-forgejo-dark\.css';/);
	assert.match(buildForgejoCss('afterglow-light'), /@import '\.\/theme-forgejo-light\.css';/);
	const auto = forgejoFiles()[forgejoAuto.file];
	assert.match(auto, /theme-afterglow-light\.css' \(prefers-color-scheme: light\)/);
	assert.match(auto, /theme-afterglow\.css' \(prefers-color-scheme: dark\)/);
});

test('variables resolve through Forgejo and the theme, and the page text holds contrast', () => {
	assert.equal(resolveVariable('afterglow', '--color-body'), '#12121a');
	assert.equal(resolveVariable('afterglow-light', '--color-box-body'), '#f2eff4');
	assert.equal(resolveVariable('afterglow', '--no-such-variable'), null);
	for (const id of ids) {
		const { errors, pairs } = validateTheme(id, buildForgejoCss(id));
		assert.deepEqual(errors, [], id);
		assert.ok(pairs > 30, id);
	}
	assert.deepEqual(validateAuto(forgejoFiles()[forgejoAuto.file]), []);
});

test('the validator rejects a variable Forgejo does not define', () => {
	const message = errorsFor('afterglow', (css) =>
		css.replace('--color-primary:', '--colour-primary:'),
	);
	assert.match(message, /--colour-primary is not a variable Forgejo defines/);
});

test('the validator rejects a value it cannot measure', () => {
	const message = errorsFor('afterglow', (css) => css.replace('#ffaa40;', 'orange;'));
	assert.match(message, /must be #rrggbb/);
});

test('the validator rejects a missing import, a missing block and a stale file', () => {
	assert.match(
		errorsFor('afterglow', (css) => css.replace(/@import.*\n/, '')),
		/must import Forgejo's/,
	);
	assert.match(
		errorsFor('afterglow', () => "@import './theme-forgejo-dark.css';"),
		/no :root block/,
	);
	assert.match(
		errorsFor('afterglow', (css) => `${css}\n`),
		/out of date/,
	);
});

test('the validator rejects text that falls below contrast', () => {
	const message = errorsFor('afterglow', (css) =>
		css.replace('--color-text: #e0e0e0;', '--color-text: #333847;'),
	);
	assert.match(message, /--color-text on --color-body is [\d.]+:1/);
});

test('the validator rejects an auto theme that picks the wrong files', () => {
	const auto = forgejoFiles()[forgejoAuto.file];
	assert.match(
		validateAuto(auto.replace('(prefers-color-scheme: light)', '')).join('\n'),
		/for light mode/,
	);
	assert.match(validateAuto(`${auto}\n`).join('\n'), /out of date/);
});

test('the instance avatar template matches the signing email under both hash forms', () => {
	const [md5, sha256] = emailHashes('Noreply@192.168.1.113 ');
	assert.equal(md5.length, 32);
	assert.equal(sha256.length, 64);
	const template = avatarTemplate('noreply@192.168.1.113', 'abc12345');
	assert.ok(template.includes(`/avatar/${md5}"`));
	assert.ok(template.includes(`/avatar/${sha256}"`));
	assert.ok(template.includes(TEMPLATE_MARKER));
	assert.ok(template.includes('/assets/img/forgejo-instance.svg?v=abc12345'));
});

test('the avatar version changes with the picture and nothing else', () => {
	assert.equal(avatarVersion('<svg/>'), avatarVersion('<svg/>'));
	assert.notEqual(avatarVersion('<svg/>'), avatarVersion('<svg />'));
	assert.match(avatarVersion('<svg/>'), /^[\da-f]{8}$/);
});
