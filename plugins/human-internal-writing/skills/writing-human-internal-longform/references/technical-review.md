# Technical article review

Use this reference after a complete technical draft exists. The review is read-only unless the user explicitly asks for revision. Its purpose is to separate “reads well” from “is technically defensible.”

## Review order

1. Read the complete article without editing.
2. Extract consequential claims, including numbers, causal statements, capability claims, comparisons, absolutes, commands, and statements derived from diagrams or plans.
3. Map each claim to the strongest available source and its locator.
4. Check whether the wording preserves scope, conditions, uncertainty, and mechanism.
5. Check reproducibility of commands, examples, experiments, and calculations.
6. Review the argument, mixed-audience explanation, metaphor boundaries, and prose only after technical integrity.

Do not silently repair the article during review. A fluent rewrite can hide a missing source or introduce a more plausible but incorrect mechanism.

## Finding format

| Location | Exact claim | Evidence and locator | Status | Severity | Recommended action |
|---|---|---|---|---|---|

Use these statuses:

- `supported` — source directly supports the claim in the stated scope;
- `partially supported` — source supports a narrower or conditional claim;
- `scenario` — calculation is valid only under named assumptions;
- `proposal` — future action is clearly separated from current state;
- `unverified` — plausible but not reproduced or source-confirmed;
- `misleading` — source exists but the wording changes mechanism, scope, or certainty;
- `contradicted` — available evidence conflicts with the claim.

Use `critical` when the central thesis, a material business number, a security or reliability promise, or an irreversible action is wrong or unsupported. Use `high`, `medium`, or `low` for decreasing consequence, not stylistic preference.

## Review gates

### Technical truth

- Exact identifiers, versions, defaults, limits, units, and error strings match current sources.
- Code and diagrams describe the implemented mechanism, not an idealized architecture.
- Plans, issue states, UI listings, and expected outputs are not treated as delivery evidence.
- Absolute words such as `彻底`, `完全`, `永久`, and `零风险` have unusually strong proof or are removed.

### Reproducibility

- Commands say whether they were executed, in which environment, and what output was observed.
- Code examples include language, dependencies, placement, and verification when the reader is expected to run them.
- Performance results name baseline, sample, traffic, percentile, time window, environment, and comparison method.
- Calculations show the formula, affected scope, assumption, and unit.

### Evidence boundary

- Facts, observations, inferences, scenarios, proposals, and Unknowns remain distinguishable.
- External benchmarks do not become internal coefficients.
- Correlation does not become causation; non-significance does not become equivalence.
- A missing source remains visible instead of being replaced by a plausible explanation.

### Argument and reader

- The opening establishes a concrete problem rather than generic importance.
- Each section advances the mechanism or decision instead of filling a template slot.
- Specialists can inspect the evidence while non-specialists can understand the consequence.
- Metaphors have a clear mapping and an explicit breakdown point.
- The ending states the supported conclusion and the next proof required, rather than announcing victory.

## Handoff

Open with a two- or three-sentence overall judgment. Present the full claim table, then list the blocking changes before optional improvements. Close with the article's strongest technical and editorial qualities so revision preserves what already works.
