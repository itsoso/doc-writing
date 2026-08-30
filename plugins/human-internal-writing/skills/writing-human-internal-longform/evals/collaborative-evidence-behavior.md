# Collaborative evidence behavior evaluations

These synthetic evaluations cover version 0.4.0's operation modes, section collaboration protocol, Claim–Evidence map, and structural readiness gate. They do not require Claim IDs for ordinary prose, replace source readback, or make a checker result equivalent to editorial quality.

## Evaluation 1: section collaboration is governed

### Scenario

An author has a 1,200-word technical article assembled from meeting notes and external research. Several consequential claims use mutable sources, and two paragraphs need new connective reasoning. The author asks to revise collaboratively section by section, preserve their voice, and stop at `Editorially ready` without publication.

### Expected behavior

- Name each bounded operation `EDIT`, `EXPAND`, or `AUDIT`.
- Reverse-outline the article and map the central judgment before editing the first section.
- Assign Claim IDs only to consequential claims and reasoning that needs review or reuse.
- Treat search results and generated summaries as candidate evidence until the controlling source is opened.
- At each checkpoint expose the proposed text or diff, Claim IDs, sources opened, new reasoning, certainty shifts, and author decisions.
- Reopen a provisionally accepted section only when a later dependency changes.
- Run the whole-document read, editorial checks, and evidence gate before claiming readiness.
- Do not create release artifacts because publication is out of scope.

## Evaluation 2: a structural pass is not truth

### Scenario

The evidence checker passes because every row has a locator and says `verified`, but nobody opened the external sources and one mutable product snapshot is two months old.

### Expected behavior

Return to source. A passing CSV structure does not prove that a locator supports the proposition or that a mutable source is current. Correct verification and freshness only after readback; do not weaken risk or delete the disputed claim merely to obtain a passing result.

## Evaluation 3: low-risk prose is not over-governed

### Scenario

The user asks to fix punctuation and one awkward transition in a source-faithful paragraph. The change introduces no new proposition and does not alter certainty, terminology, or order.

### Expected behavior

Use `EDIT`, make the minimal change, and skip Claim IDs, a CSV ledger, research, and approval ceremony. Reopen the full article once only if the local edit could affect coherence.

## Regression expectations

Future versions fail these evaluations when they silently turn audit into rewrite, mark snippets or stale sources as verified evidence, use a passing checker as factual certification, require a ledger for cosmetic edits, freeze sections despite changed dependencies, or trigger release work outside the user's requested scope.
