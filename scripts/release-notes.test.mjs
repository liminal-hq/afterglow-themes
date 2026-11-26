// Unit tests for the release notes check and the release preparation script
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import assert from 'node:assert/strict';
import { mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { checkDirectory, checkNotes, notesPath } from './release-notes.mjs';
import { nextVersion, notesTemplate, prepare, setVersion } from './release-prepare.mjs';

const good = `**Afterglow 1.2.3** adds a theme.

## Downloads

- a file

## What is new

- a thing

## Fixes

- a fix

## Known limits

- a limit
`;

function scratch() {
	const dir = mkdtempSync(join(tmpdir(), 'afterglow-release-'));
	mkdirSync(join(dir, 'vscode'));
	writeFileSync(
		join(dir, 'package.json'),
		'{\n\t"name": "x",\n\t"version": "1.2.3",\n\t"a": 1\n}\n',
	);
	writeFileSync(join(dir, 'vscode', 'package.json'), '{\n\t"version": "1.2.3",\n\t"b": 2\n}\n');
	return dir;
}

test('notes that keep the shape pass', () => {
	assert.deepEqual(checkNotes(good), []);
});

test('an empty file, a plain lead and missing headings are named', () => {
	assert.deepEqual(checkNotes('  \n'), ['the file is empty']);
	assert.ok(
		checkNotes(good.replace('**Afterglow 1.2.3** adds', 'Afterglow adds'))[0].includes('bold'),
	);
	assert.deepEqual(checkNotes(good.replace('## Fixes\n', '')), ['missing the "## Fixes" heading']);
});

test('the starting template fails until it is filled in', () => {
	const problems = checkNotes(notesTemplate('1.2.3'));
	assert.ok(problems.some((p) => p.includes('lead sentence still has')));
	assert.ok(problems.some((p) => p.includes('placeholder line')));
	assert.deepEqual(checkNotes(notesTemplate('1.2.3').replace(/…/g, 'Done.')), []);
});

test('the notes path follows the tag', () => {
	assert.equal(notesPath('0.4.0', 'docs/releases'), 'docs/releases/0.4.0.md');
});

test('checkDirectory reports only files that fail and ignores a missing directory', () => {
	const dir = scratch();
	assert.deepEqual(checkDirectory(join(dir, 'none')), []);
	const notes = join(dir, 'docs');
	mkdirSync(notes);
	writeFileSync(join(notes, '1.2.3.md'), good);
	writeFileSync(join(notes, '1.2.4.md'), 'no lead\n');
	writeFileSync(join(notes, 'README.md'), 'ignored');
	const failures = checkDirectory(notes);
	assert.deepEqual(
		failures.map((f) => f.file),
		['1.2.4.md'],
	);
	rmSync(dir, { recursive: true });
});

test('nextVersion bumps or accepts an exact X.Y.Z', () => {
	assert.equal(nextVersion('1.2.3', 'patch'), '1.2.4');
	assert.equal(nextVersion('1.2.3', 'minor'), '1.3.0');
	assert.equal(nextVersion('1.2.3', 'major'), '2.0.0');
	assert.equal(nextVersion('1.2.3', '1.9.0'), '1.9.0');
	assert.throws(() => nextVersion('1.2.3', 'v1.9.0'));
	assert.throws(() => nextVersion('1.2.3', '1.9.0-rc.1'));
});

test('setVersion changes only the top-level version line', () => {
	const text = '{\n\t"version": "1.2.3",\n\t"engines": {\n\t\t"version": "9"\n\t}\n}\n';
	assert.equal(setVersion(text, '2.0.0'), text.replace('"1.2.3"', '"2.0.0"'));
	assert.throws(() => setVersion('{}', '2.0.0'));
});

test('prepare writes both manifests, starts the notes and never overwrites them', () => {
	const dir = scratch();
	const first = prepare(dir, 'minor');
	assert.equal(first[0], '1.2.3 -> 1.3.0');
	assert.ok(first[1].startsWith('Started docs/releases/1.3.0.md'));
	assert.match(readFileSync(join(dir, 'package.json'), 'utf8'), /"version": "1.3.0"/);
	assert.match(readFileSync(join(dir, 'vscode', 'package.json'), 'utf8'), /"version": "1.3.0"/);
	assert.match(
		readFileSync(join(dir, 'docs', 'releases', '1.3.0.md'), 'utf8'),
		/^\*\*Afterglow 1\.3\.0\*\*/,
	);

	writeFileSync(join(dir, 'docs', 'releases', '1.3.0.md'), 'mine\n');
	const again = prepare(dir, '1.3.0');
	assert.ok(again[1].startsWith('Kept docs/releases/1.3.0.md'));
	assert.equal(readFileSync(join(dir, 'docs', 'releases', '1.3.0.md'), 'utf8'), 'mine\n');
	rmSync(dir, { recursive: true });
});
