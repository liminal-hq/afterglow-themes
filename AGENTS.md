# AGENTS.md

## Table of Contents

- [Project Status](#project-status)
- [Localization and Spelling](#localization-and-spelling)
- [Markdown Formatting](#markdown-formatting)
- [Authoring Voice](#authoring-voice)
- [Commit Messages](#commit-messages)
- [Pull Request Titles](#pull-request-titles)
- [Pull Request Content](#pull-request-content)
- [Pull Request Labels](#pull-request-labels)
- [Git Workflow](#git-workflow)
- [Local Tooling](#local-tooling)
- [Themes](#themes)
- [CI and Release](#ci-and-release)
- [Repository Layout](#repository-layout)
- [Licence and Copyright](#licence-and-copyright)

## Project Status

Afterglow is the Liminal HQ colour theme family for the OpenCode terminal UI. It ships three themes (`afterglow`, `afterglow-dark` and `afterglow-light`) for OpenCode, in the V2 theme format, the same three as a VS Code extension, as Midnight Commander skins, as Claude Code custom themes and as TextMate `.tmTheme` files for the Codex CLI, bat and delta, all generated from one palette. The repository is in **early development**.

## Localization and Spelling

**REQUIREMENT:** All code variables, comments, commit messages, pull request descriptions and documentation MUST use **Canadian English** spelling.

Examples: `colour` instead of `color`, `centre` instead of `center`, `behaviour` instead of `behavior`, `licence` (noun) instead of `license`.

Keep American spellings where an external format or API requires them, such as the `color-scheme` property or published topic names. OpenCode's own theme keys and identifiers are fixed by OpenCode.

## Markdown Formatting

**REQUIREMENT:** Do not hard-wrap markdown prose. Write each paragraph or bullet as a single unwrapped line in the source and let the renderer reflow it. This applies to PR descriptions, docs under `docs/`, README files and this file. Commit message bodies are the one exception: hard-wrap those at 100 columns.

## Authoring Voice

**Requirement:** Ship the result, not how the conversation arrived at it. Write every outward-facing line (code comments, workflow comments, docs, PR descriptions) as the author of the artifact, for the reader who will encounter it later, not as a record of the debugging or review process that produced it.

- Do not reference "this PR", "the review", a reviewer's name or a commit SHA inside comments or PR prose. State the fact or the reasoning directly.
- Commit messages are the exception: they are a legitimate place to record why a change happened. The `## Test plan` section of a PR description is a similar exception.

## Commit Messages

**Requirement:** Use Conventional Commits format (for example `feat: ...`, `fix: ...`, `docs: ...`, `test: ...`, `ci: ...`, `build: ...`, `chore: ...`).

- Use `feat:` or `fix:` for palette and theme changes, and `docs:` for documentation.
- Use `ci:` or `build:` when the primary change is workflow or tooling behaviour.
- Keep each commit focused on the specific unit of work completed in that commit.

Body requirements:

- Explain what changed and why. Keep subject and body lines under 100 characters.
- Use markdown where helpful: `code`, **bold** and flat bullets. Do not use markdown headings inside commit bodies.

Shell safety:

- Do not pass markdown-heavy commit bodies through `git commit -m "..."` when they contain backticks, `$()` or other shell-sensitive characters.
- Prefer writing the message to a file and committing with `git commit -F <file>`.
- Verify the stored commit message with `git log -1 --pretty=fuller` and amend immediately if shell interpolation altered it.

## Pull Request Titles

- Start with a capital letter.
- Do not use Conventional Commit prefixes in PR titles.
- Describe the outcome or behaviour change, not the implementation process.

## Pull Request Content

Use this default structure:

- `## Summary`
- optional `### Theme changes`
- optional `### Maintainer-facing changes`
- optional `### Workflow and infrastructure`
- optional `### Documentation`
- optional `### Known limitations`
- `## Test plan`

Under `## Summary`, use flat bullets with **bold** lead-ins. Under `## Test plan`, use checklist bullets (`- [x]` / `- [ ]`) with concrete commands. A colour change cannot be fully verified by the validator, so say plainly when a change has not been checked by eye in a real terminal, and include a screenshot when you have.

## Pull Request Labels

**Requirement:** Add labels to every PR when it is created or updated.

- Add at least one primary category label: `enhancement`, `bug`, `documentation`, `testing`, `ci`, `build` or `chore`.
- Add shared operational labels where they help: `infrastructure`, `internal`, `release`, `blocked` or `skip-changelog`.
- Add scope labels where helpful: `afterglow`, `dark` or `light` for a specific theme, `vscode` for the VS Code extension, `midnight-commander` for the mc skins, `claude-code` for the Claude Code themes, `codex` for the TextMate themes used by Codex, bat and delta, `palette`, `accessibility`, `transparency`, `opencode`, `tooling`, `developer-experience` or `security`.
- Prefer the broader Liminal HQ label style over Conventional Commit terms. Use `enhancement` and `bug`, not `feat` or `fix`.
- Use `skip-changelog` only when a change should be excluded from generated release notes (the categories are defined in `.github/release.yml`).

## Git Workflow

**Requirement:** Do not push changes (especially force pushes), push tags or dispatch workflows unless explicitly requested.

- **Default branch:** `main`. Work on a topic branch and open a PR; do not commit directly to `main` once the repository is established.
- **Branch naming:** `<type>/<short-description>`, where `<type>` matches the Conventional Commit type (for example `feat/softer-warning-gold`). Use `fix/issue-<number>-<short-description>` when a branch addresses a filed issue, and `chore/release-v<version>` for release prep.
- **GitHub tooling:** Prefer the `gh` CLI for repository, pull request, label, review and GitHub Actions work.

## Local Tooling

- **JS runtime and package manager:** **Bun** (not pnpm or npm), with the Node version pinned in `.node-version`. Installs use `--frozen-lockfile` in CI.
- **Formatting:** Prettier (`.prettierrc`: tabs, single quotes, 100 columns). `.editorconfig` is authoritative (tabs, LF, UTF-8). The generated `themes/`, `mc/skins/`, `claude/themes/` and `tmtheme/` directories are excluded from Prettier.
- **Validation gate:** `bun run validate` is the single local gate that mirrors CI and must pass before opening or updating a PR. It runs the format check, the licence-header check, Markdown lint, the theme build and the theme validator.
- **Release assets:** `bun run bundle` builds `dist/release` with the OpenCode theme files, a zip bundle, the VS Code `.vsix`, the Midnight Commander skins zip (`afterglow-mc-skins-vX.Y.Z.zip`), the Claude Code themes zip (`afterglow-claude-code-themes-vX.Y.Z.zip`), the TextMate themes zip (`afterglow-tmthemes-vX.Y.Z.zip`) and `SHA256SUMS`. `zip` must be installed.

## Themes

- **Edit the generator, not the JSON.** `themes/*.json` (OpenCode) and `vscode/themes/*.json` (VS Code) are generated by `scripts/build.mjs` and `scripts/build-vscode.mjs` from `scripts/palette.mjs`. Run `bun run build` and commit the regenerated files with the change. CI fails if the committed files drift from what the palette generates.
- **Stay within the V2 format.** `scripts/validate-themes.mjs` mirrors the schema bundled in OpenCode. Run `bun run validate:themes` after every palette or token change. Text, syntax and Markdown colours must keep 4.5:1 contrast.
- **Keep step meanings consistent.** The brand colour sits on step `200`, and each token uses the same step in all three themes (see `docs/theme-format.md`). Override a token in a single theme only when a trade-off needs it, and explain the trade-off in a comment.
- **Verify in a terminal.** The validator checks structure and contrast, not appearance. Check palette changes by eye in OpenCode, ideally over a transparent terminal for `afterglow`.
- **Target the V2 theme format only.** Do not add V1-format themes (`defs` and `theme` keys).
- **VS Code themes keep Dark+ and Light+ scope coverage.** `vscode/upstream/` holds unmodified copies of the upstream themes (with their MIT notice) and the generator recolours them by role. Do not edit those files. If a new literal has no role, map it in `scripts/build-vscode.mjs` rather than letting it through. `scripts/validate-vscode.mjs` checks every colour key against `scripts/vscode-colour-keys.json`, so refresh that list when VS Code adds keys. See `docs/vscode-theme.md`.
- **Midnight Commander skins are generated too.** `mc/skins/*.ini` come from `scripts/build-mc.mjs`, each variant as a truecolour skin and a `-256` fallback. `scripts/validate-mc.mjs` checks every section and key against `scripts/mc-skin-keys.json` (extracted from the skins shipped with mc), the colour syntax and contrast. Only `afterglow` may use the terminal `default` background. Refresh the key list when mc adds keys, and check changes in a real mc inside `tmux` with a scratch `XDG_DATA_HOME`, never your own mc config. See `docs/mc-skin.md`.
- **Claude Code themes are generated too.** `claude/themes/*.json` come from `scripts/build-claude.mjs` and set every token in `scripts/claude-theme-tokens.json`, which was extracted from the Claude Code binary. `scripts/validate-claude.mjs` checks the file schema (`name`, `base`, `overrides`), that no token is missing or unknown, the colour syntax and the contrast against the variant's neutral 900 surface (3:1 only for deliberately dim elements). Claude Code has no page background to make transparent, and the format is not versioned, so refresh the token list when it changes and check the themes load with a scratch `CLAUDE_CONFIG_DIR`, never your own `~/.claude`. See `docs/claude-code-theme.md`.
- **The TextMate themes derive from the VS Code themes.** `tmtheme/*.tmTheme` come from `scripts/build-tmtheme.mjs`, which converts the recoloured VS Code `tokenColors`, so change a syntax colour in `scripts/build-vscode.mjs` and never in the plist. Keep them standard TextMate (no Codex-only keys), and check changes with a scratch `CODEX_HOME` or bat config directory. `scripts/validate-tmtheme.mjs` parses the plist and checks the scopes and contrast. See `docs/tmtheme.md`.
- **Keep the version in two places in sync.** `package.json` and `vscode/package.json` must share a version. The validator fails otherwise.

## CI and Release

CI and release follow the Liminal HQ house pipeline.

- **Workflows** live in `.github/workflows/`: `ci.yml` (format, licence headers and theme checks on every PR and push to `main`), `ci-lint.yml` (actionlint and markdownlint on PRs), `security-audit.yml` (zizmor, non-blocking) and `release.yml` (tag-driven releases).
- **Generated-file drift is a CI failure.** CI rebuilds the themes and diffs them against the committed copy.
- **Licence headers** are enforced by `scripts/check-headers.sh`.
- **Releases** are tagged `vX.Y.Z` on `main`, and the tag must match the `version` in `package.json`. To release: bump `version` on a `chore/release-v<version>` branch, merge to `main`, then push the matching tag (or run the Release workflow with `workflow_dispatch`, optionally as a draft). The workflow validates, bundles and attaches the OpenCode themes, a zip, the VS Code `.vsix`, the Midnight Commander skins zip, the Claude Code themes zip, the TextMate themes zip and `SHA256SUMS` to a GitHub release with generated notes. Publishing to the VS Code Marketplace or Open VSX is a separate manual step.
- **Dependabot** labels npm updates `build` and Actions updates `ci`.
- Never push tags, trigger releases or dispatch workflows unless explicitly asked.

## Repository Layout

- `scripts/`: the palette (`palette.mjs`), colour helpers (`colour.mjs`), the theme generator (`build.mjs`), the shared hue ramps (`hues.mjs`), the VS Code generator and validator (`build-vscode.mjs`, `validate-vscode.mjs`), the Midnight Commander generator, validator, key list and installer (`build-mc.mjs`, `validate-mc.mjs`, `mc-skin-keys.json`, `install-mc.mjs`), the Claude Code generator, validator, token list and installer (`build-claude.mjs`, `validate-claude.mjs`, `claude-theme-tokens.json`, `install-claude.mjs`), the TextMate generator, validator and installer (`build-tmtheme.mjs`, `validate-tmtheme.mjs`, `install-tmtheme.mjs`), the OpenCode validator (`validate-themes.mjs`), a JSONC parser (`jsonc.mjs`), the release bundler (`bundle.mjs`), the local installer (`install.mjs`) and the licence-header check (`check-headers.sh`)
- `themes/`: the generated OpenCode theme files, committed so releases and manual installs work without a build
- `vscode/`: the VS Code extension: its manifest, README, `images/`, the generated `themes/`, and `upstream/` (the unmodified Dark+ and Light+ files with their `NOTICE.md`)
- `mc/`: the generated Midnight Commander skins in `skins/`, committed so releases and manual installs work without a build
- `claude/`: the generated Claude Code themes in `themes/`, committed so releases and manual installs work without a build
- `tmtheme/`: the generated TextMate themes, committed so releases and manual installs work without a build
- `assets/`: authored visual assets (`hero.svg`)
- `docs/`: `theme-format.md` (the OpenCode V2 format, token conventions and design decisions), `vscode-theme.md` (how the VS Code themes are built, validated and packaged) `mc-skin.md` (how the Midnight Commander skins are built, validated and tested), `claude-code-theme.md` (the Claude Code theme format, token roles and what was verified) and `tmtheme.md` (the TextMate themes for Codex, bat and delta)
- `.github/`: workflows, `dependabot.yml`, `release.yml` (changelog categories) and `zizmor.yml`

## Licence and Copyright

**REQUIREMENT:** Source files (`.mjs` and `.sh`) MUST include a licence and copyright header as the first content in the file (after a shebang, for scripts).

```js
// Brief one-line summary of what this file does
//
// (c) Copyright 2026 Liminal HQ, Scott Morris
// SPDX-License-Identifier: Apache-2.0 OR MIT
```

Shell scripts use the same format with `#` comments. Do not add headers to generated theme JSON, lockfiles, config files or Markdown. The repository is dual-licensed under Apache-2.0 or MIT (`LICENSE-APACHE` and `LICENSE-MIT`).
