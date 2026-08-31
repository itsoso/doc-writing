# Faster writing without weaker evidence

Use this reference to reduce waiting and repeated work. The target is a shorter time to a complete readable draft and a shorter time from draft to verified release. It does not weaken technical truth, publication authorization, A3, visual inspection, or remote readback requirements.

## Build one minimum article brief

For a new article, keep the pre-draft artifact compact:

| Field | Minimum useful content |
|---|---|
| Reader change | current belief or behavior, desired change, first practical action |
| Author judgment | distinctive observation, protected trade-off, confidence boundary |
| Narrative spine | central tension and one-line function for each section |
| Evidence | claim, locator, state, and conflict or missing proof |

Do not create separate polished documents for the evidence ledger, voice map, reader change, and outline. They are working state. Expand the evidence portion only for high-risk claims or genuine source conflicts.

## Preserve load-bearing meaning during structural rewrites

Before substantially shortening or restructuring an existing article, classify its narrative assets by function:

| Decision | Typical material |
|---|---|
| `keep` | Source-backed scene or observed failure, decisive trade-off, minimal technical mechanism, counterforce, or next proof that makes the central judgment credible |
| `compress` | Repeated explanation, overlapping examples, long catalogs, or multiple caveats about the same claim |
| `remove` | Unsupported expansion, distant forecast, external analogy that does not change the decision, or a second conclusion that competes with the spine |
| `move` | Version provenance, image history, release mechanics, exhaustive source notes, or other material better carried by a README, receipt, appendix, or evidence ledger |

This is a preservation map, not a content template. A short article does not need one of every item. It fails, however, when all of the source-backed scenes and mechanisms that earned the central judgment are removed while only conclusions, labels, and controls remain.

After drafting, compare the old and new reverse outlines. Record what was intentionally removed and verify that every surviving central judgment still has a path from observation or evidence through mechanism or trade-off to consequence and next proof. Do not use character reduction as a quality target by itself.

## Bound evidence discovery

Before searching, name the claim the search must confirm or bound and the evidence type that would be sufficient. Stop discovery for the first draft when every central claim is either supported, honestly marked as inference/scenario/proposal, or exposed as `Unknown`.

Do not keep searching merely to remove all Unknowns. Continue only when the missing answer would change the central judgment, safety boundary, requested action, or release truth. A complete draft can carry visible Unknowns; a verified claim cannot.

## Extract independent sources in parallel

When three or more sources are independent and delegation is available, parallelize read-only extraction. Give every extractor the same schema:

- exact claim or question;
- source locator and version or date;
- speaker or author attribution;
- confidentiality, allowed use, and authorized workspace boundary;
- evidence state;
- supported wording and unsupported extension;
- conflict, uncertainty, or next proof.

Every delegated worker must operate inside the same authorized access boundary and receive only the minimum source subset needed for its assigned claim. Delegation availability is not source authorization. Do not delegate final prose or divide the article by section. One writer must merge the evidence, resolve conflicts, preserve attribution and one authorial voice, and own the final causal argument. Skip delegation when setup and reconciliation are likely to cost more than reading the small source set directly, or when the sources are tightly coupled or especially sensitive.

## Reuse prior verified work by blast radius

For a revision, compare the new source and requested change with the prior canonical Markdown and working evidence. Classify each prior item:

- `reuse` — evidence is immutable or still within its explicit freshness window, and its locator, version or content fingerprint, claim meaning, and article function are unchanged;
- `recheck` — wording is unchanged but a dependency, number, scope, or source changed;
- `invalidate` — evidence no longer supports the claim or the claim's role changed;
- `new` — introduced by the requested revision.

Edit `recheck`, `invalidate`, and `new` items plus their direct narrative dependents. Preserve `reuse` items. Re-run a full-document coherence read and deterministic checker at the end, while reporting pre-existing findings separately from new regressions.

Treat unversioned dashboards, live URLs, APIs, configurations, code branches, organizational facts, prices, schedules, and other mutable sources as `recheck` unless current content or an accepted freshness window has been confirmed. Invalidate a reused item when its source content or version changed, its calculation inputs changed, the article makes a stronger claim, its scope expanded, or a conflicting source appeared. Cosmetic wording changes alone do not invalidate immutable, version-bound evidence.

## Parallelize only safe release preparation

Before canonical Markdown freezes, it is safe to inventory original images, check tool dependencies, preflight output directories, and resolve a company Docs target read-only when publication is already in scope. Any source zip, optional DOCX, rendered pages, review receipt, or publication receipt must be derived from the final matching version and hash.

Keep the default dependency chain sequential: canonical Markdown → Markdown and image verification → `markdown_verified` → external Docs create or update → remote readback → `docs_verified`. When DOCX/Word/WPS is explicitly requested, derive and verify that optional artifact from the same frozen Markdown and record `word_verified`; this branch must not delay or block Docs publication. Never trade correctness for parallelism along either chain.

## Track where time is actually spent

Record these timestamps or durations when writing speed is under review:

- `first_complete_draft` — the whole article exists, with Unknowns visible;
- `editorially_ready` — evidence reconciliation, technical review, cold-read, and prose editing passed;
- `markdown_verified` — frozen canonical Markdown exists; the complete local image set when images are referenced is present; the exact Docs source exists; and a fresh passing style validation is bound to that source;
- `word_verified` — an explicitly requested DOCX/Word/WPS artifact and its render passed inspection; optional and not required before Docs;
- `docs_verified` — A3 creation and live readback passed.

Use the Skill's timing recorder instead of reconstructing durations from memory:

```bash
python3 scripts/track_writing_timing.py mark \
  --file "/absolute/release/writing-timing.json" \
  --event first_complete_draft \
  --json
```

Start with `started`, then record the required milestones through `markdown_verified`. From there, record `docs_verified` directly for the default Docs route; insert `word_verified` only for an explicitly requested Word-compatible artifact. Record `rework --reason <category>` and `tool_retry --reason <category>` when they materially add latency. The file measures stage timing and rework; it does not prove that the Skill caused an improvement.

Use `durations_seconds` for adjacent milestone durations and `elapsed_seconds` for total wall-clock time from `started` to the highest recorded milestone. The optional `--at` accepts a timezone-aware ISO timestamp for importing a trustworthy external event time; otherwise the tool records current UTC. Do not reconstruct precise durations from chat memory when this evidence is absent.

Compare the last three articles before adding an SLA. Until those measurements exist, describe this workflow as reducing repeated steps and exposing the first complete draft earlier; do not claim a measured wall-clock improvement. Optimize the stage that dominates elapsed time, and do not infer that drafting is the bottleneck when rendering, evidence access, or publication is actually waiting.

For structural rewrites, also record the editorial outcome: which load-bearing assets were kept, compressed, removed, or moved; whether reviewer repairs restored a lost scene, mechanism, counterforce, or next proof; and whether evidence caveats or action controls came to dominate the prose. Faster and shorter are useful only when these checks remain green.
