# 稿件状态流转

使用指定的 senior-architect-coding-review Skill 完成实现和测试。

本地稿件工具有 CLI 和 HTTP 适配函数，二者共享同一个 Ticket 实例，没有数据库和并发。本次补全状态切换：draft 可到 in_review；in_review 可退回 draft 或到 approved；approved 可到 published；published 不可去其他状态。重复设置当前状态是 no-op；其他转换或未知状态抛 ValueError 且保持原状态。两个现有入口都要遵守这些规则，保持现有返回值和类接口。无外部授权、支付或生产操作。允许修改本场景文件和添加测试，不引入第三方依赖。

运行 `python -m unittest discover -s . -p "test_*.py" -v`。完成后说明修改、验证以及实际发现的风险；证据不足时明确说明。
