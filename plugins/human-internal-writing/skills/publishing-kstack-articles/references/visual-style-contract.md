# KStack visual style contract

This is the human-readable explanation of the mandatory KStack house style. The canonical machine tokens live in [assets/kstack-style.v1.json](../assets/kstack-style.v1.json); all generators and validators consume that asset. The tables below mirror it for review. If they ever disagree, stop the release and repair the drift rather than choosing one ad hoc. A user-supplied approved template may replace the whole profile; do not mix individual values from two profiles.

## 1. Company Docs: exact tokens

Every KStack article and article-index page uses `viewModel=A3`. A3 is the page model, not permission to enlarge the prose. Company Docs owns the font stack, so the Docs source must contain **no `font-family` declaration**. Never imitate Word fonts in HTML.

The table below describes the default formal-article profile:

| Role | Size | Text color | Alignment | Required source marker |
|---|---:|---|---|---|
| Kicker | 10 | `#2E74B5` | left | `data-kstack-role="kicker"` + `align="left"` |
| Compact body H1 | 24 | `#17344B` | center | exactly one `<h1 align="center">` |
| Subtitle | 14 | `#5F6368` | center | `data-kstack-role="subtitle"` + `align="center"` |
| Publication date | 9 | `#5F6368` | center | `data-kstack-role="date"` + `align="center"` |
| Lead/callout text | 11 | `#1F4D78` | left | `data-kstack-role="lead"` |
| H2 | 16 | `#2E74B5` | left | `<h2 align="left">` |
| H3 | 13 | `#2E74B5` | left | `<h3 align="left">` |
| Body and list text | 11 | `#202124` | left | ordinary `<p>` or `<li>` with explicit left alignment |
| Caption | 9 | `#5F6368` | left | `data-kstack-role="caption"` + `align="left"` |
| Source/note | 9 | `#5F6368` | left | `data-kstack-role="source"` |

The default formal-article profile centers H1, subtitle, and publication date; H2, H3, and body text are left aligned. The index profile centers only H1; subtitle, publication date, H2, H3, and body text are left aligned. Its kicker, lead, list, caption, source/note, entry-title, and note roles are also left aligned. Resolve these values from the profile in `assets/kstack-style.v1.json`; do not copy the default table into an index builder.

For a multi-entry index or hub, declare structure as well as layout: keep `data-kstack-layout="index"` on the page root, mark the global-introduction H2 with `data-kstack-role="global-intro"`, and mark every entry H2 with `data-kstack-role="hub-entry"`. The introduction must be the first H2 and contain a non-empty `body` paragraph before the next H2. Explicit roles are required when entry headings are not numbered. For backward-compatible numbered indexes, the validator also recognizes two or more entry headings shaped like `1｜Title`, `01｜Title`, `1 | Title`, or their whitespace variants and treats the first non-entry H2 as the introduction. It deliberately does not infer a hub from several unmarked, non-numbered H2 headings, because that would misclassify ordinary article sections.

These are company Docs **editor font-size values**, not browser-computed CSS pixels. In the source package, write the same number as `font-size: Npx`; the importer maps that numeric token to its editor size control. For example, body source must use `font-size: 11px`, and a live browser may report roughly 15 CSS pixels after rendering. Never use `17px` as a visual conversion for 11 pt: Docs will import it as editor size 17.

The only permitted palette is:

- primary ink `#202124`;
- title navy `#17344B`;
- accent blue `#2E74B5`;
- lead blue `#1F4D78`;
- muted text `#5F6368`;
- divider `#DADCE0`;
- callout background `#F4F6F9`.

Do not use theme names, RGB variants, arbitrary grays, gradients, decorative colors, or color as the sole carrier of meaning. Nested elements may not override the role's exact size or text color.

The Docs document metadata uses the main title only. For a formal article, the visible body masthead is compact and ordered: optional kicker, one short H1, subtitle, publication date, optional one lead block, then a divider. The publication date must be one standalone, valid calendar date in exact `YYYY 年 M 月 D 日` form; a month-only value, visible timezone, suffix, or impossible date is invalid. The body H1 must not repeat the subtitle, version, publication date, or `｜` suffix. Keep the subtitle and date as separate semantic paragraphs; do not add a cover page, large logo, duplicate title, author card, repeated summary card, or decorative blank space before the first argument.

In the default formal-article profile, the H1, subtitle, and publication date form one centered compact title block. In the index profile, the three semantic masthead lines remain in the same order but only H1 is centered. H2, H3, and lower-level headings remain left aligned in both profiles, and every non-heading text paragraph is left aligned except the default profile's subtitle and date. Do not justify body copy or center a paragraph for decoration.

Validate the exact Markdown/HTML file placed in the Docs content zip:

```bash
python3 "<loaded publishing-kstack-articles Skill directory>/scripts/validate_docs_style.py" \
  "<absolute Docs-source Markdown path>" \
  --json
```

Any finding is a publication block. Save the passing JSON output beside the release as `docs-style-validation.json`. Confirm that the result names the intended `default` or `index` profile, and re-run the command after every source or style change and immediately before creating the Docs document. An index source declares `data-kstack-layout="index"`; profile and marker must agree in both directions. Validation blocks both an explicit `--profile default` with the marker and an explicit `--profile index` without it, so removing the marker cannot bypass index structure gates.

For a style-only JSONML repair, pass the form explicitly so repaired source keeps the same profile:

```bash
python3 "<loaded publishing-kstack-articles Skill directory>/scripts/repair_docs_jsonml_style.py" \
  --input "<absolute fetched-jsonml path>" \
  --output "<absolute replacement-ops path>" \
  --profile default  # or: index
```

The `index` repair profile keeps subtitle and date left aligned and applies the index H3 navy token; it must not fall back to the default centered masthead.

## 2. DOCX/Word/WPS: exact profile

Unless the user supplies an approved template, first select one complete font profile from the verified target environment. Do not mix profiles or rely on renderer substitution:

- Windows/WPS: headings `微软雅黑`, body `宋体`, Latin companion `Arial`.
- macOS/WPS: headings `PingFang SC`, body `Songti SC`, Latin companion `Arial`.

The following default formal-article sizes, colors, and alignments are identical in both operating-system font profiles:

| Role | Font | Size | Color | Alignment |
|---|---|---:|---|---|
| Kicker | selected heading font, bold | 10 pt | `#2E74B5` | left |
| Title | selected heading font, bold | 24 pt | `#17344B` | center |
| Subtitle | selected heading font, regular | 14 pt | `#5F6368` | center |
| Publication date | selected body font; Latin companion `Arial` | 9 pt | `#5F6368` | center |
| H2 | selected heading font, bold | 16 pt | `#2E74B5` | left |
| H3 | selected heading font, bold | 13 pt | `#2E74B5` | left |
| Body/list | selected body font; Latin companion `Arial` | 11 pt | `#202124` | left |
| Lead | selected body font; Latin companion `Arial` | 11 pt | `#1F4D78` | left |
| Caption/source | selected body font; Latin companion `Arial` | 9 pt | `#5F6368` | left |
| Header/footer | selected body font; Latin companion `Arial` | 8.5 pt | `#5F6368` | role-specific |

The default body, list, and lead size is exactly 11 pt; do not treat it as an approximate value or a selectable range. Use A4, 21 mm margins, 1.5 line spacing for body text, and 6 pt paragraph-after spacing. Use paragraph styles rather than ad hoc direct formatting. Center only Title, subtitle, and publication date. Keep H2/H3 and all other body roles left aligned as distinct semantic paragraphs. Do not create a standalone cover page unless the user explicitly asks for one. Do not create vertical space with empty paragraphs.

Confirm the selected fonts with the target operating system before authoring. Declare East Asian and Latin fonts correctly in the DOCX style definitions. A declared font is not enough: render the DOCX in the named target application and inspect every page. For a WPS-targeted artifact, export PDF from WPS itself, verify the embedded fonts, and hash that PDF plus its rendered page images; treat LibreOffice output only as a secondary compatibility check. Missing fonts, unplanned substitution, oversized prose, color drift, isolated headings, empty title space, or captions separated from figures are release blocks.

Before rendering, run `scripts/validate_docx_style.py` on the exact DOCX. It checks the machine-verifiable floor—A4, 21 mm margins, semantic masthead/body styles, exact role sizes and colors, centered title/subtitle/date roles, left-aligned H2/H3 and body roles, and body spacing—against `assets/kstack-style.v1.json`. It does not replace WPS rendering, embedded-font inspection, or page-by-page visual review.

## 3. Cross-channel consistency

Content hierarchy, emphasis intent, image order, captions, and source notes must agree across Markdown, DOCX, and company Docs. The nominal role sizes are aligned across channels, but their encodings are not: DOCX stores point sizes, while the Docs source expresses the editor's numeric size as `font-size: Npx` for import. Do not copy DOCX font-family declarations into Docs, and do not claim visual consistency merely because the words match.
