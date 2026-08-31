---
name: writing-human-internal-longform
description: Use when turning meeting notes, interviews, leadership viewpoints, rough drafts, technical evidence, or multi-entry collections into internal long-form, all-hands, consensus, performance, architecture, incident, tutorial, article index, column homepage, or knowledge hub content, especially when claims, causal reasoning, author voice, evidence boundaries, system coherence, entry clarity, action, or repetitive AI-like phrasing need editorial control.
---

# Writing Human Internal Longform

## Core principle

Preserve the author's actual mind, not merely the topic. A strong internal article lets readers recognize what this person noticed, how they judge trade-offs, where they remain uncertain, and what they want the organization to do next.

Treat “less AI-like” as an editorial-quality request. Never claim to evade AI detection or disguise authorship.

## Protect editorial integrity

- Separate sourced statements, reasonable inference, and editorial additions.
- Never invent quotations, numbers, meetings, personal experiences, dissent, or certainty.
- Preserve meaningful tension. Do not smooth every contradiction into generic agreement.
- Ask only when a missing answer would materially change the article. Otherwise state the assumption and continue.
- Keep confidential source material in the authorized workspace. Do not copy internal source content into reusable examples.

## Do not use the full workflow

Do not activate the seven-stage pass for a one-line rewrite, literal translation, simple summary with no authorial reconstruction, metadata correction, or formatting-only repair. Handle the bounded request directly, preserving facts and scope. If the work is only DOCX/Docs packaging or visual repair, route to `publishing-kstack-articles`; load this Skill only when prose, claims, structure, or author voice also changes.

## Collect the five inputs

Identify these before drafting:

1. **Source** — transcripts, notes, drafts, links, or prior analyses.
2. **Author** — whose viewpoint the article must preserve; distinguish speakers when needed.
3. **Reader** — who will read it and what context they already have.
4. **Change** — what readers should understand, stop, start, or decide after reading.
5. **Form** — intended length, tone, channel, and required output files.

If the user provides several source documents, process all relevant material before writing. Do not infer that the latest or longest source is the most important.

## Use Onepoint only for Kuaishou-internal requests

The writing method in this Skill is general and does not require Onepoint. Read [references/onepoint-kuaishou.md](references/onepoint-kuaishou.md) only when the user explicitly provides a Kuaishou Onepoint meeting link, asks to retrieve a meeting from Onepoint, or clearly identifies the task as Kuaishou-internal.

Do not load or apply that reference to generic meeting notes, external organizations, or unrelated products named Onepoint. If the internal CLI, network, login, or meeting permission is unavailable, ask for an authorized transcript or export and continue with the general workflow. Never bypass access controls.

## Choose the operation mode, change mode, and terminal state

Select one operation mode for each bounded unit, one change mode for the article, and one terminal state. Do not confuse the kind of work, how much the article changes, or how far delivery must proceed. None permits invented facts, hidden uncertainty, or skipped evidence boundaries.

**Operation mode**

- **`EDIT`** — existing prose carries the intended claim; make the smallest sufficient change and expose substantive diffs, new claims, and certainty shifts.
- **`EXPAND`** — notes, an outline, or a gap needs new prose; define what the bounded unit must claim, must not claim, and still lacks before drafting.
- **`AUDIT`** — review evidence, voice, argument, or readiness without silently rewriting. Switch to `EDIT` only when revision is also in scope.

**Change mode**

- **Focused edit** — an existing article needs a bounded section, claim, title, or wording change. Determine the change's evidence and narrative blast radius, then reuse unchanged work.
- **Structural rewrite** — an existing article needs a new narrative spine, substantial compression, audience shift, or removal of major branches. Reuse still-valid evidence, but classify the old draft's load-bearing narrative assets before cutting so shorter does not become flatter or less explanatory.
- **New draft** — no adequate article exists. Build the minimum sufficient brief, write the whole article, and expose unresolved items as `Unknown` or visible TODOs rather than waiting indefinitely or filling gaps.

**Terminal state**

- **Complete draft** — the whole readable article exists and material Unknowns or TODOs are visible; formal review and release work may still remain.
- **Editorially ready** — evidence reconciliation, required editorial or technical review, revision, global checker, and cold-read have passed; stop without release artifacts unless the project requires them.
- **Verified release** — use `markdown_verified` as the required release base, then continue to the default `docs_verified` terminal state when company Docs publication is in scope. Record `word_verified` only when the user explicitly requests DOCX/Word/WPS; it is an optional branch and never a prerequisite for `docs_verified`. A complete draft remains an intermediate milestone.

Read [references/fast-writing-workflow.md](references/fast-writing-workflow.md) when speed matters, a revision changes factual or technical claims, or three or more independent sources are in scope. It defines safe reuse, parallel extraction, stopping rules, and latency checkpoints. A purely cosmetic edit may use the focused lane without loading this reference.

Read [references/collaborative-evidence-workflow.md](references/collaborative-evidence-workflow.md) when the user asks to work section by section, external research supports consequential claims, new connective reasoning is needed, or an audit must remain separate from revision. It defines the review envelope, Claim–Evidence IDs, source verification boundary, and optional mechanical readiness gate.

Read [references/index-and-hub-editorial-mode.md](references/index-and-hub-editorial-mode.md) when creating, restructuring, or auditing an article index, column homepage, knowledge hub, or other multi-entry landing page. These artifacts need a system boundary, entry map, first-screen explanation, and global coherence pass in addition to accurate local copy and links.

Read [references/pairwise-article-evaluation.md](references/pairwise-article-evaluation.md) when comparing an old and new article, validating a Skill revision against recent real articles, or scoring aesthetics, document quality, reliability, and reader usefulness. Keep versions blinded during the first pass and do not let a numeric average override a failed truth gate.

For a focused edit, do not mechanically recreate the full evidence ledger, voice map, reader-change statement, outline, or review record. Reuse an item only when its source locator, version or content fingerprint, freshness requirement, claim scope, and article function remain valid. Re-open the full article once for coherence and run the global checker after the edit, but distinguish pre-existing warnings from regressions introduced by the change.

For a structural rewrite, read the prior article once as an argument before optimizing its length. Use the preservation map in [references/fast-writing-workflow.md](references/fast-writing-workflow.md) to distinguish repetition and distant branches from source-backed scenes, mechanisms, counterforces, and decisive details. Rebuild the spine, but do not silently discard every concrete source moment or mechanism that made the central judgment credible.

For a new draft, combine the evidence ledger, voice map, reader change, narrative spine, and section functions into one compact article brief. Expand any high-risk numeric, causal, architecture, incident, performance, or business claim into the detailed technical ledger before stating a conclusion.

Do not wait for DOCX generation, page rendering, or company Docs creation before making a complete first draft available when the user asked to see the draft. In a full-delivery task this is a progress milestone, not completion: continue to the requested verified terminal state unless the user asked for draft-only delivery.

## Follow the seven-stage full pass

Use the full pass for a new draft or structural rewrite. For a focused edit, apply it only to the affected slice, then perform the required full-document coherence checks. Reuse unaffected outputs as described above.

### 1. Build an evidence ledger

Extract before composing. Use a compact working table when the material is large or the claim is high-risk:

| Candidate claim | Source support | Status | Notes |
|---|---|---|---|
| Author's explicit judgment | Direct statement or repeated idea | Sourced | Preserve wording where useful |
| Consequence of that judgment | Supported connection | Inference | Mark internally; phrase with calibrated certainty |
| Helpful connective idea | Not present in source | Editorial | Include only if it improves comprehension without changing stance |

Record concrete examples, repeated phrases, causal claims, decisions, doubts, objections, and proposed actions. Flag conflicts rather than silently choosing one version.

For consequential factual, numeric, causal, technical, business-impact, or commitment claims, assign stable IDs such as `C001` when the map will be reused, reviewed, or mechanically checked. Record the exact reader-facing claim, source locator and version, evidence state, risk, verification and freshness state, dependencies, and article section. Search results, snippets, generated summaries, prior prose, and another article's bibliography are candidate evidence until the controlling source is opened and matched to the exact proposition.

When the article makes claims about code, architecture, performance, incidents, experiments, technical operations, or engineering decisions, read [references/technical-article-mode.md](references/technical-article-mode.md). Select the article's primary technical mode, extend the ledger with `Verified`, `Observed`, `Inference`, `Scenario`, `Proposal`, and `Unknown`, and establish ground truth before drafting conclusions.

### 2. Build a voice map

Write five short notes for internal use:

- What does the author notice that others may miss?
- What trade-off does the author resolve differently?
- What does the author repeatedly protect or reject?
- Which examples, metaphors, or terms genuinely belong to this author?
- Where is the author's confidence high, and where is it conditional?

Remove a phrase if any competent executive could have said it without changing its meaning. Keep distinctive judgments even when their wording is less polished.

Do not invent first-person reflection to create a voice. Distinctiveness comes from the author's value ordering, trade-offs, confidence boundaries, and recurring observations—not from fabricated intimacy, quirks, or roughness.

### 3. Define the reader change

Complete these sentences before choosing headings:

- Readers currently believe or do: …
- After reading, they should understand: …
- They should stop: …
- They should start: …
- The first practical entry point is: …

Do not confuse “everyone agrees” with a useful outcome. Unified cognition should enable coordinated but context-sensitive action.

### 4. Choose a narrative spine

Choose the smallest structure that carries the author's reasoning. Do not force every article into the same outline.

| Source condition | Prefer this spine |
|---|---|
| Questions from newcomers or the field reveal a larger shift | Questions → system judgment → practice → risks → action |
| A decision needs explanation | Context → options → trade-off → decision → implications |
| A failure produced a lesson | Event → mistaken assumption → evidence → revised model → next experiment |
| A strategy needs mobilization | Why now → destination → operating principles → concrete arenas → commitments |
| Existing draft is accurate but flat | Central tension → strongest evidence → author's judgment → consequence |

Use headings to expose reasoning, not to decorate every few paragraphs.

Choose what the evidence can support, not the structure that looks most complete. Thin material may justify one diagnosis and one next experiment; do not automatically inflate it into a comprehensive framework, fixed-period roadmap, or organization-wide program.

### 5. Draft structure, then prose

Write a one-line function for each planned section. Check that each section advances the argument before expanding it.

Draft the complete article before polishing individual sentences. Let evidence lead to conclusions. Use concrete nouns and verbs before abstract management terms. Place examples where they change the reader's understanding, not in a separate “examples” container by default.

When the user explicitly requests section-by-section collaboration, first reverse-outline the whole article and map its central judgment and high-risk claims, then work one bounded section at a time. At each checkpoint expose the proposed text or diff, Claim IDs changed, sources actually opened, new inference/editorial bridges, certainty shifts, and material author decisions. Acceptance is provisional: reopen an accepted section only when a later dependency or source conflict affects it, and state why. After the last section, perform the same full-document coherence read required for a whole-draft pass.

At the end of this stage, a new-article task has its first complete draft. If early visibility was requested, present that complete draft with only material `Unknown` or TODO items called out; do not describe it as editorially ready, locally verified, or published.

Allow natural asymmetry: an important section may be long, a transition may be one sentence, and not every argument needs three parallel points.

### 6. Run the de-templating pass

Edit for thought, not cosmetic irregularity. Read [references/de-ai-editing.md](references/de-ai-editing.md) when the user asks to remove AI flavor, when the prose is highly polished but generic, or when repeated rhetorical patterns are carrying the argument.

At minimum:

- Delete repeated labels such as “一句话带走” when the judgment can stand by itself.
- Replace empty transitions with the actual logical relationship.
- Break mechanical “首先、其次、再次、最后” sequences unless order matters.
- Keep “不是……而是……” for a decisive contrast; if it recurs, replace the weaker instances with evidence, mechanism, consequence, or a direct decision.
- Remove duplicate summaries that add no new implication.
- Replace abstract clusters with a user, object, event, constraint, owner, or observable result.
- Remove invented first-person certainty, fake quotations, and decorative specificity. A detail must change the diagnosis, causal model, trade-off, action boundary, or confidence level.
- Prefer the smallest action supported by the source. Label editorial proposals as proposals instead of blending them into the author's prior commitments.
- After substantial compression, compare the old and new argument. If the source contains them, retain the smallest sufficient set of load-bearing assets: a concrete scene or observed failure, the mechanism that connects it to the judgment, a real counterforce or cost, and the next proof. These are functions, not mandatory section headings or quotas.
- Translate evidence state into reader language. Keep limitations adjacent to consequential claims, but consolidate repeated caveats about the same source. Do not let `Observed`, `Proposal`, `Unknown`, “尚未验证,” or release metadata become the dominant narrative voice.
- Preserve narrative perspective. When the source and article speak in the author's first person, do not switch to “the author says/provided” merely to signal provenance; attribute third-party material separately and keep the evidence record outside the prose.
- Match action depth to evidence and risk. Usually expand one smallest reversible next proof. Use multi-stage gates only when the source supports real dependencies or when external state, safety, or irreversible consequences require staged control. Do not turn every recommendation into a roadmap.
- Vary paragraph length only when the reasoning requires it; never add randomness for appearance.
- Keep bilingual product or technical terms when they are natural to the author and audience.
- Prefer one precise claim over a polished paragraph containing three weak claims.

Read [references/quality-rubric.md](references/quality-rubric.md) before the final editorial pass.

For a deterministic second opinion, run:

```bash
python3 scripts/check_draft.py <draft.md> --max-findings 8
```

When `Form` is a formal article or publication target, activate the masthead contract explicitly:

```bash
python3 scripts/check_draft.py <draft.md> --formal --max-findings 8
```

`--formal` requires an independent H1, subtitle, and exact publication date. Omit it for discussion notes, working drafts, and other non-publication forms; those documents must not fail merely because they have no publication masthead.

For a technical article, enable the additional warnings:

```bash
python3 scripts/check_draft.py <draft.md> --technical --max-findings 8
```

For a focused revision, compare only regressions introduced by the current draft while preserving the full finding list for context:

```bash
python3 scripts/check_draft.py <draft.md> \
  --baseline <previous-draft.md> \
  --technical \
  --json \
  --max-findings 0
```

`--baseline` suppresses only a matching rule, severity, and evidence fingerprint from the failure threshold. It does not approve the older finding, hide it from JSON, or excuse blockers in a new article.

Treat every result as a prompt for human review. The script is not a score, proof of quality, or AI-authorship detector. Fix the reasoning when a finding is valid; do not rewrite merely to silence a rule.

### 7. Cold-read and release

Read the draft once without the source material and answer:

1. Can a reader state why this article exists after the opening?
2. Can they identify at least one judgment that belongs specifically to the author?
3. Does each major conclusion follow from evidence, experience, or a stated inference?
4. Are counterforces, costs, or risks represented fairly?
5. Is the requested action concrete enough to begin?
6. Does the ending resolve the article's central tension rather than repeat the introduction?
7. If the source contained a decisive scene, mechanism, or counterforce, did compression preserve enough of it for the judgment to feel earned?
8. Are evidence boundaries readable as part of the argument, rather than repeated audit labels or editorial notes?
9. Is the action plan no deeper than the evidence and risk require?

Then compare the draft with the evidence ledger. Restore any important source nuance lost during editing. Remove any confident claim that cannot be traced.

For a technical article, read [references/technical-review.md](references/technical-review.md) and complete a review-only pass before revising. Check technical truth, reproducibility, evidence boundaries, and argument in that order. Do not let prose polish repair or conceal an unsupported mechanism.

After review-driven revision, recheck the changed claims and their dependents, then rerun the global deterministic checker and cold-read the article for coherence. A review finding does not require repeating unrelated source extraction or rebuilding unchanged planning artifacts.

When a reusable claim ledger exists and the task targets `Editorially ready`, run its structural readiness gate:

```bash
python3 scripts/check_evidence.py <evidence.csv> --require-ready --json
```

This check does not read sources or prove truth. Use it to catch missing locators, unverified or stale high-risk evidence, unbound high-risk reasoning, broken Claim ID dependencies, and material Unknowns. A passing ledger cannot compensate for a failed source readback, technical review, quality gate, or cold-read.

## Use the worked example selectively

Read [references/worked-example.md](references/worked-example.md) when source notes are fragmented, when the user asks to “remove AI flavor,” or when the distinction between polishing and preserving a viewpoint is unclear. Do not copy its wording or structure into unrelated articles.

## Apply editorial and typography rules at the right layer

When `Form` is a formal article, a formatted file, or a publication target, read [references/editorial-and-typography.md](references/editorial-and-typography.md) before choosing styles. Treat its values as a professional fallback, not as a substitute for an explicit brand template, an accepted earlier edition, accessibility requirements, or target-channel constraints.

### Preserve the formal three-line masthead and exact date

For a formal article, default to three separate visual lines:

```markdown
# Main title

> Subtitle

2099 年 4 月 5 日
```

The H1 must not contain the subtitle, date, or `｜`. The main title carries the central judgment; the subtitle adds a distinct conflict, scope, or consequence; the date remains quiet metadata. These are three separate visual lines in Markdown, rendered artifacts, and online Docs.

Use `YYYY 年 M 月 D 日`, not a year-month value. Resolve an unspecified publication date in the user's configured publication timezone, defaulting to `Asia/Shanghai`. The timezone is calculation context only and must not appear in the visible masthead, cover date, document title, or index label. Render only the date, never a timezone suffix such as `北京时间`, `UTC+8`, or `Asia/Shanghai`.

Keep three layers distinct:

- **Semantic source** — Markdown carries title hierarchy, paragraphs, lists, links, image references, alt text, and captions. Do not simulate layout with manual spaces, repeated blank lines, HTML font tags, or page-break padding.
- **Editorial form** — paragraph length, heading density, emphasis, terminology, numbers, and punctuation follow the reasoning and reader needs.
- **Delivery styling** — fonts, point sizes, spacing, margins, pagination, headers, and image placement belong to the DOCX, HTML, or Docs renderer and must be verified in the actual target.

Do not claim a font or layout is correct merely because a style name was written into a generator. Confirm font availability or fallback, render every page, and inspect the output. Online Docs is reflowable: prefer native styles and let the publishing workflow own its page/view model instead of forcing local DOCX geometry into it.

For KStack Docs, keep the accepted profiles distinct: a standard formal article centers H1, subtitle, and publication date while keeping every lower heading and body role left aligned; an article index or knowledge hub centers only H1, with subtitle, date, every lower heading, navigation, and body role left aligned. Do not copy the formal-article masthead alignment into the index profile.

## Deliver the result

Lead with the finished article when the user asks for a draft, not a long explanation of the workflow. Provide a short editorial note only when it helps the user evaluate material assumptions, inferred connections, or unresolved source conflicts.

When DOCX/Word/WPS compatibility, rendered artifacts, a release package, company Docs publication, or a project-mandated release terminal state is in scope, **REQUIRED SUB-SKILL:** use `publishing-kstack-articles`. A chat draft or canonical Markdown file alone does not trigger release generation when the user or project explicitly limits the task to draft-only or no-publication work. This Skill governs editorial quality and cannot by itself claim that release artifacts or remote publication are complete.

When both Skills apply, load each once and assign ownership: this Skill freezes the canonical Markdown and evidence boundaries; `publishing-kstack-articles` derives and verifies release artifacts. Do not recursively restart either workflow merely because they reference one another.

## Stop conditions

Do not declare the article ready when any of these remain:

- the central judgment could belong to anyone;
- important claims cannot be traced to source or marked inference;
- a high-risk sourced claim is unverified or stale, a high-risk inference/editorial bridge has no supporting Claim ID, or a material Unknown still changes the central judgment;
- the reader is asked to “act” without a first step or responsibility boundary;
- risks are absent from a consequential proposal;
- a technical claim presents plausible architecture, code, command output, performance impact, or business impact as verified when its source or run is missing;
- the draft passes a checker only because valid ideas were removed;
- the evidence ledger passes only because risk, state, freshness, or verification fields were weakened without a corresponding source readback;
- a shorter rewrite has removed all source-backed scenes, mechanisms, or counterforces that carried the central judgment;
- provenance labels, caveats, version notes, or release metadata dominate the reader-facing prose;
- an editorial suggestion has been promoted into a confirmed sequence of gates, dependencies, owners, or commitments without source support;
- an article index, column homepage, or knowledge hub has valid local sections and links but its first screen does not explain why the entries belong to one system or how a reader should choose an entry;
- confidential content has leaked into reusable plugin resources.
