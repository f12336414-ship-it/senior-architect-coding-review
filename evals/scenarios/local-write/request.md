# 本地笔记重命名

使用指定的 senior-architect-coding-review Skill 完成实现和测试。

这是单进程本地笔记工具，无网络、账号、生产配置和并发写入。请实现 `notes.rename_note(connection, note_id, title)`：去掉标题首尾空白，只接受非空字符串，更新既有记录并返回更新后的字典；不存在则抛 `KeyError`，非法标题抛 `ValueError`。其余记录不变。事务由调用方控制，此函数不得 commit 或 rollback；不修改表结构和已有查询契约。允许修改本场景文件和添加测试，不引入第三方依赖。

运行 `python -m unittest discover -s . -p "test_*.py" -v`。完成后说明修改、验证以及实际发现的风险；证据不足时明确说明。
