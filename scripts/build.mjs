// Generate the Liminal HQ Afterglow OpenCode themes (afterglow, afterglow-dark, afterglow-light)
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { baseHues, variants } from './hues.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const hue = (variant) => ({
	...baseHues(variant.mode, variant.neutral),
	accent: `$hue.${variant.accent}`,
	interactive: `$hue.${variant.interactive}`,
	neutral: variant.neutral,
});

const h = (name, step) => `$hue.${name}.${step}`;
const states = (base, hovered, focused, pressed, selected, disabled) => ({
	base,
	$hovered: hovered,
	$focused: focused,
	$pressed: pressed,
	$selected: selected,
	$disabled: disabled,
});

const tokens = ({ muted }) => {
	const n = (s) => h('neutral', s);
	const i = (s) => h('interactive', s);
	const a = (s) => h('accent', s);
	const feedback = (hues, mapper) =>
		Object.fromEntries(Object.entries(hues).map(([key, name]) => [key, mapper(name)]));
	const hues = { error: 'red', warning: 'yellow', success: 'green', info: 'cyan' };

	return {
		text: {
			base: n(200),
			muted: n(muted),
			action: {
				primary: states(i(200), i(100), i(100), i(300), i(100), n(500)),
				secondary: states(n(300), n(200), n(200), n(400), n(200), n(500)),
				destructive: states(
					h('red', 200),
					h('red', 100),
					h('red', 100),
					h('red', 300),
					h('red', 100),
					n(500),
				),
			},
			formfield: states(n(200), n(100), i(200), n(300), i(200), n(500)),
			feedback: feedback(hues, (name) => ({ base: h(name, 200), muted: h(name, 400) })),
		},
		background: {
			base: n(900),
			raised: { base: n(800), high: n(700), max: n(600) },
			action: {
				primary: states(i(700), i(600), i(600), i(800), i(600), n(700)),
				secondary: states(n(700), n(600), n(600), n(800), n(600), n(800)),
				destructive: states(
					h('red', 700),
					h('red', 600),
					h('red', 600),
					h('red', 800),
					h('red', 600),
					n(700),
				),
			},
			formfield: states(n(800), n(700), n(700), n(800), n(700), n(800)),
			feedback: feedback(hues, (name) => ({ base: h(name, 800) })),
		},
		border: { base: n(600) },
		scrollbar: { base: n(600) },
		diff: {
			text: {
				added: h('green', 200),
				removed: h('red', 200),
				context: n(400),
				hunkHeader: h('cyan', 200),
			},
			background: { added: h('green', 800), removed: h('red', 800), context: n(800) },
			highlight: { added: h('green', 700), removed: h('red', 700) },
			lineNumber: { text: n(500), background: { added: h('green', 800), removed: h('red', 800) } },
		},
		syntax: {
			comment: n(400),
			keyword: h('purple', 200),
			function: h('orange', 200),
			variable: n(100),
			string: h('green', 200),
			number: h('yellow', 200),
			type: h('cyan', 200),
			operator: n(300),
			punctuation: n(400),
		},
		markdown: {
			text: n(200),
			heading: a(200),
			link: h('blue', 200),
			linkText: h('cyan', 200),
			code: h('green', 200),
			blockQuote: n(300),
			emphasis: h('yellow', 200),
			strong: h('orange', 200),
			horizontalRule: n(500),
			listItem: a(200),
			listEnumeration: h('cyan', 200),
			image: h('blue', 200),
			imageText: h('cyan', 200),
			codeBlock: n(200),
		},
	};
};

// The prompt chips take their background from text.feedback.warning.base and their label from the
// focused primary action text, so on the dark themes the gold is muted and the label is dark. The
// focused action fill is lifted to suit dark text.
const warningChip = {
	text: {
		feedback: { warning: { base: '$hue.yellow.400' } },
		action: { primary: { $focused: '$hue.neutral.900' } },
	},
	background: { action: { primary: { $focused: '$hue.interactive.200' } } },
};

const themes = {
	// The signature theme: the liminalhq.ca void with brand orange and purple, and see-through surfaces
	afterglow: {
		...variants.afterglow,
		muted: 300,
		categorical: ['accent', 'purple', 'cyan', 'green', 'red', 'blue', 'yellow'],
		modeTokens: {
			...warningChip,
			// OpenCode flattens alpha over black rather than blending with the terminal, so the boxes are
			// a solid tone. raised.base must never be transparent: chip labels take this colour.
			background: {
				...warningChip.background,
				base: 'transparent',
				raised: { base: '#181a22', high: '#1f2230', max: '#333847' },
			},
			'@dialog': { background: { base: '#12121af2' } },
		},
	},
	'afterglow-dark': {
		...variants['afterglow-dark'],
		muted: 400,
		categorical: ['accent', 'orange', 'cyan', 'green', 'red', 'blue', 'yellow'],
		modeTokens: warningChip,
	},
	'afterglow-light': {
		...variants['afterglow-light'],
		muted: 400,
		categorical: ['accent', 'orange', 'cyan', 'green', 'red', 'blue', 'yellow'],
		modeTokens: {
			// Warning text must stay deep enough to read on paper, so the chip pairs it with light text instead
			text: { action: { primary: { $focused: '$hue.neutral.900' } } },
			background: { action: { primary: { $focused: '$hue.interactive.300' } } },
		},
	},
};

// Start clean so a renamed or removed theme never lingers in the output
rmSync(join(root, 'themes'), { recursive: true, force: true });
mkdirSync(join(root, 'themes'), { recursive: true });

for (const [name, theme] of Object.entries(themes)) {
	const file = {
		$schema: 'https://opencode.ai/theme.json',
		base: { categorical: theme.categorical, ...tokens(theme) },
		[theme.mode]: {
			hue: hue(theme),
			...theme.modeTokens,
		},
	};
	writeFileSync(join(root, 'themes', `${name}.json`), `${JSON.stringify(file, null, '\t')}\n`);
	console.log(`wrote themes/${name}.json`);
}
