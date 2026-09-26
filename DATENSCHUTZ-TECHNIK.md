# FleetSwiss Website – Datenschutz-Technik (Stand 22.09.2026)

## Externe Verbindungen
Geprüft per Browser-Audit auf allen 7 Seiten, inkl. Absenden des Kontaktformulars.
- **Vorher:** `fonts.googleapis.com` und `fonts.gstatic.com` (Google Fonts) auf jeder Seite
- **Jetzt:** keine externen Domains. Pro Seitenaufruf nur eigene Ressourcen: HTML, `inter-latin-wght-normal.woff2`, `consent.js` (Bilder sind im HTML eingebettet)
- Keine Analytics-, Marketing-, Tracking- oder Social-Pixel, keine iFrames, keine Karten oder Videos
- Nicht-geladene Referenzen: OG-Tags (nur für Link-Vorschauen), JSON-LD-Kontext (`schema.org`, wird nicht aufgerufen)

## Cookies und Browser-Speicher
- **Cookies:** keine
- **LocalStorage / SessionStorage:** keine Einträge
- **Kontaktformular:** speichert nichts, sendet aktuell nichts (Transport nicht angeschlossen)
- **Hosting:** Der Webserver darf keine Cookies setzen (beim Hosting prüfen; z. B. keine Session- oder Load-Balancer-Cookies)

## Consent-Architektur (`/assets/js/consent.js`)
- Kategorie `necessary` ist immer aktiv; optionale Kategorien (z. B. `analytics`, `marketing`) sind vorbereitet, aber leer
- Solange keine optionale Kategorie Dienste enthält: **kein Banner, kein Storage-Zugriff**, Link «Datenschutz-Einstellungen» im Footer bleibt ausgeblendet
- Sobald ein Dienst eingetragen ist: Banner mit «Nur notwendige», «Einstellungen», «Alle akzeptieren»; Entscheidung wird unter `fs_consent` im LocalStorage gespeichert (technisch notwendig, enthält nur Version, Zeitpunkt und Auswahl)
- Drittanbieter-Skripte werden nur blockiert eingebunden (`<script type="text/plain" data-consent="analytics" data-src="…">`) und erst nach Einwilligung ausgeführt
- Getestet: ohne Kategorie kein Banner; mit Testkategorie Banner sichtbar, Skript vor Einwilligung blockiert, nach «Nur notwendige» weiterhin blockiert, nach «Alle akzeptieren» ausgeführt
- Bei neuen Diensten: `CONFIG.version` erhöhen, Datenschutzerklärung nachführen, CSP-Header ergänzen

## Schriften
- Inter (Variable Font, SIL Open Font License 1.1), lokal unter `/assets/fonts/`, Lizenz liegt bei
