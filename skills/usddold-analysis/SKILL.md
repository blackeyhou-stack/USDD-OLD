---
name: token-holder-dashboard
description: >
  多链 Token 持币分析看板的维护助手。适用于追踪 ERC20/TRC20 代币在多条链（Tron、
  Ethereum、BSC、Arbitrum、Polygon 等）持币分布的项目。当用户提到：更新持币数据、
  刷新看板、修改地址标签、处理桥接扣减逻辑、推送 GitHub Pages、新增链支持，
  或操作 dashboard.html / fetch_holders.py / update_dashboard.py 时，优先使用此 skill。
---

# 多链 Token 持币分析看板 — 操作手册

## 项目概览

本项目追踪指定 Token 在多条链的持币分布，生成单文件 HTML 看板，通过 GitHub Pages 对外共享。

**首次使用前，请先完成「初始配置」章节。**

---

## 初始配置（首次使用必读）

### 1. Token 合约地址（fetch_holders.py 第 37–73 行）

打开 `fetch_holders.py`，找到 `CHAINS = {` 这个字典，将每条链的 `contract` 字段替换为你的 Token 合约地址：

```python
CHAINS = {
    'Tron': {
        'contract': 'T...你的Tron合约地址',   # ← 改这里
        'type': 'tron',
        'decimals': 18,
    },
    'Ethereum': {
        'contract': '0x...你的ETH合约地址',   # ← 改这里
        'type': 'blockscout',
        'decimals': 18,
        'base_url': 'https://eth.blockscout.com',
        'verify_balances': True,
        'chainid': 1,
    },
    'Arbitrum': {
        'contract': '0x...你的ARB合约地址',   # ← 改这里
        'type': 'blockscout',
        'decimals': 18,
        'base_url': 'https://arbitrum.blockscout.com',
        'verify_balances': True,
        'chainid': 42161,
    },
    'Polygon': {
        'contract': '0x...你的Polygon合约地址',  # ← 改这里
        'type': 'blockscout',
        'decimals': 18,
        'base_url': 'https://polygon.blockscout.com',
        'verify_balances': True,
        'chainid': 137,
    },
    'BSC': {
        'contract': '0x...你的BSC合约地址',   # ← 改这里
        'type': 'bsc_csv',
        'decimals': 18,
        'csv_input_dir': './input',
    },
}
```

> Token 的 `decimals` 通常是 18，若不同请一并修改。

### 2. 桥接预铸地址（若有，update_dashboard.py 顶部）

部分链存在提前铸造的桥接储备地址，其余额需从有效流通量中扣除。若你的 Token 没有此类地址，将 `BRIDGE_PREMINT` 设为空字典：

```python
BRIDGE_PREMINT = {
    'Ethereum': '0x...预铸地址',   # 若无则删除该行
    'BSC':      '0x...预铸地址',   # 若无则删除该行
}
```

### 3. 地址显示名称（update_dashboard.py 顶部）

将已知协议合约地址映射到可读名称，跨次更新不会丢失：

```python
LABEL_OVERRIDES = {
    '0x...合约地址': '协议名称: 合约描述',
    'T...Tron地址':  'Protocol: Pool Name',
}
```

### 4. GitHub 配置

```bash
# 添加 GitHub 远端（首次）
git remote add origin https://github.com/<用户名>/<仓库名>.git

# 开启 GitHub Pages：仓库 Settings → Pages → Source 选择 main 分支
```

---

## 日常更新流程

### 第一步：获取 BSC 数据（手动导出）
1. 打开 BSCScan 对应 Token 的 holders 页面
2. 点击右上角 **Download CSV**
3. 将文件放到项目 `input/` 目录（文件名含 `export-tokenholders-for-contract-`）

### 第二步：抓取其他链数据
```bash
python3 fetch_holders.py
```
输出到 `output/{Chain}_holders_{DATE}.csv`。

### 第三步：更新看板
```bash
python3 update_dashboard.py
```
确认每条链和 SUMMARY 均显示 `✓`。

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
- **社区持有** = 有效流通量 − 协议持有

---

## 常见维护操作

**新增地址标签**
在 `LABEL_OVERRIDES` 添加一行 → 重跑 `update_dashboard.py`

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
