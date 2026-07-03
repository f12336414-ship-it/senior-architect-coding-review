# 安装与升级

本仓库包含两层内容：

- 开源项目层：README、docs、examples、demos、schemas、CI 和评测。
- 运行时 Skill 包：[skill/senior-architect-coding-review](../skill/senior-architect-coding-review)。

安装时只需要复制或安装运行时 Skill 包。建议固定 release tag 或 commit，不要在受控项目中直接跟随 `main`。

## Codex

推荐使用 `$skill-installer` 安装固定版本：

```text
$skill-installer install https://github.com/f12336414-ship-it/senior-architect-coding-review/tree/v0.3.0/skill/senior-architect-coding-review
```

手动安装也可以：

```bash
git clone --depth 1 --branch v0.3.0 https://github.com/f12336414-ship-it/senior-architect-coding-review.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -R senior-architect-coding-review/skill/senior-architect-coding-review "${CODEX_HOME:-$HOME/.codex}/skills/"
```

Windows PowerShell 手动安装示例：

```powershell
git clone --depth 1 --branch v0.3.0 https://github.com/f12336414-ship-it/senior-architect-coding-review.git
$target = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME "skills" } else { Join-Path $HOME ".codex\skills" }
New-Item -ItemType Directory -Force $target | Out-Null
Copy-Item -Recurse -Force "senior-architect-coding-review\skill\senior-architect-coding-review" $target
```

安装后，在新任务中使用：

```text
使用 $senior-architect-coding-review 审查这个 PR。只读审查，先判断是否可走 quick 模式。
```

## Claude Code

复制完整 Skill 目录到用户级或项目级 Skills 目录：

```bash
cp -R skill/senior-architect-coding-review ~/.claude/skills/
```

项目级安装可放在 `.claude/skills/senior-architect-coding-review`。工具权限、审批和沙箱仍由 Claude Code 或 SDK 配置控制；Skill 只提供工作流和规则，不是安全边界。

## Cursor

Cursor 2.4+ 可使用 Agent Skills。复制运行时目录到项目的 `.cursor/skills/` 或用户 Skill 目录。若团队仍依赖 Rules，建议只把项目常驻约束放入 `.cursor/rules/`，不要把整份 Skill 作为 always-on 规则，否则会浪费上下文并削弱渐进加载。

## 其他 Agent

若 Agent 支持 `SKILL.md` 约定，复制完整运行时目录并确认它能按需读取 `references/` 和执行 `scripts/`。若不支持 Skill 机制，可把 `SKILL.md` 作为手动工作流引用，但不要假定 `agents/openai.yaml` 或脚本权限语义兼容。

## 项目接入清单

安装 Skill 后，建议在目标项目中补齐：

- `AGENTS.md` 或 `CLAUDE.md`：从 [templates](../templates) 复制并填入项目事实。
- 构建、测试、静态分析和迁移命令。
- 模块边界、数据所有权、公开契约和禁止修改范围。
- 高风险路径审批角色，例如认证、授权、支付、账务、医疗、租户隔离和生产配置。
- CI 中的报告校验与阻塞策略，见 [integrations.md](integrations.md)。

## 验证安装

在使用者环境中至少做三类验证：

1. 触发验证：用明确提示确认 `$senior-architect-coding-review` 会被加载。
2. 快速路径验证：提交一个局部低风险修改，确认输出不会过度设计。
3. 阻塞路径验证：使用支付重试或数据迁移类模糊需求，确认它会追问关键事实而不是直接给架构。

如果克隆了完整仓库，可运行：

```bash
pip install -r requirements-dev.txt
python tools/validate_repository.py
python -m unittest discover -s skill/senior-architect-coding-review/scripts/tests -v
python evals/run_evals.py --responses evals/fixtures/synthetic-responses.jsonl
```

## 升级

升级前阅读 [CHANGELOG.md](../CHANGELOG.md)。在受控项目中建议：

1. 新建分支。
2. 安装新 tag 到临时 Skill 目录。
3. 用项目真实 PR、历史事故或 demo 对比旧版输出。
4. 若阻塞规则、风险等级或 Schema 语义变化，按破坏性变更处理。
5. 通过后再替换团队默认版本。

## 常见问题

### Skill 没有触发

确认目录名、`SKILL.md` frontmatter 中的 `name` 和提示中的 `$senior-architect-coding-review` 一致。不同 Agent 对 Skill 发现目录的支持不同，必要时重启客户端或新开会话。

### 输出太重

确认请求是否属于 mechanical、low-behavior 或 medium-local。若是，提示中明确要求先判断 fast-path，并提供影响范围和直接验证方式。

### 输出太泛

补齐项目级 `AGENTS.md`、领域文档、测试命令、模块边界和审批角色。这个 Skill 不应该用通用最佳实践替代项目事实。

### 脚本不能运行

脚本依赖 Python 3 和标准库；仓库验证额外使用 `requirements-dev.txt`。若运行器禁止脚本执行，可仍使用 Skill 工作流，但自动化结构校验不可用。
