# ReactOS desktop card art

![A Solitaire table and a two-suit Spider table on the dusk felt at twice their size, with the Afterglow faces: cream cards in a thin gold border, rose hearts and diamonds, dusk-indigo spades and clubs, double-ended courts, the gold ring of the empty deck, an empty foundation drawn from the felt, and the sunset backs on the face-down cards and Spider's stock.](images/afterglow-cards.png)

_Solitaire and Spider Solitaire as cardlib draws them, on the proposed dusk felt, at 2×, the rows stacked by the games' own offsets._

Solitaire and Spider Solitaire share cardlib, which draws every card from `cards.dll`: 52 faces, a free-cell card, twelve backs, a joker and two empty-pile marks, all 72 × 112 and 8-bit. The back both games start with is bitmap 54 (`Background_1`, cardlib's `nBackCardIdx` 53), and it is the only back that carries the ReactOS logo; the other eleven backs are neutral patterns and stay as they are. The faces, the free-cell card and the joker are redrawn in Afterglow. The table's green is a colour compiled into both games. Which resource and which instruction hold each, and how they were found, is in [the stock art survey](reactos-stock-art-survey.md#full-image-extras).

## The art

| Master                               | Bitmap                      | Replaces                                                   | What it is                                                                                                                                                                                         |
| ------------------------------------ | --------------------------- | ---------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `card-back-sunset.svg`               | `card-back-sunset.bmp`      | `cards.dll` 54 (`Background_1`), 72 × 112                  | The Afterglow sun half risen on a gold horizon under the dusk arcs, in the boot logo's language, a few stars, and the water with the sun's glints, in a thin gold border on a white card. Selected |
| `card-o.svg`                         | `card-o.bmp`                | `cards.dll` 68 (`OSign`, cardlib's `CS_EI_CIRC`), 72 × 112 | A gold ring on the dusk felt: Solitaire's empty deck, which deals again when clicked                                                                                                               |
| `card-x.svg`                         | `card-x.bmp`                | `cards.dll` 67 (`XSign`, cardlib's `CS_EI_X`), 72 × 112    | A rose cross on the dusk felt                                                                                                                                                                      |
| `faces/NN-<suit>-<rank>.svg` (52)    | `card-NN-<suit>-<rank>.bmp` | `cards.dll` 1 to 52, 72 × 112                              | The faces, "Classic dusk". Selected. See [the faces](#the-faces)                                                                                                                                   |
| `faces/53-free-cell.svg`             | `card-53-free-cell.bmp`     | `cards.dll` 53 (`FreeCard`), 72 × 112                      | An empty cell: no index, a dashed inner frame and the Afterglow sun half risen on a gold horizon under the dusk arcs, in a gold medallion                                                          |
| `faces/66-joker.svg`                 | `card-66-joker.bmp`         | `cards.dll` 66 (`Joker`), 72 × 112                         | A double-ended jester in the courts' panel, with JOKER down the left margin and turned at the right                                                                                                |
| `alternatives/card-back-lattice.svg` | not rendered                | nothing                                                    | Review only: a dusk lattice with small gold suns at the crossings and a sun medallion                                                                                                              |
| `alternatives/card-back-rays.svg`    | not rendered                | nothing                                                    | Review only: the whole sun at the centre of a violet-to-rose sky, its rays reaching the border, the same either way up                                                                             |

The backs keep a white margin and a thin gold border, so a face-down card reads on the dark felt and the edges of a stacked pile (Spider's stock, Solitaire's deck) show as white and gold slivers rather than as the stock logo's. The colours are set E's (`desktop/icons/gen_e.py`): the sky ramp, the horizon, the sun's orange and the brand gold.

## The faces

The faces are drawn by `desktop/cards/faces/gen_faces.py` (the shared parts in `faces.py`, the set in `classic.py`) on a cream face (`#fbfaf6`) with a thin gold border (orange 300) on the third pixel ring, inside cardlib's black line.

- **Index.** Every face carries its rank and small suit side by side at the top left (rows 4 to 12) and the same turned half a turn at the bottom right, as a traditional deck does. cardlib stacks Solitaire's rows 16 pixels apart (`__cardheight / 6.7`) and Spider's 17 (`__cardheight / 6.4`), so the top-left index is what shows of a covered card; Solitaire fans its waste 12 columns apart (`CS_DEFXOFF`), where the rank shows; the top card of a pile shows whole, with both. The ranks are a bold 9-pixel bitmap font and the small suits 9 × 9 bitmaps, hinted by hand, so they are exact at 1×. `render-cards.test.mjs` checks the two corners are the same pixels on all 53 cards that have an index.
- **Suits.** Hearts and diamonds are rose (red 300, `#c9354e`, 4.9:1 on the face), spades and clubs dusk indigo (sky 1, `#1f2554`, 13.9:1): two colours, as traditional. They differ in lightness as well as hue, and the four shapes differ by silhouette, so red and black stay apart for deuteranopia, protanopia, tritanopia and in greyscale (the contact sheet shows Machado 2009 simulations).
- **Pips and aces.** The pips stand in the traditional patterns, the lower half turned. An ace is its suit large in a thin gold sun ring.
- **Courts.** A king with a rising-sun crown and a beard, a queen with a tiara, a jack with a feathered cap, each in a robe of the suit's colour with a gold collar and a small suit on the chest, in a framed panel, double-ended about a gold horizon line. The three figures are drawn once and coloured by suit.
- **Joker and free cell.** The joker is a jester in a rose-and-indigo cap with sun bells, a gold ruff, a harlequin doublet and a marotte, double-ended like the courts. The free-cell card has no index or suit, so it never reads as a playing card, and it is light, so it never reads as a back: a dashed inner frame and a gold medallion with the sun half risen on the horizon under the dusk arcs.

Two review-only alternatives, "Horizon" (pips on a dawn sky, the courts as the crowned sun, the moon and the evening star over the water) and "Pixel set E" (hand-hinted pixel pips in the icon set's materials, the courts as icon tiles), are in `desktop/cards/alternatives/faces`. Their SVGs are not committed: `gen_faces.py --alternatives OUT_DIR` writes them and `desktop/cards/alternatives/faces/SHA256SUMS` holds their hashes. `faces/render_sheets.py OUT_DIR` draws the contact sheets (the representative cards at 1×, 2× and 4× on the dusk felt and the stock green, the corners, Solitaire and Spider tables, colour-blind simulations) and an overview of the three; the copies in `faces/sheets` and `alternatives/faces/sheets` are the review images, and `faces/README.md` compares the sets.

## The felt

cardlib paints the table `PALETTERGB(0, 80, 0)`, a constant in `CardWindow`'s constructor (`cardwindow.cpp`), and draws the empty-pile sinks from it (`CreateSinkBmp`: a checker of the felt and a step toward white, with a darker rim). It is code, not a resource: the immediate of `mov dword [ebx+0x144], 0x02005000` in `sol.exe` (file offset `0x73c5`) and `spider.exe` (`0x5e09`) of the stock 0.4.16 i386 files. The proposed Afterglow felt is the dusk sky's deepest tone, `#1f2554`, written as `1f 25 54 02` over `00 50 00 02` at those offsets; the sinks follow it with no other change. The stock ring and cross carry the stock green around their mark (`RGB(0, 128, 0)`), so they are redrawn on the dusk felt and go with the felt patch. `#42396c` (the sky's fourth step) was the other felt reviewed; it is lighter, so the sinks show more, but the white cards stand out less. `map.json`'s `colours` list records the felt and both sites.

## Branding

The backs carry no ReactOS logo: the stock back that did is the one replaced, and the remaster's credit to ReactOS stays where it belongs, in the About banner. All the card art, faces included, is drawn here from shapes defined in the generators; the stock faces were looked at for their index placement only, and no pixel of them is used (see `desktop/PROVENANCE.md`).

## The render

`desktop/cards/render.py OUT_DIR` draws each master (the back, the marks and the 54 faces) with `rsvg-convert` at four times the bitmap and averages every 4 × 4 block into one pixel, then writes a 24-bit uncompressed bottom-up BMP with no dates, pixel density or colour profile. The stock bitmaps are 8-bit; cardlib copies each one into a screen-compatible bitmap with `BitBlt`, so a 24-bit bitmap of the same size draws the same way. It also writes `afterglow-cards-preview.png`, the picture at the top of this page: a Solitaire table (`solcreate.cpp`'s borders, the waste fanned by 12 columns, rows stacked by 16 pixels, face-down cards included) and a two-suit Spider table (`spigame.cpp`'s layout, 17 pixels), with cardlib's black border, its cut corners and its sinks drawn as cardlib draws them. Needs `rsvg-convert` and Pillow. `bun run check:desktop` checks:

- **Masters.** `desktop/cards/SHA256SUMS.masters` holds the hashes of the masters, of `gen_cards.py` and `render.py`, and of the face generators; the faces are also written again and compared with the committed ones, and the alternatives with `alternatives/faces/SHA256SUMS`.
- **Renders.** `desktop/cards/SHA256SUMS` holds the hashes of the 57 BMPs, rendered fresh.
- **Preview.** `images/afterglow-cards.png` is compared by pixels with a fresh render.

## Changing a master

The masters are written by the generator, never by hand:

```sh
python3 desktop/cards/gen_cards.py desktop/cards
python3 desktop/cards/faces/gen_faces.py desktop/cards/faces
(cd desktop/cards && { sha256sum card-back-sunset.svg card-x.svg card-o.svg alternatives/card-back-lattice.svg alternatives/card-back-rays.svg gen_cards.py render.py; sha256sum faces/*.svg; sha256sum faces/faces.py faces/classic.py faces/gen_faces.py faces/render_sheets.py alternatives/faces/horizon.py alternatives/faces/pixel.py; } > SHA256SUMS.masters)
python3 desktop/cards/faces/gen_faces.py --alternatives desktop/build/card-faces-alternatives
(cd desktop/build/card-faces-alternatives && sha256sum horizon/*.svg pixel/*.svg) > desktop/cards/alternatives/faces/SHA256SUMS
python3 desktop/cards/render.py desktop/build/cards
(cd desktop/build/cards && sha256sum card-back-sunset.bmp card-x.bmp card-o.bmp && sha256sum card-[0-9]*.bmp) > desktop/cards/SHA256SUMS
cp desktop/build/cards/afterglow-cards-preview.png docs/images/afterglow-cards.png
```

## Patching it in

Nothing here changes a ReactOS file. The reactos-liminal build writes the 57 bitmaps into `cards.dll` from `desktop/icons/map.json`'s `bitmaps` list (each entry names the resource id; cardlib loads face `suit * 13 + rank` into its own index `(rank - 1) * 4 + suit`, and the other bitmaps in resource order; each 24-bit bitmap is larger than the 8-bit one it replaces, so it goes in a new section, as the icon patches do) and the felt into `sol.exe` and `spider.exe` from its `colours` list.
