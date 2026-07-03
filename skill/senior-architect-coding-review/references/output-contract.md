# 审查深度与输出契约

## 深度

### Quick

用于 mechanical/low-behavior 或小型 PR。只检查意图、直接正确性、范围漂移和最小验证。最多报告最重要的少量发现，不输出架构综述。

### Standard

用于 Medium 或普通业务 PR。追踪入口、状态、持久化、外部调用、失败、安全和兼容，并运行相关测试。

### High-risk

用于 High/Critical。执行需求门禁、对称反证、专业规则、迁移恢复、独立复核和批准检查。

## 权限

- `review-only`：只输出发现，不改代码。
- `review-and-fix`：用户明确要求后，修复已确认且在范围内的问题。

不要把审查请求解释为修改授权。

## 人类可读发现

```text
[P1][blocking][confidence: high] 标题
位置：文件:行号
场景：具体输入、并发、故障或攻击步骤
影响：用户、数据、安全或运维后果
证据：代码路径、测试、日志或可复现结果
方向：最小可执行修复
```

没有可达场景、实际影响或证据链的问题不得标记 blocking。低置信度意见使用 `advisory`，并说明需要什么证据。

## 机器格式

需要 CI 或归档时，按照仓库 `schemas/review-report.schema.json` 输出 JSON。每个 finding 包含唯一 ID、严重度、处置类型、置信度、位置、场景、影响、证据和最小修复。

P0/P1 默认 blocking；只有风险负责人明确接受的 P1 才能降为 advisory。P2/P3 默认 advisory，除非项目政策明确提升。

合并相同根因的重复发现，使用 `locations` 保存多个位置。多个症状共享一个所有权、事务或边界缺陷时，报告一个系统性问题并列出影响路径。

## 长度控制

先输出 blocking findings，再输出 advisory，最后报告验证和残余风险。Quick 默认不超过 5 个发现；Standard 默认不超过 10 个，超出时聚合根因；High-risk 不设机械数量上限，但避免重复。
