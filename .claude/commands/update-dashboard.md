---
description: 执行 USDDOLD 看板完整更新流程（抓取数据 → 更新 dashboard.html → 推送 GitHub）
---

请按以下步骤执行 USDDOLD 看板更新：

1. **检查 BSC CSV** — 确认 `input/` 目录下有 BSCScan 导出文件（`export-tokenholders-for-contract-*.csv`）。如果没有，提示用户先从 https://bscscan.com/token/0xd17479997F34dd9156Deef8F95A52D81D265be9c#balances 导出并放入 `input/`。

2. **抓取数据** — 运行 `python3 fetch_holders.py`，等待完成，检查输出确认 Tron、ETH、ARB、Polygon 四条链都成功。

3. **更新看板** — 运行 `python3 update_dashboard.py`，确认输出中 5 条链的 data block 和 SUMMARY block 全部显示 ✓。

4. **提交推送** — 执行：
   ```
   git add dashboard.html
   git commit -m "data: update YYYY-MM-DD"
   git push usddold clean-main:main
   ```
   将 YYYY-MM-DD 替换为今天日期。

5. **确认上线** — 等待约 1 分钟后，访问 https://blackeyhou-stack.github.io/USDD-OLD/dashboard.html 确认看板已更新，数据截止日期显示正确。

如遇到任何错误，参考 `skills/usddold-analysis/SKILL.md` 中的故障排查章节。
