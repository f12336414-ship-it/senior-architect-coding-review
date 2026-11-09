# 评测范围与重放

## 真实执行型任务

[scenarios](scenarios/README.md) 提供隔离代码任务、原始验收测试和判分边界。
将单个任务交给独立 Agent，检查实际代码和运行结果，而非只匹配回答中的关键词。
已保存的输出见 [2026-11-09 实测记录](results/2026-11-09/README.md)。

```bash
python -m unittest discover -s evals -p "test_*.py" -v
```

其中 `test_recorded_outputs.py` 在临时目录重放已保存的 Agent 代码，运行原始验收及新增测试；不调用模型，也不能证明下一次生成一定正确。

## 回答契约 smoke 检查

`cases.json` 覆盖 fast-path、需求阻塞、权限边界、Critical 拒绝执行、范围漂移、双写缺陷、不确定性、严重度和兼容性。

评测输入是 JSONL：

```json
{"case_id":"fast-typo","decision":"fast_path","response":"..."}
```

运行：

```bash
python evals/run_evals.py --responses path/to/model-responses.jsonl --output evals/results/model-version.json
```

执行器计算已编码回答契约的通过率、分类结果、阻塞漏报和 advisory 误报，输出标注 `response_contract_smoke`。它不理解实现语义：回答包含所需词语但同时提出不必要分层，仍可能通过。不能把这些指标当作架构质量、代码正确性或真实生产误报率。

`fixtures/synthetic-responses.jsonl` 是执行器 smoke fixture，不是 Codex、Claude、Cursor 或其他模型的真实成绩。发布多模型报告时必须记录模型/Agent 版本、Skill commit、权限、工具、提示、运行次数、原始响应和失败样例。
