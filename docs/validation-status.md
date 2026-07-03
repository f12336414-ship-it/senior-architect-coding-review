# Validation status

## 已验证

- Python 风险、门禁、动作计划和能力发现脚本单元测试。
- Skill 包 UTF-8、frontmatter、相对链接和渐进加载结构。
- JSON Schema 可解析，代表性 G2 和 review report 产物通过仓库校验。
- 10 个透明合成行为用例覆盖 fast-path、需求阻塞、Critical 拒绝、范围、安全、双写、证据和兼容。
- GitHub、GitLab 和 Azure 的无外部依赖验证命令保持一致。

## 尚未验证

- 尚无足够真实生产项目样本计算可靠的误报率和漏报率。
- 尚未发布 Codex、Claude Code、Cursor、Gemini CLI 的统一多次运行对比。
- 语言专项规则尚未在各框架的大规模 PR 集合上校准。
- 社区维护者、Star、Fork、外部采用和长期兼容性仍需时间积累。

合成 fixture 只能证明评测器和规则断言可运行，不能证明模型达到资深架构师水平。提交真实评测时必须保留原始响应、版本、权限、工具、Skill commit、失败样例和专家标注。
