# VS Code theme

The Afterglow VS Code extension (`vscode/`) ships three colour themes generated from the same palette as the OpenCode themes.

| Theme             | Based on                          | Surface                           |
| ----------------- | --------------------------------- | --------------------------------- |
| `Afterglow`       | Dark+, `afterglow` palette        | The `#050507` void, orange accent |
| `Afterglow Dark`  | Dark+, `afterglow-dark` palette   | Deep indigo-black, purple accent  |
| `Afterglow Light` | Light+, `afterglow-light` palette | Warm paper, purple accent         |

## How it is built

`scripts/build-vscode.mjs` generates each theme in two parts.

- **Syntax colours** come from Dark+ and Light+. The unmodified upstream files live in `vscode/upstream/` (see `NOTICE.md` for the MIT attribution). The generator keeps every TextMate scope rule and semantic token override they define, in the same order, and replaces each colour with an Afterglow palette colour by role. Dark+ and Light+ colour roles with different literals, so the generator maps both sets of literals to roles (`keyword`, `control`, `function`, `string`, `number`, `type`, `constant`, `variable`, `tag` and so on). A literal with no role stops the build, so nothing slips through unmapped.
- **Workbench colours** (the editor, tabs, side bar, status bar, panels, terminal, lists, menus, widgets and source control decorations) are written out in full. Dark+ and Light+ leave most of these to VS Code's built-in defaults, which would bring the old blue accents back, so the generator sets about 320 colour keys itself.

Each role is the same hue in every variant, so code reads the same across the three themes and matches the syntax colours in the OpenCode themes. The hue ramps and step conventions are shared with the OpenCode generator through `scripts/hues.mjs`; see [theme-format.md](theme-format.md).

A few decisions worth knowing about:

- Dark+ and Light+ disagree about some scopes (tag names are blue in Dark+ and maroon in Light+). Afterglow pins these by scope in `scopeRoles` so every variant treats them the same way.
- The status bar uses a dark tint of the theme's accent (`accent.800`) rather than a saturated block, so it matches the rest of the chrome.
- VS Code themes cannot make the window transparent, so there is no see-through variant. `Afterglow` is the closest, with the void as a solid background.
- Light terminal colours are chosen for 4.5:1 contrast on paper, so ANSI "white" is a readable grey rather than a near-white.

## Validation

`bun run validate:themes` (part of `bun run validate`) checks each generated theme.

- The committed theme files match what the generator produces.
- Every colour key is a real VS Code colour key, checked against `scripts/vscode-colour-keys.json`, which was extracted from the [theme colour reference](https://code.visualstudio.com/api/references/theme-color). Refresh it from the `microsoft/vscode-docs` repository when VS Code adds keys.
- Every value is a 6 or 8 digit hex colour.
- The `tokenColors` rules have the same scopes, in the same order, as Dark+ and Light+.
- Syntax colours, text, and about 60 foreground and background pairs (tabs, side bar, status bar, buttons, inputs, lists, menus, terminal colours and more) meet their contrast ratios.
- `vscode/package.json` lists every theme and has the same version as the root `package.json`.

The validator checks structure and contrast, not appearance. To look at the syntax colours without opening VS Code, render samples through the theme files with [Shiki](https://shiki.style), which uses the same TextMate engine, and screenshot the result. Check the editor chrome in VS Code itself.

## Packaging and publishing

`bun run bundle` stages the extension in `dist/vscode-extension` (only the manifest, README, images, themes, the Dark+ and Light+ notice and the licences) and packages it with `vsce` into `dist/release/afterglow-vscode-vX.Y.Z.vsix`. The release workflow attaches that file to the GitHub release.

To install a release build locally, run `code --install-extension afterglow-vscode-vX.Y.Z.vsix`.

Publishing to the VS Code Marketplace (`vsce publish`) and Open VSX (`ovsx publish`) is a manual step that needs the `liminal-hq` publisher and an access token. It is not part of the release workflow.

## Images

`vscode/images/icon.png` and `vscode/images/banner.png` are rendered from `vscode/images/icon.svg` and `assets/hero.svg`. The Marketplace blocks SVG images in a README, so the PNGs are committed. To regenerate them, screenshot the SVGs with a headless browser at 256 by 256 and 1200 by 320, then commit the results.
