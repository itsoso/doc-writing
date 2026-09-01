# Human Internal Writing for Codex

把会议记录、访谈、管理者观点、技术证据或已有草稿，整理成克制、可信、可行动的长文，并把 Markdown 稳定交付到正确的目标渠道。

`doc-writing` 的核心不是“代写一篇文章”，而是把个人判断变成一条可复盘的生产链：从真实问题和 OKR 主线出发，建立证据账本，保留作者声音，形成单一叙事主线，经过质量与技术复核，再进入 Markdown、内网 Docs 或经过审批的公开导出。

这个仓库提供一个可直接安装的 Codex Marketplace，其中包含：

- `human-internal-writing` 插件；
- `$writing-human-internal-longform` 写作与编辑 Skill；
- `$publishing-kstack-articles` KStack 发布与验证 Skill；
- 来源忠实度、个人声音、论证结构、行动承接和阅读节奏评审标准；
- `EDIT`、`EXPAND`、`AUDIT` 三种明确操作模式与分章节协作协议；
- 面向文章索引、专栏主页和知识 Hub 的全局一致性检查；
- 可解释的草稿检查器、Claim–Evidence 结构门禁、Docs 样式验证与可复现实证；
- 顶层 `doc-writing-router`，统一编排写作、Kim、Docs、图片和发布能力。
- 面向 GitHub 的公开导出边界、文章简报/证据/审批 Schema 与敏感信息扫描器。

“减少 AI 味”在这里指提高编辑质量，不是规避 AI 检测。插件不会虚构观点、数字、引语或个人经历，也不会把单一检查分数当成文章质量结论。

## 三分钟了解

| 你要做什么 | 入口 | 结果 |
|---|---|---|
| 从会议、访谈或草稿写文章 | `$writing-human-internal-longform` | 保留观点、证据边界和行动路径的 Markdown |
| 处理 Kim / Docs 内网材料 | `$doc-writing-router` | 按来源路由到授权的 Kim、Docs 和会议记录 Skill |
| 发布或更新公司 Docs | `$publishing-kstack-articles` | Markdown → Docs → 文章回读 → 索引回读 |
| 做 GitHub 公开导出 | `scripts/check_public_repo.py` | 只允许通过扫描和审批的干净导出 |

完整的路由、状态机和目录约定见[架构指南](docs/guides/doc-writing-github-architecture.md)。

## 安装

```bash
codex plugin marketplace add itsoso/doc-writing
codex plugin add human-internal-writing@doc-writing
```

安装后新建一个 Codex 任务，让新任务加载插件。例如：

```text
使用 $writing-human-internal-longform，把这些会议材料整理成一篇克制、可信、保留我个人判断的内部长文。
```

也可以自然地描述任务，例如：

```text
总结我的全部发言，写成给团队全员阅读的内部长文。保留我的观点和语气，减少模板化表达，并给出明确行动路径。
```

如果任务涉及企业来源，直接说明来源和受众即可：

```text
使用授权的 Kim 消息和 Docs 材料，按我的 OKR 主线写一篇内部文章；保留 Claim ID、Unknown、配图计划和可验收行动。
```

如果任务是公开仓库工程，而不是文章外发：

```text
把这套写作流程整理成可安装的 doc-writing Skill，保留 Kim/Docs 作为企业运行时依赖，不把内网数据带进仓库。
```

## 工作方法

Skill 将写作分成七个阶段：

1. 建立证据账本，区分原始观点、推断和编辑补充；
2. 建立个人声音地图，识别作者独有的判断与价值排序；
3. 明确读者读完后应该理解、停止和开始什么；
4. 根据材料选择叙事骨架，而不是套用固定目录；
5. 先完成结构和全文，再逐句润色；
6. 删除空洞排比、机械标签、重复总结与抽象词堆叠；
7. 按文档类型通过来源、声音、论证、行动、阅读节奏、技术完整性、证据就绪、读者后果和 Index/Hub 全局一致性等条件门禁。

对现有文字的小改使用 `EDIT`，新增内容使用 `EXPAND`，只评审不改写时使用 `AUDIT`。用户要求逐节协作时，Skill 会先反向梳理全文，再在每个检查点展示文本或 diff、相关 Claim ID、已打开的来源、新增推理和需要作者决定的事项；最后仍要做一次全文一致性复核。

文章索引、专栏主页或知识 Hub 不是栏目清单。它们需要先解释各主线共同回答什么问题、彼此如何形成系统，再提供按读者问题组织的入口；栏目增删、重命名或重排后，需要重新检查题头、全局介绍、导航和栏目边界。

## Skill 地图

- [doc-writing-router](plugins/human-internal-writing/skills/doc-writing-router/SKILL.md)：统一入口、来源分类、企业路由、状态机和失败闭环；
- [writing-human-internal-longform](plugins/human-internal-writing/skills/writing-human-internal-longform/SKILL.md)：证据账本、声音地图、叙事结构、技术复核和去模板化编辑；
- [publishing-kstack-articles](plugins/human-internal-writing/skills/publishing-kstack-articles/SKILL.md)：图片、Markdown、Docs 样式、文章回读和索引同步；
- [企业路由矩阵](plugins/human-internal-writing/skills/doc-writing-router/references/enterprise-route-matrix.md)：Kim、Docs、会议记录和发布能力的最小路由；
- [公开仓库边界](plugins/human-internal-writing/skills/doc-writing-router/references/public-repo-boundary.md)：公共 GitHub 与企业运行时的隔离规则；
- [文章与证据 Schema](schemas/)：让简报、Claim、审批和发布回执可被程序检查。

## 交付物契约

写作 Skill 冻结内容与证据边界，发布 Skill 负责派生产物和发布证据。KStack 的默认链路是 `Markdown → 公司 Docs`：

- **Markdown 源文件**：唯一可编辑事实源；带图文章同时保留原图、顺序、题注和章节映射；
- **Docs 发布源**：由同版本 Markdown 派生，通过样式验证后才可用于已授权的写入；
- **远端回读证据**：写入后回读标题、正文、链接和图片，不能用“命令成功”代替发布完成；
- **DOCX/WPS**：仅在用户明确要求时生成、渲染和维护，不属于默认链路；
- **索引更新**：目标仓库有 README 或文章索引时，在同一变更集内更新。

Markdown 变化后，所有派生产物和验证证据都必须重新生成，禁止手改派生产物或沿用旧哈希。仅请求对话内评审或本地草稿时，停在用户要求的边界，不进行外部写入。

正式文章默认使用三行题头，不再把日期塞进标题：

```markdown
# 主标题

> 副标题

2099 年 4 月 5 日
```

H1、文档标题元数据和索引链接文字只使用主标题；副标题与日期分别保留独立层级。日期仍须精确到日，并在 Markdown 与实际生成的发布渠道中保持一致。

## Onepoint（仅限快手内部）

Skill 的通用写作能力不依赖 Onepoint。任何组织都可以直接使用会议文本、访谈、笔记或草稿完成长文写作。

插件同时提供一份条件加载的 Onepoint 参考，仅适用于快手公司内部、具备相应网络和会议权限的用户。当任务明确包含快手 Onepoint 会议链接或要求从 Onepoint 读取会议时，Skill 会先按公司内部规范确认 CLI 与登录状态，再读取会议摘要、行动项、ASR 和关联文档，最后回到同一套通用写作流程。

快手内部用户应以[Onepoint CLI 授权文档](https://bs3-hb1.corp.kuaishou.com/kwaishop-langbridge-evaluation/onepointcli.md)为准。最小会议读取方式为：

```bash
onepoint meeting view <meetingId> --full --output compact_json
```

Onepoint 会议链接、真实 meetingId、完整 ASR、参会人信息和内部业务内容不得写入公共仓库。外部用户或无权访问 Onepoint 的用户，可以提供已授权的会议文本或导出材料；Skill 的其余能力不受影响。

## 草稿检查器

检查器只使用 Python 标准库，不会联网，也不会修改原文：

```bash
python3 plugins/human-internal-writing/skills/writing-human-internal-longform/scripts/check_draft.py \
  path/to/draft.md --formal
```

它会给出带规则名和行号的编辑提示，包括固定标签重复、机械顺序词、抽象词集中、相邻段落重复、标题过碎以及长文缺少行动或风险表达等。`--formal` 只用于正式文章或发布目标，会额外要求独立的 H1、副标题和精确发布日期；讨论记录等非正式草稿应省略该参数。

## Claim–Evidence 门禁

重要事实、数字、因果、技术结论或承诺可以记录在 CSV 证据表中，并在声称 `Editorially ready` 前做结构校验：

```bash
python3 plugins/human-internal-writing/skills/writing-human-internal-longform/scripts/check_evidence.py \
  path/to/evidence.csv --require-ready --json
```

该检查只验证来源定位、版本/新鲜度、核验状态、Claim ID 和依赖关系。它不会打开来源、证明事实、评价文风，也不能替代人工回读。

运行完整测试：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v \
  -s plugins/human-internal-writing/skills/writing-human-internal-longform/scripts \
  -p 'test_*.py'

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v \
  -s plugins/human-internal-writing/skills/publishing-kstack-articles/scripts \
  -p 'test_*.py'
```

## 数据边界

除上面的 Onepoint 官方授权文档入口外，仓库不包含会议原文、具体会议链接、人员信息或真实发布文章。示例全部为合成内容。真实 JSONML、发布回执、内部文档 ID/URL 和未脱敏回读证据必须留在授权的非公开、非跟踪位置；公共投影只保留脱敏状态与哈希。处理内部材料时，请遵守所在组织的数据与发布规范。

## 企业路由与 GitHub 边界

企业内网任务按来源路由到 `kim-sender-context`、`kim-cli`、`docs-cli` 及其声明的子 Skill；文章质量和公司 Docs 发布仍分别由写作与发布 Skill 负责。Kim、Docs、Onepoint 的真实数据和凭证不进入可复用示例或公开仓库。

如果要生成 GitHub 公开版，请先按 [doc-writing GitHub 架构](docs/guides/doc-writing-github-architecture.md) 建立 allowlist 导出，再运行：

```bash
python3 scripts/check_public_repo.py --path <public-export> --json
```

扫描器命中内网 URL、文档 ID、凭证、邮箱或手机号时会失败闭环。`public_candidate` 不是外发授权；公开发布还需要法务、信息安全和业务 Owner 的审批记录。
