# Desktop release assets

Every release attaches two zips for the desktop, next to the editor and terminal themes, and lists both in `SHA256SUMS`.

## Wallpapers

`afterglow-wallpapers-vX.Y.Z.zip` holds the 20 SVG wallpapers from `assets/wallpapers/` (five palettes, dark and light, stepped and smooth) and the licence files. The PNG and BMP renders are not shipped; `bun run render:wallpapers` makes them from the SVGs. See [desktop-wallpapers.md](desktop-wallpapers.md).

## ReactOS desktop

`afterglow-reactos-desktop-vX.Y.Z.zip` unpacks into one `afterglow-reactos-desktop-vX.Y.Z/` folder:

- `style/afterglow.msstyles`, the default build with classic scroll bars
- `style-scrollbars/afterglow.msstyles`, the build with the Afterglow scroll bars. Both files have the same name because the style registry entries name `afterglow.msstyles`, so use one or the other
- `schemes/`, the eight colour schemes as `.reg` files and `apply-scheme.cmd`, and `install/afterglow-original.reg`, which selects the style and sets the caption metrics. See [reactos-desktop-colour-schemes.md](reactos-desktop-colour-schemes.md)
- `pointers/`, the 14 `.cur` and two `.ani` pointers, `afterglow-pointers.reg` and `patch-user32.py` with its hash list. The zip never carries a patched `user32.dll`: you patch your own copy. See [reactos-desktop-pointers.md](reactos-desktop-pointers.md)
- `SHA256SUMS` for the two styles, `README.md`, `PROVENANCE.md`, the two docs pages above and the licence files

## How the zips are built

`bun run bundle` builds both zips with the rest of the release. The ReactOS zip is drawn from source at bundle time, so the machine needs Python 3 with numpy and Pillow, `llvm-rc` and `lld-link`. Without them the bundle fails with a message naming what is missing. For a local run without those tools, set `AFTERGLOW_SKIP_REACTOS=1` to skip the ReactOS zip with a warning. CI and the release workflow never set it.

CI and the release workflow install the tools with the `.github/actions/desktop-tools` composite action: the `llvm`, `lld` and `clang` packages on `ubuntu-24.04` (`llvm-rc` runs `clang` as its preprocessor), and numpy 2.5.4 and Pillow 13.0.0 from pip. The `Desktop style` CI job runs `bun run check:desktop` with them on every pull request and push, and the release workflow runs the same check before it bundles.

## Reproducibility

The `afterglow.msstyles` bytes in `desktop/SHA256SUMS` came out identical with LLVM 18 (Ubuntu 24.04) and LLVM 23 (the development machine), so they do not depend on the `llvm-rc` or `lld-link` version in that range. The pointer hashes do depend on Pillow: they were recorded with 13.0.0, which is why CI pins it. If a newer Pillow or LLVM changes a hash, look at the output, then regenerate the sums and update the pin together.
