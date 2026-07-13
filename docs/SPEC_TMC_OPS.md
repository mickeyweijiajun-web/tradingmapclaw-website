# SPEC — tools/tmc_ops.py verify-all 质量门（子代理 D 执行）

工作目录：/home/user/workspace/repo/tradingmapclaw-website
只写这三个文件：tools/tmc_ops.py、tools/weekly_health.py、docs/VERIFY_ALL.md。不改 site/ 下任何文件。
stdlib only，兼容 python3.9+。事实基准：FACTS.md。

## tools/tmc_ops.py
子命令：verify-all [--json PATH] [--site-dir site] [--base-url https://www.tradingmapclaw.com] [--skip-network] [--smoke]
输出：人类可读报告（每项 PASS/FAIL/WARN/SKIP + 原因）+ --json 机器可读 {"as_of":…,"checks":[{"id","status","detail"}],"summary":{"pass":n,"fail":n,"warn":n},"overall":"PASS|FAIL"}。
exit code：有 FAIL → 1，否则 0。WARN 不挡。

检查项（本地，无网络）：
1 py_compile tools/*.py
2 site/data/*.json 全部可解析且 radar-latest.json 含必填键(period,data_as_of,is_sample,rows)
3 secrets 扫描：site/ 与 tools/ 无 sk-/ghp_/github_pat_/AKIA/Bearer [A-Za-z0-9]{30,}/私钥块
4 FACTS 漂移：站点 HTML 不得出现禁用旧数字（119 jobs,115 jobs,500+ scripts,502+ scripts,93+ skills,three-engine,三引擎,GPT-5.5）
5 价格漂移：HTML 中 $149、$99 不得出现；$19/$49/$79/$200/$399/$699 至少在 products/consulting 出现
6 模型名单一：council 模型只能是 DeepSeek V4 Pro/GLM-5.2/GPT-5.6/Qwen3 14B
7 内链检查：所有 href/src 指向本站相对路径的文件必须存在
8 HTML 结构：每个 .html 标签配平（div/section/table/script），有 <title>、meta description、viewport
9 canonical：每页 rel=canonical 存在且以 https://www.tradingmapclaw.com/ 开头
10 sitemap.xml：包含全部对外 html 页（404.html、thank-you.html 可豁免），URL 均为 www 域
11 OG 标签：主要页面（index,products,radar,story,faq）有 og:title/og:description
12 Payhip URL 格式：href 含 payhip.com 的必须 https 且 /TradingMapClaw 或 /b/ 格式；PAYHIP_LINK: 占位若存在 → WARN（未换链）并要求 availability=PreOrder
13 WAITLIST 无 checkout：Skills Library 区块无 payhip /b/ 链接
14 SAMPLE 标签：radar-latest.json is_sample=true 时 radar.html 与 index.html 必须渲染 SAMPLE 字样
15 stale date：HTML 中出现的 20xx-xx-xx 日期若不在 TMC 注入标记内且早于今天 30 天以上 → WARN
16 持仓泄漏：不得出现 my position/我的持仓/账户余额/持仓金额 等模式
17 命令式交易语言：正文不得出现 you should buy/sell now/act now/buy before（education 语境豁免列表）
18 保证收益语言：guaranteed return/can't lose/beat the market/稳赚 不得出现
19 可访问性基础：img 有 alt，form input 有 label 或 aria-label
20 移动端基础：每页有 viewport meta；CSS 中存在 @media
21 build_site_data.py --check 幂等通过
22 llms.txt/llms-full.txt 存在且含 v2.0 与 118 字样
23 robots.txt 存在且引用 sitemap
24 404 页存在
25 config 完整性：site-config.json 的 cta_variant ∈ {A,B}，analytics_enabled ∈ bool

网络检查（默认跳过，--smoke 开启）：
26 GET base-url 主要页 200
27 线上首页含 "Dual-Engine" 且不含禁用旧数字
28 canonical 域与实际域一致

## tools/weekly_health.py
--out health-report.md。检查（用 env GH_TOKEN 可选，无则匿名 API）：
- repo mickeyweijiajun-web/tradingmapclaw-website 与 mickeyweijiajun-web/TradingMapClaw 的 open issues/PR 数、最新 commit 距今天数
- https://www.tradingmapclaw.com 主要页 HTTP 状态
- verify-all --skip-network 的 overall
输出首行 "STATUS: OK|DRIFT|FAIL"，其后 markdown 详情。任何异常（网络失败等）→ STATUS: FAIL 但脚本本身 exit 0（fail-open，由 workflow 判断）。不打印任何 token。

## 完成标准
- 在本仓库真实运行 verify-all 并附样例输出到 docs/VERIFY_ALL.md（含 JSON 片段、退出码说明、如何在 CI/本地跑）
- weekly_health.py 真实跑一次（可 --skip 网络失败容错）并把输出贴进 docs/VERIFY_ALL.md
- 注意：site/ 正在被另一个代理同时修改 — 你只读 site/，发现 FAIL 不要去改 site 文件，如实报告即可
