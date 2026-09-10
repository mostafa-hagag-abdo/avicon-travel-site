<?php
// GA4 + conversion events. GA only loads after the visitor accepts "Statistics" in the
// Complianz cookie banner. Put the GA4 Measurement ID here (looks like 'G-ABC123XYZ9'):
$AVI_GA_ID = 'G-LB417TZKD0';
?>
<script>
(function () {
  var ID = <?= json_encode($AVI_GA_ID) ?>;
  var loaded = false;
  window.dataLayer = window.dataLayer || [];

  function hasConsent() {
    if (typeof window.cmplz_has_consent === 'function') return window.cmplz_has_consent('statistics');
    return /(?:^|;\s*)cmplz_statistics=allow/.test(document.cookie);
  }
  function loadGA() {
    if (loaded || !ID || !hasConsent()) return;
    loaded = true;
    window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
    window.gtag('js', new Date());
    window.gtag('config', ID, { anonymize_ip: true, cookie_flags: 'secure;samesite=none' });
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(ID);
    document.head.appendChild(s);
  }
  document.addEventListener('cmplz_enable_category', loadGA);
  document.addEventListener('cmplz_status_change', loadGA);
  document.addEventListener('DOMContentLoaded', loadGA);
  loadGA();

  function track(name, params) {
    if (!loaded) return;
    params = params || {};
    params.page_path = location.pathname;
    window.gtag('event', name, params);
  }

  // WhatsApp / phone / email links
  document.addEventListener('click', function (e) {
    var a = e.target.closest ? e.target.closest('a[href]') : null;
    if (!a) return;
    var h = a.getAttribute('href') || '';
    if (/wa\.me|whatsapp\.com/i.test(h)) track('whatsapp_click', { method: 'whatsapp', link_url: h });
    else if (/^tel:/i.test(h)) track('phone_click', { method: 'phone', link_url: h });
    else if (/^mailto:/i.test(h)) track('email_click', { method: 'email', link_url: h });
  }, true);

  function formName(src) {
    try {
      if (typeof src === 'string') { var o = JSON.parse(src); return o.tour_package || o.subject || ''; }
      if (src && typeof src.get === 'function') return src.get('tour_package') || src.get('subject') || '';
    } catch (err) {}
    return '';
  }

  // booking + tailor-made forms send with fetch(): count only confirmed submissions
  if (window.fetch) {
    var nativeFetch = window.fetch;
    window.fetch = function (input, init) {
      var url = typeof input === 'string' ? input : (input && input.url) || '';
      var p = nativeFetch.apply(this, arguments);
      if (/api\.web3forms\.com/.test(url)) {
        var name = formName(init && init.body);
        p.then(function (r) { return r.clone().json(); })
          .then(function (j) { if (j && j.success) track('generate_lead', { method: 'form', form_name: name }); })
          .catch(function () {});
      }
      return p;
    };
  }

  // transfer forms post straight to Web3Forms (page navigates away)
  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (!f || !/web3forms/.test(f.getAttribute('action') || '')) return;
    setTimeout(function () {
      if (!e.defaultPrevented) track('generate_lead', { method: 'form', form_name: formName(new FormData(f)), transport_type: 'beacon' });
    }, 0);
  });
})();
</script>
