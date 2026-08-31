# Profile-specific alignment behavior

This evaluation preserves the non-heading alignment regression from version 0.5.1 and adds the article-index distinction required by version 0.6.0. It covers company Docs and an explicitly requested DOCX without changing the three-line masthead semantics.

## RED baseline before version 0.5.1

The style asset centered kicker, subtitle, publication date, and caption while justifying body and list text. The Docs validator did not reject centered lead, body, list, caption, or source paragraphs, and the DOCX validator checked only the first occurrence of each semantic role.

## RED baseline before version 0.6.0

The default formal-article profile and the maintained index profile were described as if they shared one alignment rule. Generated index pages and saved validation evidence could therefore disagree about subtitle and date alignment even when they named the same style version.

## GREEN expectation in version 0.6.0

- The default formal-article profile centers H1, subtitle, and publication date; H2, H3, and all lower headings remain left aligned.
- The index profile centers only H1. Subtitle, publication date, H2, H3, and every other text role are explicitly left aligned.
- Kicker, lead, body, every list item, caption, and source/note are left aligned in both profiles.
- Justified body or list text is rejected.
- A later DOCX paragraph cannot override the required alignment after an earlier paragraph of the same role passed.
- Docs and DOCX generators read alignment from `assets/kstack-style.v1.json` rather than carrying private alignment constants.
- `validate_docx_style.py --profile index` and `validate_docx(path, profile="index")` both select the DOCX index profile; the passing receipt names that profile.
- DOCX validation evidence records `docx_sha256`, `style_contract_sha256`, `validator_sha256`, and `plugin_version`, while serializing only the artifact basename and repository-relative contract locator. A stale pass or workstation path must not survive into release evidence.

## Non-regression controls

- A3 remains mandatory for company Docs.
- Company Docs body, list, and lead text remain editor size 11.
- The visible masthead remains main title, subtitle, and publication date in that order even when their alignment differs by profile.
- Image blocks may remain centered; the rule applies to text paragraphs and their semantic captions, not the image canvas itself.
