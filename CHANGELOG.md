# Changelog

本项目遵循 [Semantic Versioning](https://semver.org/)。

## [Unreleased]

### Planned

- 真实开源 PR fixtures 和多模型行为基线。
- 更多框架专项规则与可复现误报/漏报报告。

## [0.4.0] - 2026-11-09

### Changed

- 在所有编码路径前核对项目、框架、标准库和官方 SDK 能力；只为可证明的缺口自研。
- 取消默认技术分层倾向，增加按共同变化选结构、抽象删除测试和双向反证；保留需求澄清与高风险门禁。
- 允许有直接证据的普通局部写入走 medium-local，不放宽授权、关键不变量、迁移和未知提交结果的边界。

### Added

- 4 个隔离行为场景、3 个已保存代码重放测试、26 项实测行为测试及独立反方复核记录；明确区别回答关键词 smoke 与语义验证。
- 同类型开源 Skill 的方法取舍记录，见 [复用设计说明](docs/reuse-design-notes.md)。

### Upgrade notes

- 0.x 工作流调整：普通局部数据库写入在有直接证据且满足全部条件时可以进入 medium-local，不再仅凭“写数据库”升级；受控项目升级前应审查 fast-path 差异。
- Skill 名称、安装路径、现有 Schema 与高风险批准要求不变；评测 JSON 新增范围标记，不把关键词通过率当作语义质量证明。

## [0.3.0] - 2026-07-04

### Added

- 可复现端到端使用 demo，展示从模糊支付重试需求到阻塞性审查结论的完整路径。
- 详细安装文档，覆盖 Codex、Claude Code、Cursor、固定 tag、升级和排错。
- 更完整的 Go、Rust、Python、TypeScript/Node.js 专项审查清单。

### Changed

- README 默认安装路径改为固定 release tag，避免用户跟随 `main` 漂移。
- 示例索引增加 demo 入口，区分静态示例、可复现 demo 和合成评测。

## [0.2.0] - 2026-07-04

### Added

- 独立 mechanical、low-behavior 和 medium-local fast-path。
- C#/.NET、Java/Spring、Go、Rust、TypeScript/Node.js、Python 专项路由。
- 危险动作计划校验、输出契约、Skill 组合和供应链约束。
- README、贡献、安全、版本、模板、Schema、CI 示例、案例和合成行为评测。

### Changed

- 仓库拆分为开源项目层和独立可安装 Skill 包。
- 项目能力发现扩展到 CI、基础设施、迁移、workspace 和命令候选。

## [0.1.0] - 2026-07-04

### Added

- 需求发现、独立反证、G1/G2/G3、风险分级、门禁校验和 16 项脚本测试。
