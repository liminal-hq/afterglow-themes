// Parse JSON with comments and trailing commas, the format VS Code theme files use
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT

export const parseJsonc = (text) => {
	let out = '';
	let inString = false;
	for (let i = 0; i < text.length; i++) {
		const c = text[i];
		if (inString) {
			out += c;
			if (c === '\\') out += text[++i];
			else if (c === '"') inString = false;
		} else if (c === '"') {
			inString = true;
			out += c;
		} else if (c === '/' && text[i + 1] === '/') {
			while (i < text.length && text[i] !== '\n') i++;
			out += '\n';
		} else if (c === '/' && text[i + 1] === '*') {
			i += 2;
			while (i < text.length && !(text[i] === '*' && text[i + 1] === '/')) i++;
			i++;
		} else {
			out += c;
		}
	}
	return JSON.parse(out.replace(/,(\s*[}\]])/g, '$1'));
};
