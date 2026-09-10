<?php // CTA bar only ?>
<style>
.av-home{--primary:#123f7a;--primary-2:#1e90ff;--accent:#f6a13a;--ink:#10233d;--muted:#5d6b80;--soft:#f4f8fd;--line:#dbe6f2;--green:#1a9b77;--shadow:0 12px 32px rgba(16,35,61,.1);font-family:Poppins,Arial,sans-serif;color:var(--ink);background:#fff}
.av-home *{box-sizing:border-box}
.av-home a{text-decoration:none;color:inherit}
.av-home .container{max-width:1180px;margin:0 auto;padding:0 20px}
.av-home .btn{display:inline-flex;align-items:center;justify-content:center;gap:9px;min-height:44px;border-radius:8px;padding:11px 16px;font-size:14px;font-weight:900;transition:all .2s ease}
.av-home .btn.primary{background:var(--accent);color:#10233d}
.av-home .btn.secondary{background:#fff;color:var(--primary);border:1px solid var(--line)}
.av-home .btn:hover{transform:translateY(-2px)}
.av-home .cta{padding:44px 0;background:#10233d}
.av-home .cta-grid{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:24px;align-items:center}
.av-home .cta h2{margin:0 0 8px;color:#fff;font-size:34px}
.av-home .cta p{margin:0;color:rgba(255,255,255,.84);line-height:1.7}
.av-home .cta-actions{display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end}
@media(max-width:992px){.av-home .cta-grid{grid-template-columns:1fr}.av-home .cta-actions{justify-content:flex-start}}
</style>
<div class="av-home">
<section class="cta">
    <div class="container">
      <div class="cta-grid">
        <div>
          <h2>Tailor-Made Egypt Tours by Avicon Travel</h2>
          <p>Tell Avicon Travel your destination, travel dates, group size, and preferred style, and get a custom Egypt itinerary covering packages, Nile cruises, day tours, transfers, or all of them together.</p>
        </div>
        <div class="cta-actions">
          <a class="btn primary" href="https://wa.me/201200555600" target="_blank" rel="noopener"><i class="fab fa-whatsapp"></i> WhatsApp</a>
          <a class="btn secondary" href="mailto:info@avicontravel.com"><i class="fas fa-envelope"></i> Email Us</a>
        </div>
      </div>
    </div>
  </section>
</div>
