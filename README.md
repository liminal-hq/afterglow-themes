# Afterglow

<p align="center">
  <img src="assets/hero.svg" alt="Afterglow — Liminal HQ colour themes for the tools you live in" width="100%">
</p>

<p align="center">
  <a href="https://github.com/liminal-hq/afterglow-themes/actions/workflows/ci.yml"><img src="https://github.com/liminal-hq/afterglow-themes/actions/workflows/ci.yml/badge.svg" alt="CI status"></a>
  <a href="https://github.com/liminal-hq/afterglow-themes/releases"><img src="https://img.shields.io/github/v/release/liminal-hq/afterglow-themes?include_prereleases&color=f97316" alt="Latest release"></a>
  <img src="https://img.shields.io/badge/OpenCode-V2%20themes-1f6feb" alt="OpenCode V2 themes">
  <img src="https://img.shields.io/badge/VS%20Code-themes-a78bfa" alt="VS Code themes">
  <img src="https://img.shields.io/badge/Midnight%20Commander-skins-ffaa40" alt="Midnight Commander skins">
  <img src="https://img.shields.io/badge/Claude%20Code-themes-d97757" alt="Claude Code themes">
  <img src="https://img.shields.io/badge/Codex%20%C2%B7%20bat%20%C2%B7%20delta-tmThemes-f43f5e" alt="Codex, bat and delta TextMate themes">
  <img src="https://img.shields.io/badge/Firefox%20%C2%B7%20Chrome%20%C2%B7%20Edge-themes-4285f4" alt="Firefox, Chrome and Edge themes">
  <img src="https://img.shields.io/badge/licence-Apache--2.0%20OR%20MIT-3fb950" alt="Licence: Apache-2.0 OR MIT">
</p>

Afterglow is the Liminal HQ colour theme for the [OpenCode](https://opencode.ai) terminal UI, for VS Code, for [Midnight Commander](https://midnight-commander.org), for [Claude Code](https://code.claude.com), and for the [Codex](https://developers.openai.com/codex) CLI, [bat](https://github.com/sharkdp/bat) and [delta](https://github.com/dandavison/delta) through TextMate themes, and for Firefox, Chrome and Edge: the soft orange, rose and purple that linger on the horizon after the light goes, set against a near-black void. Each comes in three variants, and the OpenCode and Midnight Commander ones have a see-through variant so your terminal's own background and blur show through.

> **Status:** early development. The themes are complete and pass the schema and contrast checks in CI. The OpenCode themes target the V2 theme format and are tested against OpenCode v2.0.21. The VS Code extension is not yet published to the Marketplace; install it from a release. The Claude Code themes follow Claude Code's custom theme format, which Anthropic documents but does not version, and the TextMate themes have not been loaded in Codex, bat or delta yet (see the docs for what was verified). The Firefox, Chrome and Edge themes are unsigned and unpublished, so they load temporarily or unpacked (see the install steps).

## The OpenCode themes

| Theme             | Mode  | What it is                                                                                                                                                                                |
| ----------------- | ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `afterglow`       | Dark  | The signature theme. The liminalhq.ca void with brand orange and purple accents and a transparent background, so your terminal's opacity or blur shows through. Dialogs stay near-opaque. |
| `afterglow-dark`  | Dark  | A solid, deep indigo-black theme with purple and blue accents, for terminals without transparency or when you want a calmer, flatter surface.                                             |
| `afterglow-light` | Light | A warm paper theme with deeper accents that hold 4.5:1 contrast on light backgrounds.                                                                                                     |

All three cover every OpenCode surface: text and actions, backgrounds and raised panels, borders, diffs, syntax highlighting and Markdown.

## The VS Code themes

| Theme             | Mode  | What it is                                                                |
| ----------------- | ----- | ------------------------------------------------------------------------- |
| `Afterglow`       | Dark  | The `#050507` void with orange accents, for a deep, high-contrast editor. |
| `Afterglow Dark`  | Dark  | A softer deep indigo-black with purple accents.                           |
| `Afterglow Light` | Light | A warm paper theme with deeper accents that hold 4.5:1 contrast.          |

The syntax colouring keeps every TextMate scope rule and semantic token override from VS Code's built-in **Dark+** and **Light+** themes, recoloured with the Afterglow palette, so languages colour the way you expect. The editor, tabs, side bar, status bar, panels and terminal are all coloured deliberately rather than inherited from VS Code's defaults. See [docs/vscode-theme.md](docs/vscode-theme.md).

## The Midnight Commander skins

| Skin              | Mode  | What it is                                                                                                                                                                                                   |
| ----------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `afterglow`       | Dark  | The `#050507` void with orange accents. The panels, viewer and editor use the terminal's own background, so transparency and blur show through (contrast is guaranteed on a near-black terminal background). |
| `afterglow-dark`  | Dark  | Solid deep indigo-black with purple accents.                                                                                                                                                                 |
| `afterglow-light` | Light | Warm paper with deeper accents that hold 4.5:1 contrast.                                                                                                                                                     |

Every section of the skin is coloured deliberately: the file list and file types, the cursor and marked files, menus, dialogs, errors, the button bar, the help, viewer, editor and diff viewer. Each skin also has a `-256` fallback (for example `afterglow-dark-256`) for terminals that report 256 colours but not truecolour. See [docs/mc-skin.md](docs/mc-skin.md).

## The Claude Code themes

| Theme             | Mode  | What it is                                                                              |
| ----------------- | ----- | --------------------------------------------------------------------------------------- |
| `Afterglow`       | Dark  | The `#050507` void with the orange accent, on Claude Code's `dark` preset.              |
| `Afterglow Dark`  | Dark  | A softer deep indigo-black with the purple accent, on the `dark` preset.                |
| `Afterglow Light` | Light | A warm paper theme with deeper accents that hold 4.5:1 contrast, on the `light` preset. |

Each theme sets all 72 colour tokens Claude Code defines, from the same role hues as the other themes: the spinner and brand, modes and dialogs, status colours, diffs, transcript backgrounds, subagent colours and the usage meter. Claude Code draws on your terminal's own background, so there is no transparency to set, and fenced code blocks use Claude Code's own syntax colours. See [docs/claude-code-theme.md](docs/claude-code-theme.md).

## The Firefox, Chrome and Edge themes

| Theme             | Mode  | What it is                                                       |
| ----------------- | ----- | ---------------------------------------------------------------- |
| `Afterglow`       | Dark  | The `#050507` void with the orange accent.                       |
| `Afterglow Dark`  | Dark  | A softer deep indigo-black with the purple accent.               |
| `Afterglow Light` | Light | A warm paper theme with deeper accents that hold 4.5:1 contrast. |

Firefox gets all 38 colours its theme manifest defines, and Chrome and Edge share one Manifest V3 theme with the 16 colours Chromium reads: the tab strip, toolbar, address bar, menus and sidebar (Firefox) and the new tab page. The dark Firefox themes also carry a faint SVG glow of the accent hues behind the tab strip and toolbars, like the liminalhq.ca background (Chromium only takes PNG theme images, so Chrome and Edge stay flat). Web pages keep their own colours, and neither browser has a see-through variant. See [docs/browser-themes.md](docs/browser-themes.md).

## The Codex, bat and delta themes

| Theme             | Mode  | What it is                                                             |
| ----------------- | ----- | ---------------------------------------------------------------------- |
| `afterglow`       | Dark  | The `#050507` void with an orange caret, for deep, high-contrast code. |
| `afterglow-dark`  | Dark  | A softer deep indigo-black with the purple accent.                     |
| `afterglow-light` | Light | A warm paper theme with deeper accents that hold 4.5:1 contrast.       |

These are standard TextMate `.tmTheme` files, with the same syntax colours as the VS Code themes. The Codex CLI uses them to highlight fenced code blocks and diffs, and bat and delta read the same format. See [docs/tmtheme.md](docs/tmtheme.md).

## Install

### OpenCode

Download the latest bundle from the [releases page](https://github.com/liminal-hq/afterglow-themes/releases), then unpack it into OpenCode's global themes directory:

```sh
mkdir -p ~/.config/opencode/themes
unzip afterglow-themes-v*.zip -d ~/.config/opencode/themes
```

Restart OpenCode, run `/themes` and pick an Afterglow theme. To make it the default, set it in `~/.config/opencode/cli.json`:

```json
{
	"theme": { "name": "afterglow", "mode": "dark" }
}
```

A project's `.opencode/themes/` directory works too, if you only want Afterglow for one project. Each release also lists a `SHA256SUMS` file so you can check the download.

### VS Code

Download `afterglow-vscode-vX.Y.Z.vsix` from the [releases page](https://github.com/liminal-hq/afterglow-themes/releases) and install it:

```sh
code --install-extension afterglow-vscode-v*.vsix
```

Then run **Preferences: Color Theme** (`Ctrl+K Ctrl+T`) and pick an Afterglow theme.

### Midnight Commander

Download `afterglow-mc-skins-vX.Y.Z.zip` from the [releases page](https://github.com/liminal-hq/afterglow-themes/releases) and unpack it into mc's skins directory:

```sh
mkdir -p ~/.local/share/mc/skins
unzip afterglow-mc-skins-v*.zip -d ~/.local/share/mc/skins
```

Then start mc with `mc -S afterglow`, or pick a skin under **Options > Appearance** and save the setup. The skins need mc 4.8.19 or newer built against S-Lang 2.3.1 or newer on a 64-bit system, and truecolour needs `COLORTERM=truecolor` (or `24bit`) in a terminal that supports it, with `TERM=xterm-256color`. If your terminal or session cannot offer that (over SSH, for example), use the `-256` skin: `mc -S afterglow-256`. Without `COLORTERM`, mc rounds the truecolour skins down to 16 colours, which looks wrong. The mc editor's syntax colours come from your terminal's own palette rather than the skin.

### Claude Code

Download `afterglow-claude-code-themes-vX.Y.Z.zip` from the [releases page](https://github.com/liminal-hq/afterglow-themes/releases) and unpack it into Claude Code's themes directory:

```sh
mkdir -p ~/.claude/themes
unzip afterglow-claude-code-themes-v*.zip '*.json' -d ~/.claude/themes
```

Then run `/theme` in Claude Code and pick **Afterglow**, **Afterglow Dark** or **Afterglow Light** from the custom themes at the end of the list. If you keep your Claude Code configuration somewhere else, use `$CLAUDE_CONFIG_DIR/themes` instead. Restart Claude Code once if the `themes` directory did not exist when it started.

### Firefox

Afterglow's Firefox themes are unsigned, and Firefox only keeps signed add-ons, so load one temporarily: open `about:debugging#/runtime/this-firefox`, choose **Load Temporary Add-on** and pick the `manifest.json` in a theme's folder under `firefox/themes/` (or the release's `.xpi`). It lasts until Firefox restarts. Firefox Developer Edition, Nightly and ESR can install the `.xpi` for good once `xpinstall.signatures.required` is `false`.

### Chrome and Edge

Download `afterglow-chromium-themes-vX.Y.Z.zip` from the [releases page](https://github.com/liminal-hq/afterglow-themes/releases) and unzip it. Open `chrome://extensions` (or `edge://extensions`), turn on **Developer mode**, choose **Load unpacked** and pick `afterglow`, `afterglow-dark` or `afterglow-light`. See [docs/browser-themes.md](docs/browser-themes.md) for the details and limits.

### Codex, bat and delta

Download `afterglow-tmthemes-vX.Y.Z.zip` from the [releases page](https://github.com/liminal-hq/afterglow-themes/releases). For the Codex CLI (v0.105 or newer), unpack it into the Codex themes directory:

```sh
mkdir -p ~/.codex/themes
unzip afterglow-tmthemes-v*.zip '*.tmTheme' -d ~/.codex/themes
```

Then run `/theme` in Codex and pick `afterglow`, `afterglow-dark` or `afterglow-light`, or set it in `$CODEX_HOME/config.toml` (`~/.codex/config.toml` by default):

```toml
[tui]
theme = "afterglow-dark"
```

Codex uses the theme for syntax highlighting in code blocks and diffs only. For bat, copy the same files into bat's themes directory and rebuild its cache:

```sh
mkdir -p "$(bat --config-dir)/themes"
unzip afterglow-tmthemes-v*.zip '*.tmTheme' -d "$(bat --config-dir)/themes"
bat cache --build
bat --theme="Afterglow Dark" README.md
```

delta takes bat's themes, so set `syntax-theme = Afterglow Dark` under `[delta]` in your git config once bat knows them.

### From source

With [Bun](https://bun.sh) installed:

```sh
git clone https://github.com/liminal-hq/afterglow-themes.git
cd afterglow-themes
bun install
bun run install:themes
```

This builds the themes and copies them into `~/.config/opencode/themes/` (or `$XDG_CONFIG_HOME/opencode/themes/`). For Midnight Commander, run `bun run install:mc` to copy the skins into `~/.local/share/mc/skins/` (or `$XDG_DATA_HOME/mc/skins/`). `bun run install:claude` copies the Claude Code themes into `~/.claude/themes/` (or `$CLAUDE_CONFIG_DIR/themes/`), and `bun run install:tmtheme` copies the TextMate themes into `~/.codex/themes/` (or `$CODEX_HOME/themes/`).

## Transparency

The `afterglow` OpenCode theme sets the main background to `transparent` and keeps raised surfaces such as the prompt and tool blocks a solid dark tone (OpenCode does not appear to blend a box with your terminal background), so the effect depends on your terminal supporting background opacity (Kitty, Alacritty, WezTerm, Ghostty and Windows Terminal all do). If you would rather have a solid background, use `afterglow-dark`. The `afterglow` Midnight Commander skin works the same way, using the terminal's default background for the panels. Claude Code never paints a page background, so its themes already let your terminal show through. A `.tmTheme` has one opaque background, so the TextMate themes do not have a see-through variant.

## Where the colours come from

The palette was gathered by scanning the [Liminal HQ](https://github.com/liminal-hq) repositories for colour tokens and counting what recurs. The pattern is a calm near-black background, a warm orange-to-rose-to-purple family of accents, and cool cyan and blue for information.

- **The void and the accents** come from liminalhq.ca: `#050507` for the background, `#e0e0e0` for text, `#b4bfce` for muted text, and the orange `#ffaa40`, rose `#f43f5e`, purple `#a78bfa`, cyan `#22d3ee` and blue `#60a5fa` accents.
- **Greens and yellows** (`#2ec66a`, `#fbbf24`) recur across SMDU, Threshold and Flow.
- **The solid dark surfaces** (`#0f0e1a`, `#1a1828`) come from Jar and the indigo-black tones used across the apps.
- **The light paper theme** uses Jar's warm `#fbfaf6` and `#2b2a33`, Cadence's `#5e44cc` purple and surface tones, and Threshold's `#2563eb` blue.
- **The roles are shared by every target**: purple keywords, rose control flow and errors, orange functions and the brand, green strings and success, yellow numbers and warnings, cyan types and information, and blue constants, variables and links.

See [docs/theme-format.md](docs/theme-format.md) for how the palette becomes OpenCode tokens and the design decisions behind the themes.

## Development

The themes are generated, so edit the palette and rebuild rather than editing the JSON by hand.

```sh
bun install
bun run build            # regenerate themes/, vscode/themes/, mc/skins/, claude/themes/, tmtheme/, firefox/themes/ and chromium/themes/
bun run validate:themes  # check the schema rules and 4.5:1 text contrast
bun run validate         # the full local gate that mirrors CI
bun run bundle           # build the release assets (including the .vsix) into dist/release
```

- `scripts/palette.mjs` holds the brand colours, the deeper light-mode variants and the neutral ramps.
- `scripts/build.mjs` turns them into OpenCode V2 themes. Each hue is a nine-step ramp with the brand colour on step `200`, matching how OpenCode's built-in themes are laid out.
- `scripts/build-vscode.mjs` builds the VS Code themes from the same palette, using the Dark+ and Light+ scope rules in `vscode/upstream/` as the structural base.
- `scripts/build-mc.mjs` builds the Midnight Commander skins (truecolour and 256-colour) from the same palette, and `scripts/validate-mc.mjs` checks every section and key against `scripts/mc-skin-keys.json`, the colour syntax and about 80 contrast pairs per skin.
- `scripts/build-claude.mjs` builds the Claude Code themes (all 72 tokens, listed in `scripts/claude-theme-tokens.json`) and `scripts/validate-claude.mjs` checks the file schema, the tokens, the colour syntax and about 80 contrast pairs per theme.
- `scripts/build-tmtheme.mjs` converts the recoloured VS Code token colours into `.tmTheme` files, so the syntax colours have one source, and `scripts/validate-tmtheme.mjs` checks the plist, the global settings, the scopes against the VS Code themes and the contrast.
- `scripts/browser-roles.mjs` maps the ramps onto the roles both browsers need. `scripts/build-firefox.mjs` and `scripts/build-chromium.mjs` build the Firefox and the Chrome and Edge theme manifests from it, and `scripts/validate-firefox.mjs` and `scripts/validate-chromium.mjs` check the keys (`scripts/firefox-theme-keys.json`, `scripts/chromium-theme-keys.json`), the colour syntax and the contrast.
- `scripts/validate-themes.mjs` mirrors the V2 theme schema bundled in OpenCode (the published JSON schema for V2 themes is not available yet), resolves every reference, and checks the contrast of text, syntax and Markdown colours. `scripts/validate-vscode.mjs` does the same for the VS Code themes (about 90 foreground and background pairs, with alpha composited first) and also checks every colour key against VS Code's published list.

CI runs the format check, the licence-header check, the theme build and validation (including a check that the committed JSON matches what the palette generates), Markdown and workflow linting, and a zizmor security audit of the workflows.

## Releases

Releases are tagged `vX.Y.Z` on `main`, and the tag must match the `version` in `package.json`. The release workflow runs the full validation, then attaches the three OpenCode theme files, a zip bundle, the VS Code `.vsix`, the Midnight Commander skins zip, the Claude Code themes zip, the TextMate themes zip, a Firefox `.xpi` per theme, the Chrome and Edge themes zip and a `SHA256SUMS` file to a GitHub release with generated notes.

## Contributing

Read [AGENTS.md](AGENTS.md) for the conventions: Canadian spelling, Conventional Commits, the pull request format and the labels. If a colour looks off in your terminal, open an issue with a screenshot and the OpenCode version.

## Licence

Dual-licensed under [Apache-2.0](LICENSE-APACHE) or [MIT](LICENSE-MIT), at your option.
