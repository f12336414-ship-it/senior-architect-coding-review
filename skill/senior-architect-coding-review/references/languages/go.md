# Go 专项审查

- `context.Context` 从入口向下传递，不存入长期结构，不用 `context.Background()` 截断请求取消。
- goroutine 必须有所有者、退出信号、错误传播、并发上限和等待/清理路径。
- 明确 channel 的发送者、关闭者和关闭时机；避免重复关闭、向已关闭 channel 发送和永久阻塞。
- 检查共享状态、map、切片和测试中的数据竞争；高风险并发改动运行 `go test -race`。
- 使用 `%w` 保留错误链，使用 `errors.Is/As` 判断语义；不要用字符串比较控制流程。
- `defer` 放在资源成功获得之后，注意循环内 defer、返回值和关闭错误。
- 接口由消费者需要定义，避免为单一实现或 mock 提前制造大接口。
- 检查 typed nil interface、零值语义、指针逃逸和 nil receiver 行为。
- HTTP/数据库客户端设置超时、连接池和响应体关闭；不要无界读取或启动任务。

优先运行 `gofmt`、`go vet`、`go test ./...`、`go test -race` 和项目已有静态分析。
