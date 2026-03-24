#!/usr/bin/env python3
"""
update_dashboard.py — Read latest holder CSVs and update dashboard.html
=======================================================================
Usage:
  python3 update_dashboard.py

Reads:  output/{Chain}_holders_{DATE}.csv  (produced by fetch_holders.py)
        output/USDDOLD_summary_{DATE}.csv
Writes: dashboard.html (DATA + SUMMARY sections updated in-place)
"""

import os, re, glob, json
import pandas as pd
from datetime import datetime
from pathlib import Path

# ── Paths ───────────────────────────────────────────────────────────────
SCRIPT_DIR   = Path(__file__).parent
OUTPUT_DIR   = SCRIPT_DIR / 'output'
INPUT_DIR    = SCRIPT_DIR / 'input'
DASHBOARD    = SCRIPT_DIR / 'dashboard.html'
TODAY_LABEL  = datetime.now().strftime('%Y-%m-%d')

# ── Display rules ────────────────────────────────────────────────────────
MIN_PROTOCOL_AMOUNT = 200   # show contracts individually if >= this
MIN_EOA_SHOW        = 10    # always show at least this many EOA
EOA_THRESHOLD       = 5000  # show EOA individually if balance >= this

# ── Bridge pre-mint addresses (excluded from effective TotalSupply) ───────
BRIDGE_PREMINT = {
    'Ethereum': '0x9277a463A508F45115FdEaf22FfeDA1B16352433',
    'BSC':      '0xca266910d92a313e5f9eb1affc462bcbb7d9c4a9',
}

# ── H (boss) addresses ────────────────────────────────────────────────────
H_ADDRESSES = {
    'Tron':     {'TT2T17KZhoDu47i2E4FWxfG79zdkEWkU9N', 'TPyjyZfsYaXStgz2NmAraF1uZcMtkgNan5'},
    'Arbitrum': {'0x3DdfA8eC3052539b6C9549F12cEA2C295cfF5296'},
}

# ── Fixed H.E values for SUMMARY (do not recompute) ──────────────────────
HE_FIXED = {
    'Tron':     {'prot': 0,            'eoa': 1501108.34},
    'Ethereum': {'prot': 255917.7554,  'eoa': 0},
    'BSC':      {'prot': 201522.0552,  'eoa': 0},
    'Polygon':  {'prot': 7447.025,     'eoa': 0},
    'Arbitrum': {'prot': 109463.04,    'eoa': 58568.37},
}

# ── Custom address labels (overrides auto-detected names) ─────────────────
LABEL_OVERRIDES = {
    # Tron
    'TU1CmpmWbCrFXqLLqMaKL2Q1d34bJNYLJe': 'BTTC: Cross-Chain Contract',
    'THxNCPGp8N8SJBScRU8rKPf7PvuwkGihmW': 'JustLend DAO: Lend Safe Vault',
    'TX7kybeP6UwTBRHLNPYmswFESHfyjm9bAS': 'jUSDD0LD Token',
    'TNTfaTpkdd4AQDeqr8SGG7tgdkajdhbP5c': 'SUN: USDDOLD2Pool',
    'TNLcz8A9hGKbTNJ6b6C1GTyigwxURbWzkM': 'SUN-USDDOLD-USDT Token',
    'TSJWbBJAS8HgQCMJfY5drVwYDa7JBAm6Es': 'SUN-USDDOLD-TRX Token',
    'TMxxHG5PRVakKwNCvTWDb73gPwXvkZAhpm': 'SUN: USDDOLD/USDT Pool Token',
    'TBSRZYLZ2pguF3EqLz86Kt9hZ4eqKEQMSY': 'SUN: 2USD LP Pool',
    'TCkNadwxyik1D66qCGmavuneowDRXPgdkL': 'SUN: USDD-USDT LP V2 Pool',
    'TEjGcD7Fb7KfEsJ2ouGCFUqqQqGjtvbmbu': 'SUN: USDD-USDT V2 Pool',
    'TCpXumigVHd2iuSkotNgkSduKqksUfpcvc': 'SUN: USDD-TRX LP Pool',
    'TAUGwRhmCP518Bm4VBqv7hDun9fg8kYjC4': 'SUN: StableSwap 2Pool (Old)',
    'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t': 'USDT Token',
    'TKVsYedAY23WFchBniU7kcx1ybJnmRSbGt': 'SUN: StableSwap 3Pool',
    # Ethereum
    '0x9277a463a508f45115fdeaf22ffeda1b16352433': 'BTTC: Cross-Chain Contract',
    '0xa3a7b6f88361f48403514059f1f16c8e78d60eec': 'Arbitrum One: L1 ERC20 Gateway',
    '0x692953e758c3669290cb1677180c64183cee374e': 'Stargate Finance: S*USDD Token',
    '0x2bc477c7c00511ec8a2ea667dd8210af9ff15e1d': 'Uniswap V3: USDD-USDT',
    '0x378ba9b73309be80bf4c2c027aad799766a7ed5a': 'Votium: Multi Merkle Stash',
    '0x40ec5b33f54e0e8a33a975908c5ba1c14e5bbbdf': 'Polygon (Matic): ERC20 Bridge',
    '0xe6b5cc1b4b47305c58392ce3d359b10282fc36ea': 'Curve: USDD3CRV3CRV-f Pool',
    '0xee5b5b923ffce93a870b3104b7ca09c3db80047a': 'Bybit: Hot Wallet 4',
    # BSC
    '0xca266910d92a313e5f9eb1affc462bcbb7d9c4a9': 'Bridge Contract (Lock)',
    '0x54c182a3c14590b3b8211e4fb831c0f0b572c825': 'PancakeSwap V2: GYRO-USDD',
    '0x4e145a589e4c03cbe3d28520e4bf3089834289df': 'Stargate Finance: S*USDD Token',
    '0xf1da185cce5bed1bebbb3007ef738ea4224025f7': 'Venus: vUSDD_Tron Token',
    '0x9f2fd23bd0a5e08c5f2b9dd6cf9c96bfb5fa515c': 'Venus: vUSDD_GameFi Token',
    '0xc3a45ad8812189cab659ad99e64b1376f6acd035': 'Venus: vUSDD_Stablecoins Token',
    '0xa615467cae6b9e0bb98bc04b4411d9296fd1dfa0': 'Venus: vUSDD_DeFi Token',
    '0x2762409baa1804d94d8c0bcff8400b78bf915d5b': 'LayerZero: Aptos Token Bridge',
    '0xd17479997f34dd9156deef8f95a52d81d265be9c': 'Decentralized USD: Old USDD Token',
    '0xf322942f644a996a617bd29c16bd7d231d9f35e9': 'Venus: Treasury',
    '0xcf799767d366d789e8b446981c2d578e241fa25c': 'Multichain: anyUSDD Token',
    '0xdf31a28d68a2ab381d42b380649ead7ae2a76e42': 'Venus: Risk Fund',
    '0x0051ef9259c7ec0644a80e866ab748a2f30841b3': 'Bybit 14',
    # Arbitrum
    '0x5151c83ad4e1c8c4ea0d1eaf91c246a8c6dab2a4': 'Arbitrum Bridge (Lock)',
    # Polygon
    '0x7ee7d075d2a74a2a05e8837a6a4727fab5d23c5b': 'Uniswap V2',
}

# ── Chain display config ──────────────────────────────────────────────────
CHAIN_CC = {
    'Tron': '#ef4444', 'Ethereum': '#6366f1', 'BSC': '#f59e0b',
    'Polygon': '#a855f7', 'Arbitrum': '#22d3ee',
}
CHAIN_ORDER = ['Tron', 'Ethereum', 'BSC', 'Polygon', 'Arbitrum']


# ════════════════════════════════════════════════════════════════════════════
def find_latest(pattern):
    files = sorted(glob.glob(str(OUTPUT_DIR / pattern)))
    return Path(files[-1]) if files else None


def load_chain_holders(chain):
    """Load latest holders CSV for a chain."""
    p = find_latest(f'{chain}_holders_*.csv')
    if not p:
        p = find_latest(f'{chain}_top50_*.csv')
    if not p:
        p = find_latest(f'{chain}_rpc_holders_*.csv')
    if not p:
        return None
    df = pd.read_csv(p)
    df.columns = [c.strip() for c in df.columns]
    print(f"  {chain}: loaded {len(df)} rows from {p.name}")
    return df


def load_bsc_from_input():
    """Load BSC holders from the BSCScan CSV export in input/ directory."""
    files = sorted(glob.glob(str(INPUT_DIR / 'export-tokenholders-for-contract-*.csv')))
    if not files:
        return None
    path = Path(files[-1])
    print(f"  BSC: loading from input/{path.name}")
    df_raw = pd.read_csv(path)
    df_raw.columns = [c.strip().strip('"') for c in df_raw.columns]

    rows = []
    for i, row in df_raw.iterrows():
        addr    = str(row.get('HolderAddress', '')).strip().strip('"')
        bal_str = str(row.get('Balance', '0')).strip().strip('"').replace(',', '')
        amt     = float(bal_str) if bal_str else 0.0
        label   = get_label(addr)
        if is_h_address('BSC', addr):
            cat = 'Boss'
        elif label:
            cat = 'Protocol'
        else:
            cat = 'EOA_Top10'
        rows.append({'Address': addr, 'USDD_Amount': amt,
                     'Category': cat, 'Name/Label': label, 'Rank': i + 1})

    df = pd.DataFrame(rows)
    print(f"  BSC: {len(df)} holders classified (input CSV)")
    return df


def load_summary():
    """Load latest summary CSV for supply + holders counts."""
    p = find_latest('USDDOLD_summary_*.csv')
    if not p:
        return {}
    df = pd.read_csv(p)
    result = {}
    for _, row in df.iterrows():
        chain = str(row.get('Chain', '')).strip()
        if '>>>' in chain:
            continue
        result[chain] = {
            'supply': float(row.get('TotalSupply_Onchain', 0) or 0),
            'holders': int(row.get('Total_Holders', 0) or 0),
        }
    return result


def get_label(addr):
    return LABEL_OVERRIDES.get(addr.lower(), LABEL_OVERRIDES.get(addr, ''))


def is_h_address(chain, addr):
    h_set = H_ADDRESSES.get(chain, set())
    return addr in h_set or addr.lower() in {a.lower() for a in h_set}


def js_val(v):
    """Format a value for JS literal."""
    if isinstance(v, str):
        escaped = v.replace("'", "\\'")
        return f"'{escaped}'"
    if isinstance(v, float):
        return f"{v:.4f}"
    if v is None:
        return 'null'
    return str(v)


def build_chain_js(chain, df, supply, holders_count):
    """Generate JS rows array for one chain."""
    if df is None or df.empty:
        return None

    amt_col = next((c for c in df.columns if 'USDD_Amount' in c or 'Balance' in c), None)
    if amt_col is None:
        return None

    df = df.copy()
    df['_amt'] = pd.to_numeric(df[amt_col].astype(str).str.replace(',', ''), errors='coerce').fillna(0)
    df['_addr'] = df.get('Address', df.get('HolderAddress', '')).astype(str).str.strip()
    df['_cat'] = df.get('Category', '').astype(str)
    df['_rank'] = pd.to_numeric(df.get('Rank', df.get('Overall_Rank', '')), errors='coerce')
    df = df.sort_values('_amt', ascending=False).reset_index(drop=True)
    df['_rank'] = df.index + 1

    supply_val = supply or df['_amt'].sum()
    pct_base   = supply_val if supply_val else 1

    lines = []
    lines.append(f"      // ── Protocol ──")

    # Classify rows
    protocols, h_rows, eoa_rows = [], [], []
    for _, row in df.iterrows():
        addr = row['_addr']
        amt  = row['_amt']
        rank = int(row['_rank'])
        cat  = row['_cat']
        label = get_label(addr) or str(row.get('Name/Label', '') or '').strip()

        if is_h_address(chain, addr):
            h_rows.append((rank, addr, label, amt))
        elif cat in ('Protocol', 'H', 'Boss'):
            protocols.append((rank, addr, label, amt))
        elif cat in ('EOA_Top10', 'EOA'):
            # 'EOA' comes from save_holders CSV; 'EOA_Top10' from BSC input CSV
            eoa_rows.append((rank, addr, label, amt))
        # EOA_Others / Others: skip (computed dynamically in JS as 其他)

    # Protocol rows: show individually if amt >= MIN_PROTOCOL_AMOUNT
    for rank, addr, label, amt in sorted(protocols, key=lambda x: -x[3]):
        if amt < MIN_PROTOCOL_AMOUNT:
            continue
        pct = round(amt / pct_base * 100, 4)
        name = label  # empty → JS shows '—'
        lines.append(f"      {{cat:'Protocol', rank:{rank:2d}, addr:{js_val(addr)}, name:{js_val(name)}, amt:{amt:.4f}, pct:{pct:.4f}}},")

    # H rows
    if h_rows:
        lines.append(f"      // ── H ──")
        for rank, addr, label, amt in sorted(h_rows, key=lambda x: -x[3]):
            pct = round(amt / pct_base * 100, 4)
            lines.append(f"      {{cat:'Boss', rank:{rank:2d}, addr:{js_val(addr)}, amt:{amt:.4f}, pct:{pct:.4f}}},")

    # EOA rows:
    #   Tron  → all EOA with amt > 5000 (no fixed top-N)
    #   Others → top 10 EOA (regardless of amount)
    if eoa_rows:
        lines.append(f"      // ── EOA ──")
        eoa_sorted = sorted(eoa_rows, key=lambda x: -x[3])
        if chain == 'Tron':
            show_eoa = [r for r in eoa_sorted if r[3] > EOA_THRESHOLD]
        else:
            show_eoa = eoa_sorted[:10]
        for rank, addr, label, amt in show_eoa:
            pct  = round(amt / pct_base * 100, 4)
            name = label or ''
            lines.append(f"      {{cat:'EOA_Top10', rank:{rank:2d}, addr:{js_val(addr)}{', name:'+js_val(name) if name else ''}, amt:{amt:.4f}, pct:{pct:.4f}}},")

    rows_str = "\n".join(lines)
    block = (
        f"    totalSupply: {supply_val:.4f}, holders: {holders_count or 0},\n"
        f"    rows: [\n"
        f"{rows_str}\n"
        f"    ]"
    )
    return block


def compute_summary_data(chain_data):
    """Compute SUMMARY array data using latest chain data + fixed H.E values."""
    result = []
    for chain in CHAIN_ORDER:
        df, supply, holders_count = chain_data.get(chain, (None, 0, 0))
        if df is None:
            continue

        he = HE_FIXED.get(chain, {'prot': 0, 'eoa': 0})
        cc = CHAIN_CC.get(chain, '#888')

        # Fallback supply from df sum if not in summary CSV
        addr_col = next((c for c in df.columns if 'Address' in c or 'Holder' in c), None) if df is not None else None
        amt_col  = next((c for c in df.columns if 'USDD_Amount' in c or 'Balance' in c), None) if df is not None else None
        if not supply and df is not None and amt_col:
            supply = df[amt_col].apply(lambda x: float(str(x).replace(',', '') or 0)).sum()
        # Fallback holders from df row count if not in summary CSV
        if not holders_count and df is not None:
            holders_count = len(df)

        # Effective supply (subtract bridge pre-mint for ETH/BSC)
        bridge_addr = BRIDGE_PREMINT.get(chain)
        bridge_amt = 0.0
        if bridge_addr and df is not None and addr_col and amt_col:
            match = df[df[addr_col].astype(str).str.lower() == bridge_addr.lower()]
            if not match.empty:
                bridge_amt = float(str(match.iloc[0][amt_col]).replace(',', ''))

        eff_supply = (supply - bridge_amt) if bridge_amt > 0 else supply

        # Protocol total (excl bridge pre-mint)
        cat_col  = 'Category'
        amt_col  = amt_col  or 'USDD_Amount'
        addr_col = addr_col or 'Address'

        prot_total = 0.0
        if df is not None and amt_col in df.columns and cat_col in df.columns:
            for _, row in df.iterrows():
                cat  = str(row.get(cat_col, '')).strip()
                addr = str(row.get(addr_col, '')).strip().lower()
                amt  = float(str(row.get(amt_col, 0)).replace(',', '') or 0)
                if bridge_addr and addr == bridge_addr.lower():
                    continue
                if cat == 'Protocol' or is_h_address(chain, addr):
                    prot_total += amt

        eoa_total = eff_supply - prot_total
        prot_comm = prot_total - he['prot']
        eoa_comm  = eoa_total - he['eoa']

        result.append({
            'chain': chain, 'cc': cc, 'supply': round(eff_supply, 2),
            'holders': holders_count or 0,
            'prot': {'total': round(prot_total, 2), 'he': he['prot'], 'comm': round(prot_comm, 2)},
            'eoa':  {'total': round(eoa_total, 2),  'he': he['eoa'],  'comm': round(eoa_comm, 2)},
        })
    return result


def summary_to_js(summary_data):
    """Convert summary data list to JS const SUMMARY = [...] string."""
    lines = []
    lines.append("// H 数值固定不变，总量与社区按最新数据计算")
    lines.append("// ETH/BSC TotalSupply 已扣除预铸桥接储备")
    lines.append("const SUMMARY = [")
    for s in summary_data:
        p, e = s['prot'], s['eoa']
        lines.append(
            f"  {{ chain:{js_val(s['chain'])}, cc:{js_val(s['cc'])}, "
            f"supply:{s['supply']}, holders:{s['holders']},\n"
            f"    prot:{{ total:{p['total']}, he:{p['he']}, comm:{p['comm']} }},\n"
            f"    eoa: {{ total:{e['total']}, he:{e['he']},  comm:{e['comm']} }} }},"
        )
    lines.append("];")
    return "\n".join(lines)


def update_dashboard(chain_data, summary_data):
    """Read dashboard.html, replace DATA and SUMMARY sections, write back."""
    html = DASHBOARD.read_text(encoding='utf-8')

    # ── Replace each chain block in DATA ──────────────────────────────────
    for chain in CHAIN_ORDER:
        df, supply, holders_count = chain_data.get(chain, (None, 0, 0))
        block = build_chain_js(chain, df, supply, holders_count)
        if block is None:
            print(f"  ⚠️  Skipping {chain} (no data)")
            continue

        # Match:  // ─── CHAINNAME ──...  ChainName: { ... },
        # Use a pattern that captures from chain comment to closing },
        pattern = (
            r'(// ─+\s*' + re.escape(chain.upper()) + r'\s*─+[^\n]*\n'
            r'\s*' + re.escape(chain) + r'\s*:\s*\{)'
            r'.*?'
            r'(^\s*\},)'
        )
        replacement_inner = f"\\1\n{block}\n\\2"
        new_html, n = re.subn(pattern, replacement_inner, html, count=1, flags=re.DOTALL | re.MULTILINE)
        if n:
            html = new_html
            print(f"  ✓ Updated {chain} data block")
        else:
            print(f"  ⚠️  Could not find {chain} block in dashboard.html (pattern not matched)")

    # ── Replace SUMMARY block ─────────────────────────────────────────────
    summary_js = summary_to_js(summary_data)
    pattern_sum = r'(// 逻辑说明[^\n]*\n(?:// [^\n]*\n)*)const SUMMARY\s*=\s*\[.*?\];'
    new_html, n = re.subn(pattern_sum, summary_js, html, count=1, flags=re.DOTALL)
    if n:
        html = new_html
        print(f"  ✓ Updated SUMMARY block")
    else:
        # Try simpler pattern
        pattern_sum2 = r'const SUMMARY\s*=\s*\[.*?\];'
        new_html, n = re.subn(pattern_sum2, summary_js, html, count=1, flags=re.DOTALL)
        if n:
            html = new_html
            print(f"  ✓ Updated SUMMARY block (simple match)")
        else:
            print(f"  ⚠️  Could not replace SUMMARY block")

    # ── Update data-date ──────────────────────────────────────────────────
    html = re.sub(
        r'(id=["\']data-date["\'][^>]*>)[^<]*(</)',
        f'\\g<1>{TODAY_LABEL}\\2',
        html
    )

    DASHBOARD.write_text(html, encoding='utf-8')
    print(f"\n  ✓ dashboard.html updated (data date: {TODAY_LABEL})")


# ════════════════════════════════════════════════════════════════════════════
def main():
    print(f"\n{'='*60}")
    print(f"  USDDOLD Dashboard Updater — {TODAY_LABEL}")
    print(f"{'='*60}\n")

    summary_meta = load_summary()

    chain_data = {}
    for chain in CHAIN_ORDER:
        if chain == 'BSC':
            df = load_bsc_from_input()
            if df is None:
                df = load_chain_holders(chain)
        else:
            df = load_chain_holders(chain)
        meta = summary_meta.get(chain, {})
        supply  = meta.get('supply', 0)
        holders = meta.get('holders', 0)
        chain_data[chain] = (df, supply, holders)

    summary_data = compute_summary_data(chain_data)

    print(f"\n{'─'*50}")
    print(f"  Updating dashboard.html...")
    print(f"{'─'*50}")
    update_dashboard(chain_data, summary_data)

    print(f"\n{'='*60}")
    print(f"  Done! Open dashboard.html to verify.")
    print(f"{'='*60}\n")


if __name__ == '__main__':
    main()
