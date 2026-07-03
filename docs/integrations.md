# 团队审查与 CI 集成

## 通用流程

1. Agent 以 `review-only` 生成符合 `schemas/review-report.schema.json` 的报告。
2. CI 校验报告、风险和 gate artifact 的结构。
3. P0/P1 blocking findings 令作业失败；P2/P3 作为 advisory 归档。
4. High/Critical 检查批准角色和证据，不允许报告本身代替 GitHub/GitLab/Azure 的保护规则。
5. 上传 JSON 报告和测试结果为 artifact，并由人工完成最终批准。

Provider-neutral 输入、输出、权限和记录要求见 [automation-contract.md](automation-contract.md)。

可以使用 `python tools/evaluate_review_report.py review-report.json --summary review-gate.json` 将 P0/P1 blocking finding 映射为非零 CI 状态。

| 风险 | 最低 CI 策略 |
| --- | --- |
| Low | 相关测试、静态检查、quick 报告 |
| Medium | 集成/契约或失败路径测试、standard 报告 |
| High | G2 artifact、独立审查、领域负责人批准、分阶段发布 |
| Critical | CI 只验证证据；禁止自动执行，使用受保护环境和人工批准 |

## GitHub

仓库的 `.github/workflows/validate.yml` 验证 Skill、Schema、脚本和合成评测。接入业务仓库时，可增加一个只读审查 job，将报告作为 artifact 上传，再用最小权限 bot 发布摘要。不要给来自 fork 的不可信代码生产秘密或写 token。

PR 摘要格式：blocking findings、advisory findings、验证、未验证风险、批准状态。GitHub Check Run 或 PR comment 只负责展示；分支保护和 required checks 才负责阻塞。

## GitLab

`.gitlab-ci.yml` 提供无外部依赖的验证示例。业务仓库可把 JSON 报告保存为 artifact，并根据 blocking findings 返回非零状态。MR bot 使用最小 `api` 权限，避免对 fork pipeline 暴露变量。

## Azure Pipelines

`azure-pipelines.yml` 使用相同测试和评测命令。高风险环境应把审批放在受保护 Environment，而不是相信 Agent 生成的 `approved: true`。

## 静态分析组合

- Semgrep：项目规则和快速安全模式。
- CodeQL：跨过程安全与数据流。
- Qodana：JetBrains 技术栈质量门禁。
- ArchUnit/Import Linter/dependency-cruiser：架构适应度函数。
- 单元、集成、契约、迁移和恢复测试：行为证据。

先运行各工具，再把结果作为审查证据；不要让 LLM 重复猜测工具能够确定的事实。覆盖率是风险线索，不是正确性证明。

## 权限建议

审查 job 默认只读：`contents: read`、`pull-requests: read`。只有独立发布摘要的 job 才获得写权限，并且不得在执行不可信仓库脚本的同一 job 中使用写 token。
