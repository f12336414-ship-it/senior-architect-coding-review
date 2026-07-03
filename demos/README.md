# Demos

这些 demo 展示 Skill 在真实形态任务中的使用方式：输入、上下文、危险方案、期望审查输出和机器可读报告。

它们是可复现的示范，不是生产项目验证，也不代表多模型基准。真实采用率、误报率和漏报率仍需要通过公开 PR、issue 和复现实验积累。

## 可用 demo

- [order-payment-retry](order-payment-retry)：支付失败自动重试需求。重点展示需求未就绪时停止设计、反方攻击、P1 阻塞发现和后续需要补齐的事实。

建议运行方式：

```text
使用 $senior-architect-coding-review 审查 demos/order-payment-retry/sample-pr.diff。
只读审查；结合 demos/order-payment-retry/context.md；发现支付幂等和未知提交结果未确认时不要直接给最终架构。
```
