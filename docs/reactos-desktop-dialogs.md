# ReactOS desktop dialog art

![The Afterglow Shut Down and Log Off dialogs and the About banner at twice their size: a dusk header with the sun-on-the-horizon mark at the right and a gold ink line, the grey panel with the violet Sleep, rose Shut Down and gold Restart buttons, the Log Off dialog's disabled Switch User and gold Log Off buttons, and the About banner with the Afterglow wordmark, the unofficial line and the ReactOS copyright over the gold bar.](images/afterglow-dialogs.png)

_The Shut Down and Log Off dialogs as ReactOS assembles them, and the About banner over its bar, at 2×. The dialogs' own words are left out: ReactOS draws them._

The bitmaps of three ReactOS 0.4.16 dialogs that still showed stock art: the About box that every program's Help, About opens (`ShellAbout`), and the Shut Down and Log Off dialogs (the friendly ones with round buttons, which the Start menu opens). Each is drawn here as a vector master and rendered to exactly the size and format of the resource it replaces. Which dialog loads which resource, and why the Shut Down dialog lives in `msgina.dll` itself, is in [the stock art survey](reactos-stock-art-survey.md).

## The art

| Master                                 | Bitmap               | Replaces                                                               | What it is                                                                                                                                                                                                                                                      |
| -------------------------------------- | -------------------- | ---------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `about-banner.svg`                     | `about-banner.bmp`   | `shell32.dll` 131 (`IDB_REACTOS`), 413 × 72, 24-bit                    | Logon banner A's dusk sky, setting sun and Afterglow wordmark, the gold line "for ReactOS · unofficial remaster, not endorsed by the ReactOS project", and "Copyright © 1996-2026 ReactOS Team & Contributors" in the dark band, as the stock banner carries it |
| `../logon/bar.svg`                     | `afterglow-bar.bmp`  | `shell32.dll` 138 (`IDB_LINEBAR`), 413 × 5, 24-bit                     | The logon bar: the stock line under the About banner is byte for byte the logon one                                                                                                                                                                             |
| `shutdown-bg.svg`                      | `shutdown-bg.bmp`    | `msgina.dll` 20003 and `shell32.dll` 500 (`IDI_DLG_BG`), 312 × 198     | The dusk header, a horizon line and the gold ink line, the panel, and the dusk footer, in the stock bitmap's bands                                                                                                                                              |
| `shutdown-mark.svg`                    | `shutdown-mark.bmp`  | `msgina.dll` 20002 and `shell32.dll` 501 (`IDI_ROSLOGO_FLAG`), 48 × 40 | The Afterglow sun half set on a gold horizon under dusk arcs, the boot logo's language, in place of the stock globe                                                                                                                                             |
| `shutdown-strip.svg`                   | `shutdown-strip.bmp` | `msgina.dll` 20004 (`IDB_IMAGE_STRIP`), 33 × 330                       | Ten 33 px buttons in `shutdown.c`'s order: Shut Down (rose, the power mark), Restart (gold, a circular arrow) and Sleep (violet, the moon), each normal, pressed and focused, then Sleep disabled. Selected                                                     |
| `logoff-strip.svg`                     | `logoff-strip.bmp`   | `shell32.dll` 502 (`IDB_IMAGE_STRIP`), 33 × 231                        | Seven buttons in `dialogs.cpp`'s order: Switch User (violet, two arrows) and Log Off (gold, out of the door), normal, pressed and focused, then Switch User disabled                                                                                            |
| `alternatives/shutdown-strip-mint.svg` | not rendered         | nothing                                                                | Review only: the design canvas's friendly-dialog colours, Stand By in mint                                                                                                                                                                                      |

The buttons are set E faces: `gen_dialogs.py` draws each one with the icon set's `Pen` (`desktop/icons/gen_e.py`) at the 32 px profile with the keyline, so the rose, gold and violet are the icon materials and every button reaches 3:1 on the grey panel. Pressed is a step darker and flat with the mark a pixel lower, focused (which the dialog also shows on hover) a step lighter with a pale rim, and disabled greyed.

## What the dialogs fix, and what they leave

- **The panel is RGB(244, 244, 244).** Both dialogs paint their labels on a brush of that grey, and their colours (the title in RGB(244, 244, 244), the labels in RGB(38, 38, 38)) are compiled into the code. So the panel stays exactly that grey, and the header and footer stay dark enough for the light title.
- **The mark sits on the header's own gradient.** The mark is a separate bitmap two pixels below the top, and the wider dialog (with Hibernate) stretches the background but not the mark, so the header is a gentle vertical gradient only and the mark carries its own copy of it.
- **The words stay.** "Shut Down ReactOS", "Log Off ReactOS" and the button labels are the dialog templates' strings; changing them means rebuilding the resource section, not swapping a bitmap.
- **The grey fade behind the dialog is code.** `msgina.dll` blends a capture of the screen toward its luminance in ten steps (`dimmedwindow.cpp`). There is no resource to theme; a dusk-tinted fade would need that loop changed, so it stays.
- **The About text is ReactOS's.** Below the banner the About box writes the program's name, version and copyright in black on the cream face, so the banner carries its own light type on the dark sky, and the copyright line keeps the stock banner's credit to ReactOS.

## Branding

The About banner, like the logon banner, carries no ReactOS logo or wordmark art: it names ReactOS only in plain type, says the remaster is unofficial and not endorsed by the ReactOS project, and keeps the ReactOS copyright line the stock banner carries. Its type is outlined from DejaVu Sans (the DejaVu font licence allows embedding outlines), so it renders without a font. The Shut Down mark is Afterglow's sun, not the ReactOS globe.

## The render

`desktop/dialogs/render.py OUT_DIR` draws each master with `rsvg-convert` at four times the bitmap and averages every 4 × 4 block into one pixel, then writes a 24-bit uncompressed bottom-up BMP with no dates, pixel density or colour profile, the format of every stock bitmap here (none is palettised, so no palette is involved). It also writes `afterglow-dialogs-preview.png`, the picture at the top of this page. Needs `rsvg-convert` and Pillow. `bun run check:desktop` checks:

- **Masters.** `desktop/dialogs/SHA256SUMS.masters` holds the hashes of the masters and of `gen_dialogs.py`, `outline.py` and `render.py`.
- **Renders.** `desktop/dialogs/SHA256SUMS` holds the hashes of the five BMPs, rendered fresh.
- **Preview.** `images/afterglow-dialogs.png` is compared by pixels with a fresh render.

## Changing a master

The masters are written by the generator, never by hand. It needs DejaVu Sans for the banner's type (`DejaVuSans.ttf`; pass its folder if it is not in a usual place):

```sh
python3 desktop/dialogs/gen_dialogs.py desktop/dialogs [FONT_DIR]
(cd desktop/dialogs && sha256sum about-banner.svg shutdown-bg.svg shutdown-mark.svg shutdown-strip.svg logoff-strip.svg alternatives/shutdown-strip-mint.svg gen_dialogs.py outline.py render.py > SHA256SUMS.masters)
python3 desktop/dialogs/render.py desktop/build/dialogs
(cd desktop/build/dialogs && sha256sum about-banner.bmp shutdown-bg.bmp shutdown-mark.bmp shutdown-strip.bmp logoff-strip.bmp) > desktop/dialogs/SHA256SUMS
cp desktop/build/dialogs/afterglow-dialogs-preview.png docs/images/afterglow-dialogs.png
```

## Patching it in

Nothing here changes a ReactOS file. The reactos-liminal build writes the bitmaps into `shell32.dll` and `msgina.dll` from `desktop/icons/map.json`'s `bitmaps` list, which names each module, resource id, size and depth; every replacement is the same size and depth as the stock bitmap, so it can be written in place.
