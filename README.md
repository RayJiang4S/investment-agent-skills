# investment-agent-skills

Cursor Agent Skills for personal investment management. These skills enable an AI agent in [Cursor IDE](https://cursor.com) to collect investment account data from brokerage platforms and generate a comprehensive cross-platform portfolio analysis report — all without leaving the editor.

> **Data privacy**: This repository contains only skill logic (AI instructions). All personal data — account snapshots, holdings, investment preferences — lives in a separate private workspace and is never part of this repo.

---

## How it works

Skills are structured instruction files that tell the Cursor AI agent what to do step by step. This repo implements a two-layer design:

```
snapshot/          ← Layer 1: Platform-specific data collection
│                     Each skill controls a browser to scrape account data
│                     and saves it as a local snapshot.json
└── tiantianjijin/ ← Tiantian Fund (天天基金)

analysis/          ← Layer 2: Cross-platform analysis
                      Reads all available platform snapshots, fetches live
                      market data, and produces a unified portfolio report
```

**Data flow:**

```
Browser (brokerage site)
        │  snapshot skill collects
        ▼
platforms/<platform>/snapshot.json   (private workspace)
        │  analysis skill reads
        ▼
投资理财/portfolio.md                 (living report, iteratively updated)
```

---

## Skills

### `snapshot/tiantianjijin` — Tiantian Fund snapshot

Navigates the Tiantian Fund trading site, collects holdings, drip investment plans, and watchlist data across multiple accounts, and saves the result to `platforms/天天基金/snapshot.json` in the workspace.

Before overwriting, it backs up the previous snapshot to `platforms/天天基金/backups/`.

**Trigger phrases:** 采集数据 / 生成快照 / 更新持仓 / sync watchlist / collect data

### `analysis` — Portfolio analysis

Reads snapshots from all platforms found under `platforms/*/snapshot.json`, fetches live market data via [akshare MCP](https://github.com/akfamily/akshare) and web search, then produces or updates a single living report at `投资理财/portfolio.md`.

Key capabilities:
- Cross-platform asset consolidation
- Quantitative metrics: HHI concentration, effective N, scenario stress tests
- Global market signal matrix (Japan, Korea, Germany, India, France…)
- Technical filter (200-day MA + 6M/12M momentum) before buy recommendations
- A-share entry condition checklist
- Iterative updates: each run carries forward the previous report's strategy context; old reports are backed up to `投资理财/backups/`

**Trigger phrases:** 帮我看看基金 / 出报告 / 资产分析 / analyze portfolio / investment review

---

## Prerequisites

- [Cursor IDE](https://cursor.com) with Agent mode enabled
- A private workspace with the directory structure described below
- **For `analysis`**: akshare MCP configured in the workspace's `.cursor/mcp.json`
- **For `snapshot/tiantianjijin`**: a logged-in Tiantian Fund browser session

---

## Setup

### 1. Clone this repo

```bash
git clone https://github.com/RayJiang4S/investment-agent-skills.git
```

### 2. Link skills into your Cursor workspace

Cursor loads skills from `<workspace>/.cursor/skills/`. Create symlinks pointing to this repo (add `.cursor/skills/` to your workspace `.gitignore` — these are local environment links, not source files):

```bash
cd /path/to/your/workspace

mkdir -p .cursor/skills
ln -s /path/to/investment-agent-skills/snapshot/tiantianjijin \
      .cursor/skills/tiantianjijin-snapshot
ln -s /path/to/investment-agent-skills/analysis \
      .cursor/skills/portfolio-analysis

echo '.cursor/skills/' >> .gitignore
```

### 3. Set up your private workspace structure

The skills expect this layout in your workspace (no personal data in this repo):

```
投资理财/
├── portfolio.md                       ← living analysis report (auto-created)
├── config/
│   └── investment-preferences.md     ← your personal investment preferences
├── backups/                           ← report history (auto-managed)
└── platforms/
    └── 天天基金/
        ├── snapshot.json              ← current snapshot (auto-managed)
        └── backups/                   ← snapshot history (auto-managed)
```

Create `investment-preferences.md` with your personal settings (risk tolerance, target allocation, investment themes, etc.). The `portfolio-analysis` skill reads this file as the foundation of every analysis.

### 4. Configure akshare MCP (for `analysis`)

Add the akshare MCP server to your workspace's `.cursor/mcp.json`. Refer to the [akshare MCP documentation](https://github.com/akfamily/akshare) for setup instructions.

---

## Adding a new platform

1. Create `snapshot/<platform>/SKILL.md` with data collection instructions for the new brokerage
2. Create `platforms/<platform>/backups/` in your private workspace (add a `.gitkeep`)
3. On first collection, the skill writes `platforms/<platform>/snapshot.json`
4. The `analysis` skill automatically picks up new platforms via `platforms/*/snapshot.json`
5. Symlink the new skill: `ln -s .../snapshot/<platform> .cursor/skills/<platform>-snapshot`

---

## Repository structure

```
investment-agent-skills/
├── README.md
├── snapshot/
│   └── tiantianjijin/
│       ├── SKILL.md           ← agent instructions for data collection
│       └── website-guide.md   ← Tiantian Fund site structure reference
└── analysis/
    ├── SKILL.md               ← agent instructions for portfolio analysis
    ├── report-template.md     ← report format and writing standards
    ├── quant-analysis.md      ← quantitative metric formulas
    ├── research-sources.md    ← market data sources and risk frameworks
    ├── akshare-functions.md   ← akshare MCP function reference
    └── scripts/
        └── quant_calc.py      ← offline quantitative calculations script
```

---

## License

MIT
