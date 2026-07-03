# Demo：支付失败自动重试

这个 demo 模拟一个常见高风险请求：

> 支付失败时自动重试，减少用户下单失败。

表面看只是加一个重试队列，实际会触碰支付幂等、未知提交结果、重复扣款责任、账务对账和用户通知。资深架构师不能在这些事实未知时直接设计“定时重试所有失败支付”。

## 文件

- [request.md](request.md)：用户原始请求。
- [context.md](context.md)：demo 项目的已知事实和未知项。
- [sample-pr.diff](sample-pr.diff)：一个故意有问题的候选 PR。
- [expected-review.md](expected-review.md)：期望的 Skill 审查路径和结论。
- [review-report.json](review-report.json)：机器可读审查报告示例。

## 如何使用

在仓库根目录向 Agent 输入：

```text
使用 $senior-architect-coding-review 审查 demos/order-payment-retry/sample-pr.diff。
上下文见 demos/order-payment-retry/context.md。
只读审查；如果需求未就绪，请输出阻塞问题、反例和最低可推进下一步，不要直接改代码。
```

## 合格输出应满足

- 先恢复真实意图：降低支付失败，而不是盲目提高重试次数。
- 明确 `payment_intent`、幂等键、失败码分类、未知提交结果恢复和重复扣款责任是阻塞事实。
- 反方攻击候选 PR：超时后 provider 可能已扣款，本地再次创建 charge 会重复扣款。
- 将“重试所有失败支付”标为 P1 blocking，而不是 advisory。
- 给出可推进的下一步：补 provider 语义、设计幂等协议、建立 reconciliation 和人工风险接受记录。
- 不虚构“一定成功”的架构，也不把网络调用和本地事务说成原子操作。
