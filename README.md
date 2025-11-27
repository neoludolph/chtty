# chtty

Chatroom application with login-protected rooms, built with FastAPI (backend) and a small vanilla JS frontend.

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

## Backend setup for devs

### Recommended tooling

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
sudo apt update
sudo apt install -y build-essential procps curl file git
sudo apt install -y make libssl-dev zlib1g-dev libbz2-dev libreadline-dev \
    libsqlite3-dev libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

### Python environment (venv)

```bash
cd ~/projects/chtty/backend
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Deactivate with `deactivate` once you finish hacking.

---

## Frontend setup for devs

- Install [Node.js](https://nodejs.org/en/download) (or use [nvm](https://github.com/nvm-sh/nvm)).
- From `frontend/`, run `npm install`.
- Start the local dev server via `npm run dev`.

---

## Docker installation

Official docs:

- [Docker for Linux Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
- [Docker for macOS](https://docs.docker.com/desktop/setup/install/mac-install/)

Summary for Ubuntu:

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
sudo usermod -aG docker $USER && exec "$SHELL"
wsl --shutdown   # PowerShell, only if using WSL
docker --version
docker run hello-world
```

---

## Build and use Docker containers

```bash
docker compose up --build -d
docker compose logs -f
docker compose down
```
