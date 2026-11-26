# ReactOS desktop icons

![The Afterglow icon sheet: the construction keylines and depth anatomy, proof strips at 48, 32, 24 and 16 px on a dark, a cream and a dusk ground, state variants, the hinted 16 px redraws, then all 69 icons in their eight groups.](images/afterglow-icons.png)

_The contact sheet, rendered from the vector masters._

The Afterglow icon set for ReactOS: 69 icons in eight groups (desktop and shell, Control Panel applets, Explorer toolbar, drives and folders, file types, dialogs, system tray and the Start menu), drawn on a 48 px grid as vector masters and rendered down by script to 16, 24, 32 and 48 px. This is the variant of the set called D, best practice in light 3D. Quill's own icons are not part of it.

## Design rules

**The base.** Every icon is drawn once on a 48 px grid inside a 4 px live area, on keyline shapes (square 36, circle 40, portrait 32 × 40, landscape 40 × 32). Each object has one 2 px navy outline, outer corners of 2 px, inner corners of 1 px and a dusk plate with 8 px corners only for apps and applets. Nine colours come from the Afterglow tokens: gold is the one accent and fill, rose appears only for delete, error and shut down, and shape rather than colour carries meaning, so the dialog badges differ in shape. The navy outline and light bodies read on the dark desktop, on cream windows and on the taskbar.

**The depth.** One light sits at the upper left for every icon. Solid bodies (folders, documents, drives, monitors, bins) get a two-stop ramp, a 1 px lit edge on their top and left, a slim extrusion 4 px down and 2 px right and a soft contact shadow. Symbols such as the dialog badges, the CD and the toolbar glyphs only lift, with the ramp and a lighter shadow but no extrusion, and the stroke-only marks (Delete, Undo, Shut Down) stay flat. Depth degrades by rule: at 24 px it halves to whole pixels and drops the lit edge, and at 16 px it is a 1 px lower-right step. Nothing is glossy or translucent, and the contact shadow is the only alpha.

## Sizes and the render

Every icon ships at 16, 24, 32 and 48 px, drawn from the master built for that size:

| Size  | Drawn from                                                                                       |
| ----- | ------------------------------------------------------------------------------------------------ |
| 48 px | `svg/ID.svg`, the master                                                                         |
| 32 px | the same master, scaled                                                                          |
| 24 px | `svg/24/ID.svg`, the 24 px profile (depth halved to whole pixels)                                |
| 16 px | `svg/ID-16.svg`, the hinted redraw, for the eight icons that have one; otherwise `svg/16/ID.svg` |

The hinted 16 px redraws are folder, document, warning, error, hard disk, My Computer, the full Recycle Bin and search. `desktop/icons/render.py OUT_DIR` runs `rsvg-convert` on each and writes `png/ID-SIZE.png` (276 files) and one `ico/ID.ico` per icon (69 files). An `.ico` holds the four frames, smallest first, as uncompressed 32-bit DIB frames with alpha and an all-zero AND mask: the classic layout that old icon loaders read, with no PNG-compressed frames. The output has no dates, so the same masters and the same `rsvg-convert` give the same bytes. The `.ico` bytes were identical with `rsvg-convert` 2.58 and 2.63; the PNG files are written as `rsvg-convert` makes them and are not hashed. The files are named by the icon ids, so a build recipe can pick `ico/folder.ico` by id. The `.ico` hashes are in `desktop/icons/SHA256SUMS`, and `bun run check:desktop` renders them again and compares.

```sh
python3 desktop/icons/render.py desktop/build/icons    # ico/, png/ and afterglow-icons-sheet.png
```

## The map

[`map.json`](../desktop/icons/map.json) lists every icon id with its label, its group and what it replaces in ReactOS. A `status` of `named` means the sheet or the plan names the ReactOS object (the shell folders and drives, the four message box icons, the 19 Control Panel applets, the Start menu entries and the main file types); `unmapped` means no ReactOS counterpart is named yet (the toolbar glyphs, the tray icons, Applications Manager, Internet Browser, Command Prompt, Read Me and Security). The `resource` of every icon is `null`: the module and resource id, or the registry `DefaultIcon` key, is filled in only once it has been checked against ReactOS 0.4.16, and none of them has been, so none is guessed. The build that applies the icons is the reactos-liminal one, and which resources it patches, or whether a registry override reaches them, is decided there.

## Vector masters

All the art is vector. `desktop/icons/gen_d.py` is the canonical source: it draws every icon and the sheet, and writes `icons/` (the 48 px masters, the `24/` and `16/` profiles and the hinted `ID-16.svg` redraws, 215 files) and `sheet.svg`. The committed [`desktop/icons/svg/`](../desktop/icons/svg/) and `desktop/icons/sheet.svg` are its output, kept so the masters can be opened and diffed without running anything. Edit the generator, not the SVGs: `bun run check:desktop` regenerates them and fails when they differ from the committed files, and `desktop/icons/SHA256SUMS.masters` records their hashes. Rasters are always rendered from the masters and never edited by hand.

```sh
python3 desktop/icons/gen_d.py OUT_DIR    # writes OUT_DIR/icons/ and OUT_DIR/sheet.svg
cp -r OUT_DIR/icons/. desktop/icons/svg/ && cp OUT_DIR/sheet.svg desktop/icons/sheet.svg
(cd desktop/icons && find svg -type f | LC_ALL=C sort | xargs sha256sum > SHA256SUMS.masters && sha256sum sheet.svg gen_d.py >> SHA256SUMS.masters)
```

The sheet's text uses whatever sans-serif the renderer finds, so the contact sheet PNG in `docs/images/` is a picture for the docs and is not compared byte for byte.

## Licence

The art, the generator and the renderer are original to this repository and licensed Apache-2.0 OR MIT, (c) Copyright 2026 Liminal HQ, Scott Morris, like the rest of it (`LICENSE-APACHE`, `LICENSE-MIT`); each SVG carries the header. No ReactOS, Windows or third-party icon was copied, traced or recoloured. The design follows public guidance (Microsoft Learn's app icon design and construction pages, Fluent 2's iconography notes) for grids, radii, sizes and light direction, and nothing from them is reproduced. ReactOS itself is GPL and LGPL code: the icons are separate files, and this repository does not ship a patched ReactOS binary.
