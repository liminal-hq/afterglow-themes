// Generate the Afterglow Claude Code custom themes from the shared palette
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { mix } from './colour.mjs';
import { resolvedHues, variants } from './hues.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

// Every colour token Claude Code defines for its built-in presets, extracted from the binary
export const claudeTokens = JSON.parse(
	readFileSync(join(root, 'scripts', 'claude-theme-tokens.json'), 'utf8'),
);

// `name` is the label /theme shows and the file name is the slug, so /theme stores `custom:<file>`
export const claudeVariants = {
	afterglow: { label: 'Afterglow', file: 'afterglow.json' },
	'afterglow-dark': { label: 'Afterglow Dark', file: 'afterglow-dark.json' },
	'afterglow-light': { label: 'Afterglow Light', file: 'afterglow-light.json' },
};

// The built-in preset a variant starts from. A theme sets every token, so the base only decides
// what Claude Code assumes about the terminal (light or dark) for things a theme cannot recolour.
export const baseFor = (variant) => (variant.mode === 'dark' ? 'dark' : 'light');

// Claude Code has no background token: it draws on the terminal's own background. Contrast is
// measured against the variant's neutral 900 surface, which is the colour the terminal should be.
export const surfaceFor = (id) => variants[id].neutral[900];

// The lighter colour a spinner animates towards. Dark ramps get lighter at step 100, but light
// ramps get darker, so a light theme mixes the main colour towards the paper instead.
const shimmerOf = (hue, variant) =>
	variant.mode === 'dark' ? hue[100] : mix(hue[200], variant.neutral[900], 0.25);

// Roles match the other Afterglow themes: purple for keywords and skills, rose for errors, orange
// for the brand and functions, green for success, yellow for warnings, cyan for information and
// blue for links. Step meanings match too: neutral 900 is the surface, 200 is body text, 400 is
// muted text, and a hue's step 200 is its main colour.
export const buildClaudeOverrides = (id) => {
	const variant = variants[id];
	const H = resolvedHues(variant);
	const N = variant.neutral;
	const dark = variant.mode === 'dark';
	const A = H.accent;
	const I = H.interactive;
	const shimmer = (hue) => shimmerOf(hue, variant);

	// There is no pink hue in the palette, so the subagent pink and the rainbow's indigo are blends
	const pink = mix(H.red[200], H.purple[200], 0.45);
	const indigo = mix(H.blue[200], H.purple[200], 0.5);
	const rainbow = {
		red: H.red,
		orange: H.orange,
		yellow: H.yellow,
		green: H.green,
		blue: H.blue,
		indigo: { 100: mix(H.blue[100], H.purple[100], 0.5), 200: indigo },
		violet: H.purple,
	};

	const overrides = {
		// Mode accents and the brand colour
		autoAccept: H.purple[200],
		autoAcceptShimmer: shimmer(H.purple),
		skill: H.purple[200],
		bashBorder: H.red[200],
		claude: A[200],
		claudeShimmer: shimmer(A),
		claudeBlue_FOR_SYSTEM_SPINNER: H.blue[200],
		claudeBlueShimmer_FOR_SYSTEM_SPINNER: shimmer(H.blue),
		permission: I[200],
		permissionShimmer: shimmer(I),
		planMode: H.cyan[200],
		ide: H.blue[200],
		// The input border is the one border read all day, so it sits a step above the 600 borders
		promptBorder: dark ? N[500] : N[400],
		promptBorderShimmer: dark ? N[400] : N[500],

		// Text
		text: N[200],
		inverseText: N[900],
		inactive: N[400],
		inactiveShimmer: dark ? N[300] : mix(N[400], N[900], 0.25),
		subtle: N[500],
		suggestion: I[200],
		remember: H.blue[200],
		background: H.cyan[200],

		// Status
		success: H.green[200],
		error: H.red[200],
		warning: H.yellow[200],
		merged: H.purple[200],
		warningShimmer: shimmer(H.yellow),

		// Diffs: the line backgrounds are faint tints and the word highlights are stronger ones
		diffAdded: H.green[700],
		diffRemoved: H.red[700],
		diffAddedDimmed: H.green[800],
		diffRemovedDimmed: H.red[800],
		diffAddedWord: H.green[500],
		diffRemovedWord: H.red[500],

		// Subagents, brand marks and the mascot
		red_FOR_SUBAGENTS_ONLY: H.red[200],
		blue_FOR_SUBAGENTS_ONLY: H.blue[200],
		green_FOR_SUBAGENTS_ONLY: H.green[200],
		yellow_FOR_SUBAGENTS_ONLY: H.yellow[200],
		purple_FOR_SUBAGENTS_ONLY: H.purple[200],
		orange_FOR_SUBAGENTS_ONLY: H.orange[200],
		pink_FOR_SUBAGENTS_ONLY: pink,
		cyan_FOR_SUBAGENTS_ONLY: H.cyan[200],
		professionalBlue: H.blue[200],
		chromeYellow: H.yellow[200],
		clawd_body: A[200],
		clawd_background: N[900],

		// Transcript surfaces. Muted text still has to hold 4.5:1 on the message and its hover state.
		userMessageBackground: N[800],
		userMessageBackgroundHover: mix(N[800], N[700], 0.4),
		composerSidebarBackground: N[800],
		selectionBg: I[600],
		bashMessageBackgroundColor: H.orange[700],
		memoryBackgroundColor: H.cyan[700],

		// Usage meter, fast mode, effort and speaker labels
		rate_limit_fill: I[200],
		rate_limit_empty: N[500],
		fastMode: H.orange[200],
		fastModeShimmer: shimmer(H.orange),
		effortUltra: H.purple[200],
		briefLabelYou: H.blue[200],
		briefLabelClaude: A[200],
	};

	for (const [colour, hue] of Object.entries(rainbow)) {
		overrides[`rainbow_${colour}`] = hue[200];
		overrides[`rainbow_${colour}_shimmer`] = shimmer(hue);
	}

	// Keep the key order of Claude Code's own presets so the files read like the built-in ones
	return Object.fromEntries(claudeTokens.map((token) => [token, overrides[token]]));
};

export const buildClaudeTheme = (id) => ({
	name: claudeVariants[id].label,
	base: baseFor(variants[id]),
	overrides: buildClaudeOverrides(id),
});

if (process.argv[1] === fileURLToPath(import.meta.url)) {
	// Start clean so a renamed or removed theme never lingers in the output
	rmSync(join(root, 'claude', 'themes'), { recursive: true, force: true });
	mkdirSync(join(root, 'claude', 'themes'), { recursive: true });

	for (const [id, meta] of Object.entries(claudeVariants)) {
		writeFileSync(
			join(root, 'claude', 'themes', meta.file),
			`${JSON.stringify(buildClaudeTheme(id), null, '\t')}\n`,
		);
		console.log(`wrote claude/themes/${meta.file}`);
	}
}
