# 真实接管状态矩阵(16 项)

As-of: 2026-07-13 12:40 UTC。判定纪律:**只有真实运行日志才算接管**。Perplexity Scheduled Task、文档、未运行脚本、dry-run、草稿、测试 fixture 一律不得写成 Hermes/Codex 已接管。

Owner 取值:PERPLEXITY-OWNED / HERMES-OWNED / CODEX-OWNED / DUAL-ENGINE / GITHUB-ACTIONS / MICKEY-MANUAL / NOT IMPLEMENTED。

| # | 任务 | 当前 Owner | 新 Owner(目标) | Schedule | 最近真实运行 | PASS | 日志 | 回滚 |
|---|---|---|---|---|---|---|---|---|
| 1 | 每日市场/持仓简报 | PERPLEXITY-OWNED(任务 9b9748d6) | LOCAL-DUAL-ENGINE(launchd `ai.tmc.daily_brief`) | 工作日 08:00 北京 | 2026-07-13 run#8;当日 13/13 数据独立复核 PASS | ✅ | `cron_tracking/9b9748d6/run_0008_*.json` + `round3-logs/04_brief_quality_review.md` | 本地失败→保持 Perplexity 任务(现仍启用) |
| 2 | 每周内容草稿 | PERPLEXITY-OWNED(d87c574c)+ 本地并行试运行 | LOCAL-DUAL-ENGINE(launchd `ai.tmc.weekly_content`) | 周一 09:00/09:30 北京 | 本地 2026-07-13 产出 `DRAFT_2026-07-13_method-note.md`,lint 震荡→NEEDS_FIX;v2 修复脚本已写好待安装(Mac 远程执行器中断) | ⚠️ NEEDS_FIX | `round3-logs/weekly_content_v2.py` + Mac `ops_migration/logs/` | 恢复 `.bak` 原脚本;Perplexity 任务仍启用 |
| 3 | 每周 GitHub 体检 | GITHUB-ACTIONS | GITHUB-ACTIONS(已接管) | 周一 01:30 UTC | 2026-07-13 run 29229659936,16s,STATUS OK | ✅ | Actions run 页 | Actions 页 Disable workflow→重启 Perplexity 任务 5196e484 |
| 4 | Weekly Radar(周报) | PERPLEXITY-OWNED(本轮主会话手动实跑 2026-W29) | DUAL-ENGINE(Hermes 叙事 + Codex 核验/构建,见 DUAL_ENGINE_PROTOCOL.md) | 每周(未排程) | 2026-07-13:`weekly_brief_mvp.py` 9/9 双源核验→/radar→归档→sitemap→RSS→Preview 162f19b2→CI 自动上生产(run 29249865816) | ✅ | `round3-logs/03_weekly_brief_run.log` | `git revert` + 重发 main;数据不合格→DATA_UNAVAILABLE 不猜 |
| 5 | System Build Log | CODEX-OWNED(页面已建并上线) | MICKEY-MANUAL 触发 + Codex 构建 | 按需(未排程) | 页面 /build-log 生产 200(Codex 阶段部署) | ✅(页面)/ 常态更新 NOT IMPLEMENTED | 站点 changelog `docs/SITE_CHANGELOG_PHASE2.md` | git revert |
| 6 | Engine Disagreement Brief | CODEX-OWNED(页面+首期内容已上线) | DUAL-ENGINE | 按需(未排程) | 页面生产 200;**周期性生成 NOT IMPLEMENTED** | ✅(页面) | 站内页面 | git revert |
| 7 | Deep Analysis | CODEX-OWNED(页面已上线) | DUAL-ENGINE | 按需(未排程) | 页面生产 200;**周期性生成 NOT IMPLEMENTED** | ✅(页面) | 站内页面 | git revert |
| 8 | 网站链接检查 | GITHUB-ACTIONS(CI verify-all `check_internal_links`) | 已接管 | 每次 push | 2026-07-13 CI run 29249865788 success | ✅ | Actions artifact verify-report | 无需(只读检查) |
| 9 | FACTS drift | GITHUB-ACTIONS(`check_facts_drift`,每次 push) | 已接管(站点侧);Mac 端 FACTS.md 41-54 行 Payhip 状态待更新(MICKEY/待执行器恢复) | 每次 push | 同上 CI run,PASS | ✅ | verify-report | 无需 |
| 10 | 产品价格 drift | GITHUB-ACTIONS(`check_price_drift`) | 已接管 | 每次 push | 同上 CI run,PASS | ✅ | verify-report | 无需 |
| 11 | secrets scan | GITHUB-ACTIONS(`check_secrets_scan` + weekly-health token 脱敏) | 已接管 | 每次 push + 每周 | 同上 CI run,PASS | ✅ | verify-report | 无需 |
| 12 | Cloudflare Preview | GITHUB-ACTIONS(deploy.yml:PR→preview)+ `tools/pages_deploy.py --branch` 手动 | 已接管 | 每 PR / 按需 | 2026-07-13 preview 162f19b2(w29-brief-preview 分支)四端点 200 | ✅ | `round3-logs/03_weekly_brief_run.log` | 删除 preview 部署即可 |
| 13 | Production smoke test | GITHUB-ACTIONS(deploy.yml `Smoke test production` 步骤) | 已接管 | 每次 main 部署后 | 2026-07-13 run 29249865816(部署+smoke 一体)success;人工复核四端点 200 | ✅ | Actions run 页 | 失败即部署标红,git revert |
| 14 | Payhip 链接更新 | CODEX-OWNED(5 商品真实上架,链接已写入 products.html 并逐行核对) | MICKEY-MANUAL(Payhip 后台)+ repo PR;CI `check_payhip_links` 守护 | 按需 | 2026-07-13 上架部署 9d455784;本轮人工复核买链在位 | ✅ | `docs/PAYHIP_TEST_CHECKLIST.md` | Payhip 后台下架 + git revert |
| 15 | 媒体草稿队列 | NOT IMPLEMENTED(本轮任务,media-ops/ 建设中) | HERMES-OWNED 起草 + MICKEY 人工发布 | 每周 | 无 | — | (待建)`media-ops/` | 不适用(仅草稿,永不自动发布) |
| 16 | 流量和销售周报 | NOT IMPLEMENTED(CF Web Analytics beacon token 仍为占位符 `REPLACE_WITH_CF_TOKEN`;`tmc-events.js` 已挂页面但无后端) | CODEX-OWNED 汇总 + MICKEY 提供 Payhip 销售数 | 每周 | 无 | — | (待建) | 不适用 |

## 结论(诚实口径)

- **已真实接管**(有运行日志):#3 GitHub 体检、#8–13 质量门与部署链(GitHub Actions,2026-07-13 全绿)。
- **已实跑一次、未常态化**:#4 Weekly Radar(2026-W29 全链路上产,需排程化交给双引擎)。
- **仍由 Perplexity 持有**:#1 每日简报、#2 每周内容(本地对应件分别为 PENDING 真实联网运行 / NEEDS_FIX)。三个 Perplexity 任务全部保持启用,直到本地真实运行合格且 Mickey 批准停用。
- **未实现**:#15 媒体队列、#16 流量销售周报(本轮在建);#5–7 的周期性内容生成未排程。
