# Pairwise evaluation for real article revisions

Use this reference to compare two versions of the same article or multi-entry editorial artifact, or to validate a Skill revision against a small, sanitized corpus. It complements evidence and release gates; it does not replace them.

## Preserve a fair comparison

1. Confirm both versions use the same source scope, reader, publication target, and intended terminal state. Record material differences instead of scoring unlike assignments as if they were equivalent.
2. Freeze the two versions and label them `A` and `B` without version numbers or “old/new” labels for the first editorial review.
3. Review semantic Markdown first. Review rendered DOCX/Docs pages separately so attractive styling cannot conceal a weaker argument.
4. Check source fidelity and consequential claims before scoring. A factual fabrication, missing image, or publication mismatch is a gate failure, not a small point deduction.
5. Collect at least one human reader judgment before claiming the new Skill improved reader value. An LLM-only score is diagnostic, not outcome evidence.

Do not copy confidential article text into this Skill or a reusable fixture. Store real review records beside the authorized release; keep only sanitized structural fixtures in plugin tests.

## Score anchors

Use a 1–5 scale with written evidence. Scores 2 and 4 sit between the named anchors.

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| Editorial aesthetics | Generic cadence, repetitive structure, or visual rhetoric carries the argument | Clear and readable, with some templated passages | Rhythm, hierarchy, and emphasis follow the article's actual reasoning |
| Document beauty | Hierarchy, spacing, images, or typography impede reading | Correct and usable with minor visual friction | Compact masthead, consistent roles, clean pagination, and images that improve understanding |
| Reliability | Consequential claims are unsupported, stale, or overgeneralized | Most claims are bounded, with visible gaps | High-risk claims are traceable, current, reproducible, and phrased at the evidence's true scope |
| Reader usefulness | Reader learns the topic but cannot decide or act | Reader gets a clear judgment and a plausible next step | Reader can explain what changed, make a better decision, and run the smallest next proof |
| Author voice | Could be attributed to any competent leader | Some distinctive judgment survives | Trade-offs, confidence boundaries, examples, and value ordering are recognizably the author's |
| Reading cost | Repetition, metadata, or control language obscures the point | Reasonable length and navigation | Every major section earns its space; caveats stay adjacent without dominating the prose |
| System coherence | Entries are individually plausible but have no supported shared boundary, result, or relationship | The umbrella is understandable, with some overlap or missing handoffs | The first screen exposes one supported system model and every entry has a distinct, composable role |
| Entry clarity | Readers must open several links to discover where to begin | Most readers can find a likely route after scanning the page | Readers can choose the first useful entry from the first screen, and labels, descriptions, status, and targets agree |

## Required output

Record for each dimension:

- score for A and B;
- one concrete reason tied to a paragraph, page, or claim ID;
- the winner or `tie`;
- confidence `low`, `medium`, or `high`;
- the smallest repair for the losing version.

Then report:

- all gate failures separately from scores;
- which version won the blind pass;
- whether the visual pass changed the result;
- whether a human reader confirmed the usefulness difference;
- unresolved confounders such as different source evidence or publication targets.

For a single article, mark `System coherence` and `Entry clarity` not applicable unless it functions as a multi-entry landing page. For an article index, column homepage, or knowledge hub, score both and report a failed Index/Hub gate separately.

Do not average away a reliability failure. If the versions trade off, state the trade-off rather than forcing a single winner.
