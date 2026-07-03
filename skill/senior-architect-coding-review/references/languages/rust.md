# Rust 专项审查

只在实际修改 Rust 边界时加载。先确认 crate 类型：library、CLI、service、embedded、FFI、WASM 或 async worker；不同类型的 panic、错误和资源策略不同。

## 所有权、生命周期与 API

- 所有权边界表达真实资源和并发所有者；不要用广泛 `Arc<Mutex<_>>` 消除设计问题。
- 生命周期参数应表达借用关系；若复杂度超过收益，重新检查所有权或数据结构，而非堆叠标注。
- public API 的 trait bound、feature flag、error type 和序列化格式是兼容契约，不能随意破坏。
- 检查 `clone` 是否隐藏大对象复制、锁竞争或所有权不清，而非机械禁止。

## Unsafe、FFI 与内存安全

- 将 `unsafe` 收敛到小而有文档的不变量边界，并用安全 API 封装。
- 审查别名、生命周期、对齐、布局、初始化、drop 顺序、panic crossing FFI 和线程所有权。
- FFI 输入必须验证长度、空指针、编码、所有权转移和释放责任。
- `unsafe` 变更至少需要独立复核；不能只靠测试证明内存安全。

## Async、并发与资源

- 不混用不兼容 async runtime、阻塞调用和 executor；阻塞工作使用受控边界。
- 跨线程和异步边界确认 `Send`/`Sync`、取消安全、任务泄漏和锁跨 await。
- channel、stream、select、timeout 和 retry 要有背压、关闭语义和错误传播。
- 进程级服务处理 SIGTERM、drain、连接关闭和任务等待预算。

## 错误、panic 与数据边界

- 库代码避免不可恢复 `panic!`、`unwrap`、`expect`；明确进程级 panic 策略和清理影响。
- 错误类型保留语义、来源和稳定边界，避免将内部实现或敏感内容暴露给调用方。
- 检查整数溢出、资源上限、递归深度、反序列化边界和拒绝服务输入。
- 加密、认证、解析器或协议代码不得引入未审计自制实现。

## 测试与证据

- 最低验证：`cargo fmt --check`、`cargo clippy --all-targets`、`cargo test`。
- unsafe、并发或解析器改动：按风险使用 Miri、loom、fuzzing 或 sanitizer。
- public API 变化：提供兼容性说明、迁移路径和下游影响证据。

阻塞信号：无文档 `unsafe`、锁跨 await 导致死锁风险、库中无条件 panic、FFI 所有权不清、外部输入无界反序列化。
