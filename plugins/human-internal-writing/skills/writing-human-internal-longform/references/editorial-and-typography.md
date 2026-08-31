# Editorial and typography best practices

Use this reference when an internal long-form article is intended for a formal Markdown file, DOCX/Word/WPS artifact, HTML page, PDF, or company Docs publication. Skip detailed typography decisions for a rough note or a chat-only draft.

The objective is not decorative polish. Typography should make the author's reasoning easier to scan, read, quote, and verify without changing the argument.

## 1. Resolve style authority first

Apply style sources in this order:

1. Explicit user request, approved brand system, legal rule, or accessibility requirement.
2. An accepted earlier edition when visual continuity matters.
3. Target-channel constraints and the renderer's native style system.
4. The fallback profile in this reference.

Do not silently override a higher-priority source. If a required font or style is unavailable, use a compatible fallback, verify the rendered result, and disclose the substitution when it materially changes appearance or pagination.

## 2. Editorial mechanics

- Let one paragraph perform one logical move. Two to five Chinese sentences is a useful reading baseline, not a lint rule; a decisive transition may be one sentence and a causal explanation may be longer.
- Use headings to expose questions, judgments, or changes in reasoning. Do not insert a heading merely because several paragraphs have passed.
- Use a list only when the items are genuinely parallel, independently actionable, or easier to compare than prose. The main argument should remain readable without treating every paragraph as a bullet.
- Use bold for a small number of high-value terms or decisions. Avoid long bold paragraphs, repeated slogan boxes, underlining, decorative highlights, and several simultaneous emphasis systems.
- Introduce an acronym or uncommon English term once before shortening it. Preserve product names exactly and keep Chinese/Latin spacing and punctuation consistent within the article.
- Attach evidence, qualifications, and links to the claim they support. State whether percentages are absolute changes or relative changes when ambiguity would affect the decision.
- Prefer full-width Chinese punctuation in Chinese prose. Avoid stacked punctuation, manual spaces for alignment, and repeated line breaks for visual rhythm.
- Treat dates, units, decimal precision, and number separators consistently. Keep a number only when its precision is supported by the source.

## 3. Semantic Markdown baseline

- Use exactly one level-one heading for the article title, then level-two and level-three headings without skipping levels.
- For a formal article, use three semantic masthead lines by default:

  ```markdown
  # 主标题

  > 副标题

  2099 年 4 月 5 日
  ```

  The H1 contains only the main title. The subtitle adds a distinct conflict, scope, or consequence, and the exact publication date remains a separate quiet line. 三层信息不得合并成 `主标题：副标题｜日期`，也不得把日期写进 H1、文档标题元数据或索引链接文字。DOCX、HTML 和 company Docs must preserve the same three semantic roles even when their typography differs.
- Separate paragraphs, headings, lists, tables, and images with blank lines. Do not encode fonts, point sizes, colors, indentation, or page geometry in the source Markdown.
- Give every meaningful image useful alt text. Place a short caption or source note next to the image when readers need context, provenance, or interpretation.
- Prefer descriptive link labels over bare URLs. Avoid using tables for ordinary prose or layout; wide tables rarely survive mobile and Docs import well.
- Keep the Markdown as the canonical editable content. Generated DOCX, HTML, PDF, and Docs versions must not introduce unsupported claims or lose meaningful paragraphs, links, or images.

## 4. Default DOCX/Word/WPS profile

Use these defaults only when no approved template exists:

| Element | Recommended fallback |
|---|---|
| Page | A4 for China-facing internal articles; 20–25 mm margins; use another page size only when the target requires it |
| Title | 24–30 pt, semibold or bold, compact line spacing, generous space below |
| Subtitle | 13–16 pt, regular or medium, visually subordinate to the title |
| Publication date | 9–11 pt, secondary color, its own paragraph below the subtitle |
| Level-two heading | 16–20 pt, semibold or bold, 14–20 pt before and 6–10 pt after |
| Level-three heading | 13–15 pt, semibold, 10–14 pt before and 4–8 pt after |
| Body | 10.5–11.5 pt; 1.4–1.6 line spacing; 6–10 pt after paragraphs |
| Caption or note | 8.5–9.5 pt; secondary color with sufficient contrast; kept with its image |
| Header/footer | Quiet and secondary; title or section in the header, page number in the footer when useful |

Font selection:

- Prefer one readable CJK family for body text and one compatible heading family. A conservative Word/WPS fallback is `宋体` for body and `微软雅黑` or `等线` for headings; a verified Noto/Source Han family is appropriate when the target devices include it.
- Use a compatible Latin companion such as Aptos, Arial, or the Latin glyphs bundled with the selected CJK family. Avoid mixing several unrelated fonts for visual novelty.
- A declared font is not proof that readers will see it. Render on a representative environment and inspect CJK glyphs, Latin glyphs, punctuation, weight, and pagination for substitution.

Paragraph and page behavior:

- Use paragraph styles rather than direct formatting. Keep title, subtitle, and publication date as three separate paragraphs; do not create vertical space with empty paragraphs.
- The modern default is no first-line indent plus visible paragraph spacing. A traditional two-character first-line indent is acceptable for a narrative house style, but do not combine it with large paragraph spacing.
- Keep headings with the following paragraph. Avoid an isolated heading at the bottom of a page, a single orphan line, a caption separated from its image, or a table row split into an unreadable fragment.
- Keep the main text measure comfortable—roughly 32–45 Chinese characters per line is a useful target. Adjust margins or font size if pages become visually dense.
- Use near-black text on a light background and at most one restrained accent color. Do not make meaning depend on color alone.

Figures and tables:

- Preserve image aspect ratio and source resolution. Fit images inside the text area; do not replace an available source asset with a screenshot.
- Make labels legible at the final rendered size. Add a caption and source when the figure contains evidence; distinguish measured data from a qualitative framework.
- Keep tables narrow, repeat header rows when they span pages, and use alignment to express type: text left-aligned, comparable numbers consistently aligned.

## 5. Company Docs and other reflowable targets

- For KStack publication, load `publishing-kstack-articles` and treat its `assets/kstack-style.v1.json` as the typography authority. In the default formal-article profile, center the masthead H1, subtitle, and publication date; keep H2/H3 and all lower-level headings, plus every body role, left aligned. In the index or knowledge-hub profile, center only H1; keep subtitle, date, every lower heading, navigation, and body role left aligned. These are separate publishing profiles, not general prose rules, and they override the fallback alignment guidance here.
- Use the target's native title, heading, body, list, quote, and caption styles. Do not reproduce DOCX pagination with manual breaks, blank lines, fixed-position objects, or a forced page size.
- Keep formatting conservative because imports may remap fonts, spacing, and table widths. Prefer semantic hierarchy over pixel-perfect imitation.
- After creation or import, read back the title and body, verify links and image count, and visually inspect sections where reflow can change meaning.
- The publication workflow owns target resolution, page/view model, permissions, and remote evidence. This editorial guide must not hardcode those operational values.

## 6. HTML and screen-reading fallback

When the article is primarily read in a browser and no design system exists:

- Use a body size around 16–18 px with a 1.65–1.8 line height.
- Keep the reading column around 680–760 px on desktop and fluid on mobile.
- Scale headings with a clear but restrained hierarchy; avoid a title so large that it pushes the opening argument below the first screen.
- Preserve focus styles, semantic heading order, descriptive links, alt text, and sufficient color contrast.

## 7. Release validation

Editorial validation and visual validation are separate gates:

1. Confirm title, section order, claims, links, images, captions, and source notes against the canonical Markdown.
2. Open or structurally validate the generated file, but do not stop there.
3. Render every DOCX/PDF page and inspect missing glyphs, font substitution, clipping, blank pages, heading isolation, widows/orphans, broken captions, image distortion, and table overflow.
4. Check the first page, a dense middle page, every page containing a figure or table, and the final page at normal reading scale; then complete a full-page pass.
5. For online publication, verify the remote title and body and reconcile the remote image count. Treat a successful upload as transport evidence, not presentation proof.

If a visual defect is found, repair the style or renderer and render again. Do not edit generated output manually when that would make it diverge from the canonical source or build path.
