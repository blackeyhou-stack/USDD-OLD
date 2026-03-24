# USDDOLD 持币分析看板

多链 USDDOLD Token 持币分布分析，覆盖 Tron / Ethereum / BSC / Polygon / Arbitrum 五条链。

🔗 **在线看板**：https://blackeyhou-stack.github.io/USDDOLD/dashboard.html

---

## 数据更新流程（每两周一次）

### 第一步：导出 BSC 持币数据

1. 打开 BSCScan：https://bscscan.com/token/0xd17479997F34dd9156Deef8F95A52D81D265be9c#balances
2. 点击页面右上角 **Download** 导出 CSV
3. 将文件放入 `input/` 目录（文件名保持 BSCScan 原始命名即可）

```
input/
└── export-tokenholders-for-contract-0xd17479997F34dd9156Deef8F95A52D81D265be9c.csv
```

### 第二步：抓取其余四条链数据

```bash
python3 fetch_holders.py
```

自动抓取 Tron、Ethereum、Arbitrum、Polygon 的持币数据，保存到 `output/` 目录。

### 第三步：更新看板

```bash
python3 update_dashboard.py
```

读取所有最新 CSV，重新生成 `dashboard.html` 内的数据块，并更新页面底部的数据日期。

### 第四步：推送到 GitHub

```bash
git add dashboard.html
git commit -m "数据更新 $(date +%Y-%m-%d)"
git push
```

推送后约 1 分钟，运营可通过以下链接访问最新看板：

> https://blackeyhou-stack.github.io/USDDOLD/dashboard.html

---

## 文件说明

| 文件 | 说明 |
|------|------|
| `dashboard.html` | 主看板（单文件，数据内嵌其中） |
| `fetch_holders.py` | 链上数据抓取脚本（Tron / ETH / ARB / Polygon） |
| `update_dashboard.py` | 看板数据更新脚本（读取 CSV → 写入 dashboard.html） |
| `input/` | 放置 BSC 手动导出 CSV 的目录 |
| `output/` | 抓取结果 CSV / Excel（本地保留，不上传 GitHub） |

---

## 看板功能

- **链明细数据**：各链持币地址明细，含协议地址、H 地址、Top EOA
- **汇总分析**：五链汇总对比，区分协议持仓 vs EOA 持仓、H 地址 vs 社区

---

## 环境依赖

```bash
python3 -m venv venv
source venv/bin/activate
pip install requests pandas openpyxl beautifulsoup4
```
