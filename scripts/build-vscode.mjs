// Generate the Afterglow VS Code colour themes from the shared palette and the Dark+ / Light+ scopes
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { resolvedHues, variants } from './hues.mjs';
import { parseJsonc } from './jsonc.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const upstream = (file) => parseJsonc(readFileSync(join(root, 'vscode', 'upstream', file), 'utf8'));

export const vscodeVariants = {
	afterglow: { label: 'Afterglow', uiTheme: 'vs-dark', file: 'afterglow-color-theme.json' },
	'afterglow-dark': {
		label: 'Afterglow Dark',
		uiTheme: 'vs-dark',
		file: 'afterglow-dark-color-theme.json',
	},
	'afterglow-light': {
		label: 'Afterglow Light',
		uiTheme: 'vs',
		file: 'afterglow-light-color-theme.json',
	},
};

// Syntax roles. Each role is the same hue in every variant, so code reads the same across themes,
// and matches the syntax colours in the OpenCode themes.
export const syntaxRoles = (H, N) => ({
	text: N[200],
	comment: N[400],
	punctuation: N[400],
	label: N[300],
	keyword: H.purple[200],
	control: H.red[200],
	tag: H.red[200],
	function: H.orange[200],
	attribute: H.orange[200],
	heading: H.orange[200],
	string: H.green[200],
	number: H.yellow[200],
	cssClass: H.yellow[200],
	type: H.cyan[200],
	constant: H.blue[200],
	variable: H.blue[100],
	header: H.blue[200],
	regexp: H.red[200],
	regexpGroup: H.purple[200],
	invalid: H.red[200],
});

// Dark+ and Light+ colour each role with a different literal, so map both sets of literals to roles.
const darkRoles = {
	'#d4d4d4': 'text',
	'#6a9955': 'comment',
	'#569cd6': 'keyword',
	'#c586c0': 'control',
	'#b5cea8': 'number',
	'#ce9178': 'string',
	'#dcdcaa': 'function',
	'#4ec9b0': 'type',
	'#4fc1ff': 'constant',
	'#9cdcfe': 'variable',
	'#d7ba7d': 'cssClass',
	'#d16969': 'regexp',
	'#646695': 'regexpGroup',
	'#f44747': 'invalid',
	'#808080': 'punctuation',
	'#c8c8c8': 'label',
	'#000080': 'header',
	'#6796e6': 'header',
};

const lightRoles = {
	'#000000': 'text',
	'#000000ff': 'text',
	'#008000': 'comment',
	'#0000ff': 'keyword',
	'#af00db': 'control',
	'#098658': 'number',
	'#a31515': 'string',
	'#795e26': 'function',
	'#267f99': 'type',
	'#0070c1': 'constant',
	'#001080': 'variable',
	'#0451a5': 'variable',
	'#800000': 'tag',
	'#e50000': 'variable',
	'#800080': 'control',
	'#811f3f': 'regexpGroup',
	'#d16969': 'regexp',
	'#ee0000': 'cssClass',
	'#cd3131': 'invalid',
	'#000080': 'header',
};

// Dark+ and Light+ disagree about a few things (tag names are blue in one and maroon in the other).
// These rules pin the role by scope so every Afterglow variant treats them the same way.
const scopeRoles = [
	[['entity.name.tag'], 'tag'],
	[['entity.name.tag.css', 'entity.name.tag.less'], 'cssClass'],
	[['entity.name.selector'], 'cssClass'],
	[['entity.other.attribute-name'], 'attribute'],
	[['entity.other.attribute-name.class.css'], 'cssClass'],
	[['punctuation.definition.tag'], 'punctuation'],
	[['markup.heading'], 'heading'],
	[['markup.bold'], 'heading'],
	[['markup.inline.raw'], 'string'],
	[['support.type.vendored.property-name', 'support.type.property-name'], 'variable'],
	[['meta.diff.header', 'meta.preprocessor', 'entity.name.function.preprocessor'], 'keyword'],
	[['punctuation.section.embedded.begin.php', 'punctuation.section.embedded.end.php'], 'keyword'],
	[['punctuation.definition.template-expression.begin'], 'keyword'],
	[['markup.changed'], 'constant'],
	[['constant.character', 'constant.other.option'], 'keyword'],
	[['constant.character.escape'], 'cssClass'],
	[['keyword.operator.quantifier.regexp'], 'cssClass'],
];

// Scopes that scopeRoles pins. A rule is pinned by its first scope, and the whole rule takes that
// role, so a pinned scope must lead its rule and a rule must never mix scopes pinned to different
// roles. Either would otherwise recolour or skip scopes silently when the upstream files change.
export const roleForRule = (rule, literals) => {
	const foreground = rule.settings?.foreground;
	if (foreground === undefined) return undefined;

	const scopes = [].concat(rule.scope ?? []);
	const pinned = scopes.map((scope) => scopeRoles.find(([names]) => names.includes(scope))?.[1]);
	const roles = new Set(pinned.filter(Boolean));
	if (roles.size > 1) {
		throw new Error(`Rule mixes scopes pinned to different roles: ${scopes.join(', ')}`);
	}
	if (roles.size === 1) {
		if (!pinned[0]) {
			throw new Error(`A pinned scope is not the first scope of its rule: ${scopes.join(', ')}`);
		}
		return pinned[0];
	}

	const role = literals[foreground.toLowerCase()];
	if (!role)
		throw new Error(`No Afterglow role for ${foreground} (scope: ${scopes[0] ?? rule.name})`);
	return role;
};

const recolour = (rules, literals, roles) =>
	rules.map((rule) => {
		const role = roleForRule(rule, literals);
		if (role === undefined) return rule;
		return { ...rule, settings: { ...rule.settings, foreground: roles[role] } };
	});

const semanticTokens = (tokens, literals, roles) =>
	Object.fromEntries(
		Object.entries(tokens).map(([name, colour]) => {
			const role = literals[colour.toLowerCase()];
			if (!role) throw new Error(`No Afterglow role for semantic token ${name} (${colour})`);
			return [name, roles[role]];
		}),
	);

const alpha = (hex, value) => `${hex}${value}`;
const CLEAR = '#00000000';

// The workbench colours: every surface, border and state in the editor chrome. Step meanings match
// the OpenCode themes: neutral 900 is the background, 800 to 600 are raised surfaces and borders,
// and hue step 200 is the main colour of a hue.
const workbench = (variant) => {
	const H = resolvedHues(variant);
	const N = variant.neutral;
	const dark = variant.mode === 'dark';
	const A = H.accent;
	const I = H.interactive;
	const shadow = dark ? '#00000080' : '#00000026';

	const bracket = [
		H.yellow[200],
		H.purple[200],
		H.cyan[200],
		H.orange[200],
		H.green[200],
		H.red[200],
	];
	const ansi = {
		black: dark ? N[600] : N[100],
		red: H.red[200],
		green: H.green[200],
		yellow: H.yellow[200],
		blue: H.blue[200],
		magenta: H.purple[200],
		cyan: H.cyan[200],
		white: dark ? N[300] : N[400],
		brightBlack: dark ? N[500] : N[400],
		brightRed: H.red[100],
		brightGreen: H.green[100],
		brightYellow: H.yellow[100],
		brightBlue: H.blue[100],
		brightMagenta: H.purple[100],
		brightCyan: H.cyan[100],
		brightWhite: dark ? N[100] : N[300],
	};

	const colors = {
		// Global
		focusBorder: A[200],
		foreground: N[200],
		disabledForeground: N[500],
		descriptionForeground: N[400],
		errorForeground: H.red[200],
		'icon.foreground': N[300],
		'widget.shadow': shadow,
		'widget.border': N[600],
		'selection.background': alpha(I[200], '59'),
		'sash.hoverBorder': A[200],
		'toolbar.hoverBackground': N[700],
		'toolbar.activeBackground': N[600],
		'textLink.foreground': H.blue[200],
		'textLink.activeForeground': H.blue[100],
		'textPreformat.foreground': H.green[100],
		'textBlockQuote.background': N[800],
		'textBlockQuote.border': alpha(A[200], '80'),
		'textCodeBlock.background': N[800],
		'textSeparator.foreground': N[600],

		// Buttons, inputs, dropdowns, badges
		'button.background': I[600],
		'button.foreground': N[100],
		'button.hoverBackground': I[500],
		'button.secondaryBackground': N[700],
		'button.secondaryForeground': N[100],
		'button.secondaryHoverBackground': N[600],
		'button.border': alpha(I[200], '4d'),
		'checkbox.background': N[800],
		'checkbox.foreground': N[100],
		'checkbox.border': N[500],
		'dropdown.background': N[800],
		'dropdown.foreground': N[200],
		'dropdown.border': N[600],
		'input.background': N[800],
		'input.foreground': N[200],
		'input.border': N[600],
		'input.placeholderForeground': N[400],
		'inputOption.activeBackground': alpha(A[200], '33'),
		'inputOption.activeBorder': A[200],
		'inputOption.activeForeground': N[100],
		'inputValidation.errorBackground': H.red[800],
		'inputValidation.errorBorder': H.red[300],
		'inputValidation.warningBackground': H.yellow[800],
		'inputValidation.warningBorder': H.yellow[300],
		'inputValidation.infoBackground': H.cyan[800],
		'inputValidation.infoBorder': H.cyan[300],
		'badge.background': A[200],
		'badge.foreground': N[900],
		'progressBar.background': A[200],
		'keybindingLabel.background': N[700],
		'keybindingLabel.foreground': N[200],
		'keybindingLabel.border': N[600],
		'keybindingLabel.bottomBorder': N[500],

		// Scrollbars and minimap
		'scrollbar.shadow': CLEAR,
		'scrollbarSlider.background': alpha(N[500], '66'),
		'scrollbarSlider.hoverBackground': alpha(N[400], '80'),
		'scrollbarSlider.activeBackground': alpha(N[300], '99'),
		'minimap.findMatchHighlight': A[200],
		'minimap.selectionHighlight': I[200],
		'minimap.errorHighlight': H.red[200],
		'minimap.warningHighlight': H.yellow[200],
		'minimapSlider.background': alpha(N[500], '33'),
		'minimapSlider.hoverBackground': alpha(N[400], '40'),
		'minimapSlider.activeBackground': alpha(N[300], '4d'),
		'minimapGutter.addedBackground': H.green[200],
		'minimapGutter.modifiedBackground': H.blue[200],
		'minimapGutter.deletedBackground': H.red[200],

		// Editor
		'editor.background': N[900],
		'editor.foreground': N[200],
		'editorLineNumber.foreground': N[500],
		'editorLineNumber.activeForeground': N[300],
		'editorCursor.foreground': A[200],
		'editor.selectionBackground': alpha(I[200], '4d'),
		'editor.inactiveSelectionBackground': alpha(I[200], '26'),
		'editor.selectionHighlightBackground': alpha(I[200], '26'),
		'editor.wordHighlightBackground': alpha(H.blue[200], '2e'),
		'editor.wordHighlightStrongBackground': alpha(H.blue[200], '4d'),
		'editor.findMatchBackground': alpha(A[200], '66'),
		'editor.findMatchHighlightBackground': alpha(A[200], '33'),
		'editor.findRangeHighlightBackground': alpha(N[500], '26'),
		'editor.hoverHighlightBackground': alpha(I[200], '26'),
		'editor.lineHighlightBackground': N[800],
		'editor.lineHighlightBorder': CLEAR,
		'editor.rangeHighlightBackground': alpha(I[200], '1a'),
		'editor.foldBackground': alpha(I[200], '1a'),
		'editorBracketMatch.background': alpha(A[200], '33'),
		'editorBracketMatch.border': alpha(A[200], '99'),
		'editorBracketHighlight.foreground1': bracket[0],
		'editorBracketHighlight.foreground2': bracket[1],
		'editorBracketHighlight.foreground3': bracket[2],
		'editorBracketHighlight.foreground4': bracket[3],
		'editorBracketHighlight.foreground5': bracket[4],
		'editorBracketHighlight.foreground6': bracket[5],
		'editorBracketHighlight.unexpectedBracket.foreground': H.red[200],
		'editorWhitespace.foreground': N[600],
		'editorIndentGuide.background1': N[700],
		'editorIndentGuide.activeBackground1': N[500],
		'editorRuler.foreground': N[700],
		'editorCodeLens.foreground': N[500],
		'editorLink.activeForeground': H.blue[200],
		'editorGhostText.foreground': N[500],
		'editorInlayHint.background': alpha(N[700], '99'),
		'editorInlayHint.foreground': N[300],
		'editorUnnecessaryCode.opacity': '#00000080',
		'editorError.foreground': H.red[200],
		'editorWarning.foreground': H.yellow[200],
		'editorInfo.foreground': H.cyan[200],
		'editorHint.foreground': N[400],
		'editorGutter.background': N[900],
		'editorGutter.addedBackground': H.green[200],
		'editorGutter.modifiedBackground': H.blue[200],
		'editorGutter.deletedBackground': H.red[200],
		'editorOverviewRuler.border': CLEAR,
		'editorOverviewRuler.errorForeground': H.red[200],
		'editorOverviewRuler.warningForeground': H.yellow[200],
		'editorOverviewRuler.infoForeground': H.cyan[200],
		'editorOverviewRuler.findMatchForeground': alpha(A[200], 'b3'),
		'editorOverviewRuler.selectionHighlightForeground': alpha(I[200], '99'),
		'editorOverviewRuler.addedForeground': alpha(H.green[200], '99'),
		'editorOverviewRuler.modifiedForeground': alpha(H.blue[200], '99'),
		'editorOverviewRuler.deletedForeground': alpha(H.red[200], '99'),
		'editorStickyScroll.background': N[800],
		'editorStickyScrollHover.background': N[700],
		'diffEditor.insertedTextBackground': alpha(H.green[200], '26'),
		'diffEditor.removedTextBackground': alpha(H.red[200], '26'),
		'diffEditor.insertedLineBackground': alpha(H.green[200], '14'),
		'diffEditor.removedLineBackground': alpha(H.red[200], '14'),
		'diffEditor.border': N[600],
		'merge.currentHeaderBackground': alpha(H.green[200], '4d'),
		'merge.currentContentBackground': alpha(H.green[200], '1a'),
		'merge.incomingHeaderBackground': alpha(H.blue[200], '4d'),
		'merge.incomingContentBackground': alpha(H.blue[200], '1a'),

		// Editor widgets
		'editorWidget.background': N[800],
		'editorWidget.foreground': N[200],
		'editorWidget.border': N[600],
		'editorSuggestWidget.background': N[800],
		'editorSuggestWidget.border': N[600],
		'editorSuggestWidget.foreground': N[200],
		'editorSuggestWidget.selectedBackground': N[700],
		'editorSuggestWidget.highlightForeground': A[200],
		'editorHoverWidget.background': N[800],
		'editorHoverWidget.border': N[600],
		'editorHoverWidget.statusBarBackground': N[700],
		'peekView.border': A[200],
		'peekViewEditor.background': N[800],
		'peekViewEditor.matchHighlightBackground': alpha(A[200], '4d'),
		'peekViewEditorGutter.background': N[800],
		'peekViewResult.background': N[800],
		'peekViewResult.fileForeground': N[200],
		'peekViewResult.lineForeground': N[400],
		'peekViewResult.matchHighlightBackground': alpha(A[200], '4d'),
		'peekViewResult.selectionBackground': I[700],
		'peekViewResult.selectionForeground': N[100],
		'peekViewTitle.background': N[700],
		'peekViewTitleLabel.foreground': N[100],
		'peekViewTitleDescription.foreground': N[300],

		// Editor groups and tabs
		'editorGroup.border': N[700],
		'editorGroup.dropBackground': alpha(I[200], '26'),
		'editorGroupHeader.tabsBackground': N[800],
		'editorGroupHeader.tabsBorder': N[700],
		'editorGroupHeader.noTabsBackground': N[900],
		'tab.activeBackground': N[900],
		'tab.activeForeground': N[100],
		'tab.activeBorderTop': A[200],
		'tab.inactiveBackground': N[800],
		'tab.inactiveForeground': N[400],
		'tab.unfocusedActiveForeground': N[300],
		'tab.unfocusedInactiveForeground': N[400],
		'tab.border': N[700],
		'tab.hoverBackground': N[700],
		'tab.hoverForeground': N[100],
		'tab.lastPinnedBorder': N[600],
		'breadcrumb.foreground': N[400],
		'breadcrumb.focusForeground': N[100],
		'breadcrumb.activeSelectionForeground': N[100],
		'breadcrumbPicker.background': N[800],

		// Side bar, activity bar, title bar, status bar
		'sideBar.background': N[800],
		'sideBar.foreground': N[300],
		'sideBar.border': N[700],
		'sideBarTitle.foreground': N[300],
		'sideBarSectionHeader.background': N[700],
		'sideBarSectionHeader.foreground': N[200],
		'sideBarSectionHeader.border': N[600],
		'activityBar.background': N[800],
		'activityBar.foreground': N[100],
		'activityBar.inactiveForeground': N[400],
		'activityBar.border': N[700],
		'activityBar.activeBorder': A[200],
		'activityBar.activeBackground': alpha(A[200], '14'),
		'activityBarBadge.background': A[200],
		'activityBarBadge.foreground': N[900],
		'titleBar.activeBackground': N[800],
		'titleBar.activeForeground': N[300],
		'titleBar.inactiveBackground': N[900],
		'titleBar.inactiveForeground': N[500],
		'titleBar.border': N[700],
		'statusBar.background': A[800],
		'statusBar.foreground': N[200],
		'statusBar.border': A[700],
		'statusBar.debuggingBackground': H.red[800],
		'statusBar.debuggingForeground': N[100],
		'statusBar.noFolderBackground': N[700],
		'statusBar.noFolderForeground': N[200],
		'statusBarItem.hoverBackground': alpha(N[100], '1f'),
		'statusBarItem.activeBackground': alpha(N[100], '33'),
		'statusBarItem.prominentBackground': A[700],
		'statusBarItem.prominentForeground': N[100],
		'statusBarItem.remoteBackground': I[600],
		'statusBarItem.remoteForeground': N[100],
		'statusBarItem.errorBackground': H.red[700],
		'statusBarItem.errorForeground': N[100],
		'statusBarItem.warningBackground': H.yellow[700],
		'statusBarItem.warningForeground': N[100],

		// Panels and terminal
		'panel.background': N[900],
		'panel.border': N[700],
		'panelTitle.activeForeground': N[100],
		'panelTitle.activeBorder': A[200],
		'panelTitle.inactiveForeground': N[400],
		'panelSectionHeader.background': N[800],
		'panelInput.border': N[600],
		'terminal.background': N[900],
		'terminal.foreground': N[200],
		'terminal.border': N[700],
		'terminal.selectionBackground': alpha(I[200], '4d'),
		'terminal.inactiveSelectionBackground': alpha(I[200], '26'),
		'terminal.findMatchBackground': alpha(A[200], '66'),
		'terminal.findMatchHighlightBackground': alpha(A[200], '33'),
		'terminal.tab.activeBorder': A[200],
		'terminalCursor.foreground': A[200],
		'terminalCursor.background': N[900],
		'terminal.ansiBlack': ansi.black,
		'terminal.ansiRed': ansi.red,
		'terminal.ansiGreen': ansi.green,
		'terminal.ansiYellow': ansi.yellow,
		'terminal.ansiBlue': ansi.blue,
		'terminal.ansiMagenta': ansi.magenta,
		'terminal.ansiCyan': ansi.cyan,
		'terminal.ansiWhite': ansi.white,
		'terminal.ansiBrightBlack': ansi.brightBlack,
		'terminal.ansiBrightRed': ansi.brightRed,
		'terminal.ansiBrightGreen': ansi.brightGreen,
		'terminal.ansiBrightYellow': ansi.brightYellow,
		'terminal.ansiBrightBlue': ansi.brightBlue,
		'terminal.ansiBrightMagenta': ansi.brightMagenta,
		'terminal.ansiBrightCyan': ansi.brightCyan,
		'terminal.ansiBrightWhite': ansi.brightWhite,

		// Lists, trees, menus, quick input, notifications
		'list.activeSelectionBackground': I[700],
		'list.activeSelectionForeground': N[100],
		'list.activeSelectionIconForeground': N[100],
		'list.inactiveSelectionBackground': N[700],
		'list.inactiveSelectionForeground': N[100],
		'list.focusBackground': I[700],
		'list.focusForeground': N[100],
		'list.focusOutline': A[200],
		'list.hoverBackground': alpha(N[600], '80'),
		'list.hoverForeground': N[100],
		'list.highlightForeground': A[200],
		'list.focusHighlightForeground': A[100],
		'list.dropBackground': alpha(I[200], '26'),
		'list.errorForeground': H.red[200],
		'list.warningForeground': H.yellow[200],
		'list.invalidItemForeground': H.red[200],
		'tree.indentGuidesStroke': N[600],
		'menu.background': N[800],
		'menu.foreground': N[200],
		'menu.selectionBackground': I[700],
		'menu.selectionForeground': N[100],
		'menu.separatorBackground': N[600],
		'menu.border': N[600],
		'quickInput.background': N[800],
		'quickInput.foreground': N[200],
		'quickInputList.focusBackground': I[700],
		'quickInputList.focusForeground': N[100],
		'quickInputTitle.background': N[700],
		'pickerGroup.foreground': A[200],
		'pickerGroup.border': N[600],
		'notifications.background': N[800],
		'notifications.foreground': N[200],
		'notifications.border': N[600],
		'notificationCenter.border': N[600],
		'notificationCenterHeader.background': N[700],
		'notificationCenterHeader.foreground': N[100],
		'notificationToast.border': N[600],
		'notificationLink.foreground': H.blue[200],
		'notificationsErrorIcon.foreground': H.red[200],
		'notificationsWarningIcon.foreground': H.yellow[200],
		'notificationsInfoIcon.foreground': H.cyan[200],
		'banner.background': N[700],
		'banner.foreground': N[100],
		'banner.iconForeground': A[200],

		// Source control and resource decorations
		'gitDecoration.addedResourceForeground': H.green[200],
		'gitDecoration.modifiedResourceForeground': H.blue[200],
		'gitDecoration.deletedResourceForeground': H.red[200],
		'gitDecoration.renamedResourceForeground': H.cyan[200],
		'gitDecoration.untrackedResourceForeground': H.green[100],
		'gitDecoration.ignoredResourceForeground': N[400],
		'gitDecoration.conflictingResourceForeground': H.orange[200],
		'gitDecoration.stageModifiedResourceForeground': H.blue[100],
		'gitDecoration.stageDeletedResourceForeground': H.red[100],
		'gitDecoration.submoduleResourceForeground': H.purple[200],

		// Debugging, settings and extensions
		'debugToolBar.background': N[700],
		'debugToolBar.border': N[600],
		'debugExceptionWidget.background': H.red[800],
		'debugExceptionWidget.border': H.red[300],
		'editor.stackFrameHighlightBackground': alpha(H.yellow[200], '26'),
		'editor.focusedStackFrameHighlightBackground': alpha(H.green[200], '26'),
		'settings.headerForeground': N[100],
		'settings.modifiedItemIndicator': A[200],
		'settings.dropdownBackground': N[800],
		'settings.dropdownBorder': N[600],
		'settings.textInputBackground': N[800],
		'settings.textInputBorder': N[600],
		'settings.checkboxBackground': N[800],
		'settings.checkboxBorder': N[500],
		'extensionButton.prominentBackground': I[600],
		'extensionButton.prominentForeground': N[100],
		'extensionButton.prominentHoverBackground': I[500],
		'extensionBadge.remoteBackground': I[600],
		'extensionBadge.remoteForeground': N[100],
		'charts.red': H.red[200],
		'charts.orange': H.orange[200],
		'charts.yellow': H.yellow[200],
		'charts.green': H.green[200],
		'charts.blue': H.blue[200],
		'charts.purple': H.purple[200],
		'charts.foreground': N[200],
		'charts.lines': N[500],
	};

	return colors;
};

export const buildVscodeTheme = (id) => {
	const variant = variants[id];
	const meta = vscodeVariants[id];
	const dark = variant.mode === 'dark';
	const [vs, plus] = dark
		? ['dark_vs.json', 'dark_plus.json']
		: ['light_vs.json', 'light_plus.json'];
	const [base, overlay] = [upstream(vs), upstream(plus)];
	const literals = dark ? darkRoles : lightRoles;
	const colors = workbench(variant);
	const roles = syntaxRoles(resolvedHues(variant), variant.neutral);

	return {
		$schema: 'vscode://schemas/color-theme',
		name: meta.label,
		type: dark ? 'dark' : 'light',
		semanticHighlighting: base.semanticHighlighting ?? true,
		colors,
		semanticTokenColors: semanticTokens(
			{ ...base.semanticTokenColors, ...overlay.semanticTokenColors },
			literals,
			roles,
		),
		tokenColors: recolour([...base.tokenColors, ...overlay.tokenColors], literals, roles),
	};
};

if (process.argv[1] === fileURLToPath(import.meta.url)) {
	// Start clean so a renamed or removed theme never lingers in the output
	rmSync(join(root, 'vscode', 'themes'), { recursive: true, force: true });
	mkdirSync(join(root, 'vscode', 'themes'), { recursive: true });

	for (const [id, meta] of Object.entries(vscodeVariants)) {
		const file = join(root, 'vscode', 'themes', meta.file);
		writeFileSync(file, `${JSON.stringify(buildVscodeTheme(id), null, '\t')}\n`);
		console.log(`wrote vscode/themes/${meta.file}`);
	}
}
