# Editorial compression behavior evaluations

These synthetic evaluations cover version 0.3.2's structural-rewrite lane. They test whether faster, shorter writing preserves load-bearing meaning, readable evidence boundaries, and proportionate action. They do not set a universal compression ratio, word count, scene quota, or gate count.

## Evaluation 1: shorter draft loses the reason to believe it

### Scenario

A prior technical strategy article contains one source-backed incident that changed the author's view, one compact latency mechanism, a real growth-versus-user-interest tension, repeated explanations, two external analogies, four future ideas, and a distant market forecast. The user asks for a much shorter, less templated revision without weakening technical truth.

### RED with version 0.3.1

The real-world baseline demonstrated that the Skill could remove branches, halve length, improve evidence boundaries, and expose a first draft quickly. It did not require a preservation map. The revision removed repetition and unsupported expansion, but also lost a source-backed operational failure, a minimal latency decomposition, and a concrete end-to-end product example. The surviving article was safer and easier to scan, yet more dependent on conclusions, abstract fields, and controls.

Failure: length and traceability improved while some of the scene, mechanism, and product consequence that earned the judgment disappeared.

### GREEN with version 0.3.2

- Choose `Structural rewrite`, not `Focused edit` or a new-article lane.
- Classify prior material as `keep`, `compress`, `remove`, or `move` before cutting.
- Delete repeated explanations, non-decisive analogies, and the distant forecast.
- Retain the smallest source-backed incident or scene that changed the judgment, one minimal mechanism, the central counterforce, and the next proof when those functions exist in the source.
- Compare old and new reverse outlines; do not use character reduction as the quality result.

Pass means the article is materially shorter and the central judgment is still earned. It does not require restoring every detail or retaining a fixed amount of text.

## Evaluation 2: evidence-safe prose becomes an audit report

### Scenario

A technically accurate draft repeats `Observed`, `Proposal`, `Unknown`, “cannot prove,” and “not yet verified” around several claims that share the same source limitation. It opens in the author's first person, then refers to “the author-provided figures.”

### GREEN expectation

- Preserve every material evidence boundary.
- Attribute a distinct third-party source where needed, but keep the author's narrative perspective coherent.
- State a shared limitation once near the affected claims or in a compact note when repetition adds no decision value.
- Keep the evidence ledger's state labels outside the reader-facing prose unless the format is explicitly an audit.
- Move version, image, and release provenance to release metadata unless they change interpretation.

The evaluation fails if natural prose is obtained by hiding uncertainty, or if factual safety is obtained by making provenance and caveats the article's dominant voice.

## Evaluation 3: one experiment becomes a governance program

### Scenario

The evidence supports one reversible first-result experiment. Several later product ideas exist, but their dependencies, owners, thresholds, and commitments are Unknown.

### GREEN expectation

- Expand the one smallest next proof with scope, evidence, feedback, and a stop or decision condition proportionate to its risk.
- Keep later ideas as conditional questions or proposals.
- Do not turn them into a confirmed sequence of gates, a fixed-period roadmap, or team commitments.

The evaluation fails if every idea receives a gate, rollback, owner placeholder, or stage dependency merely because that looks operationally complete.

## Evaluation 4: high-risk actions still require staged control

### Scenario

The source explicitly covers external state changes, irreversible financial actions, real dependencies, and an approved staged experiment.

### GREEN expectation

Retain the supported gates, authorization checks, stop conditions, idempotency or compensation boundaries, owners, and evidence. The action-depth rule must not flatten necessary governance into one lightweight next step.

## Regression expectations

Future versions fail these evaluations when they:

- optimize for a shorter character count while deleting all load-bearing source moments and mechanisms;
- require a fixed number of scenes, mechanisms, gates, or words in every article;
- hide material uncertainty to avoid an audit tone;
- switch a first-person author article into third-person provenance language without a distinct source reason;
- turn an editorial recommendation into a confirmed program or dependency chain;
- remove staged control when external state, safety, or irreversible consequences genuinely require it.
