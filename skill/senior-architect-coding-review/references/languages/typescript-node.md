# TypeScript / Node.js 专项审查

- Promise 必须被 await、返回或显式处理；检查未处理 rejection、并行失败和 fire-and-forget 生命周期。
- Express/Koa/Fastify 中间件顺序正确，认证、授权、解析、限流、路由和错误处理覆盖所有路径。
- DTO 在信任边界执行运行时验证、大小限制和未知字段策略；TypeScript 类型不构成输入验证。
- `any`、双重断言、`!` 和宽泛索引签名不得让不可信数据逃逸到核心模型。
- ORM 查询检查 N+1、过量 select、无界结果、事务、锁、分页和连接池。
- SSR、Server Actions、API route 和客户端 bundle 不泄漏秘密、服务端对象或授权决定。
- 进程处理 SIGTERM/SIGINT、停止接流、等待在途任务并在预算内关闭连接。
- 错误中间件保留 cause、稳定错误码和关联信息，不吞异常或重复响应。
- 检查事件循环阻塞、无界并发、流背压、定时器和监听器泄漏。

优先运行项目的 typecheck、lint、test、build 和集成测试；不要假设编译通过等于运行时边界安全。
