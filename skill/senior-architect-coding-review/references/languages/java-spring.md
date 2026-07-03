# Java / Spring 专项审查

## 事务与持久化

- 确认 `@Transactional` 位于可被代理调用的边界，避免 self-invocation、private 方法或异步线程使事务失效。
- 检查传播、隔离、只读、回滚异常类型和远程调用是否扩大事务。
- 检查 JPA 懒加载、N+1、Open Session in View、无界集合和序列化触发查询。
- 用批量查询、稳定分页、索引和执行计划验证容量结论。
- 连接池大小、事务时长、超时和重试不能共同导致池耗尽。

## Bean 与并发

- singleton Bean 不保存请求级可变状态；自定义 scope 和销毁回调符合生命周期。
- `@Async`、调度任务和线程池传播必要上下文，限制队列并处理拒绝、关闭和异常。
- 分布式锁具有所有权 token、租约、续期和释放条件；不能把锁当作跨系统事务。

## Web、安全与消息

- 检查 Spring Security filter chain 匹配顺序、默认规则、方法级授权和错误处理。
- 全局异常映射保持错误码、HTTP 状态和敏感信息边界一致。
- MQ 消费默认考虑至少一次投递、幂等、乱序、重试、死信和毒消息隔离。
- 批处理可续跑、幂等、限制事务规模并记录进度。

## 配置、依赖与运行

- 配置属性要在启动或边界处验证，区分缺失、非法和动态刷新语义。
- Feign/WebClient/RestTemplate、JDBC、Redis、MQ client 设置端到端超时、连接池、重试预算和熔断。
- Actuator、管理端点、debug 日志和异常响应不能泄漏 secrets、SQL、token 或内部拓扑。
- 新 starter、AOP、注解处理器和自动配置要检查启用条件、顺序、类路径漂移和生产默认值。

## 测试与证据

- 最低验证：Maven/Gradle 测试和项目静态分析。
- JPA、事务、迁移或查询改动：补 Testcontainers、执行计划、迁移兼容或回滚证据。
- Security、filter chain 或错误契约改动：补端到端或契约测试。
- MQ、批处理和调度任务改动：补幂等、重试、死信、关闭和重跑测试。

不要仅凭注解存在断言事务或安全正确。

阻塞信号：`@Transactional` 因 self-invocation 失效、远程调用包在长事务内、OSIV 掩盖 N+1、自动重试外部副作用无幂等、Security matcher 顺序导致默认放行。
