# doc-writing：从个人写作方法到可复用工程

## 目标

把一套已经验证过的写作习惯沉淀为可重复的工程流程：从 OKR 主线和真实场景出发，形成一个中心判断，用 Kim/Docs 等授权来源建立证据账本，经过叙事和技术复核，生成带图 Markdown，必要时写入内网 Docs 并回读，同时维护专栏索引。

公开 GitHub 仓库只发布方法、协议、校验器和已批准的公开示例；Kim、Docs、Onepoint 等企业连接器在受控运行时提供数据，不进入仓库。

## 作者方法的工程化表达

| 写作习惯 | 工程对象 | 通过条件 |
|---|---|---|
| 从 OKR 主线和真实问题开始 | `article-brief.json` | 明确读者、改变、主线和中心判断 |
| 保留现场，不写空泛观点 | evidence ledger | 每个关键判断有来源或明确标为推断 |
| 事实、观察、推断、方案分开 | Claim ID + evidence status | 不把 Unknown 写成确定结论 |
| 一篇文章只保留一条叙事主线 | outline / preservation map | 场景、机制、反例、行动互相支撑 |
| 文章至少有一张能解释判断的图 | `image-manifest.json` | 1–3 张，含 alt、图注、章节和来源 |
| 结尾必须能进入行动 | owner / baseline / deadline | 有验收证据和停止或回滚条件 |
| Markdown 是唯一可编辑源 | release receipt | Docs 由 Markdown 派生并完成远端回读 |

## 两种运行面

### 企业内网运行面

`doc-writing` 根据来源路由到 `kim-sender-context`、`kim-cli`、`docs-cli`、`docs-word`、`docs-meeting-record` 等已安装 Skill。所有读取遵守本地/只读、OBO、权限、目标解析和回读规则；文章 Docs 与维护索引都通过 `publishing-kstack-articles` 完成。

### GitHub 公开运行面

公开运行面不读取 Kim/Docs，也不携带内部数据。它只使用公开资料或脱敏 fixture，运行 `scripts/check_public_repo.py`、文章质量校验和 Skill 测试。只有 `clearance.schema.json` 所描述的三方审批记录存在时，才允许把 `public_candidate` 提升为 `public`。

## 推荐仓库布局

```text
doc-writing/
├── plugins/human-internal-writing/
│   └── skills/
│       ├── doc-writing/
│       ├── writing-human-internal-longform/
│       └── publishing-kstack-articles/
├── schemas/                    # brief、evidence、image、clearance、receipt
├── scripts/                    # 本地和 CI 可重复校验
├── docs/guides/                # 架构、路由、发布闸门
├── tests/                      # 脱敏 fixture，不放内网原文
└── public/                     # 仅允许经过 allowlist 的公开文章
```

当前企业工作树应作为私有源；公开仓库从 allowlist 重新导出，而不是从当前工作树直接镜像。

## 一篇文章的状态机

```text
internal
  → markdown_verified
  → article_docs_verified
  → index_synced
  → docs_verified

public_candidate
  → public_scan_passed
  → legal_security_business_clearance
  → public
```

任何来源不明、权限不足、敏感信息命中、图像来源不清、Docs/索引回读不一致，都必须停在阻塞状态。
