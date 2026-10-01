# TextMate themes (Codex, bat and delta)

Afterglow ships three standard TextMate `.tmTheme` files, generated from the same palette and the same role mapping as the VS Code themes.

| Theme             | File                      | Surface                                         |
| ----------------- | ------------------------- | ----------------------------------------------- |
| `Afterglow`       | `afterglow.tmTheme`       | The `#050507` void, with the orange caret       |
| `Afterglow Dark`  | `afterglow-dark.tmTheme`  | Solid deep indigo-black, with the purple accent |
| `Afterglow Light` | `afterglow-light.tmTheme` | Warm paper, with the purple accent              |

They are plain TextMate themes with no Codex-only extensions, so any tool that reads `.tmTheme` files can use them. Three tools are the targets:

- **The Codex CLI** (v0.105 or newer) loads custom syntax themes from `$CODEX_HOME/themes/*.tmTheme` (`~/.codex/themes` by default). The kebab-case file name is the theme name, so these are `afterglow`, `afterglow-dark` and `afterglow-light`. Choose one with `/theme`, or set `theme = "afterglow-dark"` under `[tui]` in `$CODEX_HOME/config.toml`. Codex only uses a theme to highlight fenced code blocks and file diffs.
- **bat** reads themes from `$(bat --config-dir)/themes`. Copy the files there, run `bat cache --build`, and choose one with `--theme="Afterglow Dark"` (or `BAT_THEME`). `bat --list-themes` shows the names.
- **delta** uses bat's themes, so after the steps above set `syntax-theme = Afterglow Dark` under `[delta]` in your git config.

## Install

From a release, unpack `afterglow-tmthemes-vX.Y.Z.zip` into the themes directory of the tool:

```sh
mkdir -p ~/.codex/themes
unzip afterglow-tmthemes-v*.zip '*.tmTheme' -d ~/.codex/themes

mkdir -p "$(bat --config-dir)/themes"
unzip afterglow-tmthemes-v*.zip '*.tmTheme' -d "$(bat --config-dir)/themes"
bat cache --build
```

From source, `bun run install:tmtheme` builds the themes and copies them into `${CODEX_HOME:-~/.codex}/themes`. It does not touch bat: use the `cp` and `bat cache --build` steps above.

## How the theme is built

`scripts/build-tmtheme.mjs` does not choose colours itself. It builds the VS Code theme for the variant (`scripts/build-vscode.mjs`, which recolours the Dark+ and Light+ token colours with `syntaxRoles`) and converts it to a property list:

- **Syntax roles** are the shared ones: purple keywords, rose control flow and tags, orange functions, green strings, yellow numbers, cyan types, blue constants and variables and links, and neutral 400 for comments and punctuation. Every scope rule in Dark+ and Light+ is kept, in the same order, so languages colour the way you expect.
- **Global settings** come from the editor colours of the VS Code theme: `background` (neutral 900), `foreground` (200), `caret` (the accent), `selection` and `lineHighlight`, `invisibles`, and `gutter` and `gutterForeground`, which bat and delta also read. Translucent colours such as the VS Code selection are flattened onto the background, because `.tmTheme` colours are opaque.
- **Font styles**: `bold`, `italic` and `underline` are kept. VS Code's `strikethrough` has no TextMate equivalent and the syntect library behind bat, delta and Codex rejects unknown styles, so it is dropped (a rule that only set a strikethrough is removed).
- **The UUID** of each theme is derived from its id, so rebuilding never changes the file.

`scripts/validate-tmtheme.mjs` has its own strict plist parser and checks:

- the file is a well-formed property list (matching tags, valid entities, no duplicate keys),
- the `name` and `uuid`, and that the first settings entry is the global one with the required keys,
- every colour is `#rrggbb` and every font style is one TextMate knows,
- the scope rules are exactly those of the VS Code theme (the same scopes, colours and styles, in order),
- every foreground holds 4.5:1 on the background (about 65 pairs per theme), the foreground holds 4.5:1 on the selection and line highlight, and the caret and gutter text hold 3:1,
- the committed file matches the generator.

## Transparency

A `.tmTheme` has a single opaque `background`. The signature `afterglow` theme therefore uses the `#050507` void as a solid colour, unlike the OpenCode and Midnight Commander themes. Codex and bat draw that background only where they paint one, so on a transparent terminal the effect depends on the tool.

## What was verified

- The files parse as property lists with Python's `plistlib`, and with the validator's own strict parser, which the test suite also feeds malformed input.
- The scope rules were compared with the VS Code themes by the validator, and every foreground meets the contrast above.
- The format details come from the [Codex CLI documentation](https://learn.chatgpt.com/docs/cli-customization) and the community [awesome-codex-themes](https://github.com/mcpso/awesome-codex-themes) list (the `$CODEX_HOME/themes` directory, `tui.theme`, and the file name becoming the theme name).

## What was not verified

- The themes were not loaded by Codex, bat or delta: none of them is installed on the machine they were generated on. The claims about those tools rest on their documentation and on the format being standard TextMate.
- Nothing was checked by eye in a real terminal.
- syntect (the library behind bat, delta and Codex) is stricter than TextMate about a few things, such as font styles, which is why the generator drops `strikethrough`. A scope selector that syntect cannot parse would not be caught by the validator.

## Limitations

- **Codex themes syntax only.** It colours fenced code blocks and diffs, not the rest of the terminal interface, so the Codex theme does not recolour the interface. The Codex desktop app uses a different theme format.
- **The scopes are VS Code's.** They are TextMate scope selectors, but the grammars a tool ships decide which scopes a given language produces, so colouring can differ slightly between VS Code, bat and Codex.
