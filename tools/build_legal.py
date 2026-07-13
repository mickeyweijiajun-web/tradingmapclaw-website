#!/usr/bin/env python3
"""Generate 6 legal pages for TradingMapClaw sharing the site's visual language."""
import os

OUT = os.path.join(os.path.dirname(__file__), "legal")
os.makedirs(OUT, exist_ok=True)

EFFECTIVE = "July 4, 2026"

HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title} — TradingMapClaw</title>
<meta name="description" content="{desc}" />
<meta name="robots" content="index,follow" />
<link rel="icon" href="../assets/logo-icon.jpg" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
<style>
  :root{{
    --bg:#f7f6f2; --surface:#f9f8f5; --surface-2:#fbfbf9; --surface-offset:#f1efe9;
    --divider:#e3e0d9; --border:#d4d1ca;
    --text:#28251d; --text-muted:#6f6d66; --text-faint:#b3b1aa;
    --primary:#01696f; --primary-hover:#0c4e54; --primary-highlight:#dceae8;
    --accent:#e0812f; --teal-brand:#178b8f; --error:#a12c7b; --success:#437a22;
    --font-display:'Space Grotesk',system-ui,sans-serif;
    --font-body:'Inter',system-ui,sans-serif;
    --font-mono:'JetBrains Mono',ui-monospace,monospace;
    --maxw:820px; --r-sm:8px; --r-md:14px; --r-full:999px;
  }}
  *{{margin:0;padding:0;box-sizing:border-box}}
  html{{scroll-behavior:smooth;-webkit-text-size-adjust:100%}}
  body{{font-family:var(--font-body);font-size:16px;line-height:1.7;color:var(--text);background:var(--bg);-webkit-font-smoothing:antialiased}}
  a{{color:var(--primary);text-decoration:none}}
  a:hover{{text-decoration:underline}}
  img{{max-width:100%;display:block}}
  .nav{{position:sticky;top:0;z-index:20;background:rgba(247,246,242,.9);backdrop-filter:blur(10px);border-bottom:1px solid var(--divider)}}
  .nav-inner{{max-width:var(--maxw);margin:0 auto;padding:.9rem 1.5rem;display:flex;align-items:center;justify-content:space-between}}
  .nav-logo{{display:flex;align-items:center;gap:.55rem;font-family:var(--font-display);font-weight:700;font-size:1.05rem;color:var(--text)}}
  .nav-logo img{{width:28px;height:28px;border-radius:7px}}
  .nav-logo .accent{{color:var(--primary)}}
  .nav-back{{font-family:var(--font-mono);font-size:.8rem;color:var(--text-muted)}}
  .wrap{{max-width:var(--maxw);margin:0 auto;padding:3rem 1.5rem 4rem}}
  .crumb{{font-family:var(--font-mono);font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:var(--text-muted);margin-bottom:.8rem}}
  h1{{font-family:var(--font-display);font-size:2rem;font-weight:700;letter-spacing:-.02em;line-height:1.15;margin-bottom:.5rem}}
  .eff{{font-family:var(--font-mono);font-size:.78rem;color:var(--text-muted);margin-bottom:2rem}}
  h2{{font-family:var(--font-display);font-size:1.15rem;font-weight:600;margin:2rem 0 .6rem;letter-spacing:-.01em}}
  p{{margin-bottom:1rem;color:var(--text)}}
  ul{{margin:0 0 1rem 1.2rem}}
  li{{margin-bottom:.5rem}}
  .callout{{background:var(--surface-offset);border:1px solid var(--border);border-left:3px solid var(--accent);border-radius:var(--r-sm);padding:1rem 1.2rem;margin:1.4rem 0;font-size:.95rem}}
  .callout.compliance{{border-left-color:var(--primary)}}
  strong{{font-weight:600}}
  .footer{{border-top:1px solid var(--divider);background:var(--surface-offset)}}
  .footer-inner{{max-width:var(--maxw);margin:0 auto;padding:2rem 1.5rem;display:flex;flex-wrap:wrap;gap:1rem;justify-content:space-between;align-items:center;font-size:.85rem;color:var(--text-muted)}}
  .footer-links{{display:flex;flex-wrap:wrap;gap:.4rem 1rem}}
  .footer-links a{{color:var(--text-muted)}}
  .disc{{max-width:var(--maxw);margin:0 auto;padding:0 1.5rem 2rem;font-size:.8rem;color:var(--text-muted);line-height:1.6}}
  @media(max-width:640px){{h1{{font-size:1.6rem}}}}
</style>
</head>
<body>
<nav class="nav"><div class="nav-inner">
  <a class="nav-logo" href="../index.html"><img src="../assets/logo-icon.jpg" alt="TradingMapClaw" /><span>TradingMap<span class="accent">Claw</span></span></a>
  <a class="nav-back" href="../index.html">← Back to site</a>
</div></nav>
<main class="wrap">
  <p class="crumb">Legal · {title}</p>
  <h1>{title}</h1>
  <p class="eff">Effective {eff} · TradingMapClaw (TMC)</p>
{body}
</main>
<footer class="footer">
  <div class="footer-inner">
    <span>© 2026 TradingMapClaw</span>
    <span class="footer-links">
      <a href="terms.html">Terms</a><a href="privacy.html">Privacy</a><a href="refund.html">Refund</a><a href="delivery.html">Delivery</a><a href="disclaimer.html">Disclaimer</a><a href="contact.html">Contact</a>
    </span>
  </div>
  <p class="disc"><strong>Compliance:</strong> TradingMapClaw is an educational AI-workflow product operating in WATCHLIST_ONLY mode. All content, digital products, and consulting are for research and educational purposes and are <strong>not investment advice</strong>. We do not route orders, execute trades, or provide personalized financial advice.</p>
</footer>
</body>
</html>
"""

COMPLIANCE = ('<div class="callout compliance"><strong>Not investment advice.</strong> '
    'TradingMapClaw sells educational material and AI-workflow guidance only. Nothing here is a '
    'recommendation to buy, sell, or hold any security or asset, and no product constitutes personalized '
    'financial, legal, or tax advice. Markets carry risk; you are solely responsible for your own decisions.</div>')

PAGES = {}

PAGES["terms"] = ("Terms of Service",
  "The terms governing use of the TradingMapClaw website, digital products, and consulting.",
  f"""
  <p>These Terms of Service ("Terms") govern your access to and use of the TradingMapClaw website at tradingmapclaw.com (the "Site"), and any digital products, tutorials, skill packs, or consulting services ("Products") offered through it. By accessing the Site or purchasing a Product, you agree to these Terms.</p>

  {COMPLIANCE}

  <h2>1. Who we are</h2>
  <p>TradingMapClaw ("TMC", "we", "us") is an independent, single-operator project publishing educational material about building and running AI research workflows. It is operated by an individual seller. We are not a broker-dealer, investment adviser, fund, or financial institution of any kind.</p>

  <h2>2. Nature of the Products</h2>
  <p>All Products are <strong>educational and informational</strong>. They teach system architecture, AI-workflow engineering, budget control, prompt design, and solo-operator methodology. Products include downloadable guides, code templates, prompt sets, skill packs, and — where offered — limited-seat consulting sessions about AI workflows.</p>
  <ul>
    <li>Products <strong>do not</strong> provide stock picks, trade signals, price targets, or personalized investment advice.</li>
    <li>Any example tickers, numbers, or configurations are illustrative only.</li>
    <li>The underlying research system operates in <strong>WATCHLIST_ONLY</strong> mode — it never places or executes orders.</li>
  </ul>

  <h2>3. Consulting scope and boundaries</h2>
  <p>Where consulting or "operator guidance" is offered, the scope is strictly limited to AI workflow, tooling, system design, and budget engineering. Sessions may be recorded for quality and dispute-resolution purposes with your prior notice and consent.</p>
  <ul>
    <li>We will <strong>not</strong> advise on which securities or assets to buy, sell, or hold, nor construct or manage a portfolio for you.</li>
    <li>If a client requests personalized investment advice, the session boundary will be restated. Continued insistence on receiving investment advice is grounds to <strong>terminate the session without refund</strong>, as it falls outside the agreed and lawful scope of service.</li>
    <li>Seats are limited and offered on a first-come basis.</li>
  </ul>

  <h2>4. Payment and pricing</h2>
  <p>Products are sold in US dollars through third-party digital-commerce and payment providers (for example, a digital-product storefront and PayPal). Those providers process your payment and handle receipts under their own terms and privacy policies. We do not store your full card details. Prices may change at any time; the price shown at checkout applies to your purchase.</p>
  <p>We do not accept, sell, or price Products in cryptocurrency.</p>

  <h2>5. License and acceptable use</h2>
  <p>On purchase, you receive a personal, non-exclusive, non-transferable license to use the Product for your own learning and internal use. You may not resell, redistribute, sublicense, publicly post, or republish the Products or their substantial contents. Code templates may be adapted for your own private projects.</p>

  <h2>6. Intellectual property</h2>
  <p>All Site content and Products, including text, code, designs, and the TradingMapClaw name and logo, are owned by TMC or its licensors and protected by applicable law.</p>

  <h2>7. No warranty</h2>
  <p>Products are provided "as is" and "as available", without warranties of any kind, express or implied. We do not warrant that the Products will meet your requirements, produce any financial result, or be error-free. You are responsible for validating any code or configuration before use.</p>

  <h2>8. Limitation of liability</h2>
  <p>To the maximum extent permitted by law, TMC is not liable for any indirect, incidental, or consequential damages, or for any trading, investment, or financial losses arising from your use of the Site or Products. Our total liability for any claim is limited to the amount you paid for the relevant Product.</p>

  <h2>9. Changes and termination</h2>
  <p>We may update these Terms or the Products at any time. Material changes will be reflected by the effective date above. We may suspend or terminate access for breach of these Terms.</p>

  <h2>10. Governing law and contact</h2>
  <p>These Terms are governed by applicable law in the operator's jurisdiction, without regard to conflict-of-law rules. Questions: <a href="mailto:contact@tradingmapclaw.com">contact@tradingmapclaw.com</a>.</p>
  """)

PAGES["privacy"] = ("Privacy Policy",
  "How TradingMapClaw collects, uses, and protects your personal information.",
  f"""
  <p>This Privacy Policy explains what information TradingMapClaw ("TMC", "we") collects when you visit the Site or purchase a Product, how we use it, and your choices.</p>

  <h2>1. Information we collect</h2>
  <ul>
    <li><strong>Purchase information:</strong> when you buy a Product, our payment and storefront providers collect your name, email, billing details, and transaction data. We receive order confirmations and your email for delivery and support — we do <strong>not</strong> receive or store your full card number.</li>
    <li><strong>Contact information:</strong> if you email us or book a session, we keep the messages and details you provide.</li>
    <li><strong>Usage data:</strong> basic, privacy-respecting analytics (for example, aggregate page views) may be collected to understand Site traffic. We do not build advertising profiles.</li>
  </ul>

  <h2>2. How we use your information</h2>
  <ul>
    <li>To deliver Products and download links, and to provide receipts and support.</li>
    <li>To schedule and conduct consulting sessions you have booked.</li>
    <li>To respond to your enquiries and comply with legal obligations (for example, tax records).</li>
  </ul>

  <h2>3. Third-party processors</h2>
  <p>We rely on reputable third parties to run the business, including a digital-product storefront, a payment provider (such as PayPal), an email provider, and scheduling/video-call tools for consulting. Each processes data under its own privacy policy. We share only what is necessary to complete your purchase or session.</p>

  <h2>4. Consulting call recordings</h2>
  <p>Where consulting sessions are recorded, recordings are used only for quality assurance and to resolve payment disputes or chargebacks. You are notified before recording and recordings are retained only as long as reasonably necessary.</p>

  <h2>5. Cookies</h2>
  <p>The Site uses minimal, essential cookies and may use privacy-respecting analytics. You can control cookies through your browser settings.</p>

  <h2>6. Data retention and security</h2>
  <p>We keep personal information only as long as needed for the purposes above or as required by law, and we take reasonable measures to protect it. No method of transmission or storage is completely secure.</p>

  <h2>7. Your rights</h2>
  <p>Depending on your location, you may have rights to access, correct, delete, or export your personal data, or to object to certain processing. To exercise these rights, email <a href="mailto:contact@tradingmapclaw.com">contact@tradingmapclaw.com</a>.</p>

  <h2>8. Children</h2>
  <p>The Site and Products are intended for adults. We do not knowingly collect data from children under 16.</p>

  <h2>9. Changes and contact</h2>
  <p>We may update this Policy; the effective date above reflects the latest version. Questions: <a href="mailto:contact@tradingmapclaw.com">contact@tradingmapclaw.com</a>.</p>
  """)

PAGES["refund"] = ("Refund Policy",
  "Refund terms for TradingMapClaw digital products and consulting services.",
  f"""
  <p>This Refund Policy applies to all Products purchased through TradingMapClaw. Because most Products are <strong>digital goods delivered instantly</strong>, please read carefully before purchasing.</p>

  <h2>1. Digital products (guides, templates, skill packs)</h2>
  <p>Digital Products are delivered immediately as downloadable files. Once a download has been accessed or delivered, the sale is generally <strong>final and non-refundable</strong>, because the goods cannot be "returned".</p>
  <p>We will, however, provide a refund or replacement where:</p>
  <ul>
    <li>The files are corrupted, incomplete, or cannot be downloaded and we cannot fix the issue within a reasonable time; or</li>
    <li>You were charged in error or charged more than once for the same item; or</li>
    <li>A refund is required by applicable consumer-protection law.</li>
  </ul>
  <p>To request a refund on these grounds, email <a href="mailto:contact@tradingmapclaw.com">contact@tradingmapclaw.com</a> within <strong>14 days</strong> of purchase with your order details and a description of the problem.</p>

  <h2>2. Consulting and operator guidance</h2>
  <ul>
    <li>If you cancel a booked session at least <strong>24 hours</strong> before the scheduled time, you may reschedule or receive a full refund.</li>
    <li>No-shows and cancellations inside 24 hours are non-refundable, as the seat was reserved for you.</li>
    <li>Sessions are limited to AI-workflow guidance. If a session is terminated because a client insists on receiving personalized investment advice (outside the agreed and lawful scope), <strong>no refund</strong> is due for that session.</li>
  </ul>

  <h2>3. Chargebacks</h2>
  <p>If you believe a charge is wrong, please contact us first — most issues are resolved quickly. Filing a chargeback without contacting us may delay resolution. We retain order records and, where applicable, session recordings to respond to disputes.</p>

  {COMPLIANCE}

  <h2>4. Contact</h2>
  <p>All refund requests: <a href="mailto:contact@tradingmapclaw.com">contact@tradingmapclaw.com</a>.</p>
  """)

PAGES["delivery"] = ("Delivery Policy",
  "How and when TradingMapClaw digital products and consulting sessions are delivered.",
  f"""
  <p>This Delivery Policy explains how you receive Products purchased from TradingMapClaw.</p>

  <h2>1. Digital products</h2>
  <ul>
    <li>Guides, templates, prompt sets, and skill packs are <strong>delivered digitally and automatically</strong> immediately after payment is confirmed.</li>
    <li>You will receive a download link on the confirmation screen and by email at the address used at checkout.</li>
    <li>There is no physical shipment and no shipping cost. All Products are electronic files.</li>
  </ul>

  <h2>2. If you do not receive your files</h2>
  <p>If a download link does not arrive within a few minutes, please check your spam or promotions folder. If you still cannot access your files, email <a href="mailto:contact@tradingmapclaw.com">contact@tradingmapclaw.com</a> with your order details and we will resend the link.</p>

  <h2>3. Consulting sessions</h2>
  <ul>
    <li>After booking, you will receive a scheduling link to choose a time and a video-call link for the session.</li>
    <li>Sessions are conducted online and may be recorded for quality and dispute-resolution purposes with prior notice.</li>
    <li>Any promised written follow-up (notes or summary) is delivered by email after the session.</li>
  </ul>

  <h2>4. Access and formats</h2>
  <p>Products are provided in common formats (PDF, Markdown, ZIP archives, and plain-text code). You are responsible for having software able to open these formats.</p>

  <h2>5. Contact</h2>
  <p>Delivery questions: <a href="mailto:contact@tradingmapclaw.com">contact@tradingmapclaw.com</a>.</p>
  """)

PAGES["disclaimer"] = ("Disclaimer",
  "Important disclaimers about TradingMapClaw content, products, and the WATCHLIST_ONLY boundary.",
  f"""
  {COMPLIANCE}

  <h2>1. Educational purpose only</h2>
  <p>Everything on this Site and in every Product is provided for <strong>research and educational purposes only</strong>. TradingMapClaw teaches how to build and operate AI research workflows. It does not tell you what to invest in.</p>

  <h2>2. Not financial, legal, or tax advice</h2>
  <p>TMC is not a broker-dealer, investment adviser, or financial planner, and nothing here should be construed as personalized financial, legal, or tax advice. No content is an offer or solicitation to buy or sell any security or asset. Consult a licensed professional before making financial decisions.</p>

  <h2>3. WATCHLIST_ONLY by design</h2>
  <p>The research system described on this Site operates in <strong>WATCHLIST_ONLY</strong> mode. It produces research and analysis, cross-verified by multiple AI models, and delivers reports. It has <strong>no</strong> broker API and <strong>no</strong> order-execution capability. It never places, routes, or executes trades.</p>

  <h2>4. AI-generated content and accuracy</h2>
  <p>Outputs may be generated or assisted by AI models and can contain errors, omissions, or outdated information. Example figures, tickers, and configurations are illustrative. You must independently verify anything before relying on it.</p>

  <h2>5. No guaranteed results</h2>
  <p>Building the systems described here requires your own time, skill, and API subscriptions. We make no promise of any financial return, cost saving, or performance outcome. Past examples are not indicative of future results.</p>

  <h2>6. Third-party references</h2>
  <p>References to third-party tools, platforms, or prices are for comparison and education. We are not affiliated with, endorsed by, or sponsored by those companies, and their prices and features may change.</p>

  <h2>7. Assumption of risk</h2>
  <p>Markets — including equities and crypto — carry significant risk, including total loss. You are solely responsible for your own decisions and their consequences. By using this Site or any Product, you accept these disclaimers.</p>

  <h2>8. Contact</h2>
  <p>Questions about this Disclaimer: <a href="mailto:contact@tradingmapclaw.com">contact@tradingmapclaw.com</a>.</p>
  """)

PAGES["contact"] = ("Contact",
  "How to reach TradingMapClaw for support, purchases, and consulting.",
  f"""
  <p>TradingMapClaw is an independent, single-operator project. The fastest way to reach us is by email — we read every message.</p>

  <h2>General &amp; support</h2>
  <p>Email: <a href="mailto:contact@tradingmapclaw.com">contact@tradingmapclaw.com</a></p>
  <p>Use this address for order help, download issues, refund requests, and general questions. Please include your order details where relevant.</p>

  <h2>Follow the build</h2>
  <ul>
    <li>X (Twitter): <a href="https://x.com/tradingmapclaw" target="_blank" rel="noopener">@tradingmapclaw</a></li>
    <li>LinkedIn: <a href="https://www.linkedin.com/company/tradingmapclaw/" target="_blank" rel="noopener">TradingMapClaw</a></li>
    <li>Substack: <a href="https://tradingmapclaw.substack.com" target="_blank" rel="noopener">tradingmapclaw.substack.com</a></li>
    <li>Medium: <a href="https://medium.com/@tradingmapclaw" target="_blank" rel="noopener">@tradingmapclaw</a></li>
    <li>Telegram: <a href="https://t.me/tradingmapclaw" target="_blank" rel="noopener">t.me/tradingmapclaw</a></li>
  </ul>

  <h2>Consulting &amp; guidance</h2>
  <p>Operator-guidance sessions are limited-seat and cover AI workflows, system design, and budget engineering only — <strong>not</strong> investment advice. To enquire about availability, email us with a short note about what you want to build.</p>

  {COMPLIANCE}

  <h2>Response time</h2>
  <p>As a solo operation, replies may take a little time, especially across time zones. Thank you for your patience.</p>
  """)

for slug, (title, desc, body) in PAGES.items():
    html = HEAD.format(title=title, desc=desc, eff=EFFECTIVE, body=body)
    with open(os.path.join(OUT, f"{slug}.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote legal/{slug}.html ({len(html)} bytes)")
print("done")
