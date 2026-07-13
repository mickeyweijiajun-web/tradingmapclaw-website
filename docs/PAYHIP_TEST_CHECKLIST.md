# Payhip 上架与换链测试清单

前提：Mickey 在 Payhip 后台上架 5 个数字商品（文件已在 payhip-upload-package.zip）并拿到 5 个 `https://payhip.com/b/XXXX` 链接。

## 换链流程（Computer 或本地执行）
```bash
# 1. 把 5 个 URL 写入 PASTE_LINKS_HERE.txt（每行 slot=url）或用参数
python3 tools/finalize_payhip.py --links-file PASTE_LINKS_HERE.txt --dry-run   # 先看 diff
python3 tools/finalize_payhip.py --links-file PASTE_LINKS_HERE.txt            # 真实换链
```
工具自动做：HTTPS+payhip.com 域名校验、5 URL 不重复、可达性检查、备份、diff、HTML 完整性检查、JSON-LD PreOrder→InStock、git commit、Preview 部署、smoke test。Production 部署前需 Mickey 批准。

## Mickey 手动购买测试（换链上线后）
- [ ] 用真实邮箱走一遍 Tutorial 01 购买（可用 100% off 优惠码测试，不产生真实付款）
- [ ] 确认自动发货邮件送达、文件可下载、内容正确
- [ ] 确认 Payhip 后台订单记录正常、PayPal 结算路径正常
- [ ] 确认退款政策页与 Payhip 后台设置一致
- [ ] Bundle 与 Patterns Bundle 各测一单
- [ ] 测试完成前网站 Customer-ready 状态 = PARTIAL

红线：Computer 不执行真实付款；不代替 Mickey 完成 KYC/条款确认/上架操作。
