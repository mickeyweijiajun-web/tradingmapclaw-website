# 回滚手册 — tradingmapclaw-website

## 最快：Cloudflare Dashboard（≈1 分钟）
Workers & Pages → tradingmapclaw → Deployments → 选上一个正常的 deployment → ⋯ → Rollback to this deployment。

## Git 回滚（保持源码一致）
```bash
git checkout main && git pull
git revert <bad-commit-sha>        # 或 git revert HEAD
git push origin main               # CI 通过后 Actions 自动重新部署
```

## API 回滚（无 Dashboard 时）
```bash
# 列部署，找到上一个好的 <deployment_id>
curl -s "https://api.cloudflare.com/client/v4/accounts/984e275d2928a92b9602542421828fcb/pages/projects/tradingmapclaw/deployments" | head
# 回滚
curl -s -X POST ".../deployments/<deployment_id>/rollback"
```
（token 经安全注入，不写进任何文件。）

## Payhip 换链回滚
```bash
python3 tools/swap_payhip_links.py --rollback   # 恢复最近一次 products.html 备份
git checkout -- site/products.html              # 或用 git 恢复
```

## launchd 任务回滚（Mac）
```bash
launchctl unload ~/Library/LaunchAgents/ai.tmc.daily_brief.plist
launchctl unload ~/Library/LaunchAgents/ai.tmc.weekly_content.plist
```
然后重新启用对应 Perplexity cron 即回到迁移前状态。

## 验证回滚成功
```bash
python3 tools/tmc_ops.py verify-all --smoke
```

## Apex 域切换记录（2026-07-13）

- 变更：裸域 tradingmapclaw.com 原绑定旧 Worker `tradingmapclaw`（附带只读 AAAA 100:: 记录），已解除 Worker 域绑定，新建 CNAME → tradingmapclaw.pages.dev（proxied），并作为自定义域绑定到 Pages 项目 `tradingmapclaw`（status: active）。
- 回滚：`POST /accounts/984e275d2928a92b9602542421828fcb/workers/domains` body `{"hostname":"tradingmapclaw.com","service":"tradingmapclaw","environment":"production","zone_id":"abd048979074908bfafd80603faeb585"}`，并删除 apex CNAME 记录。旧 Worker 脚本未删除，随时可恢复。
- 生产部署回滚：Cloudflare Pages 控制台将上一个 production deployment 设为当前（或 `pages_deploy.py` 重新部署旧 commit 的 site/）。

## 2026-07-13 Payhip go-live + story entries (production 9d455784)
- Change: 5 real Payhip buy links (products.html), JSON-LD PreOrder->InStock (5 digital products), STORY.md entry points on /story + homepage.
- Previous production deployment: a495f141 (restore via Cloudflare Pages UI -> Deployments -> Rollback).
- Code rollback: `git revert f68b070 ad9b393 8089cf5` then redeploy `python3 tools/pages_deploy.py --branch main`.
- products.html auto-backup created by swap tool: site/products.html.bak-* (untracked, in workspace).
