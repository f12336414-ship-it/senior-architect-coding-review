# Go 专项审查

只在实际修改 Go 边界时加载。先确认入口类型：HTTP/gRPC、CLI、worker、library、batch 或基础设施工具；不同入口的取消、日志、退出和错误语义不同。

## Context 与生命周期

- `context.Context` 从入口向下传递，不存入长期结构，不用 `context.Background()` 或 `TODO()` 静默截断请求取消。
- goroutine 必须有所有者、退出信号、错误传播、并发上限和等待/清理路径；不得用 fire-and-forget 隐藏失败。
- `errgroup`、worker pool、ticker 和 long polling 要说明取消、关闭顺序、panic 处理和 backpressure。
- `time.Ticker`、`Timer`、连接、文件、response body 和订阅必须释放；循环内 `defer` 要确认资源规模。

## 并发与数据竞争

- 明确 channel 的发送者、关闭者和关闭时机；避免重复关闭、向已关闭 channel 发送和永久阻塞。
- 检查共享 map、slice、缓存、全局变量和测试中的数据竞争；高风险并发改动运行 `go test -race`。
- 锁范围不得跨网络、磁盘、数据库或不受控 callback；避免读写锁升级、锁顺序反转和条件变量丢通知。
- 原子操作只表达简单状态，不要用 `atomic` 绕开所有权和不变量设计。

## 错误、接口与类型边界

- 使用 `%w` 保留错误链，使用 `errors.Is/As` 判断语义；不要用字符串比较控制流程。
- 错误必须区分用户可见、可重试、不可重试、未知提交结果和内部故障；HTTP/gRPC 映射保持稳定契约。
- 接口由消费者需要定义，避免为单一实现或 mock 提前制造大接口。
- 检查 typed nil interface、零值语义、nil receiver、指针逃逸和复制含锁结构的问题。
- 泛型约束要表达真实语义，不能把 `any` 当作逃避模型边界。

## I/O、HTTP 与数据库

- HTTP client、database/sql、gRPC 和消息客户端设置端到端超时、连接池、重试预算和响应体关闭。
- 不要无界读取 request/response body；流式处理要有大小限制、取消和背压。
- SQL 查询检查事务边界、隔离级别、连接泄漏、N+1、稳定分页和批处理规模。
- JSON/YAML 解析处理未知字段、大小限制、时间格式、数值精度和敏感字段。

## 测试与证据

- 最低验证：`gofmt`、`go vet`、`go test ./...`。
- 并发、缓存、锁或 worker 改动：加 `go test -race`，必要时加压力或故障注入测试。
- 公共 API、序列化或数据库语义变化：补契约测试或迁移回滚证据。

阻塞信号：无所有者 goroutine、自动重试外部副作用无幂等、忽略 context 取消、并发写 map、未关闭 response body、跨系统事务假设。
