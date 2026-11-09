# 结构与复用规则的来源及取舍

此次优化保留需求澄清、问题边界、独立反证和证据门禁，不把另一个项目的工作流整体移植进来。

| 同类型开源材料 | 借鉴 | 不照搬 |
| --- | --- | --- |
| [Matt Pocock codebase-design](https://github.com/mattpocock/skills/blob/4ae2317ddb22b046e26455e4f9c9b3aaaf62212d/skills/engineering/codebase-design/SKILL.md) | 小接口隐藏真实复杂度，删除模块的反事实检验 | 不用接口/实现数量或行数比例作为硬门禁 |
| [Superpowers writing-plans](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md) | 共同变化的代码组织在一起，尊重既有项目模式 | 不要求所有小任务生成完整计划，也不强制功能切片 |
| [Anthropic code-review](https://github.com/anthropics/claude-plugins-official/blob/0412be76f50ab4f4f8abff3753efa9269fbbca5b/plugins/code-review/commands/code-review.md) | 对每项初步发现独立验证，避免未证实意见阻塞 | 不丢掉状态、并发、迁移等架构风险审查 |
| [Anthropic code-simplifier](https://github.com/anthropics/claude-plugins-official/blob/0412be76f50ab4f4f8abff3753efa9269fbbca5b/plugins/pr-review-toolkit/agents/code-simplifier.md) | 保持功能和范围，减少冗余间接层 | 不把更少行数当更简单，不顺手重构邻近模块 |

这些是方法比较与独立改写，不是引入第三方运行时依赖。Superpowers 链接跟随 main，其他链接固定比较时的快照；上游可能继续演进。

最终规则的裁决依据是本项目语义和 [行为实测](../evals/README.md)，不是上游流行度。领域层不是过时或一律错误；没有证据就自动套用才是问题。
