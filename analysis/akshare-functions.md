# akshare MCP 常用函数索引

MCP 服务: `project-0-天天基金-akshare`
工具: `search_functions` + `execute_function`

**使用原则**: 如果不确定函数名，先用 `search_functions` 搜索，再 `execute_function` 执行。函数名和参数必须精确匹配。

> ⚠️ **实际调用格式**：参数必须用 `request` 对象包裹：
> ```json
> { "request": { "function_name": "stock_zh_index_spot_sina", "params": {} } }
> ```
> 本文件中的函数调用为简写文档形式，实际 `CallMcpTool` 时需套上 `request` 层。

---

## 基金数据

### 基金净值/历史
```
search_functions(keyword="fund open fund info em", include_detail=True)
# 通常函数名: fund_open_fund_info_em
# 参数: fund="基金代码", indicator="单位净值走势" 或 "累计净值走势"

search_functions(keyword="fund em fund name")
# 获取基金列表/名称映射
```

### 基金业绩排行
```
search_functions(keyword="fund performance em")
# 参数: symbol="全部"/"股票型"/"混合型"等, period="近1月"/"近3月"/"近1年"等
```

### ETF 数据
```
search_functions(keyword="fund etf em")
```

---

## 股票市场指数

> ⚠️ 数据源选择原则：**优先使用 Sina（新浪）数据源**，东方财富(em)系列接口在部分网络环境下会被限流导致连接中断。

### A股实时指数
```
execute_function("stock_zh_index_spot_sina", {})
# 返回：上证指数(sh000001)、深证成指、沪深300、创业板、科创50 等 562 个指数实时行情
# 备用（需代理）: stock_zh_index_spot_em
```

### 美股指数（历史数据，含最新）
```
execute_function("index_us_stock_sina", {"symbol": ".DJI"})   # 道琼斯
execute_function("index_us_stock_sina", {"symbol": ".IXIC"})  # 纳斯达克
execute_function("index_us_stock_sina", {"symbol": ".INX"})   # 标普500
# 注意：symbol 格式为 .XXX 而非 ^XXX
```

### 港股指数
```
execute_function("stock_hk_index_spot_sina", {})
# 返回：恒生指数、国企指数、港股通等 38 个港股指数实时行情
```

---

## 宏观数据

### 美联储
```
search_functions(keyword="macro usa interest rate")
search_functions(keyword="macro usa fed")
# 美联储利率决定直接影响美股估值
```

### 美国经济数据
```
search_functions(keyword="macro usa cpi")       # 通胀
search_functions(keyword="macro usa pmi")       # 制造业/服务业PMI
search_functions(keyword="macro usa gdp")       # GDP
search_functions(keyword="macro usa non farm")  # 非农就业
```

### 中国宏观
```
execute_function("macro_china_gdp", {})
search_functions(keyword="macro china pmi")
search_functions(keyword="macro china cpi")
```

---

## 汇率

```
execute_function("currency_boc_sina", {})
# 中国银行汇率历史数据（约180条），数据截止于近年某时间点，非实时当日数据
# 如需最新汇率，改用 WebSearch：搜索「美元人民币汇率 今日 中行」
# QDII 基金受人民币汇率影响显著：人民币贬值 → QDII 净值相对升高

search_functions(keyword="currency rate", include_detail=True)
# 可搜索其他汇率相关函数，按需选用
```

---

## 分析场景对应函数选择

| 分析需求 | 推荐函数（优先 Sina 源） |
|---------|---------|
| A股整体行情 | `stock_zh_index_spot_sina` （稳定，1-2秒） |
| 港股行情 | `stock_hk_index_spot_sina` （稳定，0.1秒） |
| 美股指数走势 | `index_us_stock_sina` symbol=.DJI/.IXIC/.INX |
| 汇率对QDII的影响 | `currency_boc_sina` |
| CPI通胀数据 | `macro_china_cpi_monthly` |
| 中国经济基本面 | `macro_china_gdp` |
| 具体基金近期净值 | `fund_open_fund_info_em` |

**东方财富(em)系接口在部分网络下受限，如调用失败请改用 Sina 系替代接口。**
