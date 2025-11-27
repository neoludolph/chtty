# Verwendet das offizielle Python 3.12 Image als Basis
FROM python:3.12
# Setzt das Arbeitsverzeichnis im Container auf /app
WORKDIR /app
# Kopiert die requirements.txt in das Arbeitsverzeichnis
COPY requirements.txt .
# Installiert die in requirements.txt gelisteten Abhängigkeiten
RUN pip install -r requirements.txt
# Kopiert den restlichen Quellcode in das Arbeitsverzeichnis
COPY . . 
# Öffnet Port 8001 für den Zugriff von außen
EXPOSE 8001
# Startet den Uvicorn-Server mit der Anwendung
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--reload" ]