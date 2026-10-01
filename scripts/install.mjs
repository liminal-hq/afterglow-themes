// Copy the generated themes into the global OpenCode themes directory
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { copyFileSync, mkdirSync, readdirSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const source = join(dirname(fileURLToPath(import.meta.url)), '..', 'themes');
const config = process.env.XDG_CONFIG_HOME ?? join(homedir(), '.config');
const target = join(config, 'opencode', 'themes');

mkdirSync(target, { recursive: true });
for (const file of readdirSync(source).filter((f) => f.endsWith('.json'))) {
	copyFileSync(join(source, file), join(target, file));
	console.log(`installed ${join(target, file)}`);
}
