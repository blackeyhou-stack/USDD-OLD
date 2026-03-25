---
name: usddold-analysis
description: >
  USDDOLD 持币看板项目的专属助手。每当用户提到更新 USDDOLD 数据、刷新看板、
  更新持币地址、推送到 GitHub Pages、修改地址标签、调整展示规则，或询问
  dashboard.html / fetch_holders.py / update_dashboard.py 相关操作时，
  优先使用此 skill。也适用于：调整 H 地址配置、修改桥接扣减逻辑、
  新增链的支持、以及一切与 USDDOLD 看板维护相关的任务。
---

# USDDOLD 持币分析看板 — 操作手册

## 项目概览

追踪 USDDOLD token 在 5 条链的持币分布，每两周更新一次，通过 GitHub Pages 向运营团队共享。

| 项目 | 详情 |
|------|------|
| 看板地址 | https://blackeyhou-stack.github.io/USDD-OLD/dashboard.html |
| GitHub 仓库 | https://github.com/blackeyhou-stack/USDD-OLD |
| 本地目录 | `/Users/blackey/USDDOLD/` |
| 更新周期 | 约每两周一次 |

---

## 完整更新流程

### 第一步：获取 BSC 数据（手动）

1. 打开 BSCScan：https://bscscan.com/token/0xd17479997F34dd9156Deef8F95A52D81D265be9c#balances
2. 点击右上角 **Download** 导出 CSV
3. 将文件放到 `/Users/blackey/USDDOLD/input/` 目录
   - 文件名格式：`export-tokenholders-for-contract-0xd17479...csv`

### 第二步：抓取链上数据

```bash
cd /Users/blackey/USDDOLD
python3 fetch_holders.py
```

抓取 Tron、Ethereum、Arbitrum、Polygon 四条链的持币数据，输出到 `output/{Chain}_holders_{DATE}.csv`。

### 第三步：更新看板

```bash
python3 update_dashboard.py
```

读取所有 CSV，重写 `dashboard.html` 中的 DATA 和 SUMMARY 块，更新日期显示。

### 第四步：提交并推送

```bash
cd /Users/blackey/USDDOLD
git add dashboard.html
git commit -m "data: update $(date +%Y-%m-%d)"
git push usddold clean-main:main
```

推送成功后，等 1–2 分钟，看板自动更新。

---

## 关键配置（update_dashboard.py）

### LABEL_OVERRIDES — 地址显示名称
手动维护的地址→名称映射，跨次更新不会被覆盖。新增方式：
```python
LABEL_OVERRIDES = {
    '0xABC...': '协议名称: 合约描述',
    # Tron 地址同理
}
```

### HE_FIXED — H 地址持有量（固定不变）
H 地址的金额在汇总分析中保持不变，不随数据更新而重算：
```python
HE_FIXED = {
    'Tron':     {'prot': 0,           'eoa': 1501108.34},
    'Ethereum': {'prot': 255917.7554, 'eoa': 0},
    'BSC':      {'prot': 201522.0552, 'eoa': 0},
    'Polygon':  {'prot': 7447.025,    'eoa': 0},
    'Arbitrum': {'prot': 109463.04,   'eoa': 58568.37},
}
```

### BRIDGE_PREMINT — 桥接预铸地址（从 TotalSupply 中扣除）
ETH 和 BSC 各有一个提前铸造的桥接储备地址，计算有效流通量时需扣除：
```python
BRIDGE_PREMINT = {
    'Ethereum': '0x9277a463A508F45115FdEaf22FfeDA1B16352433',
    'BSC':      '0xca266910d92a313e5f9eb1affc462bcbb7d9c4a9',
}
```

### H_ADDRESSES — H 内部地址集合
这些地址在看板中显示为 ⭐ H（不显示地址名称，保护身份）：
```python
H_ADDRESSES = {
    'Tron':     {'TT2T17KZhoDu47i2E4FWxfG79zdkEWkU9N', 'TPyjyZfsYaXStgz2NmAraF1uZcMtkgNan5'},
    'Arbitrum': {'0x3DdfA8eC3052539b6C9549F12cEA2C295cfF5296'},
}
```

---

## 展示规则

| 链 | Protocol 阈值 | EOA 展示规则 |
|----|--------------|-------------|
| 所有链 | 余额 ≥ 200 USDD 的合约单独展示 | — |
| Tron | — | 余额 > 5,000 的全部展示 |
| ETH / BSC / ARB / Polygon | — | 仅展示 TOP 10 |

**其他（合并）行** = TotalSupply − 所有已展示行之和，由 JS 动态计算，确保链总计 = TotalSupply。

---

## 汇总分析逻辑

- **ETH 有效流通量** = 链上 TotalSupply − 0x9277... 余额（桥接预铸）
- **BSC 有效流通量** = 链上 TotalSupply − 0xca266... 余额（桥接预铸）
- ARB 和 Polygon 的资产是从 ETH 链桥接过去的，因此 ETH 协议中的 H 持仓已包含这两条链的部分
- H 持有量固定（见 HE_FIXED），社区持有量 = 总量 − H 持有量

---

## 常见维护操作

### 新增地址标签
在 `update_dashboard.py` 的 `LABEL_OVERRIDES` 里添加一行，然后重跑 `update_dashboard.py`。

### 修改 H 地址金额
直接修改 `HE_FIXED` 对应的值，重跑 `update_dashboard.py`。

### 调整展示阈值
- 协议合约阈值：`MIN_PROTOCOL_AMOUNT = 200`（`update_dashboard.py` 顶部）
- EOA 阈值：`EOA_THRESHOLD = 5000`（`update_dashboard.py` 顶部）

### 仅更新看板样式（不更新数据）
直接编辑 `dashboard.html`，然后：
```bash
git add dashboard.html && git commit -m "style: ..." && git push usddold clean-main:main
```

---

## 文件结构

```
/Users/blackey/USDDOLD/
├── dashboard.html          # 看板主文件（单文件，包含所有数据）
├── fetch_holders.py        # 抓取链上数据
├── update_dashboard.py     # 更新看板数据块
├── input/                  # 放置 BSC CSV 导出文件
│   └── export-tokenholders-for-contract-*.csv
├── output/                 # 自动生成的 CSV（已 gitignore）
└── skills/usddold-analysis/SKILL.md  # 本文件
```

---

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| BSC 数据为空 / 跳过 | 确认 `input/` 目录下有 BSC CSV 文件 |
| 某链 block 未更新 | 检查 dashboard.html 中是否有 `// ─── CHAINNAME ───` 注释头 |
| SUMMARY 未更新 | 运行 `update_dashboard.py` 时查看输出，确认 "✓ Updated SUMMARY block" |
| GitHub Pages 未刷新 | 等 1–2 分钟；仓库 Actions 页查看 build 状态 |
| push 失败 | 确认 remote `usddold` 存在：`git remote -v` |
