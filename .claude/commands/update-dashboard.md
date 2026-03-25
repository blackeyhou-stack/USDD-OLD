---
description: 执行 Token 持币看板完整更新流程（检查数据 → 抓取链上数据 → 更新 dashboard.html → 推送 GitHub）
---

请按以下步骤执行看板更新，每步完成后告知结果再继续：

1. **检查 BSC CSV** — 确认 `input/` 目录下有 BSCScan 导出文件（`export-tokenholders-for-contract-*.csv`）。如果没有，提示用户先从 BSCScan 对应 Token 的 holders 页面导出 CSV 并放入 `input/`。

2. **抓取链上数据** — 运行 `python3 fetch_holders.py`，等待完成，检查输出确认各链均成功抓取并保存到 `output/`。

3. **更新看板** — 运行 `python3 update_dashboard.py`，确认输出中每条链的 data block 和 SUMMARY block 全部显示 `✓`。如有 `⚠️` 警告，分析原因并告知用户。

4. **提交推送** — 执行：
   ```bash
   git add dashboard.html
   git commit -m "data: update $(date +%Y-%m-%d)"
   git push origin main
   ```

5. **确认上线** — 告知用户推送成功，提醒等待约 1–2 分钟后访问 GitHub Pages 链接确认看板已更新，数据截止日期显示正确。

如遇错误，参考 `skills/token-holder-dashboard/SKILL.md` 中的故障排查章节。
