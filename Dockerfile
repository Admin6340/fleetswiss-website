# FleetSwiss Website – statische Auslieferung auf Nine Deploio (Dockerfile Build)
# Liefert ausschliesslich den Inhalt von public/ aus. docs/ und DEPLOYMENT.md
# werden nicht in das Image kopiert und sind damit nicht öffentlich erreichbar.

FROM nginxinc/nginx-unprivileged:stable-alpine

# Port, auf dem nginx lauscht. Standard 8080 = Deploio-Standardport der App.
# Wird zur Laufzeit eine Umgebungsvariable PORT gesetzt, gilt deren Wert.
ENV PORT=8080

# Das Image ersetzt beim Start ${PORT} in dieser Vorlage (envsubst) und
# schreibt das Ergebnis nach /etc/nginx/conf.d/default.conf.
COPY deploy/nginx/default.conf.template /etc/nginx/templates/default.conf.template

# Nur die Website-Dateien, in ein eigenes Verzeichnis (keine Standard-Seiten des Images)
COPY public/ /srv/www/

EXPOSE 8080
