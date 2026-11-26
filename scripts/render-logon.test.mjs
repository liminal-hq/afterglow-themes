// Tests for the ReactOS logon banner masters and their renderer: hashes, sizes, depth and repeatable bytes
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

const logon = join(fileURLToPath(new URL('..', import.meta.url)), 'desktop', 'logon');
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
		readFileSync(join(logon, file), 'utf8')
			.trim()
			.split('\n')
			.map((line) => {
				const [hash, name] = line.split(/\s+/);
				return [name, hash];
			}),
	);

function render() {
	const out = mkdtempSync(join(tmpdir(), 'afterglow-logon-'));
	execFileSync('python3', [join(logon, 'render.py'), out], { stdio: 'ignore' });
	return out;
}

test('the masters match their recorded hashes', () => {
	const recorded = sums('SHA256SUMS.masters');
	assert.deepEqual(Object.keys(recorded).sort(), ['banner-a.svg', 'banner-b.svg', 'bar.svg']);
	for (const [name, hash] of Object.entries(recorded)) {
		assert.equal(sha256(readFileSync(join(logon, name))), hash, `${name} changed`);
	}
});

test('every master is four times its target size, keeps its licence header and has outlined text', () => {
	const sizes = { 'banner-a.svg': [1652, 288], 'banner-b.svg': [1652, 288], 'bar.svg': [1652, 20] };
	for (const [name, [width, height]] of Object.entries(sizes)) {
		const svg = readFileSync(join(logon, name), 'utf8');
		assert.match(svg, /SPDX-License-Identifier: Apache-2\.0 OR MIT/, name);
		assert.match(svg, /\(c\) Copyright 2026 Liminal HQ, Scott Morris/, name);
		assert.ok(
			svg.includes(`width="${width}" height="${height}" viewBox="0 0 ${width} ${height}"`),
			name,
		);
		assert.ok(!/<text[\s>]/.test(svg), `${name} has live text, which needs a font to render`);
	}
});

test('the Quill concept banner is not in the layout', () => {
	for (const name of ['banner-c.svg']) assert.throws(() => readFileSync(join(logon, name)));
});

test(
	'the render is a 413 x 72 and a 413 x 5 24-bit BMP with the recorded hashes',
	needTools,
	() => {
		const out = render();
		try {
			const recorded = sums('SHA256SUMS');
			for (const [name, width, height] of [
				['afterglow-banner.bmp', 413, 72],
				['afterglow-bar.bmp', 413, 5],
			]) {
				const bmp = readFileSync(join(out, name));
				const rowBytes = Math.ceil((width * 3) / 4) * 4;
				assert.equal(bmp.toString('latin1', 0, 2), 'BM');
				assert.equal(bmp.readUInt32LE(2), bmp.length);
				assert.equal(bmp.readUInt32LE(10), 54);
				assert.equal(bmp.readUInt32LE(14), 40);
				assert.equal(bmp.readInt32LE(18), width);
				assert.equal(bmp.readInt32LE(22), height, 'positive height: rows are bottom-up');
				assert.equal(bmp.readUInt16LE(28), 24);
				assert.equal(bmp.readUInt32LE(30), 0, 'BI_RGB, uncompressed');
				assert.equal(bmp.length, 54 + rowBytes * height);
				assert.equal(sha256(bmp), recorded[name], `${name} drifted from desktop/logon/SHA256SUMS`);
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
		for (const name of ['afterglow-banner.bmp', 'afterglow-bar.bmp']) {
			assert.ok(readFileSync(join(first, name)).equals(readFileSync(join(second, name))), name);
		}
	} finally {
		rmSync(first, { recursive: true, force: true });
		rmSync(second, { recursive: true, force: true });
	}
});

test('the previews are the 2x and 4x sizes', needTools, () => {
	const out = render();
	try {
		for (const [name, width, height] of [
			['afterglow-banner-2x.png', 826, 144],
			['afterglow-banner-4x.png', 1652, 288],
			['afterglow-bar-2x.png', 826, 10],
			['afterglow-bar-4x.png', 1652, 20],
			['afterglow-logon-preview.png', 826, 154],
		]) {
			const png = readFileSync(join(out, name));
			assert.equal(png.toString('latin1', 1, 4), 'PNG');
			assert.equal(png.readUInt32BE(16), width, name);
			assert.equal(png.readUInt32BE(20), height, name);
		}
	} finally {
		rmSync(out, { recursive: true, force: true });
	}
});
