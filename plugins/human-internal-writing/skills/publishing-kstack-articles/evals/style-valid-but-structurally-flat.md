# Style-valid but structurally flat index behavior

This evaluation covers a maintained article index or editorial hub whose typography passes every deterministic style check but whose first screen still reads as a set of unrelated sections.

## Scenario

The page has a valid three-line masthead, exact role sizes and colors, clean left alignment under the selected profile, working links, and no rendering defect. It presents several long-running tracks and reading entries, but it never explains the shared problem, system boundary, or relationship that makes those tracks belong together. After several visual revisions, the user still describes the page as flat, difficult to read, or unattractive.

## RED baseline

The release workflow treated a passing Style Gate as proof that the page design was complete. It responded to the aesthetic complaint by adding a decorative card, banner, ornamental image, table, accent color, or more spacing. The page became busier while its information architecture remained unresolved.

## GREEN expectation

- State that the Style Gate proves only the typography and layout floor.
- Diagnose information architecture before changing any visual token.
- Return to `writing-human-internal-longform` because the missing global orientation is an editorial-structure problem.
- Preserve the accepted Markdown, links, images, and section content while the writing workflow determines the smallest coherent structural revision.
- Regenerate and revalidate release artifacts only after the canonical Markdown freezes again.
- For a maintained index, require local structure validation and structural remote readback parity before claiming `docs_verified`.

The expected editorial repair is not a fixed heading or paragraph count. It must let a target reader explain why the tracks form one system and then choose an entry point. That judgment remains human; validators enforce only declared structure and content parity.

## Non-regression controls

- Do not weaken exact size, color, alignment, A3, source-hash, or authorization gates.
- Do not hardcode one release's track names, counts, links, or global-introduction title into the reusable Skill.
- Do not treat a screenshot, a successful write response, or a style-validation pass as remote structural proof.
- Do not modify a confirmed historical Markdown version; create a new source version and update only the authorized maintained Docs page.
