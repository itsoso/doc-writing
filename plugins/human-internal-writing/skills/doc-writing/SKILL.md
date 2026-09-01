---
name: doc-writing
description: Route a writing task through the smallest safe combination of evidence, editorial, Kim, Docs, image, and publication capabilities. Use when a task may involve enterprise sources or when doc-writing is being packaged for GitHub.
---

# Doc-writing

## Purpose

This is the primary entry point for `doc-writing`. It turns the author's writing method into a repeatable, evidence-led workflow while keeping enterprise data connectors outside the public repository.

This entry point owns classification and hand-off. It does not replace the editorial or connector Skills, and it must not copy Kim/Docs source content into reusable examples. For direct editorial work, it delegates to `writing-human-internal-longform`; that lower-level Skill remains available for advanced users who need to select `EDIT`, `EXPAND`, or `AUDIT` explicitly.

## Dependency profiles

Use [`config/skill-dependencies.json`](../../../config/skill-dependencies.json) and `scripts/check_dependencies.py` to resolve capabilities before reading enterprise sources:

- `generic` is self-contained and uses only the bundled editorial and optional publishing Skills;
- `kuaishou-internal` adds controlled-runtime capabilities for Docs read/write, Kim message retrieval, and read-only Onepoint meeting retrieval;
- enterprise dependencies are resolved by Skill name/capability, never by copying their implementation, data, URLs, tokens, cookies, or local paths into this repository.

When an internal capability is missing, stop with `blocked` and show the missing names. Do not silently install, substitute a browser scrape, or weaken a read-only boundary. An administrator may review the generated install plan and provision the approved internal Marketplace/runtime before retrying.

## Classify before reading sources

Capture five fields before drafting:

1. `source` — where the evidence lives;
2. `author` — whose judgment and voice must remain visible;
3. `reader` — who should change what after reading;
4. `change` — the decision, behavior, or action the article should cause;
5. `audience` — `internal`, `public_candidate`, or `public`.

Default to `internal` when the source is Kim, Docs, Onepoint, code, logs, or an enterprise meeting. `public_candidate` is a review state, not permission to publish. `public` requires a written clearance record and a clean public export.

## Route to the smallest capable Skill

Use the matrix in [references/enterprise-route-matrix.md](references/enterprise-route-matrix.md). The essential rules are:

- Kim history for one sender and a date range goes through `kim-sender-context`; keep retrieval local and read-only.
- Other Kim operations go through `kim-cli` and its declared sub-Skill (`kim-calendar`, `kim-contact`, `kim-im`, `kim-todo`, or `kim-vc`).
- Docs search and asset discovery go through `docs-cli` and the matching `docs-search`, `docs-view`, `docs-docs`, `docs-recommend`, `docs-security`, `docs-recycle-bin`, or `docs-sheets` reference.
- Ordinary Docs正文 and article writes go through `docs-cli` plus `docs-word`; meeting records go through `docs-meeting-record`.
- Article prose and evidence boundaries go through `writing-human-internal-longform`.
- Article packaging, image checks, Docs style checks, article readback, and index synchronization go through `publishing-kstack-articles`.

Never call hidden APIs, hand-write tokens, scrape browser state as a connector substitute, or bypass a connector's readback and authorization rules.

## The author's writing loop

The canonical loop is:

```text
OKR/mainline → concrete scene or business question → one central judgment
→ evidence ledger → narrative spine → draft → image plan → review
→ measurable experiment/action → Markdown freeze → Docs write/readback
→ maintained index update/readback
```

Preserve the author's observation, trade-off, uncertainty, and requested action. Separate `Verified`, `Observed`, `Inference`, `Scenario`, `Proposal`, and `Unknown`; never turn a plausible interpretation into a fact.

Every article brief must name a result owner, baseline, deadline, acceptance evidence, and stop/rollback condition when it proposes action. Do not use Token count, code volume, or document completion as a substitute for user or business impact.

## Required hand-off artifacts

The router passes a small, inspectable bundle between stages:

- `article-brief.json` — reader, change, mainline, central judgment, and narrative spine;
- `evidence-ledger.json` — Claim IDs, source locators, evidence state, freshness, and sensitivity;
- `image-manifest.json` — 1–3 information-bearing images, alt text, caption, section, and provenance;
- `publication-receipt.json` — Markdown hash, Docs target, readback, and index synchronization evidence;
- `clearance.json` — only for `public` output: legal, security, business-owner decision and scope.

All artifacts must contain references or hashes, not raw Kim messages, raw Docs exports, access tokens, cookies, signed URLs, or personal identifiers.

## Failure-closed rules

Stop and surface a blocker when:

- the source, audience, mainline, or owner is ambiguous;
- a claim has no controlling source or its freshness is unknown;
- a Kim/Docs permission or readback is incomplete;
- the article has fewer than one information-bearing image or its image provenance is missing;
- a public export contains enterprise URLs, document IDs, credentials, personal information, or unapproved internal numbers;
- Markdown, article Docs, or the maintained index disagree after readback.

The public GitHub package contains this router, schemas, tests, and sanitized examples. Enterprise connector Skills remain installed in the controlled runtime and are referenced by name; their data and credentials are never vendored.
