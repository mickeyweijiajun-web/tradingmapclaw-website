# VERIFY_ALL — tmc_ops.py 质量门使用文档

本工具实现 [docs/SPEC_TMC_OPS.md](./SPEC_TMC_OPS.md) 定义的质量门。事实基准见 [FACTS.md](../FACTS.md)。

包含两个脚本：

- `tools/tmc_ops.py` — `verify-all` 子命令，对 `site/` 与 `tools/` 做 28 项检查（25 项本地 + 3 项可选网络），人类可读报告 + 可选 `--json` 机器可读报告，退出码反映结果。
- `tools/weekly_health.py` — 每周仓库/站点健康检查，fail-open（任何异常都不会让脚本本身非零退出），输出 `STATUS: OK|DRIFT|FAIL` 首行 + markdown 详情。

两者均为 **stdlib only**，兼容 **Python 3.9+**，对 `site/` **只读**（`tools/tmc_ops.py` 和 `tools/weekly_health.py` 从不写入 `site/` 下任何文件）。

---

## 1. tools/tmc_ops.py verify-all

### 1.1 用法

```bash
python3 tools/tmc_ops.py verify-all [--json PATH] [--site-dir site] \
    [--base-url https://www.tradingmapclaw.com] [--skip-network] [--smoke]
```

参数：

| 参数 | 默认值 | 说明 |
|---|---|---|
| `--json PATH` | 无 | 额外写一份机器可读 JSON 报告到指定路径 |
| `--site-dir` | `site` | 站点目录（相对当前工作目录，或绝对路径） |
| `--base-url` | `https://www.tradingmapclaw.com` | 校验 canonical / sitemap / 网络检查所用的权威域名 |
| `--skip-network` | 关闭 | 强制跳过第 26–28 项网络检查（优先于 `--smoke`） |
| `--smoke` | 关闭 | 开启第 26–28 项网络检查（需要出网） |

退出码：

- **0** — 无 FAIL（可以有 WARN / SKIP）
- **1** — 至少一项 FAIL，或写 JSON 报告本身失败

从仓库根目录运行（CI 与本文档均以此为准）：

```bash
cd /home/user/workspace/repo/tradingmapclaw-website
python3 tools/tmc_ops.py verify-all --json verify-report.json
echo "exit code: $?"
```

### 1.2 检查项清单（28 项）

本地检查（默认执行，无需出网）：

| # | id | 内容 |
|---|---|---|
| 1 | `01_py_compile` | `py_compile` 编译 `tools/*.py` 全部通过 |
| 2 | `02_json_data_files` | `site/data/*.json` 全部可解析；`radar-latest.json` 含 `period,data_as_of,is_sample,rows` |
| 3 | `03_secrets_scan` | `site/` 与 `tools/` 无 `sk-` / `ghp_` / `github_pat_` / `AKIA` / `Bearer <30+ 字符>` / PEM 私钥块 |
| 4 | `04_facts_drift` | 站点 HTML 无禁用旧数字（119/115 jobs、500+/502+ scripts、93+ skills、three-engine/三引擎、GPT-5.5） |
| 5 | `05_price_drift` | 无 `$149`/`$99`；`$19/$49/$79/$200/$399/$699` 全站至少各出现一次 |
| 6 | `06_model_roster` | council 相关页面不得出现允许清单外的模型名（允许：DeepSeek V4 Pro / GLM-5.2 / GPT-5.6 / Qwen3 14B） |
| 7 | `07_internal_links` | 所有相对 `href`/`src` 指向的文件必须存在（识别 Cloudflare Pages 干净 URL：`/x` → `x.html` 或 `x/index.html`） |
| 8 | `08_html_structure` | `div/section/table/script` 标签配平；有 `<title>`、meta description、viewport |
| 9 | `09_canonical` | 每页 `rel=canonical` 存在且以 `https://www.tradingmapclaw.com/` 开头 |
| 10 | `10_sitemap` | `sitemap.xml` 覆盖现有 html 页（404/thank-you 豁免），URL 均为 www 域 |
| 11 | `11_og_tags` | index/products/radar/story/faq 含 `og:title` / `og:description` |
| 12 | `12_payhip_links` | payhip.com 链接必须 https 且为 `/TradingMapClaw` 或 `/b/` 格式；`PAYHIP_LINK:` 占位存在 → WARN 并检查 `availability=PreOrder` |
| 13 | `13_waitlist_no_checkout` | Skills Library 区块附近无 payhip `/b/` 结账链接 |
| 14 | `14_sample_tag` | `radar-latest.json.is_sample=true` 时 `radar.html`/`index.html` 必须渲染 `SAMPLE` |
| 15 | `15_stale_dates` | HTML 中 `20xx-xx-xx` 日期，剔除 `<!--TMC:...-->` 注入标记区间后，早于今天 30 天以上 → WARN |
| 16 | `16_position_leak` | 无 `my position` / 我的持仓 / 账户余额 / 持仓金额 |
| 17 | `17_imperative_trade_language` | 无 `you should buy` / `sell now` / `act now` / `buy before`（教育语境豁免） |
| 18 | `18_guaranteed_returns` | 无 `guaranteed return` / `can't lose` / `beat the market` / 稳赚 |
| 19 | `19_accessibility_basics` | `<img>` 有 `alt`；表单 `<input>` 有 `<label for>` 或 `aria-label`/`aria-labelledby` |
| 20 | `20_mobile_basics` | 每页有 viewport meta；`site.css` 含 `@media` |
| 21 | `21_build_site_data_idempotent` | `python3 tools/build_site_data.py --check` 退出码为 0（幂等） |
| 22 | `22_llms_txt` | `llms.txt`/`llms-full.txt` 存在且含 `v2.0` 与 `118` |
| 23 | `23_robots_txt` | `robots.txt` 存在且引用 `sitemap.xml` |
| 24 | `24_404_page` | `site/404.html` 存在 |
| 25 | `25_site_config` | `site/data/site-config.json` 的 `cta_variant ∈ {A,B}`，`analytics_enabled` 为布尔值 |

网络检查（默认 SKIP，`--smoke` 开启，`--skip-network` 强制跳过）：

| # | id | 内容 |
|---|---|---|
| 26 | `26_smoke_pages_200` | `GET base-url` 的 `/`, `/products.html`, `/radar.html`, `/story.html`, `/faq.html` 均返回 200 |
| 27 | `27_smoke_homepage_content` | 线上首页含 `Dual-Engine` 且不含禁用旧数字 |
| 28 | `28_smoke_canonical_domain` | 线上首页 canonical 域与 `--base-url` 一致 |

### 1.3 缺失文件的处理方式（重要）

`site/data/radar-latest.json`、`site/data/site-config.json`、`tools/build_site_data.py` 在本任务执行期间由另一个代理并行创建。所有依赖它们的检查项在文件缺失时明确降级为 **WARN**（提示"pending from another agent"）而不是崩溃或误报 FAIL：

- `02_json_data_files`：`site/data/` 目录或 `radar-latest.json` 不存在 → WARN
- `14_sample_tag`：`radar-latest.json` 不存在 → WARN（无法验证 SAMPLE 传播）
- `21_build_site_data_idempotent`：`build_site_data.py` 不存在 → WARN
- `25_site_config`：`site-config.json` 不存在 → WARN

同理，`site-dir` 整体不存在、JSON 格式错误、文件不可读（编码错误等）也全部被捕获为 FAIL/WARN 并附带原因，从不抛出未处理异常（每个检查函数都被 `Runner.run` 包裹，任何意外异常会被转换为该检查项的 FAIL，不影响其余检查继续执行）。

### 1.4 JSON 输出结构

```json
{
  "as_of": "2026-07-13T06:18:41Z",
  "base_url": "https://www.tradingmapclaw.com",
  "site_dir": "site",
  "checks": [
    {"id": "01_py_compile", "status": "PASS", "detail": "..."},
    ...
  ],
  "summary": {"pass": 21, "fail": 2, "warn": 2, "skip": 3},
  "overall": "FAIL"
}
```

（`summary` 额外含 `skip` 字段，便于统计网络检查跳过情况；spec 要求的 `pass/fail/warn` 三键均保留。）

### 1.5 本仓库真实运行样例（人类可读，`--skip-network` 隐含，默认模式）

以下为在本仓库 `/home/user/workspace/repo/tradingmapclaw-website` 内真实执行 `python3 tools/tmc_ops.py verify-all --json verify-report.json` 得到的样例输出（`site/` 由另一代理并行修改，属于该时间点的真实快照）：

```
==============================================================================
TMC verify-all report — as_of 2026-07-13T06:18:41Z
base-url: https://www.tradingmapclaw.com   site-dir: site
==============================================================================
[PASS] 01_py_compile                    py_compile OK for 6 file(s)
[PASS] 02_json_data_files               2 JSON file(s) parsed OK; radar-latest.json has required keys
[PASS] 03_secrets_scan                  no secret-like patterns (sk-/ghp_/github_pat_/AKIA/Bearer .../private key) found in site/ or tools/
[PASS] 04_facts_drift                   no banned legacy numbers/phrases found across 15 HTML file(s)
[PASS] 05_price_drift                   no banned legacy prices; all required current prices ($19, $49, $79, $200, $399, $699) present
[PASS] 06_model_roster                  no disallowed council model names found; allowed roster = DeepSeek V4 Pro, GLM-5.2, GPT-5.6, Qwen3 14B
[FAIL] 07_internal_links                26 broken internal link(s) of 313 checked: index.html: -> /research (resolved: research); index.html: -> /system (resolved: system); index.html: -> /build-log (resolved: build-log); ... (truncated to first 15 in tool output)
[PASS] 08_html_structure                15 HTML file(s) balanced with title/meta-description/viewport
[FAIL] 09_canonical                     7 of 15 page(s) missing/incorrect canonical: 404.html: no rel=canonical; legal/contact.html: no rel=canonical; legal/delivery.html: no rel=canonical; legal/disclaimer.html: no rel=canonical; legal/privacy.html: no rel=canonical; legal/refund.html: no rel=canonical; legal/terms.html: no rel=canonical
[WARN] 10_sitemap                       5 page(s) not referenced in sitemap.xml (may be new pages pending): get-access.html, index.html, legal/contact.html, legal/delivery.html, legal/refund.html
[PASS] 11_og_tags                       all primary pages (index.html, products.html, radar.html, story.html, faq.html) have og:title and og:description
[WARN] 12_payhip_links                  PAYHIP_LINK: placeholder(s) still present (checkout not swapped) on: products.html
[PASS] 13_waitlist_no_checkout          Skills Library section(s) found with no payhip /b/ checkout link nearby
[PASS] 14_sample_tag                    is_sample=true and both radar.html and index.html render 'SAMPLE'
[PASS] 15_stale_dates                   no stale (>30 day old) dates found outside TMC injection markers
[PASS] 16_position_leak                 no position/account-balance leak patterns found
[PASS] 17_imperative_trade_language     no imperative trading-instruction language found (education-context exemptions applied)
[PASS] 18_guaranteed_returns            no guaranteed-return / can't-lose / beat-the-market language found
[PASS] 19_accessibility_basics          all 25 <img> have alt; all form inputs have label or aria-label
[PASS] 20_mobile_basics                 all pages have viewport meta; site.css contains @media rules
[PASS] 21_build_site_data_idempotent    build_site_data.py --check exited 0 (idempotent / up to date)
[PASS] 22_llms_txt                      llms.txt and llms-full.txt exist and contain 'v2.0' and '118'
[PASS] 23_robots_txt                    robots.txt exists and references sitemap.xml
[PASS] 24_404_page                      site/404.html exists and is readable
[PASS] 25_site_config                   site-config.json valid: cta_variant='A', analytics_enabled=False
[SKIP] 26_smoke_pages_200               network checks skipped (pass --smoke to enable)
[SKIP] 27_smoke_homepage_content        network checks skipped (pass --smoke to enable)
[SKIP] 28_smoke_canonical_domain        network checks skipped (pass --smoke to enable)
------------------------------------------------------------------------------
Summary: 21 PASS, 2 FAIL, 2 WARN, 3 SKIP  ->  OVERALL: FAIL
==============================================================================
```

```
$ echo $?
1
```

**这两项 FAIL 是站点内容的真实问题，不是工具的 bug**（工具对 `site/` 只读，如实报告）：

- `07_internal_links`：首页已经链接到 `/research`、`/system`、`/build-log`、`/consulting` 等页面，但这些页面截至运行时尚未创建（属于另一代理按 [SPEC_SITE_PHASE2.md](./SPEC_SITE_PHASE2.md) 正在构建的新页面）。
- `09_canonical`：`404.html` 与 6 个 `legal/*.html` 页面目前没有 `rel=canonical` 标签。

两项 WARN 同理为真实、非阻断性的观察（`sitemap.xml` 暂缺 5 个新/近期页面；`products.html` 中 `PAYHIP_LINK:` 占位尚未替换为真实 Payhip 结账链接，属预期中的预售阶段）。

### 1.6 对应的 JSON 报告片段（同一次运行）

```json
{
  "as_of": "2026-07-13T06:18:41Z",
  "base_url": "https://www.tradingmapclaw.com",
  "site_dir": "site",
  "checks": [
    {"id": "01_py_compile", "status": "PASS", "detail": "py_compile OK for 6 file(s)"},
    {"id": "07_internal_links", "status": "FAIL", "detail": "26 broken internal link(s) of 313 checked: index.html: -> /research (resolved: research); ..."},
    {"id": "09_canonical", "status": "FAIL", "detail": "7 of 15 page(s) missing/incorrect canonical: 404.html: no rel=canonical; ..."},
    {"id": "10_sitemap", "status": "WARN", "detail": "5 page(s) not referenced in sitemap.xml (may be new pages pending): get-access.html, index.html, legal/contact.html, legal/delivery.html, legal/refund.html"},
    {"id": "12_payhip_links", "status": "WARN", "detail": "PAYHIP_LINK: placeholder(s) still present (checkout not swapped) on: products.html"},
    {"id": "21_build_site_data_idempotent", "status": "PASS", "detail": "build_site_data.py --check exited 0 (idempotent / up to date)"},
    {"id": "26_smoke_pages_200", "status": "SKIP", "detail": "network checks skipped (pass --smoke to enable)"}
  ],
  "summary": {"pass": 21, "fail": 2, "warn": 2, "skip": 3},
  "overall": "FAIL"
}
```

（完整 28 项见运行时 `--json` 输出文件；此处为节选，用于展示结构。）

### 1.7 网络检查样例（`--smoke`）

在同一仓库对线上站点执行 `python3 tools/tmc_ops.py verify-all --smoke`（截至撰写本文档时，`www.tradingmapclaw.com` 可访问）：

```
[PASS] 26_smoke_pages_200               all 5 primary page(s) returned HTTP 200
[PASS] 27_smoke_homepage_content        live homepage contains 'Dual-Engine' and no banned legacy numbers
[PASS] 28_smoke_canonical_domain        live canonical 'https://www.tradingmapclaw.com/' matches base-url domain
```

整体 `overall` 仍为 `FAIL`（因为本地检查 07/09 仍是 FAIL），退出码为 1 —— 网络检查的 PASS 不会掩盖本地问题。

### 1.8 在 CI / 本地怎么跑

CI（`.github/workflows/ci.yml`、`.github/workflows/deploy.yml`）已经这样调用：

```yaml
- name: verify-all quality gate
  run: python tools/tmc_ops.py verify-all --json verify-report.json
```

CI 默认不加 `--smoke`（不做网络检查），只在部署后的 smoke-test 步骤里单独用 `curl` 验证线上 — 这与本工具的默认行为（网络检查 SKIP）一致。

本地开发者常用姿势：

```bash
# 快速本地检查（不出网，最常用）
python3 tools/tmc_ops.py verify-all

# 连同线上验证一起跑（发布后核实）
python3 tools/tmc_ops.py verify-all --smoke

# 只想要机器可读结果（例如喂给另一个脚本）
python3 tools/tmc_ops.py verify-all --json /tmp/report.json --skip-network
python3 -c "import json; d=json.load(open('/tmp/report.json')); print(d['overall'])"
```

---

## 2. tools/weekly_health.py

### 2.1 用法

```bash
python3 tools/weekly_health.py [--out health-report.md]
```

检查内容：

1. GitHub 仓库健康度 — `mickeyweijiajun-web/tradingmapclaw-website` 与 `mickeyweijiajun-web/TradingMapClaw` 的 open issues 数、open PR 数、最新 commit 距今天数。若环境变量 `GH_TOKEN`（或 `GITHUB_TOKEN`）存在则用于认证请求；否则走匿名 GitHub REST API（受匿名限流约束）。
2. `https://www.tradingmapclaw.com` 主要页面（`/`, `/products.html`, `/radar.html`, `/story.html`, `/faq.html`）的 HTTP 状态。
3. 以子进程方式运行 `python3 tools/tmc_ops.py verify-all --skip-network`，读取其 JSON 结果的 `overall`/`summary`。

输出报告首行固定为：

```
STATUS: OK
```
或
```
STATUS: DRIFT
```
或
```
STATUS: FAIL
```

判定规则：

- 任一环节抛错/网络失败/限流 → 至少 `DRIFT`（细节写入报告，但不阻断脚本本身）。
- `verify-all --skip-network` 的 `overall == "FAIL"` → 整体 `STATUS: FAIL`。
- 全部正常且无异常 → `STATUS: OK`。

**Fail-open 契约**：无论 STATUS 是什么，`weekly_health.py` 进程本身的退出码始终为 **0**（除非命令行参数解析本身出错）。是否因为 STATUS 而采取行动（例如开 GitHub issue），由调用它的 workflow（`.github/workflows/weekly-health.yml`）决定，而不是由这个脚本的退出码决定。这样网络抖动、GitHub 限流、站点临时故障都不会打断每周定时任务本身。脚本任何时候都不会打印 `GH_TOKEN`/`GITHUB_TOKEN` 的值——即便请求返回的错误信息里恰好包含 token，也会被替换为 `***REDACTED***` 后再写入报告/打印。

### 2.2 本仓库真实运行样例

在本仓库执行 `python3 tools/weekly_health.py --out health-report.md`：

```
$ python3 tools/weekly_health.py --out /tmp/health-report.md
STATUS: FAIL
$ echo $?
0
```

生成的 `health-report.md`（真实运行结果，未编辑）：

```markdown
STATUS: FAIL

# TMC Weekly Health Report

_Generated 2026-07-13T06:17:41Z by tools/weekly_health.py_

## GitHub repo health

- **mickeyweijiajun-web/tradingmapclaw-website**: ERROR — HTTP 403 from https://api.github.com/repos/mickeyweijiajun-web/tradingmapclaw-website: {"message":"API rate limit exceeded for 23.22.183.111. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)","documentation_url":"h
- **mickeyweijiajun-web/TradingMapClaw**: ERROR — HTTP 403 from https://api.github.com/repos/mickeyweijiajun-web/TradingMapClaw: {"message":"API rate limit exceeded for 23.22.183.111. (But here's the good news: Authenticated requests get a higher rate limit. Check out the documentation for more details.)","documentation_url":"h

## Site page status (https://www.tradingmapclaw.com)

- `/`: HTTP 200
- `/products.html`: HTTP 200
- `/radar.html`: HTTP 200
- `/story.html`: HTTP 200
- `/faq.html`: HTTP 200

## Local quality gate (verify-all --skip-network)

- overall: **FAIL**
- summary: 19 PASS, 3 FAIL, 3 WARN, 3 SKIP
```

这次真实运行验证了三条关键路径都按设计工作：

1. **GitHub API 匿名限流触发 403** — 沙盒共享出网 IP 被限流，脚本没有崩溃，把错误消息（已确认不含 token）计入报告，并把整体状态推高到 `FAIL`；`weekly_health.py` 进程本身仍以退出码 `0` 结束（fail-open）。
2. **站点页面探测成功** — 5 个主要页面全部 HTTP 200。
3. **本地质量门联动** — 子进程调用 `verify-all --skip-network` 拿到当时的真实结果（19 PASS / 3 FAIL / 3 WARN / 3 SKIP，即本文档 §1.5 之前一次快照；`site/` 持续变化，数字会随之波动），并把 `overall: FAIL` 正确地传导为整体 `STATUS: FAIL`。

（另外验证过一次故意提供无效 `GH_TOKEN` 的场景：GitHub API 返回 `401 Bad credentials`，脚本同样正常捕获、写入报告、不打印 token、进程退出码 0 —— 证明认证失败路径与匿名限流路径一样具备 fail-open 保证。）

### 2.3 在 CI 里怎么跑

`.github/workflows/weekly-health.yml` 已经这样调用（GITHUB_TOKEN 由 Actions 自动注入，权限仅 `contents: read`, `issues: write`）：

```yaml
- name: Run health checks
  run: python tools/weekly_health.py --out health-report.md || echo "failed=true" >> "$GITHUB_OUTPUT"
- name: Open issue on failure or drift
  run: |
    if grep -qE "^STATUS: (FAIL|DRIFT)" health-report.md; then
      gh issue create --title "..." --body-file health-report.md --label health
    fi
```

因为 `weekly_health.py` 保证进程退出码为 0，`|| echo "failed=true"` 分支实际上不会被触发；真正的判定逻辑在下一步用 `grep` 检查报告首行的 `STATUS:`。这正是本工具 fail-open 设计的目的：让"检测到问题"和"这次运行本身失败"是两件独立的事。

---

## 3. 已知限制 / 设计取舍

- `06_model_roster`、`16_position_leak`、`17_imperative_trade_language`、`18_guaranteed_returns` 均为基于正则/关键词的文本扫描，不是语义理解；已针对已知假阳性（如 "No guaranteed results" 中的否定语境、`GPT-5.6` 中的 `GPT-5` 子串）做了排除处理，但无法保证覆盖所有未来措辞变化。
- `03_secrets_scan` 的通用 30+ 字符字母数字模式默认不启用（`generic-30char-secret`），因为它对字体 URL、哈希、base64 资源等会产生大量噪音；当前只用具名前缀（`sk-`/`ghp_`/`github_pat_`/`AKIA`/`Bearer ...`/PEM 私钥块）作为判定依据，与 SPEC 列出的模式一致。
- `07_internal_links`、`10_sitemap` 已适配本站的 Cloudflare Pages "干净 URL"约定（`/story` ↔ `story.html`，`/research` ↔ `research/index.html`），但如果未来站点引入新的 URL 重写规则，需要同步更新解析逻辑。
- 网络检查（26–28）依赖沙盒/CI 环境可以出网访问 `www.tradingmapclaw.com`；`weekly_health.py` 的 GitHub 检查同理依赖出网访问 `api.github.com`，两者都已验证在出网受限或限流时优雅降级，不会导致工具本身崩溃或产生误导性的 PASS。
