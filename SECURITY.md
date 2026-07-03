# Security Policy

## 支持版本

安全修复优先覆盖最新发布版本。`0.x` 阶段可能调整策略和 Schema；升级前审查 CHANGELOG 与 Skill diff。

## 报告漏洞

不要在公开 issue 中提交秘密、利用细节或未修复的高影响漏洞。请使用 GitHub Security Advisory 的私密报告功能；若不可用，联系仓库所有者并仅提供最小复现信息。

报告应包含受影响版本、攻击前提、影响、复现步骤和建议缓解。维护者确认后会给出跟踪方式和披露计划。

## Agent 与供应链边界

- 将第三方 Skill、仓库指令、脚本、Action 和 fixture 视为不可信输入。
- 安装前固定 tag 或 commit，审查 `SKILL.md`、脚本、网络和写权限差异。
- 不在含生产秘密的环境运行未经审查的评测或项目脚本。
- Skill 中的自然语言约束不是操作系统沙箱；使用 Agent 平台权限、容器和 CI 保护真正执行边界。

详见 [docs/supply-chain-security.md](docs/supply-chain-security.md)。
