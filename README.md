# chtty

Chatroom-Anwendung mit passwortgeschützten Räumen – Backend in FastAPI, Frontend in Vanilla JavaScript.

---

## Quickstart

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Backend-Setup für Entwickler

### Empfohlene Basiswerkzeuge

```bash
git config --global user.name "Dein Name"
git config --global user.email "deine.mail@example.com"
sudo apt update
sudo apt install -y build-essential procps curl file git
sudo apt install -y make libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
    libsqlite3-dev libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

### Python-Umgebung (venv)

```bash
cd ~/projects/chtty/backend
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Mit `deactivate` verlässt du die virtuelle Umgebung wieder.

---

## Frontend-Setup für Entwickler:innen

- Installiere [Node.js](https://nodejs.org/en/download) oder nutze [nvm](https://github.com/nvm-sh/nvm).
- Führe im Ordner `frontend/` den Befehl `npm install` aus.
- Starte den lokalen Dev-Server mit `npm run dev`.

---

## Docker-Installation

Offizielle Dokumentation:

- [Docker für Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Docker für macOS](https://docs.docker.com/desktop/setup/install/mac-install/)

Zusammenfassung für Ubuntu:

```bash
sudo apt remove -y docker.io docker-engine docker-compose docker-compose-v2 podman-docker containerd runc || true
sudo apt install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER && exec \"$SHELL\"
wsl --shutdown   # PowerShell, nur falls WSL genutzt wird
docker --version
docker run hello-world
```

---

## Docker-Container bauen und nutzen

```bash
docker compose up --build -d
docker compose logs -f
docker compose down
```
