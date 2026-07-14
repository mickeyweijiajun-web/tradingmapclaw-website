#!/usr/bin/env python3
"""workspace_build.py — build the TMC Workspace pages from the JSON data contract.

Deterministic, idempotent. Reuses the site's shared head/nav/footer, /assets/site.css,
navigation, footer + disclaimer. Renders ONLY status=LIVE payloads; UNAVAILABLE assets
render an explicit 'Coming soon' state (no fabricated data). Adds canonical + SEO meta.
Does NOT touch index/products/skills/radar/rss/payhip.

Usage: python3 tools/workspace_build.py [--check]
  --check : exit 3 if any page would change (no write), 0 if up to date.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
WS_DATA = SITE / "data" / "workspace"
BASE = "https://www.tradingmapclaw.com"

NAV = '''<nav class="nav" id="nav">
  <div class="nav-inner">
    <a class="nav-logo" href="/" aria-label="TradingMapClaw home">
      <img class="mark" src="/assets/logo-icon.jpg" alt="TradingMapClaw logo" width="30" height="30" />
      <span>TradingMap<span class="accent">Claw</span></span>
    </a>
    <div class="nav-links" id="navLinks">
      <a href="/story">Story</a>
      <a href="/research">Research</a>
      <a href="/workspace">Workspace</a>
      <a href="/system">System</a>
      <a href="/products">Products</a>
      <a href="/skills/">Skills</a>
      <a href="/faq">FAQ</a>
    </div>
    <div class="nav-right">
      <a class="btn btn-primary" href="/products">Get Access</a>
      <button class="nav-toggle" id="navToggle" aria-label="Toggle navigation" aria-expanded="false">&#9776;</button>
    </div>
  </div>
</nav>'''

FOOTER = '''<footer class="footer">
  <div class="footer-inner">
    <p class="disclaimer"><b>Compliance:</b> TradingMapClaw is an independent financial-market research, information-aggregation and research-engineering platform operating in <b>WATCHLIST_ONLY</b> mode. It provides market research, educational materials, research software, and workflow-engineering services. It does not execute trades, hold customer funds, operate brokerage accounts, or provide individualized investment recommendations. All output and all products sold here are for research and educational purposes and are <b>not investment advice</b>. Markets carry risk; do your own diligence.</p>
    <div class="footer-bottom">
      <span>&copy; 2026 TradingMapClaw &middot; Research &amp; education only &middot; Not investment advice</span>
      <span>Workspace &middot; WATCHLIST_ONLY</span>
    </div>
  </div>
</footer>
<script>
  const nav = document.getElementById('nav');
  const onScroll = () => { nav.classList.toggle('scrolled', window.scrollY > 12); };
  window.addEventListener('scroll', onScroll, {passive:true}); onScroll();
  const tgl = document.getElementById('navToggle'), links = document.getElementById('navLinks');
  if (tgl && links) tgl.addEventListener('click', () => {
    const open = links.classList.toggle('open');
    tgl.setAttribute('aria-expanded', open ? 'true' : 'false');
  });
</script>
<script src="/assets/js/tmc-events.js"></script>'''


def head(title, desc, canonical):
    return f'''<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
<meta name="description" content="{desc}" />
<meta name="author" content="TradingMapClaw" />
<meta name="robots" content="index, follow, max-image-preview:large" />
<meta name="theme-color" content="#01696f" />
<link rel="canonical" href="{canonical}" />
<link rel="sitemap" type="application/xml" href="/sitemap.xml" />
<meta property="og:site_name" content="TradingMapClaw" />
<meta property="og:title" content="{title}" />
<meta property="og:description" content="{desc}" />
<meta property="og:type" content="website" />
<meta property="og:url" content="{canonical}" />
<meta property="og:image" content="{BASE}/assets/logo-slogan.jpg" />
<meta name="twitter:card" content="summary_large_image" />
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23155e63'/%3E%3Cpath d='M8 24 L11 12 L16 19 L21 12 L24 24' stroke='white' stroke-width='2.6' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3Ccircle cx='24' cy='9' r='3' fill='%23e8873a'/%3E%3C/svg%3E" />
<link rel="stylesheet" href="/assets/site.css" />
</head>
<body>
{NAV}
<main>'''


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def hero(label, h1, sub):
    return (f'<header class="page-hero"><div class="ph-inner">'
            f'<p class="section-label">{esc(label)}</p><h1>{esc(h1)}</h1>'
            f'<p class="ph-sub">{esc(sub)}</p>'
            f'<p class="ph-compliance">Research &amp; education only. Not investment advice. &middot; WATCHLIST_ONLY</p>'
            f'</div></header>')


def load(cid):
    return json.loads((WS_DATA / f"{cid}.json").read_text(encoding="utf-8"))


def render_asset_page(cid) -> str:
    d = load(cid)
    pl = d["payload"]
    t = pl["ticker"]
    canonical = f"{BASE}/workspace/assets/{cid}"
    title = f"{t} &mdash; Workspace research card | TradingMapClaw"
    desc = f"Research-only workspace card for {esc(pl['name'])} ({t}). Dual-engine verified, WATCHLIST_ONLY. Not investment advice."
    body = [head(title, desc, canonical), hero("Workspace · Asset", f"{t} — {pl['name']}", pl["sector"])]
    if d["status"] == "LIVE":
        body.append('<section class="section"><div class="wrap">')
        body.append(f'<p class="status-pill">STATUS: {d["status"]} &middot; freshness {d["freshness"]["state"]} &middot; as of {d["data_as_of"]}</p>')
        body.append(f'<p>{esc(pl["narrative"])}</p>')
        if pl.get("catalysts"):
            body.append("<h2>Catalysts on the research calendar</h2><ul>")
            body += [f"<li>{esc(c)}</li>" for c in pl["catalysts"]]
            body.append("</ul>")
        if pl.get("observations"):
            body.append('<h2>Observations</h2><table class="table"><thead><tr><th>Metric</th><th>Value</th><th>Verified by</th></tr></thead><tbody>')
            for o in pl["observations"]:
                body.append(f'<tr><td>{esc(o["label"])}</td><td>{esc(o["value"])}</td><td class="mono">{esc(o.get("verified_by",""))}</td></tr>')
            body.append("</tbody></table>")
        v = d["verification"]
        body.append(f'<p class="mono">Dual-engine: Hermes {v["hermes"]["result"]} &middot; Codex {v["codex"]["result"]}</p>')
        if d.get("sources"):
            body.append("<h2>Sources</h2><ul>")
            body += [f'<li><a href="{s["url"]}" target="_blank" rel="noopener">{esc(s["name"])}</a></li>' for s in d["sources"]]
            body.append("</ul>")
        body.append("</div></section>")
    else:
        body.append('<section class="section"><div class="wrap">')
        body.append(f'<p class="status-pill">STATUS: {d["status"]}</p>')
        body.append(f'<p>{esc(pl["narrative"])}</p>')
        body.append('<p><a href="/workspace">&larr; Back to Workspace</a></p>')
        body.append("</div></section>")
    body.append("</main>")
    body.append(FOOTER)
    body.append("</body></html>")
    return "\n".join(body)


def render_index() -> str:
    st = json.loads((WS_DATA / "status.json").read_text(encoding="utf-8"))
    canonical = f"{BASE}/workspace"
    title = "Workspace &mdash; live research surface | TradingMapClaw"
    desc = "The TMC Workspace: a research-only surface for watchlist assets, radar, catalysts and methodology. Dual-engine verified, WATCHLIST_ONLY. Not investment advice."
    body = [head(title, desc, canonical),
            hero("Workspace", "One surface. Every research thread.",
                 "A read-only window into what the dual-engine system produces — assets, radar, catalysts, methodology. Nothing here is a trade instruction.")]
    body.append('<section class="section"><div class="wrap">')
    body.append('<h2>Watchlist assets</h2><div class="card-grid-3">')
    for a in st["assets"]:
        cid = a["content_id"].replace("ws-asset-", "")
        live = a["status"] == "LIVE"
        badge = ('<span class="pstatus free">LIVE &middot; FRESH</span>' if live
                 else '<span class="pstatus lab">Coming soon</span>')
        body.append(f'<div class="note-card">{badge}<h3>{a["ticker"]}</h3>'
                    f'<p class="w-more"><a href="/workspace/assets/{cid}">Open card &rarr;</a></p></div>')
    body.append("</div>")
    body.append('<h2>Sections</h2><div class="card-grid-3">')
    for label, href, note in [
        ("Radar", "/workspace/radar", "Weekly market radar feed"),
        ("Research", "/workspace/research", "Deep research notes"),
        ("Catalysts", "/workspace/catalysts", "Upcoming research calendar"),
        ("Methodology", "/workspace/methodology", "How the dual-engine pipeline works"),
        ("Status", "/workspace/status", "System + engine ownership")]:
        body.append(f'<div class="note-card"><h3>{label}</h3><p>{note}</p>'
                    f'<p class="w-more"><a href="{href}">Open &rarr;</a></p></div>')
    body.append("</div></div></section>")
    body.append("</main>")
    body.append(FOOTER)
    body.append("</body></html>")
    return "\n".join(body)


def render_stub(slug, label, h1, sub, extra="") -> str:
    canonical = f"{BASE}/workspace/{slug}"
    title = f"{label} &mdash; Workspace | TradingMapClaw"
    desc = f"{sub} WATCHLIST_ONLY. Not investment advice."
    body = [head(title, desc, canonical), hero(f"Workspace · {label}", h1, sub)]
    body.append('<section class="section"><div class="wrap">')
    body.append(extra or '<p class="status-pill">Coming soon</p><p>This workspace section is reserved and will publish once its data contract goes LIVE. Until then it shows nothing rather than fabricating content.</p>')
    body.append('<p><a href="/workspace">&larr; Back to Workspace</a></p>')
    body.append("</div></section></main>")
    body.append(FOOTER)
    body.append("</body></html>")
    return "\n".join(body)


def render_status_page() -> str:
    st = json.loads((WS_DATA / "status.json").read_text(encoding="utf-8"))
    rows = "".join(f'<tr><td>{k}</td><td class="mono">{v}</td></tr>' for k, v in st["engines"].items())
    extra = (f'<p class="status-pill">STATUS: {st["status"]} &middot; as of {st["data_as_of"]}</p>'
             f'<h2>Engine ownership</h2><table class="table"><thead><tr><th>Engine</th><th>Role</th></tr></thead><tbody>{rows}</tbody></table>'
             f'<h2>Degradation behavior</h2><p>{esc(st["degradation"])}</p>')
    return render_stub("status", "Status", "System & engine ownership",
                       "Who owns what after the Perplexity handoff, and how the system degrades gracefully.", extra)


def targets():
    return {
        SITE / "workspace" / "index.html": render_index(),
        SITE / "workspace" / "radar" / "index.html": render_stub("radar", "Radar", "Weekly market radar", "The workspace radar mirrors the public radar feed."),
        SITE / "workspace" / "research" / "index.html": render_stub("research", "Research", "Deep research notes", "Longer-form dual-engine research write-ups."),
        SITE / "workspace" / "catalysts" / "index.html": render_stub("catalysts", "Catalysts", "Research calendar", "Upcoming catalysts tracked across the watchlist."),
        SITE / "workspace" / "methodology" / "index.html": render_stub("methodology", "Methodology", "How the pipeline works", "The read-only bypass, dual-engine verification, and the publish gate."),
        SITE / "workspace" / "status" / "index.html": render_status_page(),
        SITE / "workspace" / "assets" / "nvda" / "index.html": render_asset_page("nvda"),
        SITE / "workspace" / "assets" / "mstr" / "index.html": render_asset_page("mstr"),
        SITE / "workspace" / "assets" / "btc" / "index.html": render_asset_page("btc"),
    }


def main() -> int:
    check = "--check" in sys.argv
    changed = []
    for path, content in targets().items():
        content = content + "\n"
        old = path.read_text(encoding="utf-8") if path.exists() else None
        if old != content:
            changed.append(str(path.relative_to(SITE)))
            if not check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
    if check:
        if changed:
            print(f"WOULD_CHANGE {len(changed)}: {changed}")
            return 3
        print("OK — workspace pages up to date")
        return 0
    print(f"built {len(targets())} page(s); changed {len(changed)}: {changed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
