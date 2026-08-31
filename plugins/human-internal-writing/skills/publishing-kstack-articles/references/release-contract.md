# KStack article release contract

Use this reference for local artifact generation and completion checks.

The default delivery path is `Markdown → 内网 Docs`. Preserve and verify the Markdown first, validate the exact Docs source, perform the authorized company Docs write, and read the remote result back. DOCX/WPS 仅在用户明确要求时生成; Word-specific gates are conditional, not part of the default release.

The release's canonical style tokens are [assets/kstack-style.v1.json](../assets/kstack-style.v1.json). Builders, structural validators, and publication checks must consume the same asset.

The Style Gate is a reproducible typography and layout floor, not an editorial verdict. It cannot prove information architecture, explain why several tracks belong together, or show that a reader can choose an entry point. A style-valid but structurally flat index or hub returns to `writing-human-internal-longform`; do not repair it with additional decoration.

## Required evidence

| Gate | Required artifact or evidence | Block examples |
|---|---|---|
| Source | One editable UTF-8 Markdown source for the release | draft only in chat, multiple competing sources |
| Images | For image-bearing articles, a release-local image directory and resolvable local Markdown image references | missing original, screenshot substitution, broken relative path, remote/data-URI image |
| Docs source | A styled Markdown/HTML source derived from the frozen Markdown plus a fresh passing `docs-style-validation.json` | stale source, unvalidated style, title hierarchy drift, or a misaligned/justified paragraph |
| Maintained index structure | A release-local structure contract and fresh validation bound to the canonical Markdown and exact Docs source | missing global orientation, stale heading order, hardcoded historical counts, or navigation drift |
| Publication | For company Docs delivery: resolved target, authorization, create or update result, readback, and a private receipt; a tracked/public projection is separately redacted | guessed target, write without authorization, success without readback, or raw internal evidence committed publicly |
| Word package | Only when explicitly requested: DOCX, style validation, complete target-app render and hash-bound review | stale DOCX, missing page, font substitution, clipped content |

The generic verifier is a floor. Continue running the article's own builder and verifier when they exist; the generic script does not replace factual, accessibility, citation, or article-specific checks.

## Artifact rules

- Create a new local Markdown version instead of overwriting an accepted source snapshot. A maintained index or work document may update the authorized existing Docs document while retaining this new local version.
- Keep the Markdown, images, styled Docs source, style validation, remote readback, and publication receipt aligned to the same version.
- Bind every style validation result to the source SHA-256, style-contract SHA-256, validator version or hash, and plugin version. A pass produced by an unknown or changed contract is stale evidence even when the source hash is unchanged.
- For a maintained index or hub, keep mutable headings, labels, canonical link sets/targets, image count/order keys, and other page-specific invariants in its release-local structure contract. Do not encode one release's titles or counts in the reusable Skill. Generate the contract with `scripts/validate_index_structure.py`; it binds these semantics to the canonical source hash, plugin version, structure-validator hash, and Docs-style-validator hash.
- Validate the exact Docs source against the maintained-index contract before the write, then compare the fresh remote readback with the same contract. `docs_verified` requires both local structure validation and structural remote parity; a successful write alone is insufficient.
- For an explicitly requested Word package, save `render-review.json` with schema `kstack.render-review.v1`, the reviewed DOCX SHA-256, `reviewed: true`, and the exact relative path/SHA-256 of every rendered page. Regenerate it after any DOCX or render change.
- Preserve original-resolution image files. A rendered page screenshot is verification evidence, never a source image.
- Keep SVG or other editable sources when available, plus portable raster derivatives used by DOCX/Docs.
- If an article has no images, no empty placeholder directory is required.
- When Word/WPS was requested, a DOCX opening successfully is not visual validation. Inspect all rendered pages for missing glyphs, font substitution, clipping, blank pages, isolated headings, broken captions, and table overflow.
- Bind every Docs write and readback record to the current Markdown SHA-256. Use `release-state.json` only for a requested multi-artifact Word/WPS package.
- For an existing Docs content update, prefer `word +write --position REPLACE_ALL` against the uniquely resolved `docId`, then fetch the same document again. For a style-only update, retain the `word +fetch-jsonml` preimage and version, generate constrained replacement ops, and use `word +update-jsonml --base-version`; prove after update that text leaves, links, images, list metadata, and anchors are unchanged.
- Keep full JSONML, preimages, structure contracts, raw tool responses, actual folder/document IDs, returned URLs, and document content only in an authorized local evidence directory that is non-public and excluded from version control. A public or tracked projection must omit content, headings, link labels/targets, image locators, and absolute local paths and explicitly redact every ID and URL.
- Durable validators, release state, and public projections use release-relative locators or basenames. Never serialize an absolute workstation path into their JSON output.

## Resume an interrupted Word/WPS release

Use this state machine only when Word/WPS was explicitly requested. After the canonical source freezes:

```bash
python3 scripts/release_state.py init \
  --state "/absolute/release/release-state.json" \
  --source "/absolute/release/article.md" \
  --terminal-state word_verified \
  --json
```

Before resuming, inspect the same source. Continue only from the returned `next_stage`; do not reuse a completed flag whose `source_sha256` differs from the current source.

```bash
python3 scripts/release_state.py inspect --state "/absolute/release/release-state.json" --source "/absolute/release/article.md" --json
python3 scripts/release_state.py mark \
  --state "/absolute/release/release-state.json" \
  --source "/absolute/release/article.md" \
  --stage docx_structurally_valid \
  --json
```

`word_verified` stops after the ordered stages `source_ready`, `docx_generated`, `docx_structurally_valid`, `wps_visually_verified`, and `word_verified`. It never exposes or advances to a Docs stage. Only when the same release explicitly requests both Word/WPS and Docs may initialization use `--terminal-state docs_verified --docs-target-label '<resolved target label>' --docs-authorized`; that branch adds `docs_created` and `docs_readback_verified`. Every `mark` requires `--source`, re-hashes it, invalidates prior checkpoints on drift, and fails closed instead of marking the requested stage. A checkpoint records progress, not permission and not proof by itself; keep the underlying evidence.

## Status vocabulary

- `draft`: prose or files are still changing.
- `markdown_blocked`: Markdown, required images, or Docs style validation is incomplete.
- `markdown_verified`: the frozen Markdown and exact Docs source have fresh evidence.
- `publish_ready`: Markdown verification passed and the target is resolved, but no external write has occurred.
- `docs_blocked`: creation or readback failed or authorization is absent.
- `docs_verified`: creation or update plus post-write verification passed for the requested target; a maintained index or hub also has fresh structure validation and matching remote readback.
- `word_verified`: an explicitly requested Word/WPS package passed its additional artifact and rendering gates.

Never collapse `publish_ready` into `docs_verified`.

## Verification commands

For the default route, validate the exact Docs source and then inspect fresh remote readback. The validator does not perform the write or prove the remote state:

```bash
python3 "<loaded publishing-kstack-articles Skill directory>/scripts/validate_docs_style.py" \
  "/absolute/release/article-docs-source.md" --json
```

For a maintained index or hub, capture the semantic contract from the canonical Markdown, compare the exact local Docs source before writing, and compare the fresh fetched/exported remote Markdown or HTML after writing:

```bash
python3 "<loaded publishing-kstack-articles Skill directory>/scripts/validate_index_structure.py" capture \
  --source "/absolute/release/index.md" \
  --output "/absolute/private-evidence/index-structure.json" \
  --format markdown --json

python3 "<loaded publishing-kstack-articles Skill directory>/scripts/validate_index_structure.py" compare \
  --source "/absolute/release/index.md" \
  --contract "/absolute/private-evidence/index-structure.json" \
  --remote "/absolute/release/index-docs-source.html" \
  --source-format markdown --remote-format auto --json

python3 "<loaded publishing-kstack-articles Skill directory>/scripts/validate_index_structure.py" compare \
  --source "/absolute/release/index.md" \
  --contract "/absolute/private-evidence/index-structure.json" \
  --remote "/absolute/private-evidence/fresh-remote-index.md" \
  --source-format markdown --remote-format auto --json
```

For an explicitly requested Word/WPS package, additionally run the generic artifact verifier:

```bash
python3 "<loaded publishing-kstack-articles Skill directory>/scripts/verify_release.py" \
  --markdown "/absolute/release/article.md" \
  --docx "/absolute/release/article.docx" \
  --images-dir "/absolute/release/images" \
  --render-dir "/absolute/release/rendered-pages" \
  --render-review "/absolute/release/render-review.json" \
  --json
```

Omit `--images-dir` for a text-only Word/WPS release. If the Markdown contains an image reference, `--images-dir` is mandatory and must contain the referenced release-local asset.

A passing local validator is not `docs_verified`. That state requires inspection of the live create-or-update result, fetch output, links, and image export count when applicable. For a maintained index or hub, it additionally requires the remote heading order, navigation, link set, images, and other declared structure to match the frozen release contract.
