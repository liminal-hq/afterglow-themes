// Tests for the Afterglow icon set: masters, hashes, the id map, sizes, frames and repeatable bytes
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import { existsSync, mkdtempSync, readdirSync, readFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';

const icons = join(fileURLToPath(new URL('..', import.meta.url)), 'desktop', 'icons');
const svgDir = join(icons, 'svg');
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const SIZES = [16, 24, 32, 48];

// The renderer needs rsvg-convert and Python with Pillow; the Desktop style job has them, a plain test run may not
const haveTools =
	spawnSync('rsvg-convert', ['--version'], { stdio: 'ignore' }).status === 0 &&
	spawnSync('python3', ['-c', 'import PIL'], { stdio: 'ignore' }).status === 0;
const needTools = haveTools
	? {}
	: { skip: 'rsvg-convert and python3 with Pillow are not installed' };

// The icon ids are the 48 px masters; the hinted redraws end in -16
const ids = readdirSync(svgDir)
	.filter((f) => f.endsWith('.svg') && !f.endsWith('-16.svg'))
	.map((f) => f.slice(0, -4))
	.sort();
const hinted = readdirSync(svgDir)
	.filter((f) => f.endsWith('-16.svg'))
	.map((f) => f.slice(0, -7))
	.sort();

const sums = (file) =>
	Object.fromEntries(
		readFileSync(join(icons, file), 'utf8')
			.trim()
			.split('\n')
			.map((line) => {
				const [hash, name] = line.split(/\s+/);
				return [name, hash];
			}),
	);

function render() {
	const out = mkdtempSync(join(tmpdir(), 'afterglow-icons-'));
	execFileSync('python3', [join(icons, 'render.py'), out], { stdio: 'ignore' });
	return out;
}

test('the set has 69 icons, 8 hinted 16 px redraws and a 24 and 16 profile of every icon', () => {
	assert.equal(ids.length, 69);
	assert.deepEqual(hinted, [
		'doc',
		'error',
		'folder',
		'hdd',
		'mycomputer',
		'recyclefull',
		'search',
		'warning',
	]);
	for (const sub of ['24', '16']) {
		const files = readdirSync(join(svgDir, sub)).map((f) => f.slice(0, -4));
		assert.deepEqual(files.sort(), ids, `svg/${sub}`);
	}
});

test('the masters match their recorded hashes and keep their licence header', () => {
	const recorded = sums('SHA256SUMS.masters');
	assert.equal(Object.keys(recorded).length, 69 * 3 + 8 + 2);
	for (const [name, hash] of Object.entries(recorded)) {
		assert.equal(sha256(readFileSync(join(icons, name))), hash, `${name} changed`);
		if (name.endsWith('.svg')) {
			const text = readFileSync(join(icons, name), 'utf8');
			assert.match(text, /\(c\) Copyright 2026 Liminal HQ, Scott Morris/, name);
			assert.match(text, /SPDX-License-Identifier: Apache-2\.0 OR MIT/, name);
		}
	}
});

test('every master draws on a square grid of its own size', () => {
	for (const id of ids) {
		for (const sub of ['', '24/', '16/']) {
			const svg = readFileSync(join(svgDir, `${sub}${id}.svg`), 'utf8');
			assert.ok(svg.includes('viewBox="0 0 48 48" width="48" height="48"'), `${sub}${id}`);
		}
	}
	for (const id of hinted) {
		const svg = readFileSync(join(svgDir, `${id}-16.svg`), 'utf8');
		assert.ok(svg.includes('viewBox="0 0 16 16" width="16" height="16"'), `${id}-16`);
	}
});

test('map.json names every icon once, with a status and no guessed resource ids', () => {
	const map = JSON.parse(readFileSync(join(icons, 'map.json'), 'utf8'));
	assert.deepEqual(map.icons.map((i) => i.id).sort(), ids);
	for (const icon of map.icons) {
		assert.ok(['named', 'unmapped'].includes(icon.status), icon.id);
		assert.equal(icon.resource, null, `${icon.id} has a resource id nobody checked`);
		if (icon.status === 'named') {
			assert.ok(icon.replaces && map.kinds[icon.kind], icon.id);
		} else {
			assert.equal(icon.replaces, null, icon.id);
			assert.equal(icon.kind, null, icon.id);
		}
	}
	assert.equal(map.icons.filter((i) => i.status === 'named').length, 50);
});

test(
	'the render makes one .ico per icon with 16, 24, 32 and 48 px frames of 32-bit alpha, and a PNG per frame',
	needTools,
	() => {
		const out = render();
		try {
			for (const id of ids) {
				for (const size of SIZES) {
					const png = readFileSync(join(out, 'png', `${id}-${size}.png`));
					assert.equal(png.readUInt32BE(16), size, `${id}-${size}.png width`);
					assert.equal(png.readUInt32BE(20), size, `${id}-${size}.png height`);
				}
				const ico = readFileSync(join(out, 'ico', `${id}.ico`));
				assert.deepEqual(
					[ico.readUInt16LE(0), ico.readUInt16LE(2), ico.readUInt16LE(4)],
					[0, 1, 4],
				);
				const seen = [];
				for (let i = 0; i < 4; i++) {
					const entry = 6 + i * 16;
					const [width, height] = [ico[entry], ico[entry + 1]];
					assert.equal(width, height, id);
					assert.equal(ico.readUInt16LE(entry + 6), 32, `${id} bit count`);
					const offset = ico.readUInt32LE(entry + 12);
					assert.equal(ico.readUInt32LE(offset), 40, `${id} DIB header`);
					assert.equal(ico.readInt32LE(offset + 4), width, `${id} DIB width`);
					assert.equal(ico.readInt32LE(offset + 8), height * 2, `${id} DIB height`);
					assert.equal(ico.readUInt16LE(offset + 14), 32, `${id} DIB bit count`);
					// BGRA rows: some pixel is see-through and some is opaque
					const alpha = [];
					for (let p = 3; p < width * height * 4; p += 4) alpha.push(ico[offset + 40 + p]);
					assert.ok(alpha.includes(0) && alpha.includes(255), `${id} ${width} px alpha`);
					seen.push(width);
				}
				assert.deepEqual(seen, SIZES, `${id} frames`);
			}
			assert.equal(readdirSync(join(out, 'ico')).length, 69);
			assert.equal(readdirSync(join(out, 'png')).length, 69 * 4);
			assert.ok(existsSync(join(out, 'afterglow-icons-sheet.png')));
		} finally {
			rmSync(out, { recursive: true, force: true });
		}
	},
);

test(
	'16 px frames come from the hinted redraw where there is one, and 24 px from the 24 profile',
	needTools,
	() => {
		const out = render();
		try {
			const draw = (path, size) =>
				sha256(
					execFileSync('rsvg-convert', [
						'--format',
						'png',
						'--width',
						String(size),
						'--height',
						String(size),
						join(svgDir, path),
					]),
				);
			for (const id of ids) {
				const sixteen = hinted.includes(id) ? `${id}-16.svg` : `16/${id}.svg`;
				assert.equal(
					sha256(readFileSync(join(out, 'png', `${id}-16.png`))),
					draw(sixteen, 16),
					`${id} 16`,
				);
				assert.equal(
					sha256(readFileSync(join(out, 'png', `${id}-24.png`))),
					draw(`24/${id}.svg`, 24),
					`${id} 24`,
				);
			}
		} finally {
			rmSync(out, { recursive: true, force: true });
		}
	},
);

test('two renders give the same .ico bytes, and they match the recorded hashes', needTools, () => {
	const [a, b] = [render(), render()];
	try {
		const recorded = sums('SHA256SUMS');
		assert.deepEqual(Object.keys(recorded).sort(), ids.map((id) => `ico/${id}.ico`).sort());
		for (const id of ids) {
			const first = readFileSync(join(a, 'ico', `${id}.ico`));
			assert.deepEqual(first, readFileSync(join(b, 'ico', `${id}.ico`)), `${id} differs`);
			assert.equal(sha256(first), recorded[`ico/${id}.ico`], `${id}.ico hash`);
		}
	} finally {
		rmSync(a, { recursive: true, force: true });
		rmSync(b, { recursive: true, force: true });
	}
});
