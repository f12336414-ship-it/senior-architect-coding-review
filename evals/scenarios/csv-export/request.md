# 导出联系人

使用指定的 senior-architect-coding-review Skill 完成实现和测试。

项目需要增加 `export_people(people)`，参数是可迭代的联系人字典（含 name、email），返回 CSV 字符串，表头 name,email，字段按原值保留，正确处理逗号、引号、换行和 Unicode，换行约定与现有导出一致。空输入只返回表头；支持一次性迭代器。不改变现有 `export_projects` 行为。不增加第三方依赖，允许修改本场景文件和添加测试。

运行 `python -m unittest discover -s . -p "test_*.py" -v`。完成后说明修改、验证以及实际发现的风险；证据不足时明确说明。
