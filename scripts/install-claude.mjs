// Copy the generated Claude Code themes into the Claude Code themes directory
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

import { copyFileSync, mkdirSync, readdirSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const source = join(dirname(fileURLToPath(import.meta.url)), '..', 'claude', 'themes');
const config = process.env.CLAUDE_CONFIG_DIR || join(homedir(), '.claude');
const target = join(config, 'themes');

mkdirSync(target, { recursive: true });
for (const file of readdirSync(source).filter((f) => f.endsWith('.json'))) {
	copyFileSync(join(source, file), join(target, file));
	console.log(`installed ${join(target, file)}`);
}
