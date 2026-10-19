// Copy the Afterglow Forgejo themes, and optionally the instance avatar, into a Forgejo custom directory
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import {
	copyFileSync,
	existsSync,
	mkdirSync,
	readFileSync,
	readdirSync,
	writeFileSync,
} from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { avatarTemplate, TEMPLATE_MARKER } from './build-forgejo.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

// `--custom <dir>` is Forgejo's custom path (`GITEA_CUSTOM`, `/data/gitea` in the container image).
// `--signing-email <address>` is the instance's `[repository.signing]` SIGNING_EMAIL, and also installs the avatar.
const argument = (name) => {
	const at = process.argv.indexOf(`--${name}`);
	return at === -1 ? undefined : process.argv[at + 1];
};

const custom = argument('custom') ?? process.env.FORGEJO_CUSTOM;
const email = argument('signing-email') ?? process.env.FORGEJO_SIGNING_EMAIL;

if (!custom) {
	console.error('Pass the Forgejo custom directory with --custom <dir> (or set FORGEJO_CUSTOM).');
	process.exit(1);
}

const css = join(custom, 'public', 'assets', 'css');
mkdirSync(css, { recursive: true });
const themes = join(root, 'forgejo', 'themes');
for (const file of readdirSync(themes).filter((f) => f.endsWith('.css'))) {
	copyFileSync(join(themes, file), join(css, file));
	console.log(`installed ${join(css, file)}`);
}

if (email) {
	const img = join(custom, 'public', 'assets', 'img');
	mkdirSync(img, { recursive: true });
	copyFileSync(
		join(root, 'forgejo', 'avatar', 'forgejo-instance.svg'),
		join(img, 'forgejo-instance.svg'),
	);
	console.log(`installed ${join(img, 'forgejo-instance.svg')}`);

	// Forgejo reads this template for every page, so never replace one that is not ours
	const templates = join(custom, 'templates', 'custom');
	const target = join(templates, 'extra_links.tmpl');
	if (existsSync(target) && !readFileSync(target, 'utf8').includes(TEMPLATE_MARKER)) {
		console.error(`${target} exists and was not written by Afterglow, so it was left alone.`);
		process.exit(1);
	}
	mkdirSync(templates, { recursive: true });
	writeFileSync(target, avatarTemplate(email));
	console.log(`installed ${target}`);
}

console.log(
	'Add the themes to [ui] THEMES in app.ini (see docs/forgejo-theme.md) and restart Forgejo.',
);
