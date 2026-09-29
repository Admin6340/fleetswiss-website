# FleetSwiss – Deployment (Stand 26.09.2026, V1.10 FINAL)

**Produktiver Hosting-Modus: Nine Deploio, App-Typ «Statische Seite».**
Die Website ist rein statisch: 8 HTML-Seiten und lokale Assets. Es gibt keine Rewrites, keine serverseitigen Weiterleitungen und keine Clean URLs. Jede Adresse entspricht genau einer Datei.

## 1. Paketinhalt
- **`public/`** ist das Web-Root. Nur dieser Ordner wird als statische Seite ausgeliefert.
- `DEPLOYMENT.md` und `docs/` sind interne Unterlagen und werden **nicht** veröffentlicht.
- `Dockerfile` und `deploy/nginx/default.conf.template` sind **im aktuellen Produktionsmodus nicht in Gebrauch** (siehe Abschnitt 6).

```
public/
  index.html  produkt.html  funktionen.html  elektronisches-fahrtenbuch.html
  fr/  (6 Seiten, französisch)   en/  (6 Seiten, englisch)
  sicherheit.html  ueber-uns.html  impressum.html  datenschutz.html  agb.html
  favicon.ico  robots.txt  sitemap.xml
  assets/
    og-fleetswiss.jpg                     (1200 × 630, Link-Vorschau)
    brand/fleetswiss-logo.png             (finales Logo, transparent; Header, JSON-LD)
    brand/fleetswiss-logo-white.png       (helle Variante desselben Logos; Footer, Header im Dunkelmodus)
    product/fleetswiss-dashboard.png      (Original-Produktvisual Dashboard; Startseite)
    product/fleetswiss-produktuebersicht.png (Original-Produktcollage; Quelle der Ausschnitte, nicht direkt eingebunden)
    product/*.png                         (verlustfreie Ausschnitte für Produktseite und Mobile)
    product/fahrer-1…6-*.png              (mobile Fahreransicht, Ziel-UI mit Demodaten; offizielles Berglogo retuschiert, «Pause machen» entfernt; Fahrtenbuch-Seite und Startseite)
    fonts/inter-latin-wght-normal.woff2
    fonts/inter-latin-ext-wght-normal.woff2
    fonts/Inter-OFL-LICENSE.txt           (SIL Open Font License 1.1)
    js/consent.js
    icons/favicon-32x32.png
    icons/apple-touch-icon.png            (180 × 180)
```

## 2. URL-Schema (verbindlich)
| Seite | Öffentliche URL = Canonical = Sitemap |
|---|---|
| Startseite | `https://fleetswiss.ch/` (liefert `index.html`) |
| Produkt | `https://fleetswiss.ch/produkt.html` |
| Funktionen | `https://fleetswiss.ch/funktionen.html` |
| Elektronisches Fahrtenbuch (Digital Logbook) | `https://fleetswiss.ch/elektronisches-fahrtenbuch.html` |
| Sicherheit | `https://fleetswiss.ch/sicherheit.html` |
| Über uns | `https://fleetswiss.ch/ueber-uns.html` |
| Impressum | `https://fleetswiss.ch/impressum.html` |
| Datenschutz | `https://fleetswiss.ch/datenschutz.html` |
| AGB | `https://fleetswiss.ch/agb.html` |
| Kontakt | Sprungmarke `https://fleetswiss.ch/#kontakt` (keine eigene Seite) |

- Alle internen Links, Canonicals, `og:url` und `sitemap.xml` verwenden genau diese Adressen.
- Adressen ohne `.html` (z. B. `/produkt`) und `/kontakt` existieren **nicht** und liefern 404. Neue Links immer mit `.html` anlegen.

## 3. Domains
- Kanonische Domain: `https://fleetswiss.ch` (ohne www). Alle Canonicals zeigen darauf.
- `fleetswiss.ch` und `www.fleetswiss.ch` werden als Hosts der statischen Seite eingetragen; DNS gemäss Anleitung von Nine, nur für diese zwei Namen.
- **`app.fleetswiss.ch` ist eine andere Applikation und wird nicht verändert.**
- Eine Weiterleitung `www` → ohne www kann eine statische Seite selbst nicht ausführen. Falls Nine dafür keine Einstellung anbietet, liefern beide Hosts dieselben Inhalte aus; die Canonicals verhindern doppelte Indexierung. Keine Weiterleitungsketten konstruieren.
- HTTPS stellt Nine bereit. Nach dem Aufschalten prüfen, ob `http://` automatisch auf `https://` umgeleitet wird.

## 4. Caching und Sicherheits-Header
- Eigene Header (Caching, Sicherheits-Header) sind nur möglich, soweit Nine sie für statische Seiten anbietet. Die Website funktioniert ohne sie.
- Falls verfügbar, empfohlen:
```
Cache-Control (nur /assets/*): public, max-age=604800
Referrer-Policy: strict-origin-when-cross-origin
X-Content-Type-Options: nosniff
Permissions-Policy: camera=(), microphone=(), geolocation=()
```
- `Strict-Transport-Security` nur **ohne** `includeSubDomains` setzen, da sonst auch `app.fleetswiss.ch` betroffen wäre.
- Eine Content-Security-Policy erst nach separatem Test einführen.

## 5. Kontakt (V1.10)
- Die Website hat **kein Kontaktformular**. Kontakt ausschliesslich über:
  - `mailto:info@fleetswiss.ch`
  - externer Link `https://wa.me/41766070531?text=…` (öffnet WhatsApp erst nach bewusstem Klick, in neuem Fenster, `rel="noopener noreferrer"`)
- Keine Contact-API, kein Resend-Versand, keine WhatsApp-/Meta-Skripte oder -Widgets auf der Website. Beim normalen Seitenaufruf entsteht keine Anfrage an WhatsApp oder Meta.
- Die separat vorbereitete `fleetswiss-contact-api` (eigenes Repository) und die Resend-Domain `send.fleetswiss.ch` sind **nicht** Bestandteil dieses Website-Deployments.

## 5a. Digital Logbook – Onlineabschluss und Vertriebsregel
- Nur das Digital Logbook ist online abschliessbar. Full Fleet Software und Fleet Management Service ausschliesslich «Angebot anfordern» (Kontakt).
- Die Buttons «Jetzt online abschliessen» tragen `data-checkout-plan` (starter, business, business-plus, professional; Hero ohne Paket).
- Checkout-Endpunkt: in `elektronisches-fahrtenbuch.html` die Variable `CHECKOUT_URL` setzen. Die Buttons zeigen dann auf `CHECKOUT_URL?plan=…`, der Hinweis zur Bestellung per E-Mail wird ausgeblendet.
- **Gesetzt (V1.11 FINAL):** `CHECKOUT_URL = https://app.fleetswiss.ch/checkout` (von Codex bestätigt). Die fünf Button-Ziele und das Ausblenden des Hinweises stehen zusätzlich direkt im HTML, damit sie auch ohne JavaScript und für Suchmaschinen korrekt sind. Bei einer Änderung der URL beide Stellen anpassen.
- Solange `CHECKOUT_URL` leer ist, führen die Buttons zu den Vertragsbedingungen mit Hinweis zur Bestellung per E-Mail – es wird keine Bestellung vorgetäuscht.
- Eine Adresse `/digital-logbook` gibt es nicht (Nine «Statische Seite»: keine Clean URLs, keine Weiterleitungen).

## 5b. Mehrsprachigkeit DE / FR / EN (V1.13)
- Deutsch ist Standardsprache (`/`, bestehende URLs unverändert). Französisch unter `/fr/`, Englisch unter `/en/`. Keine automatische Weiterleitung nach Browsersprache.
- Seitenzuordnung (Dateien in `public/`, `/fr/` und `/en/` werden von `fr/index.html` bzw. `en/index.html` ausgeliefert):

| Seite | DE | FR | EN |
|---|---|---|---|
| home | `/` | `/fr/` | `/en/` |
| produkt | `/produkt.html` | `/fr/produit.html` | `/en/product.html` |
| funktionen | `/funktionen.html` | `/fr/fonctions.html` | `/en/features.html` |
| logbook | `/elektronisches-fahrtenbuch.html` | `/fr/carnet-de-route-electronique.html` | `/en/electronic-logbook.html` |
| sicherheit | `/sicherheit.html` | `/fr/securite.html` | `/en/security.html` |
| ueber | `/ueber-uns.html` | `/fr/a-propos.html` | `/en/about.html` |

- Jede Seite trägt `lang` (`de-CH`, `fr-CH`, `en`), eine selbstreferenzierende Canonical, `og:url`, `og:locale` sowie `hreflang` für `de-CH`, `fr-CH`, `en` und `x-default` (= deutsche Seite). Die Sitemap enthält alle Sprachfassungen samt `xhtml:link`-Alternativen.
- Sprachumschalter DE | FR | EN im Desktop-Header und im Mobile-Menü; er führt auf die entsprechende Seite der Zielsprache. Bis einschliesslich 1180 px Breite erscheint in allen Sprachen das Menü-Symbol mit dem Umschalter im Mobile-Menü.
- Rechtstexte (Datenschutz, Impressum, AGB) existieren nur in der freigegebenen deutschen Fassung. FR/EN verlinken sie mit `hreflang="de"` und dem Hinweis, dass die freigegebene Fassung auf Deutsch vorliegt. Auf den Rechtstext-Seiten ist nur DE aktiv; FR/EN sind deaktiviert (kein Link), und ein Hinweis unter dem Header erklärt in allen drei Sprachen, dass die freigegebene Rechtsfassung ausschliesslich auf Deutsch vorliegt.
- Die Fahrer-Screens zeigen die deutsche Oberfläche; FR/EN kennzeichnen sie in der Bildunterschrift als Beispielansicht mit deutscher Oberfläche.
- Checkout-Ziele, Preise, Fahrzeuglimits, Vertragsbedingungen und Vertriebsregeln sind in allen Sprachen identisch; der Checkout erhält keinen Sprachparameter.
- Übersetzungswörterbuch und Generator liegen unter `tools/i18n/` (nicht Teil des Web-Roots, werden nicht ausgeliefert). Änderungen am deutschen Text sind im Wörterbuch für FR/EN nachzuziehen.

## 6. Prüfung vor und nach jedem Deployment
- 0 interne 404: jeder Link, jede Sprungmarke und jede Asset-Referenz zeigt auf eine vorhandene Datei in `public/`.
- Canonical jeder Seite = tatsächlich erreichbare URL, `og:url` = Canonical, alle Sitemap-URLs erreichbar.
- Keine externen Asset-Abhängigkeiten (Schriften, Skripte, Bilder nur von der eigenen Domain).
- Die OG-Tags verweisen absolut auf `https://fleetswiss.ch/assets/og-fleetswiss.jpg`; Link-Vorschauen funktionieren erst auf der Live-Domain.

## 7. Nicht verwendete technische Dateien
`Dockerfile` und `deploy/nginx/default.conf.template` bleiben im Repository, werden im Modus «Statische Seite» aber **nicht verwendet**. Sie stammen aus einer früheren Variante mit Dockerfile-Build und nginx und enthalten deren Clean-URL- und Weiterleitungsregeln. Für einen späteren Wechsel auf Dockerfile/nginx müssten sie an das `.html`-URL-Schema aus Abschnitt 2 angepasst werden.

## Vor Go-live nicht vergessen
- Website erst nach Freigabe der produktiven FleetSwiss-App deployen (verifizierte Datenbankmigration 049, Production-Smoke-Test), da die Checkout-Buttons auf `https://app.fleetswiss.ch/checkout` führen.
- Datenschutzerklärung Ziff. 27/28 (Datenstandort Schweiz) mit dem tatsächlich gewählten Hosting der Plattform abgleichen; Ziff. 34 (Server-Logdaten) mit Nine als Website-Hoster abgleichen
