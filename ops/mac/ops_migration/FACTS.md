# FACTS.md — TradingMapClaw 唯一事实基准 (Single Source of Truth)

Version: v2.2.0
As-of: 2026-07-15 (Asia/Shanghai)
Owner: Mickey Wei
Rule: 所有公开内容（网站、社媒、Newsletter、产品文案、README）里的数字与口径必须与本文件一致。
发现漂移 → 改内容，不改本文件；要改本文件必须 Mickey 批准并升版本号。

---

## 1. 系统权威数字 (v2.0 canon)

| 事实 | 值 |
|---|---|
| 定时任务 (scheduled workflows) | 对外使用 100+；精确总数/启用数待 Mac 快照核对 |
| Python 脚本 | 对外使用 hundreds；操作者报告 415+，待 Mac 快照核对 |
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

| 产品 | 价格 | 状态 (2026-07-13) |
|---|---|---|
| Tutorial 01 — Dual-Engine Verification | $19 | LIVE — Payhip direct checkout |
| Tutorial 02 — Cron Recovery & Self-Heal | $19 | LIVE — Payhip direct checkout |
| Tutorial 03 — Budget Watchdog | $19 | LIVE — Payhip direct checkout |
| Complete Bundle (3 tutorials) | $49 | LIVE — Payhip direct checkout |
| Patterns Bundle (7 skill packs) | $79 | LIVE — Payhip direct checkout |
| Standalone skill packs shown on Products page | $9 each | LIVE — Payhip direct checkout |
| Skills Library 订阅 | $29/mo | WAITLIST ONLY — 无 checkout |
| System Architecture Review (咨询) | $200 | LIVE — 邮件申请 + 人工确认 |
| Dual-Engine Setup Session (咨询) | $399 | LIVE — 邮件申请 + 人工确认 |
| Full Pipeline Blueprint (咨询) | $699 | LIVE — 邮件申请 + 人工确认 |

- 结账渠道：**Payhip 唯一** (https://payhip.com/TradingMapClaw)，PayPal 已在 Payhip 内绑定（中银香港）。
- Lemon Squeezy：仅为未来备选，**不得**建立结账、不得在公开内容中提及为现有渠道。
- 禁止出现的过期价格：$149、$99、$29 单课等旧价。
- 只有 FACTS 中标为 LIVE 且已配置直接链接的商品可使用购买 CTA；WAITLIST 项不得出现 checkout。

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

## 6. 内容管线口径

- 目录：public-content/{inbox,normalized,redacted,drafts,approved,rejected,archive,logs}
- 内容类型：WEEKLY_RADAR / MARKET_STRUCTURE_BRIEF / ENGINE_DISAGREEMENT / SYSTEM_BUILD_LOG / METHOD_NOTE / DEEP_ANALYSIS / RUN_RECORD
- Radar 页为数据驱动（模板 + validated JSON）；门禁未过 → 展示上一期并标注日期；样例数据必须带 SAMPLE 标签。
- Fail-open：公开内容管线失败不得影响内部研究系统。
