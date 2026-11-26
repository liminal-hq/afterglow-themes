// Tests for the ReactOS Start orb and menu banner masters and their renderer: hashes, sizes, margins and repeatable bytes
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';

const start = join(fileURLToPath(new URL('..', import.meta.url)), 'desktop', 'start');
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');

// The renderer needs rsvg-convert and Python with Pillow; the Desktop style job has them, a plain test run may not
const haveTools =
	spawnSync('rsvg-convert', ['--version'], { stdio: 'ignore' }).status === 0 &&
	spawnSync('python3', ['-c', 'import PIL'], { stdio: 'ignore' }).status === 0;
const needTools = haveTools
	? {}
	: { skip: 'rsvg-convert and python3 with Pillow are not installed' };

const sums = (file) =>
	Object.fromEntries(
		readFileSync(join(start, file), 'utf8')
			.trim()
			.split('\n')
			.map((line) => {
				const [hash, name] = line.split(/\s+/);
				return [name, hash];
			}),
	);

function render() {
	const out = mkdtempSync(join(tmpdir(), 'afterglow-start-'));
	execFileSync('python3', [join(start, 'render.py'), out], { stdio: 'ignore' });
	return out;
}

test('the masters match their recorded hashes', () => {
	const recorded = sums('SHA256SUMS.masters');
	assert.deepEqual(Object.keys(recorded).sort(), ['banner.svg', 'orb.svg']);
	for (const [name, hash] of Object.entries(recorded)) {
		assert.equal(sha256(readFileSync(join(start, name))), hash, `${name} changed`);
	}
});

test('every master is eight times its target size, keeps its licence header and is self-contained', () => {
	const sizes = { 'orb.svg': [200, 160], 'banner.svg': [168, 1864] };
	for (const [name, [width, height]] of Object.entries(sizes)) {
		const svg = readFileSync(join(start, name), 'utf8');
		assert.match(svg, /SPDX-License-Identifier: Apache-2\.0 OR MIT/, name);
		assert.match(svg, /\(c\) Copyright 2026 Liminal HQ, Scott Morris/, name);
		assert.ok(
			svg.includes(`width="${width}" height="${height}" viewBox="0 0 ${width} ${height}"`),
			name,
		);
		assert.ok(!/<text[\s>]/.test(svg), `${name} has live text, which needs a font to render`);
		assert.ok(
			!/<script|font-family|href=|<image|@import/.test(svg),
			`${name} is not self-contained`,
		);
	}
});

test(
	'the orb DIB is 25 x 20, 32-bit, bottom-up, with the recorded hash and a clear margin',
	needTools,
	() => {
		const out = render();
		try {
			const dib = readFileSync(join(out, 'start-orb.dib'));
			assert.equal(dib.length, 40 + 25 * 20 * 4);
			assert.equal(dib.readUInt32LE(0), 40);
			assert.equal(dib.readInt32LE(4), 25);
			assert.equal(dib.readInt32LE(8), 20, 'positive height: rows are bottom-up');
			assert.equal(dib.readUInt16LE(14), 32);
			assert.equal(dib.readUInt32LE(16), 0, 'BI_RGB');
			assert.equal(dib.readUInt32LE(20), 2000, 'the size field of the stock resource');
			assert.equal(sha256(dib), sums('SHA256SUMS')['start-orb.dib'], 'start-orb.dib drifted');
			// explorer shows columns 0 to 19 only: the disc keeps a 1 px margin inside the 20 x 20 square, so rows 0 and 19 and columns 0 and 19 to 24 have no alpha
			let ink = 0;
			for (let row = 0; row < 20; row++) {
				const y = 19 - row; // bottom-up
				for (let x = 0; x < 25; x++) {
					const alpha = dib[40 + (row * 25 + x) * 4 + 3];
					const inside = x >= 1 && x <= 18 && y >= 1 && y <= 18;
					if (!inside) assert.equal(alpha, 0, `ink outside the 18 x 18 square at ${x},${y}`);
					else if (alpha > 0) ink++;
					if (alpha === 0) {
						assert.deepEqual(
							[...dib.subarray(40 + (row * 25 + x) * 4, 40 + (row * 25 + x) * 4 + 3)],
							[0, 0, 0],
							'fully transparent pixels are zeroed',
						);
					}
				}
			}
			assert.ok(ink > 200, 'the disc is drawn');
		} finally {
			rmSync(out, { recursive: true, force: true });
		}
	},
);

test(
	'the banner DIB is 21 x 233, 24-bit, bottom-up, size field 14,914, with navy at the top',
	needTools,
	() => {
		const out = render();
		try {
			const dib = readFileSync(join(out, 'start-banner.dib'));
			assert.equal(dib.length, 40 + 14914);
			assert.equal(dib.readInt32LE(4), 21);
			assert.equal(dib.readInt32LE(8), 233, 'positive height: rows are bottom-up');
			assert.equal(dib.readUInt16LE(14), 24);
			assert.equal(dib.readUInt32LE(16), 0, 'BI_RGB');
			assert.equal(dib.readUInt32LE(20), 14914, 'the size field of the stock resource');
			assert.equal(sha256(dib), sums('SHA256SUMS')['start-banner.dib'], 'start-banner.dib drifted');
			// The last stored row is the top of the picture: it must be the menu's navy, #090e2a (stored as B, G, R)
			const stride = 64;
			const top = 40 + 232 * stride;
			for (let x = 0; x < 21; x++) {
				assert.deepEqual([...dib.subarray(top + x * 3, top + x * 3 + 3)], [0x2a, 0x0e, 0x09]);
			}
		} finally {
			rmSync(out, { recursive: true, force: true });
		}
	},
);

test('rendering twice gives the same bytes', needTools, () => {
	const first = render();
	const second = render();
	try {
		for (const name of ['start-orb.dib', 'start-banner.dib']) {
			assert.ok(readFileSync(join(first, name)).equals(readFileSync(join(second, name))), name);
		}
	} finally {
		rmSync(first, { recursive: true, force: true });
		rmSync(second, { recursive: true, force: true });
	}
});
