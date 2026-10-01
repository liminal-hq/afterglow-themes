# Theme format and design notes

Afterglow targets the OpenCode V2 theme format, documented at [opencode.ai/v2/docs/cli/theme](https://opencode.ai/v2/docs/cli/theme). This page records how the palette becomes OpenCode tokens and why the themes make the choices they do.

## Structure

A theme file has a shared `base` token tree and at least one mode (`light` or `dark`). Each mode supplies the hue palette and can override any part of the base.

- **Hues** are nine-step ramps (`100` to `900`) for `gray`, `red`, `orange`, `yellow`, `green`, `cyan`, `blue` and `purple`, plus the aliases `accent` and `interactive` and an explicit `neutral` ramp. Dark modes run light (`100`) to dark (`900`). Light modes run dark (`100`) to light (`900`). This keeps token references such as `$hue.neutral.200` meaning "readable text" in either mode.
- **The brand colour sits on step `200`** of every hue, matching OpenCode's built-in themes. Steps `300` to `900` fade towards the background and `100` lifts towards white (dark) or black (light).
- **Tokens** are grouped as `text`, `background`, `border`, `scrollbar`, `diff`, `syntax` and `markdown`. Actions and form fields take optional `$hovered`, `$focused`, `$pressed`, `$selected` and `$disabled` states, and unspecified states fall back to `base`.
- **`@dialog`** overrides tokens for dialogs, menus and toasts only.

The step conventions the generator follows, so a token means the same thing in all three themes:

| Use                                      | Step                   |
| ---------------------------------------- | ---------------------- |
| Body text                                | `neutral.200`          |
| Muted text                               | `neutral.300`/`400`    |
| Borders and scrollbars                   | `neutral.600`          |
| Background and raised surfaces           | `neutral.900` to `600` |
| Hue text (syntax, feedback)              | `200`                  |
| Subtle fills (actions, diff backgrounds) | `700` and `800`        |

## Derived styling

OpenCode derives its code-highlighting scopes from these tokens rather than exposing them separately. Some of the useful consequences:

- `variable.builtin` and `tag` use `text.feedback.error.base`, and `attribute` uses `text.feedback.warning.base`.
- `@mention` highlights for agents use the first entry of `categorical`.
- The paste and file chips in the prompt use `text.feedback.warning.base` as their background, with `text.action.primary.$focused` as the text.

Individual UI components such as the transcript, prompt box, sidebar and status bar have no tokens of their own. They draw from the groups above.

## Design decisions

- **Transparency.** The `afterglow` theme sets `background.base` to `transparent` and gives the raised surfaces a solid tone, because OpenCode flattens alpha over black instead of blending with the terminal. `raised.base` must never be `transparent`, since the prompt chip labels take that colour. Dialogs get a near-opaque surface through `@dialog` so they stay readable over any terminal background.
- **The warning chip.** The prompt chips share `text.feedback.warning.base` with warning text, so the colour has to work as both a background and a foreground. On the dark themes it is a muted gold (`yellow.400`) that keeps 5.2:1 contrast as text. On the light theme, warning text must stay a deep gold to read on paper, so the focused primary action pairs light text with a mid-blue fill instead.
- **Accents.** `afterglow` uses orange as its accent and purple as its interactive colour. `afterglow-dark` and `afterglow-light` swap to a purple accent with blue interactive colour.
- **Contrast.** `scripts/validate-themes.mjs` requires 4.5:1 for body and muted text, action text, feedback text, and the main syntax and Markdown colours. The transparent theme is checked against the brand void.

## Changing the palette

Edit `scripts/palette.mjs` (brand colours, deeper light-mode variants, neutral ramps) or the token mapping in `scripts/build.mjs`, then run `bun run build` and `bun run validate:themes`. Commit the regenerated `themes/*.json` with the change. CI fails if the committed files differ from what the palette generates.
