# FleetSwiss – Deployment (Stand 26.09.2026, V1.6)

**Produktiver Hosting-Modus: Nine Deploio, App-Typ «Statische Seite».**
Die Website ist rein statisch: 8 HTML-Seiten und lokale Assets. Es gibt keine Rewrites, keine serverseitigen Weiterleitungen und keine Clean URLs. Jede Adresse entspricht genau einer Datei.

## 1. Paketinhalt
- **`public/`** ist das Web-Root. Nur dieser Ordner wird als statische Seite ausgeliefert.
- `DEPLOYMENT.md` und `docs/` sind interne Unterlagen und werden **nicht** veröffentlicht.
- `Dockerfile` und `deploy/nginx/default.conf.template` sind **im aktuellen Produktionsmodus nicht in Gebrauch** (siehe Abschnitt 6).

```
public/
  index.html  produkt.html  funktionen.html  sicherheit.html
  ueber-uns.html  impressum.html  datenschutz.html  agb.html
  favicon.ico  robots.txt  sitemap.xml
  assets/
    og-fleetswiss.jpg                     (1200 × 630, Link-Vorschau)
    brand/fleetswiss-logo.png             (finales Logo, transparent; Header, JSON-LD)
    brand/fleetswiss-logo-white.png       (helle Variante desselben Logos; Footer, Header im Dunkelmodus)
    product/fleetswiss-dashboard.png      (Original-Produktvisual Dashboard; Startseite)
    product/fleetswiss-produktuebersicht.png (Original-Produktcollage; Quelle der Ausschnitte, nicht direkt eingebunden)
    product/*.png                         (verlustfreie Ausschnitte für Produktseite und Mobile)
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
- Eine Content-Security-Policy erst nach separatem Test einführen (bei Anbindung des Kontaktformulars den Versanddienst berücksichtigen).

## 5. Prüfung vor und nach jedem Deployment
- 0 interne 404: jeder Link, jede Sprungmarke und jede Asset-Referenz zeigt auf eine vorhandene Datei in `public/`.
- Canonical jeder Seite = tatsächlich erreichbare URL, `og:url` = Canonical, alle Sitemap-URLs erreichbar.
- Keine externen Asset-Abhängigkeiten (Schriften, Skripte, Bilder nur von der eigenen Domain).
- Die OG-Tags verweisen absolut auf `https://fleetswiss.ch/assets/og-fleetswiss.jpg`; Link-Vorschauen funktionieren erst auf der Live-Domain.

## 6. Nicht verwendete technische Dateien
`Dockerfile` und `deploy/nginx/default.conf.template` bleiben im Repository, werden im Modus «Statische Seite» aber **nicht verwendet**. Sie stammen aus einer früheren Variante mit Dockerfile-Build und nginx und enthalten deren Clean-URL- und Weiterleitungsregeln. Für einen späteren Wechsel auf Dockerfile/nginx müssten sie an das `.html`-URL-Schema aus Abschnitt 2 angepasst werden.

## Vor Go-live nicht vergessen
- Kontaktformular an echten Versand (E-Mail/CRM) anbinden, dann Erfolgsmeldung aktivieren
- Datenschutzerklärung Ziff. 27/28 (Datenstandort Schweiz) mit dem tatsächlich gewählten Hosting der Plattform abgleichen; Ziff. 34 (Server-Logdaten) mit Nine als Website-Hoster abgleichen
