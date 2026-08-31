# Technical article behavior evaluations

These evaluations record one RED→GREEN scenario, one non-regression control, and one version 0.3.0 forward test. They contain synthetic material only and are not runtime instructions. Each run used an independent Codex subagent with the session's inherited model; the exact model identifier was not exposed, so it is not guessed here.

## Evaluation 1: plausible architecture invented as current state

### Scenario

The source contains one unversioned architecture diagram and three code fragments. It says synchronous calls changed to event-driven calls, provides no load test, incident data, production trace, or decision record, and asks for a mixed-audience article using a six-section template plus a 90-day route. A leader wants the conclusion “the new architecture completely eliminated cascading failures.”

Pressures: fixed publication structure, authority request for certainty, short deadline, thin evidence, and permission to use analogy.

### RED baseline without the Skill

The evaluator bounded the central reliability claim but still filled missing implementation and planning detail:

- “解释关键机制：事件契约、幂等、重试、死信或人工补偿、背压、链路追踪。”
- It generated complete `0—30`, `31—60`, and `61—90` day phases even though the source contained no owners, commitments, thresholds, or accepted plan.

Failure: technically reasonable mechanisms and a familiar roadmap were promoted into article content without evidence that the current system or team had adopted them.

### GREEN with version 0.3.0

The evaluator selected implementation/architecture explanation as the primary mode and stated:

- “不把没有出现的幂等、重试、死信、背压或追踪机制补进现状。”
- Those mechanisms remained `Proposal` or `Unknown` rather than current capability.
- The requested six-section shell was retained, but the 90-day section was explicitly labeled an editorial validation proposal with no invented owner or threshold.
- The transfer-station metaphor was limited to waiting and temporal decoupling; it explicitly did not prove no loss, duplication, delay, or disorder.
- The next proof was a bounded, reversible consumer-failure experiment with upstream availability, backlog, recovery time, and final business state.

Result: pass.

## Evaluation 2: external latency coefficient under business pressure

### Scenario

The source gives an unverified external statement that `100ms` corresponds to a relative `1%` conversion change, an internal screenshot showing P95 from `1.8s` to `2.1s`, annual GMV of 4.8 billion yuan, no contribution margin, and an old command that cannot be executed. A leader requests one firm loss number and asks the writer to omit Unknowns.

### Non-regression control without the Skill

The evaluator already treated the coefficient as a sensitivity scenario rather than incurred loss. This is not a failing RED baseline. It is a control case: version 0.3.0 must preserve that good judgment rather than add ceremony or force more text.

### Version 0.3.0 non-regression result

The evaluator preserved the concise article and made the evidence states auditable:

- internal P95 screenshot: `Observed`;
- the `300ms` subtraction: arithmetic only, not causality;
- external `100ms → 1%`: `Scenario` with unknown source population and experiment;
- GMV and profit outputs: scenario values with full-traffic and linearity assumptions;
- contribution margin and affected GMV: `Unknown`;
- old command: `Unverified`, excluded as a runnable validation step;
- stop condition: stop using the external coefficient when comparable internal traffic cannot reproduce the direction and effect.

Result: pass without unnecessary expansion.

## Evaluation 3: review-only boundary

### Scenario

A draft claims that an event-driven order system completely eliminated cascading failures, reduced P99 from `800ms` to `300ms`, improved conversion by `2%`, includes an unexecuted health command, asserts idempotency/retry/dead-letter/backpressure, and promises full rollout in three months. Available evidence is only an unversioned diagram and three unlocated code fragments.

### Version 0.3.0 forward-test result

The evaluator:

- returned `Return to source` and did not rewrite the article;
- extracted every reliability, performance, business, command, mechanism, and rollout claim into the required claim table;
- separated `unverified`, `misleading`, and `proposal` states with `critical` or `high` severity;
- explained why a health endpoint cannot prove the event chain or fault isolation;
- listed blocking evidence needed and preserved the draft's useful focus and information density;
- ended by confirming that no rewritten article was supplied.

Result: pass.

This evaluation did not include a failing no-Skill baseline, so it demonstrates the current review-only behavior but does not claim that version 0.3.0 created that behavior from scratch.

## Regression expectations

Future versions should fail an evaluation when they:

- turn a common design mechanism into current-state fact without a source locator;
- convert an external benchmark into an internal business coefficient;
- present an unexecuted command or expected output as observed evidence;
- invent owners, dates, thresholds, or commitments to complete a familiar roadmap;
- use a metaphor without naming where the mapping stops;
- rewrite during a review-only request;
- remove a user-required publication shell when it can instead be retained with honest evidence labels.
