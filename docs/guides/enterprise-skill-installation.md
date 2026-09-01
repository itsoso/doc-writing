# 企业运行时 Skill 安装与级联

`doc-writing` 是公共入口。它可以在没有公司连接器的环境中完成通用写作，也可以在快手受控运行时级联已安装的 Docs、Kim 和 Onepoint 能力。

## 安装边界

公共仓库负责：

- `$doc-writing`、编辑与发布 Skill；
- 依赖能力的名称、版本契约、路由和阻塞规则；
- 可重复的依赖检查和人工可审阅的安装计划。

公司运行时负责：

- `docs-cli`、`docs-word` 及 `docs-*` 子 Skill；
- `kim-sender-context`、`kim-cli` 及 `kim-im`；
- 授权、只读优先的 Onepoint 会议读取能力（例如 `onepoint-meeting-read`、`onepoint` 或 `onepoint.calendar-read/v1`）。

这些连接器不从 GitHub 公共仓库复制，也不把企业数据、内部 URL、文档 ID、会话信息或凭证写入文章产物。

## 推荐流程

1. 安装公共插件：

   ```bash
   codex plugin marketplace add itsoso/doc-writing
   codex plugin add human-internal-writing@doc-writing
   ```

2. 在已授权的企业运行时检查能力：

   ```bash
   python3 scripts/check_dependencies.py --profile kuaishou-internal --json
   ```

3. 如果结果是 `blocked`，先生成安装计划并由管理员审核：

   ```bash
   python3 scripts/check_dependencies.py \
     --profile kuaishou-internal \
     --print-install-plan \
     --enterprise-marketplace <approved-enterprise-marketplace>
   ```

   检查器只输出建议，不会静默执行企业安装。管理员在受控 Marketplace/运行时中完成安装、授权和版本校验。

4. 再次运行 `--json`。只有所有 `required` 能力为 `ready`，才可以读取 Kim、Docs 或 Onepoint；否则保持 `blocked`。

## 级联规则

`$doc-writing` 先完成来源分类，再把任务交给最小能力集合：

```text
$doc-writing
  ├─ editorial-longform → writing-human-internal-longform
  ├─ internal-docs      → docs-cli → docs-search/docs-word/docs-meeting-record
  ├─ kim-content        → kim-sender-context/kim-cli → kim-im
  └─ onepoint-meeting   → onepoint read-only adapter
                         └─ (meeting-record source may use kim-vc or docs-meeting-record)
```

“级联”表示按声明加载和路由，不表示绕过权限自动获取企业 Skill。能力提供者必须可被当前运行时发现，并且满足各自的授权、只读、分页和回读要求。

## 故障处理

- `blocked`：缺少必需能力，停止读取并列出缺失项；
- 能力名存在但版本/命令不匹配：按提供者 Skill 的当前帮助和版本门禁处理；
- Onepoint 返回错误会议、附件不可读或录制状态冲突：保留阻塞，不用其他会议替代；
- Docs/Kim 写操作：除读取能力就绪外，还要有明确的用户授权、唯一目标解析和远端回读。
