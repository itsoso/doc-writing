# Internal long-form quality rubric

Use this rubric for the final editorial pass. It is a set of gates, not a numeric score. A draft is not ready if any gate fails materially. For technical articles, Gate 6 is mandatory in addition to the first five gates. Gate 7 applies when the workflow created a reusable Claim–Evidence ledger for consequential claims. Gate 8 checks reader consequence for every substantive article. Gate 9 applies to an article index, column homepage, knowledge hub, or another multi-entry landing page.

## 1. Source fidelity

### Pass when

- The author's important claims, examples, uncertainty, and priorities are represented.
- Factual statements and quotations can be traced to source.
- Inference is calibrated with language such as “这意味着”“我的理解是” or an equivalent appropriate to the voice.
- Editorial connective material clarifies the argument without becoming a new attributed viewpoint.

### Failure symptoms

- A fluent claim has no source support.
- Several speakers have been merged into one voice.
- Conditional language in the source became certainty in the article.
- A memorable phrase was invented and presented as the author's own.

### Repair

Return to the evidence ledger. Mark each contested sentence as sourced, inferred, editorial, or unsupported. Remove unsupported claims; qualify inference; restore meaningful source language.

## 2. Voice distinctiveness

### Pass when

- A colleague familiar with the author can recognize the author's value ordering and way of resolving trade-offs.
- The article contains at least one non-obvious judgment, not merely a list of accepted principles.
- Characteristic terminology is used consistently and only where it carries meaning.
- Tension remains visible: speed and risk, depth and breadth, individual agency and organizational support, or the actual tension in the source.
- Distinctiveness comes from the author's value ordering and confidence boundaries, not from invented first-person intimacy or mannerisms.
- When the source contains a concrete moment that changed the author's judgment, the final article preserves enough of that moment to keep the voice grounded.
- Narrative perspective remains coherent: a first-person author article does not drift into “the author says/provided” unless a genuinely different source requires attribution.

### Failure symptoms

- The draft could be attributed to any leader or any company.
- Every section ends with the same uplifting cadence.
- The article sounds more certain, inspirational, or comprehensive than the source.
- Editing replaced specific discomfort with generic optimism.
- Compression retained the conclusion but removed every source-backed scene, observed failure, or uncomfortable choice that made it recognizably this author's judgment.
- Provenance language turns the author into a third party inside their own article.

### Repair

Re-open the voice map. Restore the author's decisive contrast, protected value, concrete example, and boundary. Delete sentences that only signal importance.

## 3. Argumentative traceability

### Pass when

- The opening establishes a real problem or tension.
- Each major section answers a question created by the previous section.
- Conclusions follow from examples, evidence, experience, or an explicit assumption.
- Headings expose the reasoning path and remain useful when read alone.
- The scope matches the evidence; the draft does not manufacture completeness by expanding a narrow observation into a full framework or roadmap.
- A structural rewrite preserves the smallest sufficient causal path from observation or evidence through mechanism or trade-off to consequence and next proof.

### Failure symptoms

- Sections are individually plausible but interchangeable.
- The article jumps from a trend to a prescription without a causal bridge.
- Lists accumulate concepts without establishing priority.
- A conclusion appears in the introduction and is repeated rather than earned.
- Several sections use the same binary contrast, three-part list, or uplifting cadence instead of different reasoning functions.
- A shorter draft consists mostly of conclusions and controls because the mechanism, counterforce, or decisive detail was cut with the repetition.

### Repair

Write one sentence describing the function of each section. Remove or merge sections that perform the same function. Add the missing causal bridge, not a generic transition.

## 4. Concrete action

### Pass when

- Readers know what should change after reading.
- The first action has an owner, arena, boundary, or observable result.
- The article distinguishes immediate practice from longer-term direction.
- Evaluation, feedback, or review is present when the action involves learning.
- Editorial proposals are distinguishable from actions already stated or committed by the author.
- Action depth matches the evidence and risk: one reversible next proof is preferred unless real dependencies, external state, safety, or irreversible consequences justify staged gates.

### Failure symptoms

- The ending asks everyone to “embrace,” “strengthen,” or “promote” something without a starting point.
- Actions are detached from normal work and read like an additional campaign.
- Success is defined only by tool use, activity volume, or another input metric.
- No one can tell when the proposed experiment should stop or change.
- Thin source material has been inflated into a comprehensive governance plan with invented owners, thresholds, or timelines.
- A recommendation has become a multi-stage gate sequence even though the source supports only one bounded experiment or next proof.

### Repair

Name the first practice, the people closest to it, the feedback source, and the next decision. Replace input metrics with impact and learning signals.

## 5. Restrained readability

### Pass when

- Paragraph length follows the thought rather than a visual template.
- Concrete language balances necessary abstractions.
- Repetition is deliberate and carries increasing meaning.
- Lists are used for real enumeration; prose carries argument and movement.
- The conclusion resolves the central tension in fresh language.
- Concrete details change the diagnosis, causal model, trade-off, action boundary, or confidence level rather than merely decorating the prose.
- Evidence limitations stay close to consequential claims without making audit labels or repeated caveats the dominant cadence.
- Version provenance, image history, release mechanics, and other editorial metadata live outside the reader-facing argument unless they materially affect interpretation.

### Failure symptoms

- “首先、其次、再次、最后” appears whenever a paragraph needs momentum.
- Repeated labels announce conclusions that the prose has already made clear.
- Several abstract nouns appear without a person, system, event, constraint, or decision.
- Every section has the same size, cadence, and ending.
- The text uses synonyms to repeat one idea.
- “不是……而是……”“真正的”“本质上” or repeated bold slogans carry multiple conclusions without adding evidence or mechanism.
- Nearly every paragraph repeats “不能证明、尚未验证、候选、不是承诺” even when the same evidence boundary could be stated once without weakening it.
- The article exposes working labels such as `Observed`, `Proposal`, or `Unknown`, or publication notes, where natural reader-facing attribution would preserve the same truth.

### Repair

Read aloud. Cut throat-clearing and duplicated endings. Replace one abstract sentence per section with a concrete object or consequence. Keep asymmetry when it reflects the argument.

## 6. Technical integrity

### Pass when

- Consequential technical claims are marked and traceable as verified, observed, inferred, scenario, proposal, or Unknown.
- Current code, configuration, tests, runs, traces, experiments, or authoritative sources support the stated mechanism and scope.
- Commands and code examples disclose execution status, environment, and expected or actual result where readers may rely on them.
- Performance and business-impact numbers name their metric, baseline, sample, time window, affected scope, formula, and assumption boundary.
- External benchmarks remain external; plans and diagrams remain design evidence rather than proof of deployed behavior.

### Failure symptoms

- A technically plausible mechanism was added because a mature design would normally include it.
- Absolute reliability, performance, or business claims rest on a diagram, screenshot, plan, or single observation.
- An external `100ms` coefficient is multiplied across all internal GMV and reported as incurred loss.
- A code block or command is presented as runnable or verified without a real execution or explicit `未验证` state.
- A fixed-period roadmap invents owners, thresholds, dates, or commitments not present in the source.

### Repair

Read [technical-article-mode.md](technical-article-mode.md). Rebuild the claim-to-evidence mapping, reduce each conclusion to the scope the evidence supports, and move missing mechanisms or actions into questions, scenarios, or proposals. Then run the read-only process in [technical-review.md](technical-review.md).

## 7. Evidence readiness when a claim ledger exists

### Pass when

- Claim IDs are unique, stable, and referenced by dependent high-risk reasoning.
- Sourced, observed, or verified claims have reproducible locators.
- High-risk source-bound claims were read back and are current or explicitly immutable.
- High-risk inference, scenario, proposal, or editorial connective reasoning names the claims it depends on.
- No high-risk or critical `Unknown` still controls the central judgment or requested action.
- Mechanical validation and human source review agree; neither is presented as a substitute for the other.

### Failure symptoms

- A search snippet, generated summary, old draft, or bibliography entry is marked verified without opening the controlling source.
- `latest`, an unversioned dashboard, or an old organization/code snapshot is treated as current without a freshness record.
- A causal bridge has fluent prose but no supporting Claim ID.
- The ledger passes only because a claim was downgraded, removed, or relabeled rather than resolved.

### Repair

Read [collaborative-evidence-workflow.md](collaborative-evidence-workflow.md). Reopen the controlling source, correct the claim map, and run:

```bash
python3 scripts/check_evidence.py evidence.csv --require-ready --json
```

The command checks structure and fail-closed relationships only. It does not certify factual correctness, citation quality, editorial quality, or publication readiness.

## 8. Reader consequence

### Pass when

- A target reader can state what changed in their understanding after reading.
- The article improves a real decision, practice, or next experiment rather than only signaling importance.
- The first practical move is proportional to the evidence and can be recognized when completed.
- At least one likely reader objection or cost is answered where it affects the decision.

### Failure symptoms

- The reader agrees with the theme but cannot say what to do differently.
- The article repeats familiar principles without a new mechanism, trade-off, or proof.
- The next step exists only as a slogan, comprehensive roadmap, or activity metric.
- The piece optimizes for author completeness while making the reader carry unnecessary provenance and process detail.

### Repair

Ask one target reader to explain the judgment and smallest next proof without looking back at the article. Repair the missing causal bridge or action boundary. For version comparisons, use [pairwise-article-evaluation.md](pairwise-article-evaluation.md) and keep human feedback distinct from model-generated diagnostics.

## 9. Index/Hub global coherence

### Pass when

- The first screen states the collection's purpose, system boundary, shared result, and supported relationship model before updates or the full inventory take over.
- A target reader can explain why the entries belong to one system and choose a first useful route from their question or desired outcome.
- Every entry has a distinct role; overlaps, handoffs, ordering, and abstraction-level changes are intelligible rather than accidental.
- Link labels, descriptions, dates, status, and canonical terminology agree with the entry target and the first-screen model.
- Durable navigation is separate from current updates, version history, and release metadata.

### Failure symptoms

- Locally polished sections and working links form a list of parallel topics, but the first screen never explains the whole.
- A reader can repeat the umbrella theme but cannot choose an entry; entry clarity depends on opening several links.
- Product surfaces, organization names, mechanisms, and business outcomes appear as peers without a bridge between levels.
- Two summaries are interchangeable, one role appears under several names, or updates contradict the durable route.
- A causal chain or loop was invented to make unrelated material appear coherent.

### Repair

Read [index-and-hub-editorial-mode.md](index-and-hub-editorial-mode.md). Rebuild the system boundary and entry map, write the smallest supported first-screen explanation, then run the first-screen-only and headings-and-entries-only global coherence passes. Validate links and target state separately; neither semantic coherence nor link correctness substitutes for the other.

## Release decision

Use three outcomes:

- **Ready** — all applicable gates pass; remaining edits are cosmetic.
- **Revise** — the argument is sound but one or more gates need a targeted repair.
- **Return to source** — fidelity, central judgment, or reader change is unresolved; further polishing would hide the real problem.

Do not average the gates. Strong readability cannot compensate for invented viewpoints, and source fidelity cannot compensate for an article with no reader consequence.
