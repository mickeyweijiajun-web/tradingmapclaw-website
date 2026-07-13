#!/usr/bin/env python3
"""publish_brief_page.py — freeze a weekly brief JSON into a permanent archive page + RSS.

Reads site/data/radar-<PERIOD>.json and writes:
  - site/research/radar/<period-lower>/index.html  (frozen snapshot, no TMC markers)
  - site/rss.xml  (rebuilt from all site/data/radar-*.json LIVE editions, newest first)

Usage: python3 tools/publish_brief_page.py 2026-W29
"""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE = REPO_ROOT / "site"
BASE = "https://www.tradingmapclaw.com"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_site_data import render_radar_rows  # noqa: E402

PAGE_TMPL = """<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Weekly Market Intelligence Brief {period} | TradingMapClaw Research</title>
<meta name="description" content="Weekly Market Intelligence Brief {period} — dual-source verified watchlist observations. Research and education only. Not investment advice." />
<meta name="author" content="TradingMapClaw" />
<meta name="robots" content="index, follow, max-image-preview:large" />
<meta name="theme-color" content="#01696f" />
<link rel="canonical" href="{base}/research/radar/{slug}" />
<link rel="sitemap" type="application/xml" href="/sitemap.xml" />
<link rel="alternate" type="application/rss+xml" title="TradingMapClaw Weekly Brief" href="/rss.xml" />
<meta property="og:site_name" content="TradingMapClaw" />
<meta property="og:title" content="Weekly Market Intelligence Brief {period}" />
<meta property="og:description" content="Dual-source verified watchlist observations for {period}. Research and education only." />
<meta property="og:type" content="article" />
<meta property="og:url" content="{base}/research/radar/{slug}" />
<meta property="og:image" content="{base}/assets/logo-slogan.jpg" />
<meta property="og:locale" content="en_US" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Weekly Market Intelligence Brief {period}" />
<meta name="twitter:image" content="{base}/assets/logo-slogan.jpg" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='8' fill='%23155e63'/%3E%3Cpath d='M8 24 L11 12 L16 19 L21 12 L24 24' stroke='white' stroke-width='2.6' fill='none' stroke-linecap='round' stroke-linejoin='round'/%3E%3Ccircle cx='24' cy='9' r='3' fill='%23e8873a'/%3E%3C/svg%3E" />
<link rel="stylesheet" href="/assets/site.css" />
</head>
<body>
<nav class="nav" id="nav">
  <div class="nav-inner">
    <a class="nav-logo" href="/" aria-label="TradingMapClaw home">
      <img class="mark" src="/assets/logo-icon.jpg" alt="TradingMapClaw logo" width="30" height="30" />
      <span>TradingMap<span class="accent">Claw</span></span>
    </a>
    <div class="nav-links" id="navLinks">
      <a href="/story">Story</a>
      <a href="/research">Research</a>
      <a href="/system">System</a>
      <a href="/build-log">Build Log</a>
      <a href="/products">Products</a>
      <a href="/faq">FAQ</a>
    </div>
    <div class="nav-right">
      <a class="btn btn-primary" href="/products">Get Access</a>
      <button class="nav-toggle" id="navToggle" aria-label="Toggle navigation" aria-expanded="false">☰</button>
    </div>
  </div>
</nav>
<main>

<header class="page-hero"><div class="ph-inner"><p class="section-label">Market Radar · {period}</p><h1>Weekly Market Intelligence Brief.</h1><p class="ph-sub">Archived edition for {period}, published {published_at}. Frozen at publication — this page does not change after it ships.</p><p class="ph-compliance">Research &amp; education only. Not investment advice. · WATCHLIST_ONLY</p></div></header>

<section class="section" id="table">
  <div class="section-inner">
    <div class="section-head">
      <p class="section-label">Verified Table</p>
      <h2 class="section-title">Watchlist moves, {period}.</h2>
      <p class="radar-cap mono">PERIOD {period} · DATA AS OF {data_as_of} · <span class="pstatus live">{status}</span></p>
    </div>
    <div class="radar-table-wrap">
      <table class="radar-table">
        <thead><tr><th>Ticker</th><th>Sector</th><th>Surge Δ (5d)</th><th>Band</th><th>Verified by</th></tr></thead>
        <tbody>
          {rows}
        </tbody>
      </table>
      <p class="mono radar-cap">Band = research-priority band from the verified 5-day move: <span class="sf sf-hi">±8%+</span> high priority · <span class="sf sf-mid">±3–8%</span> watch · <span class="sf sf-low">below ±3%</span> logged.</p>
      <p class="mono radar-cap">{scope_note}</p>
      <p class="mono radar-cap">Methodology: {methodology}</p>
    </div>
  </div>
</section>

<section class="cta-band">
  <div class="section-inner">
    <h2 class="section-title">Want next week's edition?</h2>
    <p class="section-sub" style="margin:0 auto 1.4rem;max-width:520px">Follow the <a href="/rss.xml" style="color:inherit;text-decoration:underline">RSS feed</a> or browse the <a href="/research/radar" style="color:inherit;text-decoration:underline">archive</a>.</p>
    <div class="hero-actions" style="justify-content:center">
      <a class="btn btn-primary btn-lg" href="/research/radar">← Radar archive</a>
      <a class="btn btn-ghost btn-lg" href="/radar">Current radar page</a>
    </div>
  </div>
</section>

</main>

<footer class="footer">
  <div class="footer-inner">
    <p class="disclaimer"><b>Compliance:</b> TradingMapClaw is an independent financial-market research, information-aggregation and research-engineering platform operating in <b>WATCHLIST_ONLY</b> mode. It provides market research, educational materials, research software, and workflow-engineering services. It does not execute trades, hold customer funds, operate brokerage accounts, or provide individualized investment recommendations. All output and all products sold here are for research and educational purposes and are <b>not investment advice</b>. Markets carry risk; do your own diligence.</p>
    <div class="footer-bottom">
      <span>© 2026 TradingMapClaw · Research &amp; education only · Not investment advice</span>
      <span>Archived edition · {period} · published {published_at}</span>
    </div>
  </div>
</footer>

<script>
  const nav = document.getElementById('nav');
  const onScroll = () => {{ nav.classList.toggle('scrolled', window.scrollY > 12); }};
  window.addEventListener('scroll', onScroll, {{passive:true}});
  onScroll();
  const tgl = document.getElementById('navToggle'), links = document.getElementById('navLinks');
  if (tgl && links) tgl.addEventListener('click', () => {{
    const open = links.classList.toggle('open');
    tgl.setAttribute('aria-expanded', open ? 'true' : 'false');
  }});
</script>
<script src="/assets/js/tmc-events.js"></script>
</body>
</html>
"""


def build_rss() -> None:
    items = []
    for p in sorted(SITE.glob("data/radar-2*.json"), reverse=True):
        d = json.loads(p.read_text())
        if d.get("is_sample") or not d.get("rows"):
            continue
        period = d["period"]
        slug = period.lower()
        ok = [r for r in d["rows"] if "surge_5d_pct" in r]
        top = sorted(ok, key=lambda r: -abs(r["surge_5d_pct"]))[:3]
        summary = "; ".join(
            f"{r['ticker']} {'+' if r['surge_5d_pct'] >= 0 else ''}{r['surge_5d_pct']}% 5d"
            for r in top)
        desc = (f"Weekly Market Intelligence Brief {period}. Dual-source verified moves: "
                f"{summary}. Research and education only — not investment advice.")
        items.append(
            "  <item>\n"
            f"   <title>Weekly Market Intelligence Brief {html.escape(period)}</title>\n"
            f"   <link>{BASE}/research/radar/{slug}</link>\n"
            f"   <guid isPermaLink=\"true\">{BASE}/research/radar/{slug}</guid>\n"
            f"   <pubDate>{d['published_at']}T04:00:00Z</pubDate>\n"
            f"   <description>{html.escape(desc)}</description>\n"
            "  </item>")
    rss = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
           "<rss version=\"2.0\" xmlns:atom=\"http://www.w3.org/2005/Atom\">\n"
           " <channel>\n"
           "  <title>TradingMapClaw — Weekly Market Intelligence Brief</title>\n"
           f"  <link>{BASE}/research/radar</link>\n"
           "  <description>Dual-source verified weekly watchlist observations. Research and education only — not investment advice. WATCHLIST_ONLY.</description>\n"
           "  <language>en-us</language>\n"
           f"  <atom:link href=\"{BASE}/rss.xml\" rel=\"self\" type=\"application/rss+xml\" />\n"
           + "\n".join(items) + "\n </channel>\n</rss>\n")
    (SITE / "rss.xml").write_text(rss)
    print(f"rss.xml rebuilt with {len(items)} item(s)")


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: publish_brief_page.py <PERIOD e.g. 2026-W29>", file=sys.stderr)
        return 2
    period = sys.argv[1]
    data_file = SITE / "data" / f"radar-{period}.json"
    d = json.loads(data_file.read_text())
    if d.get("is_sample"):
        print("refusing to archive a SAMPLE edition", file=sys.stderr)
        return 1
    slug = period.lower()
    out_dir = SITE / "research" / "radar" / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    page = PAGE_TMPL.format(
        base=BASE, period=period, slug=slug,
        published_at=d["published_at"], data_as_of=d["data_as_of"],
        status=d.get("status", "LIVE"),
        rows=render_radar_rows(d),
        scope_note=html.escape(d.get("scope_note", "")),
        methodology=html.escape(d.get("methodology", "")),
    )
    (out_dir / "index.html").write_text(page)
    print(f"wrote {out_dir / 'index.html'}")
    build_rss()
    return 0


if __name__ == "__main__":
    sys.exit(main())
