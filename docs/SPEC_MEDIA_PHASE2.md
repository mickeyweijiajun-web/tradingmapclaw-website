# SPEC — 媒体矩阵漂移修复 + 四周排期 + 合作政策（子代理 B 执行）

事实基准：/home/user/workspace/repo/tradingmapclaw-website/FACTS.md（先读）
输入（只读）：/home/user/workspace/tmc/handoff-bundle/marketing/launch-kit-20260712/（x-twitter/linkedin/reddit/hackernews/github/youtube/producthunt/emails/INDEX.md）
输出目录（只写这里）：/home/user/workspace/repo/tradingmapclaw-website/content/ 以及根目录三个政策文件。

## 1. Drift Scan（先扫描，输出报告，再修复）
扫描 launch kit 全部文件，找漂移信号：
- 旧引擎口径：three-engine/三引擎、119/115 jobs、502+/500+ scripts、93+/50+ 技能误写、GPT-5.5
- 旧价格：$149、$99、$29 单课
- 虚构客户 / 虚构收益 / testimonial、guaranteed/稳赚、"real-time" 数据声明
- buy/sell 指令语言、"high conviction"
- 未上线却写 Buy now（Payhip 尚未上架 → 只能写 waitlist/preorder/coming soon）
报告写 content/DRIFT_SCAN_REPORT.md：每处漂移 = 文件、行、原文、问题类型、修复。

## 2. 修复
把整个 launch kit 复制到 content/launch-kit/（保持子目录结构），只修复漂移处，不重写风格与结构。每个文件头部加一行 HTML 注释或 markdown 注释：<!-- status: DRAFT — requires Mickey approval before publishing -->（已有则不重复）。

## 3. 母内容模板 + 一源多用流程
- content/MOTHER_CONTENT_TEMPLATE.md：每周母内容 "Weekly Market Intelligence Brief" 模板（结构：本周主题/关键观察×3（带 as-of 与来源占位）/引擎分歧一例/方法论一角/下周关注；合规红线按 FACTS §5）。
- content/REPURPOSE_FLOW.md：母内容 → 9 种衍生（X thread、X 单条、LinkedIn 长文、Reddit 帖、HN Show、YouTube 脚本大纲、Newsletter、Substack 长文、GitHub build-log 条目）的转换规则表（每渠道：长度/语气/CTA/禁忌），及人工发布 SOP（自动点击 Publish：禁止）。

## 4. 四周排期（只排期，不发布）
content/FOUR_WEEK_SCHEDULE.csv 列：week,date,channel,content_type,title/summary,source(母内容或launch-kit文件路径),status,notes
- 4 周 × 每周约 5-7 条（周一母内容 → 周中衍生），渠道覆盖 X/LinkedIn/Reddit/HN/Newsletter/Substack/GitHub
- status ∈ READY / NEEDS FACT CHECK / NEEDS MICKEY APPROVAL / BLOCKED / OUTDATED（基于你修复后的真实状态判断；凡引用未来市场数据的 = NEEDS FACT CHECK；凡对外发布的 = 至少 NEEDS MICKEY APPROVAL）
- 日期从 2026-07-20（下周一）起

## 5. 合作政策（写到仓库根目录）
- PARTNERSHIP_POLICY.md：接受/不接受的合作类型（接受：教育内容合作、开源协作、affiliate 披露清晰的推荐；不接受：展示广告（本轮）、代言收益承诺类产品、未披露 sponsorship、要求分享用户数据）；评估标准（受众匹配、合规风险、工作量、报价底线）；决策流程（候选→评估→Mickey 决定）。
- SPONSORSHIP_DISCLOSURE.md：披露模板（英文为主+中文对照）：sponsored 内容必须显著标注、观点独立声明、与 WATCHLIST_ONLY 不冲突。
- PARTNER_PROSPECTS.csv 列：name,type,channel,audience_size_estimate,fit_reason,risk,priority(H/M/L),status(CANDIDATE),source_url — 从公开网络调研 10-15 个候选（AI 工程/量化研究/个人金融教育类 newsletter、YouTube 频道、播客、社区；受众与 "solo builder + AI research system" 匹配）。只做候选与评估，不发送任何商业邮件。

## 完成标准
- DRIFT_SCAN_REPORT.md 有逐条真实扫描结果（不得空泛）
- launch-kit 修复后 grep 无禁用旧数字/旧价格
- CSV 可被 python csv 模块解析
