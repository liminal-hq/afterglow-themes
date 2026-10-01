# Midnight Commander skins

Afterglow ships three [Midnight Commander](https://midnight-commander.org) skins generated from the same palette as the OpenCode and VS Code themes. Each comes in two flavours, so there are six files in `mc/skins/`.

| Skin              | Surface                                                                  | Fallback for 256 colours |
| ----------------- | ------------------------------------------------------------------------ | ------------------------ |
| `afterglow`       | The `#050507` void with orange accents, on the terminal's own background | `afterglow-256`          |
| `afterglow-dark`  | Solid deep indigo-black with purple accents                              | `afterglow-dark-256`     |
| `afterglow-light` | Warm paper with deeper accents that hold 4.5:1 contrast                  | `afterglow-light-256`    |

## Truecolour first, with a 256-colour fallback

mc skins can name colours three ways: the 16 named colours (`red`, `brightgreen`), 256-colour palette entries (`color0` to `color255`, `rgb000` to `rgb555`, `gray0` to `gray23`) and, since mc 4.8.19, `#rrggbb` or `#rgb` truecolour. The special background `default` means the terminal's own background. Which of those works depends on the build and the terminal, not on the skin:

- **Truecolour** needs an mc built against S-Lang 2.3.1 or newer on a 64-bit system (the same requirement as mc's own `seasons-*16M` skins), and `COLORTERM=truecolor` or `COLORTERM=24bit` in the environment, with a terminal that really supports it. A skin declares `truecolors = true` in `[skin]`.
- **256 colours** needs `TERM=xterm-256color` (or similar, such as `screen-256color`). A skin declares `256colors = true`.
- Without `COLORTERM`, mc does not use truecolour even on a `-256color` terminal. A `#rrggbb` skin is then rounded to the 16 base colours, which loses most of the design.

So each variant is generated twice:

- `afterglow.ini` uses exact palette colours as `#rrggbb`. This is the intended look, and it matches the other Afterglow themes.
- `afterglow-256.ini` uses palette colours 16 to 255 for terminals that report 256 colours but not truecolour (macOS Terminal, some multiplexer setups, older SSH sessions). Each colour is rounded to the nearest palette entry, and a foreground moves to the next-nearest entry if rounding would drop its pair below the contrast it needs. Colours 0 to 15 are never used because every terminal themes them differently.

This was checked against mc 4.8.30 under `TERM=xterm-256color`. With `COLORTERM=truecolor` the truecolour skins emit 24-bit escapes (`38;2;r;g;b`), and with `COLORTERM` unset mc quietly falls back to 16 colours for them, while the `-256` skins draw with the 256-colour palette in both cases. Pick the `-256` skin if you do not control `COLORTERM`, for example over SSH.

Plain 16-colour terminals (`TERM=xterm`, the Linux console) are not supported. The 16 named colours are whatever the terminal says they are, so no skin can make Afterglow's palette appear there.

### Transparency

`afterglow` uses `default` as the background for everything that fills the screen: the panels, file list, viewer and editor. The terminal's own background, opacity and blur show through exactly as with the OpenCode `afterglow` theme. Anything that must be readable in isolation (dialogs, menus, the button bar, the status bar, input lines and highlights) uses a solid raised surface instead. Contrast for `default` is measured against the variant's neutral 900 (`#050507`), so set your terminal's background to that, or something equally dark, for the intended look. `afterglow-dark` and `afterglow-light` never use `default`, and the validator enforces that.

### What a skin cannot change

Syntax highlighting in the mc editor (`mcedit`) is not part of the skin. The syntax files in `/usr/share/mc/syntax` name colours such as `yellow` and `brightmagenta`, which mc sends as the terminal's 16 ANSI colours however the skin is written (skin `[aliases]` do not remap them). The skin controls the editor's background, text, selection, line state, bookmarks and frame, but the code colours come from your terminal's palette. For the intended result, use a terminal colour scheme that matches the skin. The Afterglow variants for OpenCode and VS Code define the ANSI colours, and the VS Code `terminal.ansi*` colours list them.

## How it is built

`scripts/build-mc.mjs` builds the skins from `scripts/hues.mjs`, the same ramps the other generators use.

1. `buildSkinModel(id)` returns every colour pair by section and key as `{ fg, bg, attrs, min }`, where `min` is the contrast the pair must hold. The generator is the only place that decides which palette step goes where.
2. `buildSkin(id, flavour)` renders the INI. For `truecolor` it writes the hex colours as they are. For `256` it rounds each colour with `nearest256`, using a redmean distance, and honours `min` against the already rounded background.
3. Box-drawing and widget characters are the same in every skin. They use the Unicode set from mc's own Four Seasons skins, with double-line frames for the panel borders.

The step meanings are the same as everywhere else: neutral 900 is the background, 800 to 600 are raised surfaces, 200 is body text and 400 is muted text, and a hue's step 200 is its main colour. Interactive states (the cursor row, dialog focus, the selected menu item, text selection and search hits) use the variant's interactive hue at step 600, with neutral 100 text. In the light variant the hue steps run the other way, so step 100 is the deeper colour and is used where a pair on a tinted surface needs the extra contrast.

## Role mapping

| mc section                          | Colours                                                                                                                                                                                                                                           |
| ----------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `[core]`                            | Text on the base surface. Cursor and selected input are neutral 100 on the interactive hue. Marked files are yellow and bold. The progress gauge is the accent fill. Panel headers are orange and bold.                                           |
| `[filehighlight]`                   | Directories blue and bold, executables green and bold, symlinks cyan, stale links rose, devices and special files yellow, archives orange, sources purple, media purple, images blue, databases orange, documents muted, and temporary files dim. |
| `[dialog]`, `[menu]`, `[popupmenu]` | Neutral 200 on neutral 700. Focus is the interactive hue, hot keys are the accent, and titles are orange and bold. The menu bar sits on neutral 800.                                                                                              |
| `[error]`                           | Neutral 100 on a rose surface, with yellow hot keys and titles.                                                                                                                                                                                   |
| `[buttonbar]`, `[statusbar]`        | Neutral text on neutral 800, and function-key numbers on a tint of the accent.                                                                                                                                                                    |
| `[help]`                            | Orange bold, cyan italic, blue links and a purple title on neutral 800.                                                                                                                                                                           |
| `[editor]`, `[viewer]`              | Text on the base surface. Bold is orange, selection is the interactive hue, search hits are the accent with a dark foreground, bookmarks are yellow, and found bookmarks are green.                                                               |
| `[diffviewer]`                      | Added is a green tint, removed is a rose tint and changed lines are blue and yellow tints, all with neutral 100 text.                                                                                                                             |
| `[Lines]`, `[widget-*]`             | Box-drawing and glyphs, shared by every skin.                                                                                                                                                                                                     |

Every section and key the reference skins in mc 4.8.30 define is set, so nothing falls through to mc's defaults. The optional `[aliases]` section is deliberately not used. `core.shadow` is the one pair not held to a contrast ratio, since it is a drop shadow. The complete list is in `scripts/mc-skin-keys.json`.

## Validation

`bun run validate:themes` (part of `bun run validate`) runs `scripts/validate-mc.mjs` over every skin.

- The committed skins match what the generator produces.
- Every section and key in `scripts/mc-skin-keys.json` is present and non-empty, and no unknown section or key appears. The list was extracted from the skins shipped with mc 4.8.30. Refresh it when a new mc release adds keys.
- Each skin declares `truecolors = true` or `256colors = true`, matching its flavour.
- Colours are valid for the flavour: `#rrggbb` in truecolour skins, `color16` to `color255` in 256-colour skins, `default` only as a background, and only known attributes.
- About 80 foreground and background pairs meet 4.5:1, and the deliberately dim ones (disabled text, the command-line history marker, whitespace marks and temporary files) are held to a 3:1 floor. mc has no alpha, so no compositing is needed. A `default` background is measured against neutral 900. The 256-colour skins are measured with their rounded colours, not the originals.
- Only `afterglow` uses `default`, and it uses it for `[core] _default_`.

Contrast for `afterglow` is measured against the `#050507` void, so it only holds as long as your terminal background is dark and near-black. On a bright or heavily blurred background the `default` surfaces can fall below the stated ratios. The validator checks structure and contrast, not appearance.

## Testing with a real mc

The skins were loaded in real mc 4.8.30 under `tmux`, and the file panels, menu bar, dialogs, error dialog, help, viewer, editor and diff viewer of all three variants were captured and checked by eye. Transparency over a real terminal background, `COLORTERM=24bit` and 16-colour terminals have not been tested.

To try a skin without touching your own configuration, install into a scratch data directory and run mc inside a pseudo-terminal:

```sh
XDG_DATA_HOME=/tmp/mc-data bun run install:mc
XDG_DATA_HOME=/tmp/mc-data TERM=xterm-256color COLORTERM=truecolor mc -S afterglow
```

To capture the result without a terminal window, start mc in `tmux` with `terminal-features ",*:RGB"`, send keys with `tmux send-keys`, and read the screen with `tmux capture-pane -e -p`. The escape sequences convert to HTML for a screenshot with a headless browser. The skins were checked this way for the panels (with marked files and the cursor row), the menu bar and a pull-down menu, a dialog, an error dialog, the help viewer, the file viewer with a search hit, the editor with a selection and the diff viewer, in all six files.

## Installing

`bun run install:mc` builds the skins and copies them to `${XDG_DATA_HOME:-~/.local/share}/mc/skins`. Releases ship them as `afterglow-mc-skins-vX.Y.Z.zip`, which unpacks straight into that directory.
