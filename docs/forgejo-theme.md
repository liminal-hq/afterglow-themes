# Forgejo themes

Afterglow ships four themes for [Forgejo](https://forgejo.org), generated from the same palette as the OpenCode, VS Code, Midnight Commander, Claude Code and TextMate themes, plus an avatar for the instance's own signature.

| Theme             | File                        | Starts from     | What it is                                                                         |
| ----------------- | --------------------------- | --------------- | ---------------------------------------------------------------------------------- |
| `afterglow`       | `theme-afterglow.css`       | `forgejo-dark`  | The `#050507` void for the header, with orange as the primary colour               |
| `afterglow-dark`  | `theme-afterglow-dark.css`  | `forgejo-dark`  | Deep indigo-black, with purple as the primary colour                               |
| `afterglow-light` | `theme-afterglow-light.css` | `forgejo-light` | Warm paper, with deeper purple as the primary colour                               |
| `afterglow-auto`  | `theme-afterglow-auto.css`  | (the two above) | Follows the operating system: `afterglow-light` in light mode, `afterglow` in dark |

`afterglow` is the signature dark theme, as in every other Afterglow target, so it does not follow the system. `afterglow-auto` is the one that does, the way Forgejo's own `forgejo-auto` does.

## How a Forgejo theme works

A theme is a CSS file named `theme-<name>.css` in `public/assets/css/` of Forgejo's custom directory (`/data/gitea` in the container image). The names a person can choose come from the `THEMES` setting under `[ui]` in `app.ini`, and `DEFAULT_THEME` sets the one new visitors and signed-out pages get. Forgejo's interface is drawn from CSS variables on `:root`, so a theme is a list of variables.

Each Afterglow theme starts with `@import` of Forgejo's own `theme-forgejo-dark.css` or `theme-forgejo-light.css`, and then overrides the variables it recolours. Everything it does not touch (syntax highlighting, diff and alert colours, badges, the console colours) stays as Forgejo draws it, and a Forgejo upgrade that adds a variable does not leave the theme with a hole in it. `scripts/forgejo-theme-variables.json` holds the variables of both Forgejo themes (read from Forgejo 16.0.3), so the validator can reject a misspelt name, which Forgejo would silently ignore, and resolve any `var()` reference to measure contrast.

## What the themes set

| Variables                      | Dark themes                                                                                                 | Light theme                                                                                          |
| ------------------------------ | ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| The grey ramp                  | `--steel-100` to `--steel-900` (and the half steps) from the variant's neutral ramp, step for step          | `--zinc-50` to `--zinc-900`, with the page itself on neutral 900 and boxes one step darker           |
| `--color-primary` and its ramp | The variant's accent: links, buttons, the active tab. `--color-primary-dark-N` lightens, `-light-N` darkens | The same, the other way round, with `--color-primary-contrast` the page colour for text on a fill    |
| `--color-text`                 | The brand text colour `#e0e0e0`                                                                             | The ramp's darkest step                                                                              |
| The page, inputs and toggles   | From the steel ramp                                                                                         | `--color-body`, `--color-input-background` and the toggle on neutral 900, which Forgejo paints white |

The accent is orange for `afterglow` and purple for the others, the same hue Claude Code uses for its brand marks.

## Installing

Download `afterglow-forgejo-vX.Y.Z.zip` from the [releases page](https://github.com/liminal-hq/afterglow-themes/releases), or run `bun run install:forgejo -- --custom <dir>` from a checkout, which copies the files into `<dir>/public/assets/css/`. Then add the themes to `app.ini`:

```ini
[ui]
THEMES = forgejo-auto,forgejo-light,forgejo-dark,afterglow-auto,afterglow,afterglow-dark,afterglow-light
; DEFAULT_THEME = afterglow-auto
```

Restart Forgejo, then choose the theme under **Settings > Appearance**. Leave `DEFAULT_THEME` alone unless every person on the instance should get Afterglow without choosing it.

## The instance avatar

Commits that Forgejo signs itself, such as the merge a pull request makes, show "Signed by:" with the instance's signing name and an avatar. Forgejo has no setting for that avatar: it draws it from the hash of the signing email (`SIGNING_EMAIL` under `[repository.signing]`), which falls through to a Gravatar identicon or its default picture. `forgejo/avatar/forgejo-instance.svg` is an Afterglow picture for it: the app icon's dark tile and brand gradient around a git merge mark, with the nodes filled orange.

`bun run install:forgejo -- --custom <dir> --signing-email <address>` copies the picture to `<dir>/public/assets/img/` and writes `<dir>/templates/custom/extra_links.tmpl`, a stylesheet that swaps the picture in for requests carrying that address's hash. It matches both the MD5 and the SHA-256 forms of the hash, because Forgejo's avatar endpoint accepts both. The installer leaves an existing `extra_links.tmpl` alone unless Afterglow wrote it (the file says so in a comment). Forgejo reads templates when it starts, so restart it after installing.

## What was verified

- **Loaded on a real Forgejo 16.0.3:** `afterglow` and `afterglow-light` were applied to the sign-in page of a running instance (as a stylesheet injected into the page, importing the instance's own base themes), in a real browser, and looked at. The dark theme drew the near-black header and indigo-black page with an orange primary button and focus ring. The light theme drew warm paper with a purple primary button. The variable names, and what each one is for, were read from the themes in the Forgejo binary.
- **Contrast:** `scripts/validate-forgejo.mjs` resolves every variable through the base theme and checks the text, secondary text, placeholder and primary colours on the page, header, boxes, menus, cards, inputs and code blocks at 4.5:1, plus text on primary fills and on hover.

## What was not verified

- **Signed-in pages.** Repository pages, diffs, pull requests, issues, labels and settings were not seen with the themes applied, so the greys Forgejo derives from the primary colour (hover rows, highlighted lines, the alpha tints) are untested by eye. `afterglow-dark` and `afterglow-auto` were not drawn.
- **The `THEMES` setting end to end**, including how Forgejo labels the theme in the picker.
- **The avatar template on a commit page.** The avatar endpoint was seen to accept both hash forms, but which one a commit page links to was not seen without signing in.

## Limitations

- **Syntax colours do not follow Afterglow.** The Forgejo themes colour highlighted code with their own palette, and these themes keep it.
- **Forgejo's variables are not versioned.** `scripts/forgejo-theme-variables.json` was read from Forgejo 16.0.3. A theme still works on a later release (it imports whatever base the instance ships), but a renamed variable stops being recoloured, so refresh the file when Forgejo changes: extract `public/assets/css/theme-forgejo-dark.css` and `theme-forgejo-light.css` with `forgejo embedded extract` and read their `:root` blocks.
