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
const arrowDir = join(icons, 'arrow');
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const SIZES = [16, 32, 48];

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
// The Explorer toolbar glyphs also have a 24 px profile, for browseui's 24 px bitmap strips
const toolbar = readdirSync(join(svgDir, '24'))
	.map((f) => f.slice(0, -4))
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

// The strips and panels the map names: rendered by render.py as bmp/NAME.bmp
function bitmapsDrawnHere() {
	const map = JSON.parse(readFileSync(join(icons, 'map.json'), 'utf8'));
	return [
		...new Set(
			map.bitmaps
				.filter((bitmap) => /^desktop\/icons\/(strips\.py|panels\/)/.test(bitmap.file))
				.map((bitmap) => bitmap.bitmap),
		),
	];
}

function render() {
	const out = mkdtempSync(join(tmpdir(), 'afterglow-icons-'));
	execFileSync('python3', [join(icons, 'render.py'), out], { stdio: 'ignore' });
	return out;
}

test('the set has 252 icons, 108 hinted 16 px redraws, a 32 and 16 px profile of every icon and a 24 px one of the toolbar glyphs and the Applications Manager icons', () => {
	assert.equal(ids.length, 252);
	assert.equal(hinted.length, 108);
	for (const id of [
		'mydocs',
		'mypictures',
		'mymusic',
		'myvideos',
		'desktop',
		'network',
		'favorites',
		'recent',
		'programsfolder',
		'user',
		'user-locked',
		'group',
		'showdesktop',
		'ntnamespace',
		'regkey',
		'ntobject',
		'ntdevice',
		'ntport',
		'regstring',
		'regbinary',
		'none',
		'delpermanent',
		'ovl-warning',
		'ovl-error',
		'ovl-info',
		'mk-off',
		'mk-lr-down',
	]) {
		assert.ok(hinted.includes(id), `${id} has a hinted redraw`);
	}
	assert.deepEqual(toolbar, [
		'admintools',
		'appmanager',
		'audio',
		'back',
		'browser',
		'calc',
		'check',
		'clock',
		'console-app',
		'copy',
		'copyclip',
		'cut',
		'del',
		'disconnect',
		'display',
		'doc',
		'dot',
		'down',
		'fit',
		'flask',
		'floppy-disk',
		'folder',
		'folderopen',
		'folderopts',
		'folders',
		'forward',
		'go',
		'group',
		'help',
		'home',
		'image',
		'install',
		'key',
		'landscape',
		'library',
		'logoff',
		'mapdrive',
		'minus',
		'move',
		'mycomputer',
		'newfolder',
		'paint',
		'paste',
		'pause',
		'play',
		'plus',
		'portrait',
		'printer',
		'printpreview',
		'programs',
		'properties',
		'readme',
		'redo',
		'refresh',
		'rotccw',
		'rotcw',
		'search',
		'settings',
		'sleep',
		'sol',
		'sortname',
		'star',
		'stopsq',
		'undo',
		'uninstall',
		'up',
		'user',
		'video',
		'view-large',
		'view-list',
		'view-small',
		'views',
		'wusa',
		'zoomin',
		'zoomout',
	]);
	for (const sub of ['32', '16']) {
		const files = readdirSync(join(svgDir, sub)).map((f) => f.slice(0, -4));
		assert.deepEqual(files.sort(), ids, `svg/${sub}`);
	}
	assert.deepEqual(readdirSync(arrowDir).sort(), [
		'arrow-16-hinted.svg',
		'arrow-32.svg',
		'arrow-48.svg',
	]);
});

test('the masters match their recorded hashes and keep their licence header', () => {
	const recorded = sums('SHA256SUMS.masters');
	// 252 icons in three profiles, 75 at 24 px, 108 hinted redraws, 3 arrow frames, the sheet, 11 generators and helpers, 35 panels and their index
	assert.equal(Object.keys(recorded).length, 252 * 3 + 75 + 108 + 3 + 1 + 11 + 35 + 1);
	for (const [name, hash] of Object.entries(recorded)) {
		assert.equal(sha256(readFileSync(join(icons, name))), hash, `${name} changed`);
		if (name.endsWith('.svg') || name.endsWith('.py')) {
			const text = readFileSync(join(icons, name), 'utf8');
			assert.match(text, /\(c\) Copyright 2026 Liminal HQ, Scott Morris/, name);
			assert.match(text, /SPDX-License-Identifier: Apache-2\.0 OR MIT/, name);
		}
	}
});

test('the hinted 16 px redraws are pixel art: crisp, whole-pixel rects only, no blur or gradient', () => {
	for (const id of hinted) {
		const svg = readFileSync(join(svgDir, `${id}-16.svg`), 'utf8');
		assert.ok(svg.includes('shape-rendering="crispEdges"'), id);
		assert.ok(
			!/filter|Gradient|opacity/.test(svg.split('</defs>')[1]),
			`${id} has no blur, ramp or opacity`,
		);
	}
});

test('every master draws on a square grid of its own size', () => {
	for (const id of ids) {
		for (const sub of ['', '32/', '16/', ...(toolbar.includes(id) ? ['24/'] : [])]) {
			const svg = readFileSync(join(svgDir, `${sub}${id}.svg`), 'utf8');
			assert.ok(svg.includes('viewBox="0 0 48 48" width="48" height="48"'), `${sub}${id}`);
		}
	}
	for (const id of hinted) {
		const svg = readFileSync(join(svgDir, `${id}-16.svg`), 'utf8');
		assert.ok(svg.includes('viewBox="0 0 16 16" width="16" height="16"'), `${id}-16`);
	}
	for (const [name, size] of [
		['arrow-48', 48],
		['arrow-32', 32],
		['arrow-16-hinted', 16],
	]) {
		const svg = readFileSync(join(arrowDir, `${name}.svg`), 'utf8');
		assert.ok(svg.includes(`viewBox="0 0 ${size} ${size}" width="${size}" height="${size}"`), name);
	}
});

test('map.json names every icon once and the arrow, and records only verified resources', () => {
	const map = JSON.parse(readFileSync(join(icons, 'map.json'), 'utf8'));
	assert.deepEqual(map.icons.map((i) => i.id).sort(), [...ids, 'arrow'].sort());
	const checkResource = (resource, id) => {
		assert.match(resource.module, /^[a-z0-9]+\.(dll|exe|cpl|scr|ocx)$/, id);
		assert.ok(resource.evidence.length > 0, id);
		for (const kind of resource.evidence) assert.ok(['source', 'binary'].includes(kind), id);
		if (resource.module === 'browseui.dll') {
			assert.deepEqual(resource.bitmaps, [214, 215, 216, 217], id);
			assert.ok(Number.isInteger(resource.cell) && resource.cell >= 0 && resource.cell < 47, id);
		} else {
			// a group is a number, or a string where the module names the group by string (telnet.exe and logon.scr)
			assert.ok(
				(Number.isInteger(resource.group) && resource.group > 0) ||
					/^[A-Z][A-Z0-9_]*$/.test(resource.group),
				id,
			);
		}
	};
	const claimed = new Map();
	for (const icon of map.icons) {
		assert.ok(['named', 'unmapped'].includes(icon.status), icon.id);
		for (const resource of [icon.resource, ...(icon.also ?? [])].filter(Boolean)) {
			checkResource(resource, icon.id);
			// one icon per group or cell
			const key = `${resource.module}:${resource.group ?? `cell ${resource.cell}`}`;
			assert.equal(
				claimed.get(key),
				undefined,
				`${key} is claimed by ${claimed.get(key)} and ${icon.id}`,
			);
			claimed.set(key, icon.id);
		}
		if (icon.status === 'named') {
			assert.ok(icon.replaces && map.kinds[icon.kind], icon.id);
		} else {
			assert.equal(icon.replaces, null, icon.id);
			assert.equal(icon.kind, null, icon.id);
			assert.equal(icon.resource, null, icon.id);
		}
		// a toolbar glyph names one cell of the strips, unless its art is a bitmap of its own (the Go button)
		if (icon.kind === 'toolbar' && !map.bitmaps.some((bitmap) => bitmap.id === icon.id)) {
			const cells = [icon.resource, ...(icon.also ?? [])].filter(
				(r) => r?.module === 'browseui.dll',
			);
			assert.equal(cells.length, 1, `${icon.id} names one toolbar cell`);
		}
	}
	assert.deepEqual(
		map.icons.filter((i) => i.status === 'unmapped').map((i) => i.id),
		['cd-disc', 'clock', 'floppy-disk', 'showdesk'],
	);
	// The folder ids the folder icon research verified in the 0.4.16 source and binary are unchanged
	const shell32 = Object.fromEntries(
		map.icons
			.filter((i) => i.resource?.module === 'shell32.dll')
			.map((i) => [i.id, i.resource.group]),
	);
	for (const [id, group] of Object.entries({
		arrow: 30,
		desktop: 35,
		folder: 4,
		folderopen: 5,
		mycomputer: 16,
		mydocs: 235,
		mymusic: 237,
		mypictures: 236,
		myvideos: 238,
		network: 18,
		recycle: 32,
		recyclefull: 33,
	})) {
		assert.equal(shell32[id], group, id);
	}
});

test(
	'the render makes one .ico per icon and the arrow with 16, 32 and 48 px frames of 32-bit alpha, and a PNG per frame',
	needTools,
	() => {
		const out = render();
		try {
			for (const id of [...ids, 'arrow']) {
				for (const size of SIZES) {
					const png = readFileSync(join(out, 'png', `${id}-${size}.png`));
					assert.equal(png.readUInt32BE(16), size, `${id}-${size}.png width`);
					assert.equal(png.readUInt32BE(20), size, `${id}-${size}.png height`);
				}
				const ico = readFileSync(join(out, 'ico', `${id}.ico`));
				assert.deepEqual(
					[ico.readUInt16LE(0), ico.readUInt16LE(2), ico.readUInt16LE(4)],
					[0, 1, 3],
				);
				const seen = [];
				for (let i = 0; i < 3; i++) {
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
			assert.equal(readdirSync(join(out, 'ico')).length, 253);
			assert.equal(readdirSync(join(out, 'png')).length, 253 * 3 + toolbar.length);
			// the 24 px toolbar frames: a one-frame .ico each, so the three-frame .ico stays as the shell patchers read it
			assert.deepEqual(
				readdirSync(join(out, 'ico24')).sort(),
				toolbar.map((id) => `${id}.ico`),
			);
			for (const id of toolbar) {
				const ico = readFileSync(join(out, 'ico24', `${id}.ico`));
				assert.deepEqual(
					[ico.readUInt16LE(4), ico[6], ico[7], ico.readUInt16LE(12)],
					[1, 24, 24, 32],
					id,
				);
			}
			assert.ok(existsSync(join(out, 'afterglow-icons-sheet.png')));
			assert.ok(existsSync(join(out, 'afterglow-arrow-preview.png')));
		} finally {
			rmSync(out, { recursive: true, force: true });
		}
	},
);

test(
	'16 px frames come from the hinted redraw where there is one, 32 px from the 32 profile, and the arrow from its own masters',
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
					sha256(readFileSync(join(out, 'png', `${id}-32.png`))),
					draw(`32/${id}.svg`, 32),
					`${id} 32`,
				);
			}
			for (const [size, name] of [
				[16, 'arrow-16-hinted'],
				[32, 'arrow-32'],
				[48, 'arrow-48'],
			]) {
				assert.equal(
					sha256(readFileSync(join(out, 'png', `arrow-${size}.png`))),
					draw(`../arrow/${name}.svg`, size),
					`arrow ${size}`,
				);
			}
		} finally {
			rmSync(out, { recursive: true, force: true });
		}
	},
);

test(
	'the arrow draws only inside the stock overlay box at the bottom left, so the rest of the icon stays clear',
	needTools,
	() => {
		const out = render();
		try {
			// The stock boxes: 16 x 16 on 48, 11 x 11 on 32 and 8 x 8 on 16
			const box = { 48: 16, 32: 11, 16: 8 };
			const ico = readFileSync(join(out, 'ico', 'arrow.ico'));
			for (let i = 0; i < 3; i++) {
				const entry = 6 + i * 16;
				const size = ico[entry];
				const offset = ico.readUInt32LE(entry + 12) + 40;
				// rows are bottom-up: file row 0 is the bottom of the image
				for (let row = 0; row < size; row++) {
					for (let x = 0; x < size; x++) {
						if (x < box[size] && row < box[size]) continue;
						// the baked shadow's blur leaves a tail under 3 % alpha at the box edge; none of it is drawn at 16
						assert.ok(
							ico[offset + (row * size + x) * 4 + 3] <= (size === 16 ? 0 : 8),
							`${size} px pixel ${x},${row}`,
						);
					}
				}
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
		assert.deepEqual(
			Object.keys(recorded).sort(),
			[
				...[...ids, 'arrow'].map((id) => `ico/${id}.ico`),
				...toolbar.map((id) => `ico24/${id}.ico`),
				'bmp/go.bmp',
				...bitmapsDrawnHere(),
			].sort(),
		);
		for (const id of [...ids, 'arrow']) {
			const first = readFileSync(join(a, 'ico', `${id}.ico`));
			assert.deepEqual(first, readFileSync(join(b, 'ico', `${id}.ico`)), `${id} differs`);
			assert.equal(sha256(first), recorded[`ico/${id}.ico`], `${id}.ico hash`);
		}
		for (const id of toolbar) {
			const first = readFileSync(join(a, 'ico24', `${id}.ico`));
			assert.deepEqual(first, readFileSync(join(b, 'ico24', `${id}.ico`)), `${id} 24 px differs`);
			assert.equal(sha256(first), recorded[`ico24/${id}.ico`], `${id} 24 px hash`);
		}
		const go = readFileSync(join(a, 'bmp', 'go.bmp'));
		assert.deepEqual(go, readFileSync(join(b, 'bmp', 'go.bmp')), 'go.bmp differs');
		assert.equal(sha256(go), recorded['bmp/go.bmp'], 'go.bmp hash');
	} finally {
		rmSync(a, { recursive: true, force: true });
		rmSync(b, { recursive: true, force: true });
	}
});

test(
	'the Go button is a 20 x 20 32-bit bitmap with straight alpha, laid out like the stock browseui.dll 230 and 231',
	needTools,
	() => {
		const map = JSON.parse(readFileSync(join(icons, 'map.json'), 'utf8'));
		const entries = map.bitmaps.filter((entry) => entry.id === 'go');
		assert.deepEqual(
			entries.map((entry) => [entry.module, entry.resource, entry.size, entry.bits]),
			[
				['browseui.dll', 230, [20, 20], 32],
				['browseui.dll', 231, [20, 20], 32],
			],
		);
		const out = render();
		try {
			const bmp = readFileSync(join(out, 'bmp', 'go.bmp'));
			assert.equal(bmp.toString('latin1', 0, 2), 'BM');
			assert.equal(bmp.readUInt32LE(10), 54, 'pixels follow the info header');
			assert.equal(bmp.length, 54 + 20 * 20 * 4);
			// the info header of the stock resource: 40 bytes, 20 x 20 bottom-up, one plane, 32 bits, BI_RGB, no size or resolution
			assert.deepEqual(
				[0, 4, 8, 12, 14, 16, 20, 24, 28, 32, 36].map((at, index) =>
					index === 3 || index === 4 ? bmp.readUInt16LE(14 + at) : bmp.readInt32LE(14 + at),
				),
				[40, 20, 20, 1, 32, 0, 0, 0, 0, 0, 0],
			);
			const alpha = [];
			for (let p = 54 + 3; p < bmp.length; p += 4) alpha.push(bmp[p]);
			assert.ok(alpha.includes(0) && alpha.includes(255), 'see-through corners and an opaque disc');
		} finally {
			rmSync(out, { recursive: true, force: true });
		}
	},
);

test(
	'the strips and panels have the size of the stock bitmap they replace, 24-bit or 32-bit BI_RGB with an uncompressed 40-byte info header',
	needTools,
	() => {
		const map = JSON.parse(readFileSync(join(icons, 'map.json'), 'utf8'));
		const out = render();
		try {
			for (const entry of map.bitmaps.filter((bitmap) =>
				/^desktop\/icons\/(strips\.py|panels\/)/.test(bitmap.file),
			)) {
				const bmp = readFileSync(join(out, entry.bitmap));
				assert.equal(bmp.toString('latin1', 0, 2), 'BM', entry.bitmap);
				assert.equal(bmp.readUInt32LE(14), 40, `${entry.bitmap} info header`);
				assert.deepEqual([bmp.readInt32LE(18), bmp.readInt32LE(22)], entry.size, entry.bitmap);
				const bits = bmp.readUInt16LE(28);
				assert.ok(
					bits === 24 || (bits === 32 && entry.bits === 32),
					`${entry.bitmap} is ${bits}-bit`,
				);
				assert.equal(bmp.readUInt32LE(30), 0, `${entry.bitmap} is BI_RGB`);
				const row = Math.ceil((entry.size[0] * bits) / 8 / 4) * 4;
				assert.equal(bmp.length, 54 + row * entry.size[1], `${entry.bitmap} length`);
			}
		} finally {
			rmSync(out, { recursive: true, force: true });
		}
	},
);
