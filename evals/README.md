# Behavioral evaluations

`cases.json` 覆盖 fast-path、需求阻塞、权限边界、Critical 拒绝执行、范围漂移、双写缺陷、不确定性、严重度和兼容性。

评测输入是 JSONL：

```json
{"case_id":"fast-typo","decision":"fast_path","response":"..."}
```

运行：

```bash
python evals/run_evals.py --responses path/to/model-responses.jsonl --output evals/results/model-version.json
```

执行器计算通过率、分类结果、阻塞漏报和 advisory 误报。断言透明、可复现，但只能检测已编码行为，不能替代专家判断。

`fixtures/synthetic-responses.jsonl` 是执行器 smoke fixture，不是 Codex、Claude、Cursor 或其他模型的真实成绩。发布多模型报告时必须记录模型/Agent 版本、Skill commit、权限、工具、提示、运行次数、原始响应和失败样例。
