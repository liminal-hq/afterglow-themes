// Copy the generated Midnight Commander skins into the user's mc skins directory
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { copyFileSync, mkdirSync, readdirSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const source = join(dirname(fileURLToPath(import.meta.url)), '..', 'mc', 'skins');
const data = process.env.XDG_DATA_HOME || join(homedir(), '.local', 'share');
const target = join(data, 'mc', 'skins');

mkdirSync(target, { recursive: true });
for (const file of readdirSync(source).filter((f) => f.endsWith('.ini'))) {
	copyFileSync(join(source, file), join(target, file));
	console.log(`installed ${join(target, file)}`);
}
