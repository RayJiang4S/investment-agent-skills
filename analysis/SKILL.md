---
name: portfolio-analysis
description: 综合所有投资平台的快照数据，结合 akshare MCP 市场数据，生成跨平台家庭投资组合分析报告。当用户提到查看基金持仓、资产分析、投资配置评估、收益情况、组合分析、帮我看看基金、出报告时使用。Use when user asks to check fund holdings, analyze portfolio allocation, review investment returns, or evaluate overall asset distribution across all platforms.
---

# 家庭投资组合分析 Skill

## 总体流程

```
[开始]
  ↓
Step 0: 读取个性化配置 + 最新快照，确认数据时效
  ↓
Step 0.5: 读取当前分析报告（作为迭代基础，了解已有策略和近期动作）
  ↓
Step 0.6: 组合量化指标计算（纯从快照数据推算，无需联网）
  ↓
Step 1: 获取市场数据（akshare MCP）
  ↓
Step 2: 全球市场数据查询（WebSearch）—— 含技术过滤确认
  ↓
Step 3: 备份当前报告 → 就地更新报告（迭代，不新建）
```

> **无需打开浏览器**。账户数据来自各平台本地快照文件。若某平台快照不存在，提示用户先运行对应平台的数据采集 skill（如「天天基金账户数据采集」）。

---

## Step 0: 读取配置与快照

### 0.1 读取个性化配置

用 Read 工具读取以下文件，作为整个分析过程的策略基础：

```
投资理财/config/investment-preferences.md
```

提取以下信息：
- **账户持有人配置**（姓名、关系、风险承受能力）
- **核心投资哲学**（各类资产的持仓策略）
- **关注的投资主题**（分析全球市场和自选时的关联度判断依据）
- **A股加仓前提条件**（报告第七章「A股风险评估」中需逐条对照实时状态）
- **目标资产配置**（报告 5.1 合并资产结构 + 6.2 仓位缺口表的参考基准）
- **量化约束条件**（Step 0.6 中的硬性上限检查依据，生成行动指令时遵守）
- **操作纪律**（第一章行动指令的操作纪律来源）

若文件不存在，提示用户创建，并继续分析（使用通用原则）。

### 0.2 发现并读取所有平台快照

用 Glob 列出 `投资理财/platforms/*/snapshot.json`，获取所有已有快照的平台列表。

对每个平台，用 Read 工具读取对应的 `snapshot.json`：

| 平台 | 快照路径 | 未找到时 |
|-----|---------|---------|
| 天天基金 | `投资理财/platforms/天天基金/snapshot.json` | 提示运行「天天基金账户数据采集」skill |
| 东方财富证券 | `投资理财/platforms/东方财富证券/snapshot.json` | 提示运行对应采集 skill |
| （其他平台） | `投资理财/platforms/<平台名>/snapshot.json` | 同上 |

- **至少一个平台有快照**：继续分析，在报告 header 中注明哪些平台已采集、哪些缺失
- **所有平台均无快照**：停止并告知用户先采集数据

### 0.3 读取并解析快照

对每个平台的快照，提取以下信息并合并为统一的家庭资产视图：

- `snapshot_time`：快照生成时间（ISO 8601，北京时间 +08:00）
- `accounts`：各账户的总览、持仓明细、定投计划、自选基金
- 已采集账户列表

**快照数据结构说明（以天天基金格式为参考）：**

| 字段 | 说明 |
|-----|------|
| `accounts[].overview` | 账户总资产、活期宝、基金资产、投顾、养老等 |
| `accounts[].holdings` | 基金持仓列表（含 `in_transit` 在途标记） |
| `accounts[].drip_plans` | 定投计划列表（含 `status`: 正常/已暂停） |
| `watchlists[].funds` | 护照账户自选基金列表（含申购状态和限购信息） |

### 0.4 计算数据时效

对每个平台分别计算 `snapshot_time` 与当前时间的时间差，在报告 header 中逐平台注明：

| 时间差 | 提示文案 |
|-------|---------|
| < 24 小时 | 快照生成于 X 小时前 |
| 1～3 天 | 快照生成于 X 天前 |
| 3～7 天 | 快照生成于 X 天前，如近期有操作建议重新采集 |
| > 7 天 | ⚠️ 快照生成于 X 天前，数据已超过一周，建议重新采集后再分析 |

即便快照较旧，也**继续分析**，不要拒绝或中断，只在报告 header 中注明时间差。

---

## Step 0.5: 读取当前分析报告

> **此步骤的目的是让迭代分析具有延续性**：了解上一版报告的策略判断、近期操作动作、未完成的行动指令，以及当时对市场的思考，作为本次分析的背景参考。

### 0.5.1 定位当前报告

用 Read 工具直接读取 `投资理财/portfolio.md`。

- 若文件存在：继续执行 0.5.2。
- 若文件不存在：跳过此步骤，本次将首次创建 `投资理财/portfolio.md`。

### 0.5.2 读取并提取关键信息

用 Read 工具读取该 `.md` 文件，提取以下信息，供后续步骤引用：

| 信息项 | 提取位置 | 用途 |
|-------|---------|------|
| **上次行动指令** | 第一章「本期行动指令」 | 判断是否已执行、是否需要跟进 |
| **当前持仓策略判断** | 第三章持仓明细 + 第五章配置结构 | 延续或调整持仓逻辑 |
| **上次市场信号灯结论** | 第四章市场环境 | 对比本次信号，判断趋势变化 |
| **已识别的风险点** | 第八章量化风险摘要 | 持续跟踪风险状态是否改善 |
| **上次报告日期** | 文件名或报告 header | 计算距上次分析的间隔天数 |

提取后，**在本次报告的行动指令章节中**，用一小节「上次指令跟进」标注：哪些指令已完成、哪些未完成、哪些因市场变化需要调整。

---

## Step 0.6: 组合量化指标计算

> **纯离线计算，从快照数据推算，无需联网。** 计算结果是报告"六、组合量化指标"和"八、量化风险摘要"的数据来源，必须在联网查询之前先算好。

依次执行以下计算（详细公式和关键词合并规则见 [quant-analysis.md](quant-analysis.md)）：

> **⚠️ 必须用 Shell 调用量化脚本，而非手动加总。** 持仓数量多时（如跨账户共持有几十只基金）手算误差不可控。


```bash
python3 .cursor/skills/portfolio-analysis/scripts/quant_calc.py \
  "投资理财/platforms/天天基金/snapshot.json"
```

脚本会一次性输出：HHI、N_eff（含信号判断）、各策略权重、S1/S2/S3 压力损失、流动性覆盖月数。详细逻辑见 [scripts/quant_calc.py](scripts/quant_calc.py)。

1. **运行脚本**：Shell 执行上方命令，获取所有量化数据
2. **仓位缺口**：每个策略的 `target_weight - current_weight`（需手动对照 `investment-preferences.md` 五），缺口 > 2% 列为买入候选
3. **输出量化摘要**：记录脚本输出结果，供后续步骤引用（仓位缺口结果将在 Step 2 技术过滤和行动指令中引用）

---

## Step 1: 获取市场数据（akshare MCP）

**读取快照数据后，统一获取一次市场数据。**

MCP 服务器：`project-0-家庭中枢-akshare`，工具：`search_functions` / `execute_function`

### ⚠️ 调用格式（必须遵守）

akshare MCP 的 `execute_function` 工具参数需要包一层 `request` wrapper，否则会报错：

```json
// ✅ 正确格式
{
  "request": {
    "function_name": "index_us_stock_sina",
    "params": { "symbol": ".IXIC" }
  }
}

// ❌ 错误格式（会报 validation error）
{
  "function_name": "index_us_stock_sina",
  "params": { "symbol": ".IXIC" }
}
```

### 必获取数据

```python
# 美股（影响 QDII 基金）——并行调用
execute_function(request={"function_name": "index_us_stock_sina", "params": {"symbol": ".IXIC"}})  # 纳斯达克综合
execute_function(request={"function_name": "index_us_stock_sina", "params": {"symbol": ".INX"}})   # 标普500
# symbol 格式为 .XXX（点号开头），不是 ^XXX

# ⚠️ 注意：此接口返回「从 2004 年至今的每日 K 线历史数据」，字段仅有：
#   date / open / high / low / close / volume（共约 5,500 条 × 8 行 = 50,000 行）
#   没有 PE、新闻、基本面等任何其他信息。
# 结果为大文件，execute_function 会返回实际 output_file 路径，调用后立即用 Shell 读末尾：
#   Shell: tail -40 <execute_function 返回的 output 路径>
#   （每条记录 8 行，-40 约覆盖最近 3～5 个交易日，足够取最新收盘价和近期最高价）
# 不会漏掉任何重要信息——宏观/PE/叙事内容全部来自 WebSearch，不依赖此接口。

# A股指数——并行调用
# stock_hk_index_spot_sina 同时包含 A股 指数（CSI300、SSECOMP、SSE50等），可作为主要 A股数据来源
execute_function(request={"function_name": "stock_hk_index_spot_sina", "params": {}})

# 港股（同上，stock_hk_index_spot_sina 同时包含 HSI、HSTECH、HSCEI 等）

# 汇率——⚠️ currency_boc_sina 只返回 2023 年历史数据，不是实时汇率！
# 直接跳过，改用 WebSearch 获取实时数据：
# "US dollar index DXY current level YYYY" / "USD CNY exchange rate YYYY"
```

### 按需获取数据

```python
search_functions(keyword="fund open info em", include_detail=True)  # 基金历史净值
search_functions(keyword="macro usa interest rate")                  # 美联储利率
execute_function(request={"function_name": "macro_china_gdp", "params": {}})  # 中国宏观
```

### akshare MCP 不可用时的备选

使用 WebSearch 搜索关键词替代（参见 [research-sources.md](research-sources.md)）。

---

## Step 2: 全球市场数据查询（写报告行动指令和第四章前必须完成）

> **核心原则**：先查数据，再写结论。每条买入建议必须基于当日实查点位，明确告知「现在能不能买」，**禁止**出现「等回调至XX再买」而不说明当前多少点的模糊写法。
>
> **信息来源原则**：WebSearch 时**优先使用英文搜索词、英文来源**（reuters.com、ft.com、bloomberg.com、investing.com、yardeni.com 等）。仅在必要时（如 A 股专有数据）才使用中文来源。

### 必查项目（一次并行 WebSearch，全部用英文搜索词，在同一消息中发出）

| 搜索词 | 用途 |
|-------|------|
| `"Nikkei 225 current price today YYYY"` | 日本当前点位 |
| `"KOSPI index current level YYYY"` | 韩国当前点位 |
| `"DAX index current level YYYY"` | 德国当前点位 |
| `"global stock market PE ratio comparison YYYY"` | 各市场估值横向比较（yardeni.com 优先） |
| `"Fed FOMC decision CPI YYYY"` / `"US China tariff latest YYYY"` | 宏观背景 |
| `"global military conflict geopolitical risk YYYY"` | 战争/军事冲突现状（俄乌/中东/台海等） |
| `"VIX index current level"` / `"Buffett indicator YYYY"` | 市场情绪与泡沫评估 |
| `"Fed funds rate current YYYY"` / `"CME FedWatch rate probability"` | 利率周期阶段判断 |
| `"US dollar index DXY current level YYYY"` | 美元周期（影响全部 QDII 净值） |
| `"USD CNY exchange rate today YYYY"` | **实时美元兑人民币汇率**（必查，currency_boc_sina 只有历史数据，不可用） |
| `"S&P 500 52 week high current YYYY"` / `"Nasdaq 100 52 week high YYYY"` | **标普500/纳斯达克100距52周高点距离**，用于判断是否追高红线（<5%则停止新增） |

### 技术过滤（QDII 境外市场专用，并行 WebSearch）

> **适用范围：仅用于 QDII 境外市场（日本、德国、韩国、印度等）。A股不适用技术过滤，A股入场判断见第七章「A股风险评估」的 5 条前提条件。**
>
> **规则**：对于仓位缺口 > 2% 的低配 QDII 境外策略（来自 Step 0.6 量化计算），必须完成技术过滤后才能给出"立即买入"建议。
>
> **⚠️ 执行要求：在一次消息中并行发出所有目标市场的技术过滤 WebSearch（不要分批），避免反复请求。**

| 搜索词 | 用途 |
|-------|------|
| `"Nikkei 225 200-day moving average YYYY"` | 日本趋势：是否在200MA上方 |
| `"Nikkei 225 6 month 12 month performance return YYYY"` | 日本动量：6M/12M涨跌幅 |
| `"KOSPI 200 day moving average current YYYY"` | 韩国趋势 |
| `"DAX index 200 day moving average YYYY"` | 德国趋势 |
| `"Nifty 50 200 day moving average YYYY"` | 印度趋势 |
| `"CAC 40 200 day MA YYYY"` | 法国趋势 |

**技术判断矩阵（每个市场填写）：**

| 市场 | 指数>200日MA？ | 6M动量 | 12M动量 | 技术信号 |
|------|-------------|-------|--------|---------|
| 日本 Nikkei | 是/否 | +X% | +X% | 🟢/🟡/🔴 |
| 韩国 KOSPI | 是/否 | +X% | +X% | 🟢/🟡/🔴 |
| 德国 DAX | 是/否 | +X% | +X% | 🟢/🟡/🔴 |
| 印度 Nifty50 | 是/否 | +X% | +X% | 🟢/🟡/🔴 |

**技术信号判定：**
- 🟢：指数>200MA **且** 6M/12M双正动量 → 技术面确认，可积极入场
- 🟡：指数>200MA **但** 动量混合 → 可月定投，不宜大额一次性买入
- 🔴：指数<200MA → 不建议新建仓；已有定投的维持，不追加

### 查完后输出信号灯表（再写行动指令和第四章市场环境）

对照 [research-sources.md → 全球市场机会评估](research-sources.md) 中的通用框架，结合实时查询数据判断信号灯。同时参考个人配置文件中的「关注市场」优先级和「关注投资主题」作为关联度评分依据：

| 市场 | 当前点位（实查） | 距52周高点 | 当前PE（实查） | 信号灯 | 结论（直接告知） |
|-----|--------------|---------|------------|-------|--------------|
| 日本 Nikkei225 | （填实际数字） | -X% | （填实际数字） | 🟢/🟡/🔴 | ✅立即月定投 / 🟡小额定投 / 🔴暂不买 |
| 韩国 KOSPI | （填实际数字） | -X% | （填实际数字） | 🟢/🟡/🔴 | ✅立即月定投 / 🟡小额定投 / 🔴暂不买 |
| 德国 DAX | （填实际数字） | -X% | （填实际数字） | 🟢/🟡/🔴 | ✅立即月定投 / 🟡小额定投 / 🔴暂不买 |
| 法国 CAC40 | （填实际数字） | -X% | （填实际数字） | 🟢/🟡/🔴 | ✅立即月定投 / 🟡小额定投 / 🔴暂不买 |
| 印度 Nifty50 | （填实际数字） | -X% | （填实际数字） | 🟢/🟡/🔴 | ✅立即月定投 / 🟡小额定投 / 🔴暂不买 |

**信号灯判定**：🟢 距高点>10% 且 PE 在合理区间 | 🟡 偏高但未极端，月定投为主 | 🔴 距高点<5% 或 PE 超历史均值30%以上

---

## Step 3: 备份并就地更新报告

### 3.0 备份当前报告

在写入新内容之前，**必须先备份**当前报告：

```bash
# 文件名用本次运行时间戳，格式：YYYY-MM-DD_HH-MM.md
cp "投资理财/portfolio.md" \
   "投资理财/backups/YYYY-MM-DD_HH-MM.md"
```

- 若 Step 0.5 未找到现有报告（首次生成），跳过此步骤，直接创建 `投资理财/portfolio.md`。
- 若找到现有报告，备份成功后，**覆盖 `投资理财/portfolio.md`**（就地迭代，永远只有这一个报告文件）。

### 写作规范

金额用「万元」或完整数字+元（禁止 K/M），数字范围用「到」或「～」（禁止半角 `~`，Markdown 会渲染为删除线），收益用 `+96,880元（+40.67%）` 格式。完整规范见 [report-template.md](report-template.md)。

### 行动指令生成规范（必须遵守）

报告的第一章「🎯 本期行动指令」是读者最关注的部分，必须**明确、具体、数据支撑**。

#### 什么叫「明确」

| ❌ 不接受的写法 | ✅ 要求的写法 |
|--------------|------------|
| 可以考虑买入日本基金 | ✅ 买入 摩根日本精选（007280），X,XXX元（目标权重7.5%，当前0%，本期填补30%=X,XXX元），Nikkei今日XX,XXX点，PE约XX，在200日均线上方，6M/12M动量均正 |
| 纳斯达克估值偏高，注意风险 | ⏸️ 持有 广发纳斯达克100（270042），+X万元(+X%)，逻辑未破坏，权重X%（目标≤40%），策略：靠新资金稀释，不主动卖出 |
| 可以适当关注欧洲市场 | 🟡 维持定投 华安德国DAX（000614），100元/周，DAX今日XX,XXX，PE约XX，信号中性，技术面200日均线上方 |
| 等市场回调再看 | 🔴 暂不操作 — 等待条件：DAX跌破200日均线且PE低于XX时考虑入场（当前PE XX，距200日MA差X%） |

#### 仓位定量写法要求（新增）

每一条买入建议必须包含仓位计算说明：

```
权重缺口：目标 X%，当前 X%，缺口 +X%
本期填补比例：X%（首建/加仓/绿灯积极）
建议金额：家庭总基金资产 X万元 × 缺口X% × 填补比例X% = X,XXX元
```

填补比例参考：
- 首次建仓（全新策略）：30%
- 已有持仓、信号中性：50%
- 估值+技术双确认（均绿灯）：70%，上限不超过单策略月度可买额

#### 行动图标规范

| 图标 | 含义 | 使用场景 |
|-----|------|---------|
| ✅ | 立即执行 | 买入、启动定投、调整定投金额/频率 |
| 🟢 | 维持 | 当前定投计划继续，无需变动 |
| 🟡 | 建议调整 | 定投金额建议减少/增加，或建议观察等待 |
| 🔴 | 建议暂停/不操作 | 定投建议暂停，或某市场暂不入场 |
| 🚫 | 清仓止损 | 持仓逻辑已根本改变，分批赎回 |
| ⏸️ | 继续持有 | 持仓无需操作，明确说明原因 |

#### 「理由」列的写作要求

- **必须包含实查数据**：点位、PE、距高点距离等，来自本次 Step 2 的实际查询结果
- **必须说明逻辑**：为什么这个数据支持这个操作
- **禁止模糊表达**：不得写「估值合理」「可以考虑」「市场有机会」等无具体依据的表述
- **操作纪律**：以个人配置文件 `investment-preferences.md` 第六节为准，不得与之矛盾

> 利率周期、美元周期、QDII 特殊风险、量化风险管理框架（HHI/技术过滤/压力测试/仓位定量）详见 [research-sources.md](research-sources.md)。

### 报告结构

报告分**两大部分**，完整模板见 [report-template.md](report-template.md)：

**第一部分：行动指令（先写）**
- **一、本期行动指令** — 操作清单（立即执行 / 定投计划状态 / 持仓处置 / 自选行动）
  - **1.0 上次指令跟进**（迭代报告必有此节）— 对照 Step 0.5.2 提取的上次行动指令，逐条标注执行状态：✅已完成 / ⏳未完成（仍有效）/ 🔄需调整（市场变化）/ ❌已失效（逻辑改变）

**第二部分：分析支撑（后写）**
- **二、家庭资产总览** — 三账户汇总表
- **三、各账户持仓明细** — 总览 + 持仓明细（按市值排序，含当前权重列）
- **四、当前市场环境** — 主要指数 + 全球信号灯（含技术面）+ 宏观背景
- **五、家庭配置结构分析** — 资产结构、同指数假分散、各账户风险画像、盈亏分布、**关注主题覆盖度分析（5.5）**
- **六、组合量化指标** — HHI/Effective N、情景压力测试、仓位缺口表、费用拖累
- **七、A股风险评估** — 逐条核查加仓前提条件
- **八、量化风险摘要** — 集中度/美股/汇率/地缘/情绪/流动性（🔴🟡🟢）

报告 header 须包含风险速览一行（从量化风险摘要提炼）：

```markdown
> 平台数据：天天基金 ✅（X 小时前）/ 东方财富证券 ❌（未采集）/ …
> 采集账户：（账户1）✅ / （账户2）✅ / （账户3）❌（未采集）
> 市场数据：分析时实时获取（akshare MCP + Web Search）
> 量化计算：`quant_calc.py` 脚本精确计算（非手算）
> 上次分析：YYYY-MM-DD（距今 X 天），备份于 `投资理财/backups/`
> 风险速览：集中度 🔴 | N_eff=X.XX（预警线3.0）| 情景最大压力 S3=-XX万（-X.X%总资产）| 美股 🟡 | 汇率 🟡 | 地缘 🟡 | 情绪 🟢
```

> **注**：S3 百分比分母统一使用家庭完整总资产（含投顾+养老），与报告正文各章保持一致口径。

---

## 行动指令各节的分析要点

### 1.2 定投计划状态（分析要点）

数据来源：快照 `accounts[].drip_plans`，按账户分组。

**正在执行的定投（status: 正常）逐一评估：**
- 标的当前市场信号灯：🟢继续 / 🟡酌情调整 / 🔴建议暂停
- 金额是否与账户规模和目标配置相称
- 是否在已严重超配的标的上叠加定投
- 频率是否合适（日定投 vs 月定投与标的波动性的匹配）

**已暂停的定投（status: 已暂停）逐一评估：**
- 原始逻辑是否仍然成立 → 若成立且市场信号绿灯，建议重启
- 原始逻辑已不成立 → 建议彻底清除此定投计划

### 1.3 现有持仓处置（分析要点）

- **所有大仓位盈利持仓**必须在「继续持有」栏中列出，附持有逻辑（一句话）和当前策略权重，不得跳过
- **需要决策的持仓**触发条件：① 逻辑根本改变 ② 单账户占比>70% ③ 亏损且主题逻辑破坏 ④ 策略权重超目标+10个百分点
- 持仓收益数据来自快照 `holdings[].holding_income` 和 `holding_income_rate`
- 在「继续持有」表中增加「当前权重」列，来自 Step 0.6 的计算结果

### 1.4 自选基金行动（分析要点）

数据来源：快照 `watchlists[].funds`。注意：
- `can_purchase: false` 或 `purchase_status: "暂停申购"` → 标注无法买入，直接给出🔴
- `max_purchase_per_day` 有限额 → 在建议方式中说明分批买入计划
- 逐一对照个人配置文件「关注投资主题」评估契合度
- 结合 Step 2 信号灯给出明确建议，不得写「可以关注」「待评估」等模糊结论

---

## 参考资料

- akshare 基金/市场函数索引：[akshare-functions.md](akshare-functions.md)
- 辅助数据来源（Web Search）和风险评估框架：[research-sources.md](research-sources.md)
- 完整报告模板：[report-template.md](report-template.md)
- 个性化投资偏好配置：`投资理财/config/investment-preferences.md`
- 量化指标计算详细公式：[quant-analysis.md](quant-analysis.md)
