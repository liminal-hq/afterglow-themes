# Claude Code themes

Afterglow ships three custom themes for [Claude Code](https://code.claude.com), generated from the same palette as the OpenCode, VS Code and Midnight Commander themes.

| Theme             | File                   | Base preset | Surface                                         |
| ----------------- | ---------------------- | ----------- | ----------------------------------------------- |
| `Afterglow`       | `afterglow.json`       | `dark`      | The `#050507` void, with the orange accent      |
| `Afterglow Dark`  | `afterglow-dark.json`  | `dark`      | Solid deep indigo-black, with the purple accent |
| `Afterglow Light` | `afterglow-light.json` | `light`     | Warm paper, with the purple accent              |

## The file format

A custom theme is a JSON file in `${CLAUDE_CONFIG_DIR:-~/.claude}/themes/`. The file name without `.json` is the theme's slug, and choosing the theme in `/theme` stores `custom:<slug>` as your theme preference. The file has three optional fields:

| Field       | Type   | Meaning                                                                                                                                             |
| ----------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `name`      | string | The label `/theme` shows. Defaults to the slug.                                                                                                     |
| `base`      | string | The built-in preset the theme starts from: `dark`, `light`, `dark-daltonized`, `light-daltonized`, `dark-ansi` or `light-ansi`. Defaults to `dark`. |
| `overrides` | object | A map of colour token names to colour values. Tokens not listed fall through to the base preset.                                                    |

Colour values are `#rrggbb`, `#rgb`, `rgb(r,g,b)`, `ansi256(n)` or `ansi:<name>`. Unknown tokens and invalid colours are ignored, so a typo cannot break rendering (and also cannot be seen, which is why `scripts/validate-claude.mjs` rejects them). There is no `extends` field and no separate light or dark flag: whether a theme is light or dark follows from its `base` name. A file larger than 256 KiB is skipped, and `claude --safe-mode` turns custom themes off. Claude Code watches the directory, so edits apply to a running session (restart once if the `themes` directory did not exist when it started).

### Base choice

A theme can override just some tokens, so `base` mainly decides what happens to tokens the theme leaves alone. Afterglow sets every one of the 72 tokens, so nothing leaks through from the preset, and the base only records whether the theme is dark or light. `afterglow` and `afterglow-dark` use `dark`, and `afterglow-light` uses `light`. If Claude Code adds a token in a later release, a theme without it falls back to that preset's colour until the generator is updated (the validator reads `scripts/claude-theme-tokens.json`, which is refreshed from the binary).

### Transparency

The OpenCode `afterglow` theme paints a transparent page. Claude Code has no background token at all, because it never paints the page: it draws on your terminal's own background. So there is nothing to make transparent, and no transparency is added. A terminal with opacity or blur shows through exactly as it does with any other Claude Code theme. The theme's `clawd_background` (the backdrop of the mascot art) is the variant's neutral 900, and the contrast checks measure against that colour, so set your terminal background to `#050507` (`afterglow`), `#0f0e1a` (`afterglow-dark`) or `#fbfaf6` (`afterglow-light`) for the intended look.

## Tokens and roles

Each token has a deliberate colour from the shared role hues: orange for the brand and functions, purple for modes and skills, rose for errors, green for success, yellow for warnings, cyan for information and plan mode, and blue for links and the IDE. Step meanings match the other themes: neutral 900 is the surface, 200 is body text, 400 is muted text, and a hue's step 200 is its main colour.

| Tokens                                                                                                                                                   | Colour                                                                                                                                                                                                                                          |
| -------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `claude`, `clawd_body`, `briefLabelClaude`                                                                                                               | The variant's accent (orange for `afterglow`, purple for the others): the spinner, assistant label and mascot.                                                                                                                                  |
| `permission`, `suggestion`, `rate_limit_fill`                                                                                                            | The interactive hue (purple for `afterglow`, blue for the others): dialog borders, autocomplete and the pickers' highlight, and the filled usage meter.                                                                                         |
| `text`, `inactive`, `subtle`, `inverseText`                                                                                                              | Neutral 200 body text, 400 muted text, 500 faint text, and 900 for text drawn on a coloured fill.                                                                                                                                               |
| `promptBorder`                                                                                                                                           | Neutral 500 in dark themes and 400 in the light theme. The input border is read all day, so it sits above the 600 borders used elsewhere.                                                                                                       |
| `success`, `error`, `warning`, `merged`                                                                                                                  | Green, rose, yellow and purple at step 200.                                                                                                                                                                                                     |
| `planMode`, `ide`, `background`, `remember`, `claudeBlue_FOR_SYSTEM_SPINNER`, `professionalBlue`, `briefLabelYou`                                        | Cyan for plan mode and background tasks, blue for the IDE, memory, the system spinner, the blue brand mark and the `You` label.                                                                                                                 |
| `autoAccept`, `skill`, `effortUltra`                                                                                                                     | Purple, for accept-edits mode, skills and the `ultracode` tag. `bashBorder` is rose, `fastMode` orange and `chromeYellow` yellow.                                                                                                               |
| `diffAdded`, `diffRemoved`, `diffAddedDimmed`, `diffRemovedDimmed`, `diffAddedWord`, `diffRemovedWord`                                                   | Green and rose tints: step 700 for the line, 800 for the dimmed diff and 500 for the word highlight. Body text holds 4.5:1 on all of them.                                                                                                      |
| `userMessageBackground`, `userMessageBackgroundHover`, `composerSidebarBackground`, `bashMessageBackgroundColor`, `memoryBackgroundColor`, `selectionBg` | Neutral 800 for your messages and the composer sidebar, a step towards 700 on hover, an orange tint for shell entries, a cyan tint for memory entries and the interactive hue at 600 for the selection. Body and muted text hold 4.5:1 on each. |
| `red_FOR_SUBAGENTS_ONLY` and the other seven                                                                                                             | The matching hue at step 200. The palette has no pink, so `pink_FOR_SUBAGENTS_ONLY` is a blend of the rose and purple.                                                                                                                          |
| `rainbow_*` and `rainbow_*_shimmer`                                                                                                                      | The `ultrathink` gradient: rose, orange, yellow, green, blue, indigo (a blend of blue and purple) and violet (purple).                                                                                                                          |
| every `*Shimmer`                                                                                                                                         | The lighter colour the spinner animates to. Dark themes use the hue's step 100. A light theme's step 100 is the darker end, so it mixes the main colour a quarter of the way towards the paper.                                                 |
| `rate_limit_empty`                                                                                                                                       | Neutral 500, the unfilled usage meter.                                                                                                                                                                                                          |

## How it is built and validated

`scripts/build-claude.mjs` builds each theme from `scripts/hues.mjs`, the ramps the other generators use, and writes `claude/themes/*.json`. The token list is committed as `scripts/claude-theme-tokens.json`, in the order Claude Code's own presets use. `scripts/validate-claude.mjs` checks:

- the file has only `name`, `base` and `overrides`, with the expected name and base,
- every token in the list is set and none is unknown,
- every value is a colour Claude Code accepts (the same patterns as its loader), and is `#rrggbb` so contrast can be measured,
- the committed file matches the generator,
- about 80 contrast pairs per theme: 4.5:1 for text and glyphs on the variant's surface (neutral 900) and for body text on every tinted background, and `inverseText` on every colour that is filled behind it. A 3:1 floor applies only to deliberately dim elements: borders, the faint `subtle` text, the empty usage meter, the mascot and shimmer animation frames.

## Using the themes inside tmux

Claude Code limits itself to 256 colours when `$TMUX` is set, even if `tmux` and the outer terminal support truecolour. The dark surfaces then round to the nearest entry in the 256-colour cube instead of staying near-black: `#12121a`, the Afterglow prompt background, becomes palette entry 17 (`#00005f`), a saturated navy. Text and accent colours are barely affected, so only the dark surface tokens look wrong.

Set `CLAUDE_CODE_TMUX_TRUECOLOR=1` to keep truecolour inside `tmux`, for example in your shell profile:

```sh
export CLAUDE_CODE_TMUX_TRUECOLOR=1
```

Restart Claude Code afterwards, since it reads the variable at startup. `tmux` itself must pass 24-bit colour through. The `flags=` value on each `Terminal` line of `tmux info` should include `0x10`, and if it does not, add `set -as terminal-features ",*:RGB"` to `~/.tmux.conf` and restart the server. The clamp was read from Claude Code 2.1.284, and the fix was confirmed by eye in `tmux` 3.7c.

## What was verified

Checked against the installed Claude Code 2.1.266 binary and the official documentation at [code.claude.com](https://code.claude.com/docs/en/terminal-config#create-a-custom-theme), which agree:

- **From the binary:** the loader (the `.json` files in the config directory's `themes` folder, the 256 KiB limit, the three fields, the six base names, the default of `dark`, the `custom:` prefix and the file watcher), the colour patterns, the rule that an override only applies if the token exists in the base preset and the colour is valid, and the 72 tokens in each of the six presets. The token list in `scripts/claude-theme-tokens.json` was read from there.
- **From the official docs:** the field table, the colour syntax, the meaning of the documented tokens, and the statement that unknown tokens and invalid colours are ignored. The docs list about 60 tokens and leave out some single-purpose accents (the mascot, the brand marks and the system spinner). Their meanings in the table above come from the names and the community reference.
- **From the community reference** ([the gist](https://gist.github.com/cameronsjo/34a6fb8ade2b44c8380e1a2adebbac2b)) only: the descriptions of the undocumented tokens, and the note that code-block colours cannot be themed. It agrees with the binary on the format and on 72 tokens, though its description line says 69.
- **Loaded by the real binary:** with a scratch `HOME` and `CLAUDE_CONFIG_DIR` under `/tmp` holding the three files, `claude` was started in a pseudo-terminal with no login and no prompt. Its first-run "Choose the text style" picker listed `Afterglow (custom)`, `Afterglow Dark (custom)` and `Afterglow Light (custom)`. Choosing a custom theme there applied it: the screen drew the logo in the accent, the muted text in `inactive`, and the selection marker in the interactive hue (`#a78bfa`, `#8f8da6` and `#60a5fa` for Afterglow Dark, `#ffaa40` for Afterglow). That run exercised the loader and the base-and-overrides application, not every token.

## What was not verified

- Most of the 72 tokens were not seen on screen: a billable session would be needed for the transcript, diffs, plan mode, subagents and the usage meter. Their roles rest on the documentation and the token names. In the picker's own preview, the diff backgrounds were close to, but not exactly, the theme's `diff*` tokens, which was not investigated.
- The light theme was seen in the picker list only, not selected and drawn.
- Nothing was checked by eye in a real terminal session, so colour changes need a look in Claude Code itself.

## Limitations

- **Code blocks are not themable.** Claude Code highlights fenced code with its own syntax theme (the first-run preview shows "Monokai Extended"), not with these tokens. The community reference describes an older fixed ANSI map. Either way, code colours do not follow Afterglow.
- **No transparency**, as above.
- **The format is not versioned.** Tokens are added and removed between releases (the community reference notes one removed in 2.1.140), so refresh `scripts/claude-theme-tokens.json` when Claude Code changes. To list the tokens in a newer binary, extract its strings and look for the object that holds `autoAccept` and `rainbow_violet_shimmer`.
