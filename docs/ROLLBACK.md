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
