// Tests for the ReactOS boot logo master and its renderer: hashes, canvas, palette, slot size, clear progress box and repeatable bytes
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

const boot = join(fileURLToPath(new URL('..', import.meta.url)), 'desktop', 'boot');
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const palette = JSON.parse(readFileSync(join(boot, 'palette.json'), 'utf8'));
const [WIDTH, HEIGHT] = palette.size;

// The renderer needs rsvg-convert and Python with Pillow; the Desktop style job has them, a plain test run may not
const haveTools =
	spawnSync('rsvg-convert', ['--version'], { stdio: 'ignore' }).status === 0 &&
	spawnSync('python3', ['-c', 'import PIL'], { stdio: 'ignore' }).status === 0;
const needTools = haveTools
	? {}
	: { skip: 'rsvg-convert and python3 with Pillow are not installed' };

const sums = (file) =>
	Object.fromEntries(
		readFileSync(join(boot, file), 'utf8')
			.trim()
			.split('\n')
			.map((line) => {
				const [hash, name] = line.split(/\s+/);
				return [name, hash];
			}),
	);

function render() {
	const out = mkdtempSync(join(tmpdir(), 'afterglow-boot-'));
	execFileSync('python3', [join(boot, 'render.py'), out], { stdio: 'ignore' });
	return out;
}

// The palette indices of a 4-bit uncompressed BMP, top row first
function pixels4(bmp) {
	const rowBytes = Math.ceil(WIDTH / 8) * 4;
	const rows = [];
	for (let y = HEIGHT - 1; y >= 0; y--) {
		const row = [];
		for (let x = 0; x < WIDTH; x++) {
			const byte = bmp[bmp.readUInt32LE(10) + y * rowBytes + (x >> 1)];
			row.push(x % 2 === 0 ? byte >> 4 : byte & 15);
		}
		rows.push(row);
	}
	return rows;
}

// The palette indices an RLE4 BMP draws, top row first, from encoded runs and the escapes the encoder can emit
function pixelsRle4(bmp) {
	const bits = bmp.subarray(bmp.readUInt32LE(10));
	const rows = Array.from({ length: HEIGHT }, () => new Array(WIDTH).fill(0));
	let x = 0;
	let y = HEIGHT - 1;
	for (let i = 0; i < bits.length;) {
		const [count, value] = [bits[i], bits[i + 1]];
		i += 2;
		if (count) {
			for (let k = 0; k < count; k++, x++) {
				if (x < WIDTH && y >= 0) rows[y][x] = k % 2 === 0 ? value >> 4 : value & 15;
			}
		} else if (value === 0) {
			[x, y] = [0, y - 1];
		} else if (value === 1) {
			break;
		} else {
			assert.fail(`unexpected RLE4 escape ${value}`);
		}
	}
	return rows;
}

test('the master and palette match their recorded hashes', () => {
	const recorded = sums('SHA256SUMS.masters');
	assert.deepEqual(Object.keys(recorded).sort(), ['boot-logo.svg', 'palette.json']);
	for (const [name, hash] of Object.entries(recorded)) {
		assert.equal(sha256(readFileSync(join(boot, name))), hash, `${name} changed`);
	}
});

test('the master is four times the canvas, has a licence header, outlined text and no scripts', () => {
	const svg = readFileSync(join(boot, 'boot-logo.svg'), 'utf8');
	assert.match(svg, /SPDX-License-Identifier: Apache-2\.0 OR MIT/);
	assert.match(svg, /\(c\) Copyright 2026 Liminal HQ, Scott Morris/);
	const [w, h] = [WIDTH * 4, HEIGHT * 4];
	assert.ok(svg.includes(`width="${w}" height="${h}" viewBox="0 0 ${w} ${h}"`));
	assert.ok(!/<text[\s>]/.test(svg), 'live text needs a font to render');
	assert.ok(!/<script|\son[a-z]+=/i.test(svg), 'a master carries no scripts');
	assert.ok(!/ReactOS logo|<image/i.test(svg), 'no ReactOS art and no embedded bitmaps');
});

test('the palette has 16 entries, distinct in six bits, with the shown colours the DAC gives and the backdrop first', () => {
	assert.equal(palette.entries.length, 16);
	palette.entries.forEach((entry, i) => {
		assert.equal(entry.index, i);
		assert.match(entry.rgb, /^#[0-9a-f]{6}$/);
		const shown = [1, 3, 5].map((at) => {
			const dac = parseInt(entry.rgb.slice(at, at + 2), 16) >> 2;
			return ((dac << 2) | (dac & 1 ? 3 : 0)).toString(16).padStart(2, '0');
		});
		assert.equal(entry.shown, `#${shown.join('')}`, `${entry.rgb} is shown differently`);
		assert.ok(entry.role.length > 0);
	});
	assert.equal(new Set(palette.entries.map((e) => e.dac.join())).size, 16);
	assert.equal(palette.entries[0].rgb, '#090e2a');
	assert.equal(palette.entries[0].shown, '#080f28');
	assert.equal(palette.entries[15].rgb, '#fff3de');
	assert.equal(palette.slot, 16504);
});

test('every fill in the master is a palette entry', () => {
	const svg = readFileSync(join(boot, 'boot-logo.svg'), 'utf8');
	const known = new Set(palette.entries.map((e) => e.rgb));
	const fills = [...svg.matchAll(/fill="(#[0-9a-f]{6})"/g)].map((m) => m[1]);
	assert.ok(fills.length > 10);
	for (const fill of fills) assert.ok(known.has(fill), `${fill} is not in palette.json`);
});

test('the 4-bit BMP is the exact canvas with the 16-entry palette', needTools, () => {
	const out = render();
	try {
		const bmp = readFileSync(join(out, 'afterglow-logo-4bit.bmp'));
		assert.equal(bmp.toString('latin1', 0, 2), 'BM');
		assert.equal(bmp.readUInt32LE(2), bmp.length);
		assert.equal(bmp.readUInt32LE(10), 14 + 40 + 64);
		assert.equal(bmp.readUInt32LE(14), 40);
		assert.equal(bmp.readInt32LE(18), WIDTH);
		assert.equal(bmp.readInt32LE(22), HEIGHT, 'positive height: rows are bottom-up');
		assert.equal(bmp.readUInt16LE(28), 4);
		assert.equal(bmp.readUInt32LE(30), 0, 'BI_RGB, uncompressed');
		assert.equal(bmp.readUInt32LE(46), 16);
		assert.equal(bmp.length, 118 + Math.ceil(WIDTH / 8) * 4 * HEIGHT);
		palette.entries.forEach((entry, i) => {
			const at = 54 + i * 4;
			const rgb = [bmp[at + 2], bmp[at + 1], bmp[at]].map((v) => v.toString(16).padStart(2, '0'));
			assert.equal(`#${rgb.join('')}`, entry.rgb);
			assert.equal(bmp[at + 3], 0);
		});
		assert.ok(
			pixels4(bmp)
				.flat()
				.every((v) => v < 16),
		);
	} finally {
		rmSync(out, { recursive: true, force: true });
	}
});

test(
	'the RLE4 BMP draws the same pixels, fits the slot and has the recorded hashes',
	needTools,
	() => {
		const out = render();
		try {
			const recorded = sums('SHA256SUMS');
			const plain = readFileSync(join(out, 'afterglow-logo-4bit.bmp'));
			const rle = readFileSync(join(out, 'afterglow-logo-rle4.bmp'));
			assert.equal(rle.readUInt32LE(30), 2, 'BI_RLE4');
			assert.equal(rle.readUInt32LE(34), rle.length - 118, 'the image size is the run data');
			assert.equal(rle.readUInt32LE(2), rle.length);
			assert.equal(rle.subarray(54, 118).compare(plain, 54, 118), 0, 'same palette');
			assert.deepEqual(pixelsRle4(rle), pixels4(plain));
			assert.deepEqual(
				[rle[rle.length - 2], rle[rle.length - 1]],
				[0, 1],
				'ends with end of bitmap',
			);
			const dib = rle.length - 14;
			assert.ok(dib <= palette.slot, `the DIB is ${dib} bytes and the slot holds ${palette.slot}`);
			assert.ok(dib < palette.slot * 0.9, 'keeps some room under the slot');
			assert.equal(
				sha256(plain),
				recorded['afterglow-logo-4bit.bmp'],
				'4-bit drifted from SHA256SUMS',
			);
			assert.equal(
				sha256(rle),
				recorded['afterglow-logo-rle4.bmp'],
				'RLE4 drifted from SHA256SUMS',
			);
		} finally {
			rmSync(out, { recursive: true, force: true });
		}
	},
);

test('the progress bar box and the bottom row are clear', needTools, () => {
	{
		const out = render();
		try {
			const rows = pixels4(readFileSync(join(out, 'afterglow-logo-4bit.bmp')));
			const { x, y, width, height } = palette.progressBox;
			assert.ok(x + width <= WIDTH && y + height <= HEIGHT);
			for (let j = y; j < y + height; j++) {
				for (let i = x; i < x + width; i++) assert.equal(rows[j][i], 0, `${i},${j}`);
			}
			assert.ok(
				rows[HEIGHT - 1].every((v) => v === 0),
				'the bottom row is backdrop',
			);
		} finally {
			rmSync(out, { recursive: true, force: true });
		}
	}
});

test('the render uses every palette entry', needTools, () => {
	const out = render();
	try {
		const rows = pixels4(readFileSync(join(out, 'afterglow-logo-4bit.bmp')));
		assert.equal(new Set(rows.flat()).size, 16);
	} finally {
		rmSync(out, { recursive: true, force: true });
	}
});

test('rendering twice gives the same bytes', needTools, () => {
	{
		const first = render();
		const second = render();
		try {
			for (const name of [
				'afterglow-logo-4bit.bmp',
				'afterglow-logo-rle4.bmp',
				'afterglow-logo-1x.png',
				'afterglow-logo-2x.png',
				'afterglow-logo-report.txt',
			]) {
				assert.ok(readFileSync(join(first, name)).equals(readFileSync(join(second, name))), name);
			}
		} finally {
			rmSync(first, { recursive: true, force: true });
			rmSync(second, { recursive: true, force: true });
		}
	}
});

test('the previews are the 1x and 2x sizes and the report names the slot', needTools, () => {
	const out = render();
	try {
		for (const [name, width, height] of [
			['afterglow-logo-1x.png', WIDTH, HEIGHT],
			['afterglow-logo-2x.png', WIDTH * 2, HEIGHT * 2],
		]) {
			const png = readFileSync(join(out, name));
			assert.equal(png.toString('latin1', 1, 4), 'PNG');
			assert.equal(png.readUInt32BE(16), width, name);
			assert.equal(png.readUInt32BE(20), height, name);
		}
		const report = readFileSync(join(out, 'afterglow-logo-report.txt'), 'utf8');
		assert.match(report, /slot 16504, \d+ to spare/);
	} finally {
		rmSync(out, { recursive: true, force: true });
	}
});
