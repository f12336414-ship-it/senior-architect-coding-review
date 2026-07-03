# 语言与框架专项路由

先从清单、锁文件、构建配置和入口确认实际技术栈。每次只加载匹配文件；多语言仓库仅为被修改的边界加载对应规则。

| 技术栈 | 参考文件 |
| --- | --- |
| C#、.NET、ASP.NET Core、EF Core | [languages/dotnet.md](languages/dotnet.md) |
| Java、Spring、JPA/Hibernate | [languages/java-spring.md](languages/java-spring.md) |
| Go | [languages/go.md](languages/go.md) |
| Rust | [languages/rust.md](languages/rust.md) |
| TypeScript、Node.js、Express/Koa/Fastify | [languages/typescript-node.md](languages/typescript-node.md) |
| Python、FastAPI、SQLAlchemy、Celery/RQ | [languages/python.md](languages/python.md) |

专项规则是风险提示，不是无条件缺陷。报告前确认版本、框架配置、调用方和可达场景。语言惯例与项目 ADR 冲突时优先遵循已确认业务契约和项目决策；若项目规则本身造成当前风险，提供证据并请求裁决。

专项审查不替代编译器、类型检查、分析器、race detector、数据库计划和运行测试。优先运行仓库已有工具。
