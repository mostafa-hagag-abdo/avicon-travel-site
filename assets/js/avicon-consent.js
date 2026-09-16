/* Avicon cookie consent — a small Accept / Decline banner that replaced the Complianz plugin.
   The choice is stored for 6 months in the "avicon_consent" cookie ("granted" or "denied").
   - Google Analytics loads only after "granted" (includes/tracking.php listens for the "avicon:consent" event).
   - Google Maps embeds (iframe[data-consent-src]) load after "granted", or when the visitor clicks "Show map".
   - Any [data-cookie-settings] element or a[href="#cookie-settings"] link reopens the banner.
   Visitors who had accepted statistics in the old Complianz banner count as "granted". */
(function () {
  'use strict';
  var COOKIE = 'avicon_consent';
  var MAX_AGE = 60 * 60 * 24 * 182;
  var POLICY_URL = '/cookie-policy-eu/';
  var MAP_PLACEHOLDER = '/assets/images/map-placeholder.jpg';

  function read() {
    var m = document.cookie.match(/(?:^|;\s*)avicon_consent=(granted|denied)/);
    if (m) return m[1];
    if (/(?:^|;\s*)cmplz_statistics=allow/.test(document.cookie)) return 'granted';
    return null;
  }

  var status = read();
  var banner = null;

  var api = window.aviconConsent = {
    status: function () { return status; },
    granted: function () { return status === 'granted'; },
    open: function () { show(); },
    set: function (value) {
      status = value === 'granted' ? 'granted' : 'denied';
      document.cookie = COOKIE + '=' + status + ';path=/;max-age=' + MAX_AGE + ';SameSite=Lax' +
        (location.protocol === 'https:' ? ';Secure' : '');
      hide();
      if (status === 'granted') loadMaps();
      try {
        document.dispatchEvent(new CustomEvent('avicon:consent', { detail: { status: status } }));
      } catch (e) { /* very old browsers */ }
    }
  };

  var CSS =
    '.avc-banner{position:fixed;z-index:2147483000;right:20px;bottom:20px;box-sizing:border-box;width:min(370px,calc(100vw - 24px));' +
    'background:#fff;color:#1A2B4A;border:1px solid #E1E8F0;border-radius:16px;box-shadow:0 18px 48px rgba(16,35,61,.20);' +
    'padding:18px 18px 16px;font-family:Poppins,system-ui,-apple-system,"Segoe UI",Arial,sans-serif;font-size:14px;line-height:1.55;' +
    'text-align:left;opacity:0;transform:translateY(14px);transition:opacity .25s ease,transform .25s ease}' +
    '.avc-banner.avc-in{opacity:1;transform:none}' +
    '.avc-banner *{box-sizing:border-box}' +
    '.avc-head{display:flex;align-items:center;gap:10px;margin:0 0 6px;font-size:15px;font-weight:700;color:#1A3A6E}' +
    '.avc-icon{flex:none;width:32px;height:32px;border-radius:50%;background:#FFF3DC;display:flex;align-items:center;justify-content:center}' +
    '.avc-text{margin:0 0 14px;color:#5A6B85}' +
    '.avc-text a{color:#1A3A6E;font-weight:600;text-decoration:underline;text-underline-offset:2px}' +
    '.avc-actions{display:grid;grid-template-columns:1fr 1fr;gap:10px}' +
    '.avc-btn{appearance:none;-webkit-appearance:none;margin:0;border:1.5px solid #1A3A6E;border-radius:999px;padding:10px 12px;' +
    'font-family:inherit;font-size:14px;font-weight:600;line-height:1.2;cursor:pointer;transition:background-color .2s,color .2s}' +
    '.avc-accept{background:#1A3A6E;color:#fff}.avc-accept:hover{background:#12294F;border-color:#12294F}' +
    '.avc-decline{background:#fff;color:#1A3A6E}.avc-decline:hover{background:#F4F8FC}' +
    '.avc-btn:focus-visible,.avc-map-btn:focus-visible,.avc-settings-btn:focus-visible{outline:3px solid #F5A623;outline-offset:2px}' +
    '@media (max-width:600px){.avc-banner{left:12px;right:12px;bottom:12px;width:auto;padding:14px 14px 12px;border-radius:14px}' +
    '.avc-head{font-size:14px}.avc-icon{width:28px;height:28px}.avc-text{font-size:13px;margin-bottom:12px}}' +
    '@media (prefers-reduced-motion:reduce){.avc-banner{transition:none}}' +
    '.avc-map{position:relative}' +
    '.avc-map-cover{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;' +
    'background:#DDE5EE url(' + MAP_PLACEHOLDER + ') center/cover no-repeat}' +
    '.avc-map-btn{appearance:none;-webkit-appearance:none;border:0;border-radius:999px;background:#fff;color:#1A3A6E;' +
    'box-shadow:0 4px 14px rgba(16,35,61,.18);padding:7px 14px;font-family:inherit;font-size:13px;font-weight:600;line-height:1.2;cursor:pointer}' +
    '.avc-settings-btn{appearance:none;-webkit-appearance:none;border:1.5px solid #1A3A6E;border-radius:999px;background:#1A3A6E;color:#fff;' +
    'padding:10px 18px;font-family:inherit;font-size:15px;font-weight:600;cursor:pointer}';

  function addCss() {
    if (document.getElementById('avc-css')) return;
    var style = document.createElement('style');
    style.id = 'avc-css';
    style.textContent = CSS;
    document.head.appendChild(style);
  }

  var ICON = '<svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true" focusable="false">' +
    '<path fill="#E0901A" d="M12 2a10 10 0 1 0 10 10 4 4 0 0 1-5-5 4 4 0 0 1-5-5Z"/>' +
    '<circle cx="8.5" cy="10.5" r="1.4" fill="#fff"/><circle cx="14" cy="15.5" r="1.4" fill="#fff"/><circle cx="8" cy="16" r="1" fill="#fff"/></svg>';

  function show() {
    addCss();
    if (!banner) {
      banner = document.createElement('div');
      banner.className = 'avc-banner';
      banner.setAttribute('role', 'dialog');
      banner.setAttribute('aria-live', 'polite');
      banner.setAttribute('aria-labelledby', 'avc-title');
      banner.setAttribute('aria-describedby', 'avc-desc');
      banner.setAttribute('data-nosnippet', '');
      banner.innerHTML =
        '<p class="avc-head" id="avc-title"><span class="avc-icon">' + ICON + '</span>We use cookies</p>' +
        '<p class="avc-text" id="avc-desc">They help us understand how visitors use our site and show maps. ' +
        'You can change your choice anytime. <a href="' + POLICY_URL + '">Cookie Policy</a></p>' +
        '<div class="avc-actions">' +
        '<button type="button" class="avc-btn avc-decline">Decline</button>' +
        '<button type="button" class="avc-btn avc-accept">Accept</button>' +
        '</div>';
      banner.querySelector('.avc-accept').addEventListener('click', function () { api.set('granted'); });
      banner.querySelector('.avc-decline').addEventListener('click', function () { api.set('denied'); });
    }
    if (!banner.parentNode) document.body.appendChild(banner);
    void banner.offsetWidth; // apply the start state so the slide-in transition runs
    banner.classList.add('avc-in');
  }

  function hide() {
    if (!banner || !banner.parentNode) return;
    var el = banner;
    el.classList.remove('avc-in');
    setTimeout(function () { if (el.parentNode && !el.classList.contains('avc-in')) el.parentNode.removeChild(el); }, 300);
  }

  function loadMap(frame) {
    var src = frame.getAttribute('data-consent-src');
    if (!src) return;
    frame.setAttribute('src', src);
    frame.removeAttribute('data-consent-src');
    var cover = frame.parentNode && frame.parentNode.querySelector('.avc-map-cover');
    if (cover) cover.parentNode.removeChild(cover);
  }

  function loadMaps() {
    var frames = document.querySelectorAll('iframe[data-consent-src]');
    for (var i = 0; i < frames.length; i++) loadMap(frames[i]);
  }

  function coverMaps() {
    var frames = document.querySelectorAll('iframe[data-consent-src]');
    for (var i = 0; i < frames.length; i++) {
      var frame = frames[i];
      var parent = frame.parentNode;
      if (!parent || parent.querySelector('.avc-map-cover')) continue;
      parent.classList.add('avc-map');
      var cover = document.createElement('div');
      cover.className = 'avc-map-cover';
      cover.innerHTML = '<button type="button" class="avc-map-btn">Show map</button>';
      (function (f) {
        cover.querySelector('button').addEventListener('click', function () { loadMap(f); });
      })(frame);
      parent.appendChild(cover);
    }
  }

  document.addEventListener('click', function (e) {
    var t = e.target && e.target.closest ? e.target.closest('[data-cookie-settings],a[href="#cookie-settings"]') : null;
    if (!t) return;
    e.preventDefault();
    show();
  });

  function init() {
    if (status === 'granted') {
      loadMaps();
    } else {
      addCss();
      coverMaps();
    }
    if (!status) show();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
