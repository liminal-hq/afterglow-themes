// Package the themes into release assets: the JSON files, a zip bundle, and SHA256SUMS
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { copyFileSync, mkdirSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const out = join(root, 'dist', 'release');
const { version } = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8'));
const themes = readdirSync(join(root, 'themes')).filter((f) => f.endsWith('.json'));

if (!themes.length) throw new Error('No themes found. Run `bun run build` first.');

rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });

for (const file of themes) copyFileSync(join(root, 'themes', file), join(out, file));

const bundle = `afterglow-themes-v${version}.zip`;
execFileSync('zip', ['-q', '-j', join(out, bundle), ...themes.map((f) => join(out, f))]);

const sums = readdirSync(out)
	.sort()
	.map(
		(file) =>
			`${createHash('sha256')
				.update(readFileSync(join(out, file)))
				.digest('hex')}  ${file}`,
	);
writeFileSync(join(out, 'SHA256SUMS'), `${sums.join('\n')}\n`);

console.log(`Release assets for v${version} in dist/release:`);
for (const line of sums) console.log(`  ${line}`);
