# TypeScript / Node.js 专项审查

只在实际修改 TypeScript/Node.js 边界时加载。先确认运行形态：API server、Next.js/SSR、worker、CLI、library、browser 或 edge runtime；不同运行形态的权限、秘密和生命周期不同。

## 异步、进程与运行时

- Promise 必须被 await、返回或显式处理；检查未处理 rejection、并行失败和 fire-and-forget 生命周期。
- 定时任务、队列消费者和后台任务必须有并发上限、重试预算、幂等、停止信号和错误传播。
- 进程处理 SIGTERM/SIGINT、停止接流、等待在途任务并在预算内关闭 HTTP、DB、queue 和 telemetry 连接。
- 检查事件循环阻塞、无界并发、流背压、定时器、AbortController 传播和监听器泄漏。

## Web、认证与输入边界

- Express/Koa/Fastify 中间件顺序正确，认证、授权、解析、限流、路由和错误处理覆盖所有路径。
- DTO 在信任边界执行运行时验证、大小限制和未知字段策略；TypeScript 类型不构成输入验证。
- `any`、双重断言、`!`、宽泛索引签名和 `as unknown as` 不得让不可信数据逃逸到核心模型。
- SSR、Server Actions、API route、edge function 和客户端 bundle 不泄漏秘密、服务端对象或授权决定。
- CORS、cookie、CSRF、session、JWT audience/issuer/expiry 和多租户隔离必须由可验证机制保护。

## 数据、事务与外部副作用

- ORM 查询检查 N+1、过量 select、无界结果、事务、锁、稳定分页、连接池和迁移兼容窗口。
- 外部 API 调用设置超时、取消、重试预算、熔断和幂等键；不要用无限 retry 掩盖未知提交结果。
- 消息消费者默认至少一次投递，检查幂等、乱序、毒消息、死信和重复投递。
- 金额、时间、时区和 decimal 处理要用稳定类型和边界测试，避免浮点和本地时区漂移。

## 包、构建与类型边界

- 新依赖检查锁文件、postinstall、维护状态、许可证、transitive risk 和 bundle 体积。
- ESM/CJS、tree shaking、server/client boundary 和 tsconfig path alias 不应制造运行时解析差异。
- 错误中间件保留 cause、稳定错误码和关联信息，不吞异常或重复响应。

## 测试与证据

- 最低验证：typecheck、lint、test、build。
- API、ORM、队列和认证改动：补集成测试、契约测试和失败路径测试。
- 浏览器或 SSR 改动：验证 bundle 泄漏、hydration、缓存和边缘运行时限制。

阻塞信号：不可信输入只靠 TS 类型、自动重试外部扣款无幂等、后台任务无关闭路径、服务端秘密进入客户端 bundle、认证中间件顺序错误。
