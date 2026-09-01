# Public repository boundary

`doc-writing` can be published as code, but the current enterprise worktree is not itself a public export. Build a clean allowlist export containing only:

- router and editorial Skills;
- connector route names and contracts, not connector data or credentials;
- schemas, deterministic validators, tests, and sanitized fixtures;
- articles explicitly cleared for external use;
- original images whose rights and metadata have been checked.

Never export:

- Kim messages, meeting transcripts, Docs JSONML, Docs export ZIPs, WPS/DOCX packages, screenshots, or publication receipts containing internal IDs;
- internal company domains (for example, Docs or Onepoint hosts), internal document IDs, signed URLs, cookies, tokens, or authorization headers;
- employee, user, merchant, order, device, or contact identifiers;
- unpublished architecture, traffic, model, cost, experiment, incident, or roadmap details;
- raw prompts, tool schemas, endpoint names, permission maps, logs, or stack traces;
- third-party material without a recorded license or quotation basis.

Deletion from the latest commit is insufficient. Scan the export and its Git history before the first public push. If a secret or sensitive URL was ever exposed, rotate/revoke it and scrub the history before publishing.

The public package should use an explicit `audience: public` manifest and a clearance record naming the scope, approvers, date, and expiry. Without that record the status is `public_blocked`.
