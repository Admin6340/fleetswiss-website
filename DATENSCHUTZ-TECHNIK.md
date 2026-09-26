# FleetSwiss Website – Datenschutz-Technik (Stand 26.09.2026, V1.10 FINAL)

## Externe Verbindungen
Geprüft per Browser-Audit auf allen 8 Seiten.
- **Vorher:** `fonts.googleapis.com` und `fonts.gstatic.com` (Google Fonts) auf jeder Seite
- **Jetzt:** keine externen Domains beim Seitenaufruf. Geladen werden nur eigene Ressourcen der Domain (HTML, lokale Schrift, `consent.js`, Bilder unter `/assets/`)
- Keine Analytics-, Marketing-, Tracking- oder Social-Pixel, keine iFrames, keine Karten oder Videos
- Nicht-geladene Referenzen: OG-Tags (nur für Link-Vorschauen), JSON-LD-Kontext (`schema.org`, wird nicht aufgerufen)
- Externe Links, die erst nach bewusstem Klick geöffnet werden: `https://wa.me/41766070531` (WhatsApp, neues Fenster, ohne Referrer) und `https://app.fleetswiss.ch` (Login)
- Kein Kontaktformular, keine Contact-API, kein Resend-Versand für Website-Anfragen; Kontakt per `mailto:` und WhatsApp-Link

## Cookies und Browser-Speicher
- **Cookies:** keine
- **LocalStorage / SessionStorage:** keine Einträge
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
