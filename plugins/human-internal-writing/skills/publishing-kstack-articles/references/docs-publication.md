# Publish a verified article to company Docs

Use this reference after the Markdown Gate is green or when resolving the target read-only.

The default path is `Markdown → 内网 Docs`. DOCX/WPS 仅在用户明确要求时生成; neither artifact is a prerequisite for company Docs publication.

Page, size, color, and alignment values come from [assets/kstack-style.v1.json](../assets/kstack-style.v1.json). Do not duplicate or locally reinterpret those tokens in a Docs-source builder.

The default formal-article profile centers H1, subtitle, and publication date; H2, H3, and body text are left aligned. The index profile centers only H1; subtitle, publication date, H2, H3, and body text are left aligned. Select the profile from the document form and validate that exact source; do not use the default masthead alignment as an index fallback.

## Target policy

The default destination is the current user's dedicated shared drive whose title exactly equals `我的个人主页`. Resolve it on every publication. The title is an alias, not proof of identity; never persist a previously returned internal ID as the permanent target.

Before running Docs commands, read the current `docs-cli`, `docs-shared`, `docs-docs`, and `docs-word` Skill instructions plus the references for shared-drive listing, word creation, word fetch, and Markdown export.

Run the supported version check once per session:

```bash
kcli docs-cli --version
```

Resolve the unique target from a complete page:

```bash
set -o pipefail
kcli docs-cli +list-shared-drive --page-size 100 |
  python3 "<loaded publishing-kstack-articles Skill directory>/scripts/resolve_docs_target.py" \
    --title '我的个人主页'
```

The resolver accepts a page only when `hasNext` is exactly JSON `false`. A missing field, `null`, a string such as `"false"`, numeric zero, or `true` is not proof of completeness and fails closed. Zero matches, duplicate matches, missing IDs, or a non-`group` `docTypeEn` also fail closed. If pagination becomes necessary, complete the documented pagination flow and do not select a target from a partial page.

## Authorization and preview

Creating or updating a Docs document is an external write. An explicit request such as “发布/写入/同步到我的公司内分享专区” authorizes creation of the named article after Markdown verification. A request to “直接改这个内网文档” authorizes only the resolved existing document. “准备发布版”“看看能否发布” or a general preference for future capability does not authorize a write.

Immediately before the write, make the target and consequence inspectable:

- exact title `我的个人主页` and current resolved target type/ID;
- article title and local release version;
- Markdown/image zip used as the Docs source;
- link-share and classification settings, if explicitly requested, plus the mandatory page setting `A3`;
- operation and consequence: either one new ordinary Docs document will be created, or the one explicitly named maintained document will be updated in place.

Do not pass `--link-share` or `--classify-level` unless the user supplied those values. For KStack article and article-index publication, always pass `--view-model A3`; this repository convention overrides the general Docs default. A request for another page model requires changing this publishing policy before release rather than silently creating a one-off exception.

## Create from Markdown and images

The content zip must contain exactly one Markdown file plus its referenced image assets. Use the current resolved folder ID:

Before creating the zip, run `scripts/validate_docs_style.py` against that exact Markdown/HTML source and save the passing JSON as `docs-style-validation.json` beside the release. Re-run it after the zip is finalized and immediately before the write. The source must follow the selected profile in [visual-style-contract.md](visual-style-contract.md): native Docs font stack, exact editor sizes/colors, profile-correct alignment, semantic paragraph roles, compact body H1, and no nested overrides. Confirm the validator reports `default` for a formal article or `index` for an article index. A formal masthead uses one exact `YYYY 年 M 月 D 日` date without a visible timezone, and its H1 must not recombine a separately rendered subtitle. `viewModel=A3` does not relax the exact editor-size-11 rule for body, list, and lead text.

For a maintained index or hub, capture its release-local semantic structure from the frozen canonical Markdown, then compare the exact Docs source against that contract before writing:

```bash
python3 "<loaded publishing-kstack-articles Skill directory>/scripts/validate_index_structure.py" capture \
  --source '<absolute canonical Markdown>' \
  --output '<absolute private evidence directory>/index-structure.json' \
  --format markdown \
  --json

python3 "<loaded publishing-kstack-articles Skill directory>/scripts/validate_index_structure.py" compare \
  --source '<absolute canonical Markdown>' \
  --contract '<absolute private evidence directory>/index-structure.json' \
  --remote '<absolute Docs-source Markdown or HTML>' \
  --source-format markdown \
  --remote-format auto \
  --json
```

The structure contract captures heading order, the canonical link set/targets, and image count/order keys without hardcoding a particular title, track count, or track name in the reusable Skill. It is bound to the canonical source SHA-256, plugin version, structure-validator SHA-256, and Docs-style-validator SHA-256. A changed source or validator makes the contract stale.

```bash
kcli docs-cli word +create \
  --title '<actual article title>' \
  --content-zip '<absolute release source zip>' \
  --folder-id '<resolved folder id>' \
  --view-model A3
```

Do not substitute `docs-cli +import` and do not use a DOCX as the content source. Markdown plus images is the Docs source of truth.

## 更新已有文档

When the user explicitly identifies an existing ordinary Docs document and asks to update it, preserve a new local Markdown version and validate its exact styled Docs source first. Fetch the same document through the `docs-cli` capture wrapper and export its current Markdown/images into the private evidence directory before editing.

For an authorized content replacement, prefer the current public CLI and replace only the resolved document:

```bash
kcli docs-cli word +write \
  --doc-id '<resolved document id>' \
  --content-zip '<absolute release source zip>' \
  --position REPLACE_ALL
```

Use `--content-file` instead of `--content-zip` only for a text-only source. Do not fall back to Browser merely to replace正文; a write success remains provisional until the same `docId` is fetched and compared with the frozen Markdown.

For a style-only repair, do not replace the content. Fetch the current JSONML/version, save it as a private preimage, generate constrained ops, dry-run them, and apply them with the fetched base version:

```bash
kcli docs-cli word +fetch-jsonml \
  --doc-id '<resolved document id>' \
  --format raw \
  > '<absolute private preimage JSON>'

python3 "<loaded publishing-kstack-articles Skill directory>/scripts/repair_docs_jsonml_style.py" \
  --input '<absolute private preimage JSON>' \
  --output '<absolute private style ops JSON>'

kcli docs-cli word +update-jsonml \
  --doc-id '<resolved document id>' \
  --ops-file '<absolute private style ops JSON>' \
  --base-version '<version returned by fetch-jsonml>' \
  --dry-run

kcli docs-cli word +update-jsonml \
  --doc-id '<resolved document id>' \
  --ops-file '<absolute private style ops JSON>' \
  --base-version '<version returned by fetch-jsonml>'
```

The style ops may change only alignment, line-height, role size/color, and necessary emphasis. They must preserve every text leaf, link, image, list attribute, custom block, and anchor. A missing or zero base version is not acceptable concurrency evidence. After the update reports saved, fetch the same `docId` again, compare text leaves and preserved anchors against the preimage, and inspect the rendered title hierarchy, alignment, links, and spacing.

## Verify the remote result

Creation or update success is provisional. Use the actual `docId` with the `docs-shared` capture wrapper and `word +fetch --format raw`. Compare the returned title/body/links with the final Markdown. For image-bearing articles, also run `word +export-md --unzip` and confirm the actual `data.image_count` equals the source expectation.

For a maintained index or hub, run the same structural comparison against the freshly fetched Markdown/HTML readback or the Markdown path returned by `word +export-md`:

```bash
python3 "<loaded publishing-kstack-articles Skill directory>/scripts/validate_index_structure.py" compare \
  --source '<absolute canonical Markdown>' \
  --contract '<absolute private evidence directory>/index-structure.json' \
  --remote '<absolute fresh fetched or exported Markdown/HTML>' \
  --source-format markdown \
  --remote-format auto \
  --json
```

Any changed heading order, canonical link set/target, image count/order key, source hash, plugin version, or validator hash is a publication block. This deterministic comparison supplements the normal title/body/link readback; it does not prove that the remote call happened on its own.

Do not create another document merely because readback failed. Report the created URL and the verification block so the user can decide whether to retry verification or create a replacement.

## Publication receipt

After successful readback, save the full `docs-publication.json` only in an authorized local evidence directory that is non-public and excluded from version control. The full JSONML, fetched preimage, raw create/update/fetch outputs, real folder/document IDs, returned URL, and article-specific structure contract belong only in that private evidence area; never place them in a public repository, plugin package, tracked release folder, issue, test fixture, or public projection. A redacted structure result may retain hashes and pass/fail booleans, but must omit headings, link labels/targets, image locators, document text, IDs, URLs, and absolute paths.

The private receipt uses this schema:

```json
{
  "schema_version": "kstack.docs-publication.v1",
  "target": {
    "kind": "drive",
    "id": "actual resolved folder id",
    "label": "我的个人主页"
  },
  "document": {
    "docId": "actual returned document id",
    "url": "actual returned document URL",
    "operation": "create or update",
    "viewModel": "A3 for a new document; omit if an existing document model was not changed"
  },
  "release": {
    "title": "actual article title",
    "version": "actual local release version",
    "markdownSha256": "SHA-256 of current Markdown",
    "docsSourceSha256": "SHA-256 of validated Docs source"
  },
  "authorization": {
    "confirmed": true
  },
  "readback": {
    "verified": true,
    "titleMatched": true,
    "bodyMatched": true,
    "linksMatched": true,
    "imageCount": 0
  }
}
```

Use actual tool results only. Bind the receipt to the exact local Markdown and Docs-source hashes. `linksMatched` is true only when fresh readback confirms the canonical link set and targets; body equality does not imply it. For `operation=create`, `document.viewModel` records the page model sent in the successful request and absence of `A3` is a verification failure. For `operation=update`, do not invent a page-model value that was not changed or read. The receipt is evidence metadata, not permission to publish this or another version; authority comes from the current user request.

If a repository needs durable release status, generate a separate redacted `docs-publication.public.json`. It may retain the schema/status, operation, non-sensitive alias, hashes, and match booleans, but it must replace IDs and URLs with explicit redaction flags and must omit JSONML, preimages, raw response bodies, local absolute paths, and document text. Never feed this public projection to `verify_release.py`; verification consumes the authorized private receipt.

```json
{
  "schema_version": "kstack.docs-publication-public.v1",
  "target": {
    "kind": "drive",
    "label": "configured target alias",
    "idRedacted": true
  },
  "document": {
    "operation": "create or update",
    "viewModel": "A3 when verified",
    "docIdRedacted": true,
    "urlRedacted": true
  },
  "release": {
    "version": "local release version",
    "markdownSha256": "SHA-256 of current Markdown",
    "docsSourceSha256": "SHA-256 of validated Docs source"
  },
  "readback": {
    "verified": true,
    "titleMatched": true,
    "bodyMatched": true,
    "linksMatched": true
  }
}
```

Only fresh live outputs from this run—the resolved target, actual create-or-update result, fetched title/body/links, and image export count when applicable—close publication as `docs_verified`.
