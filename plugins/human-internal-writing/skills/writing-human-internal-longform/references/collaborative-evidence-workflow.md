# Collaborative writing and claim-to-evidence workflow

Read this reference when the user wants section-by-section collaboration, when external research must support consequential claims, when an existing draft mixes sourced material with new connective reasoning, or when an audit must remain separate from revision.

## Select the operation mode

Name the mode before substantive work. A single article can move between modes, but each bounded operation has one mode.

| Mode | Use when | Default behavior |
|---|---|---|
| `EDIT` | Existing prose already carries the intended claim | Make the smallest sufficient change; expose substantive diffs and certainty shifts |
| `EXPAND` | Notes, an outline, or a gap needs new prose | Define the bounded claim, evidence, exclusions, and connection before drafting |
| `AUDIT` | The user asks for review, diagnosis, or readiness | Report findings and blockers without silently rewriting |

Grammar, punctuation, broken formatting, and other meaning-preserving corrections are low risk. Reordering, new causal bridges, new examples, new citations, terminology changes, and stronger or weaker claims are substantive: show them with a short rationale. Do not turn `AUDIT` into `EDIT` unless the user also asked for revision.

## Build the claim map only where it changes decisions

Use a compact CSV ledger for consequential factual, numeric, causal, technical, business-impact, or commitment claims. Ordinary connective prose and low-risk wording edits do not need IDs unless they introduce a new proposition.

Required columns:

```csv
claim_id,section,claim,state,risk,source_locator,source_version,verification_status,freshness_status,depends_on,notes
```

Use stable IDs such as `C001`. Separate multiple dependencies with commas.

| Field | Allowed or expected values |
|---|---|
| `state` | `sourced`, `observed`, `verified`, `inference`, `scenario`, `proposal`, `editorial`, `unknown` |
| `risk` | Prefer `low`, `medium`, `high`, or `critical` |
| `verification_status` | Prefer `verified`, `unverified`, or `not_required` |
| `freshness_status` | Prefer `current`, `immutable`, `stale`, `unknown`, or `not_applicable` |
| `source_locator` | Exact document, URL, file and line, dashboard panel, trace, meeting and timestamp, or other reproducible locator |
| `source_version` | Date, revision, content hash, commit, snapshot, or explicit empty value when unavailable |
| `depends_on` | Claim IDs that support an inference, scenario, proposal, or editorial bridge |

The ledger is a reasoning aid, not a substitute for reading the source. Search results, snippets, generated summaries, prior prose, and another article's bibliography are candidate evidence. Mark a claim verified only after opening the controlling source and checking that it supports the exact proposition, scope, and certainty.

For mutable sources, record what establishes freshness: retrieval time, accepted freshness window, snapshot, content hash, or version. `latest`, an unversioned dashboard, current organization data, live code, configuration, prices, schedules, and public web pages do not prove they were rechecked.

## Bound research before drafting

For each research gap, record:

- the claim or question to confirm or bound;
- what source type would be sufficient;
- the candidate sources found;
- the source actually opened and verified;
- the exact supported wording and unsupported extension;
- the stop condition for further search.

Stop when the central claims are supported, honestly bounded as inference/scenario/proposal, or exposed as material `Unknown`. Do not collect citations merely to make the bibliography look comprehensive.

## Collaborate section by section without fragmenting the article

When the user explicitly asks for section-by-section collaboration, that request overrides the default preference to expose the whole first draft before sentence polishing.

Before the first section:

1. Reverse-outline the whole article or proposed spine.
2. Identify the central judgment, load-bearing claims, and voice boundary.
3. Map the high-risk claims and research gaps.

At each section checkpoint, show a compact review envelope:

| Field | What to expose |
|---|---|
| Section and mode | The bounded section plus `EDIT`, `EXPAND`, or `AUDIT` |
| Proposed text or diff | A reviewable replacement, not an invisible rewrite |
| Claims changed | Claim IDs, additions, removals, and certainty changes |
| Sources used | Exact locators actually opened for this section |
| New reasoning | Inference, scenario, proposal, or editorial bridge added by the assistant |
| Author decisions | Choices that materially change stance, scope, terminology, or action |

An accepted section is provisionally accepted, not permanently frozen. Reopen it only when a later source conflict, claim change, terminology decision, or narrative dependency affects it; explain why. Do not repeatedly ask for approval on low-risk wording once the author has established a clear preference.

After the last section, read the whole article for causal continuity, duplicated conclusions, perspective, terminology, heading logic, and whether the ending resolves the opening tension.

## Run the evidence readiness gate

For serious factual or causal work, validate the ledger before claiming `Editorially ready`:

```bash
python3 scripts/check_evidence.py evidence.csv --require-ready --json
```

The checker validates structure and a small set of fail-closed relationships. It does not open sources, judge prose, prove truth, or replace technical review. A passing result means only that:

- source-bound claims have locators;
- high-risk source-bound claims are verified and current or immutable;
- high-risk reasoning names its claim dependencies;
- referenced claim IDs exist and are unique;
- no high-risk or critical `Unknown` remains in the proposed ready state.

Keep `Complete draft` available when blockers remain visible. Do not promote it to `Editorially ready` by deleting a difficult claim, downgrading its risk without reason, or marking a source verified without readback.
