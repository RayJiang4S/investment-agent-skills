"""
组合量化指标计算脚本
用法: python scripts/quant_calc.py <snapshot_json_path>
输出: HHI、N_eff、策略权重、情景压力测试、流动性覆盖月数

策略关键词映射规则与 quant-analysis.md 0.5.2 保持一致。
"""

import json
import sys

STRATEGY_MAP = {
    "纳斯达克100": ["纳斯达克", "NASDAQ", "纳指"],
    "标普500":    ["标普500", "S&P 500", "标普", "SPY", "标普5"],
    "全球/港股":  ["全球", "恒生", "HSI", "港股"],
    "日本":       ["日经", "日本", "Nikkei", "TOPIX"],
    "欧洲/德国":  ["欧洲", "德国", "DAX", "CAC"],
    "印度":       ["印度", "Nifty"],
    "A股指数":    ["创业板", "沪深300", "中证500", "上证50", "中证1000", "基建"],
    "债券":       ["债券", "纯债", "信用债", "国债"],
    "货币":       ["货币", "活期宝"],
}

MONTHLY_EXPENSE = 20000  # 月均家庭开支，与 investment-preferences.md 7.2「月均家庭开支参考值」保持一致
# ⚠️ 若 investment-preferences.md 7.2 中修改了月均开支，需同步更新此处


def classify(name: str) -> str:
    for strategy, keywords in STRATEGY_MAP.items():
        if any(kw in name for kw in keywords):
            return strategy
    return "其他主动"


def main(snapshot_path: str):
    with open(snapshot_path, encoding="utf-8") as f:
        data = json.load(f)

    strategies: dict[str, float] = {}
    total_fund = 0.0
    total_cash = 0.0

    for acc in data.get("accounts", []):
        total_cash += acc.get("overview", {}).get("cash_fund_balance", 0) or 0
        for h in acc.get("holdings", []):
            mv = h.get("market_value", 0) or 0
            total_fund += mv
            s = classify(h["name"])
            strategies[s] = strategies.get(s, 0) + mv

    total_portfolio = total_fund + total_cash

    # HHI & N_eff（基于基金资产权重）
    hhi = sum((v / total_fund) ** 2 for v in strategies.values()) if total_fund else 0
    n_eff = (1 / hhi) if hhi else 0

    # 信号判断
    if n_eff < 3:
        neff_signal = "🔴 高度集中"
    elif n_eff < 5:
        neff_signal = "🟡 中度集中"
    else:
        neff_signal = "🟢 分散合理"

    # 情景压力测试
    nasdaq_mv = strategies.get("纳斯达克100", 0)
    qdii_mv = sum(v for k, v in strategies.items()
                  if k not in ["A股指数", "债券", "货币", "其他主动"])
    s1 = nasdaq_mv * -0.20
    s2 = qdii_mv * -0.05
    s3 = s1 + s2

    # 流动性
    liquidity_months = total_cash / MONTHLY_EXPENSE if MONTHLY_EXPENSE else 0
    liquidity_signal = "⚠️ 不足3个月" if liquidity_months < 3 else "✅ 充足"

    # 输出
    print("=" * 60)
    print(f"  家庭总基金资产：{total_fund:>12,.0f} 元")
    print(f"  活期宝（含货币）：{total_cash:>11,.0f} 元")
    print(f"  家庭总资产：{total_portfolio:>15,.0f} 元")
    print("=" * 60)

    print(f"\n【集中度】HHI={hhi:.4f}  N_eff={n_eff:.2f}  {neff_signal}")

    print("\n【策略权重（vs 总基金资产）】")
    for k, v in sorted(strategies.items(), key=lambda x: -x[1]):
        pct = v / total_fund * 100 if total_fund else 0
        print(f"  {k:<12} {v:>10,.0f} 元  {pct:>5.1f}%")

    print("\n【情景压力测试】")
    print(f"  S1 纳斯达克-20%：  {s1:>10,.0f} 元  ({s1/total_portfolio*100:.1f}% 总资产)")
    print(f"  S2 汇率贬值-5%：   {s2:>10,.0f} 元  ({s2/total_portfolio*100:.1f}% 总资产)")
    print(f"  S3 S1+S2 叠加：    {s3:>10,.0f} 元  ({s3/total_portfolio*100:.1f}% 总资产)")

    print(f"\n【流动性】活期宝 {liquidity_months:.1f} 个月开支  {liquidity_signal}")
    print("=" * 60)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"用法: python {sys.argv[0]} <snapshot_json_path>")
        sys.exit(1)
    main(sys.argv[1])
