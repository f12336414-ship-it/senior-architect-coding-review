# 版本策略

项目使用 SemVer：`MAJOR.MINOR.PATCH`。

- MAJOR：触发语义、门禁、风险等级、Schema 或默认权限的破坏性变化。
- MINOR：向后兼容的新语言规则、工具、Schema 可选字段、案例和评测。
- PATCH：误报修复、文档、兼容缺陷和不改变策略含义的脚本修复。

`0.x` 表示早期开发，但仍通过 CHANGELOG 说明破坏性变化。Release 必须包含固定提交、验证结果、已知限制和安装路径。用户在受控环境应固定 tag/commit，不跟随 `main` 自动更新。
