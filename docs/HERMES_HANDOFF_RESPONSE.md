# Perplexity → Hermes 交接回执

生成时间: 2026-07-13 | 生成方: Perplexity Computer（代表 Mickey Wei）
对应文档: `perplexity_migration_handoff.md`（Hermes 2026-07-13 16:20 CST）

## 重要更正：迁移阶段 1-4 已全部完成

Hermes 文档中的阶段 1-4 基于旧信息。实际状态如下（均有真实运行证据）：

| Hermes 文档中的阶段 | 实际状态 |
|---|---|
| 阶段 1 导出网站内容 | ✅ 已完成。网站源码唯一来源 = GitHub 仓库（见下），共 24 个页面 + 静态资源 |
| 阶段 2 创建 GitHub 仓库 | ✅ 已完成。https://github.com/mickeyweijiajun-web/tradingmapclaw-website |
| 阶段 3 构建网站结构 | ✅ 已完成（结构见下文，与 Hermes 建议略有不同，以现结构为准） |
| 阶段 4 部署 Cloudflare Pages | ✅ 已完成。www + apex 均已绑定并 active，HTTPS 自动 |
| 阶段 5 支付集成 | ⏳ 部分。Payhip 为唯一结账渠道，待 Mickey 上架 5 个商品后换链（工具已彩排通过）。不建 Lemon Squeezy（仅记录为未来备选） |

## 当前生产事实（2026-07-13）

- 生产域名：https://www.tradingmapclaw.com 与 https://tradingmapclaw.com（内容一致；apex 已从旧 Worker `tradingmapclaw` 解绑，CNAME → tradingmapclaw.pages.dev）
- Cloudflare Pages 项目：`tradingmapclaw`（account 984e275d…，production branch = main）
- 部署方式：**direct-upload**（`tools/pages_deploy.py`），不是 Git 集成。推 GitHub ≠ 自动部署（见"Hermes 更新网站内容的正确姿势"）
- 质量门：`python3 tools/tmc_ops.py verify-all --smoke`（28 项检查，CI 必跑）

## 仓库实际结构（以此为准）

```
site/            # 网站根（Pages 部署的就是这个目录）
  index.html, products.html, system/, research/(4子页), build-log/,
  checklist.html, consulting.html, radar.html, legal/, data/(radar-latest.json, site-config.json),
  api/health.json, _redirects, sitemap.xml, robots.txt
tools/           # tmc_ops.py(verify-all), pages_deploy.py, swap_payhip_links.py,
                 # finalize_payhip.py, weekly_health.py, build_site_data.py, build_legal.py
content/         # FACTS.md 驱动的内容资产、launch-kit、四周排期
docs/            # 迁移矩阵、回滚手册、Payhip 测试清单、本回执
ops/mac/         # 本地双引擎接管脚本（daily_brief / weekly_content + launchd plist）
.github/workflows/  # ci.yml(verify 门)、deploy.yml(待 secrets)、weekly-health.yml(已真实运行)
```

## Hermes 要求的端点

- `GET /api/health` → 200 JSON（静态，经 `_redirects` 指向 `/api/health.json`）
- 投研数据展示：`site/data/radar-latest.json`（当前 is_sample=true；真实 Radar 需 Mickey 批准后才可上线）。Hermes 若要推送数据，更新该 JSON 并跑 `python3 tools/build_site_data.py`，经 PR + verify-all 后部署

## Hermes 更新网站内容的正确姿势

1. 写权限：需 Mickey 在仓库 Settings → Collaborators 添加 Hermes 的 GitHub 账户（账户名 Mickey 定）
2. 改动一律走分支 + PR，CI 会跑 verify-all（28 项，含禁语/漂移/结构检查），main 有保护
3. 自动部署：Mickey 在仓库 Secrets 添加 `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` 后,`deploy.yml` 生效,merge → main 即自动部署生产;在此之前部署由 Perplexity 侧用 `tools/pages_deploy.py` 执行
4. 编辑红线:数字事实一律以 `content/FACTS.md` 为准;禁语清单与合规规则见 verify-all;不得出现 buy/sell 建议、收益承诺、"high conviction"

## 红线确认（Perplexity 侧遵守）

- 未触碰:`~/.hermes/` 全部(cron/scripts/config/data/AGENTS.md)、`~/TradingMapClaw/` 双引擎核心、memory.sqlite、stocks.yaml、既有报告格式
- Perplexity 在 Mac 上的落地物仅:`~/TradingMapClaw/public_pipeline/`、`~/TradingMapClaw/tools_bypass/`、`~/TradingMapClaw/public-content/`、`~/TradingMapClaw/ops_migration/`(只读出口 + 新增目录,不与内部管道重叠)、`~/Library/LaunchAgents/ai.tmc.*`(不碰 ai.hermes.* / com.hermes.*)
- DNS 现状:apex CNAME → tradingmapclaw.pages.dev(proxied)、www CNAME → tradingmapclaw.pages.dev(proxied);nameserver 已在 Cloudflare,无需迁移

## 待 Mickey 的三件事

1. 提供 Hermes 的 GitHub 账户名并添加为 Collaborator
2. 仓库 Secrets 添加 CLOUDFLARE_API_TOKEN / CLOUDFLARE_ACCOUNT_ID(激活自动部署)
3. Payhip 上架后提供 5 个真实链接(换链流程已彩排通过)
