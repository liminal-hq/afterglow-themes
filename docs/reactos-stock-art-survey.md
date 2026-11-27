# ReactOS stock art survey

Which icon groups and bitmaps of ReactOS 0.4.16 still show stock art in the Afterglow image, found by reading every resource of the stock files rather than by booting and spotting them one at a time. Each row says what the resource is, what shows it and whether Afterglow art covers it: on the image already, drawn and waiting for a patch, drawn by the dialog art pass, or still stock. The patches themselves are made by the reactos-liminal build from [`map.json`](../desktop/icons/map.json); nothing here changes a ReactOS file.

## Method

- **Files.** Every PE file in `ReactOS/system32` and `ReactOS` of the stock 0.4.16 i386 install (the reactos-liminal golden disk, read with mtools without mounting it: 661 and 8 files), compared with the same files on the built Afterglow image. A resource whose bytes differ on the image, or that lives in the patched copies `agexplorer.exe` and `agmsgina.dll`, counts as Afterglow.
- **Resources.** Every `RT_GROUP_ICON` (with its frames as size and bits per pixel, from the group directory) and every `RT_BITMAP` (width, height and depth from its header) in each file: 1,073 in 133 files. Evidence `binary`.
- **Names and uses.** The ReactOS 0.4.16 source at tag `0.4.16-release` (commit `822e864`, the build the image runs): each id is named from the module's `.rc` and header files, and the dialog templates (`lang/en-US.rc`) and code that load it are listed under _Shown by_. Evidence `source`.
- **Shortcuts.** Every `.lnk` under `Default User` and `All Users` on the image, with its target and icon location (an icon index of 0 is the file's first icon group in directory order).

## Summary

| Status            | Resources | What it means                                                                                             |
| ----------------- | --------- | --------------------------------------------------------------------------------------------------------- |
| Afterglow         | 89        | The image shows Afterglow art                                                                             |
| Stock, art ready  | 43        | `map.json` already named the resource; the art exists and the image only needs the patch                  |
| Stock, drawn here | 40        | Drawn or mapped by the dialog art pass (icons v3 and `desktop/dialogs`); needs the patch                  |
| Stock             | 798       | No Afterglow art: mostly resources ReactOS rarely or never shows, listed so nothing is missed (see below) |
| Trimmed           | 103       | In files the `base` trim removes; no art needed for the image                                             |

Of the art the image actually shows, every item the owner reported is now covered: 83 resources are drawn and named in the map but not yet patched (43 ready before this pass, 40 from it). The full image, with nothing trimmed, is surveyed in [Full image extras](#full-image-extras).

## What the owner saw, and where it comes from

| Seen                                       | Resource                                                                                                                                | Status                                                          |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| About box banner (ShellAbout)              | `shell32.dll` bitmap 131 `IDB_REACTOS`, 413 × 72, 24-bit; the line under it, bitmap 138 `IDB_LINEBAR`, 413 × 5, 24-bit                  | Drawn here: `about-banner`, and the logon bar for 138           |
| About box icon                             | the calling program's icon (`iexplore.exe` 1)                                                                                           | Afterglow already (`browser`)                                   |
| Administrative Tools: Device Manager       | `devmgmt.exe` group 1 (the shortcut's icon index 0)                                                                                     | Art ready: `devmgmt`                                            |
| Administrative Tools: Event Viewer         | `eventvwr.exe` group 10                                                                                                                 | Art ready: `eventvwr`                                           |
| Administrative Tools: Service Manager      | `servman.exe` group 50                                                                                                                  | Art ready: `servman`                                            |
| Administrative Tools: System Configuration | `msconfig.exe` group 3001                                                                                                               | Art ready: `msconfig`                                           |
| Explorer status bar, My Computer zone      | `shell32.dll` group 181 `IDI_SHELL_COMPUTER_DESKTOP` (`CDefView.cpp`, `LoadIconW`), one frame, 32 px 32-bit                             | Drawn here: `mycomputer`                                        |
| Network Connections item                   | `netshell.dll` group 105 `IDI_NET_IDLE` (106 when unplugged; 107 to 109 the tray states)                                                | Drawn here: `lan`, `lanoff`, `lanrec`, `lantrans`, `lanboth`    |
| System Properties, Hardware tab            | `sysdm.cpl` groups 51 `IDI_DEVMGR`, 2502 `IDI_ADDHW`, 52 `IDI_HARDPROF`, each one 32 px 32-bit frame                                    | Drawn here: `devmgmt`, `addhw`, `hwprofile`                     |
| Customize Classic Start Menu               | `explorer.exe` group 257 `IDI_STARTMENU2` and 108 `IDI_RECYCLEBIN`                                                                      | Drawn here: `startmenu`, `recycle`                              |
| Mouse, Button tab                          | `main.cpl` groups 109 and 110 (`IDI_MOUSE_LEFT`, `_RIGHT`, 48 px) and 605 and 606 (the test folder, 48 px)                              | Drawn here: `mouse-left`, `mouse-right`, `folder`, `folderopen` |
| Mouse, other tabs; Keyboard, Speed tab     | `main.cpl` 104, 108, 600, 601, 602, 603, 607, 105, 106                                                                                  | Drawn here (see the builder list)                               |
| Task Manager window and Start menu icon    | `taskmgr.exe` group 136                                                                                                                 | Art ready: `taskmgr`                                            |
| Shut Down dialog (Start, Shut Down)        | `msgina.dll` bitmaps 20003 `IDI_DLG_BG` (312 × 198), 20002 `IDI_ROSLOGO_FLAG` (48 × 40), 20004 `IDB_IMAGE_STRIP` (33 × 330), all 24-bit | Drawn here: `shutdown-bg`, `shutdown-mark`, `shutdown-strip`    |
| Log Off dialog                             | `shell32.dll` bitmaps 500, 501 and 502 (33 × 231), 24-bit                                                                               | Drawn here: `shutdown-bg`, `shutdown-mark`, `logoff-strip`      |

## Every program the Start menu shows

The shortcuts' icon is the target's first icon group (index 0), or index 1 for ReactOS Explorer.

| Shortcut                                                                                                                                                                                                 | Target                           | Group | Status                                                                                   |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- | ----- | ---------------------------------------------------------------------------------------- |
| Applications Manager                                                                                                                                                                                     | `rapps.exe`                      | 10    | Afterglow (`appmanager`)                                                                 |
| Command Prompt                                                                                                                                                                                           | `cmd.exe`                        | 1     | Afterglow (`cmd`)                                                                        |
| Notepad                                                                                                                                                                                                  | `system32/notepad.exe`           | 521   | Afterglow (`text`); the copy in `ReactOS/` is stock                                      |
| Wine Internet Explorer                                                                                                                                                                                   | `iexplore.exe`                   | 1     | Afterglow (`browser`)                                                                    |
| ReactOS Explorer                                                                                                                                                                                         | `explorer.exe`                   | 101   | Art ready (`explorer`); `agexplorer.exe` is the shell, this shortcut runs the stock file |
| Device Manager                                                                                                                                                                                           | `devmgmt.exe`                    | 1     | Art ready (`devmgmt`)                                                                    |
| Event Viewer                                                                                                                                                                                             | `eventvwr.exe`                   | 10    | Art ready (`eventvwr`)                                                                   |
| Service Manager                                                                                                                                                                                          | `servman.exe`                    | 50    | Art ready (`servman`)                                                                    |
| System Configuration                                                                                                                                                                                     | `msconfig.exe`                   | 3001  | Art ready (`msconfig`)                                                                   |
| Task Manager                                                                                                                                                                                             | `taskmgr.exe`                    | 136   | Art ready (`taskmgr`)                                                                    |
| Registry Editor                                                                                                                                                                                          | `ReactOS/regedit.exe`            | 100   | Art ready (`regedit`; 101 `regfile`)                                                     |
| Clipboard Viewer                                                                                                                                                                                         | `clipbrd.exe`                    | 100   | Art ready (`clipbrd`)                                                                    |
| Keyboard Layout Switcher                                                                                                                                                                                 | `kbswitch.exe`                   | 150   | Art ready (`kbdlayout`)                                                                  |
| Accessibility Utility Manager                                                                                                                                                                            | `utilman.exe`                    | 30    | Art ready (`utilman`); one 32 px 32-bit frame                                            |
| Volume Control                                                                                                                                                                                           | `sndvol32.exe`                   | 301   | Art ready (`sound`)                                                                      |
| FontSub (Font Substitutes Editor)                                                                                                                                                                        | `fontsub.exe`                    | 1     | Drawn here (`fontsub`); the group has 24-bit frames only                                 |
| Virtual CDRom Control Panel                                                                                                                                                                              | `vcdcontroltool.exe`             | none  | No icon of its own: shows `shell32.dll` 3, Afterglow `program`                           |
| Calculator, Paint, WordPad, Character Map, ReactX Diagnostic, SnapShot, Magnify, On-Screen Keyboard, Multimedia Player, Sound Recorder, Remote Desktop Connection, Solitaire, Spider Solitaire, WineMine | removed by the `base` trim       |       | Trimmed: their shortcuts are dead; the art exists for all but SnapShot                   |
| WineVDM                                                                                                                                                                                                  | `Program Files/otvdm/otvdmw.exe` |       | Third-party (otvdm), not a ReactOS file; not surveyed                                    |

## For the builder: what to patch

The art is the `.ico` of the id under `desktop/icons` (rendered to `ico/ID.ico` with 16, 32 and 48 px 32-bit frames) and the BMPs of `desktop/dialogs` (`render.py`). Stock files on the golden disk:

| File                    | Size       | SHA-256                                                            |
| ----------------------- | ---------- | ------------------------------------------------------------------ |
| `system32/msgina.dll`   | 827,392    | `95863449bd6af48e256708624ccc9b96ee91c931c4ac8eeb59b174c475dfca77` |
| `system32/shell32.dll`  | 10,935,296 | `88858710130e8e97eecfc246e61dd1aaf45b410718f4b818be39a9a69a01cf72` |
| `system32/main.cpl`     | 896,000    | `d6e65c9dae365134e0e25f44f836efaa72f955f9f379fa46d3b0dbfee8cabde9` |
| `system32/sysdm.cpl`    | 998,400    | `d68f02dc31123572208b59a91edfc56bdd51d44fb057075034d8f88dc6d612d2` |
| `system32/netshell.dll` | 684,544    | `9630e1a7a506c15e19586fa1502a192c55d4148c7fbb2f459752d2681d435a47` |
| `ReactOS/explorer.exe`  | 1,841,664  | `4e54225b041fe93ce0b252c6fda3c6c3cdae6203ba6a2d1e5b77873cd86488f7` |
| `system32/devmgmt.exe`  | 70,656     | `7cc79d3a2c1a2d52f3eba7a8306e9478f745d25cce61d8a2ede3b4e26058e0d8` |
| `system32/devmgr.dll`   | 869,376    | `0670f9388529d74252a08d0c4b25a93be6a971f0ab770600bf448278cbbf2fd3` |
| `system32/eventvwr.exe` | 406,528    | `3f0c1bd6542f913991452165c8fed30bd9745f76edcb3d8ad33d4dda0f026c12` |
| `system32/servman.exe`  | 508,928    | `fedc937af119f17ef243407e02f777f994488bba6dae785610d04f3cf7931668` |
| `system32/msconfig.exe` | 250,880    | `02030816cca7c289a5ed53b548ccf070b99ef609198aa9cb3b61a8d6e0b68b62` |
| `system32/taskmgr.exe`  | 680,448    | `579a15a60994106506c673ffa92a2c15d7cb156e294b7c005c2e4b27e94e4975` |
| `ReactOS/regedit.exe`   | 1,056,256  | `7abee39f6daa53a0d0fed7464ab5b6a5228b98d7035a5bddf59b39ecbcecd58b` |
| `system32/fontsub.exe`  | 296,448    | `04e3bb96444842e561e52e4ca6df4afbe8831b00d22c164e312d3f098bcd2b98` |
| `system32/clipbrd.exe`  | 153,600    | `3f07112479426bb55770f88bfe590b198cd1a2030803892e0eab2c6ab3573b8a` |
| `system32/kbswitch.exe` | 122,368    | `203c36281691c4e5c80d851c4dd79f40f44f411f103e2e7d626c2d6930da7230` |
| `system32/utilman.exe`  | 38,912     | `3045783db1595bdb3d0d64d39db9d8a607147105ba2d47d5a66c0e4d9117cd96` |
| `system32/sndvol32.exe` | 262,656    | `22c72feebf88dcdbc2f11054d6add67cd79865c98853bfc4f5db28bea872b8ce` |
| `system32/wusa.exe`     | 51,712     | `989cf594e4323c9efd7c53d02a053e750f436e15ca4331912e3f0b749f0eace5` |
| `ReactOS/notepad.exe`   | 345,088    | `90b2639e7462461879cf8302804c2c7436fb2062e4c2302a12412674bf3348e3` |
| `system32/stobject.dll` | 479,232    | `7c8776d0ca106e67b624a7843f5a57fe62cd5682ab72693d39078a64a68e70f3` |

Icon groups, with the frames each stock group owns (size@bits); many own fewer than three 32-bit frames, so the patcher's rule of three ids needs a mode that writes the sizes the group holds (and a 32-bit frame over an 8, 24 or 1-bit id where the group has none):

| Module         | Groups                                                                                                                                                                                                                                                                                                 | Art                                                                                                                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `main.cpl`     | 109, 110 (`48@8 48@32`), 605, 606 (`48@8 48@32`), 104, 601 (`16`–`256@32`), 603 (`32@32 32@8`), 602 (`32@8 32@32`), 105 (`32@24 32@32`), 106 (`32@8 32@32`), 607 (`16@8 16@32 32@8 32@32`), 108 (`32@8 32@8`), 600 (`32@1 32@1`)                                                                       | `mouse-left`, `mouse-right`, `folder`, `folderopen`, `mouse-speed`, `mouse-hide`, `mouse-wheel`, `mouse-locate`, `kbd-delay`, `kbd-rate`, `clicklock`, `mouse-snap`, `mouse-trails` |
| `sysdm.cpl`    | 51, 52, 2502 (`32@32`), 53 (`32@8 32@24 32@32`)                                                                                                                                                                                                                                                        | `devmgmt`, `hwprofile`, `addhw`, `usrmgr`                                                                                                                                           |
| `netshell.dll` | 105, 106, 107, 108, 109 (`32@32 16@32`)                                                                                                                                                                                                                                                                | `lan`, `lanoff`, `lanrec`, `lantrans`, `lanboth`                                                                                                                                    |
| `shell32.dll`  | 181 (`32@32`)                                                                                                                                                                                                                                                                                          | `mycomputer`                                                                                                                                                                        |
| `explorer.exe` | 257 (`32@32 32@4 16@4`), 107 (`32@32 32@8 32@4 16@32 16@8 16@4`), 108 (nine frames); and 101 for the ReactOS Explorer shortcut                                                                                                                                                                         | `startmenu`, `startmenu`, `recycle`, `explorer`                                                                                                                                     |
| `msgina.dll`   | 21 (six frames), 22 (`32@8 16@8 32@32 16@32`), 109 (six frames), 115 (`32@8 32@32`)                                                                                                                                                                                                                    | `logoff`, `shutdown`, `keyboard`, `shield`                                                                                                                                          |
| `devmgr.dll`   | 20 (six frames)                                                                                                                                                                                                                                                                                        | `devmgmt`                                                                                                                                                                           |
| Programs       | `devmgmt.exe` 1, `eventvwr.exe` 10, `servman.exe` 50, `msconfig.exe` 3001, `taskmgr.exe` 136, `regedit.exe` 100 and 101, `clipbrd.exe` 100, `kbswitch.exe` 150, `utilman.exe` 30 (`32@32`), `sndvol32.exe` 301, `wusa.exe` 101, `fontsub.exe` 1 (`16@24 32@24 48@24 64@24`), `ReactOS/notepad.exe` 521 | as `map.json` names them                                                                                                                                                            |
| Tray           | `stobject.dll` 230, 231, 400 to 413, 420, 421 (and `ctfmon.exe` 100)                                                                                                                                                                                                                                   | as `map.json` names them                                                                                                                                                            |

Bitmaps, all 24-bit and the same size as the stock ones, so each can be written in place:

| Module        | Bitmap                            | Art                                  |
| ------------- | --------------------------------- | ------------------------------------ |
| `shell32.dll` | 131 `IDB_REACTOS`, 413 × 72       | `desktop/dialogs` `about-banner.bmp` |
| `shell32.dll` | 138 `IDB_LINEBAR`, 413 × 5        | `desktop/logon` `afterglow-bar.bmp`  |
| `shell32.dll` | 500 `IDB_DLG_BG`, 312 × 198       | `shutdown-bg.bmp`                    |
| `shell32.dll` | 501 `IDB_REACTOS_FLAG`, 48 × 40   | `shutdown-mark.bmp`                  |
| `shell32.dll` | 502 `IDB_IMAGE_STRIP`, 33 × 231   | `logoff-strip.bmp`                   |
| `msgina.dll`  | 20003 `IDI_DLG_BG`, 312 × 198     | `shutdown-bg.bmp`                    |
| `msgina.dll`  | 20002 `IDI_ROSLOGO_FLAG`, 48 × 40 | `shutdown-mark.bmp`                  |
| `msgina.dll`  | 20004 `IDB_IMAGE_STRIP`, 33 × 330 | `shutdown-strip.bmp`                 |

## Findings that change how the patch is made

- **The Start menu's Shut Down dialog is the stock `msgina.dll`, not `agmsgina.dll`.** `shell32.dll` (`dialogs/dialogs.cpp`) calls `LoadLibraryW(L"msgina.dll")` and `ShellShutdownDialog` by name, and the dimmed desktop is `msgina.dll` ordinal 16 (`ShellDimScreen`), so the `GinaDLL` copy carries the logon boxes but never this dialog. Its three bitmaps have to go into `msgina.dll` itself (or into a copy that `shell32.dll`'s string is pointed at); the Log Off dialog's are in `shell32.dll`.
- **The text and its colours are code.** Both dialogs paint the title in RGB(244, 244, 244) and the labels in RGB(38, 38, 38) on a brush of RGB(244, 244, 244) (`DARK_GREY_COLOR` and `LIGHT_GREY_COLOR` in `shutdown.c` and `dialogs.cpp`), and the title "Shut Down ReactOS" is the dialog template's. So the art keeps the panel exactly that grey and the header and footer dark, and the title stays as it is unless the string table is rebuilt.
- **The greyed desktop behind them is code, not art.** `dimmedwindow.cpp` captures the screen and blends it toward its luminance in ten steps (`(r * 30 + g * 59 + b * 11) / 100`, then `(2 × colour + grey) / 3` per step). A dusk-tinted fade would mean changing that loop in `msgina.dll`: no resource holds it, so it is left as it is.
- **The About banner's line is the logon bar.** `shell32.dll` 131 and 138 are byte for byte `msgina.dll` 20000 and 20001, so the logon bar serves both; the banner is its own, because it carries the ReactOS copyright line.
- **`explorer.exe` and `agexplorer.exe`.** The shell runs `agexplorer.exe`, so its dialogs (Customize Classic Start Menu, Taskbar Properties) take the art from that copy, which `afterglow.start` already patches; the ReactOS Explorer shortcut runs the stock `explorer.exe`, whose group 101 needs its own patch.
- **Two copies of Notepad.** `system32/notepad.exe` is patched; `ReactOS/notepad.exe` is not.

## Left stock on purpose

- **ReactOS logo art:** the System Properties General tab picture (`sysdm.cpl` 55 `IDB_ROSBMP`, 320 × 159, and its mask 56) and `user32.dll` group 105 (`IDI_WINLOGO`). The branding rule keeps ReactOS's own logo art unmodified or out, never restyled.
- **Large pictures not yet drawn**, which ReactOS does show: the monitor in Display Properties (`desk.cpl` 1001, 160 × 120, 8-bit), the world map in Date and Time (`timedate.cpl` 115, 360 × 180, 24-bit), the taskbar previews of Taskbar Properties (`explorer.exe` 145 to 155, 170, 171 and 180 to 189: 336 × 35 and 300 × 180, 4, 8 and 24-bit), the wizard watermarks and headers (`hdwwiz.cpl` 50 and 51, `appwiz.cpl` 5001 and 5002, 8-bit) and Setup's bitmaps (`syssetup.dll`). They are candidates for the next pass; an 8 or 4-bit one would need a palette-safe export.
- **Everything else marked Stock** below: inner icons of programs and applets (Event Viewer's event types, Service Manager's toolbar, the Internet Options pages, `setupapi.dll`'s device classes, `pifmgr.dll`'s picker), screen savers, `cards.dll`, the `user32.dll` system bitmaps and the like, which are either rarely seen or not drawn from Afterglow's language yet.

## Full image extras

The full image (the `afterglow` recipe, nothing trimmed) keeps the files the compact image's `base` trim removes, 35 of which hold icons or bitmaps, and the art above was surveyed as the compact image shows it. This pass read the built full image the same way: every PE file in `ReactOS/system32`, `ReactOS` and `Program Files` of a read-only copy, and the two files of `system32/drivers` the trim names, 784 files and 1,147 icon groups and bitmaps, each with its languages and its frames read from the frame headers, compared with the stock files and named from the `0.4.16-release` source. It also looked at what the owner saw while using the full image: the Control Panel, User Accounts, the games, the taskbar's tray end and the Start menu.

### What the owner saw

| Seen                                                                                     | Resource                                                                                                                                                                                                                                                                             | Status                                                                                                                                                                                                  |
| ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Control Panel: Game Controllers, Phone and Modem, User Accounts                          | `joy.cpl` 102, `telephon.cpl` 100, `usrmgr.cpl` 40                                                                                                                                                                                                                                   | Art exists (`joystick`, `telephon`, `usrmgr`); the files are not in the patcher's list yet                                                                                                              |
| Control Panel: OpenGL Configuration, WineD3D Options                                     | `openglcfg.cpl` 1, `wined3dcfg.cpl` 1 (both `IDI_CPLICON`)                                                                                                                                                                                                                           | Drawn here: `openglcfg`, `wined3dcfg`                                                                                                                                                                   |
| User Accounts: the title bar and taskbar icon                                            | `usrmgr.cpl` 40 (`IDI_USRMGR_ICON`; 100 is its theme-compatibility copy)                                                                                                                                                                                                             | Art exists: `usrmgr`                                                                                                                                                                                    |
| User Accounts: Administrator, Guest (disabled) and the Groups tab                        | `usrmgr.cpl` 41 `IDI_USER`, 42 `IDI_LOCKED_USER`, 43 `IDI_GROUP`, each `16@8 16@32` only                                                                                                                                                                                             | Drawn here: `user`, `user-locked`, `group`, each with a hand-tuned 16 px frame                                                                                                                          |
| Games: Solitaire, Spider Solitaire, WineMine in the Games folder, title bars and taskbar | `sol.exe` 100, `spider.exe` 100, `winmine.exe` 1                                                                                                                                                                                                                                     | Art exists (`sol`, `spider`, `winmine`); the binaries confirm `spider` and `sndrec32`, which were `source` only                                                                                         |
| The card back with the ReactOS logo (Solitaire's deck, Spider's stock pile)              | `cards.dll` bitmap 54 (`Background_1`, 72 × 112, 8-bit): cardlib's default back (`nBackCardIdx` 53, so resource 54)                                                                                                                                                                  | Drawn here: `card-back-sunset` (and two review-only alternatives)                                                                                                                                       |
| The dark green felt and the empty-pile placeholders                                      | Code, not a resource: cardlib's `CardWindow` sets `crBackgnd = PALETTERGB(0, 80, 0)`, compiled into `sol.exe` (file offset `0x73c5`) and `spider.exe` (`0x5e09`) as the immediate of `mov dword [ebx+0x144], 0x02005000`; the sunk placeholders are drawn from it by `CreateSinkBmp` | Proposed: the dusk felt `#1f2554`; the sinks follow it. Solitaire's empty-deck ring (`cards.dll` 68) and the cross (67) carry the stock green, so they are redrawn on the dusk felt: `card-o`, `card-x` |
| The Show Desktop/Windows button: a folder                                                | `traydeskbtn.cpp` loads `imageres.dll` icon 110 and falls back to `shell32.dll` 35 (`IDI_SHELL_DESKTOP`), the Desktop folder's own icon; 0.4.16 ships no `imageres.dll`                                                                                                              | Drawn here: `showdesktop`, for a resource-only `imageres.dll` (see below)                                                                                                                               |
| The plug beside the volume icon                                                          | `stobject.dll` 413 `IDI_POWER_AC`, the mains-power tray icon                                                                                                                                                                                                                         | Afterglow already: the image's group 413 is pixel for pixel `acpower` at 16, 32 and 48 px; it is set E's gold, not a stock icon                                                                         |
| The Device Manager class icons                                                           | `setupapi.dll`'s device classes                                                                                                                                                                                                                                                      | Stock, in both images (see _Left stock on purpose_); the Bluetooth class from `bthci.dll` 201 is drawn here (`bluetooth`)                                                                               |

### Every resource of the full image's extra files

The 35 files the trim removes, then the four files in both images that the owner's full-image session showed (the console windows, Device Manager and two screen savers). Seen in says where ReactOS shows it. Icons with no number are named by string in their `.rc` file.

| File              | Id          | Type   | Name                      | Language | Frames or size                                    | Seen in                                                                   | Status                     | Art                                                       |
| ----------------- | ----------- | ------ | ------------------------- | -------- | ------------------------------------------------- | ------------------------------------------------------------------------- | -------------------------- | --------------------------------------------------------- |
| `sol.exe`         | 100         | icon   | `IDI_SOLITAIRE`           | neutral  | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32   | Games folder, title bar, taskbar                                          | **Art exists, patch only** | `sol`                                                     |
| `spider.exe`      | 100         | icon   | `IDI_SPIDER`              | neutral  | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32   | Games folder, title bar, taskbar                                          | **Art exists, patch only** | `spider`                                                  |
| `winmine.exe`     | 1           | icon   | `IDI_WINEMINE`            | neutral  | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32   | Games folder, title bar, taskbar                                          | **Art exists, patch only** | `winmine`                                                 |
| `winmine.exe`     | 2           | bitmap | `IDI_FACES`               | neutral  | 24 × 120, 4-bit                                   | WineMine                                                                  | Stock                      | the smiley button: game art, left as it is                |
| `winmine.exe`     | 3           | bitmap | `IDI_LEDS`                | neutral  | 13 × 276, 4-bit                                   | WineMine                                                                  | Stock                      | the counter digits: game art                              |
| `winmine.exe`     | 4           | bitmap | `IDI_MINES`               | neutral  | 16 × 256, 4-bit                                   | WineMine                                                                  | Stock                      | the cells, mines and flags: game art                      |
| `calc.exe`        | 110         | icon   | `IDI_CALC`                | neutral  | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32   | Accessories, title bar                                                    | **Art exists, patch only** | `calc`                                                    |
| `mspaint.exe`     | 500         | icon   | `IDI_APPICON`             | en-US    | 48@8 32@8 16@8 48@32 32@32 16@32                  | Accessories, title bar                                                    | **Art exists, patch only** | `paint`                                                   |
| `mspaint.exe`     | 526         | icon   | `IDI_TRANSPARENT`         | en-US    | 40@8                                              | Paint's tool box and Stretch and Skew dialog                              | Stock                      | a tool option picture: a candidate for the next pass      |
| `mspaint.exe`     | 527         | icon   | `IDI_NONTRANSPARENT`      | en-US    | 40@8                                              | Paint's tool box and Stretch and Skew dialog                              | Stock                      | a tool option picture: a candidate for the next pass      |
| `mspaint.exe`     | 535         | icon   | `IDI_HORZSTRETCH`         | en-US    | 32@4                                              | Paint's tool box and Stretch and Skew dialog                              | Stock                      | a tool option picture: a candidate for the next pass      |
| `mspaint.exe`     | 536         | icon   | `IDI_VERTSTRETCH`         | en-US    | 32@4                                              | Paint's tool box and Stretch and Skew dialog                              | Stock                      | a tool option picture: a candidate for the next pass      |
| `mspaint.exe`     | 537         | icon   | `IDI_HORZSKEW`            | en-US    | 32@4                                              | Paint's tool box and Stretch and Skew dialog                              | Stock                      | a tool option picture: a candidate for the next pass      |
| `mspaint.exe`     | 538         | icon   | `IDI_VERTSKEW`            | en-US    | 32@4                                              | Paint's tool box and Stretch and Skew dialog                              | Stock                      | a tool option picture: a candidate for the next pass      |
| `mspaint.exe`     | 510         | bitmap | `IDB_TOOLBARICONS`        | en-US    | 256 × 16, 24-bit                                  | Paint's tool box and text toolbar                                         | Stock                      | a toolbar strip: a candidate for the next pass            |
| `mspaint.exe`     | 511         | bitmap | `IDB_FONTSTOOLBAR`        | en-US    | 64 × 16, 24-bit                                   | Paint's tool box and text toolbar                                         | Stock                      | a toolbar strip: a candidate for the next pass            |
| `wordpad.exe`     | 102         | icon   | `IDI_WORDPAD`             | en-US    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32   | Accessories, title bar                                                    | **Art exists, patch only** | `wordpad`                                                 |
| `wordpad.exe`     | 103         | icon   | `IDI_RTFDOC`              | en-US    | 48@8 32@8 16@8 48@32 32@32 16@32                  | `.rtf` files (`rtffile\DefaultIcon` is `wordpad.exe,-103`)                | **Art exists, patch only** | `rtf`                                                     |
| `wordpad.exe`     | 100         | bitmap | `IDB_TOOLBAR`             | en-US    | 16 × 16, 4-bit                                    | WordPad's toolbars                                                        | Stock                      | a toolbar strip: a candidate for the next pass            |
| `wordpad.exe`     | 101         | bitmap | `IDB_FORMATBAR`           | en-US    | 128 × 16, 4-bit                                   | WordPad's toolbars                                                        | Stock                      | a toolbar strip: a candidate for the next pass            |
| `write.exe`       | 1           | icon   | —                         | neutral  | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32   | `write.exe` in a file list                                                | **Art exists, patch only** | `wordpad` (`also`)                                        |
| `charmap.exe`     | 100         | icon   | —                         | neutral  | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32   | System Tools, title bar                                                   | **Art exists, patch only** | `charmap`                                                 |
| `mplay32.exe`     | 10          | icon   | `IDI_MAIN`                | neutral  | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32   | Entertainment, title bar                                                  | **Art exists, patch only** | `mplay32`                                                 |
| `mplay32.exe`     | 50          | bitmap | `IDB_PLAYICON`            | neutral  | 16 × 16, 8-bit                                    | Multimedia Player's buttons                                               | Stock                      | transport button: a candidate for the next pass           |
| `mplay32.exe`     | 51          | bitmap | `IDB_STOPICON`            | neutral  | 16 × 16, 8-bit                                    | Multimedia Player's buttons                                               | Stock                      | transport button: a candidate for the next pass           |
| `mplay32.exe`     | 52          | bitmap | `IDB_EJECTICON`           | neutral  | 16 × 16, 8-bit                                    | Multimedia Player's buttons                                               | Stock                      | transport button: a candidate for the next pass           |
| `mplay32.exe`     | 53          | bitmap | `IDB_BACKWARDICON`        | neutral  | 16 × 16, 8-bit                                    | Multimedia Player's buttons                                               | Stock                      | transport button: a candidate for the next pass           |
| `mplay32.exe`     | 54          | bitmap | `IDB_SEEKBACKICON`        | neutral  | 16 × 16, 8-bit                                    | Multimedia Player's buttons                                               | Stock                      | transport button: a candidate for the next pass           |
| `mplay32.exe`     | 55          | bitmap | `IDB_SEEKFORWICON`        | neutral  | 16 × 16, 8-bit                                    | Multimedia Player's buttons                                               | Stock                      | transport button: a candidate for the next pass           |
| `mplay32.exe`     | 56          | bitmap | `IDB_FORWARDICON`         | neutral  | 16 × 16, 8-bit                                    | Multimedia Player's buttons                                               | Stock                      | transport button: a candidate for the next pass           |
| `mplay32.exe`     | 57          | bitmap | `IDB_PAUSEICON`           | neutral  | 16 × 16, 8-bit                                    | Multimedia Player's buttons                                               | Stock                      | transport button: a candidate for the next pass           |
| `sndrec32.exe`    | 107         | icon   | —                         | neutral  | 48@4 32@4 16@4 48@24 32@24 16@8 48@32 32@32 16@32 | Entertainment, title bar                                                  | **Art exists, patch only** | `sndrec32`                                                |
| `sndrec32.exe`    | 8           | bitmap | —                         | neutral  | 59 × 29, 32-bit                                   | Sound Recorder's buttons                                                  | Stock                      | transport button: a candidate for the next pass           |
| `sndrec32.exe`    | 133         | bitmap | —                         | neutral  | 59 × 29, 32-bit                                   | Sound Recorder's buttons                                                  | Stock                      | transport button: a candidate for the next pass           |
| `sndrec32.exe`    | 134         | bitmap | —                         | neutral  | 59 × 29, 32-bit                                   | Sound Recorder's buttons                                                  | Stock                      | transport button: a candidate for the next pass           |
| `sndrec32.exe`    | 135         | bitmap | —                         | neutral  | 59 × 29, 32-bit                                   | Sound Recorder's buttons                                                  | Stock                      | transport button: a candidate for the next pass           |
| `sndrec32.exe`    | 136         | bitmap | —                         | neutral  | 59 × 29, 32-bit                                   | Sound Recorder's buttons                                                  | Stock                      | transport button: a candidate for the next pass           |
| `sndrec32.exe`    | 137         | bitmap | —                         | neutral  | 59 × 29, 32-bit                                   | Sound Recorder's buttons                                                  | Stock                      | transport button: a candidate for the next pass           |
| `sndrec32.exe`    | 141         | bitmap | —                         | neutral  | 59 × 29, 32-bit                                   | Sound Recorder's buttons                                                  | Stock                      | transport button: a candidate for the next pass           |
| `sndrec32.exe`    | 142         | bitmap | —                         | neutral  | 59 × 29, 32-bit                                   | Sound Recorder's buttons                                                  | Stock                      | transport button: a candidate for the next pass           |
| `sndrec32.exe`    | 143         | bitmap | —                         | neutral  | 59 × 29, 32-bit                                   | Sound Recorder's buttons                                                  | Stock                      | transport button: a candidate for the next pass           |
| `sndrec32.exe`    | 144         | bitmap | —                         | neutral  | 59 × 29, 32-bit                                   | Sound Recorder's buttons                                                  | Stock                      | transport button: a candidate for the next pass           |
| `dxdiag.exe`      | 20000       | icon   | `IDI_APPICON`             | neutral  | 48@4 32@4 16@4 16@8 48@8 32@8 48@32 32@32 16@32   | System Tools, title bar                                                   | **Art exists, patch only** | `dxdiag`                                                  |
| `mstsc.exe`       | 2000        | icon   | `IDI_MSTSC`               | en-US    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32   | Communications, title bar, `.rdp` files                                   | **Art exists, patch only** | `mstsc`                                                   |
| `mstsc.exe`       | 2001        | icon   | `IDI_LOGON`               | en-US    | 32@4 32@8 32@32                                   | Remote Desktop Connection, General tab                                    | **Drawn here**             | `rdp-logon`                                               |
| `mstsc.exe`       | 2002        | icon   | `IDI_CONN`                | en-US    | 32@4 32@8 32@32                                   | Remote Desktop Connection, General tab                                    | **Drawn here**             | `rdp-connection`                                          |
| `mstsc.exe`       | 2003        | icon   | `IDI_REMOTE`              | en-US    | 24@8 16@8 32@8 32@4 32@8 32@32                    | Remote Desktop Connection, Display tab                                    | **Drawn here**             | `rdp-display`                                             |
| `mstsc.exe`       | 2004        | icon   | `IDI_COLORS`              | en-US    | 32@4 32@8 32@32                                   | Remote Desktop Connection, Display tab                                    | **Drawn here**             | `rdp-colours`                                             |
| `mstsc.exe`       | 1100        | bitmap | `IDB_HEADER`              | en-US    | 390 × 70, 24-bit                                  | Remote Desktop Connection                                                 | Stock                      | the dialog's header banner: a candidate for the next pass |
| `mstsc.exe`       | 1101        | bitmap | `IDB_SPECT`               | en-US    | 154 × 14, 24-bit                                  | Remote Desktop Connection, Display tab                                    | Stock                      | the colour-depth scale: functional                        |
| `magnify.exe`     | 101         | icon   | —                         | neutral  | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32   | Accessibility, title bar                                                  | **Art exists, patch only** | `magnify`                                                 |
| `osk.exe`         | 200         | icon   | —                         | en-US    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32   | Accessibility, title bar                                                  | **Art exists, patch only** | `osk`                                                     |
| `osk.exe`         | 201         | icon   | —                         | en-US    | 16@4                                              | On-Screen Keyboard's keys                                                 | Stock                      | a key glyph: functional                                   |
| `osk.exe`         | 202         | icon   | —                         | en-US    | 16@4                                              | On-Screen Keyboard's keys                                                 | Stock                      | a key glyph: functional                                   |
| `osk.exe`         | 203         | icon   | —                         | en-US    | 16@4                                              | On-Screen Keyboard's keys                                                 | Stock                      | a key glyph: functional                                   |
| `osk.exe`         | 204         | icon   | —                         | en-US    | 16@4                                              | On-Screen Keyboard's keys                                                 | Stock                      | a key glyph: functional                                   |
| `osk.exe`         | 205         | icon   | —                         | en-US    | 16@4                                              | On-Screen Keyboard's keys                                                 | Stock                      | a key glyph: functional                                   |
| `osk.exe`         | 206         | icon   | —                         | en-US    | 16@8 16@4 16@32                                   | On-Screen Keyboard's keys                                                 | Stock                      | a key glyph: functional                                   |
| `osk.exe`         | 207         | icon   | —                         | en-US    | 16@4                                              | On-Screen Keyboard's keys                                                 | Stock                      | a key glyph: functional                                   |
| `osk.exe`         | 208         | icon   | —                         | en-US    | 16@4                                              | On-Screen Keyboard's keys                                                 | Stock                      | a key glyph: functional                                   |
| `osk.exe`         | 209         | icon   | —                         | en-US    | 16@4                                              | On-Screen Keyboard's keys                                                 | Stock                      | a key glyph: functional                                   |
| `osk.exe`         | 210         | icon   | —                         | en-US    | 16@4                                              | On-Screen Keyboard's keys                                                 | Stock                      | a key glyph: functional                                   |
| `osk.exe`         | 211         | icon   | —                         | en-US    | 16@4                                              | On-Screen Keyboard's keys                                                 | Stock                      | a key glyph: functional                                   |
| `osk.exe`         | 212         | icon   | —                         | en-US    | 16@4                                              | On-Screen Keyboard's keys                                                 | Stock                      | a key glyph: functional                                   |
| `osk.exe`         | 213         | icon   | —                         | en-US    | 16@4                                              | On-Screen Keyboard's keys                                                 | Stock                      | a key glyph: functional                                   |
| `osk.exe`         | 214         | icon   | —                         | en-US    | 16@4                                              | On-Screen Keyboard's keys                                                 | Stock                      | a key glyph: functional                                   |
| `mmc.exe`         | 101         | icon   | `IDI_MAINAPP`             | en-US    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32   | title bar, taskbar (no Start menu shortcut)                               | **Drawn here**             | `mmc`                                                     |
| `progman.exe`     | 1           | icon   | `IDI_APPICON`             | neutral  | 48@8 32@8 16@8 48@32 32@32 16@32                  | title bar, taskbar (no Start menu shortcut)                               | **Drawn here**             | `progman`                                                 |
| `progman.exe`     | 8           | icon   | `IDI_GROUP_PERSONAL_ICON` | neutral  | 32@8 16@8 32@32 16@32                             | Program Manager's groups                                                  | **Drawn here**             | `programs` (`also`)                                       |
| `progman.exe`     | 9           | icon   | `IDI_GROUP_COMMON_ICON`   | neutral  | 32@8 16@8 32@32 16@32                             | Program Manager's groups                                                  | **Drawn here**             | `programs` (`also`)                                       |
| `progman.exe`     | 10          | icon   | `IDI_ROSLOGO`             | neutral  | 32@4 16@4 32@8 16@8 32@32 16@32                   | Program Manager                                                           | Stock                      | the ReactOS logo: left as it is by the branding rule      |
| `progman.exe`     | 48          | icon   | `IDI_GROUP_ICON`          | neutral  | 32@8 16@8 32@32 16@32                             | Program Manager's groups                                                  | **Drawn here**             | `programs` (`also`)                                       |
| `progman.exe`     | 49          | icon   | `IDI_TERMINAL`            | neutral  | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32   | Program Manager's console programs                                        | **Drawn here**             | `console-app` (`also`)                                    |
| `screenshot.exe`  | 1           | icon   | `IDI_ICON`                | en-US    | 48@8 32@8 16@8 48@32 32@32 16@32                  | System Tools: SnapShot, title bar                                         | **Drawn here**             | `snapshot`                                                |
| `telnet.exe`      | IDI_APPICON | icon   | `IDI_APPICON`             | neutral  | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4   | title bar, taskbar                                                        | **Drawn here**             | `telnet`                                                  |
| `joy.cpl`         | 102         | icon   | `IDI_CPLSYSTEM`           | neutral  | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32   | Control Panel: Game Controllers                                           | **Art exists, patch only** | `joystick`                                                |
| `telephon.cpl`    | 100         | icon   | `IDI_CPLSYSTEM`           | neutral  | 32@8 16@8 32@32 16@8                              | Control Panel: Phone and Modem                                            | **Art exists, patch only** | `telephon`                                                |
| `usrmgr.cpl`      | 40          | icon   | `IDI_USRMGR_ICON`         | neutral  | 48@8 32@8 16@8 48@32 32@32 16@32                  | Control Panel: User Accounts; the dialog's title bar and taskbar          | **Art exists, patch only** | `usrmgr`                                                  |
| `usrmgr.cpl`      | 41          | icon   | `IDI_USER`                | neutral  | 16@8 16@32                                        | User Accounts, Users tab (Administrator)                                  | **Drawn here**             | `user`                                                    |
| `usrmgr.cpl`      | 42          | icon   | `IDI_LOCKED_USER`         | neutral  | 16@8 16@32                                        | User Accounts, Users tab (Guest, disabled)                                | **Drawn here**             | `user-locked`                                             |
| `usrmgr.cpl`      | 43          | icon   | `IDI_GROUP`               | neutral  | 16@8 16@32                                        | User Accounts, Groups tab                                                 | **Drawn here**             | `group`                                                   |
| `usrmgr.cpl`      | 100         | icon   | `IDI_USRMGR_ICON2`        | neutral  | 48@8 32@8 16@8 48@32 32@32 16@32                  | the theme-compatibility copy                                              | **Art exists, patch only** | `usrmgr` (`also`)                                         |
| `openglcfg.cpl`   | 1           | icon   | `IDI_CPLICON`             | neutral  | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32   | Control Panel: OpenGL Configuration                                       | **Drawn here**             | `openglcfg`                                               |
| `wined3dcfg.cpl`  | 1           | icon   | `IDI_CPLICON`             | neutral  | 16@8 32@8 48@8 16@32 32@32 48@32                  | Control Panel: WineD3D Options                                            | **Drawn here**             | `wined3dcfg`                                              |
| `3dtext.scr`      | 101         | icon   | `IDI_ICON`                | neutral  | 48@32 32@32 24@32 16@32                           | a file list (`.scr` takes its own icon)                                   | **Drawn here**             | `scr-3dtext`                                              |
| `butterflies.scr` | 106         | icon   | `IDI_ICON`                | neutral  | 48@32 32@32 16@32                                 | a file list                                                               | **Drawn here**             | `scr-butterflies`                                         |
| `butterflies.scr` | 103         | bitmap | `IDB_BUTTERFLY1`          | neutral  | 128 × 128, 24-bit                                 | the screen saver running                                                  | Stock                      | the screen saver's own picture                            |
| `butterflies.scr` | 104         | bitmap | `IDB_BUTTERFLY2`          | neutral  | 128 × 128, 24-bit                                 | the screen saver running                                                  | Stock                      | the screen saver's own picture                            |
| `butterflies.scr` | 105         | bitmap | `IDB_BUTTERFLY3`          | neutral  | 128 × 128, 24-bit                                 | the screen saver running                                                  | Stock                      | the screen saver's own picture                            |
| `circles.scr`     | 101         | icon   | `IDI_ICON`                | neutral  | 48@32 32@32 16@32                                 | a file list                                                               | **Drawn here**             | `scr-circles`                                             |
| `cylfrac.scr`     | 101         | icon   | `IDI_ICON`                | neutral  | 48@32 32@32 16@32                                 | a file list                                                               | **Drawn here**             | `scr-cylfrac`                                             |
| `matrix.scr`      | 106         | icon   | `IDI_ICON1`               | neutral  | 32@8 16@8 32@32                                   | a file list                                                               | **Drawn here**             | `scr-matrix`                                              |
| `matrix.scr`      | 104         | bitmap | `IDB_BITMAP1`             | neutral  | 364 × 84, 8-bit                                   | the screen saver running                                                  | Stock                      | the screen saver's own picture                            |
| `mazescr.scr`     | 101         | icon   | `IDI_ICON`                | neutral  | 48@32 32@32 16@32                                 | a file list                                                               | **Drawn here**             | `scr-maze`                                                |
| `ssstars.scr`     | 101         | icon   | `IDI_STARFIELD`           | neutral  | 32@8                                              | a file list                                                               | **Drawn here**             | `scr-ssstars`                                             |
| `ssstars.scr`     | 102         | bitmap | `IDB_COSMOS`              | neutral  | 420 × 148, 8-bit                                  | the screen saver running                                                  | Stock                      | the screen saver's own picture                            |
| `ssstars.scr`     | 103         | bitmap | `IDB_STAR`                | neutral  | 128 × 128, 8-bit                                  | the screen saver running                                                  | Stock                      | the screen saver's own picture                            |
| `starfield.scr`   | 101         | icon   | `IDI_ICON`                | neutral  | 48@32 32@32 16@32                                 | a file list                                                               | **Drawn here**             | `scr-starfield`                                           |
| `vgafontedit.exe` | 100         | icon   | —                         | neutral  | 48@4 32@4 16@4                                    | VGA Font Editor                                                           | Stock                      | a developer tool with no shortcut                         |
| `vgafontedit.exe` | 101         | icon   | —                         | neutral  | 16@4                                              | VGA Font Editor                                                           | Stock                      | a developer tool with no shortcut                         |
| `vgafontedit.exe` | 401         | bitmap | —                         | neutral  | 16 × 16, 4-bit                                    | VGA Font Editor                                                           | Stock                      | a developer tool with no shortcut                         |
| `vgafontedit.exe` | 402         | bitmap | —                         | neutral  | 24 × 24, 4-bit                                    | VGA Font Editor                                                           | Stock                      | a developer tool with no shortcut                         |
| `shellbtrfs.dll`  | 101         | icon   | —                         | 2057     | 16@32 32@32 64@32 128@32 13@32png                 | Btrfs properties                                                          | Stock                      | shown only with a Btrfs volume                            |
| `cmicpl.cpl`      | 100         | icon   | `IDI_CPLICON`             | en-US    | 16@8 128@32 48@32 32@32                           | Control Panel, with the driver                                            | Stock                      | shown only with a C-Media CMI8738 card                    |
| `cmicontrol.exe`  | 150         | icon   | `IDI_APP_ICON`            | en-US    | 16@8 128@32 48@32 32@32                           | CMI control program                                                       | Stock                      | shown only with a C-Media CMI8738 card                    |
| `blankscr.scr`    | 101         | icon   | `IDI_ICON`                | neutral  | 48@32 32@32 16@32                                 | a file list (in the compact image too)                                    | **Drawn here**             | `scr-blank`                                               |
| `logon.scr`       | IDI_ICON    | icon   | `IDI_ICON`                | neutral  | 48@32 32@32 16@32                                 | a file list (in the compact image too)                                    | **Drawn here**             | `scr-logon`                                               |
| `logon.scr`       | 256         | bitmap | `IDB_WORKSTATION`         | neutral  | 205 × 164, 24-bit                                 | the Logon screen saver (in the compact image too)                         | Stock                      | the ReactOS logo: left as it is by the branding rule      |
| `logon.scr`       | 512         | bitmap | `IDB_SERVER`              | neutral  | 205 × 164, 24-bit                                 | the Logon screen saver (in the compact image too)                         | Stock                      | the ReactOS logo: left as it is by the branding rule      |
| `winsrv.dll`      | 1           | icon   | `IDI_TERMINAL`            | neutral  | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32   | every console window whose program has no icon (in the compact image too) | **Drawn here**             | `console-app`                                             |
| `bthci.dll`       | 201         | icon   | `IDI_BLUETOOTH`           | neutral  | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32   | Device Manager, the Bluetooth class (in the compact image too)            | **Drawn here**             | `bluetooth`                                               |

Of the 111 resources here, 19 already have Afterglow art and only need patching, 29 are drawn or mapped here, and 63 stay stock: the games' own sprites, the screen savers' pictures, the key glyphs of the On-Screen Keyboard, three toolbar strips and button sets that are candidates for the next pass (Paint, WordPad, Multimedia Player, Sound Recorder and Remote Desktop's header), the ReactOS logo in `progman.exe` 10 and `logon.scr`, and tools ReactOS shows only with hardware or volumes the image does not have. `cards.dll` adds 68 bitmaps: 52 faces, `FreeCard` (53), eleven neutral backs (55 to 65) and the Joker (66) stay as they are; 54, 67 and 68 are drawn here.

Files with no icon of their own show something else: the console programs (`ftp.exe`, `telnetd.exe`, `tftpd.exe`, `roshttpd.exe`, `ncftp.exe`, `rosperf.exe`, `gdb2.exe`, `regexpl.exe`, `vfd.exe`, `vcdcli.exe`, `wlanconf.exe`) take consrv's default console icon (`winsrv.dll` 1, `console-app`) in their title bar and on the taskbar, and `program` (`shell32.dll` 3) in a file list; `maze.exe` and `vcdcontroltool.exe` take `program`; `bthprops.cpl` registers no applet the Control Panel lists. The file types the extra programs register are `.rtf` (`wordpad.exe,-103`, art `rtf`), `.rdp` (`mstsc.exe,0`, art `mstsc`) and `.scr` (`%1`, each screen saver's own icon, drawn here); `.bmp`, `.wav`, `.avi` and `.mid` keep their `shimgvw.dll` and `shell32.dll` icons, which are Afterglow already.

### The Show Desktop button

The button asks for `imageres.dll` first (`ExtractIconExW(L"imageres.dll", -110, NULL, &icon, 1)`, the 16 px small icon) and only then for `shell32.dll` 35, which is the Desktop folder's icon (`desktop`) and is shared with the Desktop item in every folder tree. Nothing else in 0.4.16 loads `imageres.dll`. So the least invasive patch is a new resource-only `system32/imageres.dll` holding icon group 110 with `showdesktop`'s frames: `shell32.dll` stays as it is, `agexplorer.exe` needs no code change, and removing the file restores the stock behaviour. The button draws at `SM_CXSMICON` (16 px) on the dark taskbar, so `showdesktop` has a hand-tuned 16 px frame whose light bezel reaches 3:1 on the taskbar; it ships without the keyline, which is for light grounds.

### The cards and the felt

Solitaire and Spider Solitaire share cardlib, which loads all 68 `cards.dll` bitmaps with `LoadBitmap`, copies each into one screen-compatible strip with `BitBlt`, paints a black border over each card's outer pixel ring and leaves out the corner pixels. The art is drawn to that: `card-back-sunset` fills the whole 72 × 112 bitmap and keeps its detail inside the ring. The stock bitmaps are 8-bit; the Afterglow ones are 24-bit at the same size, which `BitBlt` copies the same way, so the patch places them in a new section as the icon patches do. The felt is the one value in code: writing `1f 25 54 02` over `00 50 00 02` at the two offsets above makes it `PALETTERGB(0x1f, 0x25, 0x54)`, and cardlib then draws the empty-pile sinks from it. `map.json`'s `colours` list records both sites. See [the card art](reactos-desktop-cards.md).

### For the builder

The files to add to the patcher's families (all stock 0.4.16 i386, as the full image holds them):

| File                              | Size      | SHA-256                                                            |
| --------------------------------- | --------- | ------------------------------------------------------------------ |
| `system32/sol.exe`                | 256,000   | `a3458ec0f12199c0aca5ea319c0c15f481e607a3ad4318466ae278a00fd4a131` |
| `system32/spider.exe`             | 218,624   | `e13be1bfb78b7f3f9779e22b2265e1880456c7c4d9d2f4d4a8761c2cb593f0ac` |
| `system32/winmine.exe`            | 1,159,168 | `03e87561e90cc5e11a53bd6f3b31da2c01f1d920310fb62dd5898e04c431cbed` |
| `system32/calc.exe`               | 526,336   | `6e7f0d03e1afd01a25d29bfa8834a71b5323ca94c579d0e2041875b4ed099b1e` |
| `system32/mspaint.exe`            | 1,021,440 | `f1c5ce159d419fe9a265f9e9fa3321a9aa3a8f3f5c6ccc8304796354e551d9a2` |
| `system32/wordpad.exe`            | 371,712   | `02427cf826dc027be68c1db994ff03a95351e3574b814793a6563440f44eb2cb` |
| `system32/write.exe`              | 59,392    | `76234577f9ce4afe98ee4f5ef53026cc0402c7508a1e67be07ee05112757937c` |
| `system32/charmap.exe`            | 182,784   | `54e6db22fe77184c4963a3c2f73f4308681393b60a1ff41e191e4dcc703f98ec` |
| `system32/mplay32.exe`            | 125,952   | `c79be89b2d4a3fa28334afeb01b1d39980be1c5e915c8bb618c6e9304028c9b4` |
| `system32/sndrec32.exe`           | 227,328   | `30fb6e5bb99c609f5dbe32a942009eee8715d8061351f5de4e943459af47684b` |
| `system32/dxdiag.exe`             | 405,504   | `eb1d92a925fcb16efb58fe9e9523c77e0886ddcd032e1416d400646008fe24ea` |
| `system32/mstsc.exe`              | 524,800   | `8db81358f80f1ca31364a52b21d859831da484106da2c773838f2c5c7036bacb` |
| `system32/magnify.exe`            | 132,608   | `a17c8c00a14594f00859534013703bf50d0d9e3504a395b2d31e78e82597a72a` |
| `system32/osk.exe`                | 156,160   | `a7a25a8033cd059ec0ec7b1973e822a4af614f137584c9cd0ca1f79e0c16b26e` |
| `system32/mmc.exe`                | 87,040    | `7e2ad31ad98fd150114d0e31c238ffc9245280cc2da5e6fb9dd05ec38fc01520` |
| `system32/progman.exe`            | 192,512   | `183d52f60b6cc604e4f1476a44db425dede2647aaed6a51f038c0a1d27090f9c` |
| `system32/screenshot.exe`         | 59,392    | `618296616d7f85df8ba1f0286e6480997e8db570b55edd6a72c94c6827577d5a` |
| `system32/telnet.exe`             | 941,568   | `db7e91493c4adbed8c16f51a1ca8b4015cbd57fc1af1f3d30e272605fa46c7e5` |
| `system32/joy.cpl`                | 144,384   | `8f2131e2b93cf0aeac3138943bcce6246bb9c5297890a244c23ac1fb4e150cc0` |
| `system32/telephon.cpl`           | 46,592    | `6306332ded6c69832163e15d1f570ecb6985aed22292281e3d927dfb8198c5f6` |
| `system32/usrmgr.cpl`             | 253,440   | `54dc9239c9c36f1653860ab3a1e781aeedc3d5e4f7f638e84277cf811ced778c` |
| `system32/openglcfg.cpl`          | 79,872    | `191c2c36024a6b5571384d55999e03c4e5364668baaa2319acb69a6e99dd4523` |
| `system32/wined3dcfg.cpl`         | 80,384    | `6e5d61a0c49216152e493f27ac93fbf05b30a21429f7ad039bddfd2f5799cb59` |
| `system32/3dtext.scr`             | 77,312    | `ac12143afe60a890b2f1e0bd34389eb75f94c0315a554eaeecb77fdce532b557` |
| `system32/butterflies.scr`        | 228,864   | `b47d552fd1fc92f2e2ebc041fa0a3935a30d606f9438cc69eaa78bfa68b0ee08` |
| `system32/circles.scr`            | 56,832    | `10992239b7a1734f3648830ae5a06a1fe475030e149864eb1933c0738f313e99` |
| `system32/cylfrac.scr`            | 64,000    | `3002ea5c9ac1cffa7458ddba5c188d0b6f3ee00f851fa7ddf507333d2073adda` |
| `system32/matrix.scr`             | 139,264   | `a93f68763fc7c4fd80e0fddf55ece26801a505ed19b095f60c0f2d6b563c409d` |
| `system32/mazescr.scr`            | 98,304    | `175ebfba0d3014867f9ef831385e755dabdb3b39aacdad46ba16facb8f9edb47` |
| `system32/ssstars.scr`            | 158,720   | `fd71646a0fe8d70fa6bc6e1f4ec31c8d0b6d7d81b0377aafb6b088ff198a893f` |
| `system32/starfield.scr`          | 59,392    | `f2fbc7703fc5540916edeffd9f029bad830c81f925c36ee2f451affa9ffe5b23` |
| `system32/vgafontedit.exe`        | 117,248   | `1307626f77dc083d50603d4ef0cb9bfdf77d0aadff545bd5189ef865f3b7dc9d` |
| `system32/shellbtrfs.dll`         | 2,127,360 | `35e2266c92bd65e41b758d747482d9dc118c02166c73894413116aa70209461c` |
| `system32/drivers/cmicpl.cpl`     | 114,688   | `6d01ca92da37878202a370fa76910877d5cc17db9d30e9a999642c3877905008` |
| `system32/drivers/cmicontrol.exe` | 156,160   | `30ea6b1c53b1854c0d5f64606eb3b91d1276740c76ece321c51288263b39124f` |
| `system32/blankscr.scr`           | 55,296    | `3eb6abd70e6119fec8e45ef39342cd09d486f33d8a7b4d4620bd50c448dd174d` |
| `system32/logon.scr`              | 262,656   | `8854a5f9e239d96413c60bd0185847ead1a9d33dbfbf64dba8cf96098ec6e05d` |
| `system32/winsrv.dll`             | 630,784   | `2c7cdb84fa47ce45062439ecfd2ef2fb9c742dfe06f26afce7cc9b6c4089e9c3` |
| `system32/bthci.dll`              | 55,808    | `1f7ed85962e65cd9141be4106c9691255956146cabd852991c4344f28e3050b5` |

- **Icon groups (art exists).** `sol.exe` 100, `spider.exe` 100, `winmine.exe` 1, `calc.exe` 110, `mspaint.exe` 500, `wordpad.exe` 102 and 103, `write.exe` 1, `charmap.exe` 100, `mplay32.exe` 10, `sndrec32.exe` 107, `dxdiag.exe` 20000, `mstsc.exe` 2000, `magnify.exe` 101, `osk.exe` 200, `joy.cpl` 102, `telephon.cpl` 100, `usrmgr.cpl` 40 and 100.
- **Icon groups (drawn here).** `usrmgr.cpl` 41, 42, 43 (`16@8 16@32`: fitted to 16 and 32), `openglcfg.cpl` 1, `wined3dcfg.cpl` 1, `mmc.exe` 101 (language en-US), `progman.exe` 1, 8, 9, 48 and 49, `screenshot.exe` 1, `telnet.exe` `IDI_APPICON` (a named group), `mstsc.exe` 2001 to 2004, the ten screen savers (`3dtext.scr` 101, `blankscr.scr` 101, `butterflies.scr` 106, `circles.scr` 101, `cylfrac.scr` 101, `logon.scr` `IDI_ICON`, `matrix.scr` 106, `mazescr.scr` 101, `ssstars.scr` 101 (one `32@8` frame: fitted), `starfield.scr` 101), `winsrv.dll` 1 and `bthci.dll` 201.
- **A new file.** `system32/imageres.dll`, resource-only, with icon group 110 from `ico/showdesktop.ico`.
- **Bitmaps.** `cards.dll` 54, 67 and 68 from `desktop/cards` (`card-back-sunset.bmp`, `card-x.bmp`, `card-o.bmp`), 72 × 112, 24-bit.
- **Code.** The felt colour in `sol.exe` and `spider.exe` (two four-byte writes); 67 and 68 are drawn on the dusk felt, so they go with it.

## Every resource

The full sweep, by file. _Shown by_ is the dialog template or source file that names the id in the 0.4.16 source (empty when the source does not name it directly: a resource the shell or another module loads by number, or none). Frames are `size@bits per pixel` in stock order.

### `system32/3dtext.scr` (removed by the `base` trim)

| Id  | Type | Name | Frames or size          | Shown by | Status  |
| --- | ---- | ---- | ----------------------- | -------- | ------- |
| 101 | icon | —    | 48@32 32@32 24@32 16@32 | —        | Trimmed |

### `system32/access.cpl`

| Id  | Type | Name            | Frames or size                                  | Shown by | Status               |
| --- | ---- | --------------- | ----------------------------------------------- | -------- | -------------------- |
| 110 | icon | `IDI_CPLACCESS` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | access.c | Afterglow (`access`) |

### `system32/aclui.dll`

| Id   | Type   | Name | Frames or size  | Shown by | Status |
| ---- | ------ | ---- | --------------- | -------- | ------ |
| 1001 | bitmap | —    | 48 × 16, 24-bit | —        | Stock  |

### `system32/appwiz.cpl`

| Id   | Type   | Name              | Frames or size                                  | Shown by     | Status                  |
| ---- | ------ | ----------------- | ----------------------------------------------- | ------------ | ----------------------- |
| 1500 | icon   | `IDI_CPLSYSTEM`   | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | appwiz.c     | Afterglow (`addremove`) |
| 1501 | icon   | `IDI_APPICO`      | 32@8 32@32                                      | —            | Stock                   |
| 1502 | icon   | `IDI_INSTICO`     | 32@8 32@32                                      | —            | Stock                   |
| 1503 | icon   | `IDI_RECBINICO`   | 32@8 32@32                                      | —            | Stock                   |
| 1504 | icon   | `IDI_DOWNLOADICO` | 32@8 32@32                                      | —            | Stock                   |
| 1505 | icon   | `IDI_APPINETICO`  | 32@32 32@8 16@8 16@32                           | createlink.c | Stock                   |
| 5001 | bitmap | `IDB_WATERMARK`   | 164 × 400, 8-bit                                | —            | Stock                   |
| 5002 | bitmap | `IDB_SHORTCUT`    | 164 × 400, 8-bit                                | createlink.c | Stock                   |

### `system32/batt.dll`

| Id  | Type | Name | Frames or size | Shown by | Status |
| --- | ---- | ---- | -------------- | -------- | ------ |
| 2   | icon | —    | 32@32 16@32    | —        | Stock  |

### `system32/blankscr.scr`

| Id  | Type | Name | Frames or size    | Shown by | Status |
| --- | ---- | ---- | ----------------- | -------- | ------ |
| 101 | icon | —    | 48@32 32@32 16@32 | —        | Stock  |

### `system32/browseui.dll`

| Id  | Type   | Name                        | Frames or size               | Shown by        | Status                      |
| --- | ------ | --------------------------- | ---------------------------- | --------------- | --------------------------- |
| 214 | bitmap | `IDB_SHELL_EXPLORER_LG`     | 1128 × 24, 32-bit            | toolsband.cpp   | Afterglow (`toolbar cells`) |
| 215 | bitmap | `IDB_SHELL_EXPLORER_LG_HOT` | 1128 × 24, 32-bit            | toolsband.cpp   | Afterglow (`toolbar cells`) |
| 216 | bitmap | `IDB_SHELL_EXPLORER_SM`     | 752 × 16, 32-bit             | —               | Afterglow (`toolbar cells`) |
| 217 | bitmap | `IDB_SHELL_EXPLORER_SM_HOT` | 752 × 16, 32-bit             | —               | Afterglow (`toolbar cells`) |
| 230 | bitmap | `IDB_SHELL_GO`              | 20 × 20, 32-bit              | —               | Stock                       |
| 231 | bitmap | `IDB_SHELL_GO_HOT`          | 20 × 20, 32-bit              | —               | Stock                       |
| 240 | bitmap | `IDB_SHELL_BRANDBAND_SM_HI` | 22 × 704, 32-bit, compressed | —               | Stock                       |
| 545 | bitmap | `IDB_BANDBUTTONS`           | 39 × 11, 24-bit              | basebarsite.cpp | Stock                       |

### `system32/bthci.dll`

| Id  | Type | Name | Frames or size                                  | Shown by | Status |
| --- | ---- | ---- | ----------------------------------------------- | -------- | ------ |
| 201 | icon | —    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Stock  |

### `system32/butterflies.scr` (removed by the `base` trim)

| Id  | Type   | Name | Frames or size    | Shown by | Status  |
| --- | ------ | ---- | ----------------- | -------- | ------- |
| 106 | icon   | —    | 48@32 32@32 16@32 | —        | Trimmed |
| 103 | bitmap | —    | 128 × 128, 24-bit | —        | Trimmed |
| 104 | bitmap | —    | 128 × 128, 24-bit | —        | Trimmed |
| 105 | bitmap | —    | 128 × 128, 24-bit | —        | Trimmed |

### `system32/cabview.dll`

| Id  | Type | Name         | Frames or size                    | Shown by | Status                |
| --- | ---- | ------------ | --------------------------------- | -------- | --------------------- |
| 1   | icon | `IDI_FOLDER` | 48@24 32@8 16@8 48@32 32@32 16@32 | —        | Afterglow (`archive`) |

### `system32/calc.exe` (removed by the `base` trim)

| Id  | Type | Name       | Frames or size                                  | Shown by  | Status                |
| --- | ---- | ---------- | ----------------------------------------------- | --------- | --------------------- |
| 110 | icon | `IDI_CALC` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | winmain.c | Trimmed (art: `calc`) |

### `system32/cards.dll`

| Id  | Type   | Name | Frames or size  | Shown by | Status |
| --- | ------ | ---- | --------------- | -------- | ------ |
| 1   | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 2   | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 3   | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 4   | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 5   | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 6   | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 7   | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 8   | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 9   | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 10  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 11  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 12  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 13  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 14  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 15  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 16  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 17  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 18  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 19  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 20  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 21  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 22  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 23  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 24  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 25  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 26  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 27  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 28  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 29  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 30  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 31  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 32  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 33  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 34  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 35  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 36  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 37  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 38  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 39  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 40  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 41  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 42  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 43  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 44  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 45  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 46  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 47  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 48  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 49  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 50  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 51  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 52  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 53  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 54  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 55  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 56  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 57  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 58  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 59  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 60  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 61  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 62  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 63  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 64  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 65  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 66  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 67  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |
| 68  | bitmap | —    | 72 × 112, 8-bit | —        | Stock  |

### `system32/certmgr.exe`

| Id  | Type | Name | Frames or size        | Shown by | Status |
| --- | ---- | ---- | --------------------- | -------- | ------ |
| 100 | icon | —    | 16@8 32@8 16@32 32@32 | —        | Stock  |

### `system32/charmap.exe` (removed by the `base` trim)

| Id  | Type | Name | Frames or size                                  | Shown by | Status                   |
| --- | ---- | ---- | ----------------------------------------------- | -------- | ------------------------ |
| 100 | icon | —    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Trimmed (art: `charmap`) |

### `system32/circles.scr` (removed by the `base` trim)

| Id  | Type | Name | Frames or size    | Shown by | Status  |
| --- | ---- | ---- | ----------------- | -------- | ------- |
| 101 | icon | —    | 48@32 32@32 16@32 | —        | Trimmed |

### `system32/cleanmgr.exe`

| Id  | Type | Name           | Frames or size                                    | Shown by              | Status |
| --- | ---- | -------------- | ------------------------------------------------- | --------------------- | ------ |
| 100 | icon | `IDI_CLEANMGR` | 32@4 16@4 48@8 32@8 16@8 256@32 48@32 32@32 16@32 | cleanmgr/cleanmgr.cpp | Stock  |

### `system32/clipbrd.exe`

| Id  | Type | Name           | Frames or size                                  | Shown by  | Status                          |
| --- | ---- | -------------- | ----------------------------------------------- | --------- | ------------------------------- |
| 100 | icon | `CLIPBRD_ICON` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | clipbrd.c | **Stock, art ready**: `clipbrd` |
| 101 | icon | `CLPFILE_ICON` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —         | Stock                           |

### `system32/cmd.exe`

| Id  | Type | Name | Frames or size                                  | Shown by | Status            |
| --- | ---- | ---- | ----------------------------------------------- | -------- | ----------------- |
| 1   | icon | —    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Afterglow (`cmd`) |

### `system32/comctl32.dll`

| Id  | Type   | Name | Frames or size               | Shown by | Status |
| --- | ------ | ---- | ---------------------------- | -------- | ------ |
| 22  | icon   | —    | 16@32 16@8 16@4              | —        | Stock  |
| 25  | icon   | —    | 16@32 16@8 16@4              | —        | Stock  |
| 28  | icon   | —    | 16@32 16@8 16@4              | —        | Stock  |
| 501 | icon   | —    | 32@1                         | —        | Stock  |
| 120 | bitmap | —    | 240 × 16, 32-bit, compressed | —        | Stock  |
| 121 | bitmap | —    | 360 × 24, 32-bit, compressed | —        | Stock  |
| 124 | bitmap | —    | 192 × 16, 32-bit, compressed | —        | Stock  |
| 125 | bitmap | —    | 288 × 24, 32-bit, compressed | —        | Stock  |
| 130 | bitmap | —    | 80 × 16, 32-bit, compressed  | —        | Stock  |
| 131 | bitmap | —    | 120 × 24, 32-bit, compressed | —        | Stock  |
| 401 | bitmap | —    | 31 × 16, 4-bit, compressed   | —        | Stock  |

### `system32/comdlg32.dll`

| Id             | Type   | Name | Frames or size  | Shown by  | Status |
| -------------- | ------ | ---- | --------------- | --------- | ------ |
| CDROM          | icon   | —    | 16@32 16@8 16@4 | —         | Stock  |
| FLOPPY         | icon   | —    | 16@32 16@8 16@4 | —         | Stock  |
| FOLDER         | icon   | —    | 16@32 16@8 16@4 | —         | Stock  |
| FOLDER2        | icon   | —    | 16@32 16@8 16@4 | —         | Stock  |
| HDISK          | icon   | —    | 16@32 16@8 16@4 | —         | Stock  |
| NETWORK        | icon   | —    | 16@32 16@8 16@4 | —         | Stock  |
| PD32_COLLATE   | icon   | —    | 76@8 76@4 76@32 | —         | Stock  |
| PD32_LANDSCAPE | icon   | —    | 32@32 32@8 32@4 | —         | Stock  |
| PD32_NOCOLLATE | icon   | —    | 76@32 76@8 76@4 | —         | Stock  |
| PD32_PORTRAIT  | icon   | —    | 32@32 32@8 32@4 | —         | Stock  |
| 38             | bitmap | `38` | 100 × 12, 4-bit | fontdlg.c | Stock  |

### `system32/conime.exe`

| Id  | Type | Name | Frames or size | Shown by | Status |
| --- | ---- | ---- | -------------- | -------- | ------ |
| 100 | icon | —    | 64@24          | —        | Stock  |

### `system32/console.dll`

| Id  | Type | Name          | Frames or size                                  | Shown by  | Status    |
| --- | ---- | ------------- | ----------------------------------------------- | --------- | --------- |
| 40  | icon | `IDC_CPLICON` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | console.c | Afterglow |

### `system32/control.exe`

| Id  | Type | Name           | Frames or size                                  | Shown by | Status                               |
| --- | ---- | -------------- | ----------------------------------------------- | -------- | ------------------------------------ |
| 100 | icon | `IDI_MAINICON` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | **Stock, art ready**: `controlpanel` |

### `system32/credui.dll`

| Id  | Type   | Name | Frames or size   | Shown by | Status |
| --- | ------ | ---- | ---------------- | -------- | ------ |
| 200 | bitmap | —    | 320 × 60, 24-bit | —        | Stock  |

### `system32/cryptext.dll`

| Id  | Type | Name | Frames or size | Shown by | Status |
| --- | ---- | ---- | -------------- | -------- | ------ |
| 1   | icon | —    | 48@32          | —        | Stock  |

### `system32/cryptui.dll`

| Id  | Type   | Name | Frames or size   | Shown by | Status |
| --- | ------ | ---- | ---------------- | -------- | ------ |
| 200 | bitmap | —    | 48 × 16, 24-bit  | —        | Stock  |
| 201 | bitmap | —    | 32 × 32, 4-bit   | —        | Stock  |
| 202 | bitmap | —    | 32 × 32, 4-bit   | —        | Stock  |
| 203 | bitmap | —    | 32 × 32, 4-bit   | —        | Stock  |
| 204 | bitmap | —    | 64 × 16, 24-bit  | —        | Stock  |
| 205 | bitmap | —    | 164 × 628, 4-bit | —        | Stock  |
| 206 | bitmap | —    | 49 × 49, 4-bit   | —        | Stock  |

### `system32/ctfmon.exe`

| Id  | Type | Name | Frames or size                   | Shown by | Status                            |
| --- | ---- | ---- | -------------------------------- | -------- | --------------------------------- |
| 100 | icon | —    | 48@8 32@8 16@8 48@32 32@32 16@32 | —        | **Stock, art ready**: `kbdlayout` |

### `system32/cylfrac.scr` (removed by the `base` trim)

| Id  | Type | Name | Frames or size    | Shown by | Status  |
| --- | ---- | ---- | ----------------- | -------- | ------- |
| 101 | icon | —    | 48@32 32@32 16@32 | —        | Trimmed |

### `system32/desk.cpl`

| Id   | Type   | Name              | Frames or size                                  | Shown by   | Status                |
| ---- | ------ | ----------------- | ----------------------------------------------- | ---------- | --------------------- |
| 40   | icon   | `IDC_DESK_ICON`   | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | desk.c     | Afterglow (`display`) |
| 100  | icon   | `IDC_DESK_ICON2`  | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —          | Afterglow (`display`) |
| 209  | bitmap | `IDB_SPECTRUM_4`  | 16 × 1, 4-bit                                   | settings.c | Stock                 |
| 210  | bitmap | `IDB_SPECTRUM_8`  | 153 × 8, 8-bit                                  | —          | Stock                 |
| 211  | bitmap | `IDB_SPECTRUM_16` | 288 × 1, 8-bit                                  | —          | Stock                 |
| 1001 | bitmap | `IDC_MONITOR`     | 160 × 120, 8-bit                                | desk.c     | Stock                 |

### `system32/deskadp.dll`

| Id  | Type | Name | Frames or size | Shown by | Status |
| --- | ---- | ---- | -------------- | -------- | ------ |
| 209 | icon | —    | 32@8 32@32     | —        | Stock  |

### `system32/deskmon.dll`

| Id  | Type | Name | Frames or size | Shown by | Status |
| --- | ---- | ---- | -------------- | -------- | ------ |
| 208 | icon | —    | 32@8 32@32     | —        | Stock  |

### `system32/devmgmt.exe`

| Id  | Type | Name | Frames or size                                                    | Shown by | Status                          |
| --- | ---- | ---- | ----------------------------------------------------------------- | -------- | ------------------------------- |
| 1   | icon | —    | 48@8 32@8 24@8 16@8 48@24 32@24 24@8 16@8 48@32 32@32 24@32 16@32 | —        | **Stock, art ready**: `devmgmt` |

### `system32/devmgr.dll`

| Id  | Type   | Name             | Frames or size                   | Shown by               | Status                           |
| --- | ------ | ---------------- | -------------------------------- | ---------------------- | -------------------------------- |
| 20  | icon   | `IDI_MAIN_ICON`  | 48@8 32@8 16@8 48@32 32@32 16@32 | devmgmt/MainWindow.cpp | **Stock, drawn here**: `devmgmt` |
| 21  | bitmap | `IDB_ROOT_IMAGE` | 16 × 16, 24-bit                  | devmgmt/RootNode.cpp   | Stock                            |
| 22  | bitmap | `IDB_TOOLBAR`    | 96 × 16, 32-bit                  | devmgmt/MainWindow.cpp | Stock                            |

### `system32/dxdiag.exe` (removed by the `base` trim)

| Id    | Type | Name          | Frames or size                                  | Shown by | Status                  |
| ----- | ---- | ------------- | ----------------------------------------------- | -------- | ----------------------- |
| 20000 | icon | `IDI_APPICON` | 48@4 32@4 16@4 16@8 48@8 32@8 48@32 32@32 16@32 | dxdiag.c | Trimmed (art: `dxdiag`) |

### `system32/eventvwr.exe`

| Id  | Type | Name                   | Frames or size                   | Shown by    | Status                           |
| --- | ---- | ---------------------- | -------------------------------- | ----------- | -------------------------------- |
| 10  | icon | `IDI_EVENTVWR`         | 48@8 32@8 16@8 48@32 32@32 16@32 | eventvwr.c  | **Stock, art ready**: `eventvwr` |
| 11  | icon | `IDI_EVENTLOG`         | 48@8 32@8 16@8 48@32 32@32 16@32 | eventvwr.c  | Stock                            |
| 12  | icon | `IDI_CLOSED_CATEGORY`  | 16@8 16@32                       | eventvwr.c  | Stock                            |
| 13  | icon | `IDI_OPENED_CATEGORY`  | 16@8 16@32                       | eventvwr.c  | Stock                            |
| 14  | icon | `IDI_INFORMATIONICON`  | 16@32 16@8                       | eventvwr.c  | Stock                            |
| 15  | icon | `IDI_WARNINGICON`      | 16@32 16@8                       | eventvwr.c  | Stock                            |
| 16  | icon | `IDI_ERRORICON`        | 16@32 16@8                       | eventvwr.c  | Stock                            |
| 17  | icon | `IDI_AUDITSUCCESSICON` | 16@8 16@32                       | eventvwr.c  | Stock                            |
| 18  | icon | `IDI_AUDITFAILUREICON` | 16@8 16@32                       | eventvwr.c  | Stock                            |
| 19  | icon | `IDI_NEXT`             | 16@8 16@32                       | evtdetctl.c | Stock                            |
| 20  | icon | `IDI_PREV`             | 16@8 16@32                       | evtdetctl.c | Stock                            |
| 21  | icon | `IDI_COPY`             | 16@8 16@32                       | evtdetctl.c | Stock                            |

### `ReactOS/explorer.exe`

| Id  | Type   | Name                                  | Frames or size                                  | Shown by                   | Status                             |
| --- | ------ | ------------------------------------- | ----------------------------------------------- | -------------------------- | ---------------------------------- |
| 100 | icon   | `IDI_MAIN`                            | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4 | —                          | Stock                              |
| 101 | icon   | `IDI_CABINET`                         | 48@32 48@8 48@4 32@32 32@8 32@4 16@8 16@32 16@4 | —                          | **Stock, art ready**: `explorer`   |
| 102 | icon   | `IDI_PRINTER`                         | 48@8 48@4 32@8 32@4 16@8 16@4                   | —                          | Stock                              |
| 103 | icon   | `IDI_DESKTOP`                         | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4 | —                          | Stock                              |
| 104 | icon   | `IDI_PRINTER_PROBLEM`                 | 48@8 48@4 32@8 32@4 16@8 16@4                   | —                          | Stock                              |
| 107 | icon   | `IDI_STARTMENU`                       | 32@32 32@8 32@4 16@32 16@8 16@4                 | trayprop.cpp               | **Stock, drawn here**: `startmenu` |
| 108 | icon   | `IDI_RECYCLEBIN`                      | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4 | IDD_CLASSICSTART_CUSTOMIZE | **Stock, drawn here**: `recycle`   |
| 109 | icon   | `IDI_SHOWINFO`                        | 48@32 48@8 32@32 32@8 32@4 32@1 16@32 16@8 16@4 | —                          | Stock                              |
| 110 | icon   | `IDI_SHOWALERT`                       | 32@4 32@1 16@4                                  | —                          | Stock                              |
| 111 | icon   | `IDI_SHOWERROR`                       | 48@32 48@8 32@32 32@8 32@4 32@1 16@32 16@8 16@4 | —                          | Stock                              |
| 205 | icon   | `IDI_COMPUTER`                        | 48@8 48@4 32@8 32@4 16@8 16@4                   | —                          | Stock                              |
| 250 | icon   | `IDI_ARROWLEFT`                       | 16@1                                            | —                          | Stock                              |
| 251 | icon   | `IDI_ARROWRIGHT`                      | 16@1                                            | —                          | Stock                              |
| 252 | icon   | `IDI_FOLDER`                          | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4 | —                          | Stock                              |
| 253 | icon   | `IDI_INTERNET`                        | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4 | —                          | Stock                              |
| 254 | icon   | `IDI_MAIL`                            | 48@32 48@8 32@32 32@8 16@32 16@8                | —                          | Stock                              |
| 256 | icon   | `IDI_MAILSMALL`                       | 16@4                                            | —                          | Stock                              |
| 257 | icon   | `IDI_STARTMENU2`                      | 32@32 32@4 16@4                                 | IDD_CLASSICSTART_CUSTOMIZE | **Stock, drawn here**: `startmenu` |
| 143 | bitmap | `IDB_START`                           | 25 × 20, 32-bit                                 | traywnd.cpp                | Afterglow in `agexplorer.exe`      |
| 145 | bitmap | `IDB_TASKBARPROP_AUTOHIDE`            | 336 × 35, 4-bit                                 | trayprop.cpp               | Stock                              |
| 146 | bitmap | `IDB_TASKBARPROP_LOCK_GROUP_QL`       | 336 × 35, 24-bit                                | trayprop.cpp               | Stock                              |
| 147 | bitmap | `IDB_TASKBARPROP_NOLOCK_GROUP_QL`     | 336 × 35, 24-bit                                | trayprop.cpp               | Stock                              |
| 148 | bitmap | `IDB_TASKBARPROP_LOCK_NOGROUP_QL`     | 336 × 35, 24-bit                                | trayprop.cpp               | Stock                              |
| 149 | bitmap | `IDB_TASKBARPROP_NOLOCK_NOGROUP_QL`   | 336 × 35, 24-bit                                | trayprop.cpp               | Stock                              |
| 150 | bitmap | `IDB_TASKBARPROP_LOCK_GROUP_NOQL`     | 336 × 35, 24-bit                                | trayprop.cpp               | Stock                              |
| 151 | bitmap | `IDB_TASKBARPROP_NOLOCK_GROUP_NOQL`   | 336 × 35, 24-bit                                | trayprop.cpp               | Stock                              |
| 152 | bitmap | `IDB_TASKBARPROP_LOCK_NOGROUP_NOQL`   | 336 × 35, 24-bit                                | trayprop.cpp               | Stock                              |
| 153 | bitmap | `IDB_TASKBARPROP_NOLOCK_NOGROUP_NOQL` | 336 × 35, 24-bit                                | trayprop.cpp               | Stock                              |
| 154 | bitmap | `IDB_SYSTRAYPROP_SHOW_SECONDS_NODESK` | 336 × 35, 8-bit                                 | trayprop.cpp               | Stock                              |
| 155 | bitmap | `IDB_SYSTRAYPROP_HIDE_SECONDS_NODESK` | 336 × 35, 8-bit                                 | trayprop.cpp               | Stock                              |
| 158 | bitmap | `IDB_STARTMENU`                       | 21 × 233, 24-bit                                | traywnd.cpp                | Afterglow in `agexplorer.exe`      |
| 170 | bitmap | `IDB_STARTPREVIEW`                    | 300 × 180, 8-bit                                | trayprop.cpp               | Stock                              |
| 171 | bitmap | `IDB_STARTPREVIEW_CLASSIC`            | 300 × 180, 8-bit                                | trayprop.cpp               | Stock                              |
| 180 | bitmap | `IDB_SYSTRAYPROP_HIDE_CLOCK_NODESK`   | 336 × 35, 8-bit                                 | trayprop.cpp               | Stock                              |
| 181 | bitmap | `IDB_SYSTRAYPROP_HIDE_NOCLOCK_NODESK` | 336 × 35, 8-bit                                 | trayprop.cpp               | Stock                              |
| 182 | bitmap | `IDB_SYSTRAYPROP_SHOW_CLOCK_NODESK`   | 336 × 35, 8-bit                                 | trayprop.cpp               | Stock                              |
| 183 | bitmap | `IDB_SYSTRAYPROP_SHOW_NOCLOCK_NODESK` | 336 × 35, 8-bit                                 | trayprop.cpp               | Stock                              |
| 184 | bitmap | `IDB_SYSTRAYPROP_SHOW_SECONDS_DESK`   | 336 × 35, 8-bit                                 | trayprop.cpp               | Stock                              |
| 185 | bitmap | `IDB_SYSTRAYPROP_HIDE_SECONDS_DESK`   | 336 × 35, 8-bit                                 | trayprop.cpp               | Stock                              |
| 186 | bitmap | `IDB_SYSTRAYPROP_HIDE_CLOCK_DESK`     | 336 × 35, 8-bit                                 | trayprop.cpp               | Stock                              |
| 187 | bitmap | `IDB_SYSTRAYPROP_HIDE_NOCLOCK_DESK`   | 336 × 35, 8-bit                                 | trayprop.cpp               | Stock                              |
| 188 | bitmap | `IDB_SYSTRAYPROP_SHOW_CLOCK_DESK`     | 336 × 35, 8-bit                                 | trayprop.cpp               | Stock                              |
| 189 | bitmap | `IDB_SYSTRAYPROP_SHOW_NOCLOCK_DESK`   | 336 × 35, 8-bit                                 | trayprop.cpp               | Stock                              |

### `system32/fontsub.exe`

| Id  | Type   | Name | Frames or size          | Shown by | Status                           |
| --- | ------ | ---- | ----------------------- | -------- | -------------------------------- |
| 1   | icon   | —    | 16@24 32@24 48@24 64@24 | —        | **Stock, drawn here**: `fontsub` |
| 2   | bitmap | —    | 12 × 12, 8-bit          | —        | Stock                            |
| 3   | bitmap | —    | 12 × 12, 8-bit          | —        | Stock                            |
| 4   | bitmap | —    | 12 × 12, 8-bit          | —        | Stock                            |

### `system32/fontview.exe`

| Id  | Type | Name     | Frames or size                                  | Shown by   | Status |
| --- | ---- | -------- | ----------------------------------------------- | ---------- | ------ |
| 800 | icon | `IDI_TT` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | fontview.c | Stock  |

### `system32/frag.exe`

| Id  | Type   | Name | Frames or size      | Shown by | Status |
| --- | ------ | ---- | ------------------- | -------- | ------ |
| 114 | icon   | —    | 32@4 32@0 48@0 16@0 | —        | Stock  |
| 110 | bitmap | —    | 91 × 90, 4-bit      | —        | Stock  |

### `system32/gdihv.exe`

| Id   | Type | Name | Frames or size                                                  | Shown by | Status |
| ---- | ---- | ---- | --------------------------------------------------------------- | -------- | ------ |
| 2000 | icon | —    | 48@4 32@4 24@4 16@4 48@8 32@8 24@8 16@8 48@32 32@32 24@32 16@32 | —        | Stock  |

### `system32/hdwwiz.cpl`

| Id  | Type   | Name              | Frames or size                                  | Shown by       | Status              |
| --- | ------ | ----------------- | ----------------------------------------------- | -------------- | ------------------- |
| 100 | icon   | `IDI_CPLICON`     | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | hdwwiz.c       | Afterglow (`addhw`) |
| 102 | icon   | `IDI_WARNINGICON` | 32@8 32@32                                      | IDD_STARTPAGE  | Stock               |
| 103 | icon   | `IDI_SEARCHICON`  | 32@8 32@32                                      | IDD_SEARCHPAGE | Stock               |
| 50  | bitmap | `IDB_WATERMARK`   | 164 × 400, 8-bit                                | hdwwiz.c       | Stock               |
| 51  | bitmap | `IDB_HEADER`      | 49 × 49, 8-bit                                  | hdwwiz.c       | Stock               |

### `ReactOS/hh.exe`

| Id  | Type | Name | Frames or size                   | Shown by | Status                       |
| --- | ---- | ---- | -------------------------------- | -------- | ---------------------------- |
| 2   | icon | —    | 48@8 32@8 16@8 48@32 32@32 16@32 | —        | **Stock, art ready**: `help` |

### `system32/hhctrl.ocx`

| Id   | Type   | Name | Frames or size                   | Shown by | Status |
| ---- | ------ | ---- | -------------------------------- | -------- | ------ |
| 100  | icon   | —    | 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Stock  |
| 1000 | bitmap | —    | 144 × 24, 32-bit, compressed     | —        | Stock  |
| 1001 | bitmap | —    | 48 × 16, 32-bit, compressed      | —        | Stock  |

### `system32/hotplug.dll`

| Id  | Type | Name | Frames or size        | Shown by | Status |
| --- | ---- | ---- | --------------------- | -------- | ------ |
| 100 | icon | —    | 32@8 32@32 16@8 16@32 | —        | Stock  |

### `system32/ieframe.dll`

| Id   | Type   | Name | Frames or size                                          | Shown by | Status                       |
| ---- | ------ | ---- | ------------------------------------------------------- | -------- | ---------------------------- |
| 1401 | icon   | —    | 48@8 32@8 24@8 16@8 48@24 32@24 48@32 32@32 24@32 16@32 | —        | **Stock, art ready**: `html` |
| 1400 | bitmap | —    | 192 × 32, 32-bit, compressed                            | —        | Stock                        |

### `system32/iernonce.dll`

| Id  | Type | Name | Frames or size                   | Shown by | Status |
| --- | ---- | ---- | -------------------------------- | -------- | ------ |
| 1   | icon | —    | 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Stock  |

### `system32/imm32.dll`

| Id  | Type   | Name | Frames or size | Shown by | Status |
| --- | ------ | ---- | -------------- | -------- | ------ |
| 100 | bitmap | —    | 16 × 9, 4-bit  | —        | Stock  |
| 101 | bitmap | —    | 16 × 9, 4-bit  | —        | Stock  |
| 102 | bitmap | —    | 22 × 9, 4-bit  | —        | Stock  |
| 103 | bitmap | —    | 26 × 9, 4-bit  | —        | Stock  |
| 104 | bitmap | —    | 23 × 9, 4-bit  | —        | Stock  |
| 105 | bitmap | —    | 16 × 9, 4-bit  | —        | Stock  |
| 106 | bitmap | —    | 18 × 9, 4-bit  | —        | Stock  |
| 107 | bitmap | —    | 16 × 9, 4-bit  | —        | Stock  |
| 108 | bitmap | —    | 376 × 8, 1-bit | —        | Stock  |
| 201 | bitmap | —    | 32 × 24, 4-bit | —        | Stock  |
| 202 | bitmap | —    | 32 × 24, 4-bit | —        | Stock  |
| 203 | bitmap | —    | 38 × 24, 4-bit | —        | Stock  |
| 204 | bitmap | —    | 38 × 24, 4-bit | —        | Stock  |
| 205 | bitmap | —    | 56 × 24, 4-bit | —        | Stock  |
| 206 | bitmap | —    | 34 × 20, 4-bit | —        | Stock  |
| 207 | bitmap | —    | 34 × 20, 4-bit | —        | Stock  |
| 208 | bitmap | —    | 34 × 20, 4-bit | —        | Stock  |
| 209 | bitmap | —    | 376 × 8, 1-bit | —        | Stock  |

### `system32/indicdll.dll`

| Id  | Type | Name | Frames or size | Shown by | Status |
| --- | ---- | ---- | -------------- | -------- | ------ |
| 10  | icon | —    | 16@32 32@32    | —        | Stock  |
| 11  | icon | —    | 16@32 32@32    | —        | Stock  |
| 12  | icon | —    | 16@32 32@32    | —        | Stock  |
| 13  | icon | —    | 16@32 32@32    | —        | Stock  |
| 14  | icon | —    | 16@32 32@32    | —        | Stock  |
| 15  | icon | —    | 16@32 32@32    | —        | Stock  |
| 16  | icon | —    | 16@32 32@32    | —        | Stock  |

### `system32/inetcpl.cpl`

| Id   | Type | Name               | Frames or size                                  | Shown by    | Status                     |
| ---- | ---- | ------------------ | ----------------------------------------------- | ----------- | -------------------------- |
| 100  | icon | `ICO_MAIN`         | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | inetcpl.c   | Afterglow (`inetsettings`) |
| 1313 | icon | `ICO_INTERNET`     | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —           | Stock                      |
| 1314 | icon | `ICO_CERTIFICATES` | 16@8 32@8 16@32 32@32                           | IDD_CONTENT | Stock                      |
| 1315 | icon | `ICO_HISTORY`      | 32@8 32@32                                      | IDD_GENERAL | Stock                      |
| 1316 | icon | `ICO_HOME`         | 32@8 32@32                                      | IDD_GENERAL | Stock                      |
| 4480 | icon | `ICO_TRUSTED`      | 32@8 32@32                                      | —           | Stock                      |
| 4481 | icon | `ICO_RESTRICTED`   | 32@8 32@32                                      | —           | Stock                      |

### `system32/input.dll`

| Id   | Type | Name | Frames or size                                  | Shown by | Status |
| ---- | ---- | ---- | ----------------------------------------------- | -------- | ------ |
| 1502 | icon | —    | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 1503 | icon | —    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Stock  |
| 1504 | icon | —    | 16@24                                           | —        | Stock  |

### `system32/intl.cpl`

| Id  | Type | Name          | Frames or size                                 | Shown by           | Status                 |
| --- | ---- | ------------- | ---------------------------------------------- | ------------------ | ---------------------- |
| 200 | icon | `IDC_CPLICON` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@8 | generalp.c, intl.c | Afterglow (`regional`) |

### `system32/joy.cpl` (removed by the `base` trim)

| Id  | Type | Name | Frames or size                                  | Shown by | Status                    |
| --- | ---- | ---- | ----------------------------------------------- | -------- | ------------------------- |
| 102 | icon | —    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Trimmed (art: `joystick`) |

### `system32/kbswitch.exe`

| Id  | Type | Name       | Frames or size                   | Shown by | Status                            |
| --- | ---- | ---------- | -------------------------------- | -------- | --------------------------------- |
| 150 | icon | `IDI_MAIN` | 48@8 32@8 16@8 48@32 32@32 16@32 | —        | **Stock, art ready**: `kbdlayout` |

### `system32/logon.scr`

| Id       | Type   | Name              | Frames or size    | Shown by | Status |
| -------- | ------ | ----------------- | ----------------- | -------- | ------ |
| IDI_ICON | icon   | —                 | 48@32 32@32 16@32 | —        | Stock  |
| 256      | bitmap | `IDB_WORKSTATION` | 205 × 164, 24-bit | logon.c  | Stock  |
| 512      | bitmap | `IDB_SERVER`      | 205 × 164, 24-bit | logon.c  | Stock  |

### `system32/logonui.exe`

| Id  | Type   | Name | Frames or size    | Shown by | Status |
| --- | ------ | ---- | ----------------- | -------- | ------ |
| 100 | bitmap | —    | 219 × 207, 24-bit | —        | Stock  |
| 123 | bitmap | —    | 137 × 86, 24-bit  | —        | Stock  |
| 125 | bitmap | —    | 800 × 2, 24-bit   | —        | Stock  |
| 126 | bitmap | —    | 800 × 3, 24-bit   | —        | Stock  |

### `system32/magnify.exe` (removed by the `base` trim)

| Id  | Type | Name | Frames or size                                  | Shown by | Status                   |
| --- | ---- | ---- | ----------------------------------------------- | -------- | ------------------------ |
| 101 | icon | —    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Trimmed (art: `magnify`) |

### `system32/main.cpl`

| Id  | Type | Name                     | Frames or size                                          | Shown by                | Status                                |
| --- | ---- | ------------------------ | ------------------------------------------------------- | ----------------------- | ------------------------------------- |
| 100 | icon | `IDC_CPLICON_1`          | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32         | main.c, mouse.c         | Afterglow (`mouse`)                   |
| 104 | icon | `IDI_MOUSE_SPEED`        | 16@32 24@32 32@32 48@32 64@32 72@32 96@32 128@32 256@32 | IDD_PAGE_OPTION         | **Stock, drawn here**: `mouse-speed`  |
| 105 | icon | `IDI_REPEAT_DELAY`       | 32@24 32@32                                             | IDD_KEYBSPEED           | **Stock, drawn here**: `kbd-delay`    |
| 106 | icon | `IDI_REPEAT_RATE`        | 32@8 32@32                                              | IDD_KEYBSPEED           | **Stock, drawn here**: `kbd-rate`     |
| 108 | icon | `IDI_MOUSE_BUTTON`       | 32@8 32@8                                               | IDD_PAGE_OPTION         | **Stock, drawn here**: `mouse-snap`   |
| 109 | icon | `IDI_MOUSE_LEFT`         | 48@8 48@32                                              | mouse.c                 | **Stock, drawn here**: `mouse-left`   |
| 110 | icon | `IDI_MOUSE_RIGHT`        | 48@8 48@32                                              | mouse.c                 | **Stock, drawn here**: `mouse-right`  |
| 200 | icon | `IDC_CPLICON_2`          | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32         | keyboard.c, main.c      | Afterglow (`keyboard`)                |
| 300 | icon | `IDI_PRINTERS_FOLDER`    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32         | —                       | Afterglow (`printers`)                |
| 400 | icon | `IDI_FONTS_FOLDER`       | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32         | —                       | Afterglow (`fonts`)                   |
| 500 | icon | `IDI_ADMIN_TOOLS_FOLDER` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32         | —                       | Afterglow (`admintools`)              |
| 600 | icon | `IDI_MOUSE_TRAILS`       | 32@1 32@1                                               | IDD_PAGE_OPTION         | **Stock, drawn here**: `mouse-trails` |
| 601 | icon | `IDI_MOUSE_HIDE`         | 16@32 24@32 32@32 48@32 64@32 72@32 96@32 128@32 256@32 | IDD_PAGE_OPTION         | **Stock, drawn here**: `mouse-hide`   |
| 602 | icon | `IDI_MOUSE_POINTER`      | 32@8 32@32                                              | IDD_PAGE_OPTION         | **Stock, drawn here**: `mouse-locate` |
| 603 | icon | `IDI_MOUSE_WHEEL`        | 32@32 32@8                                              | IDD_PAGE_WHEEL          | **Stock, drawn here**: `mouse-wheel`  |
| 605 | icon | `IDI_FOLDER_CLOSED`      | 48@8 48@32                                              | mouse.c                 | **Stock, drawn here**: `folder`       |
| 606 | icon | `IDI_FOLDER_OPEN`        | 48@8 48@32                                              | mouse.c                 | **Stock, drawn here**: `folderopen`   |
| 607 | icon | `IDI_LOCK_KEY`           | 16@8 16@32 32@8 32@32                                   | IDD_CLICK_LOCK, mouse.c | **Stock, drawn here**: `clicklock`    |

### `system32/matrix.scr` (removed by the `base` trim)

| Id  | Type   | Name | Frames or size  | Shown by | Status  |
| --- | ------ | ---- | --------------- | -------- | ------- |
| 106 | icon   | —    | 32@8 16@8 32@32 | —        | Trimmed |
| 104 | bitmap | —    | 364 × 84, 8-bit | —        | Trimmed |

### `system32/mazescr.scr` (removed by the `base` trim)

| Id  | Type | Name | Frames or size    | Shown by | Status  |
| --- | ---- | ---- | ----------------- | -------- | ------- |
| 101 | icon | —    | 48@32 32@32 16@32 | —        | Trimmed |

### `system32/mmc.exe` (removed by the `base` trim)

| Id  | Type | Name | Frames or size                                  | Shown by | Status  |
| --- | ---- | ---- | ----------------------------------------------- | -------- | ------- |
| 101 | icon | —    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Trimmed |

### `system32/mmsys.cpl`

| Id   | Type | Name                  | Frames or size                                  | Shown by                                            | Status              |
| ---- | ---- | --------------------- | ----------------------------------------------- | --------------------------------------------------- | ------------------- |
| 3004 | icon | `IDI_CPLICON`         | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | IDD_AUDIO, IDD_VOICE, IDD_VOLUME, mmsys.c, volume.c | Afterglow (`sound`) |
| 3005 | icon | `IDI_PLAY_ICON`       | 32@1                                            | sounds.c                                            | Stock               |
| 3006 | icon | `IDI_STOP_ICON`       | 32@1                                            | sounds.c                                            | Stock               |
| 3007 | icon | `IDI_MIDICON`         | 32@24 32@32                                     | IDD_AUDIO                                           | Stock               |
| 3009 | icon | `IDI_SHUTDOWN_ICON`   | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —                                                   | Stock               |
| 4354 | icon | `4354`                | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —                                                   | Stock               |
| 4355 | icon | `4355`                | 16@4                                            | —                                                   | Stock               |
| 4356 | icon | `4356`                | 16@4                                            | —                                                   | Stock               |
| 4357 | icon | `4357`                | 16@4                                            | —                                                   | Stock               |
| 4358 | icon | `4358`                | 16@4                                            | —                                                   | Stock               |
| 4359 | icon | `4359`                | 16@4                                            | —                                                   | Stock               |
| 4360 | icon | `4360`                | 16@4                                            | —                                                   | Stock               |
| 4361 | icon | `IDI_JOY_ICON`        | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —                                                   | Stock               |
| 4362 | icon | `4362`                | 16@4                                            | —                                                   | Stock               |
| 4363 | icon | `4363`                | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —                                                   | Stock               |
| 4364 | icon | `IDI_CAMERA_ICON`     | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —                                                   | Stock               |
| 4365 | icon | `4365`                | 16@4                                            | —                                                   | Stock               |
| 4366 | icon | `IDI_SOUND_SECTION`   | 48@8 32@8 16@8 48@32 32@32 16@32                | sounds.c                                            | Stock               |
| 4367 | icon | `IDI_SOUND_ASSIGNED`  | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | sounds.c                                            | Stock               |
| 4368 | icon | `4368`                | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —                                                   | Stock               |
| 4369 | icon | `4369`                | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —                                                   | Stock               |
| 4370 | icon | `4370`                | 16@4                                            | —                                                   | Stock               |
| 4371 | icon | `4371`                | 16@4                                            | —                                                   | Stock               |
| 4372 | icon | `4372`                | 16@4                                            | —                                                   | Stock               |
| 4373 | icon | `4373`                | 16@4                                            | —                                                   | Stock               |
| 4374 | icon | `4374`                | 16@4                                            | —                                                   | Stock               |
| 4375 | icon | `4375`                | 16@4                                            | —                                                   | Stock               |
| 4376 | icon | `4376`                | 16@4                                            | —                                                   | Stock               |
| 4377 | icon | `4377`                | 16@4                                            | —                                                   | Stock               |
| 4378 | icon | `IDI_MICROPHONE_ICON` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | IDD_AUDIO, IDD_VOICE                                | Stock               |
| 4379 | icon | `4379`                | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | IDD_PERFORMANCE1, IDD_SPEAKERS                      | Stock               |
| 4380 | icon | `4380`                | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | IDD_PERFORMANCE2                                    | Stock               |
| 4381 | icon | `4381`                | 16@4                                            | —                                                   | Stock               |
| 4382 | icon | `4382`                | 16@4                                            | —                                                   | Stock               |
| 4383 | icon | `4383`                | 16@4                                            | —                                                   | Stock               |
| 4384 | icon | `4384`                | 16@4                                            | —                                                   | Stock               |
| 4385 | icon | `4385`                | 16@4                                            | —                                                   | Stock               |
| 4386 | icon | `4386`                | 16@4                                            | —                                                   | Stock               |
| 4387 | icon | `4387`                | 16@4                                            | —                                                   | Stock               |
| 4388 | icon | `4388`                | 16@4                                            | —                                                   | Stock               |
| 4390 | icon | `IDI_NO_HW`           | 32@8 32@32                                      | volume.c                                            | Stock               |
| 4393 | icon | `IDI_MUTED_ICON`      | 32@8 32@32                                      | volume.c                                            | Stock               |
| 4624 | icon | `IDI_SPEAKIMG`        | 72@4 72@8 72@32                                 | volume.c                                            | Stock               |

### `system32/modemui.dll`

| Id   | Type | Name | Frames or size                                     | Shown by | Status |
| ---- | ---- | ---- | -------------------------------------------------- | -------- | ------ |
| 700  | icon | —    | 32@8 16@8 32@24 16@24 32@32 16@32                  | —        | Stock  |
| 701  | icon | —    | 32@8 24@8 16@8 32@24 24@24 16@24 32@32 24@32 16@32 | —        | Stock  |
| 702  | icon | —    | 32@8 16@8 32@24 16@24 32@32 16@32                  | —        | Stock  |
| 703  | icon | —    | 32@4 16@4                                          | —        | Stock  |
| 5100 | icon | —    | 32@8 24@8 16@8 32@24 24@24 16@24 32@32 24@32 16@32 | —        | Stock  |

### `system32/mplay32.exe` (removed by the `base` trim)

| Id  | Type   | Name               | Frames or size                                  | Shown by  | Status                   |
| --- | ------ | ------------------ | ----------------------------------------------- | --------- | ------------------------ |
| 10  | icon   | `IDI_MAIN`         | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | mplay32.c | Trimmed (art: `mplay32`) |
| 50  | bitmap | `IDB_PLAYICON`     | 16 × 16, 8-bit                                  | mplay32.c | Trimmed                  |
| 51  | bitmap | `IDB_STOPICON`     | 16 × 16, 8-bit                                  | mplay32.c | Trimmed                  |
| 52  | bitmap | `IDB_EJECTICON`    | 16 × 16, 8-bit                                  | mplay32.c | Trimmed                  |
| 53  | bitmap | `IDB_BACKWARDICON` | 16 × 16, 8-bit                                  | mplay32.c | Trimmed                  |
| 54  | bitmap | `IDB_SEEKBACKICON` | 16 × 16, 8-bit                                  | mplay32.c | Trimmed                  |
| 55  | bitmap | `IDB_SEEKFORWICON` | 16 × 16, 8-bit                                  | mplay32.c | Trimmed                  |
| 56  | bitmap | `IDB_FORWARDICON`  | 16 × 16, 8-bit                                  | mplay32.c | Trimmed                  |
| 57  | bitmap | `IDB_PAUSEICON`    | 16 × 16, 8-bit                                  | mplay32.c | Trimmed                  |

### `system32/msconfig.exe`

| Id   | Type | Name          | Frames or size                   | Shown by   | Status                           |
| ---- | ---- | ------------- | -------------------------------- | ---------- | -------------------------------- |
| 3001 | icon | `IDI_APPICON` | 48@8 32@8 16@8 48@32 32@32 16@32 | msconfig.c | **Stock, art ready**: `msconfig` |

### `system32/msgina.dll`

| Id    | Type   | Name                | Frames or size                   | Shown by                                                                                   | Status                                  |
| ----- | ------ | ------------------- | -------------------------------- | ------------------------------------------------------------------------------------------ | --------------------------------------- |
| 13    | icon   | `IDI_NOT_CONNECTED` | 64@8                             | —                                                                                          | Stock                                   |
| 21    | icon   | `IDI_LOGOFF`        | 48@8 32@8 16@8 48@32 32@32 16@32 | IDD_LOGOFF                                                                                 | **Stock, drawn here**: `logoff`         |
| 22    | icon   | `IDI_SHUTDOWN`      | 32@8 16@8 32@32 16@32            | IDD_SHUTDOWN, IDD_SHUTDOWN_REASON                                                          | **Stock, drawn here**: `shutdown`       |
| 109   | icon   | `IDI_KEYBOARD`      | 48@8 32@8 16@8 48@32 32@32 16@32 | IDD_WELCOME                                                                                | **Stock, drawn here**: `keyboard`       |
| 110   | icon   | `IDI_HARDWARE`      | 32@8 16@8 32@32 16@32            | —                                                                                          | Stock                                   |
| 115   | icon   | `IDI_LOCKICON`      | 32@8 32@32                       | IDD_LOCKED, IDD_UNLOCK                                                                     | **Stock, drawn here**: `shield`         |
| 20000 | bitmap | `IDI_ROSLOGO`       | 413 × 72, 24-bit                 | IDD_CHANGEPWD, IDD_LOCKED, IDD_LOGON, IDD_SECURITY, IDD_SHUTDOWN, IDD_SHUTDOWN_REASON, IDD | Afterglow in `agmsgina.dll`             |
| 20001 | bitmap | `IDI_BAR`           | 413 × 5, 24-bit                  | IDD_LOGON, IDD_SHUTDOWN, IDD_WELCOME, gui.c                                                | Afterglow in `agmsgina.dll`             |
| 20002 | bitmap | `IDI_ROSLOGO_FLAG`  | 48 × 40, 24-bit                  | IDD_SHUTDOWN_FANCY, IDD_SHUTDOWN_FANCY_LONG                                                | **Stock, drawn here**: `shutdown-mark`  |
| 20003 | bitmap | `IDI_DLG_BG`        | 312 × 198, 24-bit                | IDD_SHUTDOWN_FANCY, IDD_SHUTDOWN_FANCY_LONG                                                | **Stock, drawn here**: `shutdown-bg`    |
| 20004 | bitmap | `IDB_IMAGE_STRIP`   | 33 × 330, 24-bit                 | shutdown.c                                                                                 | **Stock, drawn here**: `shutdown-strip` |

### `system32/mshta.exe`

| Id  | Type | Name | Frames or size | Shown by | Status |
| --- | ---- | ---- | -------------- | -------- | ------ |
| 1   | icon | `1`  | 32@32 16@32    | —        | Stock  |

### `system32/msi.dll`

| Id   | Type   | Name | Frames or size | Shown by | Status |
| ---- | ------ | ---- | -------------- | -------- | ------ |
| 4097 | bitmap | —    | 32 × 16, 4-bit | —        | Stock  |
| 4098 | bitmap | —    | 32 × 16, 4-bit | —        | Stock  |
| 4099 | bitmap | —    | 32 × 16, 4-bit | —        | Stock  |

### `system32/msiexec.exe`

| Id  | Type | Name | Frames or size                   | Shown by | Status |
| --- | ---- | ---- | -------------------------------- | -------- | ------ |
| 1   | icon | —    | 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Stock  |

### `system32/mspaint.exe` (removed by the `base` trim)

| Id  | Type   | Name                 | Frames or size                   | Shown by                 | Status                 |
| --- | ------ | -------------------- | -------------------------------- | ------------------------ | ---------------------- |
| 500 | icon   | `IDI_APPICON`        | 48@8 32@8 16@8 48@32 32@32 16@32 | fullscreen.cpp, main.cpp | Trimmed (art: `paint`) |
| 526 | icon   | `IDI_TRANSPARENT`    | 40@8                             | toolsettings.cpp         | Trimmed                |
| 527 | icon   | `IDI_NONTRANSPARENT` | 40@8                             | toolsettings.cpp         | Trimmed                |
| 535 | icon   | `IDI_HORZSTRETCH`    | 32@4                             | IDD_STRETCHSKEW          | Trimmed                |
| 536 | icon   | `IDI_VERTSTRETCH`    | 32@4                             | IDD_STRETCHSKEW          | Trimmed                |
| 537 | icon   | `IDI_HORZSKEW`       | 32@4                             | IDD_STRETCHSKEW          | Trimmed                |
| 538 | icon   | `IDI_VERTSKEW`       | 32@4                             | IDD_STRETCHSKEW          | Trimmed                |
| 510 | bitmap | `IDB_TOOLBARICONS`   | 256 × 16, 24-bit                 | toolbox.cpp              | Trimmed                |
| 511 | bitmap | `IDB_FONTSTOOLBAR`   | 64 × 16, 24-bit                  | dialogs.cpp              | Trimmed                |

### `system32/mstsc.exe` (removed by the `base` trim)

| Id   | Type   | Name | Frames or size                                  | Shown by | Status                 |
| ---- | ------ | ---- | ----------------------------------------------- | -------- | ---------------------- |
| 2000 | icon   | —    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Trimmed (art: `mstsc`) |
| 2001 | icon   | —    | 32@4 32@8 32@32                                 | —        | Trimmed                |
| 2002 | icon   | —    | 32@4 32@8 32@32                                 | —        | Trimmed                |
| 2003 | icon   | —    | 24@8 16@8 32@8 32@4 32@8 32@32                  | —        | Trimmed                |
| 2004 | icon   | —    | 32@4 32@8 32@32                                 | —        | Trimmed                |
| 1100 | bitmap | —    | 390 × 70, 24-bit                                | —        | Trimmed                |
| 1101 | bitmap | —    | 154 × 14, 24-bit                                | —        | Trimmed                |

### `system32/msutb.dll`

| Id  | Type   | Name | Frames or size  | Shown by | Status |
| --- | ------ | ---- | --------------- | -------- | ------ |
| 100 | icon   | —    | 16@32 32@32     | —        | Stock  |
| 154 | bitmap | —    | 88 × 36, 4-bit  | —        | Stock  |
| 155 | bitmap | —    | 132 × 35, 4-bit | —        | Stock  |

### `system32/msxml3.dll`

| Id  | Type | Name | Frames or size                              | Shown by | Status |
| --- | ---- | ---- | ------------------------------------------- | -------- | ------ |
| 128 | icon | —    | 48@8 32@8 22@8 16@8 48@32 32@32 22@32 16@32 | —        | Stock  |
| 129 | icon | —    | 48@8 32@8 24@8 16@8 48@32 32@32 24@32 16@32 | —        | Stock  |

### `system32/mydocs.dll`

| Id  | Type | Name  | Frames or size                                   | Shown by | Status |
| --- | ---- | ----- | ------------------------------------------------ | -------- | ------ |
| 100 | icon | `100` | 48@4 32@4 16@4 48@32 32@8 16@8 48@24 32@32 16@32 | —        | Stock  |
| 101 | icon | `101` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32  | —        | Stock  |

### `system32/netcfgx.dll`

| Id  | Type | Name | Frames or size                   | Shown by | Status |
| --- | ---- | ---- | -------------------------------- | -------- | ------ |
| 100 | icon | —    | 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Stock  |
| 101 | icon | —    | 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Stock  |

### `system32/netid.dll`

| Id  | Type | Name | Frames or size                                                  | Shown by | Status |
| --- | ---- | ---- | --------------------------------------------------------------- | -------- | ------ |
| 101 | icon | —    | 48@8 32@8 24@8 16@8 48@8 32@8 24@8 16@8 48@32 32@32 24@32 16@32 | —        | Stock  |
| 102 | icon | —    | 16@8 16@24 16@32                                                | —        | Stock  |

### `system32/netplwiz.dll`

| Id   | Type | Name | Frames or size                   | Shown by | Status |
| ---- | ---- | ---- | -------------------------------- | -------- | ------ |
| 4400 | icon | —    | 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Stock  |

### `system32/netshell.dll`

| Id  | Type | Name                       | Frames or size                                                  | Shown by                                     | Status                            |
| --- | ---- | -------------------------- | --------------------------------------------------------------- | -------------------------------------------- | --------------------------------- |
| 100 | icon | `IDI_SHELL_NETWORK_FOLDER` | 48@4 32@4 24@4 16@4 48@8 32@8 24@8 16@8 48@32 32@32 24@32 16@32 | shfldr_netconnect.cpp                        | Afterglow (`netconn`)             |
| 104 | icon | `IDI_NET_ERROR`            | 32@32 16@32                                                     | —                                            | Stock                             |
| 105 | icon | `IDI_NET_IDLE`             | 32@32 16@32                                                     | lanstatusui.cpp, shfldr_netconnect.cpp       | **Stock, drawn here**: `lan`      |
| 106 | icon | `IDI_NET_OFF`              | 32@32 16@32                                                     | lanstatusui.cpp, shfldr_netconnect.cpp       | **Stock, drawn here**: `lanoff`   |
| 107 | icon | `IDI_NET_REC`              | 32@32 16@32                                                     | lanstatusui.cpp                              | **Stock, drawn here**: `lanrec`   |
| 108 | icon | `IDI_NET_TRANS`            | 32@32 16@32                                                     | lanstatusui.cpp                              | **Stock, drawn here**: `lantrans` |
| 109 | icon | `IDI_NET_TRANSREC`         | 32@32 16@32                                                     | lanstatusui.cpp                              | **Stock, drawn here**: `lanboth`  |
| 110 | icon | `IDI_NET_SETUP`            | 48@8 32@8 24@8 16@8 48@8 32@8 24@8 16@8 48@32 32@32 24@32 16@32 | IDD_NETWORKINITPAGE, IDD_NETWORKSETTINGSPAGE | Stock                             |

### `system32/newdev.dll`

| Id  | Type   | Name            | Frames or size   | Shown by | Status |
| --- | ------ | --------------- | ---------------- | -------- | ------ |
| 100 | bitmap | `IDB_WATERMARK` | 164 × 400, 8-bit | wizard.c | Stock  |
| 101 | bitmap | `IDB_HEADER`    | 49 × 49, 8-bit   | wizard.c | Stock  |

### `system32/notepad.exe`

| Id  | Type | Name         | Frames or size                                  | Shown by         | Status             |
| --- | ---- | ------------ | ----------------------------------------------- | ---------------- | ------------------ |
| 521 | icon | `IDI_NPICON` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | dialog.c, main.c | Afterglow (`text`) |

### `ReactOS/notepad.exe`

| Id  | Type | Name         | Frames or size                                  | Shown by         | Status                       |
| --- | ---- | ------------ | ----------------------------------------------- | ---------------- | ---------------------------- |
| 521 | icon | `IDI_NPICON` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | dialog.c, main.c | **Stock, art ready**: `text` |

### `system32/ntobjshex.dll`

| Id  | Type | Name                  | Frames or size                              | Shown by                       | Status |
| --- | ---- | --------------------- | ------------------------------------------- | ------------------------------ | ------ |
| 1   | icon | `IDI_NTOBJECTFOLDER`  | 16@8 32@8 48@8 16@32 32@32 48@32            | —                              | Stock  |
| 2   | icon | `IDI_NTOBJECTDIR`     | 16@8 32@8 48@8 16@32 32@32 48@32            | ntobjfolder.cpp                | Stock  |
| 3   | icon | `IDI_NTOBJECTDIROPEN` | 16@8 32@8 48@8 16@32 32@32 48@32            | ntobjfolder.cpp                | Stock  |
| 4   | icon | `IDI_NTOBJECTITEM`    | 48@8 32@8 16@8 48@32 32@32 16@32            | ntobjfolder.cpp, regfolder.cpp | Stock  |
| 5   | icon | `IDI_NTOBJECTDEVICE`  | 48@8 32@8 24@8 16@8 48@32 32@32 24@32 16@32 | ntobjfolder.cpp                | Stock  |
| 6   | icon | `IDI_NTOBJECTPORT`    | 16@8 32@8 16@32 32@32                       | ntobjfolder.cpp                | Stock  |
| 7   | icon | `IDI_REGISTRYKEY`     | 16@8 32@8 48@8 16@32 32@32 48@32            | ntobjfolder.cpp, regfolder.cpp | Stock  |
| 8   | icon | `IDI_REGISTRYVALUE`   | 48@8 32@8 16@8 48@32 32@32 16@32            | regfolder.cpp                  | Stock  |

### `system32/ntoskrnl.exe`

| Id  | Type   | Name | Frames or size               | Shown by | Status |
| --- | ------ | ---- | ---------------------------- | -------- | ------ |
| 2   | bitmap | —    | 278 × 15, 4-bit, compressed  | —        | Stock  |
| 3   | bitmap | —    | 213 × 11, 4-bit, compressed  | —        | Stock  |
| 4   | bitmap | —    | 22 × 9, 4-bit, compressed    | —        | Stock  |
| 5   | bitmap | —    | 190 × 224, 4-bit, compressed | —        | Stock  |
| 6   | bitmap | —    | 640 × 55, 4-bit, compressed  | —        | Stock  |
| 7   | bitmap | —    | 640 × 3, 4-bit, compressed   | —        | Stock  |
| 8   | bitmap | —    | 22 × 9, 4-bit, compressed    | —        | Stock  |
| 13  | bitmap | —    | 190 × 224, 4-bit, compressed | —        | Stock  |
| 14  | bitmap | —    | 640 × 55, 4-bit, compressed  | —        | Stock  |
| 15  | bitmap | —    | 640 × 2, 4-bit, compressed   | —        | Stock  |
| 20  | bitmap | —    | 640 × 6, 4-bit, compressed   | —        | Stock  |
| 21  | bitmap | —    | 138 × 15, 4-bit, compressed  | —        | Stock  |
| 22  | bitmap | —    | 185 × 26, 4-bit, compressed  | —        | Stock  |

### `system32/ntvdm.exe`

| Id  | Type | Name | Frames or size                                  | Shown by | Status |
| --- | ---- | ---- | ----------------------------------------------- | -------- | ------ |
| 1   | icon | —    | 32@4 16@4 32@8 16@8 32@32 16@32                 | —        | Stock  |
| 2   | icon | —    | 32@4 16@4 32@8 16@8 32@32 16@32                 | —        | Stock  |
| 3   | icon | —    | 32@4 16@4 32@8 16@8                             | —        | Stock  |
| 4   | icon | —    | 32@4 32@8 32@32                                 | —        | Stock  |
| 5   | icon | —    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Stock  |
| 6   | icon | —    | 32@4 16@4 32@8 16@8 32@32 16@32                 | —        | Stock  |
| 7   | icon | —    | 32@4 16@4 32@8 16@8 32@32 16@32                 | —        | Stock  |
| 8   | icon | —    | 32@4 16@4 32@8 16@8                             | —        | Stock  |
| 9   | icon | —    | 32@4 32@8 32@32                                 | —        | Stock  |
| 10  | icon | —    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Stock  |
| 11  | icon | —    | 32@4 32@8 32@32                                 | —        | Stock  |
| 12  | icon | —    | 32@4 32@8 32@32                                 | —        | Stock  |

### `system32/openglcfg.cpl` (removed by the `base` trim)

| Id  | Type | Name | Frames or size                                  | Shown by | Status  |
| --- | ---- | ---- | ----------------------------------------------- | -------- | ------- |
| 1   | icon | —    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Trimmed |

### `system32/osk.exe` (removed by the `base` trim)

| Id  | Type | Name | Frames or size                                  | Shown by | Status               |
| --- | ---- | ---- | ----------------------------------------------- | -------- | -------------------- |
| 200 | icon | —    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Trimmed (art: `osk`) |
| 201 | icon | —    | 16@4                                            | —        | Trimmed              |
| 202 | icon | —    | 16@4                                            | —        | Trimmed              |
| 203 | icon | —    | 16@4                                            | —        | Trimmed              |
| 204 | icon | —    | 16@4                                            | —        | Trimmed              |
| 205 | icon | —    | 16@4                                            | —        | Trimmed              |
| 206 | icon | —    | 16@8 16@4 16@32                                 | —        | Trimmed              |
| 207 | icon | —    | 16@4                                            | —        | Trimmed              |
| 208 | icon | —    | 16@4                                            | —        | Trimmed              |
| 209 | icon | —    | 16@4                                            | —        | Trimmed              |
| 210 | icon | —    | 16@4                                            | —        | Trimmed              |
| 211 | icon | —    | 16@4                                            | —        | Trimmed              |
| 212 | icon | —    | 16@4                                            | —        | Trimmed              |
| 213 | icon | —    | 16@4                                            | —        | Trimmed              |
| 214 | icon | —    | 16@4                                            | —        | Trimmed              |

### `system32/pifmgr.dll`

| Id  | Type | Name | Frames or size                  | Shown by | Status |
| --- | ---- | ---- | ------------------------------- | -------- | ------ |
| 1   | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 2   | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 3   | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 4   | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 5   | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 6   | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 7   | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 8   | icon | —    | 32@4 16@4 32@8 16@8 32@32 16@32 | —        | Stock  |
| 9   | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 11  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 12  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 13  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 14  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 15  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 16  | icon | —    | 32@4 16@4 32@8 16@8 32@32 16@32 | —        | Stock  |
| 17  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 18  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 19  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 20  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 21  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 22  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 23  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 24  | icon | —    | 32@4 16@4 32@8 16@8 32@32 16@32 | —        | Stock  |
| 25  | icon | —    | 32@4 16@4 32@8 16@8 32@32 16@32 | —        | Stock  |
| 26  | icon | —    | 32@4 16@4 32@8 16@8 32@32 16@32 | —        | Stock  |
| 27  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 28  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 29  | icon | —    | 32@4 16@4 32@8 16@8 32@32 16@32 | —        | Stock  |
| 30  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 31  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 32  | icon | —    | 32@4 16@4 32@8 16@8 32@32 16@32 | —        | Stock  |
| 33  | icon | —    | 32@4 16@4 32@8 16@8 32@32 16@32 | —        | Stock  |
| 34  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 35  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 36  | icon | —    | 32@4 16@4 32@8 16@8 32@32 16@32 | —        | Stock  |
| 37  | icon | —    | 32@4 16@4 32@8 16@8 32@32 16@32 | —        | Stock  |
| 38  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |
| 39  | icon | —    | 32@4 32@8 32@32                 | —        | Stock  |

### `system32/powercfg.cpl`

| Id  | Type | Name                   | Frames or size                                  | Shown by                                                                 | Status              |
| --- | ---- | ---------------------- | ----------------------------------------------- | ------------------------------------------------------------------------ | ------------------- |
| 100 | icon | `IDI_AC`               | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | IDD_POWERSCHEMESPAGE_ACDC, powermeter.c                                  | Afterglow (`power`) |
| 101 | icon | `IDI_DC`               | 32@8 32@24 32@32                                | IDD_POWERSCHEMESPAGE_ACDC                                                | Stock               |
| 102 | icon | `IDI_ACDC`             | 32@8 32@24 32@32                                | IDD_POWERSCHEMESPAGE_AC, IDD_POWERSCHEMESPAGE_ACDC, IDD_PROPPAGEADVANCED | Stock               |
| 103 | icon | `IDI_SCREEN`           | 32@8 32@24 32@32                                | —                                                                        | Stock               |
| 104 | icon | `IDI_HIBERNATE`        | 32@8 32@24 32@32                                | IDD_PROPPAGEHIBERNATE                                                    | Stock               |
| 110 | icon | `IDI_BAT_CHARGE_CRIT`  | 32@8 32@24 32@32                                | powermeter.c                                                             | Stock               |
| 111 | icon | `IDI_BAT_CHARGE_LOW`   | 32@8 32@24 32@32                                | powermeter.c                                                             | Stock               |
| 112 | icon | `IDI_BAT_CHARGE_HALF`  | 32@8 32@24 32@32                                | powermeter.c                                                             | Stock               |
| 113 | icon | `IDI_BAT_CHARGE_HIGH`  | 32@8 32@24 32@32                                | powermeter.c                                                             | Stock               |
| 114 | icon | `IDI_BAT_CHARGE_FULL`  | 32@8 32@24 32@32                                | powermeter.c                                                             | Stock               |
| 115 | icon | `IDI_BAT_DISCHRG_CRIT` | 32@8 32@24 32@32                                | powermeter.c                                                             | Stock               |
| 116 | icon | `IDI_BAT_DISCHRG_LOW`  | 32@8 32@24 32@32                                | powermeter.c                                                             | Stock               |
| 117 | icon | `IDI_BAT_DISCHRG_HALF` | 32@8 32@24 32@32                                | powermeter.c                                                             | Stock               |
| 118 | icon | `IDI_BAT_DISCHRG_HIGH` | 32@8 32@24 32@32                                | powermeter.c                                                             | Stock               |
| 119 | icon | `IDI_BAT_DISCHRG_FULL` | 32@8 32@24 32@32                                | powermeter.c                                                             | Stock               |
| 120 | icon | `IDI_BAT_UNKNOWN`      | 32@8 32@24 32@32                                | powermeter.c                                                             | Stock               |
| 121 | icon | `IDI_BAT_NONE`         | 32@8 32@24 32@32                                | —                                                                        | Stock               |

### `system32/progman.exe` (removed by the `base` trim)

| Id  | Type | Name | Frames or size                                  | Shown by | Status  |
| --- | ---- | ---- | ----------------------------------------------- | -------- | ------- |
| 1   | icon | —    | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Trimmed |
| 8   | icon | —    | 32@8 16@8 32@32 16@32                           | —        | Trimmed |
| 9   | icon | —    | 32@8 16@8 32@32 16@32                           | —        | Trimmed |
| 10  | icon | —    | 32@4 16@4 32@8 16@8 32@32 16@32                 | —        | Trimmed |
| 48  | icon | —    | 32@8 16@8 32@32 16@32                           | —        | Trimmed |
| 49  | icon | —    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Trimmed |

### `system32/rapps.exe`

| Id  | Type | Name                  | Frames or size                                                  | Shown by                                       | Status                   |
| --- | ---- | --------------------- | --------------------------------------------------------------- | ---------------------------------------------- | ------------------------ |
| 10  | icon | `IDI_MAIN`            | 48@4 32@4 24@4 16@4 48@8 32@8 24@8 16@8 48@32 32@32 24@32 16@32 | appview.cpp, geninst.cpp, gui.cpp, loaddlg.cpp | Afterglow (`appmanager`) |
| 11  | icon | `IDI_EXIT`            | 24@8                                                            | appview.cpp                                    | Stock                    |
| 12  | icon | `IDI_INSTALL`         | 24@8 24@32                                                      | appview.cpp                                    | Stock                    |
| 13  | icon | `IDI_UNINSTALL`       | 24@8 24@32                                                      | appview.cpp                                    | Stock                    |
| 14  | icon | `IDI_SETTINGS`        | 24@8 24@32                                                      | appview.cpp                                    | Stock                    |
| 15  | icon | `IDI_MODIFY`          | 24@8 24@32                                                      | appview.cpp                                    | Stock                    |
| 16  | icon | `IDI_REFRESH`         | 24@8 24@32                                                      | appview.cpp                                    | Stock                    |
| 17  | icon | `IDI_APPS`            | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 18  | icon | `IDI_APPUPD`          | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 19  | icon | `IDI_CATEGORY`        | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 20  | icon | `IDI_UPDATE_DB`       | 24@8 24@32                                                      | appview.cpp                                    | Stock                    |
| 21  | icon | `IDI_CHECK_ALL`       | 24@8 24@32                                                      | appview.cpp                                    | Stock                    |
| 22  | icon | `IDI_SELECTEDFORINST` | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 23  | icon | `IDI_BROKEN_IMAGE`    | 192@32                                                          | appview.cpp                                    | Stock                    |
| 50  | icon | `IDI_CAT_AUDIO`       | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 51  | icon | `IDI_CAT_DEVEL`       | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 52  | icon | `IDI_CAT_DRIVERS`     | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 53  | icon | `IDI_CAT_EDU`         | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 54  | icon | `IDI_CAT_ENGINEER`    | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 55  | icon | `IDI_CAT_FINANCE`     | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 56  | icon | `IDI_CAT_GAMES`       | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 57  | icon | `IDI_CAT_GRAPHICS`    | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 58  | icon | `IDI_CAT_INTERNET`    | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 59  | icon | `IDI_CAT_LIBS`        | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 60  | icon | `IDI_CAT_OFFICE`      | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 61  | icon | `IDI_CAT_OTHER`       | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 62  | icon | `IDI_CAT_SCIENCE`     | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 63  | icon | `IDI_CAT_TOOLS`       | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 64  | icon | `IDI_CAT_VIDEO`       | 24@8 24@32                                                      | gui.cpp                                        | Stock                    |
| 65  | icon | `IDI_CAT_THEMES`      | 24@32                                                           | gui.cpp                                        | Stock                    |

### `system32/rasdlg.dll`

| Id    | Type   | Name | Frames or size                                                  | Shown by | Status |
| ----- | ------ | ---- | --------------------------------------------------------------- | -------- | ------ |
| 50    | icon   | —    | 16@4                                                            | —        | Stock  |
| 51    | icon   | —    | 16@4                                                            | —        | Stock  |
| 52    | icon   | —    | 32@8 32@24 32@32                                                | —        | Stock  |
| 53    | icon   | —    | 32@8 32@24 32@32                                                | —        | Stock  |
| 54    | icon   | —    | 32@8 32@24 32@32                                                | —        | Stock  |
| 55    | icon   | —    | 32@8 32@24 32@32                                                | —        | Stock  |
| 56    | icon   | —    | 16@8 32@8 16@24 32@24 16@32 32@32                               | —        | Stock  |
| 57    | icon   | —    | 32@8 32@24 32@32                                                | —        | Stock  |
| 58    | icon   | —    | 32@8 32@24 32@32                                                | —        | Stock  |
| 59    | icon   | —    | 32@8 32@24 32@32                                                | —        | Stock  |
| 60    | icon   | —    | 16@4                                                            | —        | Stock  |
| 61    | icon   | —    | 16@4                                                            | —        | Stock  |
| 62    | icon   | —    | 16@4                                                            | —        | Stock  |
| 63    | icon   | —    | 16@4                                                            | —        | Stock  |
| 134   | icon   | —    | 16@4 16@32                                                      | —        | Stock  |
| 135   | icon   | —    | 16@4 16@32                                                      | —        | Stock  |
| 144   | icon   | —    | 16@4 16@32                                                      | —        | Stock  |
| 145   | icon   | —    | 16@4 16@32                                                      | —        | Stock  |
| 562   | icon   | —    | 48@4 32@4 24@4 16@4 48@8 32@8 24@8 16@8 48@32 32@32 24@32 16@32 | —        | Stock  |
| 563   | icon   | —    | 48@8 32@8 16@8 48@32 32@32 16@32                                | —        | Stock  |
| 15102 | icon   | —    | 32@8 32@24 32@32                                                | —        | Stock  |
| 100   | bitmap | —    | 400 × 80, 4-bit                                                 | —        | Stock  |
| 101   | bitmap | —    | 164 × 314, 8-bit                                                | —        | Stock  |
| 102   | bitmap | —    | 49 × 49, 8-bit                                                  | —        | Stock  |
| 1678  | bitmap | —    | 400 × 80, 8-bit                                                 | —        | Stock  |

### `ReactOS/regedit.exe`

| Id  | Type | Name          | Frames or size                                  | Shown by                     | Status                          |
| --- | ---- | ------------- | ----------------------------------------------- | ---------------------------- | ------------------------------- |
| 100 | icon | `IDI_REGEDIT` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | about.c, IDD_FINDING, main.c | **Stock, art ready**: `regedit` |
| 101 | icon | `IDI_REGFILE` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —                            | **Stock, art ready**: `regfile` |
| 102 | icon | `IDI_ARROW`   | 12@24                                           | childwnd.c                   | Stock                           |
| 135 | icon | `IDI_STRING`  | 16@32                                           | listview.c                   | Stock                           |
| 136 | icon | `IDI_BIN`     | 16@32                                           | listview.c                   | Stock                           |

### `system32/regedt32.exe`

| Id  | Type | Name | Frames or size                                     | Shown by | Status |
| --- | ---- | ---- | -------------------------------------------------- | -------- | ------ |
| 101 | icon | —    | 48@8 32@8 16@8 48@32 32@32 16@32 48@24 32@24 16@24 | —        | Stock  |

### `system32/rundll32.exe`

| Id  | Type | Name | Frames or size                   | Shown by | Status |
| --- | ---- | ---- | -------------------------------- | -------- | ------ |
| 100 | icon | —    | 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Stock  |

### `system32/runonce.exe`

| Id  | Type | Name | Frames or size                   | Shown by | Status |
| --- | ---- | ---- | -------------------------------- | -------- | ------ |
| 10  | icon | —    | 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Stock  |

### `system32/screenshot.exe` (removed by the `base` trim)

| Id  | Type | Name | Frames or size                   | Shown by | Status  |
| --- | ---- | ---- | -------------------------------- | -------- | ------- |
| 1   | icon | —    | 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Trimmed |

### `system32/servman.exe`

| Id    | Type   | Name            | Frames or size                                  | Shown by                                                                    | Status                          |
| ----- | ------ | --------------- | ----------------------------------------------- | --------------------------------------------------------------------------- | ------------------------------- |
| 50    | icon   | `IDI_SM_ICON`   | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | create.c, delete.c, listview.c, mainwnd.c, propsheet.c, stop_dependencies.c | **Stock, art ready**: `servman` |
| 52    | icon   | `IDI_NODEPENDS` | 16@4 32@4 16@8 32@8 16@32 32@32                 | propsheet_depends.c                                                         | Stock                           |
| 53    | icon   | `IDI_SERVICE`   | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —                                                                           | Stock                           |
| 54    | icon   | `IDI_DRIVER`    | 32@4 16@4 32@8 16@8 32@32 16@32                 | propsheet_depends.c                                                         | Stock                           |
| 10000 | bitmap | `IDB_PROP`      | 16 × 16, 24-bit                                 | mainwnd.c                                                                   | Stock                           |
| 10001 | bitmap | `IDB_REFRESH`   | 16 × 16, 24-bit                                 | —                                                                           | Stock                           |
| 10002 | bitmap | `IDB_EXPORT`    | 16 × 16, 24-bit                                 | —                                                                           | Stock                           |
| 10003 | bitmap | `IDB_CREATE`    | 16 × 16, 24-bit                                 | —                                                                           | Stock                           |
| 10004 | bitmap | `IDB_DELETE`    | 16 × 16, 24-bit                                 | —                                                                           | Stock                           |
| 10005 | bitmap | `IDB_START`     | 16 × 16, 24-bit                                 | —                                                                           | Stock                           |
| 10006 | bitmap | `IDB_STOP`      | 16 × 16, 24-bit                                 | —                                                                           | Stock                           |
| 10007 | bitmap | `IDB_PAUSE`     | 16 × 16, 24-bit                                 | —                                                                           | Stock                           |
| 10008 | bitmap | `IDB_RESTART`   | 16 × 16, 24-bit                                 | mainwnd.c                                                                   | Stock                           |

### `system32/setupapi.dll`

| Id  | Type | Name                        | Frames or size                                  | Shown by | Status |
| --- | ---- | --------------------------- | ----------------------------------------------- | -------- | ------ |
| 1   | icon | `IDI_SETUPAPI_DISP_ADAPT`   | 48@8 32@8 24@8 16@8 48@32 32@32 24@32 16@32     | —        | Stock  |
| 2   | icon | `IDI_SETUPAPI_MOUSE`        | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 3   | icon | `IDI_SETUPAPI_KEYBOARD`     | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 4   | icon | `IDI_SETUPAPI_PRINTER`      | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 5   | icon | `IDI_SETUPAPI_NETCARD`      | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 6   | icon | `IDI_SETUPAPI_NODE`         | 32@32 32@8 16@32 16@8                           | —        | Stock  |
| 7   | icon | `IDI_SETUPAPI_COMPUTER`     | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 8   | icon | `IDI_SETUPAPI_SHCOMPUTER`   | 32@8 16@8 32@32 16@32                           | —        | Stock  |
| 9   | icon | `IDI_SETUPAPI_DRV_CONTROL`  | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 10  | icon | `IDI_SETUPAPI_POWER`        | 32@8 16@8 32@32 16@32                           | —        | Stock  |
| 11  | icon | `IDI_SETUPAPI_CARD`         | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 18  | icon | `IDI_SETUPAPI_UNKNOWN`      | 16@8 32@8 48@8 16@32 32@32 48@32                | —        | Stock  |
| 19  | icon | `IDI_SETUPAPI_LEGACY_DRV`   | 32@8 48@8 32@8 16@8 48@32 32@32 16@32           | —        | Stock  |
| 20  | icon | `IDI_SETUPAPI_USB`          | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 21  | icon | `IDI_SETUPAPI_REM_DRIVE`    | 32@4 16@4                                       | —        | Stock  |
| 22  | icon | `IDI_SETUPAPI_SATELLITE`    | 32@4 16@4                                       | —        | Stock  |
| 23  | icon | `IDI_SETUPAPI_PORTS`        | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 24  | icon | `IDI_SETUPAPI_HID`          | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 25  | icon | `IDI_SETUPAPI_NEEDSNAME1`   | 32@4 16@4                                       | —        | Stock  |
| 26  | icon | `IDI_SETUPAPI_NEEDSNAME2`   | 16@8 32@8 16@32 32@32                           | —        | Stock  |
| 27  | icon | `IDI_SETUPAPI_MYCOMPUTER`   | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 28  | icon | `IDI_SETUPAPI_PROCESSOR`    | 32@8 24@8 16@8 32@8 24@8 16@8 32@32 24@32 16@32 | —        | Stock  |
| 40  | icon | `IDI_SETUPAPI_SIGNED_DRV`   | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 41  | icon | `IDI_SETUPAPI_BLANK`        | 32@4 16@4                                       | —        | Stock  |
| 42  | icon | `IDI_SETUPAPI_WARNING`      | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 43  | icon | `IDI_SETUPAPI_DEVICES`      | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 50  | icon | `IDI_SETUPAPI_FLOPPY`       | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 51  | icon | `IDI_SETUPAPI_CDROM`        | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 52  | icon | `IDI_SETUPAPI_NETDRIVE`     | 48@8 32@8 16@8 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Stock  |
| 53  | icon | `IDI_SETUPAPI_HARDDRIVE`    | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 54  | icon | `IDI_SETUPAPI_NEEDSNAME3`   | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 105 | icon | `IDI_SETUPAPI_314FLOP`      | 48@8 32@8 16@8 48@32 32@32 16@32                | —        | Stock  |
| 159 | icon | `IDI_SETUPAPI_CHIP`         | 16@8 32@8 16@32 32@32                           | —        | Stock  |
| 161 | icon | `IDI_SETUPAPI_ERROR`        | 32@8 32@32                                      | —        | Stock  |
| 500 | icon | `IDI_SETUPAPI_WARN_OVERLAY` | 32@8 16@8 32@32 16@32                           | —        | Stock  |
| 501 | icon | `IDI_SETUPAPI_ERR_OVERLAY`  | 32@8 16@8 32@32 16@32                           | —        | Stock  |
| 502 | icon | `IDI_SETUPAPI_INFO_OVERLAY` | 32@8 16@8 32@32 16@32                           | —        | Stock  |

### `system32/shell32.dll`

| Id    | Type   | Name                             | Frames or size                                                      | Shown by                                                                                   | Status                                 |
| ----- | ------ | -------------------------------- | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | -------------------------------------- |
| 1     | icon   | `IDI_SHELL_DOCUMENT`             | 48@8 32@8 16@8 48@32 32@32 16@32                                    | dialogs/filetypes.cpp, folders/CFSFolder.cpp, folders/CRegFolder.cpp, iconcache.cpp        | Afterglow (`doc`)                      |
| 2     | icon   | `IDI_SHELL_RICH_TEXT`            | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 3     | icon   | `IDI_SHELL_EXE`                  | 48@8 32@8 16@8 48@32 32@32 16@32                                    | dialogs/filetypes.cpp, folders/CFSFolder.cpp                                               | Afterglow (`program`)                  |
| 4     | icon   | `IDI_SHELL_FOLDER`               | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | CNewMenu.cpp, brfolder.cpp, dialogs/filedefext.cpp, folders/CFSFolder.cpp, wine/shell32_ma | Afterglow (`folder`)                   |
| 5     | icon   | `IDI_SHELL_FOLDER_OPEN`          | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Afterglow (`folderopen`)               |
| 6     | icon   | `IDI_SHELL_5_12_FLOPPY`          | 16@4 16@8 16@32 32@4 32@8 32@32 48@4 48@8 48@32                     | —                                                                                          | Stock                                  |
| 7     | icon   | `IDI_SHELL_3_14_FLOPPY`          | 16@4 16@8 16@32 32@4 32@8 32@32 48@4 48@8 48@32                     | dialogs/drvdefext.cpp, folders/CDrivesFolder.cpp                                           | Afterglow (`floppy`)                   |
| 8     | icon   | `IDI_SHELL_REMOVEABLE`           | 48@8 32@8 16@8 48@32 32@32 16@32                                    | dialogs/drvdefext.cpp, folders/CDrivesFolder.cpp                                           | Afterglow (`removable`)                |
| 9     | icon   | `IDI_SHELL_DRIVE`                | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | dialogs/drvdefext.cpp, folders/CDrivesFolder.cpp                                           | Afterglow (`hdd`)                      |
| 10    | icon   | `IDI_SHELL_NETDRIVE`             | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | dialogs/drvdefext.cpp, folders/CDrivesFolder.cpp                                           | Afterglow (`netdrive`)                 |
| 11    | icon   | `IDI_SHELL_NETDRIVE_OFF`         | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Stock                                  |
| 12    | icon   | `IDI_SHELL_CDROM`                | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | dialogs/drvdefext.cpp, folders/CDrivesFolder.cpp                                           | Afterglow (`cd`)                       |
| 13    | icon   | `IDI_SHELL_RAMDISK`              | 48@8 48@32 32@4 32@32                                               | dialogs/drvdefext.cpp, folders/CDrivesFolder.cpp                                           | Afterglow (`ramdisk`)                  |
| 14    | icon   | `IDI_SHELL_ENTIRE_NETWORK`       | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Stock                                  |
| 15    | icon   | `IDI_SHELL_NETWORK`              | 48@8 32@8 16@8 48@32 32@32 16@32                                    | wine/shellpath.c                                                                           | Afterglow (`network`)                  |
| 16    | icon   | `IDI_SHELL_MY_COMPUTER`          | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Afterglow (`mycomputer`)               |
| 17    | icon   | `IDI_SHELL_PRINTER`              | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | folders/CPrinterFolder.cpp                                                                 | Stock                                  |
| 18    | icon   | `IDI_SHELL_MY_NETWORK_PLACES`    | 48@8 32@8 16@8 48@32 32@32 16@32                                    | CDefView.cpp                                                                               | Afterglow (`network`)                  |
| 19    | icon   | `IDI_SHELL_COMPUTERS_NEAR_ME`    | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 20    | icon   | `IDI_SHELL_PROGRAMS_FOLDER`      | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | COpenWithMenu.cpp                                                                          | Afterglow (`programsfolder`)           |
| 21    | icon   | `IDI_SHELL_RECENT_DOCUMENTS`     | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | wine/shellpath.c                                                                           | Afterglow (`recent`)                   |
| 22    | icon   | `IDI_SHELL_CONTROL_PANEL`        | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | shellmenu/CStartMenu.cpp, wine/control.c, wine/shellpath.c                                 | Afterglow (`controlpanel`)             |
| 23    | icon   | `IDI_SHELL_SEARCH`               | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Afterglow (`search`)                   |
| 24    | icon   | `IDI_SHELL_HELP`                 | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Afterglow (`help`)                     |
| 25    | icon   | `IDI_SHELL_RUN`                  | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | dialogs/dialogs.cpp                                                                        | Stock                                  |
| 26    | icon   | `IDI_SHELL_SLEEP`                | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Stock                                  |
| 27    | icon   | `IDI_SHELL_HARDWARE_REMOVE`      | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4                     | —                                                                                          | Stock                                  |
| 28    | icon   | `IDI_SHELL_SHUTDOWN`             | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Stock                                  |
| 29    | icon   | `IDI_SHELL_SHARE`                | 16@4 32@4 48@4 16@8 32@8 48@8 16@32 32@32 48@32                     | —                                                                                          | Stock                                  |
| 30    | icon   | `IDI_SHELL_SHORTCUT`             | 32@8 16@8 32@32 16@32                                               | CNewMenu.cpp, CShellLink.cpp, iconcache.cpp                                                | Afterglow (`arrow`)                    |
| 31    | icon   | `IDI_SHELL_FOLDER_WAIT`          | 32@8 16@8 32@32 16@32                                               | —                                                                                          | Stock                                  |
| 32    | icon   | `IDI_SHELL_EMPTY_RECYCLE_BIN`    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Afterglow (`recycle`)                  |
| 33    | icon   | `IDI_SHELL_FULL_RECYCLE_BIN`     | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Afterglow (`recyclefull`)              |
| 34    | icon   | `IDI_SHELL_DIALUP_FOLDER`        | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 35    | icon   | `IDI_SHELL_DESKTOP`              | 48@32 32@32 16@32                                                   | folders/CRegFolder.cpp                                                                     | Afterglow (`desktop`)                  |
| 36    | icon   | `IDI_SHELL_CONTROL_PANEL2`       | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 37    | icon   | `IDI_SHELL_PROGRAMS_FOLDER2`     | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | IDD_FOLDER_OPTIONS_VIEW                                                                    | Stock                                  |
| 38    | icon   | `IDI_SHELL_PRINTERS_FOLDER`      | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | wine/shell32_main.c, wine/shellpath.c                                                      | Afterglow (`printers`)                 |
| 39    | icon   | `IDI_SHELL_FONTS_FOLDER`         | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | wine/shellpath.c                                                                           | Afterglow (`fonts`)                    |
| 40    | icon   | `IDI_SHELL_TSKBAR_STARTMENU`     | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | shellmenu/CStartMenu.cpp, wine/shellpath.c                                                 | Afterglow (`taskbarstart`)             |
| 41    | icon   | `IDI_SHELL_CD_MUSIC`             | 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                          | —                                                                                          | Stock                                  |
| 42    | icon   | `IDI_SHELL_TREE`                 | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 43    | icon   | `IDI_SHELL_COMPUTER_FOLDER`      | 48@8 32@8 16@8 48@32 32@32 16@32                                    | wine/shellpath.c                                                                           | Afterglow (`mycomputer`)               |
| 44    | icon   | `IDI_SHELL_FAVORITES`            | 48@4 32@4 16@4 48@24 32@8 16@8 48@32 32@32 16@32                    | wine/shellpath.c                                                                           | Afterglow (`favorites`)                |
| 45    | icon   | `IDI_SHELL_LOGOFF`               | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | IDD_LOG_OFF                                                                                | Afterglow (`logoff`)                   |
| 46    | icon   | `IDI_SHELL_EXPLORER`             | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Stock                                  |
| 47    | icon   | `IDI_SHELL_UPDATE`               | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 48    | icon   | `IDI_SHELL_LOCKED`               | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Stock                                  |
| 49    | icon   | `IDI_SHELL_DISCONN`              | 16@32 32@32                                                         | IDD_DISCONNECT                                                                             | Stock                                  |
| 50    | icon   | `IDI_SHELL_NONE_50`              | 16@4                                                                | —                                                                                          | Stock                                  |
| 51    | icon   | `IDI_SHELL_NONE_51`              | 16@4                                                                | —                                                                                          | Stock                                  |
| 52    | icon   | `IDI_SHELL_NONE_52`              | 16@4                                                                | —                                                                                          | Stock                                  |
| 53    | icon   | `IDI_SHELL_NONE_53`              | 16@4                                                                | —                                                                                          | Stock                                  |
| 54    | icon   | `IDI_SHELL_NOT_CONNECTED_HDD`    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | folders/CDrivesFolder.cpp                                                                  | Afterglow (`netdriveoff`)              |
| 133   | icon   | `IDI_SHELL_MULTIPLE_FILES`       | 48@8 32@8 16@8 48@32 32@32 16@32                                    | dialogs/filedefext.cpp                                                                     | Stock                                  |
| 134   | icon   | `IDI_SHELL_OPEN_WITH`            | 16@8 24@8 32@8 48@8 16@24 24@24 32@24 48@24 16@32 24@32 32@32 48@32 | IDD_OPEN_WITH                                                                              | Stock                                  |
| 135   | icon   | `IDI_SHELL_FIND_COMPUTER`        | 16@8 16@32                                                          | —                                                                                          | Stock                                  |
| 137   | icon   | `IDI_SHELL_CONTROL_PANEL3`       | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Afterglow (`controlpanel`)             |
| 138   | icon   | `IDI_SHELL_PRINTER2`             | 48@8 32@8 16@8 48@32 32@32 16@32                                    | shellmenu/CStartMenu.cpp                                                                   | Afterglow (`printers`)                 |
| 139   | icon   | `IDI_SHELL_PRINTER_ADD`          | 16@8 32@8 48@8 16@32 32@32 48@32                                    | —                                                                                          | Stock                                  |
| 140   | icon   | `IDI_SHELL_NET_PRINTER`          | 16@8 32@8 48@8 16@32 32@32 48@32                                    | —                                                                                          | Stock                                  |
| 141   | icon   | `IDI_SHELL_FILE_PRINTER`         | 16@8 32@8 48@8 16@32 32@32 48@32                                    | —                                                                                          | Stock                                  |
| 142   | icon   | `IDI_SHELL_TRASH_FILE`           | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | shlfileop.cpp                                                                              | Stock                                  |
| 143   | icon   | `IDI_SHELL_TRASH_FOLDER`         | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 144   | icon   | `IDI_SHELL_TRASH_FILE_FOLDER`    | 48@8 16@8 32@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 145   | icon   | `IDI_SHELL_FILE_COPY_DELTE`      | 32@8 32@32                                                          | —                                                                                          | Stock                                  |
| 146   | icon   | `IDI_SHELL_FOLDER_MOVE1`         | 48@8 32@8 24@8 16@8 48@32 32@32 24@32 16@32                         | —                                                                                          | Stock                                  |
| 147   | icon   | `IDI_SHELL_FOLDER_RENAME`        | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 148   | icon   | `IDI_SHELL_SETTINGS_FOLDER`      | 32@8 32@32                                                          | —                                                                                          | Stock                                  |
| 151   | icon   | `IDI_SHELL_INF_FILE`             | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Afterglow (`inifile`)                  |
| 152   | icon   | `IDI_SHELL_TEXT_FILE`            | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Afterglow (`text`)                     |
| 153   | icon   | `IDI_SHELL_BAT_FILE`             | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Afterglow (`batch`)                    |
| 154   | icon   | `IDI_SHELL_SYSTEM_FILE`          | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | IDD_NOOPEN                                                                                 | Afterglow (`library`)                  |
| 155   | icon   | `IDI_SHELL_FONT_FILE`            | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Afterglow (`font`)                     |
| 156   | icon   | `IDI_SHELL_TT_FONT_FILE`         | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Afterglow (`font`)                     |
| 157   | icon   | `IDI_SHELL_FONT_FILE2`           | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Stock                                  |
| 160   | icon   | `IDI_SHELL_RUN2`                 | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Stock                                  |
| 161   | icon   | `IDI_SHELL_CONFIRM_DELETE`       | 32@32 32@8                                                          | shlfileop.cpp                                                                              | Stock                                  |
| 165   | icon   | `IDI_SHELL_TOOLS_BACKUP`         | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4                     | IDD_DRIVE_TOOLS                                                                            | Stock                                  |
| 166   | icon   | `IDI_SHELL_TOOLS_CHKDSK`         | 32@32 32@8                                                          | IDD_DRIVE_TOOLS                                                                            | Stock                                  |
| 167   | icon   | `IDI_SHELL_TOOLS_DEFRAG`         | 32@8 32@32                                                          | IDD_DRIVE_TOOLS                                                                            | Stock                                  |
| 168   | icon   | `IDI_SHELL_PRINTER_OK`           | 16@8 32@8 48@8 16@32 32@32 48@32                                    | —                                                                                          | Stock                                  |
| 169   | icon   | `IDI_SHELL_NET_PRINTER_OK`       | 16@8 32@8 48@8 16@32 32@32 48@32 32@32                              | —                                                                                          | Stock                                  |
| 170   | icon   | `IDI_SHELL_FILE_PRINTER_OK`      | 16@8 32@8 48@8 16@32 32@32 48@32                                    | —                                                                                          | Stock                                  |
| 171   | icon   | `IDI_SHELL_CHART`                | 48@32 32@32 16@32                                                   | —                                                                                          | Stock                                  |
| 172   | icon   | `IDI_SHELL_NETWORK_FOLDER`       | 48@8 32@8 16@8 48@32 32@32 16@32                                    | folders/CNetFolder.cpp, wine/shellpath.c                                                   | Afterglow (`network`)                  |
| 173   | icon   | `IDI_SHELL_FAVORITES2`           | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Stock                                  |
| 174   | icon   | `IDI_SHELL_EXTENDED_PROPERTIES`  | 32@32 32@4 32@24                                                    | IDD_SHORTCUT_EXTENDED_PROPERTIES                                                           | Stock                                  |
| 175   | icon   | `IDI_SHELL_NETWORK_CONNECTIONS`  | 48@4 32@4 24@4 16@4 48@8 32@8 24@8 16@8 48@32 32@32 24@32 16@32     | wine/shellpath.c                                                                           | Stock                                  |
| 176   | icon   | `IDI_SHELL_NETWORK_CHART`        | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 177   | icon   | `IDI_SHELL_VIEW_SETTINGS`        | 32@32 16@32                                                         | —                                                                                          | Stock                                  |
| 178   | icon   | `IDI_SHELL_INTERNET_CHART`       | 48@32 32@32 16@32                                                   | —                                                                                          | Stock                                  |
| 179   | icon   | `IDI_SHELL_COMPUTER_SYNC`        | 32@32 16@32                                                         | —                                                                                          | Stock                                  |
| 180   | icon   | `IDI_SHELL_COMPUTER_WINDOW`      | 32@32                                                               | —                                                                                          | Stock                                  |
| 181   | icon   | `IDI_SHELL_COMPUTER_DESKTOP`     | 32@32                                                               | CDefView.cpp                                                                               | **Stock, drawn here**: `mycomputer`    |
| 182   | icon   | `IDI_SHELL_SHOW_COMMON_TASKS`    | 32@4 32@8 32@32                                                     | dialogs/general.cpp                                                                        | Stock                                  |
| 183   | icon   | `IDI_SHELL_CLASSIC_FOLDERS`      | 32@4 32@8 32@32                                                     | dialogs/general.cpp                                                                        | Stock                                  |
| 184   | icon   | `IDI_SHELL_OPEN_IN_SOME_WINDOW`  | 32@8 32@32                                                          | dialogs/general.cpp                                                                        | Stock                                  |
| 185   | icon   | `IDI_SHELL_OPEN_IN_NEW_WINDOW`   | 32@8 32@32                                                          | dialogs/general.cpp                                                                        | Stock                                  |
| 186   | icon   | `IDI_SHELL_SINGLE_CLICK_TO_OPEN` | 32@8 32@32                                                          | dialogs/general.cpp                                                                        | Stock                                  |
| 187   | icon   | `IDI_SHELL_DOUBLE_CLICK_TO_OPEN` | 32@8 32@32                                                          | dialogs/general.cpp                                                                        | Stock                                  |
| 191   | icon   | `IDI_SHELL_EMPTY_RECYCLE_BIN1`   | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Stock                                  |
| 192   | icon   | `IDI_SHELL_FULL_RECYCLE_BIN1`    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Stock                                  |
| 193   | icon   | `IDI_SHELL_WEB_FOLDERS`          | 48@32 32@32 16@32                                                   | —                                                                                          | Stock                                  |
| 194   | icon   | `IDI_SHELL_SECURITY`             | 32@32                                                               | IDD_RUN_AS                                                                                 | Stock                                  |
| 196   | icon   | `IDI_SHELL_FAX`                  | 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                          | —                                                                                          | Stock                                  |
| 197   | icon   | `IDI_SHELL_FAX_OK`               | 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                          | —                                                                                          | Stock                                  |
| 198   | icon   | `IDI_SHELL_NET_FAX_OK`           | 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                          | —                                                                                          | Stock                                  |
| 199   | icon   | `IDI_SHELL_NET_FAX`              | 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                          | —                                                                                          | Stock                                  |
| 200   | icon   | `IDI_SHELL_NO`                   | 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                          | —                                                                                          | Stock                                  |
| 210   | icon   | `IDI_SHELL_FOLDER_OPTIONS`       | 48@32 48@8 48@4 32@32 32@8 32@4 16@8 16@32 16@4                     | dialogs/folder_options.cpp                                                                 | Afterglow (`folderopts`)               |
| 220   | icon   | `IDI_SHELL_USERS2`               | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 221   | icon   | `IDI_SHELL_TURN_OFF`             | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 222   | icon   | `IDI_SHELL_DVD_ROM`              | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 223   | icon   | `IDI_SHELL_PAGES`                | 32@8 32@32                                                          | —                                                                                          | Stock                                  |
| 224   | icon   | `IDI_SHELL_MOVIE_FILE`           | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Afterglow (`video`)                    |
| 225   | icon   | `IDI_SHELL_MUSIC_FILE`           | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Afterglow (`audio`)                    |
| 226   | icon   | `IDI_SHELL_PICTURE_FILE`         | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 227   | icon   | `IDI_SHELL_MULTIMEDIA_FILE`      | 48@32 32@32 16@32                                                   | —                                                                                          | Stock                                  |
| 228   | icon   | `IDI_SHELL_CD_MUSIC2`            | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 229   | icon   | `IDI_SHELL_MOUSE`                | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 230   | icon   | `IDI_SHELL_ZIP_DRIVE2`           | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 231   | icon   | `IDI_SHELL_ARROWN_DOWN`          | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 232   | icon   | `IDI_SHELL_ARROWN_DOWN1`         | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 233   | icon   | `IDI_SHELL_FDD`                  | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 234   | icon   | `IDI_SHELL_NO_DRIVE`             | 32@32                                                               | —                                                                                          | Stock                                  |
| 235   | icon   | `IDI_SHELL_MY_DOCUMENTS`         | 48@4 32@4 16@4 48@32 32@8 16@8 48@24 32@32 16@32                    | shellmenu/CStartMenu.cpp, wine/shellpath.c                                                 | Afterglow (`mydocs`)                   |
| 236   | icon   | `IDI_SHELL_MY_PICTURES`          | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | shellmenu/CStartMenu.cpp, wine/shellpath.c                                                 | Afterglow (`mypictures`)               |
| 237   | icon   | `IDI_SHELL_MY_MUSIC`             | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | wine/shellpath.c                                                                           | Afterglow (`mymusic`)                  |
| 238   | icon   | `IDI_SHELL_MY_MOVIES`            | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | wine/shellpath.c                                                                           | Afterglow (`myvideos`)                 |
| 239   | icon   | `IDI_SHELL_WEB_BROWSER2`         | 16@8 32@8 48@8 16@32 32@32 48@32                                    | —                                                                                          | Stock                                  |
| 240   | icon   | `IDI_SHELL_FULL_RECYCLE_BIN2`    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Stock                                  |
| 241   | icon   | `IDI_SHELL_FILE_MOVE`            | 16@8 16@32                                                          | —                                                                                          | Stock                                  |
| 242   | icon   | `IDI_SHELL_RENAME`               | 16@8 32@8 48@8 16@32 32@32 48@32                                    | —                                                                                          | Stock                                  |
| 243   | icon   | `IDI_SHELL_FILES`                | 16@8 16@32                                                          | —                                                                                          | Stock                                  |
| 244   | icon   | `IDI_SHELL_MOVE_INTERNET`        | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 245   | icon   | `IDI_SHELL_PRINTER3`             | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 246   | icon   | `IDI_SHELL_ICON_246`             | 16@8 16@24 16@32                                                    | —                                                                                          | Stock                                  |
| 247   | icon   | `IDI_SHELL_WEB_MUSIC`            | 16@8 16@32                                                          | —                                                                                          | Stock                                  |
| 248   | icon   | `IDI_SHELL_CAMERA`               | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 249   | icon   | `IDI_SHELL_SLIDE_SHOW`           | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 250   | icon   | `IDI_SHELL_DISPLAY`              | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Stock                                  |
| 251   | icon   | `IDI_SHELL_WEB_PICS`             | 48@32 32@32 16@32                                                   | —                                                                                          | Stock                                  |
| 252   | icon   | `IDI_SHELL_PRINT_PICS`           | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 253   | icon   | `IDI_SHELL_FILE_CHECK`           | 16@8 16@32                                                          | —                                                                                          | Stock                                  |
| 254   | icon   | `IDI_SHELL_EMPTY_RECYCLE_BIN3`   | 48@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                          | —                                                                                          | Stock                                  |
| 255   | icon   | `IDI_SHELL_ICON_255`             | 16@8 16@24 16@32                                                    | —                                                                                          | Stock                                  |
| 256   | icon   | `IDI_SHELL_FOLDER_MOVE2`         | 48@8 32@8 16@8 48@32 32@32 16@32                                    | shlfileop.cpp                                                                              | Stock                                  |
| 257   | icon   | `IDI_SHELL_NETWORK_CONNECTIONS2` | 48@4 32@4 24@4 16@4 48@8 32@8 24@8 16@8 48@32 32@32 24@32 16@32     | shellmenu/CStartMenu.cpp                                                                   | Afterglow (`netconn`)                  |
| 258   | icon   | `IDI_SHELL_NEW_NETWORK_FOLDER`   | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 259   | icon   | `IDI_SHELL_NETWORK_HOME`         | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 260   | icon   | `IDI_SHELL_CD_EDIT`              | 16@8 16@32                                                          | —                                                                                          | Stock                                  |
| 261   | icon   | `IDI_SHELL_CD_ERASE`             | 16@8 16@32                                                          | —                                                                                          | Stock                                  |
| 262   | icon   | `IDI_SHELL_CD_DELETE`            | 16@8 16@32                                                          | —                                                                                          | Stock                                  |
| 263   | icon   | `IDI_SHELL_HELP1`                | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 264   | icon   | `IDI_SHELL_FOLDER_POINT`         | 16@8 16@32                                                          | —                                                                                          | Stock                                  |
| 265   | icon   | `IDI_SHELL_SENDMAIL`             | 16@8 16@24 16@32                                                    | —                                                                                          | Stock                                  |
| 266   | icon   | `IDI_SHELL_CD_POINT`             | 16@8 16@32                                                          | —                                                                                          | Stock                                  |
| 267   | icon   | `IDI_SHELL_SHARED_FOLDER`        | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 268   | icon   | `IDI_SHELL_ACCESSIBILITY`        | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 269   | icon   | `IDI_SHELL_USERS`                | 48@8 32@8 16@8 48@24 32@24 16@8 48@32 32@32 16@32                   | —                                                                                          | Stock                                  |
| 270   | icon   | `IDI_SHELL_SCREEN_COLORS`        | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 271   | icon   | `IDI_SHELL_ADD_REM_PROGRAMS`     | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 272   | icon   | `IDI_SHELL_PRINTER_MOUSE`        | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 273   | icon   | `IDI_SHELL_INTERNET_STATUS`      | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 274   | icon   | `IDI_SHELL_SYSTEM_GEAR`          | 48@8 32@8 16@8 48@32 32@32 16@32                                    | wine/shellpath.c                                                                           | Stock                                  |
| 275   | icon   | `IDI_SHELL_PIE_CHART`            | 48@8 48@32 32@8 32@32 16@8 16@32                                    | —                                                                                          | Stock                                  |
| 276   | icon   | `IDI_SHELL_INTERNET_DATE`        | 48@8 48@32 32@32 32@8 16@32 16@8                                    | —                                                                                          | Stock                                  |
| 277   | icon   | `IDI_SHELL_TUNES`                | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 278   | icon   | `IDI_SHELL_CMD`                  | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 279   | icon   | `IDI_SHELL_USER_ACCOUNTS`        | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 281   | icon   | `IDI_SHELL_WINDOWS_SEARCH`       | 16@8 32@8 48@8 16@32 32@32 48@32                                    | —                                                                                          | Stock                                  |
| 282   | icon   | `IDI_SHELL_COMPUTER_TEXT`        | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 283   | icon   | `IDI_SHELL_OSK`                  | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 284   | icon   | `IDI_SHELL_ICON_284`             | 16@8                                                                | —                                                                                          | Stock                                  |
| 289   | icon   | `IDI_SHELL_HELP_FILE`            | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 290   | icon   | `IDI_SHELL_GO`                   | 16@8 16@24 16@32                                                    | —                                                                                          | Stock                                  |
| 291   | icon   | `IDI_SHELL_DVD_DRIVE`            | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 292   | icon   | `IDI_SHELL_CD_ADD_MUSIC`         | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 293   | icon   | `IDI_SHELL_CD`                   | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 294   | icon   | `IDI_SHELL_CD_ROM`               | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 295   | icon   | `IDI_SHELL_CDR`                  | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 296   | icon   | `IDI_SHELL_CDRW`                 | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 297   | icon   | `IDI_SHELL_DVD_RAM`              | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 298   | icon   | `IDI_SHELL_DVDR_ROM`             | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 299   | icon   | `IDI_SHELL_MP3_PLAYER`           | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 300   | icon   | `IDI_SHELL_SERVER`               | 48@8 16@8 32@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 301   | icon   | `IDI_SHELL_SERVER1`              | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 302   | icon   | `IDI_SHELL_CD_ROM1`              | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 303   | icon   | `IDI_SHELL_COMPACT_FLASH`        | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4                     | —                                                                                          | Stock                                  |
| 304   | icon   | `IDI_SHELL_DVD_ROM1`             | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 305   | icon   | `IDI_SHELL_FDD2`                 | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 307   | icon   | `IDI_SHELL_SD_MMC`               | 48@32 48@8 32@32 32@8 16@32 16@8                                    | —                                                                                          | Stock                                  |
| 308   | icon   | `IDI_SHELL_SMART_MEDIA`          | 48@8 32@8 16@8 48@24 32@24 16@8 48@32 32@32 16@32                   | —                                                                                          | Stock                                  |
| 309   | icon   | `IDI_SHELL_CAMERA1`              | 48@8 32@8 16@8 48@24 32@24 16@8 48@32 32@32 16@32                   | —                                                                                          | Stock                                  |
| 310   | icon   | `IDI_SHELL_PHONE`                | 48@8 32@8 24@8 16@8 48@32 32@32 24@32 16@32                         | —                                                                                          | Stock                                  |
| 311   | icon   | `IDI_SHELL_WEB_PRINTER`          | 48@8 32@8 24@8 16@8 48@32 32@32 24@32 16@32                         | —                                                                                          | Stock                                  |
| 312   | icon   | `IDI_SHELL_JAZ_DRIVE`            | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 313   | icon   | `IDI_SHELL_ZIP_DRIVE`            | 16@8 32@8 48@8 16@32 32@32 48@32                                    | —                                                                                          | Stock                                  |
| 314   | icon   | `IDI_SHELL_PDA`                  | 48@32 48@8 32@32 32@8 24@32 24@8 16@32 16@8                         | —                                                                                          | Stock                                  |
| 315   | icon   | `IDI_SHELL_SCANNER`              | 48@8 32@8 16@8 48@24 32@24 16@8 48@32 32@32 16@32                   | —                                                                                          | Stock                                  |
| 316   | icon   | `IDI_SHELL_IMAGING_DEVICES`      | 48@32 48@8 32@32 32@8 16@32 16@8                                    | —                                                                                          | Stock                                  |
| 317   | icon   | `IDI_SHELL_CAMCORDER`            | 48@8 32@8 16@8 48@24 32@8 16@8 48@32 32@32 16@32                    | —                                                                                          | Stock                                  |
| 318   | icon   | `IDI_SHELL_DVDRW_ROM`            | 48@8 32@8 16@8 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 319   | icon   | `IDI_SHELL_NEW_FOLDER`           | 48@8 32@8 16@8 48@24 32@24 16@8 48@32 32@32 16@32                   | —                                                                                          | Stock                                  |
| 320   | icon   | `IDI_SHELL_CD_POINT1`            | 16@8 16@32                                                          | —                                                                                          | Stock                                  |
| 321   | icon   | `IDI_SHELL_CONTROL_PANEL4`       | 48@8 32@8 16@4 48@32 32@32 16@32                                    | —                                                                                          | Stock                                  |
| 322   | icon   | `IDI_SHELL_FAVOTITES`            | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4                     | shellmenu/CStartMenu.cpp                                                                   | Afterglow (`favorites`)                |
| 323   | icon   | `IDI_SHELL_SEARCH1`              | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4                     | shellmenu/CStartMenu.cpp                                                                   | Afterglow (`search`)                   |
| 324   | icon   | `IDI_SHELL_HELP2`                | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4                     | shellmenu/CStartMenu.cpp                                                                   | Afterglow (`help`)                     |
| 325   | icon   | `IDI_SHELL_LOGOFF1`              | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4                     | shellmenu/CStartMenu.cpp                                                                   | Afterglow (`logoff`)                   |
| 326   | icon   | `IDI_SHELL_PROGRAMS_FOLDER1`     | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4                     | shellmenu/CStartMenu.cpp                                                                   | Afterglow (`programs`)                 |
| 327   | icon   | `IDI_SHELL_RECENT_DOCUMENTS1`    | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4                     | shellmenu/CStartMenu.cpp                                                                   | Afterglow (`documents`)                |
| 328   | icon   | `IDI_SHELL_RUN1`                 | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4                     | shellmenu/CStartMenu.cpp                                                                   | Afterglow (`run`)                      |
| 329   | icon   | `IDI_SHELL_SHUTDOWN1`            | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4                     | shellmenu/CStartMenu.cpp                                                                   | Afterglow (`shutdown`)                 |
| 330   | icon   | `IDI_SHELL_CONTROL_PANEL1`       | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4                     | shellmenu/CStartMenu.cpp                                                                   | Afterglow (`settings`)                 |
| 331   | icon   | `IDI_SHELL_DISCONNECT`           | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4                     | —                                                                                          | Stock                                  |
| 337   | icon   | `IDI_SHELL_SEARCH_DIRECTORY`     | 16@8 32@8 48@8 16@32 32@32 48@32                                    | —                                                                                          | Stock                                  |
| 338   | icon   | `IDI_SHELL_DELETE_PERMANENTLY`   | 48@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                          | —                                                                                          | Stock                                  |
| 512   | icon   | `IDI_SHELL_WEB_BROWSER`          | 16@8 32@8 48@8 16@32 32@32 48@32                                    | —                                                                                          | Afterglow                              |
| 1001  | icon   | `IDI_SHELL_IDEA`                 | 48@32 32@32 16@32 48@8 32@8 16@8 48@4 32@4 16@4                     | dialogs/drive.cpp                                                                          | Stock                                  |
| 1002  | icon   | `IDI_SHELL_PRINTER_OK2`          | 16@8 16@32                                                          | —                                                                                          | Stock                                  |
| 1003  | icon   | `IDI_SHELL_SERVER_OK`            | 16@32 16@8                                                          | —                                                                                          | Stock                                  |
| 1004  | icon   | `IDI_SHELL_HELP_FILE1`           | 48@8 32@8 24@8 16@8 48@24 32@8 24@8 16@8 48@32 32@32 24@32 16@32    | —                                                                                          | Stock                                  |
| 1005  | icon   | `IDI_SHELL_FILE_MOVE1`           | 16@8 16@32                                                          | —                                                                                          | Stock                                  |
| 1006  | icon   | `IDI_SHELL_FILE_PRINT`           | 16@8 16@32                                                          | —                                                                                          | Stock                                  |
| 1007  | icon   | `IDI_SHELL_FILE_OK`              | 16@8 16@32                                                          | —                                                                                          | Stock                                  |
| 1008  | icon   | `IDI_SHELL_PRINT_PAUSE`          | 16@8 16@32                                                          | —                                                                                          | Stock                                  |
| 1009  | icon   | `IDI_SHELL_PRINT_PLAY`           | 16@8 16@32                                                          | —                                                                                          | Stock                                  |
| 1010  | icon   | `IDI_SHELL_PRINT_SHARE`          | 16@8 16@32                                                          | —                                                                                          | Stock                                  |
| 1011  | icon   | `IDI_SHELL_FAX2`                 | 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32                          | —                                                                                          | Stock                                  |
| 8240  | icon   | `IDI_SHELL_SHUTDOWN2`            | 48@8 32@8 16@8 48@8 32@8 16@8 48@32 32@32 16@32                     | —                                                                                          | Stock                                  |
| 16710 | icon   | `IDI_SHELL_DELETE1`              | 32@32 32@8                                                          | —                                                                                          | Stock                                  |
| 16715 | icon   | `IDI_SHELL_DELETE2`              | 32@32 32@8                                                          | —                                                                                          | Stock                                  |
| 16717 | icon   | `IDI_SHELL_DELETE3`              | 32@32 32@8                                                          | —                                                                                          | Stock                                  |
| 16718 | icon   | `IDI_SHELL_DELETE4`              | 32@32 32@8                                                          | —                                                                                          | Stock                                  |
| 16721 | icon   | `IDI_SHELL_DELETE5`              | 32@32 32@8                                                          | —                                                                                          | Stock                                  |
| 131   | bitmap | `IDB_REACTOS`                    | 413 × 72, 24-bit                                                    | wine/shell32_main.c                                                                        | **Stock, drawn here**: `about-banner`  |
| 138   | bitmap | `IDB_LINEBAR`                    | 413 × 5, 24-bit                                                     | wine/shell32_main.c                                                                        | **Stock, drawn here**: `about-bar`     |
| 204   | bitmap | `IDB_SHELL_IEXPLORE_LG`          | 384 × 24, 32-bit                                                    | —                                                                                          | Stock                                  |
| 205   | bitmap | `IDB_SHELL_IEXPLORE_LG_HOT`      | 384 × 24, 32-bit                                                    | —                                                                                          | Stock                                  |
| 206   | bitmap | `IDB_SHELL_IEXPLORE_SM`          | 256 × 16, 32-bit                                                    | —                                                                                          | Stock                                  |
| 207   | bitmap | `IDB_SHELL_IEXPLORE_SM_HOT`      | 256 × 16, 32-bit                                                    | —                                                                                          | Stock                                  |
| 225   | bitmap | `IDB_SHELL_EDIT_LG`              | 96 × 16, 32-bit                                                     | —                                                                                          | Stock                                  |
| 226   | bitmap | `IDB_SHELL_EDIT_LG_HOT`          | 96 × 16, 32-bit                                                     | —                                                                                          | Stock                                  |
| 227   | bitmap | `IDB_SHELL_EDIT_SM`              | 144 × 24, 32-bit                                                    | —                                                                                          | Stock                                  |
| 228   | bitmap | `IDB_SHELL_EDIT_SM_HOT`          | 144 × 24, 32-bit                                                    | —                                                                                          | Stock                                  |
| 500   | bitmap | `IDB_DLG_BG`                     | 312 × 198, 24-bit                                                   | IDD_LOG_OFF_FANCY                                                                          | **Stock, drawn here**: `shutdown-bg`   |
| 501   | bitmap | `IDB_REACTOS_FLAG`               | 48 × 40, 24-bit                                                     | IDD_LOG_OFF_FANCY                                                                          | **Stock, drawn here**: `shutdown-mark` |
| 502   | bitmap | `IDB_IMAGE_STRIP`                | 33 × 231, 24-bit                                                    | dialogs/dialogs.cpp                                                                        | **Stock, drawn here**: `logoff-strip`  |

### `system32/shellbtrfs.dll` (removed by the `base` trim)

| Id  | Type | Name | Frames or size                   | Shown by | Status  |
| --- | ---- | ---- | -------------------------------- | -------- | ------- |
| 101 | icon | —    | 16@32 32@32 64@32 128@32 13@3328 | —        | Trimmed |

### `system32/shimgvw.dll`

| Id  | Type   | Name | Frames or size                                                      | Shown by | Status              |
| --- | ------ | ---- | ------------------------------------------------------------------- | -------- | ------------------- |
| 1   | icon   | —    | 16@8 24@8 32@8 48@8 16@24 24@24 32@24 48@24 16@32 24@32 32@32 48@32 | —        | Afterglow (`image`) |
| 2   | icon   | —    | 48@8 32@8 24@8 16@8 48@32 32@32 24@32 16@32                         | —        | Afterglow (`image`) |
| 5   | icon   | —    | 48@8 32@8 24@8 16@8 48@32 32@32 24@32 16@32                         | —        | Afterglow (`image`) |
| 50  | bitmap | —    | 16 × 16, 24-bit                                                     | —        | Stock               |
| 51  | bitmap | —    | 16 × 16, 24-bit                                                     | —        | Stock               |
| 52  | bitmap | —    | 16 × 16, 24-bit                                                     | —        | Stock               |
| 53  | bitmap | —    | 16 × 16, 24-bit                                                     | —        | Stock               |
| 54  | bitmap | —    | 16 × 16, 24-bit                                                     | —        | Stock               |
| 55  | bitmap | —    | 16 × 16, 24-bit                                                     | —        | Stock               |
| 56  | bitmap | —    | 16 × 16, 24-bit                                                     | —        | Stock               |
| 57  | bitmap | —    | 16 × 16, 24-bit                                                     | —        | Stock               |
| 58  | bitmap | —    | 16 × 16, 24-bit                                                     | —        | Stock               |
| 59  | bitmap | —    | 16 × 16, 24-bit                                                     | —        | Stock               |
| 60  | bitmap | —    | 16 × 16, 24-bit                                                     | —        | Stock               |
| 61  | bitmap | —    | 16 × 16, 24-bit                                                     | —        | Stock               |
| 62  | bitmap | —    | 16 × 16, 24-bit                                                     | —        | Stock               |
| 63  | bitmap | —    | 16 × 16, 24-bit                                                     | —        | Stock               |
| 64  | bitmap | —    | 16 × 16, 24-bit                                                     | —        | Stock               |
| 65  | bitmap | —    | 16 × 16, 24-bit                                                     | —        | Stock               |

### `system32/sndrec32.exe` (removed by the `base` trim)

| Id  | Type   | Name | Frames or size                                    | Shown by | Status                    |
| --- | ------ | ---- | ------------------------------------------------- | -------- | ------------------------- |
| 107 | icon   | —    | 48@4 32@4 16@4 48@24 32@24 16@8 48@32 32@32 16@32 | —        | Trimmed (art: `sndrec32`) |
| 8   | bitmap | —    | 59 × 29, 32-bit                                   | —        | Trimmed                   |
| 133 | bitmap | —    | 59 × 29, 32-bit                                   | —        | Trimmed                   |
| 134 | bitmap | —    | 59 × 29, 32-bit                                   | —        | Trimmed                   |
| 135 | bitmap | —    | 59 × 29, 32-bit                                   | —        | Trimmed                   |
| 136 | bitmap | —    | 59 × 29, 32-bit                                   | —        | Trimmed                   |
| 137 | bitmap | —    | 59 × 29, 32-bit                                   | —        | Trimmed                   |
| 141 | bitmap | —    | 59 × 29, 32-bit                                   | —        | Trimmed                   |
| 142 | bitmap | —    | 59 × 29, 32-bit                                   | —        | Trimmed                   |
| 143 | bitmap | —    | 59 × 29, 32-bit                                   | —        | Trimmed                   |
| 144 | bitmap | —    | 59 × 29, 32-bit                                   | —        | Trimmed                   |

### `system32/sndvol32.exe`

| Id  | Type | Name                | Frames or size                                  | Shown by                           | Status                        |
| --- | ---- | ------------------- | ----------------------------------------------- | ---------------------------------- | ----------------------------- |
| 301 | icon | `IDI_MAINAPP`       | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | IDD_ADVANCED, sndvol32.c           | **Stock, art ready**: `sound` |
| 302 | icon | `IDI_SPEAKER_LEFT`  | 16@4 16@8 16@32                                 | IDD_NORMAL_LINE, IDD_NORMAL_MASTER | Stock                         |
| 303 | icon | `IDI_SPEAKER_RIGHT` | 16@4 16@8 16@32                                 | IDD_NORMAL_LINE, IDD_NORMAL_MASTER | Stock                         |

### `system32/sol.exe` (removed by the `base` trim)

| Id  | Type | Name | Frames or size                                  | Shown by | Status               |
| --- | ---- | ---- | ----------------------------------------------- | -------- | -------------------- |
| 100 | icon | —    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Trimmed (art: `sol`) |

### `system32/spider.exe` (removed by the `base` trim)

| Id  | Type | Name | Frames or size                                  | Shown by | Status                  |
| --- | ---- | ---- | ----------------------------------------------- | -------- | ----------------------- |
| 100 | icon | —    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Trimmed (art: `spider`) |

### `system32/ssstars.scr` (removed by the `base` trim)

| Id  | Type   | Name | Frames or size   | Shown by | Status  |
| --- | ------ | ---- | ---------------- | -------- | ------- |
| 101 | icon   | —    | 32@0             | —        | Trimmed |
| 102 | bitmap | —    | 420 × 148, 8-bit | —        | Trimmed |
| 103 | bitmap | —    | 128 × 128, 8-bit | —        | Trimmed |

### `system32/starfield.scr` (removed by the `base` trim)

| Id  | Type | Name | Frames or size    | Shown by | Status  |
| --- | ---- | ---- | ----------------- | -------- | ------- |
| 101 | icon | —    | 48@32 32@32 16@32 | —        | Trimmed |

### `system32/stobject.dll`

| Id  | Type | Name                        | Frames or size                   | Shown by    | Status                               |
| --- | ---- | --------------------------- | -------------------------------- | ----------- | ------------------------------------ |
| 200 | icon | `IDI_BATTERY`               | 48@32 48@8 32@32 32@8 16@32 16@8 | —           | **Stock, art ready**: `battery5`     |
| 210 | icon | `IDI_EXTRACT`               | 48@32 48@8 32@32 32@8 16@32 16@8 | —           | **Stock, art ready**: `hotplug`      |
| 230 | icon | `IDI_VOLUME`                | 48@32 48@8 32@32 32@8 16@32 16@8 | volume.cpp  | **Stock, art ready**: `volume`       |
| 231 | icon | `IDI_VOLMUTE`               | 48@32 48@8 32@32 32@8 16@32 16@8 | volume.cpp  | **Stock, art ready**: `volumemute`   |
| 400 | icon | `IDI_BATTCAP0`              | 32@8 32@32 16@8 16@32            | power.cpp   | **Stock, art ready**: `battery0`     |
| 401 | icon | `IDI_BATTCAP1`              | 32@8 32@32 16@8 16@32            | power.cpp   | **Stock, art ready**: `battery1`     |
| 402 | icon | `IDI_BATTCAP2`              | 32@8 32@32 16@8 16@32            | power.cpp   | **Stock, art ready**: `battery2`     |
| 403 | icon | `IDI_BATTCAP3`              | 32@8 32@32 16@8 16@32            | power.cpp   | **Stock, art ready**: `battery3`     |
| 404 | icon | `IDI_BATTCAP4`              | 32@8 32@32 16@8 16@32            | power.cpp   | **Stock, art ready**: `battery4`     |
| 405 | icon | `IDI_BATTCAP5`              | 32@8 32@32 16@8 16@32            | —           | **Stock, art ready**: `battery5`     |
| 406 | icon | `IDI_BATTCHA0`              | 16@8 16@32                       | power.cpp   | **Stock, art ready**: `charging0`    |
| 407 | icon | `IDI_BATTCHA1`              | 16@8 16@32                       | power.cpp   | **Stock, art ready**: `charging1`    |
| 408 | icon | `IDI_BATTCHA2`              | 16@8 16@32                       | power.cpp   | **Stock, art ready**: `charging2`    |
| 409 | icon | `IDI_BATTCHA3`              | 16@8 16@32                       | power.cpp   | **Stock, art ready**: `charging3`    |
| 410 | icon | `IDI_BATTCHA4`              | 16@8 16@32                       | power.cpp   | **Stock, art ready**: `charging4`    |
| 412 | icon | `IDI_BATTCAP_ERR`           | 32@8 16@8 32@32 16@32            | power.cpp   | **Stock, art ready**: `batteryerror` |
| 413 | icon | `IDI_POWER_AC`              | 32@8 16@8 32@32 16@32            | power.cpp   | **Stock, art ready**: `acpower`      |
| 420 | icon | `IDI_HOTPLUG_ERR`           | 16@8 16@32                       | —           | **Stock, art ready**: `hotplugerror` |
| 421 | icon | `IDI_HOTPLUG_OK`            | 16@8 16@32                       | hotplug.cpp | **Stock, art ready**: `hotplug`      |
| 440 | icon | `IDI_MOUSE_DISABLED`        | 16@8                             | mouse.cpp   | Stock                                |
| 441 | icon | `IDI_MOUSE_NOBTN`           | 16@8                             | mouse.cpp   | Stock                                |
| 442 | icon | `IDI_MOUSE_L_ACTIVE`        | 16@8                             | mouse.cpp   | Stock                                |
| 443 | icon | `IDI_MOUSE_L_DOWN`          | 16@8                             | mouse.cpp   | Stock                                |
| 444 | icon | `IDI_MOUSE_R_ACTIVE`        | 16@8                             | mouse.cpp   | Stock                                |
| 445 | icon | `IDI_MOUSE_R_DOWN`          | 16@8                             | mouse.cpp   | Stock                                |
| 446 | icon | `IDI_MOUSE_LR_ACTIVE`       | 16@8                             | mouse.cpp   | Stock                                |
| 447 | icon | `IDI_MOUSE_LR_DOWN`         | 16@8                             | mouse.cpp   | Stock                                |
| 448 | icon | `IDI_MOUSE_L_ACTIVE_R_DOWN` | 16@8                             | mouse.cpp   | Stock                                |
| 449 | icon | `IDI_MOUSE_R_ACTIVE_L_DOWN` | 16@8                             | mouse.cpp   | Stock                                |

### `system32/sysdm.cpl`

| Id   | Type   | Name            | Frames or size                                  | Shown by                                                                    | Status                             |
| ---- | ------ | --------------- | ----------------------------------------------- | --------------------------------------------------------------------------- | ---------------------------------- |
| 50   | icon   | `IDI_CPLSYSTEM` | 48@8 32@8 16@8 48@32 32@32 16@32                | sysdm.c                                                                     | Afterglow (`system`)               |
| 51   | icon   | `IDI_DEVMGR`    | 32@32                                           | IDD_PROPPAGEHARDWARE                                                        | **Stock, drawn here**: `devmgmt`   |
| 52   | icon   | `IDI_HARDPROF`  | 32@32                                           | IDD_HARDWAREPROFILE, IDD_HARDWAREPROFILES, IDD_PROPPAGEHARDWARE, hardprof.c | **Stock, drawn here**: `hwprofile` |
| 53   | icon   | `IDI_USERPROF`  | 32@8 32@24 32@32                                | IDD_USERPROFILE                                                             | **Stock, drawn here**: `usrmgr`    |
| 54   | icon   | `IDI_LICENSE`   | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | licence.c                                                                   | Stock                              |
| 2500 | icon   | `IDI_UP`        | 32@4                                            | hardprof.c                                                                  | Stock                              |
| 2501 | icon   | `IDI_DOWN`      | 32@4                                            | hardprof.c                                                                  | Stock                              |
| 2502 | icon   | `IDI_ADDHW`     | 32@32                                           | IDD_PROPPAGEHARDWARE                                                        | **Stock, drawn here**: `addhw`     |
| 55   | bitmap | `IDB_ROSBMP`    | 320 × 159, 24-bit                               | general.c                                                                   | Stock                              |
| 56   | bitmap | `IDB_ROSMASK`   | 320 × 159, 8-bit                                | general.c                                                                   | Stock                              |

### `system32/syssetup.dll`

| Id  | Type   | Name            | Frames or size                    | Shown by                        | Status |
| --- | ------ | --------------- | --------------------------------- | ------------------------------- | ------ |
| 10  | icon   | `IDI_ICON1`     | 48@8 32@8 48@24 32@24 48@32 32@32 | IDD_COMPUTERPAGE                | Stock  |
| 11  | icon   | `IDI_ICON2`     | 48@8 32@8 48@24 32@24 48@32 32@32 | IDD_OWNERPAGE                   | Stock  |
| 12  | icon   | `IDI_ICON3`     | 48@8 32@8 48@24 32@24 48@32 32@32 | IDD_DATETIMEPAGE                | Stock  |
| 13  | icon   | `IDI_ICON4`     | 48@8 32@8 48@24 32@24 48@32 32@32 | IDD_LOCALEPAGE                  | Stock  |
| 14  | icon   | `IDI_ICON5`     | 48@8 32@8 48@24 32@24 48@32 32@32 | IDD_COMPUTERPAGE                | Stock  |
| 15  | icon   | `IDI_CHECKICON` | 16@4                              | wizard.c                        | Stock  |
| 16  | icon   | `IDI_ARROWICON` | 16@4                              | wizard.c                        | Stock  |
| 17  | icon   | `IDI_CROSSICON` | 16@4                              | wizard.c                        | Stock  |
| 100 | bitmap | `IDB_WATERMARK` | 164 × 400, 8-bit                  | wizard.c                        | Stock  |
| 101 | bitmap | `IDB_HEADER`    | 49 × 49, 24-bit                   | wizard.c                        | Stock  |
| 102 | bitmap | `IDB_CLASSIC`   | 180 × 163, 24-bit                 | wizard.c                        | Stock  |
| 103 | bitmap | `IDB_LAUTUS`    | 180 × 163, 24-bit                 | wizard.c                        | Stock  |
| 104 | bitmap | `IDB_LUNAR`     | 180 × 163, 24-bit                 | wizard.c                        | Stock  |
| 105 | bitmap | `IDB_MIZU`      | 180 × 163, 24-bit                 | wizard.c                        | Stock  |
| 106 | bitmap | `IDB_REACTOS`   | 413 × 72, 24-bit                  | IDD_STATUSWINDOW_DLG, install.c | Stock  |
| 107 | bitmap | `IDB_LINE`      | 413 × 5, 24-bit                   | install.c                       | Stock  |

### `system32/tapiui.dll`

| Id  | Type   | Name | Frames or size                                     | Shown by | Status |
| --- | ------ | ---- | -------------------------------------------------- | -------- | ------ |
| 201 | icon   | —    | 16@8 32@8 48@8 16@24 32@24 48@24 16@32 32@32 48@32 | —        | Stock  |
| 202 | icon   | —    | 32@8 32@24 32@32                                   | —        | Stock  |
| 203 | icon   | —    | 32@8 32@24 32@32                                   | —        | Stock  |
| 504 | icon   | —    | 32@8 32@24 32@32                                   | —        | Stock  |
| 301 | bitmap | —    | 32 × 16, 4-bit                                     | —        | Stock  |
| 302 | bitmap | —    | 132 × 252, 8-bit, compressed                       | —        | Stock  |

### `system32/taskmgr.exe`

| Id  | Type   | Name              | Frames or size                                  | Shown by                  | Status                          |
| --- | ------ | ----------------- | ----------------------------------------------- | ------------------------- | ------------------------------- |
| 136 | icon   | `IDI_TASKMANAGER` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | about.c, run.c, taskmgr.c | **Stock, art ready**: `taskmgr` |
| 137 | icon   | `IDI_WINDOW`      | 32@32                                           | applpage.c                | Stock                           |
| 138 | icon   | `IDI_WINDOWSM`    | 16@32                                           | applpage.c                | Stock                           |
| 150 | bitmap | `IDB_TRAYMASK`    | 16 × 16, 4-bit                                  | trayicon.c                | Stock                           |
| 153 | bitmap | `IDB_TRAYICON`    | 16 × 16, 4-bit                                  | trayicon.c                | Stock                           |

### `system32/telephon.cpl` (removed by the `base` trim)

| Id  | Type | Name | Frames or size       | Shown by | Status                    |
| --- | ---- | ---- | -------------------- | -------- | ------------------------- |
| 100 | icon | —    | 32@8 16@8 32@32 16@8 | —        | Trimmed (art: `telephon`) |

### `system32/telnet.exe` (removed by the `base` trim)

| Id          | Type | Name | Frames or size                                  | Shown by | Status  |
| ----------- | ---- | ---- | ----------------------------------------------- | -------- | ------- |
| IDI_APPICON | icon | —    | 48@32 48@8 48@4 32@32 32@8 32@4 16@32 16@8 16@4 | —        | Trimmed |

### `system32/themeui.dll`

| Id  | Type | Name | Frames or size                  | Shown by | Status |
| --- | ---- | ---- | ------------------------------- | -------- | ------ |
| 1   | icon | —    | 16@8 32@8 48@8 16@8 32@32 48@32 | —        | Stock  |

### `system32/timedate.cpl`

| Id  | Type   | Name          | Frames or size                                  | Shown by   | Status                 |
| --- | ------ | ------------- | ----------------------------------------------- | ---------- | ---------------------- |
| 1   | icon   | `IDC_CPLICON` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | timedate.c | Afterglow (`datetime`) |
| 115 | bitmap | `IDC_WORLD`   | 360 × 180, 24-bit                               | timezone.c | Stock                  |

### `system32/url.dll`

| Id  | Type | Name | Frames or size                   | Shown by | Status |
| --- | ---- | ---- | -------------------------------- | -------- | ------ |
| 102 | icon | —    | 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Stock  |

### `system32/user32.dll`

| Id    | Type   | Name  | Frames or size                                  | Shown by                                                                                   | Status                           |
| ----- | ------ | ----- | ----------------------------------------------- | ------------------------------------------------------------------------------------------ | -------------------------------- |
| 100   | icon   | `100` | 32@8 16@8 32@32 16@32                           | controls/appswitch.c, controls/edit.c, SELWINDOW, misc/stubs.c, windows/cursoricon.c, wind | **Stock, art ready**: `program`  |
| 101   | icon   | `101` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —                                                                                          | **Stock, art ready**: `warning`  |
| 102   | icon   | `102` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —                                                                                          | **Stock, art ready**: `question` |
| 103   | icon   | `103` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | windows/cursoricon.c                                                                       | **Stock, art ready**: `error`    |
| 104   | icon   | `104` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —                                                                                          | **Stock, art ready**: `info`     |
| 105   | icon   | `105` | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —                                                                                          | Stock                            |
| 32732 | bitmap | —     | 14 × 14, 4-bit                                  | —                                                                                          | Stock                            |
| 32734 | bitmap | —     | 17 × 17, 4-bit                                  | —                                                                                          | Stock                            |
| 32735 | bitmap | —     | 17 × 17, 4-bit                                  | —                                                                                          | Stock                            |
| 32736 | bitmap | —     | 17 × 17, 4-bit                                  | —                                                                                          | Stock                            |
| 32737 | bitmap | —     | 17 × 17, 4-bit                                  | —                                                                                          | Stock                            |
| 32738 | bitmap | —     | 7 × 9, 1-bit                                    | —                                                                                          | Stock                            |
| 32739 | bitmap | —     | 6 × 9, 1-bit                                    | —                                                                                          | Stock                            |
| 32740 | bitmap | —     | 17 × 17, 4-bit                                  | —                                                                                          | Stock                            |
| 32741 | bitmap | —     | 17 × 17, 4-bit                                  | —                                                                                          | Stock                            |
| 32742 | bitmap | —     | 17 × 17, 4-bit                                  | —                                                                                          | Stock                            |
| 32743 | bitmap | —     | 17 × 17, 4-bit                                  | —                                                                                          | Stock                            |
| 32744 | bitmap | —     | 16 × 14, 4-bit                                  | —                                                                                          | Stock                            |
| 32745 | bitmap | —     | 16 × 14, 4-bit                                  | —                                                                                          | Stock                            |
| 32746 | bitmap | —     | 16 × 14, 4-bit                                  | —                                                                                          | Stock                            |
| 32747 | bitmap | —     | 16 × 14, 4-bit                                  | —                                                                                          | Stock                            |
| 32748 | bitmap | —     | 16 × 14, 4-bit                                  | —                                                                                          | Stock                            |
| 32749 | bitmap | —     | 16 × 14, 4-bit                                  | —                                                                                          | Stock                            |
| 32750 | bitmap | —     | 17 × 17, 4-bit                                  | —                                                                                          | Stock                            |
| 32751 | bitmap | —     | 17 × 17, 4-bit                                  | —                                                                                          | Stock                            |
| 32752 | bitmap | —     | 17 × 17, 4-bit                                  | —                                                                                          | Stock                            |
| 32753 | bitmap | —     | 17 × 17, 4-bit                                  | —                                                                                          | Stock                            |
| 32754 | bitmap | —     | 16 × 14, 4-bit                                  | —                                                                                          | Stock                            |
| 32755 | bitmap | —     | 25 × 19, 1-bit                                  | —                                                                                          | Stock                            |
| 32756 | bitmap | —     | 25 × 19, 1-bit                                  | —                                                                                          | Stock                            |
| 32757 | bitmap | —     | 25 × 19, 1-bit                                  | —                                                                                          | Stock                            |
| 32758 | bitmap | —     | 14 × 14, 1-bit                                  | —                                                                                          | Stock                            |
| 32759 | bitmap | —     | 56 × 39, 1-bit                                  | —                                                                                          | Stock                            |
| 32760 | bitmap | —     | 14 × 14, 1-bit                                  | —                                                                                          | Stock                            |
| 32761 | bitmap | —     | 15 × 15, 1-bit                                  | —                                                                                          | Stock                            |
| 32762 | bitmap | —     | 15 × 15, 1-bit                                  | —                                                                                          | Stock                            |
| 32763 | bitmap | —     | 15 × 15, 1-bit                                  | —                                                                                          | Stock                            |
| 32764 | bitmap | —     | 15 × 15, 1-bit                                  | —                                                                                          | Stock                            |
| 32765 | bitmap | —     | 15 × 15, 1-bit                                  | —                                                                                          | Stock                            |
| 32766 | bitmap | —     | 13 × 13, 1-bit                                  | —                                                                                          | Stock                            |
| 32767 | bitmap | —     | 36 × 18, 4-bit                                  | —                                                                                          | Stock                            |

### `system32/userenv.dll`

| Id  | Type | Name | Frames or size                   | Shown by | Status |
| --- | ---- | ---- | -------------------------------- | -------- | ------ |
| 1   | icon | —    | 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Stock  |

### `system32/userinit.exe`

| Id  | Type   | Name | Frames or size    | Shown by | Status |
| --- | ------ | ---- | ----------------- | -------- | ------ |
| 100 | bitmap | —    | 320 × 159, 24-bit | —        | Stock  |
| 101 | bitmap | —    | 320 × 159, 8-bit  | —        | Stock  |

### `system32/usrmgr.cpl` (removed by the `base` trim)

| Id  | Type | Name | Frames or size                   | Shown by | Status                  |
| --- | ---- | ---- | -------------------------------- | -------- | ----------------------- |
| 40  | icon | —    | 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Trimmed (art: `usrmgr`) |
| 41  | icon | —    | 16@8 16@32                       | —        | Trimmed                 |
| 42  | icon | —    | 16@8 16@32                       | —        | Trimmed                 |
| 43  | icon | —    | 16@8 16@32                       | —        | Trimmed                 |
| 100 | icon | —    | 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Trimmed (art: `usrmgr`) |

### `system32/utilman.exe`

| Id  | Type | Name               | Frames or size | Shown by | Status                          |
| --- | ---- | ------------------ | -------------- | -------- | ------------------------------- |
| 30  | icon | `IDI_ICON_UTILMAN` | 32@32          | —        | **Stock, art ready**: `utilman` |

### `system32/vfd.dll`

| Id  | Type | Name | Frames or size | Shown by | Status |
| --- | ---- | ---- | -------------- | -------- | ------ |
| 104 | icon | —    | 32@4 16@4      | —        | Stock  |
| 105 | icon | —    | 32@4 16@4      | —        | Stock  |
| 106 | icon | —    | 32@4 16@4      | —        | Stock  |

### `system32/vgafontedit.exe` (removed by the `base` trim)

| Id  | Type   | Name | Frames or size | Shown by | Status  |
| --- | ------ | ---- | -------------- | -------- | ------- |
| 100 | icon   | —    | 48@4 32@4 16@4 | —        | Trimmed |
| 101 | icon   | —    | 16@4           | —        | Trimmed |
| 401 | bitmap | —    | 16 × 16, 4-bit | —        | Trimmed |
| 402 | bitmap | —    | 24 × 24, 4-bit | —        | Trimmed |

### `ReactOS/welcome.exe`

| Id   | Type   | Name               | Frames or size                                  | Shown by  | Status |
| ---- | ------ | ------------------ | ----------------------------------------------- | --------- | ------ |
| 3000 | icon   | `IDI_MAIN`         | 16@8 32@8 48@8 16@4 32@4 48@4 16@32 32@32 48@32 | welcome.c | Stock  |
| 101  | bitmap | `IDB_TITLE_BITMAP` | 558 × 79, 24-bit                                | welcome.c | Stock  |

### `system32/wined3dcfg.cpl` (removed by the `base` trim)

| Id  | Type | Name | Frames or size                   | Shown by | Status  |
| --- | ---- | ---- | -------------------------------- | -------- | ------- |
| 1   | icon | —    | 16@8 32@8 48@8 16@32 32@32 48@32 | —        | Trimmed |

### `ReactOS/winhlp32.exe`

| Id   | Type | Name          | Frames or size                                  | Shown by           | Status                       |
| ---- | ---- | ------------- | ----------------------------------------------- | ------------------ | ---------------------------- |
| 3840 | icon | `IDI_WINHELP` | 16@4 16@8 16@32 32@4 32@8 48@4 48@8 48@32 32@32 | macro.c, winhelp.c | **Stock, art ready**: `help` |

### `system32/winlogon.exe`

| Id  | Type | Name           | Frames or size                  | Shown by             | Status |
| --- | ---- | -------------- | ------------------------------- | -------------------- | ------ |
| 4   | icon | `IDI_WINLOGON` | 32@32 32@8 32@4 16@32 16@8 16@4 | IDD_SHUTDOWNCOMPUTER | Stock  |

### `system32/winmine.exe` (removed by the `base` trim)

| Id  | Type   | Name | Frames or size                                  | Shown by | Status                   |
| --- | ------ | ---- | ----------------------------------------------- | -------- | ------------------------ |
| 1   | icon   | —    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Trimmed (art: `winmine`) |
| 2   | bitmap | —    | 24 × 120, 4-bit                                 | —        | Trimmed                  |
| 3   | bitmap | —    | 13 × 276, 4-bit                                 | —        | Trimmed                  |
| 4   | bitmap | —    | 16 × 256, 4-bit                                 | —        | Trimmed                  |

### `system32/winsrv.dll`

| Id  | Type | Name | Frames or size                                  | Shown by | Status |
| --- | ---- | ---- | ----------------------------------------------- | -------- | ------ |
| 1   | icon | —    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Stock  |

### `system32/wordpad.exe` (removed by the `base` trim)

| Id  | Type   | Name            | Frames or size                                  | Shown by  | Status                   |
| --- | ------ | --------------- | ----------------------------------------------- | --------- | ------------------------ |
| 102 | icon   | `IDI_WORDPAD`   | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | wordpad.c | Trimmed (art: `wordpad`) |
| 103 | icon   | `IDI_RTFDOC`    | 48@8 32@8 16@8 48@32 32@32 16@32                | —         | Trimmed (art: `rtf`)     |
| 100 | bitmap | `IDB_TOOLBAR`   | 16 × 16, 4-bit                                  | wordpad.c | Trimmed                  |
| 101 | bitmap | `IDB_FORMATBAR` | 128 × 16, 4-bit                                 | wordpad.c | Trimmed                  |

### `system32/write.exe` (removed by the `base` trim)

| Id  | Type | Name | Frames or size                                  | Shown by | Status                   |
| --- | ---- | ---- | ----------------------------------------------- | -------- | ------------------------ |
| 1   | icon | —    | 48@4 32@4 16@4 48@8 32@8 16@8 48@32 32@32 16@32 | —        | Trimmed (art: `wordpad`) |

### `system32/wusa.exe`

| Id  | Type | Name       | Frames or size                   | Shown by | Status                       |
| --- | ---- | ---------- | -------------------------------- | -------- | ---------------------------- |
| 101 | icon | `IDI_WUSA` | 48@8 32@8 16@8 48@32 32@32 16@32 | —        | **Stock, art ready**: `wusa` |

### `system32/zipfldr.dll`

| Id  | Type   | Name            | Frames or size                    | Shown by                                      | Status |
| --- | ------ | --------------- | --------------------------------- | --------------------------------------------- | ------ |
| 1   | icon   | `IDI_ZIPFLDR`   | 48@24 32@8 16@8 48@32 32@32 16@32 | CZipExtract.cpp                               | Stock  |
| 164 | bitmap | `IDB_ZIPFLDR`   | 117 × 225, 24-bit                 | IDD_PROPPAGECOMPLETE, IDD_PROPPAGEDESTINATION | Stock  |
| 200 | bitmap | `IDB_HEADER`    | 49 × 49, 24-bit                   | CZipExtract.cpp                               | Stock  |
| 201 | bitmap | `IDB_WATERMARK` | 164 × 628, 24-bit                 | CZipExtract.cpp                               | Stock  |
