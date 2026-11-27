// Tests for the Afterglow dialog art: masters, hashes, the bitmap map, sizes, depth and repeatable bytes
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
const dialogs = join(root, 'desktop', 'dialogs');
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');

// The renderer needs rsvg-convert and Python with Pillow; the Desktop style job has them, a plain test run may not
const haveTools =
	spawnSync('rsvg-convert', ['--version'], { stdio: 'ignore' }).status === 0 &&
	spawnSync('python3', ['-c', 'import PIL'], { stdio: 'ignore' }).status === 0;
const needTools = haveTools
	? {}
	: { skip: 'rsvg-convert and python3 with Pillow are not installed' };

// bitmap name -> [width, height], the stock sizes of the resources they replace
const BITMAPS = {
	'about-banner.bmp': [413, 72],
	'shutdown-bg.bmp': [312, 198],
	'shutdown-mark.bmp': [48, 40],
	'shutdown-strip.bmp': [33, 330],
	'logoff-strip.bmp': [33, 231],
};

const sums = (file) =>
	Object.fromEntries(
		readFileSync(join(dialogs, file), 'utf8')
			.trim()
			.split('\n')
			.map((line) => {
				const [hash, name] = line.split(/\s+/);
				return [name, hash];
			}),
	);

function render() {
	const out = mkdtempSync(join(tmpdir(), 'afterglow-dialogs-'));
	execFileSync('python3', [join(dialogs, 'render.py'), out], { stdio: 'ignore' });
	return out;
}

test('the dialog masters match their recorded hashes, keep their licence header and carry no text elements', () => {
	const recorded = sums('SHA256SUMS.masters');
	assert.deepEqual(Object.keys(recorded).sort(), [
		'about-banner.svg',
		'alternatives/shutdown-strip-mint.svg',
		'gen_dialogs.py',
		'logoff-strip.svg',
		'outline.py',
		'render.py',
		'shutdown-bg.svg',
		'shutdown-mark.svg',
		'shutdown-strip.svg',
	]);
	for (const [name, hash] of Object.entries(recorded)) {
		const bytes = readFileSync(join(dialogs, name));
		assert.equal(sha256(bytes), hash, `${name} changed`);
		const text = bytes.toString('utf8');
		assert.match(text, /\(c\) Copyright 2026 Liminal HQ, Scott Morris/, name);
		assert.match(text, /SPDX-License-Identifier: Apache-2\.0 OR MIT/, name);
		if (name.endsWith('.svg')) {
			assert.ok(!/<text\b|<image\b|<script\b/.test(text), `${name} is shapes only`);
		}
	}
});

test('map.json names each dialog bitmap with its stock resource, size and depth', () => {
	const map = JSON.parse(readFileSync(join(root, 'desktop', 'icons', 'map.json'), 'utf8'));
	const claimed = new Set();
	// the card bitmaps are render-cards.test.mjs's
	for (const entry of map.bitmaps.filter((bitmap) => !bitmap.file.startsWith('desktop/cards/'))) {
		assert.ok(existsSync(join(root, entry.file)), entry.file);
		assert.match(entry.module, /^[a-z0-9]+\.(dll|exe)$/, entry.id);
		assert.ok(Number.isInteger(entry.resource) && entry.resource > 0, entry.id);
		assert.equal(entry.bits, 24, entry.id);
		for (const kind of entry.evidence) assert.ok(['source', 'binary'].includes(kind), entry.id);
		const key = `${entry.module}:${entry.resource}`;
		assert.ok(!claimed.has(key), `${key} is claimed twice`);
		claimed.add(key);
		if (BITMAPS[entry.bitmap]) assert.deepEqual(entry.size, BITMAPS[entry.bitmap], entry.id);
	}
	assert.deepEqual([...claimed].sort(), [
		'msgina.dll:20002',
		'msgina.dll:20003',
		'msgina.dll:20004',
		'shell32.dll:131',
		'shell32.dll:138',
		'shell32.dll:500',
		'shell32.dll:501',
		'shell32.dll:502',
	]);
});

test(
	'the render makes 24-bit bottom-up BMPs at the stock sizes, the same bytes twice, matching the hashes',
	needTools,
	() => {
		const [first, second] = [render(), render()];
		try {
			const recorded = sums('SHA256SUMS');
			assert.deepEqual(Object.keys(recorded).sort(), Object.keys(BITMAPS).sort());
			for (const [name, [width, height]] of Object.entries(BITMAPS)) {
				const bytes = readFileSync(join(first, name));
				assert.equal(bytes.toString('latin1', 0, 2), 'BM', name);
				assert.equal(bytes.readUInt32LE(14), 40, `${name} header`);
				assert.equal(bytes.readInt32LE(18), width, `${name} width`);
				assert.equal(bytes.readInt32LE(22), height, `${name} height, positive for bottom-up rows`);
				assert.equal(bytes.readUInt16LE(28), 24, `${name} depth`);
				assert.equal(bytes.readUInt32LE(30), 0, `${name} uncompressed`);
				assert.deepEqual(
					bytes,
					readFileSync(join(second, name)),
					`${name} differs between renders`,
				);
				assert.equal(sha256(bytes), recorded[name], `${name} hash`);
			}
			assert.ok(existsSync(join(first, 'afterglow-dialogs-preview.png')));
		} finally {
			rmSync(first, { recursive: true, force: true });
			rmSync(second, { recursive: true, force: true });
		}
	},
);

test(
	'the Shut Down and Log Off panels stay the grey the dialogs paint their labels on',
	needTools,
	() => {
		const out = render();
		try {
			const bytes = readFileSync(join(out, 'shutdown-bg.bmp'));
			const width = 312;
			const stride = Math.ceil((width * 3) / 4) * 4;
			const pixel = (x, y) => {
				const at = 54 + (197 - y) * stride + x * 3;
				return [bytes[at + 2], bytes[at + 1], bytes[at]];
			};
			// the label rows and the button rows of both dialogs, across the whole width
			for (const y of [46, 75, 100, 114, 131, 153]) {
				for (const x of [0, 54, 156, 225, 311]) {
					assert.deepEqual(pixel(x, y), [244, 244, 244], `${x}, ${y}`);
				}
			}
		} finally {
			rmSync(out, { recursive: true, force: true });
		}
	},
);
