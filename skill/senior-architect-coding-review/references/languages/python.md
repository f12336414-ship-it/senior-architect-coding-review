# Python 专项审查

只在实际修改 Python 边界时加载。先确认运行形态：同步 Web、ASGI、CLI、Celery/RQ、notebook、data job 或 library；运行形态决定并发、生命周期和部署风险。

## Async、线程与任务

- async 路径避免阻塞 I/O、同步数据库或 CPU 密集工作占用事件循环；阻塞工作必须进入受控线程池、进程池或外部 worker。
- `asyncio.create_task`、background task 和 fire-and-forget 必须有所有者、错误记录、取消、超时和关闭路径。
- 明确线程、进程、asyncio 与 GIL 的容量模型，不把线程数量等同于 CPU 扩展。
- 进程退出、SIGTERM、容器停止和 worker recycle 时，要能停止接流、等待在途任务并释放连接。

## Web、模型与边界验证

- FastAPI dependency 的 scope、yield 清理、异常和后台任务生命周期与请求边界一致。
- Pydantic 模型区分输入、领域和输出边界，处理额外字段、严格类型、敏感字段、默认值和版本差异。
- typing 用于表达边界和不变量；避免广泛 `Any`、无检查 cast、`type: ignore` 泛滥和与运行时模型不一致。
- 错误处理保持稳定响应契约，不泄漏 traceback、内部类型、SQL、token 或个人敏感信息。

## 数据、事务与任务队列

- SQLAlchemy Session 不跨线程/任务共享，事务、连接池、lazy load、flush/commit 和关闭路径清楚。
- 数据库查询检查 N+1、无界结果、稳定分页、锁等待、迁移兼容窗口和连接池耗尽。
- Celery/RQ 等任务默认考虑至少一次执行、幂等、重试风暴、超时、撤销、毒任务和死信处理。
- 外部副作用要有幂等键、重试预算和未知提交结果恢复；不能把 Python 异常捕获当作业务补偿。

## 模块初始化与供应链

- import 不应执行网络、数据库、迁移或不可逆副作用；检查循环导入和模块初始化顺序。
- 避免隐式全局状态、可变默认值、monkey patch 漂移和测试污染。
- 新依赖要检查维护状态、许可证、锁文件、构建脚本、native extension 和供应链风险。

## 测试与证据

- 最低验证：项目 formatter、linter、类型检查和 `pytest`。
- 数据库、队列、异步和外部 API 改动：补集成测试、失败路径测试和超时/取消测试。
- 高风险迁移：提供回填、回滚、重跑幂等和观测指标。

阻塞信号：异步路径阻塞事件循环、Session 跨线程共享、任务无幂等自动重试、import 执行生产副作用、广泛吞异常后继续提交状态。
