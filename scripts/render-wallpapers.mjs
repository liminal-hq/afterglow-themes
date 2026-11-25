// Render the Afterglow wallpapers to PNG and BMP, dither the smooth ones and draw a contact sheet
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

// Needs rsvg-convert (librsvg) and ImageMagick 7 (`magick`) on the PATH. The renders are large,
// so they go to dist/wallpapers (ignored by git) and are not committed.
//
//   node scripts/render-wallpapers.mjs [--out <dir>] [--only <text>] [--seed <n>] [--no-bmp]

import { spawnSync } from 'node:child_process';
import { mkdirSync, rmSync } from 'node:fs';
import { dirname, join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { HEIGHT, WIDTH, parseId, wallpaperDir, wallpaperIds } from './build-wallpapers.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

// Screen sizes for the PNGs, each rendered from the SVG at that size
export const SIZES = [
	[3840, 2160],
	[2560, 1440],
	[1920, 1080],
];
// ReactOS and other 4:3 desktops: the centre 4:3 crop of the canvas, scaled, as a 24-bit BMP
export const BMP_SIZE = [1024, 768];
export const CROP_4_3 = { x: (WIDTH - (HEIGHT * 4) / 3) / 2, width: (HEIGHT * 4) / 3 };
// Triangular dither added after rendering to the smooth wallpapers, in 8-bit levels either way.
// A smooth dark gradient bands visibly even at 24 bits; one level of noise hides the steps
// without showing as grain. Each size is dithered on its own, because scaling a dithered image
// averages the noise away and brings the bands back.
export const DITHER = 1;

const args = process.argv.slice(2);
const option = (name, fallback) => {
	const i = args.indexOf(name);
	return i === -1 ? fallback : args[i + 1];
};
const out = join(root, option('--out', join('dist', 'wallpapers')));
const only = option('--only', '');
const seed = Number(option('--seed', 2026));
const bmp = !args.includes('--no-bmp');

const run = (command, commandArgs, input) => {
	const result = spawnSync(command, commandArgs, { input, maxBuffer: 1 << 30 });
	if (result.error) throw new Error(`${command}: ${result.error.message}`);
	if (result.status !== 0) throw new Error(`${command} failed: ${result.stderr.toString()}`);
	return result.stdout;
};

// A small seeded generator, so a render is the same every time
const mulberry32 = (a) => () => {
	a = (a + 0x6d2b79f5) | 0;
	let t = Math.imul(a ^ (a >>> 15), 1 | a);
	t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
	return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
};
const hash = (text) =>
	[...text].reduce((h, ch) => Math.imul(h ^ ch.charCodeAt(0), 16777619), 2166136261);

// Add triangular noise (the sum of two uniform draws) of +-`amount` levels to raw RGB bytes
export const dither = (rgb, amount, key) => {
	const random = mulberry32(hash(key) ^ seed);
	const outBytes = Buffer.alloc(rgb.length);
	for (let i = 0; i < rgb.length; i++) {
		const v = rgb[i] + (random() + random() - 1) * amount;
		outBytes[i] = Math.min(255, Math.max(0, Math.round(v)));
	}
	return outBytes;
};

// Raw RGB of an image file, after optional ImageMagick operations
const rawRgb = (file, ops = []) =>
	run('magick', [file, ...ops, '-alpha', 'off', '-depth', '8', 'rgb:-']);
const writeRaw = (rgb, [w, h], target, format = 'png') =>
	run(
		'magick',
		['-size', `${w}x${h}`, '-depth', '8', 'rgb:-', '-type', 'TrueColor', `${format}:${target}`],
		rgb,
	);

const say = (file) => console.log(`wrote ${relative(root, file)}`);

const renderOne = (id) => {
	const svg = join(wallpaperDir, `${id}.svg`);
	const smooth = parseId(id).style === 'smooth';
	mkdirSync(join(out, 'png'), { recursive: true });
	let full;
	for (const [w, h] of SIZES) {
		const target = join(out, 'png', `${id}-${w}x${h}.png`);
		const plain = smooth ? join(out, 'png', `${id}-${w}x${h}-nodither.png`) : target;
		run('rsvg-convert', ['-w', String(w), '-h', String(h), '-o', plain, svg]);
		if (w === WIDTH) full = plain;
		if (smooth) writeRaw(dither(rawRgb(plain), DITHER, `${id}-${w}`), [w, h], target);
		say(target);
		// Keep the undithered copy only at full size, for anyone who dithers on their own
		if (smooth && w === WIDTH) say(plain);
		else if (smooth) rmSync(plain);
	}
	if (bmp) {
		mkdirSync(join(out, 'bmp'), { recursive: true });
		const target = join(out, 'bmp', `${id}-${BMP_SIZE[0]}x${BMP_SIZE[1]}.bmp`);
		const scaled = rawRgb(full, [
			'-crop',
			`${CROP_4_3.width}x${HEIGHT}+${CROP_4_3.x}+0`,
			'+repage',
			'-filter',
			'Lanczos',
			'-resize',
			`${BMP_SIZE[0]}x${BMP_SIZE[1]}!`,
		]);
		writeRaw(smooth ? dither(scaled, DITHER, `${id}-bmp`) : scaled, BMP_SIZE, target, 'BMP3');
		say(target);
	}
};

const ids = wallpaperIds().filter((id) => id.includes(only));
for (const id of ids) renderOne(id);

// Every variant at a glance, stepped beside smooth, from the 1920 renders
if (ids.length > 1) {
	const sheet = join(out, 'contact-sheet.png');
	run('magick', [
		'montage',
		...ids.flatMap((id) => [
			'-label',
			id.replace('afterglow-', ''),
			join(out, 'png', `${id}-1920x1080.png`),
		]),
		'-tile',
		'4x',
		'-geometry',
		'640x360+12+12',
		'-background',
		'#12121a',
		'-fill',
		'#e0e0e0',
		'-pointsize',
		'22',
		sheet,
	]);
	say(sheet);

	// Stepped and smooth side by side at 100%, cropped around the sun where the bands are closest
	const pairs = ids.filter((id) => id.endsWith('-stepped'));
	const compare = join(out, 'compare-stepped-smooth.png');
	run('magick', [
		'montage',
		...pairs.flatMap((id) =>
			['stepped', 'smooth'].flatMap((style) => {
				const name = id.replace('-stepped', `-${style}`);
				return [
					'-label',
					name.replace('afterglow-', ''),
					`${join(out, 'png', `${name}-1920x1080.png`)}[640x360+1120+600]`,
				];
			}),
		),
		'-tile',
		'4x',
		'-geometry',
		'+12+12',
		'-background',
		'#12121a',
		'-fill',
		'#e0e0e0',
		'-pointsize',
		'22',
		compare,
	]);
	say(compare);
}
