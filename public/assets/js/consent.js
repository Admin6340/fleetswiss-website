/*!
 * FleetSwiss Consent – schlanke, wiederverwendbare Einwilligungsverwaltung
 *
 * Aktueller Stand: Es sind KEINE optionalen (einwilligungspflichtigen) Dienste
 * registriert. Das Skript zeigt daher kein Banner an und liest oder schreibt
 * nichts in Cookies oder LocalStorage.
 *
 * Später ergänzen (Beispiel Statistik):
 *   1. Unten in CONFIG.categories die Kategorie aktivieren und den Dienst eintragen:
 *        analytics: { label: 'Statistik', description: '…',
 *                     services: [{ name: 'Anbieter X', purpose: '…' }] }
 *   2. Das Dienst-Skript im HTML nur blockiert einbinden:
 *        <script type="text/plain" data-consent="analytics" data-src="https://…"></script>
 *      oder mit Inline-Code: <script type="text/plain" data-consent="analytics">…</script>
 *   3. CONFIG.version erhöhen, wenn sich Dienste/Zwecke ändern (erneute Abfrage).
 *   4. Datenschutzerklärung nachführen.
 *
 * API: window.FleetSwissConsent.has('analytics'), .open(), .onChange(fn)
 */
(function () {
  'use strict';

  var CONFIG = {
    version: 1,
    storageKey: 'fs_consent',
    privacyUrl: '/datenschutz.html',
    categories: {
      necessary: {
        required: true,
        label: 'Technisch notwendig',
        description: 'Für den Betrieb der Website erforderlich. Aktuell werden keine Cookies gesetzt.',
        services: []
      },
      // analytics: { label: 'Statistik', description: '', services: [] },
      // marketing: { label: 'Marketing', description: '', services: [] }
    }
  };

  var listeners = [];
  var state = null; // { v: version, t: timestamp, c: { kategorie: true|false } }

  function optionalCategories() {
    return Object.keys(CONFIG.categories).filter(function (k) {
      var c = CONFIG.categories[k];
      return !c.required && c.services && c.services.length > 0;
    });
  }

  function read() {
    try {
      var raw = window.localStorage.getItem(CONFIG.storageKey);
      if (!raw) return null;
      var s = JSON.parse(raw);
      return s && s.v === CONFIG.version ? s : null;
    } catch (e) { return null; }
  }

  function write(choices) {
    state = { v: CONFIG.version, t: new Date().toISOString(), c: choices };
    try { window.localStorage.setItem(CONFIG.storageKey, JSON.stringify(state)); } catch (e) {}
    activate();
    listeners.forEach(function (fn) { try { fn(api.get()); } catch (e) {} });
  }

  function has(cat) {
    var c = CONFIG.categories[cat];
    if (!c) return false;
    if (c.required) return true;
    return !!(state && state.c && state.c[cat]);
  }

  // Blockierte Skripte erst nach Einwilligung ausführen
  function activate() {
    var nodes = document.querySelectorAll('script[type="text/plain"][data-consent]');
    Array.prototype.forEach.call(nodes, function (n) {
      if (!has(n.getAttribute('data-consent'))) return;
      var s = document.createElement('script');
      if (n.getAttribute('data-src')) s.src = n.getAttribute('data-src');
      else s.text = n.text;
      n.parentNode.replaceChild(s, n);
    });
  }

  var box = null;
  function render(showDetails) {
    if (box) box.remove();
    var cats = optionalCategories();
    box = document.createElement('div');
    box.className = 'fs-consent';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-label', 'Datenschutz-Einstellungen');
    var html = '<p class="fs-consent__text">Wir möchten optionale Dienste nutzen. Sie entscheiden, welche aktiviert werden. ' +
      'Details in der <a href="' + CONFIG.privacyUrl + '">Datenschutzerklärung</a>.</p>';
    if (showDetails) {
      html += '<div class="fs-consent__cats">';
      Object.keys(CONFIG.categories).forEach(function (k) {
        var c = CONFIG.categories[k];
        if (!c.required && cats.indexOf(k) < 0) return;
        html += '<label><input type="checkbox" data-cat="' + k + '"' + (c.required ? ' checked disabled' : (has(k) ? ' checked' : '')) + '> ' +
          '<strong>' + c.label + '</strong><span>' + (c.description || '') + '</span></label>';
      });
      html += '</div>';
    }
    html += '<div class="fs-consent__actions">' +
      '<button type="button" data-act="necessary">Nur notwendige</button>' +
      (showDetails ? '<button type="button" data-act="save">Auswahl speichern</button>'
                   : '<button type="button" data-act="details">Einstellungen</button>') +
      '<button type="button" data-act="all" class="fs-consent__primary">Alle akzeptieren</button></div>';
    box.innerHTML = html;
    box.addEventListener('click', function (e) {
      var act = e.target.getAttribute && e.target.getAttribute('data-act');
      if (!act) return;
      if (act === 'details') return render(true);
      var choices = {};
      cats.forEach(function (k) {
        if (act === 'all') choices[k] = true;
        else if (act === 'save') { var i = box.querySelector('input[data-cat="' + k + '"]'); choices[k] = !!(i && i.checked); }
        else choices[k] = false;
      });
      write(choices);
      box.remove(); box = null;
    });
    injectCss();
    document.body.appendChild(box);
  }

  function injectCss() {
    if (document.getElementById('fs-consent-css')) return;
    var st = document.createElement('style');
    st.id = 'fs-consent-css';
    st.textContent =
      '.fs-consent{position:fixed;left:16px;right:16px;bottom:calc(16px + env(safe-area-inset-bottom,0px));z-index:100;max-width:560px;margin-left:auto;background:var(--white,#fff);color:var(--ink,#14202E);border:1px solid var(--line,#DFE6EC);border-radius:10px;box-shadow:0 20px 50px -25px rgba(14,42,71,.45);padding:20px;font:14px/1.55 var(--font,sans-serif)}' +
      '.fs-consent a{color:var(--blue,#1D5FA8)}' +
      '.fs-consent__cats{margin:14px 0;display:grid;gap:10px}.fs-consent__cats label{display:grid;grid-template-columns:auto 1fr;gap:2px 10px}.fs-consent__cats span{grid-column:2;color:var(--slate,#4B5A68);font-size:13px}' +
      '.fs-consent__actions{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}.fs-consent__actions button{font:600 14px var(--font,sans-serif);padding:10px 16px;border-radius:6px;border:1px solid var(--line,#DFE6EC);background:transparent;color:inherit;cursor:pointer}' +
      '.fs-consent__actions .fs-consent__primary{background:var(--blue,#1D5FA8);border-color:var(--blue,#1D5FA8);color:#fff}';
    document.head.appendChild(st);
  }

  var api = {
    config: CONFIG,
    has: has,
    get: function () { var o = {}; Object.keys(CONFIG.categories).forEach(function (k) { o[k] = has(k); }); return o; },
    open: function () { if (optionalCategories().length) render(true); },
    onChange: function (fn) { listeners.push(fn); }
  };
  window.FleetSwissConsent = api;

  function init() {
    var cats = optionalCategories();
    // Einstellungs-Links nur zeigen, wenn es etwas einzustellen gibt
    Array.prototype.forEach.call(document.querySelectorAll('[data-consent-open]'), function (el) {
      var li = el.closest('li') || el;
      if (cats.length) { li.hidden = false; el.addEventListener('click', function (e) { e.preventDefault(); api.open(); }); }
    });
    if (!cats.length) return;          // keine optionalen Dienste: kein Banner, kein Storage
    state = read();
    if (state) activate(); else render(false);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
