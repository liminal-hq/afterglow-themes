# Icon alternatives (review only)

Nothing in this folder ships. These are alternatives to icons in the Afterglow set, kept for the owner to pick from per icon. They are not in `map.json`, not rendered by `render.py`, not in the release zip and not in the recorded sums. When a pick is made, it moves into the generators (`gen_e.py`, `gen_v2.py`) and the sums are updated there.

`alternatives.py` is the generator: `python3 alternatives.py` rewrites the masters here, and `python3 alternatives.py --review OUT_PNG` renders every frame at 16, 32 and 48 px and draws the review sheet, [`docs/images/afterglow-icons-alternatives.png`](../../../docs/images/afterglow-icons-alternatives.png).

| Folder            | What                                                                                                                                                   |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `device/`         | Redraws of the five icons that show the medium or a part instead of the system item: CD drive, floppy drive, removable drive, RAM disk and My Computer |
| `device-keyline/` | The same five redraws with the keyline                                                                                                                 |
| `keyline/`        | Every icon in the set with the keyline                                                                                                                 |

Each folder holds the 48 px master `ID.svg`, the `32/` and `16/` profiles, and a hand-tuned `ID-16.svg` where the icon has one.

## The keyline

The keyline is set E's own clipped inner edge, made opaque and retuned in each material's hue to a luminance of about 0.137, about 1.5 screen pixels wide at 32 and 16 px. The classic cream window colour has a luminance of about 0.62 and the Dusk desktop about 0.006, and that band is the one that reaches 3:1 against both. Plates get a rim in the same way, a little lighter, because on cream the plate's dark body already carries the contrast. Hinted 16 px frames get the retune on their outer ring of pixels, and Views, Keyboard layout and Folders have hand-tuned 16 px frames, because their scripted frames are too thin to carry it.

## How contrast is measured

WCAG 2 contrast against the ground, at the edge of the icon's main silhouette: the pixels of at least 50 % alpha, so the soft contact shadow is left out. Each pixel on the silhouette's outer ring is scored with the stronger of itself and the pixel just inside it, because an anti-aliased curve leaves the outermost pixel part ground. The icon's score is the median over the ring, and the sheet shows the worst of its 48, 32 and 16 px frames. Every keyline and device-with-keyline alternative reaches 3:1 on both grounds at every size.
