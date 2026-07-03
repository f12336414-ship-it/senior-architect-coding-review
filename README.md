# senior-architect-coding-review

需求驱动、独立反证、证据裁决和风险治理的架构开发与审查 Skill。

它负责确认问题边界、架构权衡、跨边界风险和交付证据，不试图替代编译器、语言分析器、静态安全扫描、测试或最终人工批准。

## 当前状态

- 版本：`0.3.0`
- 阶段：早期公开版本；尚未宣称经过大规模社区或生产验证
- 许可证：MIT
- 运行时包：[skill/senior-architect-coding-review](skill/senior-architect-coding-review)

## 适用场景

- 需求澄清、架构设计和 ADR
- 高风险 PR、跨模块重构和遗留系统修改
- 数据、事务、消息、兼容迁移和可靠性审查
- 认证授权、支付账务、租户、合规等敏感路径
- C#/.NET、Java/Spring、Go、Rust、TypeScript/Node.js 和 Python 项目的架构加专项审查

不适合作为唯一语言审查器，也不应用于机械格式化、简单文本替换或无架构风险的微小修改。低风险任务会走独立 fast-path。

## 安装

### Codex

在 Codex 中调用 `$skill-installer` 安装仓库内的 Skill 路径：

```text
$skill-installer install https://github.com/f12336414-ship-it/senior-architect-coding-review/tree/v0.3.0/skill/senior-architect-coding-review
```

也可以把 `skill/senior-architect-coding-review` 复制到 `$CODEX_HOME/skills/`。`agents/openai.yaml` 是 Codex 的 UI 元数据，其他 Agent 可以忽略。完整安装、固定版本、升级和排错步骤见 [docs/installation.md](docs/installation.md)。

### Claude Code

Claude Code 官方支持项目级 `.claude/skills/` 和用户级 `~/.claude/skills/`。复制完整 Skill 目录，例如：

```bash
cp -R skill/senior-architect-coding-review ~/.claude/skills/
```

参见 [Claude Code Agent Skills](https://code.claude.com/docs/en/agent-sdk/skills)。Claude 的工具权限仍由 Claude Code/SDK 配置控制，Skill 本身不是沙箱。

### Cursor

Cursor 2.4+ 支持 Agent Skills。将目录复制到项目的 `.cursor/skills/` 或用户 Skill 目录；若团队仍使用 Rules，把项目常驻约束放在 `.cursor/rules/`，不要复制整份 Skill 作为 always-on 上下文。参见 [Cursor Agent 最佳实践](https://cursor.com/blog/agent-best-practices)和 [Cursor 2.4 Skills](https://cursor.com/changelog/2-4)。

### 其他 Agent

如果运行器实现 Agent Skills/SKILL.md 约定，复制完整目录并确认它支持渐进加载和脚本。否则将 `SKILL.md` 作为任务工作流手动引用；不要假定 `agents/openai.yaml`、权限或脚本执行语义兼容。

## 最小使用示例

```text
使用 $senior-architect-coding-review 审查这个 PR。只读审查；先判断是否可走 quick 模式，发现需求不清时不要直接设计。
```

```text
使用 $senior-architect-coding-review 设计订单履约改造。先追问会改变数据所有权、一致性和恢复策略的问题，通过 G1 后再比较方案。
```

```text
使用 $senior-architect-coding-review 修复这个局部空值问题。若满足 low-behavior fast-path，只做最小修改和直接验证。
```

## 工作方式

```text
任务分流
→ fast-path 或需求发现
→ 需求反证与 G1
→ 候选方案与对称攻击
→ G2 与批准
→ 实现/审查
→ 运行证据与 G3
```

风险治理不会用低风险项平均掉身份、数据、兼容或不可逆风险。High 需要领域负责人确认；Critical 需要领域负责人、专业审查者和风险负责人批准，并禁止代理自行执行。

## 项目级上下文

本 Skill 需要项目事实才能作出准确判断。复制并调整：

- [templates/AGENTS.md](templates/AGENTS.md)：Codex 与支持 AGENTS.md 的 Agent
- [templates/CLAUDE.md](templates/CLAUDE.md)：Claude Code

至少填写技术栈、模块和数据所有权、构建测试命令、禁止修改范围、兼容承诺、部署恢复和审批角色。

## 审查深度

- `quick`：mechanical/low-behavior，小型 PR，最多报告少量关键发现。
- `standard`：普通业务 PR，覆盖状态、数据、失败、安全和兼容。
- `high-risk`：完整门禁、专业规则、迁移恢复和独立复核。

审查默认 `review-only`。只有用户明确要求修复后才进入 `review-and-fix`。

## 自动化

- 风险分类：`python skill/senior-architect-coding-review/scripts/assess_change_risk.py --help`
- 项目能力发现：`python skill/senior-architect-coding-review/scripts/detect_project_capabilities.py .`
- 门禁产物校验：`python skill/senior-architect-coding-review/scripts/validate_artifact_structure.py artifact-a.json artifact-b.json --gate G2 --output gate-report.json`
- 动作计划校验：`python skill/senior-architect-coding-review/scripts/validate_action_plan.py action-plan.json`
- CI 与 PR 集成：[docs/integrations.md](docs/integrations.md)
- JSON Schema：[schemas](schemas)

这些工具检查确定性结构和策略，不判断业务语义。

## 示例与评测

- 行为示例：[examples](examples)
- 端到端使用 demo：[demos](demos)
- 评测用例与执行器：[evals](evals)
- 当前评测仅提供可重复的合成基线，不冒充真实多模型或生产验证报告。
- 验证范围与尚未验证项：[docs/validation-status.md](docs/validation-status.md)

## 开发与验证

```bash
pip install -r requirements-dev.txt
python -m unittest discover -s skill/senior-architect-coding-review/scripts/tests -v
python evals/run_evals.py --responses evals/fixtures/synthetic-responses.jsonl
python tools/validate_repository.py
```

GitHub Actions、GitLab CI 和 Azure Pipelines 示例会运行同一组无外部依赖检查。

## 版本与贡献

- 版本策略：[docs/versioning.md](docs/versioning.md)
- 变更记录：[CHANGELOG.md](CHANGELOG.md)
- 贡献指南：[CONTRIBUTING.md](CONTRIBUTING.md)
- 安全策略：[SECURITY.md](SECURITY.md)

社区采用、真实误报/漏报和跨模型表现需要通过公开 issue、fixture 和复现实验逐步积累；仓库不会把尚未完成的验证描述为成熟能力。
