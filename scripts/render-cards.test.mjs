// Tests for the Afterglow card art: masters, hashes, the bitmap and felt entries of the map, sizes, depth and repeatable bytes
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdtempSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('..', import.meta.url));
const cards = join(root, 'desktop', 'cards');
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');

// The renderer needs rsvg-convert and Python with Pillow; the Desktop style job has them, a plain test run may not
const haveTools =
	spawnSync('rsvg-convert', ['--version'], { stdio: 'ignore' }).status === 0 &&
	spawnSync('python3', ['-c', 'import PIL'], { stdio: 'ignore' }).status === 0;
const needTools = haveTools
	? {}
	: { skip: 'rsvg-convert and python3 with Pillow are not installed' };

// bitmap name -> cards.dll resource; every card bitmap is 72 x 112
const BITMAPS = { 'card-back-sunset.bmp': 54, 'card-x.bmp': 67, 'card-o.bmp': 68 };
const FELT = [0x1f, 0x25, 0x54];

const sums = (file) =>
	Object.fromEntries(
		readFileSync(join(cards, file), 'utf8')
			.trim()
			.split('\n')
			.map((line) => {
				const [hash, name] = line.split(/\s+/);
				return [name, hash];
			}),
	);

function render() {
	const out = mkdtempSync(join(tmpdir(), 'afterglow-cards-'));
	execFileSync('python3', [join(cards, 'render.py'), out], { stdio: 'ignore' });
	return out;
}

test('the card masters match their recorded hashes, keep their licence header and carry no text elements', () => {
	const recorded = sums('SHA256SUMS.masters');
	assert.deepEqual(Object.keys(recorded).sort(), [
		'alternatives/card-back-lattice.svg',
		'alternatives/card-back-rays.svg',
		'card-back-sunset.svg',
		'card-o.svg',
		'card-x.svg',
		'gen_cards.py',
		'render.py',
	]);
	for (const [name, hash] of Object.entries(recorded)) {
		const bytes = readFileSync(join(cards, name));
		assert.equal(sha256(bytes), hash, `${name} changed`);
		const text = bytes.toString('utf8');
		assert.match(text, /\(c\) Copyright 2026 Liminal HQ, Scott Morris/, name);
		assert.match(text, /SPDX-License-Identifier: Apache-2\.0 OR MIT/, name);
		if (name.endsWith('.svg')) {
			assert.ok(!/<text\b|<image\b|<script\b/.test(text), `${name} is shapes only`);
			assert.ok(text.includes('viewBox="0 0 72 112"'), `${name} is drawn in the card's pixels`);
		}
	}
});

test('map.json names each card bitmap in cards.dll and the felt colour in both games', () => {
	const map = JSON.parse(readFileSync(join(root, 'desktop', 'icons', 'map.json'), 'utf8'));
	const entries = map.bitmaps.filter((entry) => entry.file.startsWith('desktop/cards/'));
	assert.deepEqual(
		Object.fromEntries(entries.map((entry) => [entry.bitmap, entry.resource])),
		BITMAPS,
	);
	for (const entry of entries) {
		assert.ok(existsSync(join(root, entry.file)), entry.file);
		assert.equal(entry.module, 'cards.dll', entry.id);
		assert.deepEqual(entry.size, [72, 112], entry.id);
		assert.equal(entry.bits, 8, `${entry.id} records the stock depth`);
		assert.deepEqual(entry.evidence, ['source', 'binary'], entry.id);
	}
	const felt = map.colours.find((colour) => colour.id === 'felt');
	assert.deepEqual(
		felt.code.map((site) => site.module),
		['sol.exe', 'spider.exe'],
	);
	for (const site of felt.code) {
		assert.equal(site.stock_bytes, '00 50 00 02', site.module);
		assert.equal(
			site.afterglow_bytes,
			`${FELT.map((value) => value.toString(16).padStart(2, '0')).join(' ')} 02`,
			site.module,
		);
	}
});

test(
	'the render makes 24-bit bottom-up 72 x 112 BMPs, the same bytes twice, matching the hashes',
	needTools,
	() => {
		const [first, second] = [render(), render()];
		try {
			const recorded = sums('SHA256SUMS');
			assert.deepEqual(Object.keys(recorded).sort(), Object.keys(BITMAPS).sort());
			for (const name of Object.keys(BITMAPS)) {
				const bytes = readFileSync(join(first, name));
				assert.equal(bytes.toString('latin1', 0, 2), 'BM', name);
				assert.equal(bytes.readUInt32LE(14), 40, `${name} header`);
				assert.equal(bytes.readInt32LE(18), 72, `${name} width`);
				assert.equal(bytes.readInt32LE(22), 112, `${name} height, positive for bottom-up rows`);
				assert.equal(bytes.readUInt16LE(28), 24, `${name} depth`);
				assert.equal(bytes.readUInt32LE(30), 0, `${name} uncompressed`);
				assert.deepEqual(
					bytes,
					readFileSync(join(second, name)),
					`${name} differs between renders`,
				);
				assert.equal(sha256(bytes), recorded[name], `${name} hash`);
			}
			assert.ok(existsSync(join(first, 'afterglow-cards-preview.png')));
		} finally {
			rmSync(first, { recursive: true, force: true });
			rmSync(second, { recursive: true, force: true });
		}
	},
);

test('the empty-pile marks are drawn on the dusk felt, edge to edge', needTools, () => {
	const out = render();
	try {
		for (const name of ['card-x.bmp', 'card-o.bmp']) {
			const bytes = readFileSync(join(out, name));
			const stride = 72 * 3;
			const pixel = (x, y) => {
				const at = 54 + (111 - y) * stride + x * 3;
				return [bytes[at + 2], bytes[at + 1], bytes[at]];
			};
			for (const [x, y] of [
				[0, 0],
				[71, 0],
				[0, 111],
				[71, 111],
				[36, 4],
				[4, 56],
			]) {
				assert.deepEqual(pixel(x, y), FELT, `${name} ${x}, ${y}`);
			}
		}
	} finally {
		rmSync(out, { recursive: true, force: true });
	}
});
