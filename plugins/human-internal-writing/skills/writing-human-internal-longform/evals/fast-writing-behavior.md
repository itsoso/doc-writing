# Fast-writing behavior evaluations

These evaluations cover the version 0.3.0 speed failures and version 0.3.1 workflow changes. They use synthetic scenarios and measure decision steps and delivery checkpoints, not wall-clock time or prose taste.

## Evaluation 1: one-section metric revision

### Scenario

An existing, previously reviewed technical article contains a `100ms` sensitivity scenario. One new reliable source changes only that scenario's applicable population. The user asks for the revised readable draft quickly and explicitly says not to publish yet.

### RED with version 0.3.0

The evaluator found no explicit incremental lane and enumerated a full evidence ledger, five-item voice map, five-item reader change, narrative spine, section-function plan, reverse outline, claim audit, rhetoric inventory, and full technical review. The global checker also surfaced eight pre-existing warnings outside the changed section without a rule for distinguishing them from regressions.

Failure: the Skill preserved rigor but did not define evidence reuse, invalidation radius, or a user-visible complete-draft checkpoint.

### GREEN with version 0.3.1

- Choose `Focused edit`.
- Compare the new source with the prior claim and mark only that claim, its calculation, and direct narrative dependents as `recheck` or `invalidate`.
- Reuse unchanged evidence, voice, reader-change, outline, and image inventory.
- Produce the complete revised draft before any release work.
- Run changed-claim review plus a full coherence read and global checker; report pre-existing findings separately from new regressions.
- Do not generate DOCX or write to company Docs because publication is out of scope.

The evaluator followed this route, retained the external-coefficient evidence boundary, kept the full-document checker and coherence read, and separated eight pre-existing warnings from change regressions. The pre-draft planning contract changed from multiple full-article artifacts to one evidence blast-radius classification for the changed slice. Result: workflow pass; no wall-clock claim.

## Evaluation 2: four-source new technical article with full delivery

### Scenario

Four independent reliable sources support a new 1,200-word technical article. The user wants to see a complete draft quickly, while the project ultimately requires Markdown, DOCX, rendered-page verification, and company Docs A3 publication.

### RED with version 0.3.0

The evaluator found that `process all relevant material before writing` did not explicitly permit parallel extraction. It placed the first conservative user-visible handoff after de-templating, cold-read, review-only technical review, and revision because version 0.3.0 had no delivery checkpoint after stage 5.

Failure: the workflow left safe parallelism and the distinction between `first_complete_draft` and `docs_verified` implicit.

### GREEN with version 0.3.1

- Choose `Verified release`, with `Complete first draft` as an intermediate milestone.
- Extract the four independent sources in parallel when delegation is available, using one shared evidence schema; merge conflicts before prose.
- Build one compact article brief rather than four polished planning artifacts.
- Present the whole draft when stage 5 ends, with material Unknowns visible; do not claim editorial or release completion.
- Continue with technical review, canonical Markdown freeze, the explicitly requested DOCX, render, visual review, `word_verified`, A3 Docs creation, and live readback.
- Parallelize image inventory, dependency checks, and read-only target resolution, but keep the hash-dependent release chain sequential.

The evaluator exposed the complete draft at stage 5 instead of after stages 6 and 7, preserved a single writer for voice and causal synthesis, prohibited stale DOCX generation, and retained A3 plus live readback as final publication gates. Result: workflow pass; no wall-clock claim.

## Regression expectations

Future versions fail these evaluations when they:

- weaken claim traceability or hide Unknowns to produce a faster draft;
- treat an early draft as `markdown_verified`, `word_verified`, or `docs_verified`;
- regenerate unchanged planning artifacts without a stated reason;
- let multiple extractors draft separate article sections or fragment author voice;
- reuse evidence after its source version, claim strength, scope, inputs, or conflicts changed;
- generate DOCX, renders, or receipts from a source that is still changing;
- publish without the A3 page model or without live readback.

## Measurement status

Version 0.3.1 has demonstrated fewer mandatory planning artifacts for the focused-edit scenario, an earlier explicit first-draft checkpoint for the four-source scenario, and preserved quality/release gates. It has not yet demonstrated a real elapsed-time improvement. Record the four workflow timestamps for the next three articles before setting an SLA or claiming a percentage speedup.
