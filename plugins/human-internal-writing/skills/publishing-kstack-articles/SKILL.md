---
name: publishing-kstack-articles
description: Use when a KStack internal or technical article, maintained article index, or editorial hub must be preserved as Markdown, published or updated in company Docs, or explicitly delivered as a Word/DOCX/WPS package.
---

# Publishing KStack Articles

## Own the release outcome

Use this Skill after or alongside editorial work. `writing-human-internal-longform` owns source fidelity and the canonical Markdown; this Skill owns artifacts derived from that frozen source and publication evidence. Load both once when both apply; their cross-references define ownership and do not require recursively restarting either workflow.

For article drafting or revision, **REQUIRED SUB-SKILL:** use `writing-human-internal-longform`. For company Docs publication, **REQUIRED SUB-SKILL:** use `docs-cli` and its shared, docs, and word references. Use the available `documents` or `docx` Skill only when the user explicitly requests a DOCX/Word/WPS deliverable.

A passing Style Gate is only a typography and layout floor. It does not prove information architecture, global coherence, or reader usefulness. If a style-valid index or hub still feels flat, crowded, or hard to enter, return to `writing-human-internal-longform` for editorial diagnosis before regenerating release artifacts. Do not stack a decorative card, banner, ornamental image, table, or accent color on top of an unresolved structural problem.

The default KStack delivery path is `Markdown → 内网 Docs`. Freeze and preserve Markdown first, then write or update the company document, then read the remote result back. DOCX/WPS 仅在用户明确要求时生成; do not create, render, or maintain those artifacts by default.

## Define the requested terminal state

Choose one status before work begins:

- `markdown_verified`: editable Markdown exists; image-bearing articles also retain the complete local image set; the exact Docs source passes style validation.
- `docs_verified`: `markdown_verified` is already true, the user has authorized the write, the requested company document was created or updated, and title/body/links/images were read back successfully. For a maintained index or hub, its frozen structure contract and remote readback must also agree on section order, navigation, links, and other declared structural invariants.
- `word_verified`: only when explicitly requested, a valid DOCX and its target-app rendering evidence exist in addition to the Markdown source.

If the user asks for release files without naming Word/WPS, stop at `markdown_verified`. A review-only or editorially-ready request does not invoke this Skill unless project rules explicitly require publication. If the user explicitly asks to publish, synchronize, or update the company document, the requested terminal state is `docs_verified`. Do not interpret “make it publishable” as authorization to publish.

An early complete draft may be shown before either terminal state is reached. It is a progress milestone, not evidence that the release is complete.

Before the canonical Markdown freezes, do only work that will not become stale: inventory original images, preflight the version directory, and inspect the Docs target read-only when publication is already requested. Generate the Docs source and receipts only from the final matching Markdown/version/hash. Generate DOCX, renders, and render reviews only for an explicit `word_verified` request.

## Enforce the release contract

Read [references/release-contract.md](references/release-contract.md) before generating release files. Preserve confirmed historical versions and unrelated workspace changes.

Read [references/visual-style-contract.md](references/visual-style-contract.md) before generating a company Docs source or an explicitly requested DOCX. Its sizes, colors, page model, and compact-masthead rules are exact release tokens, not suggestions. The flexible ranges in the editorial guide apply only outside this KStack release profile.

Treat [assets/kstack-style.v1.json](assets/kstack-style.v1.json) as the single machine-readable source for page, font, size, color, spacing, and alignment tokens. Generators and validators must consume that file instead of carrying private copies. The visual reference explains the tokens; it does not override the asset. A mismatch between prose, generator, validator, and asset is a release block.

Apply the selected KStack profile exactly. In the default formal-article profile, H1/main title, subtitle, and publication date are centered; H2, H3, and lower-level headings are left aligned. In the index profile, only H1 is centered; subtitle, publication date, H2, H3, and every other text role are left aligned. Kicker, lead, body, list item, caption, and source/note are always left aligned. Two-sided justification is forbidden. Apply the corresponding DOCX profile only when it was explicitly requested.

For new formal articles, preserve the canonical three-line masthead across channels: main title, subtitle, then exact publication date. The document metadata title and index link text use only the main title. Do not show a timezone in the kicker, H1, subtitle, or date, and do not recombine a separately rendered subtitle into the H1 with `：` or `｜`. Confirmed historical versions remain unchanged.

Every `markdown_verified` release version must contain:

1. the editable source Markdown;
2. for an image-bearing article, a complete image directory preserving original assets, order, captions, and section mapping;
3. the exact Markdown/HTML source used for company Docs;
4. a fresh passing `docs-style-validation.json`.

A `docs_verified` release must additionally retain the authorized write result and fresh remote readback evidence.

For a maintained index or hub, also preserve a fresh structural validation bound to the same canonical Markdown and Docs source, then prove the remote readback matches its declared heading order, navigation, link set, images, and other page-specific invariants. Keep current counts and labels in the release-local contract rather than hardcoding them into this Skill. Use the reusable helper for both phases:

```bash
python3 "<loaded publishing-kstack-articles Skill directory>/scripts/validate_index_structure.py" capture \
  --source '<absolute canonical Markdown>' \
  --output '<absolute private evidence directory>/index-structure.json' \
  --format markdown --json

python3 "<loaded publishing-kstack-articles Skill directory>/scripts/validate_index_structure.py" compare \
  --source '<absolute canonical Markdown>' \
  --contract '<absolute private evidence directory>/index-structure.json' \
  --remote '<absolute exact Docs source or fresh remote readback>' \
  --source-format markdown --remote-format auto --json
```

Run `compare` once against the exact local Docs source before the write and again against the fresh fetched/exported remote result after it. The contract and full comparison evidence contain article-specific headings and link targets, so keep them in the authorized non-public evidence area; a public projection retains only hashes and booleans.

When `word_verified` is explicitly requested, additionally require a DOCX, rendered page images, a `kstack.render-review.v1` record, a passing `kstack.docx-style-validation.v1` result, and the applicable release verification output.

For an explicit Word/WPS delivery, load the bundled workspace dependencies and use the renderer supported by the active `documents` or `docx` Skill; do not assume that the article repository contains a private rendering script. System Python may lack the required document dependencies. Inspect every rendered page. Structural ZIP/XML checks do not count as visual QA.

When the user names WPS as the target, open the exact DOCX in WPS, export that document to PDF, and inspect every exported page. The WPS PDF is the authoritative visual record; a LibreOffice render is only a secondary compatibility signal and must not replace or contradict the target-app check. Record the DOCX hash, WPS PDF hash, page-image hashes, page count, and actual embedded PDF fonts in the render review.

For DOCX, verify the exact A4/21 mm Word-WPS profile from the visual contract during page inspection. Select its complete OS-specific font profile—Windows/WPS (`微软雅黑` + `宋体`) or macOS/WPS (`PingFang SC` + `Songti SC`)—with `Arial` as the Latin companion, then enforce the exact point sizes and approved palette. Body text, list text, and lead text default to exactly 11 pt; this is a hard value, not a range. Company Docs remains A3 but uses the same nominal editor sizes: body, list, and lead are exactly 11. The Docs importer maps the numeric `font-size` token to the editor's font-size control; do not write `17px` hoping it will render as an 11 pt-equivalent screen size. A declared style without a clean target-app render is not a pass.

When a Word/WPS package is requested, initialize `release-state.json` with `scripts/release_state.py init --terminal-state word_verified` after freezing the canonical Markdown. That branch stops at `word_verified` and contains no Docs stages. Only if the same request explicitly includes an authorized Docs publication with a resolved target may initialization use `--terminal-state docs_verified --docs-target-label '<resolved target label>' --docs-authorized`. Pass the current `--source` on every `mark`; the state tool re-hashes it and fails closed on drift. For the default Markdown-and-Docs path, preserve the Markdown hash, Docs style validation, write result, and remote readback without manufacturing unused WPS checkpoints.

When delivery speed is being evaluated, also use the loaded writing Skill's `scripts/track_writing_timing.py` from `started` through the requested terminal state. Its `durations_seconds` and `elapsed_seconds` fields are the comparable wall-clock record; release-state completion timestamps alone are not a duration report or an SLA result.

For an explicit Word/WPS package, run the deterministic gate with absolute paths:

```bash
python3 "<loaded publishing-kstack-articles Skill directory>/scripts/verify_release.py" \
  --markdown "<absolute-markdown>" \
  --docx "<absolute-docx>" \
  --images-dir "<absolute-images-dir>" \
  --render-dir "<absolute-render-dir>" \
  --render-review "<absolute-render-review-json>" \
  --json
```

Omit `--images-dir` for a text-only Word/WPS release. If the Markdown references any image, the directory argument becomes mandatory and every reference must resolve inside it. The verifier requires an exact ordered match of normalized semantic text blocks, Markdown-to-DOCX hyperlink targets, and rendered image references; substring presence or an unreferenced media file is not content proof. It also rejects a canonical Markdown H1 that recombines subtitle/date metadata; package the formal masthead as three distinct roles instead.

For an index or hub Word/WPS package, add `--docx-profile index` and require the saved DOCX style receipt to report `profile: index`; omit it for the unchanged default formal-article profile.

Replace `python3` with the bundled workspace Python when the system environment lacks document dependencies. A nonzero result is a release block, not a warning.

## Publish to the dedicated company area

Read [references/docs-publication.md](references/docs-publication.md) only when the requested terminal state is `docs_verified` or the user asks to inspect the target.

The default target alias is the exact shared-drive title `我的个人主页`. Resolve it live; never hardcode a previously observed folder or view ID. Zero matches, multiple matches, incomplete pagination, loss of permission, or a changed target are blockers.

Before the external write, verify the final title, target, source package, requested sharing/classification settings, and whether the user has actually asked to publish. Every KStack article or article-index page published to company Docs must use the A3 page model. Use `docs-cli word +create` with the Markdown/image zip, the resolved `--folder-id`, and `--view-model A3`; do not import the DOCX as the Docs source. A create command without `--view-model A3` is a publication block.

Validate the exact Docs-source Markdown/HTML before building the content zip and again immediately before creation:

```bash
python3 "<loaded publishing-kstack-articles Skill directory>/scripts/validate_docs_style.py" \
  "<absolute Docs-source Markdown path>" \
  --json
```

The validator enforces the native font policy, exact role-based sizes, colors, profile-specific alignment, semantic paragraph markers, nested-style consistency, and the compact body title. This Style Gate does not prove information architecture, section quality, or remote content parity. Any style finding is a publication block. Preserve the passing output as `docs-style-validation.json`; require it to identify the exact source hash, style-contract hash, validator version or hash, and plugin version, and do not reuse evidence from an earlier source or contract.

After creation, read the new document back through the `docs-cli` capture wrapper and export Markdown/images when images are present. For a maintained index or hub, compare the fresh remote readback with the frozen structure contract; a successful write without structural remote parity is not `docs_verified`.

When the user explicitly requests updating an existing ordinary Docs document, prefer the current public CLI. For a content replacement, use `docs-cli word +write --doc-id '<resolved id>' --content-zip '<release zip>' --position REPLACE_ALL`, then fetch the same document again. For a style-only repair, fetch and save its JSONML/version with `word +fetch-jsonml`, run `scripts/repair_docs_jsonml_style.py` against that private preimage, dry-run the ops, and apply them with `word +update-jsonml --base-version '<fetched version>'`; the ops may change only style attributes and must preserve text leaves, links, images, list metadata, custom blocks, and anchors. Do not substitute a browser-first editing path for these available commands.

Bind the private publication receipt to both `markdownSha256` and `docsSourceSha256`, and record `linksMatched` only from fresh link readback; do not use a DOCX hash or body match as a substitute. Record full JSONML/preimages, structure contracts, raw responses, actual identifiers, URL, and document content only in an authorized local evidence directory that is non-public and excluded from version control. A tracked or public projection must redact IDs/URLs, omit headings/link targets/content and absolute local paths, and must not be presented to the verifier as the private receipt.

The verifier may return `docs_evidence_consistent`; that means only that the receipt is structurally consistent with the current applicable artifact hashes and required target. It never proves that a remote call happened. Claim `docs_verified` only after inspecting the current run's actual target-resolution, create, fetch, and image-export outputs. The receipt's `authorization.confirmed` field records the authority already present in the current user request; it cannot grant permission by itself.

## Stop conditions

Do not claim completion when any of these is true:

- Markdown is missing, or an image-bearing article lacks its complete image directory;
- any original image was silently removed, reordered, downsampled, or replaced with a screenshot;
- Markdown embeds remote or data-URI images instead of release-local assets;
- only an online Docs link exists without its preserved Markdown source;
- the Docs target was guessed or selected from an incomplete/ambiguous list;
- a new Docs create request or publication receipt does not prove `viewModel=A3`;
- the current Docs source has no fresh passing `docs-style-validation.json`, or contains a forbidden font, size, color, wrong masthead/heading alignment, justified paragraph, unmarked special paragraph, nested style override, or expanded body title;
- the style receipt is not bound to the current source, style contract, validator, and plugin version;
- a maintained index or hub lacks fresh structure validation or remote readback parity for its declared headings, navigation, links, images, and page-specific invariants;
- a style-valid page still has unresolved information architecture and was decorated instead of being returned to editorial revision;
- an existing Docs style update lacks a fetched preimage, base-version check, style-only ops, or post-update proof that user text, links, images, lists, custom blocks, and anchors were preserved;
- publication was not authorized for the current article;
- Docs creation or update returned success but title, body, links, or images were not read back;
- raw Docs content, JSONML/preimages, actual IDs/URLs, or absolute workstation paths were copied into a public or tracked evidence projection;
- Word/WPS was explicitly requested but its DOCX, render, style validation, or visual evidence is missing.

Do not turn `docs_evidence_consistent` into `docs_verified` without fresh live outputs from the same publication run.

If the user literally requests WordPress rather than Word/WPS, treat that as a separate HTML/asset deliverable and state that it is outside this Skill's DOCX contract unless explicitly added to the request.
