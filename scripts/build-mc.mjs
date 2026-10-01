// Generate the Afterglow Midnight Commander skins (truecolour and 256-colour) from the shared palette
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { contrast, toHex, toRgb } from './colour.mjs';
import { resolvedHues, variants } from './hues.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

export const mcVariants = {
	afterglow: {
		label: 'Afterglow',
		blurb: 'the signature void, with the terminal background showing through',
	},
	'afterglow-dark': { label: 'Afterglow Dark', blurb: 'solid indigo-black with a purple accent' },
	'afterglow-light': { label: 'Afterglow Light', blurb: 'warm paper with a purple accent' },
};

// Each variant ships as a truecolour skin and as a 256-colour fallback
export const flavours = {
	truecolor: { suffix: '', key: 'truecolors', label: 'truecolour' },
	256: { suffix: '-256', key: '256colors', label: '256-colour' },
};

export const skinFile = (id, flavour) => `${id}${flavours[flavour].suffix}.ini`;

// The colour of the terminal's own background, which mc cannot read. Contrast for `default` is
// measured against the variant's neutral 900 surface, the colour a terminal should be set to.
export const DEFAULT = 'default';

// The xterm 256-colour palette as mc sees it: 16 to 231 are the 6x6x6 cube and 232 to 255 the
// greyscale ramp. Indices 0 to 15 are left alone because every terminal themes them differently.
const cubeLevels = [0, 95, 135, 175, 215, 255];
export const xtermHex = (index) => {
	if (index >= 232) {
		const level = 8 + (index - 232) * 10;
		return toHex([level, level, level]);
	}
	const n = index - 16;
	return toHex([
		cubeLevels[Math.floor(n / 36)],
		cubeLevels[Math.floor(n / 6) % 6],
		cubeLevels[n % 6],
	]);
};
const palette256 = Array.from({ length: 240 }, (_, i) => [i + 16, xtermHex(i + 16)]);

// Redmean weighted distance, a cheap approximation of perceived colour difference
const distance = (a, b) => {
	const [ar, ag, ab] = toRgb(a);
	const [br, bg, bb] = toRgb(b);
	const r = (ar + br) / 2;
	const [dr, dg, db] = [ar - br, ag - bg, ab - bb];
	return (2 + r / 256) * dr * dr + 4 * dg * dg + (2 + (255 - r) / 256) * db * db;
};

// The nearest 256-colour index to a hex colour. When `against` and `min` are given, only colours
// that keep `min`:1 contrast with `against` are considered, so rounding never costs legibility.
export const nearest256 = (hex, against, min = 0, exclude = new Set()) => {
	const candidates = palette256
		.filter(([index]) => !exclude.has(index))
		.filter(([, candidate]) => !against || min === 0 || contrast(candidate, against) >= min)
		.sort((a, b) => distance(hex, a[1]) - distance(hex, b[1]));
	const [best] = candidates.length
		? candidates
		: [...palette256].sort((a, b) => distance(hex, a[1]) - distance(hex, b[1]));
	return best[0];
};

const entry = (fg, bg, attrs = '', min = 4.5) => ({ fg, bg, attrs, min });

// Every colour pair mc draws, by section and key. Roles match the other Afterglow themes: purple for
// keywords and accents, rose for errors, orange for headers and functions, green for success,
// yellow for numbers and warnings, cyan for types and information, and blue for links and constants.
// Step meanings match too: neutral 900 is the background, 800 to 600 are raised surfaces and
// borders, 200 is body text, 400 is muted text, and a hue's step 200 is its main colour.
// `min` is the contrast a pair must hold: 4.5 for text, 3 for deliberately dim elements, 0 to skip.
export const buildSkinModel = (id) => {
	const variant = variants[id];
	const H = resolvedHues(variant);
	const N = variant.neutral;
	const dark = variant.mode === 'dark';
	const A = H.accent;
	const I = H.interactive;
	const base = id === 'afterglow' ? DEFAULT : N[900];
	const baseSurface = N[900];
	// Light-mode hues are deeper at step 100, which is what holds 4.5:1 on the tinted raised surfaces
	const raised = (hue) => (dark ? hue[200] : hue[100]);

	const core = {
		_default_: entry(N[200], base),
		selected: entry(N[100], I[600]),
		marked: entry(H.yellow[200], base, 'bold'),
		markselect: entry(H.yellow[100], I[600], 'bold'),
		gauge: entry(N[900], A[200]),
		input: entry(N[100], N[900]),
		inputunchanged: entry(N[300], N[900]),
		inputmark: entry(N[100], I[600]),
		disabled: entry(N[400], N[700], '', 3),
		reverse: entry(N[900], N[300]),
		commandlinemark: entry(N[100], I[600]),
		header: entry(H.orange[200], base, 'bold'),
		inputhistory: entry(N[300], N[900]),
		commandhistory: entry(N[400], base, '', 3),
		shadow: entry(N[500], dark ? N[900] : N[600], '', 0),
	};

	const file = (fg, attrs = '') => entry(fg, base, attrs);
	const filehighlight = {
		directory: file(H.blue[200], 'bold'),
		executable: file(H.green[200], 'bold'),
		symlink: file(H.cyan[200]),
		hardlink: file(H.cyan[100]),
		stalelink: file(H.red[200]),
		device: file(H.yellow[200]),
		special: file(H.yellow[100]),
		core: file(H.red[100]),
		temp: entry(N[400], base, '', 3),
		archive: file(H.orange[200]),
		doc: file(N[300]),
		source: file(H.purple[200]),
		media: file(H.purple[100]),
		graph: file(H.blue[100]),
		database: file(H.orange[100]),
	};

	const dialog = {
		_default_: entry(N[200], N[700]),
		dfocus: entry(N[100], I[600]),
		dhotnormal: entry(A[200], N[700]),
		dhotfocus: entry(A[100], I[600]),
		dtitle: entry(raised(H.orange), N[700], 'bold'),
	};

	// Dark mode needs stronger reds to stand apart from the dialog surface, light mode paler ones to keep contrast
	const errorBg = dark ? H.red[600] : H.red[700];
	const errorFocus = dark ? H.red[400] : H.red[600];
	const error = {
		_default_: entry(N[100], errorBg),
		errdfocus: entry(N[100], errorFocus),
		errdhotnormal: entry(raised(H.yellow), errorBg),
		errdhotfocus: entry(H.yellow[100], errorFocus),
		errdtitle: entry(H.yellow[100], errorBg, 'bold'),
	};

	const menu = {
		_default_: entry(N[200], N[700]),
		menusel: entry(N[100], I[600]),
		menuhot: entry(A[200], N[700]),
		menuhotsel: entry(A[100], I[600]),
		menuinactive: entry(N[300], N[800]),
	};

	const popupmenu = {
		_default_: entry(N[200], N[700]),
		menusel: entry(N[100], I[600]),
		menutitle: entry(raised(H.orange), N[700], 'bold'),
	};

	const buttonbar = {
		hotkey: entry(N[100], A[700]),
		button: entry(N[200], N[800]),
	};

	const statusbar = { _default_: entry(N[200], N[800]) };

	const help = {
		_default_: entry(N[200], N[800]),
		helpitalic: entry(H.cyan[200], N[800], 'italic'),
		helpbold: entry(raised(H.orange), N[800], 'bold'),
		helplink: entry(H.blue[200], N[800]),
		helpslink: entry(N[100], I[600]),
		helptitle: entry(H.purple[200], N[800], 'bold'),
	};

	const editor = {
		_default_: entry(N[200], base),
		editbold: entry(H.orange[200], base, 'bold'),
		editmarked: entry(N[100], I[600]),
		editwhitespace: entry(N[500], base, '', 3),
		editlinestate: entry(N[300], N[800]),
		bookmark: entry(N[900], H.yellow[200]),
		bookmarkfound: entry(N[900], H.green[200]),
		editrightmargin: entry(N[300], N[800]),
		editframeactive: entry(A[200], base),
		editframedrag: entry(H.green[200], base),
		editframe: entry(N[400], base),
		editbg: entry(N[200], base),
	};

	const viewer = {
		_default_: entry(N[200], base),
		viewbold: entry(H.orange[200], base, 'bold'),
		viewunderline: entry(H.cyan[200], base, 'underline'),
		viewselected: entry(N[900], A[200]),
	};

	const diffviewer = {
		added: entry(N[100], H.green[700]),
		changedline: entry(N[100], H.blue[700]),
		changednew: entry(N[100], H.yellow[600]),
		changed: entry(N[100], H.blue[600]),
		removed: entry(N[100], H.red[700]),
		error: entry(N[100], H.red[800]),
		_default_: entry(N[200], base),
	};

	return {
		baseSurface,
		sections: {
			core,
			dialog,
			error,
			filehighlight,
			menu,
			popupmenu,
			buttonbar,
			statusbar,
			help,
			editor,
			viewer,
			diffviewer,
		},
	};
};

// Glyphs and box-drawing characters are the same in every skin
const fixed = {
	Lines: {
		horiz: '─',
		vert: '│',
		lefttop: '┌',
		righttop: '┐',
		leftbottom: '└',
		rightbottom: '┘',
		topmiddle: '┬',
		bottommiddle: '┴',
		leftmiddle: '├',
		rightmiddle: '┤',
		cross: '┼',
		dhoriz: '═',
		dvert: '║',
		dlefttop: '╔',
		drighttop: '╗',
		dleftbottom: '╚',
		drightbottom: '╝',
		dtopmiddle: '╤',
		dbottommiddle: '╧',
		dleftmiddle: '╟',
		drightmiddle: '╢',
	},
	'widget-panel': {
		'sort-up-char': '▴',
		'sort-down-char': '▾',
		'hiddenfiles-show-char': '•',
		'hiddenfiles-hide-char': '○',
		'history-prev-item-char': '◂',
		'history-next-item-char': '▸',
		'history-show-list-char': '▾',
		'filename-scroll-left-char': '◂',
		'filename-scroll-right-char': '▸',
		'hiddenfiles-sign-show': '•',
		'hiddenfiles-sign-hide': '○',
		'history-prev-item-sign': '◂',
		'history-next-item-sign': '▸',
		'history-show-list-sign': '▾',
	},
	'widget-scrollbar': {
		'first-vert-char': '▴',
		'last-vert-char': '▾',
		'first-horiz-char': '◂',
		'last-horiz-char': '▸',
		'current-char': '■',
		'background-char': '▒',
	},
	'widget-editor': { 'window-state-char': '↕', 'window-close-char': '✕' },
	'widget-common': { 'sort-sign-up': '↑', 'sort-sign-down': '↓' },
};

// Resolve a model entry to concrete colours for a flavour. In the 256-colour flavour every colour is
// rounded to the palette, and a foreground may shift to the nearest colour that still meets its
// contrast so the fallback stays as legible as the truecolour skin.
export const resolveEntry = (model, item, flavour, exclude) => {
	const surface = item.bg === DEFAULT ? model.baseSurface : item.bg;
	if (flavour === 'truecolor') return { fg: item.fg, bg: item.bg };
	const bgIndex = nearest256(surface);
	const fgIndex = nearest256(item.fg, xtermHex(bgIndex), item.min, exclude);
	return { fg: `color${fgIndex}`, bg: item.bg === DEFAULT ? DEFAULT : `color${bgIndex}` };
};

export const buildSkin = (id, flavour) => {
	const meta = mcVariants[id];
	const model = buildSkinModel(id);
	const lines = [
		`# ${meta.label} for Midnight Commander (${flavours[flavour].label}): ${meta.blurb}.`,
		'# Generated from the Afterglow palette by scripts/build-mc.mjs. Edit the generator, not this file.',
	];
	if (flavour === 'truecolor') {
		lines.push(
			'# Needs mc 4.8.19 or newer built against S-Lang 2.3.1 or newer on a 64-bit system, and a terminal with COLORTERM=truecolor (or 24bit).',
			`# Without that, use ${id}-256 instead.`,
		);
	} else {
		lines.push('# For terminals that report 256 colours (TERM=xterm-256color) but not truecolour.');
	}
	if (id === 'afterglow') {
		lines.push(
			'# The main panels, viewer and editor use the terminal default background so transparency shows through.',
		);
	}
	lines.push(
		'',
		'[skin]',
		`    description = ${meta.label}${flavour === '256' ? ' (256 colours)' : ''}`,
		`    ${flavours[flavour].key} = true`,
	);

	const section = (name, body) => {
		lines.push('', `[${name}]`);
		for (const [key, value] of Object.entries(body)) lines.push(`    ${key} = ${value}`);
	};

	// File types must stay distinguishable, so in the 256 flavour no two share a foreground
	const rendered = (items, distinct = false) => {
		const used = new Set();
		return Object.fromEntries(
			Object.entries(items).map(([key, item]) => {
				const { fg, bg } = resolveEntry(model, item, flavour, distinct ? used : undefined);
				if (distinct) used.add(Number(fg.replace('color', '')));
				return [key, [fg, bg, item.attrs].filter((part, i) => i < 2 || part).join(';')];
			}),
		);
	};

	section('Lines', fixed.Lines);
	for (const [name, items] of Object.entries(model.sections)) {
		section(name, rendered(items, flavour === '256' && name === 'filehighlight'));
	}
	for (const name of ['widget-panel', 'widget-scrollbar', 'widget-editor', 'widget-common']) {
		section(name, fixed[name]);
	}
	return `${lines.join('\n')}\n`;
};

if (process.argv[1] === fileURLToPath(import.meta.url)) {
	// Start clean so a renamed or removed skin never lingers in the output
	rmSync(join(root, 'mc', 'skins'), { recursive: true, force: true });
	mkdirSync(join(root, 'mc', 'skins'), { recursive: true });

	for (const id of Object.keys(mcVariants)) {
		for (const flavour of Object.keys(flavours)) {
			const file = skinFile(id, flavour);
			writeFileSync(join(root, 'mc', 'skins', file), buildSkin(id, flavour));
			console.log(`wrote mc/skins/${file}`);
		}
	}
}
