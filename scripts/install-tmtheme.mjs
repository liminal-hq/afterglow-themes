// Copy the generated TextMate themes into the Codex CLI themes directory
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { copyFileSync, mkdirSync, readdirSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const source = join(dirname(fileURLToPath(import.meta.url)), '..', 'tmtheme');
const home = process.env.CODEX_HOME || join(homedir(), '.codex');
const target = join(home, 'themes');

mkdirSync(target, { recursive: true });
for (const file of readdirSync(source).filter((f) => f.endsWith('.tmTheme'))) {
	copyFileSync(join(source, file), join(target, file));
	console.log(`installed ${join(target, file)}`);
}
