# 定时任务迁移矩阵 — Perplexity → 本地双引擎 / GitHub Actions

As-of: 2026-07-13。状态说明：迁移完成的判定必须有真实运行日志，不得把计划算成已运行。

| 任务 | 原 Perplexity cron | 新 Owner | 新载体 | dry-run | 真实运行 | 日志位置 | 停用/回滚方法 |
|---|---|---|---|---|---|---|---|
| 每日市场简报 (B组8股+BTC/ETH) | `9b9748d6` 工作日 08:00 北京时间 | LOCAL-DUAL-ENGINE | `~/TradingMapClaw/ops_migration/daily_brief.py` + launchd `ai.tmc.daily_brief` (Mon-Fri 08:00 本地=北京时间) | 脚本已推送到 Mac /tmp/tmc_stage，沿管道测试 53/53 PASS；数据层 dry-run 被 pc 沙盒禁网阻断（记录于日志），需 Mickey 在终端跑一次 | PENDING（需终端/launchd 环境） | `~/TradingMapClaw/ops_migration/logs/daily_brief-<date>.json` + `brief-<date>.md` | `launchctl unload ~/Library/LaunchAgents/ai.tmc.daily_brief.plist`；回滚=重新启用 Perplexity cron |
| 每周内容草稿 (轮换主题→Substack) | `d87c574c` 周一 09:00 北京时间 | LOCAL-DUAL-ENGINE | `~/TradingMapClaw/ops_migration/weekly_content.py` + launchd `ai.tmc.weekly_content` (Mon 09:30 本地) | PENDING | PENDING | `~/TradingMapClaw/ops_migration/logs/weekly_content-<date>.json`；草稿在 `public-content/drafts/DRAFT_*.md` | 同上，label 换 weekly_content |
| 每周 GitHub 体检 | `5196e484` 周一 09:30 北京时间 | GITHUB-ACTIONS | `.github/workflows/weekly-health.yml` (Mon 01:30 UTC = 09:30 北京)，失败/漂移时开 GitHub issue | DONE (workflow_dispatch) | **DONE 2026-07-13** run 29229659936，16s，STATUS: OK，未建 issue（符合只在失败时通知），token 已脱敏 | Actions run 页面 + issue | 在 GitHub Actions 页面 Disable workflow；回滚=重新启用 Perplexity cron |

## 已知限制：pc 沙盒禁网

通过 Perplexity 远程执行（pc）在 Mac 上拉起的进程无法访问外网（curl/ping 均被阻断，实测 2026-07-13）。因此①②的联网 dry-run 必须由 launchd 或 Mickey 在终端手动触发：

```bash
# 安装（一次）：
bash /tmp/tmc_stage/ops_migration/install_ops.sh
# 或仅验证 dry-run（不安装）：
~/.hermes/hermes-agent/venv/bin/python /tmp/tmc_stage/ops_migration/daily_brief_tmp.py --dry-run
```

## 数据与红线（三任务共用）

- 每日简报：双源交叉核验（股票 Stooq+Yahoo，加密 Coinbase+Binance，容差 1.5%），不一致→ DATA_UNAVAILABLE 不猜测；草稿经独立数字核验（逐数对照源数据）+ 禁语扫描 + 未来日期扫描，核验失败不发送。
- 每周内容：数字只能来自 FACTS.md；lint 扫描旧价格/旧口径/Buy now；输出永远 DRAFT_ 前缀，不自动发布。
- 体检：只用内置 GITHUB_TOKEN，不打印任何 token；只在 FAIL/DRIFT 时通知。

## 原 Perplexity 任务处置

三个 Perplexity cron（9b9748d6 / d87c574c / 5196e484）**保持启用**，直到：
1. 本地/Actions 各完成至少一次真实运行且日志合格；
2. Mickey 明确批准停用。
届时在 Perplexity 任务页手动停用，或告知 Computer 代为停用（需确认）。

## Handoff：Mickey 需要做的

1. Mac Perplexity 桌面端把活动工作区设为 `/Users/mikicourage`（安装需要写权限）。
2. 安装后验证 `launchctl list | grep ai.tmc` 有两条。
3. GitHub repo `tradingmapclaw-website` → Settings → Secrets and variables → Actions，添加 `CLOUDFLARE_API_TOKEN`（Pages Edit 最小权限）与 `CLOUDFLARE_ACCOUNT_ID`（`984e275d2928a92b9602542421828fcb`）→ 之后 push main 即自动部署。
4. （可选）Mac 上 `gh auth login` 修复 GitHub CLI，本地也能推送。
