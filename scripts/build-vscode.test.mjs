// Unit tests for the VS Code generator helpers: the JSONC parser, scope pinning and alpha compositing
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import assert from 'node:assert/strict';
import { test } from 'node:test';
import { roleForRule } from './build-vscode.mjs';
import { over } from './colour.mjs';
import { parseJsonc } from './jsonc.mjs';

const literals = { '#ff0000': 'string', '#00ff00': 'number' };

test('parseJsonc drops comments, trailing commas and a byte order mark', () => {
	const text = '\uFEFF{\n  // line comment\n  "a": [1, 2,], /* block */\n  "b": "x",\n}';
	assert.deepEqual(parseJsonc(text), { a: [1, 2], b: 'x' });
});

test('parseJsonc leaves comma-brace sequences inside strings alone', () => {
	assert.deepEqual(parseJsonc('{"a": ",}", "b": ", ]", "c": "// not a comment"}'), {
		a: ',}',
		b: ', ]',
		c: '// not a comment',
	});
});

test('roleForRule maps an unpinned rule by its literal colour', () => {
	const rule = { scope: ['string'], settings: { foreground: '#FF0000' } };
	assert.equal(roleForRule(rule, literals), 'string');
});

test('roleForRule pins a rule by scope regardless of its literal colour', () => {
	const rule = { scope: ['entity.name.tag'], settings: { foreground: '#00ff00' } };
	assert.equal(roleForRule(rule, literals), 'tag');
});

test('roleForRule leaves a rule without a foreground uncoloured, even when its scope is pinned', () => {
	assert.equal(
		roleForRule({ scope: ['entity.name.tag'], settings: { fontStyle: 'bold' } }, literals),
		undefined,
	);
	assert.equal(
		roleForRule({ scope: 'emphasis', settings: { fontStyle: 'italic' } }, literals),
		undefined,
	);
});

test('roleForRule fails on a colour with no role', () => {
	const rule = { scope: ['string'], settings: { foreground: '#123456' } };
	assert.throws(() => roleForRule(rule, literals), /No Afterglow role for #123456/);
});

test('roleForRule fails when a pinned scope is not first in its rule', () => {
	const rule = { scope: ['string', 'entity.name.tag'], settings: { foreground: '#ff0000' } };
	assert.throws(() => roleForRule(rule, literals), /not the first scope/);
});

test('roleForRule fails when a rule mixes scopes pinned to different roles', () => {
	const rule = {
		scope: ['entity.name.tag', 'markup.heading'],
		settings: { foreground: '#ff0000' },
	};
	assert.throws(() => roleForRule(rule, literals), /different roles/);
});

test('over composites a translucent colour onto an opaque base', () => {
	assert.equal(over('#ffffff00', '#000000'), '#000000');
	assert.equal(over('#ffffffff', '#000000'), '#ffffff');
	assert.equal(over('#ffffff80', '#000000'), '#808080');
	assert.equal(over('#123456', '#000000'), '#123456');
});
