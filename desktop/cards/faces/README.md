# Card faces: three proposed directions

Solitaire and Spider Solitaire draw their faces from `cards.dll`: 52 faces (bitmaps 1 to 52, suit order clubs, diamonds, hearts, spades, ace to king), `FreeCard` (53) and the Joker (66), all 72 × 112. These are proposals for redrawing them in Afterglow. Nothing here is shipped or patched yet: `render.py`, its hashes and the selected sunset back are untouched, and the back stays `card-back-sunset`.

## What every direction keeps

- **cardlib's geometry.** cardlib paints a black line over each card's outer pixel ring with the corners cut, overlaps Solitaire's rows by 16 pixels (`__cardheight / 6.7`), Spider's by 17 (`__cardheight / 6.4`), and fans Solitaire's waste by 12 columns (`CS_DEFXOFF`). So the index (rank and small suit side by side) sits in rows 4 to 12 at the top left, and the rank alone fits in the left 12 columns, as on the stock faces.
- **A hand-hinted index.** The ranks are a bold 9-pixel bitmap font with two-pixel stems, and the small suits are 9 × 9 bitmaps, both drawn by hand in `faces.py`, so they are exact at 1x. The joker's `JOKER` runs down the left margin in the same font.
- **Suit colours.** Hearts and diamonds are rose (`#c9354e`, red 300, 4.9:1 on the cream face), spades and clubs dusk indigo (`#1f2554`, sky 1, 13.9:1). They differ in lightness as well as hue, so red and black stay apart in the deuteranopia, protanopia, tritanopia and greyscale simulations on every sheet; the four suits also differ by silhouette. Measured through the simulations, the rose-to-indigo contrast is 3.4:1 (deuteranopia), 2.0:1 (protanopia, where the hue difference, olive against navy, carries the rest) and 2.8:1 (tritanopia).
- **A cream face with a thin gold border**, as the sunset back has a white margin and a gold line.
- **Spider.** The one-suit deck is all spades and the two-suit deck spades and hearts, so every direction's indigo and rose read on their own and side by side; the sheets show both.

## The directions

| Direction       | Pips                                                                        | Aces                                             | Courts, joker and free cell                                                                                                                                                                    |
| --------------- | --------------------------------------------------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| A, Classic dusk | Traditional layout, flat vector suits                                       | The suit in a thin gold sun ring with short rays | Double-ended figures drawn once and coloured by suit: the king with a rising-sun crown, the queen with a tiara, the jack with a feathered cap; a jester joker; a dashed gold free cell         |
| B, Horizon      | On a faint dawn-sky panel with a gold horizon line, framed like the back    | The suit rising as the sun over the dusk arcs    | Night panels over the water with an emblem and its reflection: the crowned sun (king), the crescent moon (queen), the evening star (jack); an eclipse joker; an empty horizon as the free cell |
| C, Pixel set E  | Hand-hinted 12 × 12 pixel pips in set E's rose and dusk materials, keylined | A pixel suit in a stepped gold ring              | Icon tiles on set E's dusk plate, drawn with its Pen (crown over a rising sun, crescent, star) with a suit badge; the four suits round a sun for the joker; a dotted ring for the free cell    |

## Recommendation

**B, Horizon.** It is the one that reads as the same deck as the sunset back: the panel has the back's frame, the courts are its sky at night, and the king is the back's sun crowned. Its courts are emblems rather than figures, so they stay legible at 72 × 112 where small faces turn to mush, and the dark court panels make J, Q and K findable at a glance on a busy table. It is also the cheapest to finish. The weak spot is the pip cards' sky, which is faint by design; if the owner wants crisper pips, C's hand-hinted pips drop into B's panel without other changes.

## Cost to finish

| Direction | Bespoke illustrations                                                                    | Generator work to ship (estimate)                                                                                                             |
| --------- | ---------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| A         | 4 (king, queen, jack, jester), each coloured for four suits: 12 courts and the joker     | 10 to 14 hours: figures need a pixel pass at 1x (faces, hands, a prop each), per-suit details so the four kings differ, and the review rounds |
| B         | 4 emblems (sun, moon, star, eclipse) and one ace scene template                          | 5 to 8 hours: tune the sky tint per suit, a pixel pass on the emblems' reflections, and decide the pip panel's strength                       |
| C         | 4 tile glyphs (crown, crescent, star, four-suit joker), 4 hinted pips, 4 hinted big aces | 8 to 12 hours: hand-hint the 30-pixel aces (now taken from the vector by coverage), check the tiles against the icon set's 32 px frames       |

All three then need the same shipping work, about 3 hours: hashes of the selected masters, 56 BMPs from `render.py`, a docs preview, `map.json` entries for bitmaps 1 to 53 and 66 in reactos-liminal, and a look in the running games.

## Files

- `faces.py`: the shared parts (cards.dll order, the suit outlines, pip layouts, the index font, the SVG writer)
- `classic.py`, `horizon.py`, `pixel.py`: one direction each
- `gen_faces.py OUT_DIR [DIRECTION ...]`: writes the 54 masters of each direction (`NN-<suit>-<rank>.svg`, `53-free-cell.svg`, `66-joker.svg`)
- `render_sheets.py OUT_DIR [--stock DIR]`: the contact sheets and the overview (needs rsvg-convert, Pillow and numpy); `--stock` adds the stock faces as a reference column, shown and never drawn from

The masters and sheets are review material and are not committed; the generators are deterministic, so they can be written again at any time. Once a direction is picked, its masters move beside the back with hashes in `SHA256SUMS.masters`, as the back's are.
