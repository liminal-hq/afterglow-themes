// Check that the hand-written release notes in docs/releases keep the notes shape
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { existsSync, readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(fileURLToPath(new URL('.', import.meta.url)), '..');

export const requiredHeadings = ['Downloads', 'What is new', 'Fixes', 'Known limits'];

// The path of the notes for a version: the tag vX.Y.Z reads docs/releases/X.Y.Z.md
export function notesPath(version, dir = join(root, 'docs', 'releases')) {
	return join(dir, `${version}.md`);
}

// Problems with one notes file's text; an empty list means it keeps the shape
export function checkNotes(text) {
	if (!text.trim()) return ['the file is empty'];
	const problems = [];
	const lines = text.split('\n');
	const lead = lines.find((line) => line.trim() !== '') ?? '';
	if (!/^\*\*[^*]+\*\*\s+\S.*[.!?]$/.test(lead)) {
		problems.push(
			'the first line must be a bold lead sentence, such as "**Afterglow 1.2.3** is …."',
		);
	}
	if (lead.includes('…')) problems.push('the lead sentence still has its placeholder');
	for (const heading of requiredHeadings) {
		if (!lines.some((line) => line.trimEnd() === `## ${heading}`)) {
			problems.push(`missing the "## ${heading}" heading`);
		}
	}
	if (lines.some((line) => /^(- )?…$/.test(line.trim()))) {
		problems.push('a placeholder line (a lone …) is still there: fill it in or delete it');
	}
	return problems;
}

// Check every notes file in a directory; returns { file, problems } for each file that fails
export function checkDirectory(dir = join(root, 'docs', 'releases')) {
	if (!existsSync(dir)) return [];
	return readdirSync(dir)
		.filter((name) => /^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?\.md$/.test(name))
		.sort()
		.map((name) => ({ file: name, problems: checkNotes(readFileSync(join(dir, name), 'utf8')) }))
		.filter((result) => result.problems.length > 0);
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
	const { version } = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
	const failures = checkDirectory();
	for (const { file, problems } of failures) {
		for (const problem of problems) console.error(`docs/releases/${file}: ${problem}`);
	}
	if (failures.length) process.exit(1);
	console.log(
		existsSync(notesPath(version))
			? `✓ docs/releases/${version}.md keeps the notes shape`
			: `✓ no hand-written notes for ${version}; the release will use generated notes only`,
	);
}
