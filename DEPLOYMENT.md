# FleetSwiss – Deployment-Anforderungen (Stand 22.09.2026)

Die Website ist statisch (8 HTML-Seiten, Bilder eingebettet). Interne Links verwenden Clean URLs ohne `.html`. Folgende Regeln müssen beim Hosting eingerichtet sein, sonst funktionieren die Links nicht.

## 0. Paketinhalt
- **`public/`** ist das Web-Root. Nur dieser Ordner wird auf den Server hochgeladen.
- `DEPLOYMENT.md` und `docs/` sind interne Unterlagen und werden **nicht** veröffentlicht.

```
public/
  index.html  produkt.html  funktionen.html  sicherheit.html
  ueber-uns.html  impressum.html  datenschutz.html  agb.html
  favicon.ico  robots.txt  sitemap.xml
  assets/
    og-fleetswiss.jpg                     (1200 × 630, Link-Vorschau)
    brand/fleetswiss-logo.png             (finales Logo, transparent; Header, JSON-LD)
    brand/fleetswiss-logo-white.png       (helle Variante desselben Logos; Footer, Header im Dunkelmodus)
    fonts/inter-latin-wght-normal.woff2
    fonts/inter-latin-ext-wght-normal.woff2
    fonts/Inter-OFL-LICENSE.txt           (SIL Open Font License 1.1)
    js/consent.js
    icons/favicon-32x32.png
    icons/apple-touch-icon.png            (180 × 180)
```

## 1. Kanonische Domain
- Kanonisch: `https://fleetswiss.ch` (ohne www)
- `https://www.fleetswiss.ch/*` → **301/308** auf `https://fleetswiss.ch/*` (Pfad und Query beibehalten)
- `http://` → **301/308** auf `https://`

## 2. Clean URLs (interne Rewrites, keine Weiterleitung)
| Aufgerufene URL | Ausgelieferte Datei |
|---|---|
| `/` | `index.html` |
| `/produkt` | `produkt.html` |
| `/funktionen` | `funktionen.html` |
| `/sicherheit` | `sicherheit.html` |
| `/ueber-uns` | `ueber-uns.html` |
| `/impressum` | `impressum.html` |
| `/datenschutz` | `datenschutz.html` |
| `/agb` | `agb.html` |

## 3. Weiterleitungen
- `/kontakt` → **301** auf `/#kontakt` (Kontaktbereich der Startseite)
- `/*.html` → **301** auf die Clean URL (z. B. `/produkt.html` → `/produkt`, `/index.html` → `/`)
- Keine Trailing-Slash-Varianten: `/produkt/` → **301** auf `/produkt`

## 4. Weitere Dateien im Web-Root
- Den gesamten Ordner `public/` unverändert ausliefern, inklusive `/assets/` (Schriften, `consent.js`, Logo, Icons, OG-Bild) und `/favicon.ico`
- `robots.txt`, `sitemap.xml` (URLs bereits auf `https://fleetswiss.ch`)
- Die OG-Tags verweisen absolut auf `https://fleetswiss.ch/assets/og-fleetswiss.jpg`; Link-Vorschauen funktionieren erst auf der Live-Domain
- Empfohlenes Caching: `/assets/*` → `Cache-Control: public, max-age=604800` (bei unveränderten Dateinamen keine `immutable`-Angabe verwenden)

## Beispiel Netlify / Cloudflare Pages (`_redirects`)
```
https://www.fleetswiss.ch/*  https://fleetswiss.ch/:splat  301!
/kontakt        /#kontakt          301
/index.html     /                  301
/produkt.html   /produkt           301
/funktionen.html /funktionen       301
/sicherheit.html /sicherheit       301
/ueber-uns.html /ueber-uns         301
/impressum.html /impressum         301
/datenschutz.html /datenschutz     301
/agb.html       /agb               301
```
(Netlify und Cloudflare Pages liefern `/produkt` automatisch aus `produkt.html` aus.)

## Beispiel Apache (`.htaccess`)
```
RewriteEngine On
RewriteCond %{HTTP_HOST} ^www\.fleetswiss\.ch$ [NC]
RewriteRule ^(.*)$ https://fleetswiss.ch/$1 [R=301,L]
RewriteCond %{HTTPS} off
RewriteRule ^(.*)$ https://fleetswiss.ch/$1 [R=301,L]
RewriteRule ^kontakt/?$ /#kontakt [R=301,NE,L]
RewriteCond %{THE_REQUEST} \s/+(.+?)\.html[\s?] [NC]
RewriteRule ^ /%1 [R=301,L]
RewriteCond %{REQUEST_FILENAME}.html -f
RewriteRule ^(.+?)/?$ $1.html [L]
```

## Beispiel nginx
```
server { server_name www.fleetswiss.ch; return 301 https://fleetswiss.ch$request_uri; }
server {
  server_name fleetswiss.ch;
  location = /kontakt { return 301 /#kontakt; }
  location ~ ^/(.+)\.html$ { return 301 /$1; }
  location / { try_files $uri $uri.html $uri/ =404; }
}
```

## 5. Empfohlene Sicherheits-Header
Die Website lädt nur Ressourcen der eigenen Domain. Empfohlen (bei Anbindung des Kontaktformulars `connect-src`/`form-action` um den Versanddienst ergänzen):
```
Content-Security-Policy: default-src 'self'; img-src 'self' data:; font-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; connect-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'
Strict-Transport-Security: max-age=31536000; includeSubDomains
Referrer-Policy: strict-origin-when-cross-origin
X-Content-Type-Options: nosniff
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

## Vor Go-live nicht vergessen
- Kontaktformular an echten Versand (E-Mail/CRM) anbinden, dann Erfolgsmeldung aktivieren
- Datenschutzerklärung Ziff. 27/28 (Datenstandort Schweiz) mit dem tatsächlich gewählten Hosting der Plattform abgleichen; Hosting-Anbieter der Website festlegen (Ziff. 34 Server-Logdaten)
