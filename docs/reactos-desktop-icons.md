# ReactOS desktop icons

![The Afterglow icon sheet: the construction keylines and materials, proof strips at 48, 32 and 16 px on a dark, a cream and a dusk ground, the hinted 16 px redraws, then all 140 icons in their nine groups.](images/afterglow-icons.png)

_The contact sheet, rendered from the vector masters._

The Afterglow icon set for ReactOS: 140 icons in nine groups (desktop and shell, programs, Control Panel applets, Explorer toolbar, drives and folders, file types, dialogs, system tray and the Start menu) and the shortcut arrow, drawn on a 48 px grid as vector masters and rendered down by script to 16, 32 and 48 px. The whole set is drawn in the language of the folder (variant E, after the folder called G-M1). Quill's own icons are not part of it.

## Design rules

**The language.** Every icon has a flat two-tone base from the Afterglow tokens (a deeper tone behind, a lighter one in front), a very gentle top-to-bottom ramp, a 1 px lit band on the top and left, a thin inner edge in a darker tone of the same hue, a soft contact shadow and generous rounded corners. There is no ink outline and no extrusion: depth comes from a front face over a back face, and the edge is clipped inside the face so the silhouette never grows. Apps and applets sit on the same softly raised dusk plate as Folder Options. Gold is the one accent, rose is for delete, error and shut down, and shape rather than colour separates the dialog badges. The bottom-left corner (16 × 16 at 48, 11 × 11 at 32, 8 × 8 at 16) is plain on every icon, because ReactOS draws the shortcut arrow there.

**Devices and media.** The drive slots and My Computer show the device, not what goes in it, and each device is drawn as the object people know, seen from a little above like the hard disk:

- **CD drive** says optical drive. It is a slim 5.25 in drive: the faceplate with its light and eject button, and the black tray run out of it with a silver disc seated on it. The disc on the open tray is what tells it from the hard disk.
- **Floppy** says 3.5 in floppy drive. It is the faceplate with its slot, light and eject button, and a violet floppy disk going into the slot shutter end first, in front of the faceplate, with its leading edge lost in the slot.
- **Removable drive** says a drive you plug in and pull out. It is a USB flash drive laid on the diagonal, plug up and to the right: a gold body with a label, a lit activity light and a key ring hole, and the steel USB plug with its two windows. On the slant and in gold it is a different object from the upright, light `usb-key`, and nothing about it is a drive box.
- **RAM disk** says a drive held in memory. It is one black memory chip with its legs, the part people know as memory, with a gold disk platter printed on its lid, its lit sector the usage pie Windows draws for a drive. One chip with a platter is not the `ram-module` stick of three chips, and it needs no drive box around it.
- **My Computer** says this computer: the monitor with its system unit beside it.

The art that shows the medium or the part on its own is kept under its own ids, for media, storage and hardware lists: `cd-disc` (CD disc), `floppy-disk` (floppy disk), `monitor` (monitor alone), `usb-key` (USB key) and `ram-module` (RAM module). They are in `map.json` as `unmapped`, because no drive, floppy, removable, RAM disk or My Computer slot uses them. Each of the five device icons has a hand-tuned 16 px frame.

**The keyline on the drives.** ReactOS shows the drives and My Computer on light windows (the white file list of My Computer, cream dialogs), where set E's light faces and soft inner edge left them pale: Local Disk read at 1.4:1 against cream. So Hard disk, Floppy, Removable drive, RAM disk and My Computer ship with the keyline (`KEYLINED_DRIVES` in `gen_e.py`): set E's own inner edge, made opaque and retuned in each material's own hue to a luminance of about 0.137, about 1.5 screen pixels wide at 32 and 16 px. It is not an ink outline: the steel body keeps a steel edge, the gold a deeper gold. Removable drive's hand-tuned 16 px frame gives its edge pixels the same tone; the other 16 px frames already reach 3:1. CD drive does not need it, because its black tray carries it. Contrast of the main silhouette's edge (WCAG 2, measured as `desktop/icons/alternatives/README.md` describes), at 48, 32 and 16 px:

| Icon            | Cream before     | Cream now        | Dusk now         | White now        |
| --------------- | ---------------- | ---------------- | ---------------- | ---------------- |
| Hard disk       | 1.40, 1.48, 3.04 | 3.63, 3.64, 3.04 | 6.78, 5.27, 14.8 | 5.58, 5.60, 4.68 |
| Floppy          | 1.36, 1.57, 4.04 | 3.63, 3.64, 4.04 | 6.46, 4.70, 4.90 | 5.58, 5.60, 6.21 |
| Removable drive | 1.60, 1.81, 2.48 | 3.48, 3.65, 3.65 | 4.16, 4.16, 10.0 | 5.35, 5.61, 5.61 |
| RAM disk        | 2.12, 2.97, 6.72 | 3.63, 3.63, 6.72 | 3.40, 3.40, 5.89 | 5.58, 5.58, 10.3 |
| My Computer     | 1.49, 1.79, 4.04 | 3.63, 3.63, 4.04 | 6.28, 4.59, 4.05 | 5.58, 5.58, 6.21 |
| CD drive        | 6.50, 5.78, 9.46 | unchanged        | 3.14, 5.17, 4.05 | 10.0, 8.76, 14.5 |

**The keyline on light grounds.** The same keyline then went to the rest of the icons ReactOS shows on light grounds, where set E's soft edge left them at 1.3 to 2.6:1 against cream (`KEYLINED_PAGES`, `KEYLINED_TOOLBAR` and `KEYLINED_LIGHT` in `gen_e.py`):

- **The 14 icons drawn on a page**: Document, Documents, Text, Image, Library, Archive, Font, Rich text, Audio, Video, Batch, Registry, Settings and Web page files. Their hand-tuned 16 px frames give their edge pixels the keyline tone too, because the paper edge alone was 2.8:1.
- **The 17 Explorer toolbar glyphs** on the cream toolbar, at every size the strips use: Back, Forward, Up, Search, Folders, Move to, Copy to, Cut, Copy, Paste, Delete, Undo, Views, Properties, Favourites, Map network drive and Disconnect network drive. The 24 px frames keep the strips' cells as they were. Views gains a hand-tuned 16 px frame, because the scripted one blurred its three bars into one block at 1.9:1. The Folders glyph is M1's drawing with the keyline laid on its strokes, and the light core of its tree takes the keyline tone, because a line that thin cannot carry an edge at 24 and 16 px.
- **The light objects of the white file windows**: both Recycle Bins, Program, Network drive and Network drive (not connected), and the media and hardware art (CD disc, Floppy disk, USB key and Monitor). Their hand-tuned 16 px frames already reach 3:1, so they are unchanged.

Every one reaches 3:1 on cream, white and Dusk at every size. Contrast at 48, 32, 24 (toolbar glyphs) and 16 px:

| Icon                            | Cream before           | Cream now              | Dusk now               | White now              |
| ------------------------------- | ---------------------- | ---------------------- | ---------------------- | ---------------------- |
| Document and 11 more page icons | 1.36, 1.79, 2.80       | 3.64, 3.64, 3.65       | 8.27, 6.12, 16.6       | 5.60, 5.60, 5.61       |
| Documents                       | 1.36, 1.79, 2.80       | 3.64, 3.64, 3.65       | 7.74, 5.77, 14.8       | 5.60, 5.60, 5.61       |
| Web page                        | 1.36, 1.79, 2.80       | 3.64, 3.64, 3.65       | 8.27, 5.69, 16.6       | 5.60, 5.60, 5.61       |
| Back                            | 1.64, 1.70, 1.60, 2.34 | 3.65, 3.65, 3.65, 3.65 | 6.03, 4.34, 4.70, 3.38 | 5.61, 5.61, 5.61, 5.61 |
| Copy                            | 1.36, 1.49, 1.35, 2.79 | 3.64, 3.64, 3.64, 3.64 | 7.74, 5.68, 4.26, 4.35 | 5.60, 5.60, 5.60, 5.60 |
| Copy to                         | 1.37, 1.48, 1.43, 1.98 | 3.64, 3.64, 3.64, 3.64 | 6.81, 4.70, 4.23, 3.38 | 5.60, 5.60, 5.60, 5.60 |
| Cut                             | 1.41, 1.72, 1.97, 2.48 | 3.57, 3.65, 3.65, 3.53 | 4.62, 4.06, 3.84, 3.91 | 5.48, 5.61, 5.61, 5.43 |
| Delete                          | 2.39, 2.45, 2.55, 2.86 | 3.42, 3.54, 3.62, 3.61 | 3.61, 3.48, 3.87, 3.42 | 5.25, 5.44, 5.55, 5.54 |
| Disconnect network drive        | 1.47, 1.88, 2.02, 2.74 | 3.63, 3.63, 3.63, 3.48 | 6.42, 3.98, 4.15, 3.89 | 5.58, 5.58, 5.58, 5.35 |
| Favourites                      | 1.50, 1.75, 1.82, 2.22 | 3.63, 3.65, 3.63, 3.58 | 4.56, 4.13, 4.27, 3.85 | 5.58, 5.61, 5.58, 5.50 |
| Folders                         | 1.51, 1.54, 1.51, 1.55 | 3.65, 3.65, 3.65, 3.55 | 4.25, 3.84, 4.04, 3.49 | 5.61, 5.61, 5.61, 5.37 |
| Forward                         | 1.53, 1.77, 1.60, 2.34 | 3.65, 3.65, 3.65, 3.65 | 6.03, 4.34, 4.07, 3.44 | 5.61, 5.61, 5.61, 5.61 |
| Map network drive               | 1.46, 1.80, 1.97, 2.49 | 3.63, 3.63, 3.63, 3.61 | 6.46, 4.29, 4.15, 3.89 | 5.58, 5.58, 5.58, 5.53 |
| Move to                         | 1.37, 1.41, 1.32, 2.35 | 3.64, 3.64, 3.64, 3.64 | 6.79, 4.70, 4.23, 3.48 | 5.60, 5.60, 5.60, 5.60 |
| Paste                           | 1.32, 1.51, 1.66, 2.16 | 3.64, 3.65, 3.64, 3.65 | 7.30, 4.91, 6.00, 3.68 | 5.60, 5.61, 5.60, 5.61 |
| Properties                      | 1.56, 1.79, 2.07, 3.05 | 3.64, 3.64, 3.64, 3.64 | 5.97, 4.56, 5.67, 4.35 | 5.60, 5.60, 5.60, 5.60 |
| Search                          | 1.74, 2.17, 2.93, 4.04 | 3.58, 3.63, 3.63, 4.04 | 4.43, 4.08, 3.71, 10.2 | 5.51, 5.58, 5.58, 6.21 |
| Undo                            | 1.37, 1.43, 1.46, 1.77 | 3.65, 3.65, 3.65, 3.65 | 5.85, 4.97, 4.96, 5.99 | 5.61, 5.61, 5.61, 5.61 |
| Up                              | 1.52, 1.53, 1.84, 2.48 | 3.64, 3.64, 3.64, 3.64 | 6.12, 4.70, 4.75, 3.49 | 5.60, 5.60, 5.60, 5.60 |
| Views                           | 1.31, 1.45, 1.45, 1.93 | 3.64, 3.64, 3.64, 3.65 | 7.56, 4.59, 5.67, 5.89 | 5.60, 5.60, 5.60, 5.61 |
| CD disc                         | 1.26, 1.56, 3.04       | 3.35, 3.64, 3.04       | 5.39, 4.68, 14.8       | 5.15, 5.60, 4.68       |
| Floppy disk                     | 2.64, 2.86, 4.89       | 3.65, 3.65, 4.89       | 4.22, 3.38, 4.90       | 5.61, 5.61, 7.52       |
| Monitor                         | 1.38, 1.91, 3.04       | 3.64, 3.64, 3.04       | 7.55, 5.82, 14.8       | 5.60, 5.60, 4.68       |
| Network drive                   | 1.41, 1.76, 3.04       | 3.63, 3.64, 3.04       | 6.46, 3.98, 10.0       | 5.58, 5.60, 4.68       |
| Network drive (not connected)   | 1.47, 1.88, 4.04       | 3.63, 3.63, 4.04       | 6.42, 4.42, 10.0       | 5.58, 5.58, 6.21       |
| Program                         | 1.56, 1.98, 3.04       | 3.64, 3.64, 3.04       | 7.55, 5.15, 14.8       | 5.60, 5.60, 4.68       |
| Recycle Bin (empty)             | 1.40, 1.89, 4.04       | 3.63, 3.63, 4.04       | 5.48, 4.58, 10.2       | 5.58, 5.58, 6.21       |
| Recycle Bin (full)              | 1.36, 1.75, 4.04       | 3.63, 3.63, 4.04       | 4.98, 4.56, 10.2       | 5.58, 5.58, 6.21       |
| USB key                         | 1.44, 1.62, 3.04       | 3.64, 3.64, 3.04       | 7.55, 4.70, 14.8       | 5.60, 5.60, 4.68       |

The rest of the set does not ship the keyline: 43 icons are below 3:1 on cream and 51 on Dusk. They are the tray glyphs (Volume, Clock, the batteries), which sit on the near-black taskbar; the plated apps and applets, which fail only on Dusk, where the glyph on the plate carries them; the M1 folders and ReactOS Explorer, which keep the chosen M1 design; and the dialog badges and Start menu items. Their keyline variants are review-only alternatives in `desktop/icons/alternatives/`, with a sheet of the 24 furthest below it.

**The tiers and sizes.** Body objects (folders, documents, drives, monitors, bins) get a 30 % contact shadow. Symbols, dialog badges and toolbar glyphs only lift, with a 20 % shadow, and Delete, Undo and Shut Down are flat stroke marks. The edge is 1 px at 30 % at 48, 1 screen pixel at 45 % at 32 and a baked solid tone at 16, where the ramp, lit band and shadow are dropped. 24 px is not drawn because ReactOS never asks for it.

## The folders

Folder, Folder (open), My Documents, My Pictures, My Music, My Videos, Desktop, My Network Places, Folder Options and Folders are exactly G-M1: one sheet with a sloped tab and a separate flap. `gen_e.py` imports `folders_g.py` and renders it with M1's own tags, so they cannot drift from the chosen design. The special folders (My Documents, My Pictures, My Music, My Videos, Desktop and My Network Places) are the closed folder with an embossed emblem. The open folder is delivered but ReactOS 0.4.16 rarely shows it: only the file dialog's Look in list and regedit ask for it. The Recycle Bin is two icons, empty and full, because it is the one icon ReactOS changes with its contents.

## The shortcut arrow

`arrow.ico` is the overlay ReactOS draws over a shortcut's icon. It is the original A1 paper coin: a paper disc with a tinted indigo edge, a dusk-navy straight diagonal arrow and a slim soft shadow at 48 and 32. The owner chose it after exploring other badges, obtuse arrow heads and bent elbows (`arrows.py` keeps those options, but nothing shipped uses them). The stock overlay, shell32 group 30, has only 16 and 32 px frames, so at Shell Icon Size 48 ReactOS stretches the 32 px frame and blurs it; `arrow.ico` has real 16, 32 and 48 px frames, with each size's shadow baked in and none at 16. The 16 px frame is drawn pixel by pixel. All the art sits inside the stock boxes (16 × 16, 11 × 11 and 8 × 8, bottom-left), so no icon loses more than it does today, and a test checks it.

![The shortcut arrow over a folder, document, My Computer, hard disk, Recycle Bin and program at 48, 32 and 16 px, on the dark desktop and on cream, enlarged three times.](images/afterglow-arrow.png)

_The arrow composited the way ReactOS does it: at the top left of a frame of the same size._

The arrow reads at 13.9:1 on its coin. The coin is light, so its separation comes from the tinted edge: 1.9:1 against the gold back of the folder, 2.5:1 against the gold front and 3.5:1 against paper. That edge is the weak point on light and gold icons, where the coin is almost the same tone as what it sits on, and at 16 px the edge is a single pixel ring. On the dark desktop and on the dusk app plate the paper coin stands out strongly.

To use it, replace shell32 group 30, which is the `Shell Icons` registry value `29` (`HKLM\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Icons`), with `ico/arrow.ico`. ReactOS composites the overlay at paint time over the icon at the same size, so it has to be 32-bit at every size.

## Sizes and the render

Every icon ships at 16, 32 and 48 px, drawn from the master built for that size:

| Size  | Drawn from                                                                                    |
| ----- | --------------------------------------------------------------------------------------------- |
| 48 px | `svg/ID.svg`, the master                                                                      |
| 32 px | `svg/32/ID.svg`, the 32 px profile (still a 48 viewBox, with its own edge)                    |
| 24 px | `svg/24/ID.svg`, the 24 px profile, for the 18 Explorer toolbar glyphs only                   |
| 16 px | `svg/ID-16.svg`, the hinted redraw, for the 82 icons that have one; otherwise `svg/16/ID.svg` |

The hinted 16 px redraws are pixel drawings: Folder, Folder (open), My Documents, My Pictures, My Music, My Videos, Desktop, My Network Places, Document, Documents, Warning, Error, Search, Hard disk, My Computer, Monitor, both Recycle Bins, Favourites, Recent and the Programs folder, and the 62 hand-tuned frames below. `desktop/icons/render.py OUT_DIR` runs `rsvg-convert` on each, which bakes each size's own blur for the shadows, and writes `png/ID-SIZE.png` (441 files), one `ico/ID.ico` per icon (141 files with the arrow) and, for each toolbar glyph, `ico24/ID.ico` with its one 24 px frame (18 files). An `.ico` holds the three frames, smallest first, as uncompressed 32-bit BGRA DIB frames with alpha and an all-zero AND mask: the classic layout that old icon loaders read, with no PNG-compressed frames. The output has no dates, so the same masters and the same `rsvg-convert` give the same bytes. The `.ico` bytes were identical with `rsvg-convert` 2.58 and 2.63; the PNG files are written as `rsvg-convert` makes them and are not hashed. The files are named by the icon ids, so a build recipe can pick `ico/folder.ico` by id. The `.ico` hashes are in `desktop/icons/SHA256SUMS`, and `bun run check:desktop` renders them again and compares.

```sh
python3 desktop/icons/render.py desktop/build/icons    # ico/, ico24/, png/, afterglow-icons-sheet.png and afterglow-arrow-preview.png
python3 desktop/icons/contact.py desktop/build/icons docs/images/afterglow-icons-contact.png
```

## Hand-tuned 16 px frames

ReactOS shows most icons at 16 px: the Explorer tree, the List and Details views, Start menu submenus, the tray and the Control Panel list. A scripted downscale of a 48 px drawing blurs there, so 62 icons have a 16 px frame drawn on the pixel grid in `desktop/icons/hint16_v2.py`: the drives (CD, floppy, network, removable, RAM disk, not connected), the file types (text, image, program, library, archive, font, rich text, audio, video, batch, registry, settings, web page), the Start menu (Programs, Settings, Help, Run, Shut Down, Log Off), the Control Panel list (the 19 applets of set E with Folder Options, the Control Panel itself and the three added in v2), the tray (volume, muted, clock, keyboard layout), the Information and Question dialogs, Command Prompt, Internet Browser and the Views toolbar glyph. My Computer and the media art (CD disc, floppy disk, USB key and RAM module) have one as well.

Each frame is one 16 x 16 grid of characters written out pixel by pixel, with the same silhouette and palette as the master: a material's base tone, its baked 16 px edge, the plate's sky ramp and horizon rim, and the set's flat detail colours. It is written as one whole-pixel rect per pixel with crisp edges, so there is no anti-aliasing, blur, ramp or shadow. `gen_e.py` writes it as `svg/ID-16.svg`, and `render.py` uses it for the 16 px frame like the other hinted redraws.

![The 62 hand-tuned 16 px frames at eight times: in each cell, the scripted downscale and the hand-tuned frame on the Dusk desktop, then the same pair on cream.](images/afterglow-icons-16px-before-after.png)

_Before and after at 8x, drawn by `desktop/icons/compare16.py docs/images/afterglow-icons-16px-before-after.png`._

## The map

[`map.json`](../desktop/icons/map.json) lists every icon id, and the arrow, with its label, its group and what it replaces in ReactOS. A `status` of `named` means a ReactOS object is named; `unmapped` means none is yet (Clock, Show desktop, Network in the tray and Security, which ReactOS 0.4.16 does not draw from a resource). A `resource` names the module and icon group to replace, or for the Explorer toolbar the four `browseui.dll` bitmap strips (214 and 215 at 24 px, 216 and 217 at 16 px) and the cell index; `also` lists more groups or cells that take the same icon, each with what uses it. Every id carries its evidence: `source` (the ReactOS 0.4.16 source at tag `0.4.16-release`: the resource headers and `.rc` files, `hivecls.inf`, `shortcuts.inf` and the `*ImageIndex` constants in `browseui/toolsband.cpp`) and `binary` (the stock 0.4.16 i386 file holds that group). Spider Solitaire and Sound Recorder are `source` only, because the stock files at hand did not include them. 130 icons carry a resource, and no group or cell is claimed by two icons; a test checks both. The build that applies the icons is the reactos-liminal one.

## Icons v2

The second pass draws the icons ReactOS still showed in its stock art once set E was applied, from the reactos-liminal icon survey's lists of missing art and from what the 0.4.16 Start menu installs (`shortcuts.inf`). They are drawn in `desktop/icons/gen_v2.py` with set E's own Pen, materials, profiles, dusk plate and shadows, so nothing about the language changes; the three new special folders add their emblems to the M1 folder's emblem tables. Set E's 73 masters and `.ico` files are byte for byte what they were.

- **Programs (23).** Calculator, Paint, Registry Editor, Task Manager, WordPad, Character Map, Clipboard Viewer, Minesweeper, Solitaire, Spider Solitaire, On-Screen Keyboard, Magnifier, Remote Desktop Connection, Media Player, Sound Recorder, Event Viewer, System Configuration, ReactX Diagnostic, Service Manager, Device Manager, Utility Manager, the update installer and ReactOS Explorer. Applications Manager, Internet Browser and Read Me were in set E and now carry their ids.
- **Control Panel applets (3).** Game Controllers, Phone and Modem, User Accounts.
- **Shell and Start menu (4).** Favourites, Recent and the Programs folder (M1 folders with a star, clock and grid emblem, each with a hinted 16 px redraw) and Log Off.
- **Drives (3).** Removable drive (a USB flash drive), RAM disk (a memory chip with a disk platter) and the network drive that is not connected.
- **File types (6).** Audio, video, batch, registry, settings (`.ini`, `.inf`) and web page files.
- **Explorer toolbar (7).** Cut, Copy, Paste, Properties, Favourites, Map network drive and Disconnect network drive: every cell `toolsband.cpp` uses now has an Afterglow glyph. All 18 toolbar glyphs also get a 24 px profile, because the large strips are 24 px.
- **Tray (16).** Volume muted, the six battery levels, the five charging levels, battery fault, mains power, and safely remove hardware with its problem state, from `stobject.dll`.

Existing icons were also given the ids the survey and the stock files verify: the drives, the Start menu items, the applets, the file types, the dialog icons in `user32.dll` (101 to 104) and the toolbar cells.

**Left out, and why.** No Afterglow art goes in `user32.dll` group 105 (`IDI_WINLOGO`, the ReactOS logo), or in the Mouse Keys tray states (`stobject.dll` 440 to 449: 16 px, 8-bit only, so they have no 32-bit frame id to reuse). History and full screen are not drawn: no 0.4.16 toolbar button uses them, and their strip cells are not named in `toolsband.cpp`. The 24 px hot strips take the same cells as the normal ones, because Afterglow draws no hot state. Help Viewer, Volume Control, the Keyboard Layout Switcher, `control.exe`, `netshell.dll` and the CSIDL_DRIVES, NetHood and Entire Network folders take existing icons (Help, Sound and Audio, Keyboard layout, Control Panel, Network Connections, My Computer and My Network Places) through `also`.

**Design choices.** One variant of each was drawn; the review of the first pass changed two. ReactX Diagnostic first had a white cross on a violet disc, which read as Close or Error, so it became a gold four-point sparkle on the disc with a lens. Paint's brush first ran past the plate's top-right corner; it was turned so the tip points at the canvas and the handle stays inside. Cut's blades and rings were drawn heavier after the first render, because at 16 px the thin strokes left no solid pixel. The removable drive is a USB flash drive rather than a cartridge drive, the RAM disk a memory chip with a disk platter, and the network drive states share one drive with a gold plus (map), a rose minus (disconnect) or a rose cross (not connected).

![The Afterglow system icons: every icon at 48, 32 and 16 px at true size and its 16 px frame at four times, on the Dusk desktop colour and on the classic cream window colour.](images/afterglow-icons-contact.png)

_The system contact sheet, drawn by `desktop/icons/contact.py` from the render._

## Vector masters

All the art is vector. `desktop/icons/gen_e.py` is the canonical source for the icons: it draws every icon and the sheet, and writes `icons/` (the 48 px masters, the `32/`, `24/` and `16/` profiles and the hinted `ID-16.svg` redraws, 520 files) and `sheet.svg`. It imports `folders_g.py` and `gen_v2.py` beside it for the folder family. `desktop/icons/arrows.py` is the canonical source for the arrow (`arrows.py --variant A1 --out DIR` writes the three masters in `desktop/icons/arrow/`); the copy keeps its other variants and its own sheet code, which this repository does not use. The committed [`desktop/icons/svg/`](../desktop/icons/svg/), `desktop/icons/sheet.svg` and `desktop/icons/arrow/` are their output, kept so the masters can be opened and diffed without running anything. Edit the generators, not the SVGs: `bun run check:desktop` regenerates them and fails when they differ from the committed files, and `desktop/icons/SHA256SUMS.masters` records their hashes. Rasters are always rendered from the masters and never edited by hand.

```sh
python3 desktop/icons/gen_e.py OUT_DIR    # writes OUT_DIR/icons/ and OUT_DIR/sheet.svg
python3 -B desktop/icons/arrows.py --variant A1 --out OUT_DIR/arrow
cp -r OUT_DIR/icons/. desktop/icons/svg/ && cp OUT_DIR/sheet.svg desktop/icons/sheet.svg
cp OUT_DIR/arrow/arrow-48.svg OUT_DIR/arrow/arrow-32.svg OUT_DIR/arrow/arrow-16-hinted.svg desktop/icons/arrow/
(cd desktop/icons && find svg arrow -type f | LC_ALL=C sort | xargs sha256sum > SHA256SUMS.masters && sha256sum sheet.svg gen_e.py gen_v2.py hint16_v2.py folders_g.py arrows.py >> SHA256SUMS.masters)
```

The sheet's text uses whatever sans-serif the renderer finds, so the contact sheet PNG in `docs/images/` is a picture for the docs and is not compared byte for byte.

## Licence

The art, the generators and the renderer are original to this repository and licensed Apache-2.0 OR MIT, (c) Copyright 2026 Liminal HQ, Scott Morris, like the rest of it (`LICENSE-APACHE`, `LICENSE-MIT`); each SVG carries the header. No ReactOS, Windows or third-party icon was copied, traced or recoloured, and the arrow is not the stock bitmap. The design follows public guidance (Microsoft Learn's app icon design and construction pages, Fluent 2's iconography notes) for grids, radii, sizes and light direction, and nothing from them is reproduced. ReactOS itself is GPL and LGPL code: the icons are separate files, and this repository does not ship a patched ReactOS binary.
