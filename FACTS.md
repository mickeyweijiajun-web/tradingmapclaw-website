# FACTS.md — TradingMapClaw 唯一事实基准 (Single Source of Truth)

Version: v2.1.0
As-of: 2026-07-14 (Asia/Shanghai)
Owner: Mickey Wei
Rule: 所有公开内容（网站、社媒、Newsletter、产品文案、README）里的数字与口径必须与本文件一致。
发现漂移 → 改内容，不改本文件；要改本文件必须 Mickey 批准并升版本号。

---

## 1. 系统权威数字 (v2.0 canon)

| 事实 | 值 |
|---|---|
| 定时任务 (scheduled workflows) | 对外只使用 100+；精确总数与启用数待 Mac 快照核对（Hermes 报告的 118/121 互相矛盾） |
| Python 脚本 | 对外只使用 hundreds；操作者报告 415+，待 Mac 快照生成可复核清单 |
| SKILL.md 模块 | 50+ |
| Tickers | 82 (75 unique)，5 个分组 (A/B/C/D/E) |
| 报告类型 | 13 |
| 数据源 | 12 |
| 成本 | $55/月预算上限；实际约 $7/月 (~13.5%) |
| 硬件 | 一台 Mac mini (Apple Silicon) |
| 交付渠道 | 英文 → Telegram；中文 → Feishu |
| 边界 | WATCHLIST_ONLY — 无券商 API、不下单、不执行交易 |

**禁止出现的过期数字**（v1.x 漂移信号）：119 或 115 个任务、500/502+ 脚本、93+ 技能、"three-engine/三引擎"、GPT-5.5（现役为 GPT-5.6）、"real-time data"（用 "updated weekly/daily" 表述）。

## 2. 引擎与模型口径

- Engine 1 — **Hermes Agent**：编排器；基本面、宏观、情绪推理；调度整条夜间管线。
- Engine 2 — **Codex / GPT-5.6**：独立核验；技术面与资金流；独立重算关键数字。
- **Multi-Model Council**：DeepSeek V4 Pro、GLM-5.2、GPT-5.6，另有本地 Qwen3 14B。
- Fallback 链：GLM-5.2 → GPT-5.6 → DeepSeek V4 Pro → Qwen3 14B (local, free)。
- 口号："One model can be confidently wrong. Two engines catch it. A council of three decides."
- 品牌：One Hand · One Bag · One System. Not pity. Visibility.

## 3. 产品与价格（唯一价格表）

> Baseline: 网站产品页 (https://www.tradingmapclaw.com/products) + Payhip 店铺 (https://payhip.com/TradingMapClaw)，2026-07-14 验证。

### 3a. 数字产品 (Digital Products — Payhip 即时下载)

| 产品 | 价格 | 状态 (2026-07-14) |
|---|---|---|
| Tutorial 01 — The $55 AI Research Stack (Beginner, PDF) | $19 | LIVE · Payhip 已上架 · 即时下载 |
| Tutorial 02 — Building the Dual-Engine System (Intermediate, PDF) | $19 | LIVE · Payhip 已上架 · 即时下载 |
| Tutorial 03 — The Solo-Operator Blueprint (Advanced, PDF) | $19 | LIVE · Payhip 已上架 · 即时下载 |
| The Solo-Operator Blueprint — Complete Bundle (3 volumes + extras, ZIP) | $49 | LIVE · Payhip 已上架 · 即时下载 |
| Engineering Patterns Bundle — 7 Production Skill Packs (ZIP) | $79 | LIVE · Payhip 已上架 · 即时下载 |

### 3b. Skill Minis (Payhip 即时下载)

| 产品 | 价格 | 状态 (2026-07-14) |
|---|---|---|
| Financial Research Checklist | $9 | LIVE · Payhip 已上架 |
| Earnings Research Prep | $9 | LIVE · Payhip 已上架 |
| Dual-Engine Verification Prompt | $9 | LIVE · Payhip 已上架 |
| Evidence vs. Counter-Evidence Matrix | $9 | LIVE · Payhip 已上架 |
| Market Research Journal Template | $9 | LIVE · Payhip 已上架 |

### 3c. 订阅

| 产品 | 价格 | 状态 (2026-07-14) |
|---|---|---|
| The Skills Library | $29/mo | WAITLIST ONLY — 无 checkout |

### 3d. 技术咨询服务 (邮件申请 + 人工确认)

| 产品 | 价格 | 状态 (2026-07-14) |
|---|---|---|
| Operator Consulting (60-min session) | $200 | LIVE — 邮件申请 |
| Research-System Audit (written report) | $399 | LIVE — 邮件申请 |
| Architecture Blueprint Session | $699 | LIVE — 邮件申请 |

- 结账渠道：**Payhip 唯一** (https://payhip.com/TradingMapClaw)，PayPal 已在 Payhip 内绑定（中银香港）。
- Lemon Squeezy：仅为未来备选，**不得**建立结账、不得在公开内容中提及为现有渠道。
- 禁止出现的过期价格：$149、$99、$29 单课等旧价。
- 禁止出现的过期产品名称（v2.0.x 漂移信号）：Dual-Engine Verification / Cron Recovery & Self-Heal / Budget Watchdog / Complete Bundle (3 tutorials) / Patterns Bundle (7 skill packs) / System Architecture Review / Dual-Engine Setup Session / Full Pipeline Blueprint。

## 4. 网站与部署口径

- 域名：https://www.tradingmapclaw.com （canonical，全站 canonical 指 www）
- Cloudflare Pages 项目：`tradingmapclaw`，Account `984e275d2928a92b9602542421828fcb`，production branch = main
- 源码唯一来源：GitHub repo `tradingmapclaw-website`；部署经 GitHub Actions (wrangler) 由 Git commit/PR 触发；Preview 通过后才进 Production。
- 已知问题：根域名 apex 未挂到 Pages（需 301 → www）。

## 5. 合规红线（公开内容）

1. 不输出 buy/sell/hold 指令 → 只用 bullish / neutral / bearish **scenario label**。
2. 不承诺收益，不出现 guaranteed / can't lose / beat the market。
3. 不伪造实时数据；数据一律带 as-of 日期；缺数写 DATA_UNAVAILABLE，不猜。
4. 不公开 Mickey 持仓、订单、账户、金额。
5. "high conviction" → 公开文案改用 "high research priority" 或 "high evidence density"。
6. 每页带 "Research & education only. Not investment advice. · WATCHLIST_ONLY" 声明。
7. 中文公开文案不写 "cron"，写 "定时任务"。
8. 所有公开输出默认 DRAFT；未经 Mickey 批准不得发布到社媒。
9. 虚构客户、虚构收益、虚构 testimonial：禁止。
10. 面向公众的研究必须是一般性、非个性化、固定频率发布；不得因单一证券的即时行情或事件临时催促发布。
11. 自动发布只允许确定性的系统更新日志。涉及证券、加密资产、宏观判断或量化数据的内容，必须 Hermes 与 Codex 双 PASS、双源可审计并经 Preview 门禁；默认不自动合并。
12. 结构/合规预检不得称为“独立事实核验”；未实际访问外部来源时必须标注 `external_fact_check=NOT_PERFORMED`。

## 6. 内容管线口径

- 目录：public-content/{inbox,normalized,redacted,drafts,approved,rejected,archive,logs}
- 内容类型：WEEKLY_RADAR / MARKET_STRUCTURE_BRIEF / ENGINE_DISAGREEMENT / SYSTEM_BUILD_LOG / METHOD_NOTE / DEEP_ANALYSIS / RUN_RECORD
- Radar 页为数据驱动（模板 + validated JSON）；门禁未过 → 展示上一期并标注日期；样例数据必须带 SAMPLE 标签。
- Fail-open：公开内容管线失败不得影响内部研究系统。
