# Firefox, Chrome and Edge themes

Afterglow ships three browser themes for Firefox and three for Chrome and Edge, generated from the same palette as the other targets. Both browsers colour only their own chrome (the tab strip, toolbar, address bar, menus and new tab page), not the web pages inside it.

| Theme             | Firefox id                     | What it is                                         |
| ----------------- | ------------------------------ | -------------------------------------------------- |
| `Afterglow`       | `afterglow@liminalhq.ca`       | The `#050507` void, with the orange accent         |
| `Afterglow Dark`  | `afterglow-dark@liminalhq.ca`  | Solid deep indigo-black, with the purple accent    |
| `Afterglow Light` | `afterglow-light@liminalhq.ca` | Warm paper, with deeper accents that hold contrast |

## Roles

`scripts/browser-roles.mjs` maps the shared ramps onto the roles both browsers need, so the two generators cannot drift apart. Step meanings match the other themes: neutral 900 is the surface, 800 a raised surface, 200 body text, 400 muted text and a hue's step 200 its main colour.

| Role                                     | Colour                                                                                       |
| ---------------------------------------- | -------------------------------------------------------------------------------------------- |
| Frame and inactive tabs                  | Neutral 900. An inactive window uses 800.                                                    |
| Toolbar and the selected tab             | Neutral 800, so the active tab reads as one piece with the bar under it.                     |
| Address bar                              | Neutral 900 with a 600 border. Focus uses the interactive hue and the strongest text colour. |
| Text, muted text and icons               | Neutral 200, 400 and 300.                                                                    |
| Selected tab line, loading and attention | The variant's accent (orange for `afterglow`, purple for the others).                        |
| Menus, panels and the sidebar            | Neutral 800 with a 600 border, and the interactive hue at 600 behind a highlighted row.      |
| New tab page                             | Neutral 900 with 800 cards. Links use the interactive hue.                                   |

## Firefox

`scripts/build-firefox.mjs` writes `firefox/themes/<id>/manifest.json`, a WebExtension theme with all 38 colour keys from the [MDN theme reference](https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/theme), listed in `scripts/firefox-theme-keys.json`. Each variant is its own add-on, with a fixed `browser_specific_settings.gecko.id`, and sets `color_scheme` to `dark` or `light` so Firefox's own UI follows. The release carries one `.xpi` per theme, which is the manifest zipped at the root.

Firefox only installs signed add-ons permanently, and Afterglow's `.xpi` files are unsigned. Without signing, a theme can be loaded in two ways:

- **Temporarily, in any Firefox:** open `about:debugging#/runtime/this-firefox`, choose **Load Temporary Add-on** and pick a theme's `manifest.json` (from `firefox/themes/<id>/` in a checkout). It lasts until Firefox restarts.
- **Permanently, in Firefox Developer Edition, Nightly or ESR:** set `xpinstall.signatures.required` to `false` in `about:config`, then install the `.xpi` from `about:addons`.

Publishing to addons.mozilla.org, or signing for self-distribution there, is a separate manual step.

## Chrome and Edge

`scripts/build-chromium.mjs` writes `chromium/themes/<id>/manifest.json`, a Manifest V3 theme. Chrome and Edge read the same file. Colours are `[r, g, b]` arrays, and the 16 keys come from `kOverwritableColorTable` in Chromium's `browser_theme_pack.cc`, listed in `scripts/chromium-theme-keys.json`. The release carries `afterglow-chromium-themes-vX.Y.Z.zip`, holding one folder per theme.

To load one, unzip the release, open `chrome://extensions` (or `edge://extensions`), turn on **Developer mode**, choose **Load unpacked** and pick a theme folder. Chrome shows a theme as a theme and offers **Reset to default**. Installing from the Chrome Web Store or Edge Add-ons needs icons, screenshots and a store listing, which the repository does not carry yet.

## Limits

- **No transparency.** Neither browser paints its chrome over the desktop, so `afterglow` is an opaque void.
- **Page content is untouched.** Web pages keep their own colours. `color_scheme: dark` makes Firefox report a dark preference to pages that honour it, and Chrome and Edge have no equivalent in a theme.
- **Chromium has no menu colours.** Menus, the address bar's dropdown and the settings pages follow the operating system's appearance, so only the frame, tabs, toolbar, address bar and new tab page take Afterglow.
- **Chromium's accent is not themable.** The address bar's focus ring, the text selection and buttons such as the one on the "installed theme" bar use Chromium's own baseline blue-purple. Colours come from the manifest's `colors` table, which has no accent key, and Chromium sets no seed colour for an extension theme, so it falls back to the baseline palette. The accent that Chrome's own **Customize Chrome** colour picker sets belongs to the profile, not to a theme, and a theme cannot ship it.

## How it is built and validated

`scripts/validate-firefox.mjs` and `scripts/validate-chromium.mjs` check:

- the manifest version, name, version (which must match `package.json`) and, for Firefox, the id and colour scheme,
- every key in the list is set and none is unknown,
- every colour is `#rrggbb` (Firefox) or an integer `[r, g, b]` (Chromium),
- the committed file matches the generator,
- contrast: 4.5:1 for text on its surface, and 3:1 for icons and the selected-tab line.

The generated manifests carry the package version, so a release bump needs `bun run build` and the regenerated files committed.

## What was verified

- The key lists against the MDN reference and the Chromium source.
- The generators, validators and unit tests, and that the `.xpi` and zip packages contain the manifests at the expected paths.
