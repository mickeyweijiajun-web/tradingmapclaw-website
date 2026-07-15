# SPEC — 网站第二阶段改造（子代理 A 执行）

工作目录：/home/user/workspace/repo/tradingmapclaw-website
唯一事实基准：FACTS.md（读它，所有数字/价格/模型名/合规红线以它为准）
现有站点在 site/（v2.0 设计已合格 — 复用现有 CSS/nav/footer/设计语言，不重做设计，不引入框架，纯静态 HTML+CSS+JS）。

## A. 修复（必须）
1. site/radar.html:69 "high conviction" → "high research priority"（保留 S-Factor 分段含义）。全站 grep 复查无 "high conviction"。
2. 死日期数据驱动化：index.html 里 "Latest update: 2026-07-12" 与 "Next scheduled publication: … Monday, July 13, 2026" 改为由构建脚本注入：
   - 新建 site/data/radar-latest.json：{"period":"2026-W28","data_as_of":"2026-07-10","published_at":"2026-07-12","is_sample":true,"status":"SAMPLE","next_publication":"auto","rows":[…现 radar.html 表格行的结构化版本…]}
   - 新建 tools/build_site_data.py（stdlib only, python3.9 兼容）：读 radar-latest.json，把值写进 HTML 注释标记之间，如 <!--TMC:latest-update-->2026-07-12<!--/TMC:latest-update-->；next publication 自动算下一个周一；radar-latest.json 里 is_sample=true 时页面显著标 "SAMPLE — illustrative only"。给 index.html 与 radar.html 加标记。脚本幂等、--check 模式返回非零表示需要重建。
3. products.html：确认 5 个 PAYHIP_LINK 占位（tutorial-01/02/03、bundle、patterns 共 5 个；若只有 4 个则补齐 bundle 占位为 PAYHIP_LINK:bundle-49），JSON-LD availability=PreOrder，CTA 文案与 FACTS.md 产品状态一致（不得出现 Buy now available）。
4. canonical 全站指 https://www.tradingmapclaw.com/<page>；sitemap.xml 与 llms.txt 补新页面；robots.txt 不变。

## B. 新页面（复用现有设计，均带合规 footer 声明）
- site/system/index.html：系统页 — 把 index.html 的 All-Weather Run 时间表整块迁来（迁移后首页删除该区块），加架构图文字版（Engine1/Engine2/Council/fallback，按 FACTS §2）。
- site/research/index.html：Research hub — 4 类入口卡片。
- site/research/radar/index.html：Radar 归档索引（本期 = SAMPLE，注明；结构支持后续每周新增 <li>）。
- site/research/market-structure/index.html、site/research/engine-disagreements/index.html、site/research/methods/index.html：栏目页，各含 1 条 SAMPLE 占位条目（标 SAMPLE）+ 栏目说明。
- site/build-log/index.html：Build Log — 3 条真实里程碑（v1→v2 重构、100+ 定时任务、$55 预算工程，从 FACTS/llms-full.txt 取材），标注日期。
- site/checklist.html：免费 lead magnet "Financial Research Checklist" — 纯客户端静态清单（研究流程 12-15 项 checkbox，localStorage 记忆），页面顶部 email 订阅框（复用现有 newsletter 表单机制），红线：不含买卖建议/目标价/仓位建议。
- site/consulting.html：咨询资格表 — 静态表单，字段：姓名、email、想解决的问题(textarea)、现有技术水平(select)、预算档($200/$399/$699/not sure)；提交 = mailto: 组装（现有 get-access.html 模式）；禁止询问持仓金额/账户/密码。

## C. 首页重构（不无限加长 — 目标 ≤ 现长度）
顺序：Hero → Market Coverage → How Dual-Engine Works（保留）→ Latest Intelligence（新，数据驱动块：显示 radar-latest.json 的 period/as-of/SAMPLE 标签 + 链到 /research/radar/）→ Free Archive → Products（价格从 FACTS）→ Consulting（3 档价 + 链 consulting.html）→ Founder Story 摘要（链 story.html）→ Newsletter CTA → Footer。
All-Weather Run 时间表区块整块删除（已迁 /system/）。导航加 Research / System / Build Log。

## D. Newsletter CTA A/B（可切换文案，不随机分流）
site/data/site-config.json：{"cta_variant":"A","analytics_enabled":false}
两套文案：A "Get the weekly radar brief" / B "See what 100+ jobs found this week"。build_site_data.py 按 variant 注入。

## E. 匿名事件埋点（隐私友好，默认关）
site/assets/js/tmc-events.js：window.tmcEvent(name) → analytics_enabled=false 时仅 console.debug；true 时发 GoatCounter（预留 endpoint 常量）。事件：page_view, newsletter_submit, radar_view, product_click, payhip_click, consulting_mail_click, github_click。在相应元素挂 data-tmc-event 属性 + 统一监听。无 cookie、无指纹、无第三方脚本（GoatCounter 仅 enabled 时动态注入）。

## F. 完成标准
- python3 tools/build_site_data.py 真实跑过且幂等（跑两次 diff 为空）
- 全站无 "high conviction"、无 2026-07-12 死日期残留（data 注入除外）、无 FACTS 禁用旧数字
- 所有新页移动端可读（viewport、现有响应式 class）
- sitemap/llms.txt 已更新；把改动清单写到 docs/SITE_CHANGELOG_PHASE2.md
