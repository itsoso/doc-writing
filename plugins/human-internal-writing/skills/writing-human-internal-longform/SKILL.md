---
name: writing-human-internal-longform
description: Use when turning meeting notes, interviews, leadership viewpoints, or rough drafts into internal long-form writing, including all-hands letters, consensus documents, transformation articles, newcomer communications, or drafts that feel generic, templated, repetitive, over-polished, or weakly connected to action.
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

## Collect the five inputs

Identify these before drafting:

1. **Source** — transcripts, notes, drafts, links, or prior analyses.
2. **Author** — whose viewpoint the article must preserve; distinguish speakers when needed.
3. **Reader** — who will read it and what context they already have.
4. **Change** — what readers should understand, stop, start, or decide after reading.
5. **Form** — intended length, tone, channel, and required output files.

If the user provides several source documents, process all relevant material before writing. Do not infer that the latest or longest source is the most important.

## Follow the seven-stage workflow

### 1. Build an evidence ledger

Extract before composing. Use a compact working table when the material is large:

| Candidate claim | Source support | Status | Notes |
|---|---|---|---|
| Author's explicit judgment | Direct statement or repeated idea | Sourced | Preserve wording where useful |
| Consequence of that judgment | Supported connection | Inference | Mark internally; phrase with calibrated certainty |
| Helpful connective idea | Not present in source | Editorial | Include only if it improves comprehension without changing stance |

Record concrete examples, repeated phrases, causal claims, decisions, doubts, objections, and proposed actions. Flag conflicts rather than silently choosing one version.

### 2. Build a voice map

Write five short notes for internal use:

- What does the author notice that others may miss?
- What trade-off does the author resolve differently?
- What does the author repeatedly protect or reject?
- Which examples, metaphors, or terms genuinely belong to this author?
- Where is the author's confidence high, and where is it conditional?

Remove a phrase if any competent executive could have said it without changing its meaning. Keep distinctive judgments even when their wording is less polished.

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

### 5. Draft structure, then prose

Write a one-line function for each planned section. Check that each section advances the argument before expanding it.

Draft the complete article before polishing individual sentences. Let evidence lead to conclusions. Use concrete nouns and verbs before abstract management terms. Place examples where they change the reader's understanding, not in a separate “examples” container by default.

Allow natural asymmetry: an important section may be long, a transition may be one sentence, and not every argument needs three parallel points.

### 6. Run the de-templating pass

Edit for thought, not cosmetic irregularity:

- Delete repeated labels such as “一句话带走” when the judgment can stand by itself.
- Replace empty transitions with the actual logical relationship.
- Break mechanical “首先、其次、再次、最后” sequences unless order matters.
- Remove duplicate summaries that add no new implication.
- Replace abstract clusters with a user, object, event, constraint, owner, or observable result.
- Vary paragraph length only when the reasoning requires it; never add randomness for appearance.
- Keep bilingual product or technical terms when they are natural to the author and audience.
- Prefer one precise claim over a polished paragraph containing three weak claims.

Read [references/quality-rubric.md](references/quality-rubric.md) before the final editorial pass.

For a deterministic second opinion, run:

```bash
python3 scripts/check_draft.py <draft.md> --max-findings 8
```

Treat every result as a prompt for human review. The script is not a score, proof of quality, or AI-authorship detector. Fix the reasoning when a finding is valid; do not rewrite merely to silence a rule.

### 7. Cold-read and release

Read the draft once without the source material and answer:

1. Can a reader state why this article exists after the opening?
2. Can they identify at least one judgment that belongs specifically to the author?
3. Does each major conclusion follow from evidence, experience, or a stated inference?
4. Are counterforces, costs, or risks represented fairly?
5. Is the requested action concrete enough to begin?
6. Does the ending resolve the article's central tension rather than repeat the introduction?

Then compare the draft with the evidence ledger. Restore any important source nuance lost during editing. Remove any confident claim that cannot be traced.

## Use the worked example selectively

Read [references/worked-example.md](references/worked-example.md) when source notes are fragmented, when the user asks to “remove AI flavor,” or when the distinction between polishing and preserving a viewpoint is unclear. Do not copy its wording or structure into unrelated articles.

## Deliver the result

Lead with the finished article when the user asks for a draft, not a long explanation of the workflow. Provide a short editorial note only when it helps the user evaluate material assumptions, inferred connections, or unresolved source conflicts.

When files are requested, keep the editable source and the release artifact aligned. Verify layout separately when generating DOCX or PDF; this Skill governs editorial quality, not file-format rendering.

## Stop conditions

Do not declare the article ready when any of these remain:

- the central judgment could belong to anyone;
- important claims cannot be traced to source or marked inference;
- the reader is asked to “act” without a first step or responsibility boundary;
- risks are absent from a consequential proposal;
- the draft passes a checker only because valid ideas were removed;
- confidential content has leaked into reusable plugin resources.
