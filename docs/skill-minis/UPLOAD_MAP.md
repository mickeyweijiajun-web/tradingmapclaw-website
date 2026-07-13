# Skill Minis — Payhip 上传对照单

> 用途:Mickey 上传 5 个 $5 Skill Mini 到 Payhip 时,照这张表逐个对应。
> 已核对:网站 /skills/ 页 5 张卡 = 上传包 5 个 ZIP = dist/ 5 个 ZIP,三边完全一致,无多无少。
> 更新时间:2026-07-14 JST

## 一、判断哪个是哪个(口诀)

文件名 `TMC-SkillMini-` **和** `-v1.0.0.zip` 中间那段 = 商品名。
封面 `cover-<同一段>.png` = 对应封面。

---

## 二、5 个单品(每个 $5)

| # | Payhip 商品名(直接抄) | 价格 | 上传的 ZIP | 配的封面 | 网站对应卡 |
|---|---|---|---|---|---|
| 1 | Financial Research Checklist | $5 | TMC-SkillMini-financial-research-checklist-v1.0.0.zip | cover-financial-research-checklist.png | /skills/ 第1张 |
| 2 | Earnings Research Prep | $5 | TMC-SkillMini-earnings-research-prep-v1.0.0.zip | cover-earnings-research-prep.png | /skills/ 第2张 |
| 3 | Dual-Engine Verification Prompt | $5 | TMC-SkillMini-dual-engine-verification-prompt-v1.0.0.zip | cover-dual-engine-verification-prompt.png | /skills/ 第3张 |
| 4 | Evidence vs. Counter-Evidence Matrix | $5 | TMC-SkillMini-evidence-counter-evidence-matrix-v1.0.0.zip | cover-evidence-counter-evidence-matrix.png | /skills/ 第4张 |
| 5 | Market Research Journal Template | $5 | TMC-SkillMini-market-research-journal-template-v1.0.0.zip | cover-market-research-journal-template.png | /skills/ 第5张 |

## 三、可选:全集 Bundle

| Payhip 商品名 | 价格 | 上传内容 | 说明 |
|---|---|---|---|
| Skill Minis — All 5 | $25 | 5 个 ZIP 一起打包(或用 Payhip bundle 功能关联上面 5 个) | 网站定价梯已锁 $25(单个$5 / 任选三个$12 / 五个全集$25),保梯度不与 Tutorial $19 冲突 |

## 四、每个商品在 Payhip 里怎么填

- **Product name**:抄上表第二列,一字不改。
- **Price**:$5(单品)/ $25(全集)。
- **Upload file**:上表第四列那个 ZIP。
- **Cover image**:上表第五列那个 PNG。
- **Description**:用 dist/<slug>/README.md 顶部那段,或 minis_index.json 里的 title + summary。
- **License**:个人使用许可(见 ZIP 内 LICENSE.txt),非 MIT。

## 五、传完之后

把 Payhip 给你的 5 个(+1 个全集)真实链接发回给我,格式随意,例如:
```
Financial Research Checklist = https://payhip.com/b/xxxxx
Earnings Research Prep       = https://payhip.com/b/xxxxx
...
```
我会:把 /skills/ 页的 5 个 `PAYHIP_LINK` 槽位和 "Ready — checkout connecting" 按钮换成真实链接 + 改成 "Buy for $5",跑 verify-all,推送上线。

## 六、红线提醒

- Publish、接受条款、真实付款/退款 = 只有你本人操作,我不代做。
- 拿到真实 URL 前,网站按钮保持 "Ready — checkout connecting",不放假链接。
