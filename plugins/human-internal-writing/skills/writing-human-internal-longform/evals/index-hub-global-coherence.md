# Index and hub global-coherence evaluations

These synthetic evaluations cover version 0.6.0's article index, column homepage, and knowledge hub mode. They test global coherence and entry clarity under release pressure; they do not treat working links, attractive formatting, or a forced taxonomy as proof of editorial readiness.

## Evaluation 1: valid page, missing system

### Scenario

A column homepage presents several strategic tracks. Every section has a concise question, current status, and canonical link. The structure and links already pass. The page opens with recommended readings and a current-update block, but it never explains why the tracks belong to one system. A leader says publication is in five minutes and asks for a release decision, not a rewrite.

Pressures: five minutes, completed structural checks, functioning links, polished local summaries, and authority preference for immediate publication.

### RED baseline before version 0.6.0

The artifact-level baseline judgment was:

> 不会直接发布。
>
> 首屏能看懂“这是多条经营主线的阅读索引”，但看不懂它们为何属于同一个系统；目前更像几个并列栏目加若干阅读入口。
>
> 最关键缺口：首屏缺少一句把这些主线串成同一条受来源支持的工作链——问题发现 → 决策 → 交付 → 运行反馈 → 资源约束。

Failure: local correctness and navigation existed, but the first screen did not expose the collection's system boundary or relationship model. Readers could identify topics without understanding the whole or choosing an entry from that whole.

### GREEN with version 0.6.0

- Select `AUDIT` because revision was not authorized.
- Route to `index-and-hub-editorial-mode.md` and apply the Index/Hub quality gate after structural and link checks.
- Decline direct publication for the one material blocker: missing first-screen system explanation.
- Name the smallest sufficient repair: one supported system thesis plus reader-oriented routes whose labels align with the distinct entry roles.
- Do not claim the illustrative causal chain is true until the source or owner confirms those relationships.

Pass means the reviewer distinguishes global coherence from valid local structure and identifies the smallest repair without silently editing.

## Evaluation 2: forced coherence would invent a system

### Scenario

A knowledge hub contains useful material from unrelated business, engineering, hiring, and community programs. The user asks for one elegant flywheel connecting every entry, but the sources establish no shared outcome or dependency.

### GREEN expectation

- Mark the relationship model `Unknown`; do not invent a causal loop.
- Propose a truthful umbrella, split the hub, or ask for the missing owner judgment when that answer would materially change the taxonomy.
- Preserve useful entries and verified links while withholding global-readiness approval.

The evaluation fails if system coherence is achieved by fabricating causality, ownership, sequence, or business impact.

## Evaluation 3: clear umbrella, unclear entry choice

### Scenario

An article index states a credible shared system model, but four entry summaries all promise “understand the strategy and take action.” Their titles, status labels, and ordering use different vocabularies from the first screen.

### GREEN expectation

- Pass the system-boundary check but fail entry clarity.
- Rebuild the entry map around distinct reader questions and unique roles.
- Align link labels with canonical main titles; keep dates and status separate.
- Re-run the headings-and-entries-only read before publication.

## Regression expectations

Future versions fail these evaluations when they:

- treat structure and links already pass as sufficient publication evidence;
- polish entries independently without a global coherence pass;
- let a current-update block displace the first-screen contract;
- force unrelated entries into an unsupported loop;
- let generic or inconsistent entry descriptions obscure the first useful route;
- rewrite during `AUDIT` without authorization.
