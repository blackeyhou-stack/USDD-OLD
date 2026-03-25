---
name: token-holder-dashboard
description: >
  多链 Token 持币分析看板的维护助手。适用于追踪 ERC20/TRC20 代币在多条链（Tron、
  Ethereum、BSC、Arbitrum、Polygon 等）持币分布的项目。当用户提到：更新持币数据、
  刷新看板、修改地址标签、调整内部地址（H/Boss）配置、处理桥接扣减逻辑、
  推送 GitHub Pages、新增链支持，或操作 dashboard.html / fetch_holders.py /
  update_dashboard.py 时，优先使用此 skill。
---

# 多链 Token 持币分析看板 — 操作手册

## 项目概览

本项目追踪指定 Token 在多条链的持币分布，生成单文件 HTML 看板，通过 GitHub Pages 对外共享。

**首次使用前，请先完成「初始配置」章节。**

---

## 初始配置（首次使用必读）

克隆项目后，需在 `update_dashboard.py` 顶部填写以下配置：

### 1. 项目路径
脚本默认读取同目录下的 `output/` 和 `input/`，无需修改路径。确认目录结构：
```
<your-project>/
├── dashboard.html
├── fetch_holders.py
├── update_dashboard.py
├── input/        ← 放 BSC CSV 导出文件
└── output/       ← 自动生成，无需手动操作
```

### 2. 内部地址（H 地址）
将需要隐藏身份、打 ⭐H 标记的地址填入 `H_ADDRESSES`：
```python
H_ADDRESSES = {
    'Tron':     {'T...地址1', 'T...地址2'},
    'Ethereum': {'0x...地址'},
    'Arbitrum': {'0x...地址'},
    # 按实际情况填写，没有则留空 set()
}
```

### 3. 固定 H 持有量（汇总分析用）
H 地址的金额在汇总分析中保持固定，不随数据更新变化（防止泄露实时变动）：
```python
HE_FIXED = {
    'Tron':     {'prot': 0,      'eoa': 0},   # ← 填入实际金额
    'Ethereum': {'prot': 0,      'eoa': 0},
    'BSC':      {'prot': 0,      'eoa': 0},
    'Polygon':  {'prot': 0,      'eoa': 0},
    'Arbitrum': {'prot': 0,      'eoa': 0},
}
```

### 4. 桥接预铸地址（若有）
部分链存在提前铸造的桥接储备地址，其余额需从有效流通量中扣除：
```python
BRIDGE_PREMINT = {
    'Ethereum': '0x...预铸地址',   # 若无则删除该行
    'BSC':      '0x...预铸地址',
}
```

### 5. 地址显示名称
将已知协议合约地址映射到可读名称：
```python
LABEL_OVERRIDES = {
    '0x...合约地址': '协议名称: 合约描述',
    'T...Tron地址':  'SUN: USDD-USDT Pool',
    # 持续补充，跨次更新不会丢失
}
```

### 6. GitHub 配置
```bash
# 添加 GitHub 远端（首次）
git remote add origin https://github.com/<用户名>/<仓库名>.git

# 推送（后续更新）
git add dashboard.html
git commit -m "data: update YYYY-MM-DD"
git push origin main
```
推送后在仓库 Settings → Pages → Source 选择 `main` 分支开启 GitHub Pages。

---

## 日常更新流程（每次更新执行）

### 第一步：获取 BSC 数据（手动导出）
1. 打开 BSCScan 对应 Token 的 holders 页面
2. 点击右上角 **Download CSV**
3. 将文件放到项目 `input/` 目录
   - 文件名格式：`export-tokenholders-for-contract-0x...csv`

### 第二步：抓取其他链数据
```bash
python3 fetch_holders.py
```
抓取 Tron、Ethereum、Arbitrum、Polygon 数据，输出到 `output/{Chain}_holders_{DATE}.csv`。

### 第三步：更新看板
```bash
python3 update_dashboard.py
```
确认输出中每条链和 SUMMARY 均显示 `✓`。

### 第四步：提交推送
```bash
git add dashboard.html
git commit -m "data: update $(date +%Y-%m-%d)"
git push origin main
```
1–2 分钟后 GitHub Pages 自动更新。

---

## 展示规则说明

| 项目 | 规则 |
|------|------|
| 协议合约 | 余额 ≥ `MIN_PROTOCOL_AMOUNT`（默认 200）的合约单独展示 |
| Tron EOA | 余额 > `EOA_THRESHOLD`（默认 5,000）的地址全部展示 |
| 其他链 EOA | 仅展示 TOP 10 |
| 其他（合并）行 | = TotalSupply − 所有已展示行之和，JS 动态计算 |
| H 地址 | 显示为 ⭐ H，不显示地址或名称 |
| 未知地址 | 名称显示为 `—` |

调整阈值：修改 `update_dashboard.py` 顶部的常量：
```python
MIN_PROTOCOL_AMOUNT = 200   # 协议合约最低展示金额
EOA_THRESHOLD       = 5000  # Tron EOA 展示门槛
MIN_EOA_SHOW        = 10    # 其他链 EOA 展示数量
```

---

## 汇总分析逻辑

- **有效流通量** = 链上 TotalSupply − 桥接预铸地址余额（仅配置了 `BRIDGE_PREMINT` 的链）
- **协议持有** = 所有 Protocol 类地址之和（不含桥接预铸）
- **H 持有** = `HE_FIXED` 中的固定值（不随数据变化）
- **社区持有** = 总量 − H 持有
- 若某链资产是从另一链桥接而来，需在 `HE_FIXED` 中手动体现跨链 H 持仓

---

## 常见维护操作

**新增地址标签**
在 `LABEL_OVERRIDES` 添加一行 → 重跑 `update_dashboard.py`

**更新 H 持有金额**
修改 `HE_FIXED` 对应值 → 重跑 `update_dashboard.py`

**新增 H 地址**
在 `H_ADDRESSES` 对应链的 set 里添加地址 → 重跑 `update_dashboard.py`

**仅改样式不改数据**
直接编辑 `dashboard.html` → commit → push

---

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| BSC 数据跳过 | 确认 `input/` 目录下有 CSV 文件，文件名含 `export-tokenholders-for-contract-` |
| 某链 block 未更新 | 检查 `dashboard.html` 中是否有 `// ─── CHAINNAME ───` 注释头 |
| SUMMARY 未更新 | 查看脚本输出，确认 "✓ Updated SUMMARY block" |
| GitHub Pages 未刷新 | 等 1–2 分钟；在仓库 Actions 页查看 build 状态 |
| push 失败 | 运行 `git remote -v` 确认 remote 地址正确 |
| H 地址显示为普通地址 | 确认 `H_ADDRESSES` 中地址大小写与链上一致 |
