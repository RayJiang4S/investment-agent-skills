# 组合量化分析参考

> Step 0.5 的详细计算逻辑。所有计算均为离线推算，无需联网，数据来自快照 JSON。

---

## 0.5.1 汇总持仓数据

从所有账户的 `holdings` 中提取：
- 每只基金的 `market_value`（市值）
- 基金名称和类型（用于判断跟踪指数）

计算：
- `total_fund_assets`：所有账户基金资产之和（不含活期宝）
- `total_portfolio_assets`：基金资产 + 所有账户活期宝

---

## 0.5.2 合并同指数策略

将跟踪同一指数的基金合并为一个"策略"，合并规则：

| 策略名 | 判断关键词（基金名称含以下任意一个） |
|--------|--------------------------------|
| 纳斯达克100 | 纳斯达克、NASDAQ、纳指100、纳指ETF |
| 标普500 | 标普500、S&P 500、标普、SPY |
| 全球/MSCI | 全球、MSCI世界、ACWI |
| A股沪深300 | 沪深300、CSI 300、沪深 |
| A股上证 | 上证、上证50、SSE |
| A股中证500 | 中证500、中证1000 |
| 港股/恒生 | 恒生、HSI、港股通、H股 |
| 日本 | 日经、日本、Nikkei、TOPIX |
| 欧洲/德国 | 欧洲、德国、DAX、CAC |
| 印度 | 印度、Nifty、孟买 |
| 债券/固收 | 债券、信用债、利率债、国债 |
| 货币/活期宝 | 活期宝、货币基金、现金 |

```
strategy_weight_i = strategy_market_value_i / total_fund_assets
```

---

## 0.5.3 计算 HHI 与 Effective N

```
HHI = Σ(strategy_weight_i²)
N_eff = 1 / HHI
```

- N_eff < 3 → 🔴 高度集中，在报告头部显著标注
- N_eff 3到5 → 🟡 中度集中
- N_eff > 5 → 🟢 合理分散

---

## 0.5.4 情景压力测试估算

```
nasdaq_total = 纳斯达克100策略合并市值
qdii_total   = 所有QDII类基金合并市值（含纳斯达克、标普、日本、欧洲、印度等一切境外基金）

S1_impact = nasdaq_total × (-20%)    // 美股科技回调20%
S2_impact = qdii_total × (-5%)       // 汇率贬值5%（人民币升值，QDII净值缩水）
S3_impact = S1_impact + S2_impact    // 综合压力叠加（简化计算）

S1_pct = S1_impact / total_portfolio_assets × 100
S2_pct = S2_impact / total_portfolio_assets × 100
S3_pct = S3_impact / total_portfolio_assets × 100
```

> 一阶近似，偏保守（忽略持仓间相关性）。目的是让风险可感知，非精确预测。

---

## 0.5.5 流动性检查

```
cash_total = 所有账户活期宝余额之和
monthly_expenses = 2万元（来自 investment-preferences.md 第七节 7.2 家庭流动性底线）
liquidity_months = cash_total / monthly_expenses
```

若 `liquidity_months < 3` → 在行动指令顶部标注 ⚠️ 流动性警告，建议暂停权益加仓。

---

## 0.5.6 仓位缺口计算（新资金分配依据）

对照 `investment-preferences.md` 第五节目标配置：

```
对每个策略 i：
  target_weight_i   = 目标占比中间值（如5到10%取7.5%）
  current_weight_i  = strategy_weight_i
  gap_i = target_weight_i - current_weight_i

  若 gap_i > 2%：低配，列入"建议买入"候选
  若 gap_i < -10%：超配，停止新增
```

---

## 0.5.7 量化摘要输出格式（供后续步骤使用）

```
家庭总基金资产：X万元
家庭总资产（含活期宝）：X万元
N_eff：X.X（🔴/🟡/🟢）
HHI：X.XX

主要策略权重：
  纳斯达克100：X%（目标≤40%，缺口X%）
  标普500：X%
  日本QDII：X%（目标5到10%，缺口X%）
  ...

压力测试：
  S1（美股-20%）：-X万元（-X%）
  S2（汇率-5%）：-X万元（-X%）
  S3（综合）：-X万元（-X%）

流动性：活期宝X万元，覆盖约X个月家庭开支
```
