# ReactOS desktop card art

![The Solitaire table on the dusk felt at twice its size: the deck with the Afterglow sunset back, the gold ring of the empty deck, four empty foundation piles drawn from the felt colour, seven tableau columns of face-down sunset backs, and the rose cross mark at the right.](images/afterglow-cards.png)

_Solitaire's table as cardlib draws it, on the proposed dusk felt, at 2×. The card faces are ReactOS's own and are left out._

Solitaire and Spider Solitaire share cardlib, which draws every card from `cards.dll`: 52 faces, a free-cell card, twelve backs, a joker and two empty-pile marks, all 72 × 112 and 8-bit. The back both games start with is bitmap 54 (`Background_1`, cardlib's `nBackCardIdx` 53), and it is the only back that carries the ReactOS logo; the other eleven backs are neutral patterns and stay as they are, and so do the faces, which are the games' own art. The table's green is a colour compiled into both games. Which resource and which instruction hold each, and how they were found, is in [the stock art survey](reactos-stock-art-survey.md#full-image-extras).

## The art

| Master                               | Bitmap                 | Replaces                                                   | What it is                                                                                                                                                                                         |
| ------------------------------------ | ---------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `card-back-sunset.svg`               | `card-back-sunset.bmp` | `cards.dll` 54 (`Background_1`), 72 × 112                  | The Afterglow sun half risen on a gold horizon under the dusk arcs, in the boot logo's language, a few stars, and the water with the sun's glints, in a thin gold border on a white card. Selected |
| `card-o.svg`                         | `card-o.bmp`           | `cards.dll` 68 (`OSign`, cardlib's `CS_EI_CIRC`), 72 × 112 | A gold ring on the dusk felt: Solitaire's empty deck, which deals again when clicked                                                                                                               |
| `card-x.svg`                         | `card-x.bmp`           | `cards.dll` 67 (`XSign`, cardlib's `CS_EI_X`), 72 × 112    | A rose cross on the dusk felt                                                                                                                                                                      |
| `alternatives/card-back-lattice.svg` | not rendered           | nothing                                                    | Review only: a dusk lattice with small gold suns at the crossings and a sun medallion                                                                                                              |
| `alternatives/card-back-rays.svg`    | not rendered           | nothing                                                    | Review only: the whole sun at the centre of a violet-to-rose sky, its rays reaching the border, the same either way up                                                                             |

The backs keep a white margin and a thin gold border, so a face-down card reads on the dark felt and the edges of a stacked pile (Spider's stock, Solitaire's deck) show as white and gold slivers rather than as the stock logo's. The colours are set E's (`desktop/icons/gen_e.py`): the sky ramp, the horizon, the sun's orange and the brand gold.

## The felt

cardlib paints the table `PALETTERGB(0, 80, 0)`, a constant in `CardWindow`'s constructor (`cardwindow.cpp`), and draws the empty-pile sinks from it (`CreateSinkBmp`: a checker of the felt and a step toward white, with a darker rim). It is code, not a resource: the immediate of `mov dword [ebx+0x144], 0x02005000` in `sol.exe` (file offset `0x73c5`) and `spider.exe` (`0x5e09`) of the stock 0.4.16 i386 files. The proposed Afterglow felt is the dusk sky's deepest tone, `#1f2554`, written as `1f 25 54 02` over `00 50 00 02` at those offsets; the sinks follow it with no other change. The stock ring and cross carry the stock green around their mark (`RGB(0, 128, 0)`), so they are redrawn on the dusk felt and go with the felt patch. `#42396c` (the sky's fourth step) was the other felt reviewed; it is lighter, so the sinks show more, but the white cards stand out less. `map.json`'s `colours` list records the felt and both sites.

## Branding

The backs carry no ReactOS logo: the stock back that did is the one replaced, and the remaster's credit to ReactOS stays where it belongs, in the About banner.

## The render

`desktop/cards/render.py OUT_DIR` draws each master with `rsvg-convert` at four times the bitmap and averages every 4 × 4 block into one pixel, then writes a 24-bit uncompressed bottom-up BMP with no dates, pixel density or colour profile. The stock bitmaps are 8-bit; cardlib copies each one into a screen-compatible bitmap with `BitBlt`, so a 24-bit bitmap of the same size draws the same way. It also writes `afterglow-cards-preview.png`, the picture at the top of this page, with cardlib's black border, its cut corners and its sinks drawn as cardlib draws them. Needs `rsvg-convert` and Pillow. `bun run check:desktop` checks:

- **Masters.** `desktop/cards/SHA256SUMS.masters` holds the hashes of the masters and of `gen_cards.py` and `render.py`.
- **Renders.** `desktop/cards/SHA256SUMS` holds the hashes of the three BMPs, rendered fresh.
- **Preview.** `images/afterglow-cards.png` is compared by pixels with a fresh render.

## Changing a master

The masters are written by the generator, never by hand:

```sh
python3 desktop/cards/gen_cards.py desktop/cards
(cd desktop/cards && sha256sum card-back-sunset.svg card-x.svg card-o.svg alternatives/card-back-lattice.svg alternatives/card-back-rays.svg gen_cards.py render.py > SHA256SUMS.masters)
python3 desktop/cards/render.py desktop/build/cards
(cd desktop/build/cards && sha256sum card-back-sunset.bmp card-x.bmp card-o.bmp) > desktop/cards/SHA256SUMS
cp desktop/build/cards/afterglow-cards-preview.png docs/images/afterglow-cards.png
```

## Patching it in

Nothing here changes a ReactOS file. The reactos-liminal build writes the three bitmaps into `cards.dll` from `desktop/icons/map.json`'s `bitmaps` list (each 24-bit bitmap is larger than the 8-bit one it replaces, so it goes in a new section, as the icon patches do) and the felt into `sol.exe` and `spider.exe` from its `colours` list.
