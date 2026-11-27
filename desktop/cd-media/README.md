# Afterglow for ReactOS CD media

The generator, masters and print render for the Afterglow for ReactOS install and live CD: the disc art (three compositions, B · Halo selected), a full-face CD label, the jewel case front insert and back tray card, and a mock-up. The full specification, the wording rules and how to print are in [`docs/cd-media.md`](../../docs/cd-media.md).

## Two styles

Every piece is drawn twice, under the same file names, in the styles the desktop wallpapers use:

- **`stepped/`**: flat bands of the boot logo's colours, the retro 16 and 256 colour look. The PDFs are vector throughout. Print it for an old-school look, or on a printer with few colours or one that bands gradients.
- **`smooth/`**: the same colours as continuous gradients, with a soft glow round the sun. In the PDFs each sky is a 300 dpi image with a little seeded noise, so it cannot band on paper, under vector text, shapes and clips. Print it for photo-quality output, and use it on screens.

Only the sky differs between the two; the test checks that the rest of each master is identical.

## Files

| File                  | What                                                                                                                                                          |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gen_media.py`        | The generator: edit it, never a master. `--style stepped` or `--style smooth` draws one style; without it, both                                               |
| `render.py`           | Lays the masters out on print pages and writes the PDFs and previews of each style to `OUT_DIR/stepped/` and `OUT_DIR/smooth/`                                |
| `stepped/`, `smooth/` | The SVG masters: `disc.svg`, `alternatives/disc-sunrise.svg`, `alternatives/disc-horizon.svg`, `label.svg`, `jewel-front.svg`, `jewel-back.svg`, `mockup.svg` |

```sh
python3 desktop/cd-media/gen_media.py desktop/cd-media   # both styles' masters (needs Noto Sans)
python3 desktop/cd-media/render.py dist/cd-media         # both styles' PDFs and previews, and stepped-vs-smooth.png
node --test scripts/render-cd-media.test.mjs
```
