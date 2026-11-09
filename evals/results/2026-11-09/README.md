# 2026-11-09 Skill 行为实测

结论：本次单轮、小样本任务中，没有默认生成技术分层或重复实现已有设施；共享规则边界和支付需求澄清得到保留。这不是“所有任务无问题”的证明。

## 方法与版本

- 基线仓库 commit：`d4766690bdce2d41c1d416016f2a12253149fce1`；执行评测时待测版本为未提交修改，随后收录于 v0.4.0；完整运行时文件 SHA-256 见 [manifest.json](manifest.json)。
- Codex Desktop 的独立上下文子代理，每个场景 1 次，不传入预期答案、先前结论或其他场景。没有指定模型覆盖；工具未暴露精确后端模型构建号，因此不编造模型版本。
- 原始任务、代码与验收测试见 [scenarios](../../scenarios/README.md)。每次仅传入单个目录、其 request.md 和 Skill 路径。
- 允许修改单个临时目录及添加测试；禁止改弱原测试、访问其他测试目录、联网或操作真实服务。使用 Windows、Python 3.13.13、标准库 SQLite/CSV/unittest。
- 原始三个编码输入都先运行失败；保留失败原因与退出码，不把它们当模型失败。
- 产出后由主代理重新运行测试，另一独立上下文审查者检查原需求、代码、规则 diff 和测试，没有读取作者总结。独立上下文仍不等于不同模型或人类专家。
- `response.txt` 保存最终回复内容，仅移除链接绝对路径和样式；不是完整交互日志。`verification.txt` 是主代理重新运行的实际输出。

## 实际结果

| 场景 | 初始基线 | 产出后 | 结构/复用证据 |
| --- | --- | --- | --- |
| [局部写入](local-write/response.txt) | 6 方法，9 个子项错误，退出 1 | 11 方法通过，退出 0 | [notes.py](local-write/notes.py) 只补全原函数，参数化 UPDATE 后复用 get_note；没有 commit/rollback、schema 或新层 |
| [CSV 导出](csv-export/response.txt) | 5 方法，4 个错误，退出 1 | 8 方法通过，退出 0 | [exports.py](csv-export/exports.py) 一行复用既有 `_csv_text`，不重写转义或复制导出设施 |
| [共享状态规则](shared-rules/response.txt) | 3 方法，42 个子项错误，退出 1 | 7 方法通过，退出 0 | [tickets.py](shared-rules/tickets.py) 保留共享规则所有者；两入口不复制规则，无状态机依赖 |
| [支付需求未知](payment-unknown/response.txt) | 无网关契约、无真实服务 | discovery / G1 NOT_READY；未改文件 | 追问幂等键、未知结果、查单恢复、重试次数及负责人；不把 order_id 当作幂等保证 |

三项代码任务合计 **26 个测试方法通过**，其中 14 个为原始验收、12 个为 Agent 新增；参数化子项不重复计入方法数。支付文件前后 SHA-256 均为 `509e3920aa6c73425152cd9e6318398825cde3392740109f63666a4503a30272`。

## 反方复核与裁决

独立审查者没有报告可复现的 P0–P3 缺陷，并完成三个目录的 unittest（11/8/7，退出 0）、额外 SQLite CHECK 约束失败探针（退出 0）、原始 request/测试文件哈希对比（6 项一致）和 `git diff --check`（退出 0）。原作者明确指出的 medium-local 独立复核缺口，由这次第二遍复核补齐。

复核区分了以下情况：

- 普通写入走轻量路径不代表绕过安全：仅限既有所有者、schema 和事务语义，未知提交结果、授权变更、迁移和困难回滚仍升级。
- 删除测试只是反事实分析，不授予删除文件权限；安全、事务与共享不变量可以证明单一实现边界的价值。
- CSV 原值保留不等于电子表格公式安全；没有把约定内的原值输出误报为本次缺陷。
- Ticket 的公开 state 属性是既有接口，不借本次任务擅自封装或改造；当前接口外直接赋值不在已验证状态转换保证内。

支付响应与未修改哈希由主代理复核；独立审查者没有做真实支付网关或专业支付复核。

## 重放

```bash
python -m unittest discover -s evals -p "test_*.py" -v
```

其中三个 `RecordedOutputTests` 会在新临时目录组合原始输入和保存的代码，运行同样的 26 个测试。它验证已保存产物，**不会重新调用 Agent**。要测新版本模型/Skill，须重新复制场景并独立执行，再审查新的输出，不能只重放旧产物。

仓库原有 26 项单元测试、10 个回答契约 smoke、仓库结构校验及 Skill quick_validate 也已执行。Windows quick_validate 使用 `python -X utf8`；验证依赖复用 requirements-dev.txt，安装在临时 venv，不更改全局 Python。

加上 3 项存档重放，仓库单元测试合计 29 项通过，见 [仓库验证输出](repository-verification.txt)。两个本机安装副本（Codex / Claude Code）各同步 7 个运行时文件并逐个核对 SHA-256；未改无关配置。该验证日志记录的是发布前状态；后续发布见 [v0.4.0](https://github.com/f12336414-ship-it/senior-architect-coding-review/releases/tag/v0.4.0)。

## 限制与未验证项

- 场景是人工构造的小项目，不是用户生产项目，也没有旧版/新版 Agent A/B 或统计显著性。
- 未实际运行 C#/.NET、Java/Spring 等框架任务，不能推断跨语言同样稳定。
- 没有生产并发、磁盘故障、真实 SDK、长周期任务、多模型重复运行或人类专家评测。
- 旧关键词执行器仍只测回答契约，不测语义质量；报告已显式区分，未靠增加目录名禁词来声称修复。
