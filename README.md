# Human Internal Writing for Codex

把会议记录、访谈、管理者观点或已有草稿整理成克制、可信、可行动的内部长文，同时保留作者真实的判断、张力与语言习惯。

这个仓库提供一个可直接安装的 Codex Marketplace，其中包含：

- `human-internal-writing` 插件；
- `$writing-human-internal-longform` 核心 Skill；
- 来源忠实度、个人声音、论证结构、行动承接和阅读节奏评审标准；
- 可解释的草稿检查器与测试。

“减少 AI 味”在这里指提高编辑质量，不是规避 AI 检测。插件不会虚构观点、数字、引语或个人经历，也不会把单一检查分数当成文章质量结论。

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

## 工作方法

Skill 将写作分成七个阶段：

1. 建立证据账本，区分原始观点、推断和编辑补充；
2. 建立个人声音地图，识别作者独有的判断与价值排序；
3. 明确读者读完后应该理解、停止和开始什么；
4. 根据材料选择叙事骨架，而不是套用固定目录；
5. 先完成结构和全文，再逐句润色；
6. 删除空洞排比、机械标签、重复总结与抽象词堆叠；
7. 通过来源、声音、论证、行动和阅读节奏五道发布门禁。

## 交付物契约

Skill 治理编辑质量，也治理发布时的交付物形态。任何使用该 Skill 的 agent（Codex、WorkBuddy、DSH 等）在执行发布或归档时，必须同时产出并保持对齐：

- **Markdown 源文件**：可编辑的事实源，存入目标仓库，所有后续修改只发生在这一份上；
- **Word/WPS 兼容 doc（`.docx`）**：默认分享与评审格式，从 Markdown 用 pandoc 生成（`pandoc <article>.md -o <article>.docx --toc-depth=2 -M lang=zh-CN`），与源文件同目录，Word 和 WPS 均可正确打开，H1 为文档标题、正文从 `h2` 起；
- **WordPress 兼容 HTML 片段**（可选，仅 web 发布时）：从 Markdown 生成，仅使用 WordPress 保留的块级标签（`h1–h4, p, strong, em, blockquote, ul/ol/li, a, img, hr, code, pre, table`），无 `style`/`script`/内联样式/类属性，无文档级包裹，标题 H1 作为文章题目不在正文重复，正文从 `h2` 起；
- **索引更新**：目标仓库有 README 或索引时，在同一变更集内更新条目。

一致性规则：`.docx` 与 HTML 片段均为派生产物——Markdown 变更必须在同一提交内重新生成，不允许手改。仅请求对话内评审（无发布或归档）时，单独交付 Markdown 即可。

## OnePoint（仅限快手内部）

Skill 的通用写作能力不依赖 OnePoint。任何组织都可以直接使用会议文本、访谈、笔记或草稿完成长文写作。

插件同时提供一份条件加载的 OnePoint 参考，仅适用于快手公司内部、具备相应网络和会议权限的用户。当任务明确包含快手 OnePoint 会议链接或要求从 OnePoint 读取会议时，Skill 会先按公司内部规范确认 CLI 与登录状态，再读取会议摘要、行动项、ASR 和关联文档，最后回到同一套通用写作流程。

快手内部用户应以[OnePoint CLI 授权文档](https://bs3-hb1.corp.kuaishou.com/kwaishop-langbridge-evaluation/onepointcli.md)为准。最小会议读取方式为：

```bash
onepoint meeting view <meetingId> --full --output compact_json
```

OnePoint 会议链接、真实 meetingId、完整 ASR、参会人信息和内部业务内容不得写入公共仓库。外部用户或无权访问 OnePoint 的用户，可以提供已授权的会议文本或导出材料；Skill 的其余能力不受影响。

## 草稿检查器

检查器只使用 Python 标准库，不会联网，也不会修改原文：

```bash
python3 plugins/human-internal-writing/skills/writing-human-internal-longform/scripts/check_draft.py \
  path/to/draft.md
```

它会给出带规则名和行号的编辑提示，包括固定标签重复、机械顺序词、抽象词集中、相邻段落重复、标题过碎以及长文缺少行动或风险表达等。

运行测试：

```bash
PYTHONDONTWRITEBYTECODE=1 python3 \
  plugins/human-internal-writing/skills/writing-human-internal-longform/scripts/test_check_draft.py -v

PYTHONDONTWRITEBYTECODE=1 python3 \
  plugins/human-internal-writing/skills/writing-human-internal-longform/scripts/test_skill_contract.py -v
```

## 数据边界

除上面的 OnePoint 官方授权文档入口外，仓库不包含会议原文、具体会议链接、人员信息或真实发布文章。示例全部为合成内容。处理内部材料时，请在获得授权的工作区中操作，并遵守所在组织的数据与发布规范。
