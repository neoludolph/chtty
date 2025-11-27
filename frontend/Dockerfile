# Verwendet das offizielle Node.js 22 Image als Basis
FROM node:22
# Setzt das Arbeitsverzeichnis im Container auf /app
WORKDIR /app
# Kopiert package.json und package-lock.json in das Arbeitsverzeichnis
COPY package.json package-lock.json /app/
# Installiert die Node.js-Abhängigkeiten
RUN npm install
# Kopiert den restlichen Quellcode in das Arbeitsverzeichnis
COPY . . 
# Öffnet Port 5174 für den Zugriff von außen
EXPOSE 5174
# Startet den Entwicklungsserver und macht ihn extern verfügbar
CMD [ "npm", "run", "dev", "--", "--host", "0.0.0.0" ]