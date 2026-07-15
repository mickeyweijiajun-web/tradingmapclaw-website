# 双引擎分工协议与内容状态机

As-of: 2026-07-13。适用范围:一切面向公众的内容(Radar 周报、Build Log、Method Note、Engine Disagreement Brief、Substack/LinkedIn/X 草稿、网站页面)。内部交易/订单/券商/执行模块不在本协议范围内,双引擎均不得触碰。

## 固定分工

### Hermes(叙事引擎)

- 读取**允许公开的报告副本**(只读旁路输出,永不读原始内部报告);
- 提取研究主题;
- 生成结构化内容;
- 生成 Radar / Build Log / Method Note 初稿;
- 生成 Substack、LinkedIn、X 草稿;
- 检查叙事与研究价值;
- **不直接修改生产站;不直接发布。**

### Codex(工程/核验引擎)

- 独立复核价格、百分比、日期、来源(对照原始数据源,不信任 Hermes 的数字);
- 检查 stale data、币种、前收盘定义;
- 检查 FACTS drift;
- 检查个人持仓泄漏;
- 检查 secrets;
- 构建 JSON、HTML、Schema、RSS、sitemap;
- 运行 unit test、link test、HTML test(`tools/tmc_ops.py verify-all`);
- 创建 branch、PR、Preview(`tools/pages_deploy.py --branch <name>`);
- 输出 rollback 说明;
- **不绕过发布门禁。**

## 七条双引擎原则

1. Hermes PASS + Codex PASS 才能进入 APPROVED-CANDIDATE;
2. 任一 BLOCK 则停止发布;
3. 两者不得互相覆盖原始报告;
4. 公共内容失败不得影响内部系统;
5. 两者必须保留独立日志(Hermes:内容日志;Codex:核验/构建日志,不得合并成一份);
6. 不得让 Hermes 同时写稿、审稿、批准自己;
7. 不得让 Codex 只做格式化而不做独立事实核验。

## 内容状态机

```
DRAFT ──Hermes 审(叙事/价值)──▶ HERMES_PASS ─┐
  │                                            ├─▶ APPROVED-CANDIDATE ──发布门禁(人工/CI)──▶ PUBLISHED ──▶ ARCHIVED
  └──Codex 审(事实/工程)──▶ CODEX_PASS ──────┘
  任一审出问题 ─▶ NEEDS_FIX(≤2 轮确定性修复)─▶ 回 DRAFT 重审
  红线命中 / 数据不可核验 ─▶ BLOCKED(终态,不发布,人工介入)
```

状态取值(历史标签,仍接受):`DRAFT` `HERMES_PASS` `CODEX_PASS` `NEEDS_FIX` `BLOCKED` `APPROVED-CANDIDATE` `PUBLISHED` `ARCHIVED`。

### 状态机标签调和(2026-07-14,P3)

自 Workspace 数据契约起,采用更细粒度的**规范标签**;历史标签等价保留、不作废:

```
DRAFT → HERMES_READY → CODEX_VERIFYING → APPROVED_CANDIDATE → PREVIEW → LIVE → ARCHIVED
            │                  │
            └─ NEEDS_FIX ◀──────┘   (≤2 轮确定性修复,超出→BLOCKED)
```

| 规范标签(新) | 历史标签(v1) |
|---|---|
| `HERMES_READY` | `HERMES_PASS` |
| `CODEX_VERIFYING` | (隐式:Codex 审查中) |
| `APPROVED_CANDIDATE` | `APPROVED-CANDIDATE` |
| `PREVIEW` | (隐式:CF Pages PR 预览) |
| `LIVE` | `PUBLISHED` |
| `ARCHIVED` | `ARCHIVED` |

发布门禁:`LIVE` 需 **Hermes=PASS 且 Codex=PASS 且 freshness=FRESH**,由 `tools/workspace_validate.py` 与 radar 发布管道确定性强制。详见 `docs/handoff/FINAL_HANDOFF_20260714.md` §4。

落地约定:

- 状态写在内容元数据里:公开 JSON 用 `"status"` 字段(如 `site/data/radar-*.json`);Mac 端草稿用 `.lintreport.json` 伴生文件(weekly_content v2 已实现 NEEDS_FIX 落盘)。
- NEEDS_FIX 的修复必须是**确定性 lint**(同输入同输出),最多 2 轮(`MAX_FIX_ITERATIONS=2`);两轮后仍不干净→ BLOCKED,人工处理,严禁无限修复循环。
- PUBLISHED 之后内容冻结(如 `/research/radar/2026-w29/` 快照);更正必须发新版本并在页面标注,不得原地篡改。

## 报告→网站 只读旁路(唯一合法通道)

```
内部报告 → allowlist(仅白名单报告可出)→ normalize(统一结构)→ redact(去持仓/去敏感)
→ fact check(检查器实际抓取双源,容差 1.5%,不一致→DATA_UNAVAILABLE)
→ Hermes content draft → deterministic candidate preflight
→ Codex/external checker re-retrieval (未实际抓取时必须标记 NOT_PERFORMED)
→ public JSON(site/data/)→ website Preview(分支部署)
→ publish gate(CI verify-all + smoke + 人工确认)→ Production(main 分支)→ archive(冻结快照 + RSS)
```

## 首个实例:2026-W29 Weekly Radar

2026-07-13 的 W29 周报按上述管道等价流程实跑一次:双源核验(Yahoo+Nasdaq / Coinbase+Kraken,9/9)→ public JSON(`radar-2026-W29.json`,status LIVE)→ Preview(162f19b2,四端点 200)→ CI 质量门+生产 smoke 全绿 → Production → 冻结归档+RSS。本协议自 W30 起正式按状态机字段记录各阶段状态。
