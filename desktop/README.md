# Afterglow for the ReactOS desktop

The generator for the Afterglow visual style for ReactOS 0.4.16: dusk captions, a near-black taskbar with a gold Start button, rose and gold accents, classic cream client areas and classic Windows scroll bars (the Afterglow scroll bars are built on request with `--scrollbars`). It holds eight colour schemes (Dusk, the default, Ember, Aurora, Graphite and a light version of each) in the Normal size. Every bitmap is drawn by `style/agart.py` from the palette table in `style/agdraw.py` and the style INI is written by hand in `style/ini/normal.ini`. See `docs/reactos-desktop-colour-schemes.md` for the schemes and how to apply them, and `PROVENANCE.md` for how each part was made (no Lunar, Mizu, Blackshade or other style's files were used).

## Files

| Path                                        | What                                                                                                                                                                    |
| ------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `style/agdraw.py`                           | The palette, the colour scheme table (`SCHEMES`), `use_scheme()`, a small pixel canvas and a BMP writer                                                                 |
| `style/agart.py`                            | Every bitmap: captions, frames, caption buttons, scroll bars (Afterglow and classic), dialog controls, bars, the taskbar, the Start button and the tray                 |
| `style/ini/normal.ini`                      | The style INI, written once for every scheme; `{tokens}` are the scheme's palette colours. Its `[Scrollbar.*]` sections are the Afterglow scroll bars (`--scrollbars`)  |
| `style/ini/scroll-classic.ini`              | The default `[Scrollbar.*]` sections: classic Windows scroll bars                                                                                                       |
| `style/gen.py`                              | Draws each scheme's bitmaps, fills the INI, checks every image is named and used, checks 4.5:1 title contrast, writes the `.reg` files, `themes.ini` and `afterglow.rc` |
| `style/build.sh`                            | `gen.py`, then `llvm-rc` and `lld-link /Brepro` into a resource-only x86 DLL; `--schemes` refreshes the `.reg` files, `--scrollbars` themes the scroll bars             |
| `schemes/*.reg`, `schemes/apply-scheme.cmd` | One generated registry file per scheme, and a script that imports one                                                                                                   |
| `install/afterglow-original.reg`            | Selects the style (Dusk) and sets the caption metrics                                                                                                                   |
| `SHA256SUMS`                                | The hashes of the default build (731,136 bytes) and of the `--scrollbars` build (824,320 bytes)                                                                         |

## Build and check

Needs Python 3 with numpy, `llvm-rc` and `lld-link` (LLVM). Pillow is only needed for the optional contact sheet (`PREVIEW=sheet.png`).

```sh
bash desktop/style/build.sh desktop/build            # the style is desktop/build/afterglow.msstyles
bash desktop/style/build.sh desktop/build --schemes  # also refreshes desktop/schemes/*.reg
bash desktop/style/build.sh desktop/build --scrollbars  # the Afterglow scroll bars instead of the classic ones
bun run check:desktop                                # rebuild both, then compare with SHA256SUMS and schemes/*.reg
```

The built style stays out of git (`desktop/build/` is ignored); the build is reproducible (`/Brepro`), so the same sources give the same bytes and `SHA256SUMS` is the record. The `check:desktop` script is not part of `bun run validate` because it needs the LLVM tools.

## Scroll bars

The default style draws classic Windows scroll bars; `--scrollbars` builds the Afterglow ones (dusk thumbs, gold hot states) from the same generator, with `SHA256SUMS` recording both builds. `uxtheme` has no classic fallback for a window's own scroll bars (without a `SCROLLBAR` class a themed window gets no arrow buttons and its thumb leaves trails), so the default build carries a classic-looking class instead: `style/ini/scroll-classic.ini` and the `classic_*` drawing in `style/agart.py`. See `docs/reactos-desktop-colour-schemes.md`.

## Not yet here

The Afterglow pointer set and the tool that patches it into ReactOS's `user32.dll` are a separate change.
