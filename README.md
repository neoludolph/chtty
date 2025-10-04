# chtty

A chatroom app with a login functionality

---

## Quickstart

### Backend

```bash
pyenv install 3.13.0
pyenv virtualenv 3.13.0 chtty-env
cd backend/
pip install -r requirements.txt -r requirements-dev.txt
```

#### Start FastAPI

```bash
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend/
npm install
npm run dev
```

## Backend setup for devs

### Basic installations

Add Git identity:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Install base tools:

```bash
sudo apt update
sudo apt install build-essential procps curl file git -y
```

Important Python dependencies to avoid compiling issues:

```bash
sudo apt install make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev curl git \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev
```

---

### Set up pyenv and pyenv-virtualenv

#### Requirements

- [pyenv](https://github.com/pyenv/pyenv?tab=readme-ov-file#b-set-up-your-shell-environment-for-pyenv)
- [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)

For the pyenv installation you have to check your profile:

```bash
ls -a ~ | grep profile
```

1. Load Python 3.13.0 in `~/.pyenv/versions/3.13.0`:

```bash
pyenv install 3.13.0
```

2. Create virtual environment `chtty-env` in `~/.pyenv/versions with Python 3.13.0`:

```bash
pyenv virtualenv 3.13.0 chtty-env
```
Activate

```bash
pyenv activate chtty-env
```

3. Navigate to project:

```bash
cd ~/projects/chtty
```

4. Install dependencies:

Core dependencies:

```bash
cd ~/projects/chtty/backend
pip install -r requirements.txt
```

Development dependencies:

```bash
pip install -r requirements-dev.txt
```

---

## Frontend setup for devs

1. Navigate to frontend folder:

```bash
cd ~/projects/chtty/frontend
```

2. Install dependencies:

```bash
npm install
```

---

## Docker installation

Official docs:

[Docker for Linux Ubuntu](https://docs.docker.com/engine/install/ubuntu/)

[Docker for macOS](https://docs.docker.com/desktop/setup/install/mac-install/)

Or follow these steps for Linux:

1. Remove old Docker packages (if any):

```bash
sudo apt remove -y docker.io docker-engine docker-compose docker-compose-v2 podman-docker containerd runc || true
```

2. Set up prerequisites:

```bash
sudo apt install -y ca-certificates curl gnupg lsb-release
```

3. Add Docker’s official GPG key:

```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
```

4. Add the Docker repository:

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

5. Install Docker Engine:

```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

6. Run Docker without `sudo`:

```bash
sudo usermod -aG docker $USER
exec "$SHELL"
```

Powershell:

```powershell
wsl --shutdown
```

Restart WSL now!

7. Verify installation:

```bash
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
