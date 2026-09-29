# -*- coding: utf-8 -*-
"""FleetSwiss V1.13: erzeugt DE/FR/EN aus der geprüften V1.12 FINAL (Quelle bleibt unverändert)."""
import re, html, json, os, shutil, sys
sys.path.insert(0, '/home/claude/i18n')
from tr import T, KEEP

SRC = '/tmp/v112chk/fleetswiss-deploy'          # V1.12 FINAL, unverändert
OUT = '/home/claude/deploy/fleetswiss-deploy'   # Arbeitsstand V1.13
BASE = 'https://fleetswiss.ch'
LANGS = ['de', 'fr', 'en']
HREFLANG = {'de': 'de-CH', 'fr': 'fr-CH', 'en': 'en'}
OGLOC = {'de': 'de_CH', 'fr': 'fr_CH', 'en': 'en_GB'}
IDX = {'fr': 0, 'en': 1}

# Seitenzuordnung: Schlüssel -> URL je Sprache (Pfad ohne Domain)
PAGES = {
  'home':       {'src': 'index.html',                      'de': '/',                                   'fr': '/fr/',                                  'en': '/en/'},
  'produkt':    {'src': 'produkt.html',                    'de': '/produkt.html',                       'fr': '/fr/produit.html',                      'en': '/en/product.html'},
  'funktionen': {'src': 'funktionen.html',                 'de': '/funktionen.html',                    'fr': '/fr/fonctions.html',                    'en': '/en/features.html'},
  'logbook':    {'src': 'elektronisches-fahrtenbuch.html', 'de': '/elektronisches-fahrtenbuch.html',    'fr': '/fr/carnet-de-route-electronique.html', 'en': '/en/electronic-logbook.html'},
  'sicherheit': {'src': 'sicherheit.html',                 'de': '/sicherheit.html',                    'fr': '/fr/securite.html',                     'en': '/en/security.html'},
  'ueber':      {'src': 'ueber-uns.html',                  'de': '/ueber-uns.html',                     'fr': '/fr/a-propos.html',                     'en': '/en/about.html'},
}
LEGAL = ['impressum.html', 'datenschutz.html', 'agb.html']      # nur Deutsch (freigegebene Fassung)
DE2KEY = {v['de']: k for k, v in PAGES.items()}
DE2KEY['/index.html'] = 'home'

def file_for(url):
    if url == '/': return 'index.html'
    return url.strip('/') + '/index.html' if url.endswith('/') else url.strip('/')

def tr(s, L):
    if L == 'de': return s
    key = ' '.join(s.split())
    if key in T: return T[key][IDX[L]]
    return s

# ---------------- Sprachumschalter ----------------
LABEL = {'de': 'Sprache wählen', 'fr': 'Choisir la langue', 'en': 'Choose language'}
OFF_TITLE = {'fr': 'Version juridique disponible uniquement en allemand', 'en': 'Legal text available in German only'}
def lang_switch(key, L, cls, legal=None):
    parts = []
    for tl in LANGS:
        if legal and tl != 'de':
            parts.append(f'<span class="lang-off" lang="{HREFLANG[tl]}" aria-disabled="true" title="{OFF_TITLE[tl]}">{tl.upper()}</span>')
            continue
        url = PAGES[key][tl] if key else '/' + legal
        cur = ' aria-current="page"' if tl == L else ''
        parts.append(f'<a href="{url}" hreflang="{HREFLANG[tl]}" lang="{HREFLANG[tl]}"{cur}>{tl.upper()}</a>')
    return (f'<div class="lang-switch {cls}" role="group" aria-label="{LABEL[L]}">'
            + '<span aria-hidden="true">|</span>'.join(parts) + '</div>')

I18N_CSS = '''<style id="i18n-lang">
  /* V1.13 Sprachumschalter DE | FR | EN */
  .lang-switch { display: flex; align-items: center; gap: 2px; font-size: 13px; font-weight: 600; color: var(--slate-light); white-space: nowrap; }
  .lang-switch span { padding: 0 1px; }
  .lang-switch a { padding: 4px 5px; border-radius: 4px; color: var(--slate); text-decoration: none; line-height: 1.2; }
  .lang-switch a:hover, .lang-switch a:focus-visible { color: var(--blue); }
  .lang-switch a[aria-current="page"] { color: var(--navy); text-decoration: underline; text-underline-offset: 4px; }
  nav.primary .lang-switch { margin-left: -12px; }
  nav.primary .lang-switch a { font-size: 13px; font-weight: 600; }
  .mobile-menu .lang-switch { order: 99; justify-content: flex-start; gap: 6px; padding: 16px 0 2px; font-size: 15px; }
  .mobile-menu .lang-switch a { padding: 8px 12px; border: 1px solid var(--line); border-radius: 6px; font-weight: 600; }
  .mobile-menu .lang-switch a[aria-current="page"] { border-color: var(--navy); }
  .mobile-menu .lang-switch span { display: none; }
  :root[data-theme="dark"] .lang-switch a { color: #C9D6E3; }
  :root[data-theme="dark"] .lang-switch a[aria-current="page"] { color: #fff; }
  .legal-lang-note { margin-top: 18px; font-size: 12.5px; color: #93A9BE; }
  .lang-switch .lang-off { padding: 4px 5px; color: var(--slate-light); opacity: .55; cursor: not-allowed; }
  .mobile-menu .lang-switch .lang-off { display: inline-block; padding: 8px 12px; border: 1px dashed var(--line); border-radius: 6px; font-weight: 600; }
  .legal-lang-banner { background: var(--paper, #F5F7FA); border-bottom: 1px solid var(--line); font-size: 13px; line-height: 1.5; color: var(--slate); }
  .legal-lang-banner .wrap { padding-top: 9px; padding-bottom: 9px; }
  .legal-lang-banner span[lang="de-CH"] { color: var(--navy); font-weight: 600; }
  @media (max-width: __BP__px) {
    nav.primary { display: none; }
    .menu-toggle { display: block; }
    header.site .nav-right { display: flex; }
  }
</style>
'''
BREAKPOINT = int(os.environ.get('I18N_BP', '1180'))

LEGAL_BANNER = ('<div class="legal-lang-banner" role="note"><div class="wrap">'
  '<span lang="de-CH">Diese Rechtsfassung liegt derzeit ausschliesslich auf Deutsch vor.</span> '
  '<span lang="fr-CH">Version juridique approuvée disponible uniquement en allemand.</span> '
  '<span lang="en">The approved legal text is currently available in German only.</span></div></div>')
LEGAL_NOTE = {'fr': 'Les documents juridiques (protection des données, mentions légales, CGV) sont actuellement disponibles en allemand, dans leur version approuvée.',
              'en': 'The legal documents (privacy policy, legal notice, GTC) are currently available in German in their approved version.'}
WA = {'de': None,
      'fr': 'Bonjour, je m\'intéresse à FleetSwiss et j\'aimerais en savoir plus.',
      'en': 'Hello, I am interested in FleetSwiss and would like to learn more.'}
MAIL_SUBJ = {'fr': 'Commande FleetSwiss Digital Logbook', 'en': 'Order FleetSwiss Digital Logbook'}
TERMS_P = {
 'fr': '<p>Les <a href="/agb.html" hreflang="de">CGV</a> et la <a href="/datenschutz.html" hreflang="de">déclaration de protection des données</a> s\'appliquent (la version actuellement approuvée est disponible en allemand).</p>',
 'en': '<p>The <a href="/agb.html" hreflang="de">General Terms and Conditions</a> and the <a href="/datenschutz.html" hreflang="de">Privacy Policy</a> apply (the currently approved version is available in German).</p>'}

from urllib.parse import quote

def head_block(key, L):
    out = []
    for tl in LANGS:
        out.append(f'<link rel="alternate" hreflang="{HREFLANG[tl]}" href="{BASE}{PAGES[key][tl]}">')
    out.append(f'<link rel="alternate" hreflang="x-default" href="{BASE}{PAGES[key]["de"]}">')
    for tl in LANGS:
        if tl != L: out.append(f'<meta property="og:locale:alternate" content="{OGLOC[tl]}">')
    return '\n'.join(out)

def remap_href(url, L):
    """Interne Links in die Zielsprache abbilden; Rechtstexte bleiben deutsch."""
    if L == 'de' or not url.startswith('/') or url.startswith('/assets/') or url.startswith('//'):
        return url, False
    path, frag = (url.split('#', 1) + [''])[:2]
    frag = ('#' + frag) if '#' in url else ''
    if path in ('', '/') or path == '/index.html':
        return PAGES['home'][L] + frag, False
    if path in DE2KEY:
        return PAGES[DE2KEY[path]][L] + frag, False
    if path.lstrip('/') in LEGAL:
        return url, True
    return url, False

def translate_body(s, L):
    parts = re.split(r'(<script\b.*?</script>|<style\b.*?</style>)', s, flags=re.S)
    for i, p in enumerate(parts):
        if p.startswith('<style'):
            continue
        if p.startswith('<script'):
            if p.startswith('<script type="application/ld+json">'):
                parts[i] = translate_jsonld(p, L)
            continue
        # Textknoten
        def txt(m):
            raw = m.group(1)
            t = ' '.join(html.unescape(raw).split())
            if not t or not re.search(r'[A-Za-zÄÖÜäöü]', t): return m.group(0)
            new = tr(t, L)
            if new == t: return m.group(0)
            lead = raw[:len(raw) - len(raw.lstrip())]; trail = raw[len(raw.rstrip()):]
            return '>' + lead + html.escape(new, quote=False) + trail + '<'
        p = re.sub(r'>([^<]+)<', txt, p)
        # Attribute
        def tag(m):
            t = m.group(0)
            def att(a):
                k, v = a.group(1), a.group(2)
                vv = html.unescape(v)
                if k in ('alt', 'aria-label', 'title', 'placeholder', 'content'):
                    nv = tr(vv, L)
                    if nv != vv: return f'{k}="{html.escape(nv, quote=True)}"'
                return a.group(0)
            t = re.sub(r'\b(alt|aria-label|title|placeholder|content)="([^"]*)"', att, t)
            # hrefs
            def hr(a):
                new, legal = remap_href(a.group(1), L)
                return f'href="{new}"' + (' hreflang="de"' if legal and 'hreflang=' not in t else '')
            t = re.sub(r'href="([^"]*)"', hr, t)
            return t
        p = re.sub(r'<[a-zA-Z][^>]*>', tag, p)
        parts[i] = p
    return ''.join(parts)

def translate_jsonld(block, L):
    j = re.search(r'<script type="application/ld\+json">(.*?)</script>', block, re.S).group(1)
    data = json.loads(j)
    def walk(o):
        if isinstance(o, dict):
            for k, v in list(o.items()):
                if isinstance(v, str):
                    if k in ('name', 'description', 'alternateName'): o[k] = tr(v, L)
                    elif k in ('url', 'item') and v.startswith(BASE):
                        path = v[len(BASE):] or '/'
                        if path in DE2KEY and not (o.get('@type') == 'Organization'):
                            o[k] = BASE + PAGES[DE2KEY[path]][L]
                    elif k == 'inLanguage': o[k] = HREFLANG[L]
                else: walk(v)
        elif isinstance(o, list):
            for x in o: walk(x)
    walk(data)
    lead = block[:block.find('>') + 1]
    return lead + '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n</script>'

def common_header(s, key, L):
    """Alten (versteckten) Umschalter entfernen, neuen in Navigation und Mobile-Menü einsetzen."""
    s2 = re.sub(r'\s*<div class="lang-switch" role="group" aria-label="Sprache wählen" hidden>.*?</div>', '', s, count=1, flags=re.S)
    assert s2 != s, 'alter Umschalter nicht gefunden'
    s = s2
    a = '<a href="https://app.fleetswiss.ch" class="nav-login">Login</a>\n    </nav>'
    assert s.count(a) == 1
    s = s.replace(a, '<a href="https://app.fleetswiss.ch" class="nav-login">Login</a>\n      <!--LANGSWITCH:lang-desktop-->\n    </nav>')
    b = '<a href="https://app.fleetswiss.ch" class="btn btn-outline mobile-login">Login</a>\n  </div>'
    assert s.count(b) == 1
    s = s.replace(b, '<a href="https://app.fleetswiss.ch" class="btn btn-outline mobile-login">Login</a>\n    <!--LANGSWITCH:lang-mobile-->\n  </div>')
    s = s.replace('</head>', I18N_CSS.replace('__BP__', str(BREAKPOINT)) + '</head>', 1)
    return s

def place_switch(s, key, L, legal=None):
    for cls in ('lang-desktop', 'lang-mobile'):
        m = f'<!--LANGSWITCH:{cls}-->'
        assert s.count(m) == 1, m
        s = s.replace(m, lang_switch(key, L, cls, legal))
    return s

def build_page(key, L):
    src = open(os.path.join(SRC, 'public', PAGES[key]['src']), encoding='utf-8').read()
    s = common_header(src, key, L)
    s = re.sub(r'<html lang="[^"]*">', f'<html lang="{HREFLANG[L]}">', s, count=1)
    url = BASE + PAGES[key][L]
    if L != 'de':
        # Sonderfälle vor der Übersetzung
        if key == 'logbook':
            old = '<p>Es gelten die <a href="/agb.html">AGB</a> und die <a href="/datenschutz.html">Datenschutzerklärung</a>.</p>'
            assert s.count(old) == 1; s = s.replace(old, TERMS_P[L])
            s = s.replace('subject=Bestellung%20FleetSwiss%20Digital%20Logbook', 'subject=' + quote(MAIL_SUBJ[L]))
        s = re.sub(r'(https://wa\.me/41766070531\?text=)[^"]+', lambda m: m.group(1) + quote(WA[L]), s)
        s = translate_body(s, L)
        # Hinweis Rechtstexte im Footer
        fb = '<div class="footer-bottom">'
        assert s.count(fb) == 1
        s = s.replace(fb, f'<p class="legal-lang-note">{LEGAL_NOTE[L]}</p>\n    ' + fb)
    # Head: canonical, og:url, og:locale, hreflang
    s = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{url}">', s, count=1)
    s = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{url}">', s, count=1)
    s = re.sub(r'<meta property="og:locale" content="[^"]*">', f'<meta property="og:locale" content="{OGLOC[L]}">', s, count=1)
    s = s.replace(f'<link rel="canonical" href="{url}">', f'<link rel="canonical" href="{url}">\n' + head_block(key, L), 1)
    return place_switch(s, key, L)

def build_legal(fname):
    s = open(os.path.join(SRC, 'public', fname), encoding='utf-8').read()
    s = common_header(s, None, 'de')          # FR/EN führen auf die jeweilige Startseite (keine übersetzte Rechtsfassung)
    s = re.sub(r'<html lang="[^"]*">', '<html lang="de-CH">', s, count=1)
    h = '</header>'
    assert s.count(h) == 1
    s = s.replace(h, h + '\n' + LEGAL_BANNER, 1)
    return place_switch(s, None, 'de', legal=fname)

def sitemap():
    lm_new = '2026-09-29'
    rows = []
    def alt(key):
        return ''.join(f'<xhtml:link rel="alternate" hreflang="{HREFLANG[t]}" href="{BASE}{PAGES[key][t]}"/>' for t in LANGS) + \
               f'<xhtml:link rel="alternate" hreflang="x-default" href="{BASE}{PAGES[key]["de"]}"/>'
    for L in LANGS:
        for key in PAGES:
            rows.append(f'  <url><loc>{BASE}{PAGES[key][L]}</loc><lastmod>{lm_new}</lastmod>{alt(key)}</url>')
    for f in LEGAL:
        rows.append(f'  <url><loc>{BASE}/{f}</loc><lastmod>2026-09-28</lastmod></url>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + '\n'.join(rows) + '\n</urlset>\n')

if __name__ == '__main__':
    # Arbeitsstand frisch aus V1.12 FINAL aufbauen
    if os.path.exists(OUT): shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT)
    n = 0
    for key in PAGES:
        for L in LANGS:
            p = os.path.join(OUT, 'public', file_for(PAGES[key][L]))
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, 'w', encoding='utf-8').write(build_page(key, L)); n += 1
    for f in LEGAL:
        open(os.path.join(OUT, 'public', f), 'w', encoding='utf-8').write(build_legal(f)); n += 1
    open(os.path.join(OUT, 'public', 'sitemap.xml'), 'w', encoding='utf-8').write(sitemap())
    print(f'{n} Seiten erzeugt, Breakpoint {BREAKPOINT}px')

# ---------------- DEPLOYMENT.md (Sprachstruktur) ----------------
def update_deployment():
    p = os.path.join(OUT, 'DEPLOYMENT.md'); s = open(p, encoding='utf-8').read()
    a = '## 6. Prüfung vor und nach jedem Deployment'
    assert s.count(a) == 1
    rows = '\n'.join(f"| {k} | `{v['de']}` | `{v['fr']}` | `{v['en']}` |" for k, v in PAGES.items())
    sec = f'''## 5b. Mehrsprachigkeit DE / FR / EN (V1.13)
- Deutsch ist Standardsprache (`/`, bestehende URLs unverändert). Französisch unter `/fr/`, Englisch unter `/en/`. Keine automatische Weiterleitung nach Browsersprache.
- Seitenzuordnung (Dateien in `public/`, `/fr/` und `/en/` werden von `fr/index.html` bzw. `en/index.html` ausgeliefert):

| Seite | DE | FR | EN |
|---|---|---|---|
{rows}

- Jede Seite trägt `lang` (`de-CH`, `fr-CH`, `en`), eine selbstreferenzierende Canonical, `og:url`, `og:locale` sowie `hreflang` für `de-CH`, `fr-CH`, `en` und `x-default` (= deutsche Seite). Die Sitemap enthält alle Sprachfassungen samt `xhtml:link`-Alternativen.
- Sprachumschalter DE | FR | EN im Desktop-Header und im Mobile-Menü; er führt auf die entsprechende Seite der Zielsprache. Bis einschliesslich 1180 px Breite erscheint in allen Sprachen das Menü-Symbol mit dem Umschalter im Mobile-Menü.
- Rechtstexte (Datenschutz, Impressum, AGB) existieren nur in der freigegebenen deutschen Fassung. FR/EN verlinken sie mit `hreflang="de"` und dem Hinweis, dass die freigegebene Fassung auf Deutsch vorliegt. Auf den Rechtstext-Seiten ist nur DE aktiv; FR/EN sind deaktiviert (kein Link), und ein Hinweis unter dem Header erklärt in allen drei Sprachen, dass die freigegebene Rechtsfassung ausschliesslich auf Deutsch vorliegt.
- Die Fahrer-Screens zeigen die deutsche Oberfläche; FR/EN kennzeichnen sie in der Bildunterschrift als Beispielansicht mit deutscher Oberfläche.
- Checkout-Ziele, Preise, Fahrzeuglimits, Vertragsbedingungen und Vertriebsregeln sind in allen Sprachen identisch; der Checkout erhält keinen Sprachparameter.
- Übersetzungswörterbuch und Generator liegen unter `tools/i18n/` (nicht Teil des Web-Roots, werden nicht ausgeliefert). Änderungen am deutschen Text sind im Wörterbuch für FR/EN nachzuziehen.

'''
    s = s.replace(a, sec + a)
    b = '## Vor Go-live nicht vergessen'
    if b in s and '049' not in s:
        s = s.replace(b, b + '\n- Website erst nach Freigabe der produktiven FleetSwiss-App deployen (verifizierte Datenbankmigration 049, Production-Smoke-Test), da die Checkout-Buttons auf `https://app.fleetswiss.ch/checkout` führen.', 1)
    s = s.replace('  index.html  produkt.html  funktionen.html  elektronisches-fahrtenbuch.html\n',
                  '  index.html  produkt.html  funktionen.html  elektronisches-fahrtenbuch.html\n  fr/  (6 Seiten, französisch)   en/  (6 Seiten, englisch)\n', 1)
    open(p, 'w', encoding='utf-8').write(s)

if __name__ == '__main__':
    update_deployment(); print('DEPLOYMENT.md ergänzt')
