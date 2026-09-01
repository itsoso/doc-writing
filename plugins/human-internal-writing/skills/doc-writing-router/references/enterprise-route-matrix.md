# Enterprise route matrix

This matrix names runtime dependencies without embedding their implementation or data. The public repository may include this file; the referenced Skills and connectors must be available only in the controlled enterprise runtime.

| Need | Entry Skill | Required sub-skill or reference | Boundary |
|---|---|---|---|
| One sender's Kim messages over a date range | `kim-sender-context` | its local-history workflow | Read-only, local retrieval, no raw-message persistence by default |
| Kim calendar, contacts, IM, todos, meetings | `kim-cli` | `kim-calendar`, `kim-contact`, `kim-im`, `kim-todo`, `kim-vc` | Use public help and OBO auth; no manual tokens |
| Search enterprise Docs | `docs-cli` | `docs-search` | Search result is a candidate; open the controlling document before citing |
| Recent/owned/shared Docs | `docs-cli` | `docs-view` | Confirm the exact document and permission before reading |
| Docs folders, assets, images, permissions | `docs-cli` | `docs-docs` or `docs-security` | Security changes require explicit authorization |
| Normal Docs正文 read/write | `docs-cli` | `docs-word` and `docs-shared` | Freeze Markdown, write only the resolved target, then read back |
| Meeting record analysis | `docs-cli` | `docs-meeting-record` | Preserve speaker and transcript uncertainty |
| Article prose, voice, claims, evidence | `writing-human-internal-longform` | evidence, technical, collaborative references as needed | No invented facts or hidden certainty shifts |
| Article package and company Docs release | `publishing-kstack-articles` | visual style, release contract, Docs publication | Markdown first; image and article/index readback required |
| Public GitHub export | `doc-writing-router` | `scripts/check_public_repo.py` and clearance record | Allowlist export only; fail on enterprise data or credentials |

## Routing sequence

1. Classify the task and audience.
2. Resolve the source connector.
3. Extract evidence into Claim IDs and sensitivity labels.
4. Draft and review with the writing Skill.
5. Validate images and style with the publishing Skill.
6. For internal Docs, perform article and index readback.
7. For GitHub, create a separate allowlist export and run the public scanner; do not mirror the internal worktree.
