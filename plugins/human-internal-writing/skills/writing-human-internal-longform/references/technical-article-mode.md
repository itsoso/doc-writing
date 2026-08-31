# Technical article mode

Read this reference when an article makes claims about code, architecture, performance, incidents, experiments, technical operations, or engineering decisions. It supplements the main evidence ledger; it does not replace the author's viewpoint or force every article into a tutorial.

## Select the article's job

Choose the smallest mode that matches the material. A piece may have one primary mode and one secondary mode, but do not combine modes merely to look complete.

| Mode | Reader's question | Minimum evidence |
|---|---|---|
| Implementation deep dive | How does this mechanism actually work? | Current code path, key types or functions, tests or executable examples, known limitations |
| Performance analysis | Where is time or capacity lost, and what changes it? | Environment, time window, sample, baseline, percentile or distribution, controlled variable, business-metric boundary |
| Architecture decision | Why this design rather than the alternatives? | Constraints, considered options, decision, trade-offs, reversal or review condition |
| Incident retrospective | What happened, why did it propagate, and what prevents recurrence? | Timeline, logs or traces, impact scope, causal evidence, corrective action, verification |
| Tutorial or how-to | Can the reader reproduce a bounded outcome? | Prerequisites, version and environment, runnable steps, expected output, verification, rollback or cleanup |

When the material proves only a structural change, write an implementation or architecture explanation. Do not inflate it into a performance success, incident prevention claim, or fixed-period transformation roadmap.

## Bind technical claims to evidence

Extend the evidence ledger with a status for every consequential technical claim:

| Status | Meaning | Publication treatment |
|---|---|---|
| Verified | Confirmed from current code, a real run, trace, experiment, or authoritative source | State directly and retain the locator |
| Observed | Seen in a bounded dashboard, screenshot, log, interview, or production sample | State the observation and its scope; do not infer universal causality |
| Inference | Reasonable explanation connecting verified or observed facts | Name the reasoning and preserve alternatives |
| Scenario | Sensitivity calculation based on explicit assumptions | Show the formula and assumptions; never call it an incurred loss |
| Proposal | A future implementation, experiment, or governance action | Attribute it as a proposal, not an existing capability or commitment |
| Unknown | Material information is unavailable or contradictory | Keep it visible when it changes confidence or action |

Search results, issue titles, plans, architecture diagrams, expected output, and plausible industry behavior are discovery inputs. They do not prove that the current system implements or exhibits the claim.

## Establish technical ground truth

Before drafting a technical conclusion:

- Read the current code, configuration, schema, test, API definition, or incident artifact that owns the behavior.
- Copy exact identifiers, defaults, versions, error strings, units, and paths from the source rather than memory.
- Run commands and code in a representative environment when safe and in scope. If they were not run, label them `未验证` or `预期输出`.
- For repository claims, link to the relevant file, commit, test, or generated architecture source. A line number alone is brittle; include a stable symbol or revision when useful.
- For external sources, prefer primary or authoritative sources. Record title, publisher, date, URL, applicable population, and the exact proposition supported.
- Do not invent missing mechanisms because they are common in a sound design. If the material shows event publication but not idempotency, dead-letter handling, backpressure, or tracing, keep those as review questions or proposals.

## Apply mode-specific gates

### Performance and business impact

- State metric definition, collection point, time window, sample, environment, traffic segment, and baseline.
- Use distributions and percentiles when averages hide long-tail behavior.
- Distinguish relative percentage change from percentage points.
- Separate internal observation from external benchmark and causal experiment.
- Treat external `100ms → conversion` figures as sensitivity parameters until internal segmentation, controlled experiment, or gray-release evidence exists.
- Calculate `affected baseline × relative change` only after naming the affected scope. Profit requires a separately sourced contribution-margin assumption.
- State the stop, rollback, or falsification condition for an experiment or rollout.

### Architecture and implementation

- Explain the concrete failure or limitation before the solution.
- Show the key insight, then enough implementation detail for the reader to build the right mental model.
- If an earlier approach failed, include it only when evidence shows what failed and why.
- Separate what the code proves from what requires load, fault, or production evidence.
- Name new failure modes, maintenance costs, and operational responsibilities introduced by the design.

### Incident retrospectives

- Keep timeline, trigger, propagation mechanism, impact, root cause, contributing factors, and corrective actions distinct.
- Do not turn correlation into root cause or a repair plan into evidence that recurrence is prevented.
- Give each corrective action an owner, verification signal, deadline when sourced, and rollback or escalation boundary when relevant.

### Tutorials and how-to articles

- State audience, scope, non-scope, prerequisites, versions, and required permissions before the steps.
- Use minimal runnable examples; tell the reader where each code block belongs.
- Include real or explicitly labeled expected output.
- End with a verification step and rollback, cleanup, or failure exit when the action changes state.

## Write a technical argument, not a template

A common technical arc is:

`concrete problem → insufficient or failed approach → key insight → mechanism → evidence → trade-off → remaining proof`

Use it only when the evidence supports the sequence. Do not force a fixed section count, an SEO hook, a call to action, or a 30/60/90-day roadmap. The article's structure should expose how the conclusion was earned.

For mixed audiences, layer the explanation:

1. the user or business consequence;
2. the mechanism in plain technical language;
3. code, trace, data, or architecture detail for specialists.

Use a metaphor only when it shortens comprehension. State which elements map to the real mechanism and where the metaphor stops working. Never use a metaphor as evidence.

## Technical stop conditions

Return to source or mark the gap when:

- an absolute reliability, performance, or business claim has no matching experiment or run;
- a command, code sample, or error output is presented as tested but was not executed;
- a diagram or plan is treated as proof of deployed behavior;
- external data is converted into an internal coefficient without an explicit scenario boundary;
- plausible mechanisms or operational controls were added because the design would normally need them;
- a proposed roadmap contains invented owners, dates, thresholds, or commitments.
