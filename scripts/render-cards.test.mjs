// Tests for the Afterglow card art: masters, hashes, the bitmap and felt entries of the map, sizes, depth, repeatable bytes and the faces' indices
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

// cards.dll's faces: resource = suit * 13 + rank, suits in this order, ace to king (dll/win32/cards/cards.rc)
const SUITS = ['clubs', 'diamonds', 'hearts', 'spades'];
const RANKS = [
	'ace',
	'two',
	'three',
	'four',
	'five',
	'six',
	'seven',
	'eight',
	'nine',
	'ten',
	'jack',
	'queen',
	'king',
];
const FACES = [
	...SUITS.flatMap((suit, suitIndex) =>
		RANKS.map((rank, rankIndex) => [
			`${String(suitIndex * 13 + rankIndex + 1).padStart(2, '0')}-${suit}-${rank}`,
			suitIndex * 13 + rankIndex + 1,
		]),
	),
	['53-free-cell', 53],
	['66-joker', 66],
];
// bitmap name -> cards.dll resource; every card bitmap is 72 x 112
const BITMAPS = {
	'card-back-sunset.bmp': 54,
	'card-x.bmp': 67,
	'card-o.bmp': 68,
	...Object.fromEntries(FACES.map(([stem, resource]) => [`card-${stem}.bmp`, resource])),
};
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
	assert.deepEqual(
		Object.keys(recorded).sort(),
		[
			'alternatives/card-back-lattice.svg',
			'alternatives/card-back-rays.svg',
			'alternatives/faces/horizon.py',
			'alternatives/faces/pixel.py',
			'card-back-sunset.svg',
			'card-o.svg',
			'card-x.svg',
			'faces/classic.py',
			'faces/faces.py',
			'faces/gen_faces.py',
			'faces/render_sheets.py',
			...FACES.map(([stem]) => `faces/${stem}.svg`),
			'gen_cards.py',
			'render.py',
		].sort(),
	);
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

test(
	'every face carries its index at the top left and, turned, at the bottom right',
	needTools,
	() => {
		const out = render();
		try {
			for (const [stem] of FACES) {
				if (stem === '53-free-cell') continue; // an empty cell has no index
				const bytes = readFileSync(join(out, `card-${stem}.bmp`));
				const pixel = (x, y) => {
					const at = 54 + (111 - y) * 72 * 3 + x * 3;
					return [bytes[at + 2], bytes[at + 1], bytes[at]];
				};
				// the rank and small suit sit in rows 4 to 12 from column 4, inside the 16 rows a Solitaire row shows; the joker's word runs down
				const [rows, columns] =
					stem === '66-joker'
						? [
								[4, 52],
								[4, 10],
							]
						: [
								[4, 12],
								[4, 25],
							];
				let ink = 0;
				for (let y = rows[0]; y <= rows[1]; y++) {
					for (let x = columns[0]; x <= columns[1]; x++) {
						assert.deepEqual(pixel(x, y), pixel(71 - x, 111 - y), `${stem} ${x}, ${y}`);
						if (pixel(x, y).reduce((sum, value) => sum + value, 0) < 500) ink++;
					}
				}
				assert.ok(ink >= 20, `${stem} has an index`);
			}
		} finally {
			rmSync(out, { recursive: true, force: true });
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
