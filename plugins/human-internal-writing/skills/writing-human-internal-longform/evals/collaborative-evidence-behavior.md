# Collaborative evidence behavior evaluations

These synthetic evaluations cover version 0.4.0's explicit operation modes, section collaboration protocol, Claim–Evidence map, and structural readiness gate. They do not require a claim ID for ordinary prose, replace source readback, or make a checker score equivalent to editorial quality.

## Evaluation 1: section collaboration is inferred but not governed

### Scenario

An author has a 1,200-word internal technical article assembled from two internal meeting notes and three external research links. Eight consequential factual or causal claims are present, several sources are mutable, and two paragraphs need new connective reasoning. The author asks to revise collaboratively section by section, preserve their voice, and finish at `Editorially ready` without publication.

### RED with version 0.3.2

The evaluator correctly inferred a compact evidence ledger, mutable-source recheck, provisional section checkpoints, a final whole-document read, technical review, the deterministic draft checker, and a cold-read. It also identified these gaps:

- no explicit `EDIT`, `EXPAND`, or `AUDIT` operation mode;
- no defined section review envelope or rule for reopening an accepted section;
- tension between “complete the whole draft first” and explicit section-by-section collaboration;
- no required Claim IDs, dependencies, freshness proof, or mechanical evidence gate;
- no explicit author-decision boundary for new connective inference or editorial additions.

The workflow was defensible only because the evaluator invented a reasonable collaboration protocol from adjacent rules.

### GREEN expectation for version 0.4.0

- Name the operation on each bounded unit: existing prose is `EDIT`, new connective reasoning is `EXPAND`, and review-only work is `AUDIT`.
- Reverse-outline the whole article and map the central judgment before editing the first section.
- Assign Claim IDs only to consequential claims and reasoning that needs review or reuse.
- Treat research results and generated summaries as candidate evidence until the controlling source is opened and matched to the exact proposition.
- At each section checkpoint expose the proposed text or diff, changed Claim IDs, sources opened, new reasoning, certainty shifts, and author decisions.
- Treat accepted sections as provisionally accepted and reopen them only when a later dependency changes.
- Run the whole-document coherence read, technical review, draft checker, cold-read, and the evidence-ledger structural gate before claiming `Editorially ready`.
- Stop before DOCX, company Docs, or any release artifact because publication is out of scope.

## Evaluation 2: a mechanical pass is mistaken for truth

### Scenario

The evidence checker passes because every row has a locator and says `verified`, but nobody opened the three external sources and the organization snapshot is two months old.

### GREEN expectation

Return to source. A passing CSV structure does not prove that the locator supports the proposition or that a mutable source is current. Correct the verification and freshness records only after readback; do not weaken risk or delete the disputed claim merely to obtain a passing result.

## Evaluation 3: low-risk prose is over-governed

### Scenario

The user asks to fix punctuation and one awkward transition in a source-faithful paragraph. The change introduces no new proposition and does not alter certainty, terminology, or order.

### GREEN expectation

Use `EDIT`, make the minimal change, and skip Claim IDs, a CSV ledger, research, and approval ceremony. Reopen the full article once only if the local edit could affect coherence.

## Regression expectations

Future versions fail these evaluations when they:

- make section collaboration depend on an improvised protocol;
- silently turn audit into rewrite or connective prose into sourced fact;
- mark snippets, summaries, or stale mutable sources as verified evidence;
- use a passing checker as factual, editorial, technical, or publication certification;
- require a claim ledger for cosmetic or low-risk wording edits;
- freeze accepted sections even when their evidence dependencies later change;
- trigger release work after the user explicitly stopped at editorial readiness.
