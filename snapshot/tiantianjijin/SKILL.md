---
name: tiantianjijin-snapshot
description: Collects fund account data from Tiantian Fund website (holdings, drip plans, passport watchlist) and saves as snapshot JSON. Use when the user asks to collect data, generate a snapshot, update holdings, sync watchlist, or mentions 采集数据/生成快照/更新持仓/同步自选基金.
---

# 天天基金账户数据采集 Skill

> 每次运行均**创建新快照文件**（不往以往运行的旧文件里追加）。同一次运行内若有多账户，首个账户创建新文件，后续账户追加到**本次的**同一文件；每采完一个账户立即写入，再询问是否继续，避免上下文膨胀。

## 浏览器使用说明

优先使用当前 Agent 环境内置的浏览器；若无内置浏览器，则使用系统浏览器。

---

## 总体流程

**通用原则**：`browser_navigate` 会自动返回当前页 snapshot，**不要**在 navigate 之后重复调用 `browser_snapshot` 取同一页；仅当页面需等待异步内容时再 `browser_wait_for` + `browser_snapshot`。

```
[开始]
  ↓
Step 0: 检查浏览器，识别当前已登录账户
  ↓
Step 1+2+3: 采集当前账户（总览 + 持仓 + 定投计划）
  ↓
Step S1: 立即写入快照文件，询问用户「还有其他账号要采集吗？」
  ↓
  【此处必须停止，等待用户回复；不得自行进入 Step W】
  ↓
  用户回复「有」 → 用户自行切换登录，告知后确认新账户 → 回到 Step 0
  用户回复「没有了」 → 方可开始 Step W: 采集自选基金
                ↓
  Step W: 采集当前通行证账户的自选基金，立即写入
                ↓
  【此处必须停止，等待用户回复】
                ↓
  用户回复「有」 → 用户自行切换通行证登录，告知后 → 回到 Step W
  用户回复「没有了」 → 全部完成，告知用户（见「完成后告知用户」格式）
```

---

## Step 0: 识别当前账户

导航到主页并确认登录状态：

```
browser_navigate("https://trade.1234567.com.cn/MyAssets/Default")
```

（navigate 已返回 snapshot，无需再调 `browser_snapshot`。）

| 情况 | 处理 |
|-----|------|
| 已登录 | 页面 title **含**「资产概况」且 snapshot 中出现 `listitem name: [姓名]`，读取账户名，继续 Step 1 |
| 跳转到登录页 | URL 变为 `login.1234567.com.cn` 或 `passport.1234567.com.cn`、或 title 含「登录」→ 提示用户扫码登录后告知 |
| title 为「页面过期」| 重新 navigate 到主页 |

---

## Step 1: 获取资产总览

直接从 Step 0 `browser_navigate` 已返回的 snapshot 中提取（无需再次 snapshot）：

```
资产总额、活期宝余额、活期宝每日收益
基金资产总额、基金持仓收益、基金累计收益
投顾资产总额 / 投顾累计收益
养老资产总额 / 养老累计收益
```

⚠️ 主页基金资产卡片内有「买基金 持仓 | 卖出 | 转换」快捷链接，**不要点击**。

---

## Step 2: 获取基金持仓明细

直接 URL 跳转（左侧导航点击无效）：

```
browser_navigate("https://trade.1234567.com.cn/myAssets/hold")
```

（navigate 已返回 snapshot。）**仅当** snapshot 中只有表头（如「产品类型」「产品名称」「市值」）而无具体基金行（无基金名称链接）时，说明持仓由 JS 异步渲染，再执行：

```
browser_wait_for(time: 2)   ← 单位：秒
browser_snapshot
```

若持仓较多，snapshot 可能以「Large snapshot written to file」形式返回，需从 MCP 返回的 **Snapshot File** 路径读取（通常为 `~/.cursor/browser-logs/snapshot-<timestamp>.log`），按 listitem 结构解析每条持仓（基金名+代码、类型、净值、市值、收益、在途）。

持仓基金名称是 `<a>` 链接，可从 accessibility tree 读取。每条记录格式：

```
listitem「基金名（代码）| 类型 | 最新净值 X.XXXX（MM-DD）」
listitem「市值」
listitem「收益金额 收益率%」
```

提取字段：基金名称、代码、类型、最新净值及日期、市值、持仓收益（元）、持仓收益率（%）、是否有在途交易。

> 活期宝每日收益在此页精度更高（4位小数），用此值替代主页数字。

---

## Step 3: 获取定投计划

在**左侧边栏**（与「我的持仓」「交易查询」同组、在「基金交易」下方）点击「基金定投」进入定投计划页面。从当前页 snapshot 中取**与「我的持仓」「交易查询」同一区域的**「基金定投」link 的 ref（勿用顶部导航的「基金定投」，其 ref 在不同页会变）。

```
browser_click(element: "基金定投", ref: "上述左侧边栏中「基金定投」的 ref")
```

> 点击后通常直接进入定投计划页（URL 含 `Investment/default`，title 含「定投计划」），无需再点子菜单。若仅展开子菜单未跳转，再点击左侧「定投计划」链接。
> ⚠️ **入口区分**：页面上有两处「基金定投」——顶部导航栏与左侧边栏。必须使用**左侧边栏**中「我的资产」「我的持仓」「基金定投」「交易查询」同一区域的「基金定投」链接，勿点顶部导航的「基金定投」，否则可能进入错误入口。  
> `browser_click` 的 `element` 描述需与页面可见文本一致（如直接用「基金定投」），勿加多余修饰。  
> ① 主页卡片的「查看定投计划」链接是 JS 触发，实测无法跳转，禁止使用；② `browser_click` 返回的 snapshot 可能仍显示旧页面（SPA 渲染滞后），**不可用来读定投数据**，必须先 `browser_wait_for(time: 2)`（单位：秒）再截图。

定投计划表格是纯文字 `<td>`，**不出现在 `browser_snapshot` 中，必须截图读取**。  
⚠️ **必须采全**：表格常有多行，且页面下方还有「智能定投计划」等区域，**禁止一次滚动过多**（否则会把「普通定投计划」表格滚出视口）。  
**未在任一张截图中看到表格底部「共N条」之前，不得结束 Step 3**——必须继续「滚一屏、截一图」直到出现「共N条」，再用 N 校验汇总条数是否一致。

**推荐流程（短清单）**：  
1. `browser_take_screenshot()` 截当前视口（不滚动）；  
2. 若截图中已出现表格底部「**共N条**」且能看清所有「普通定投计划」行，则无需滚动；否则：循环 `browser_scroll(direction: "down", amount: 400)` → `browser_take_screenshot()`；  
3. 直到某张截图中出现表格底部「**共N条**」，合并「普通定投计划」行、去重，确认条数等于 N。

**不推荐**：先连续多次 `browser_scroll` 再 `browser_take_screenshot(fullPage: true)` —— 易把定投表格滚出视口，截到「智能定投计划」等。若用整页截图，也须先滚到定投表格底部（看到「共N条」）后再用。

（`browser_scroll` 参数为 `amount` 像素，不是 `distance`。）  
从截图汇总「普通定投计划」每条记录，提取：基金名称、代码、每期金额（元）、扣款频率、扣款日、计划状态（正常/暂停/已终止）。  
> 扣款周期若为「每日(交易日)」可归一为「每日」；扣款日为「1日」表示每月 1 号。

> 「活期宝定期充值计划」同页面，有则采集，`type` 记为 `"活期宝定期充值"`。  
> 「智能定投计划」仅 App 可操作，有则记录，字段不全属正常。  
> 无定投计划时（只有「新增」按钮），`drip_plans` 记为 `[]`。

---

## Step S1: 立即写入账户数据

完成 Step 1+2+3 后**立即写入**，不等后续账户。

**文件路径**：`~/Documents/Repositories/persional/家庭中枢/投资理财/platforms/天天基金/snapshot.json`  
（固定文件名，每次采集覆盖；写入前先将旧文件备份到 `platforms/天天基金/backups/YYYY-MM-DD_HH-MM.json`，后续账户追加到本次同一文件）

**首个账户** → 创建新文件：

```json
{
  "snapshot_time": "2026-03-01T14:30:00+08:00",
  "accounts": [
    {
      "name": "张三",
      "alias": "本人",
      "overview": { ... },
      "holdings": [ ... ],
      "drip_plans": [ ... ]
    }
  ],
  "watchlists": []
}
```

**后续账户** → 读取文件，将新账户对象追加到 `accounts` 数组，写回。

写入后**仅**提示用户（不得接着执行 Step W）：

```
✅ [账户名] 的数据已写入。

还有其他账号要采集吗？
  - 有的话：请在浏览器里切换登录（退出后用下一个账号扫码登录），完成后告诉我。
  - 没有了：告诉我「没有了」，继续采集自选基金。
```

**⚠️ 执行完本步后必须停止并等待**：必须等用户明确回复「没有了」后，才能开始 Step W 自选基金采集。不得在用户未确认时自行跳转到自选基金页面或执行任何 Step W 操作。

**用户回复「有」并切换完成后**：重新 navigate 到主页确认新账户姓名，然后回到 **Step 0**。

---

## Step W: 采集自选基金

**前置条件（必须满足才能执行本节）**：用户已明确回复「没有了」（无更多交易账号要采集）。若尚未收到该回复，不得执行 Step W，应停留在上一步等待用户回复。

**自选基金使用通行证登录，与交易账号完全独立。** 每采完一个通行证账户立即写入，再询问是否继续。

**数据来源原则（必须遵守）：**

- **每次统计/采集自选基金都必须从页面重新获取数据**，不得使用历史快照、以往截图或已有快照文件中的自选数据。
- 流程必须是：`browser_navigate` 到自选页 → 确认登录与「净值列表」视图 → **当次**截图（必要时滚动后再截）→ 从**当次**页面/截图内容逐行识别并写入 `watchlists[].funds`。
- 不得引用、合并、补全自任何其他时间点的快照或截图；若当次页面无法识别某字段，该字段填 `null` 并注明原因。

```
browser_navigate("https://favor.fund.eastmoney.com/")
```

### 判断通行证登录状态

`browser_navigate` 已返回 snapshot，优先从 snapshot 判断：

| snapshot 特征 | 状态 |
|---------|------|
| 出现 `link name: [账户名]`（如「爱也成习惯」）及「切换账号」「退出」链接 | ✅ 已登录 |
| 出现 `link name: 通行证登录` 或仅有「安全登录」 | ❌ 未登录 |

若 snapshot 无法明确判断，再截图确认（**多标签时截图前先 `browser_lock`**，避免截到错误 tab）：

```
browser_lock()
browser_take_screenshot()
browser_unlock()
```

**未登录时**提示用户：

```
请在浏览器中点击「通行证登录」按钮完成登录，登录成功后告诉我继续。
如不采集自选基金，告诉我「跳过自选基金」。
```

登录后重新 navigate 并截图确认，识别账户名。

**⚠️ 自选登录人（`watchlists[].account_name`）必须从页面「自选」区域读取，不能取顶部栏：**
- **正确**：自选区块内「欢迎 [账户名] 切换账号」或该区块里与「切换账号」「退出」同一行的账户名链接（如「爱也成习惯」）。
- **错误**：页面顶部「刘佳 安全退出」等是网站主头部，可能与通行证自选账户不一致，不可用作自选账户名。

### 切换到净值列表并采集

若当前不是「净值列表」视图，点击切换。

**自选基金必须采集的字段（不可缺漏）：**

| 字段 | 含义 | 来源 |
|------|------|------|
| `cumulative_nav` | 累计净值 | 表格「累计净值」列 |
| `daily_growth_value` | 日增长值（元） | 表格「日增长值」列 |
| `daily_growth_rate` | 日增长率（%，存数字如 0.27） | 表格「日增长率」列 |
| `since_inception_rate` | 成立以来涨幅（%，存数字如 84.67） | 表格「成立来」列 |
| `max_purchase_per_day` | 单日申购限额（字符串，如 `"500元"` `"--"` `"100万元"`） | 表格「单日申购限额」列 |
| `purchase_status` | 申购状态列文字 | 如「开放申购」「限大额」「暂停申购」 |
| `can_purchase` | 是否可购买 | 购买按钮：橙色=`true`，灰色=`false` |

⚠️ **表格中上述列在 snapshot/无障碍树中不可见，必须通过截图读取：**（**多标签时截图前先 `browser_lock`**）

```
browser_lock()   ← 多标签时先锁定
browser_take_screenshot()
browser_scroll(direction: "down", amount: 400)   ← 若内容超出一屏
browser_take_screenshot()
browser_unlock()
```

从截图**逐行**识别每只基金的：基金名称、代码、单位净值（及日期）、**累计净值、日增长值、日增长率、申购状态、购买按钮颜色**，全部填入 `funds[]` 对应字段，不得留空（无法识别时填 `null` 并注明原因）。

> `purchase_status`（申购状态列文字）与 `can_purchase`（按钮颜色）是两个独立字段，同为「限大额」时按钮颜色可能不同。

### 写入并询问是否继续

将当前账户数据追加到快照文件的 `watchlists` 数组：

```json
{
  "passport_account": "爱也成习惯",
  "funds": [
    {
      "name": "基金名称", "code": "000001",
      "nav": 1.1130, "nav_date": "03-06",
      "cumulative_nav": 3.6860,
      "daily_growth_value": 0.0030, "daily_growth_rate": 0.27,
      "since_inception_rate": 84.67,
      "max_purchase_per_day": "500元",
      "purchase_status": "开放申购", "can_purchase": true
    }
  ]
}
```

写入后**停止并等待用户回复**：

```
✅ [账户名] 的自选基金已写入（共 N 只）。

还有其他通行证账号要采集吗？
  - 有的话：请切换通行证登录，完成后告诉我继续。
  - 没有了：告诉我「没有了」，输出完成摘要。
```

**用户回复「有」**：用户切换通行证后告知，重新 navigate 到自选页确认新账户名，回到本节「判断通行证登录状态」继续采集。  
**用户回复「没有了」**：输出「完成后告知用户」格式的汇总摘要。

---

## 完成后告知用户

```
✅ 快照已完成：platforms/天天基金/snapshot.json

交易账户（共 N 个）：
  - 张三：持仓 X 只，定投 Y 条
自选基金（共 M 个通行证账户）：
  - 账户A：X 只
快照时间：YYYY-MM-DD HH:MM（北京时间）

如需分析报告，告诉我「帮我看看基金」或「出报告」。
```

---

## 操作安全规则

1. **只读**：仅用 `browser_snapshot` / `browser_take_screenshot` / `browser_click`（导航链接），不做任何交易操作
2. **禁止点击**：买基金、卖出、转换、充值、取现、新增定投、撤单、删除自选、添加自选
3. **定投页面**：仅查看「定投计划」，禁止点击「新增」「暂停」「终止」「修改」
4. 页面不符合预期时，从主页重新导航，不随意继续点击
5. **截图多标签**：执行 `browser_take_screenshot` 前如有多个 tab，先 `browser_lock` 锁定当前操作的 viewId，截完后 `browser_unlock`，避免截到错误标签页
6. **流程等待**：Step S1 完成后必须停止，等用户明确回复「没有了」后才能进入 Step W（自选基金）；严禁在未收到用户回复时提前跳转或执行自选采集。

---

## 参考资料

- 网站结构、字段解读、JSON Schema：[website-guide.md](website-guide.md)

---

## 自检清单（符合 Cursor Skill 规范）

- **Frontmatter**：`name` 小写连字符、`description` 第三人称且含 WHAT+WHEN 与触发词
- **篇幅**：SKILL.md 控制在 500 行内，细节放在 website-guide.md
- **引用**：仅一层引用（本文件 → website-guide.md）
- **术语**：快照、账户、自选、定投、持仓、通行证 统一用法
- **路径**：使用正斜杠，无 Windows 反斜杠
- **流程**：Step 0→1→2→3→S1→W 明确步骤与条件分支
