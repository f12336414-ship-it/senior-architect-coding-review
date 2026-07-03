# Low-risk fast-path

请求：修复订单列表为空时访问第一项导致的空指针；已有空列表测试入口，不改变 API。

```text
路径：low-behavior
范围：OrderListPresenter 的空列表分支和邻近测试
风险：局部、可逆、无数据写入、无公开契约变化
修改：空列表返回 EmptyState，不访问 items[0]
验证：空列表、单项列表测试；类型/静态检查
未验证：无
```

不会生成 ADR，不重构列表模块，不引入 Result 抽象。若发现 EmptyState 的产品语义未确认，则退出 fast-path 并追问。
