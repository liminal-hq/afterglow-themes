// Tests for the Afterglow for ReactOS CD media in both styles: the masters' geometry, palette, wording and type sizes, the generator, and
// the print render
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import assert from 'node:assert/strict';
import { execFileSync, spawnSync } from 'node:child_process';
import { existsSync, mkdtempSync, readFileSync, readdirSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';

const root = fileURLToPath(new URL('..', import.meta.url));
const media = join(root, 'desktop', 'cd-media');
// Both styles draw the same pieces under the same names, in stepped/ and smooth/
const STYLES = ['stepped', 'smooth'];
const read = (style, name) => readFileSync(join(media, style, name), 'utf8');
const each = (names) => STYLES.flatMap((style) => names.map((name) => [style, name]));

// The physical specification, in mm, written out here rather than read from the generator so the two check each other
const DISC = {
	size: 120,
	edge: 60,
	printOuter: 59,
	label: 58.5,
	hole: 20.5,
	stacking: 16.5,
	spindle: 7.5,
};
const LABEL = { size: 123, cut: 58.5, hole: 20.5, bleed: 3 };
const SAFE = { inner: 23, outer: 56 };
const MIN_POINTS = 6;
const DISCS = ['disc.svg', 'alternatives/disc-sunrise.svg', 'alternatives/disc-horizon.svg'];
const MASTERS = [...DISCS, 'label.svg', 'jewel-front.svg', 'jewel-back.svg', 'mockup.svg'];

const palette = new Set(
	JSON.parse(readFileSync(join(root, 'desktop', 'boot', 'palette.json'), 'utf8')).entries.map(
		(entry) => entry.rgb,
	),
);
// The Afterglow colours from outside the boot palette that gen_media.py names in EXTRA_COLOURS
for (const colour of [
	'#b4bfce',
	'#fbfaf6',
	'#e4e2ec',
	'#8f8da6',
	'#f43f5e',
	'#ffffff',
	'#ffd08e',
	'#ffbd67',
	'#ffaa40',
	'#fca073',
	'#f995a6',
]) {
	palette.add(colour);
}

// Every text path: its words, size and points (the paths are absolute M, L and Q pairs, so the points bound the outline)
function texts(svg) {
	return [
		...svg.matchAll(/<path data-text="([^"]*)" data-pt="([\d.]+)" fill="[^"]+" d="([^"]+)"\/>/g),
	].map(([, words, points, data]) => {
		const numbers = data
			.replace(/[MLQZ]/g, ' ')
			.trim()
			.split(/\s+/)
			.map(Number);
		const coordinates = [];
		for (let i = 0; i < numbers.length; i += 2) coordinates.push([numbers[i], numbers[i + 1]]);
		return { words: words.replace(/&amp;/g, '&'), points: Number(points), coordinates };
	});
}

function guideCircles(svg) {
	const guides = svg.match(/<g id="guides" data-print="no"[^>]*>(.*?)<\/g>/s);
	assert.ok(guides, 'a guides group');
	return [
		...guides[1].matchAll(
			/<circle cx="([\d.]+)" cy="([\d.]+)" r="([\d.]+)" data-guide="([^"]+)"\/>/g,
		),
	].map(([, x, y, r, name]) => ({ x: Number(x), y: Number(y), r: Number(r), name }));
}

// The radii of an even-odd annulus written as two full circles of arcs
function annulus(svg, id) {
	const clip = svg.match(
		new RegExp(`<clipPath id="${id}"><path clip-rule="evenodd" d="([^"]+)"/></clipPath>`),
	);
	assert.ok(clip, `${id} clip`);
	return [...clip[1].matchAll(/a([\d.]+) /g)]
		.map((match) => Number(match[1]))
		.filter((_, i) => i % 2 === 0);
}

test('the masters keep their licence header, are shapes only and use only Afterglow colours', () => {
	for (const [style, file] of each(MASTERS)) {
		const svg = read(style, file);
		const name = `${style}/${file}`;
		assert.match(svg, /\(c\) Copyright 2026 Liminal HQ, Scott Morris/, name);
		assert.match(svg, /SPDX-License-Identifier: Apache-2\.0 OR MIT/, name);
		assert.ok(
			!/<text\b|<image\b|<script\b|<style\b|font-family/.test(svg),
			`${name} is shapes only`,
		);
		for (const [, colour] of svg.matchAll(/(?:fill|stroke|stop-color)="(#[0-9a-f]{6})"/gi)) {
			assert.ok(
				palette.has(colour.toLowerCase()),
				`${name} uses ${colour}, which is not an Afterglow colour`,
			);
		}
	}
});

test('each disc is a 120 mm artboard with the hole, the printable limits and the safe area on its guide layer', () => {
	for (const [style, file] of each(DISCS)) {
		const svg = read(style, file);
		const name = `${style}/${file}`;
		assert.match(svg, /width="120mm" height="120mm" viewBox="0 0 120 120"/, name);
		const circles = guideCircles(svg);
		for (const circle of circles)
			assert.deepEqual([circle.x, circle.y], [60, 60], `${name} ${circle.name} centred`);
		assert.deepEqual(
			circles.map((circle) => circle.r).sort((a, b) => b - a),
			[
				DISC.edge,
				DISC.printOuter,
				DISC.label,
				SAFE.outer,
				SAFE.inner,
				DISC.hole,
				DISC.stacking,
				DISC.spindle,
			],
			name,
		);
		// the art runs from the 41 mm inner limit to the disc edge and never into the hub
		assert.deepEqual(annulus(svg, 'd-print'), [DISC.edge, DISC.hole], `${name} print area`);
		assert.match(svg, /<g id="d-art" clip-path="url\(#d-print\)">/, name);
	}
});

test('the label is 117 mm with a 41 mm hole and 3 mm of bleed both ways', () => {
	for (const style of STYLES) checkLabel(read(style, 'label.svg'));
});

function checkLabel(svg) {
	assert.match(svg, /width="123mm" height="123mm" viewBox="0 0 123 123"/);
	const radii = Object.fromEntries(guideCircles(svg).map((circle) => [circle.name, circle.r]));
	assert.equal(radii['label cut 117 mm'], LABEL.cut);
	assert.equal(radii['label hole 41 mm'], LABEL.hole);
	assert.equal(radii['bleed outer 123 mm'], LABEL.cut + LABEL.bleed);
	assert.equal(radii['bleed inner 35 mm'], LABEL.hole - LABEL.bleed);
	assert.deepEqual(annulus(svg, 'l-print'), [LABEL.cut + LABEL.bleed, LABEL.hole - LABEL.bleed]);
	assert.equal(LABEL.size / 2, LABEL.cut + LABEL.bleed);
}

test('the disc and label text stays inside the safe ring, clear of the hole and the edge', () => {
	for (const [style, name, centre] of [
		...each(DISCS).map(([style, name]) => [style, name, 60]),
		...STYLES.map((style) => [style, 'label.svg', LABEL.size / 2]),
	]) {
		const lines = texts(read(style, name));
		assert.ok(lines.length >= 8, `${name} has its text`);
		for (const line of lines) {
			for (const [x, y] of line.coordinates) {
				const radius = Math.hypot(x - centre, y - centre);
				assert.ok(
					radius >= SAFE.inner && radius <= SAFE.outer,
					`${name}: "${line.words}" reaches ${radius.toFixed(2)} mm from the centre`,
				);
			}
		}
	}
});

test('no text anywhere is set under 6 pt', () => {
	for (const [style, name] of each(MASTERS)) {
		for (const line of texts(read(style, name))) {
			assert.ok(line.points >= MIN_POINTS, `${name}: "${line.words}" is ${line.points} pt`);
		}
	}
});

test('the disc and label carry the title, the media, the version, the unofficial notice, the credit and the licence', () => {
	const version = readFileSync(join(media, 'gen_media.py'), 'utf8').match(
		/^VERSION = "([^"]+)"/m,
	)[1];
	assert.match(version, /^v\d+\.\d+\.\d+$/);
	for (const [style, name] of each([...DISCS, 'label.svg'])) {
		const words = texts(read(style, name)).map((line) => line.words);
		const all = words.join('\n');
		for (const wanted of [
			'Afterglow',
			'FOR REACTOS™',
			'INSTALL AND LIVE CD',
			'ReactOS 0.4.16 · x86 · 32-bit',
			version,
			'Unofficial remaster. Not endorsed by the ReactOS project.',
			'Copyright © 1996-2026 ReactOS Team & Contributors',
			'GPL-2.0-or-later',
			'Apache-2.0 OR MIT',
			'github.com/liminal-hq-labs/reactos-liminal',
			'Liminal HQ Labs',
		]) {
			assert.ok(all.includes(wanted), `${name} says "${wanted}"`);
		}
		assert.ok(!/ISO/.test(all), `${name} says nothing about an ISO`);
	}
});

test('the jewel case front is 120 mm with 2 mm bleed and its text 3 mm inside the trim', () => {
	for (const style of STYLES) checkFront(read(style, 'jewel-front.svg'));
});

function checkFront(svg) {
	assert.match(svg, /width="124mm" height="124mm" viewBox="0 0 124 124"/);
	assert.match(svg, /<rect x="0" y="0" width="120" height="120" data-guide="trim"\/>/);
	for (const line of texts(svg)) {
		for (const [x, y] of line.coordinates) {
			assert.ok(x >= 3 && x <= 117 && y >= 3 && y <= 117, `"${line.words}" at ${x}, ${y}`);
		}
	}
	const all = texts(svg).map((line) => line.words);
	assert.ok(
		all.includes('Not endorsed by the ReactOS project') ||
			all.some((w) => w.includes('Not endorsed by the ReactOS project')),
	);
}

test('the tray card is 150 x 118 mm with 6 mm spines, the spine text inside its spine and the rest on the back', () => {
	for (const style of STYLES) checkTray(read(style, 'jewel-back.svg'));
});

function checkTray(svg) {
	assert.match(svg, /width="154mm" height="122mm" viewBox="0 0 154 122"/);
	assert.match(svg, /<rect x="0" y="0" width="150" height="118" data-guide="trim"\/>/);
	assert.match(
		svg,
		/<path d="M6 0V118" data-guide="fold"\/><path d="M144 0V118" data-guide="fold"\/>/,
	);
	const lines = texts(svg);
	const spines = lines.filter((line) => line.words.startsWith('Afterglow for ReactOS™  ·'));
	assert.equal(spines.length, 2, 'a title on each spine');
	for (const line of lines) {
		const xs = line.coordinates.map(([x]) => x);
		const ys = line.coordinates.map(([, y]) => y);
		assert.ok(
			Math.min(...ys) >= 3 && Math.max(...ys) <= 115,
			`"${line.words}" stays 3 mm inside the top and bottom`,
		);
		if (spines.includes(line)) {
			const [low, high] = Math.min(...xs) < 75 ? [0.5, 5.5] : [144.5, 149.5];
			assert.ok(
				Math.min(...xs) >= low && Math.max(...xs) <= high,
				`spine text inside its spine (${Math.min(...xs)}-${Math.max(...xs)})`,
			);
		} else {
			assert.ok(
				Math.min(...xs) >= 9 && Math.max(...xs) <= 141,
				`"${line.words}" stays on the back, 3 mm from the folds`,
			);
		}
	}
	const all = lines.map((line) => line.words).join(' ');
	for (const wanted of [
		'WHAT IS ON THIS DISC',
		'Boot menu entry “ReactOS (Afterglow)”',
		'Afterglow desktop',
		'icons and pointers',
		'boot logo and logon banner',
		'The full ReactOS applications and games',
		'afterfetch',
		'Wine Gecko',
		'LICENSES folder',
		'not made, endorsed',
		'ReactOS™ is a trademark of the ReactOS project.',
		'Copyright © 1996-2026 ReactOS Team &',
	]) {
		assert.ok(all.includes(wanted), `the tray card says "${wanted}"`);
	}
}

// The parts of a master that the style may change: the scene groups, and the gradients the smooth ones use
// The scene group always ends where the sun's clipped group begins
const withoutScenes = (svg) =>
	svg
		.replace(/<(linear|radial)Gradient id="[a-z-]*bands[^"]*".*?<\/\1Gradient>/g, '')
		.replace(
			/<g id="[a-z-]*scene" .*?(?=<g clip-path="url\(#[a-z-]*sky\)"><circle [^>]*fill="#ffaa40")/gs,
			'',
		)
		.replace(/^(Afterglow .*|Stepped: .*|Smooth: .*)$/gm, '')
		.replace(/<title>.*<\/title>/, '');

test('the styles differ only in the sky: stepped is flat bands, smooth is gradients, and the rest is the same', () => {
	for (const name of MASTERS) {
		const stepped = read('stepped', name);
		const smooth = read('smooth', name);
		const scenes = [...stepped.matchAll(/<g id="[a-z-]*scene" data-raster="([-\d. ]+)">/g)];
		assert.ok(scenes.length >= 1, `${name} has a scene group`);
		assert.equal(
			[...smooth.matchAll(/<g id="[a-z-]*scene" data-raster="([-\d. ]+)">/g)].length,
			scenes.length,
			`${name} has its scene groups in both styles`,
		);
		assert.ok(
			!/<(linear|radial)Gradient id="[a-z-]*bands/.test(stepped),
			`stepped/${name} has no sky gradient`,
		);
		assert.match(smooth, /<radialGradient id="[a-z-]*bands/, `smooth/${name} has a sky gradient`);
		assert.equal(
			withoutScenes(smooth),
			withoutScenes(stepped),
			`${name}: only the sky changes between the styles`,
		);
	}
});

const haveFonts =
	existsSync('/usr/share/fonts/noto/NotoSans-Light.ttf') ||
	existsSync('/usr/share/fonts/truetype/noto/NotoSans-Light.ttf');
test(
	'the generator writes exactly the committed masters',
	haveFonts ? {} : { skip: 'Noto Sans is not installed' },
	() => {
		const out = mkdtempSync(join(tmpdir(), 'afterglow-cd-media-'));
		try {
			execFileSync('python3', [join(media, 'gen_media.py'), out], { stdio: 'ignore' });
			for (const [style, name] of each(MASTERS)) {
				assert.equal(
					readFileSync(join(out, style, name), 'utf8'),
					read(style, name),
					`${style}/${name} differs from what gen_media.py draws`,
				);
			}
			// --style draws one style only
			const one = mkdtempSync(join(tmpdir(), 'afterglow-cd-media-one-'));
			try {
				execFileSync('python3', [join(media, 'gen_media.py'), one, '--style', 'smooth'], {
					stdio: 'ignore',
				});
				assert.deepEqual(readdirSync(one), ['smooth']);
			} finally {
				rmSync(one, { recursive: true, force: true });
			}
		} finally {
			rmSync(out, { recursive: true, force: true });
		}
	},
);

const haveRsvg = spawnSync('rsvg-convert', ['--version'], { stdio: 'ignore' }).status === 0;
const haveNumpy =
	spawnSync('python3', ['-c', 'import numpy, PIL'], { stdio: 'ignore' }).status === 0;
test(
	'the print render makes every PDF of both styles at its page size, with no guides left in',
	haveRsvg && haveNumpy ? {} : { skip: 'rsvg-convert, numpy or Pillow is not installed' },
	() => {
		const root = mkdtempSync(join(tmpdir(), 'afterglow-cd-media-render-'));
		try {
			execFileSync('python3', [join(media, 'render.py'), root], { stdio: 'ignore' });
			assert.ok(existsSync(join(root, 'stepped-vs-smooth.png')), 'the comparison sheet');
			for (const style of STYLES) checkRender(join(root, style), style);
		} finally {
			rmSync(root, { recursive: true, force: true });
		}
	},
);

function checkRender(out, style) {
	const mm = (value) => (value * 72) / 25.4;
	const expected = {
		'disc-art.pdf': [120, 120],
		'disc-label-single.pdf': [138, 138],
		'disc-label-A4.pdf': [210, 297],
		'disc-label-Letter.pdf': [215.9, 279.4],
		'disc-label-plain-A4.pdf': [210, 297],
		'disc-label-plain-Letter.pdf': [215.9, 279.4],
		'disc-label-single-A4.pdf': [210, 297],
		'disc-label-single-Letter.pdf': [215.9, 279.4],
		'jewel-case-front.pdf': [139, 139],
		'jewel-case-front-A4.pdf': [210, 297],
		'jewel-case-front-Letter.pdf': [215.9, 279.4],
		'jewel-case-back.pdf': [169, 137],
		'jewel-case-back-A4.pdf': [210, 297],
		'jewel-case-back-Letter.pdf': [215.9, 279.4],
	};
	const havePdfinfo = spawnSync('pdfinfo', ['-v'], { stdio: 'ignore' }).status === 0;
	for (const [name, [width, height]] of Object.entries(expected)) {
		// each PDF is converted from the page SVG of the same name, whose size is in mm
		const page = readFileSync(join(out, 'svg', name.replace(/\.pdf$/, '.svg')), 'utf8');
		const size = page.match(/<svg [^>]*width="([\d.]+)mm" height="([\d.]+)mm"/);
		assert.deepEqual([Number(size[1]), Number(size[2])], [width, height], `${name} page`);
		const pdf = readFileSync(join(out, name), 'latin1');
		assert.ok(pdf.startsWith('%PDF-'), `${name} is a PDF`);
		// Stepped is vector throughout. Smooth places each sky as one image under the vector text: one image per label
		// or piece on the page, and the text paths still in the page
		const images = (pdf.match(/\/Subtype\s*\/Image/g) ?? []).length;
		const pieces = (page.match(/<use /g) ?? []).length || 1;
		if (style === 'stepped') assert.equal(images, 0, `${style}/${name} is vector`);
		else assert.equal(images, pieces, `${style}/${name} has one sky image per piece`);
		if (style === 'smooth')
			assert.ok(
				/<image [^>]*href="data:image\/png;base64,/.test(page) &&
					/data-text="Afterglow"/.test(page),
				`${style}/${name} keeps its text as vector paths over the sky image`,
			);
		if (havePdfinfo) {
			const info = execFileSync('pdfinfo', [join(out, name)], { encoding: 'utf8' });
			const [, pointsWide, pointsHigh] = info.match(/Page size:\s+([\d.]+) x ([\d.]+) pts/);
			assert.ok(Math.abs(Number(pointsWide) - mm(width)) < 0.05, `${name} width`);
			assert.ok(Math.abs(Number(pointsHigh) - mm(height)) < 0.05, `${name} height`);
		}
	}
	for (const name of readdirSync(join(out, 'svg'))) {
		const svg = readFileSync(join(out, 'svg', name), 'utf8');
		assert.ok(
			!svg.includes('id="guides"') && !svg.includes(' data-guide="'),
			`${name} has no guides`,
		);
	}
	assert.ok(existsSync(join(out, 'preview.png')));
	assert.ok(existsSync(join(out, 'contact-sheet.png')));
}
