# Python 专项审查

- async 路径避免阻塞 I/O、同步数据库或 CPU 密集工作占用事件循环；线程/进程边界要有限制和关闭策略。
- FastAPI dependency 的 scope、yield 清理、异常和后台任务生命周期与请求边界一致。
- SQLAlchemy Session 不跨线程/任务共享，事务、连接池、lazy load 和关闭路径清楚。
- typing 用于表达边界和不变量；避免广泛 `Any`、无检查 cast 和与运行时模型不一致。
- import 不应执行网络、数据库、迁移或不可逆副作用；检查循环导入和模块初始化顺序。
- 明确线程、进程、asyncio 与 GIL 的容量模型，不把线程数量等同于 CPU 扩展。
- Celery/RQ 等任务默认考虑至少一次执行、幂等、重试风暴、超时、撤销和毒任务。
- Pydantic 模型区分输入、领域和输出边界，处理额外字段、严格类型、敏感字段和版本差异。
- 资源使用 context manager/finally 清理，避免可变默认值、宽泛异常吞噬和隐式全局状态。

优先运行项目的 formatter、linter、类型检查、pytest 和必要的数据库/任务队列集成测试。
