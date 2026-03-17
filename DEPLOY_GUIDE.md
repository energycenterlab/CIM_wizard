# Deployment Guide: Stop Docker, Copy Edited Code, Run on Server

This guide covers deploying the updated CIM Wizard backend (with scenario endpoints) to the server using the provided bash scripts.

---

## Prerequisites

- `sshpass` installed locally: `sudo apt install sshpass`
- SSH access to the server
- Server credentials configured in `deploy-to-server.sh`

---

## Step 1: Stop the Dockerized Version on the Server

SSH into the server and stop all services:

```bash
ssh eclabuser@130.192.238.11
cd ~/cim
./run-docker.sh down
```

Or stop individually:

```bash
./run-docker.sh backend-down   # Stop backend only
./run-docker.sh db-down        # Stop database only (use after backend if needed)
```

---

## Step 2: Copy the Edited Version to the Server

From your local machine (inside the CIM_wizard project root):

```bash
./deploy-to-server.sh
```

This copies:

- `cim-database/` (excluding large backups)
- `cim_wizard_integrated_2026/` (including updated `vector_routes.py`)
- `run-docker.sh` (updated with db-up, db-down, backend-up, backend-down)

---

## Step 3: Run on the Server

SSH into the server and start services:

```bash
ssh eclabuser@130.192.238.11
cd ~/cim
chmod +x run-docker.sh
./run-docker.sh up
```

Or start individually:

```bash
./run-docker.sh db-up          # Start database first
./run-docker.sh backend-up     # Start backend (requires DB running)
```

---

## Run-Docker Commands Reference

| Command        | Action                                      |
|----------------|---------------------------------------------|
| `./run-docker.sh up`         | Start database and backend                  |
| `./run-docker.sh down`       | Stop database and backend                   |
| `./run-docker.sh db-up`      | Start database only                         |
| `./run-docker.sh db-down`    | Stop database only                          |
| `./run-docker.sh backend-up` | Start backend only (DB must be running)    |
| `./run-docker.sh backend-down`| Stop backend only                           |

---

## Verify Deployment

After starting:

- API docs: http://130.192.238.11:8001/docs (or your server host)
- Health: http://130.192.238.11:8001/health
- New scenario endpoints: see `SCENARIO_ENDPOINTS.md`

---

## Quick Deployment Workflow

```bash
# Local: deploy
./deploy-to-server.sh

# Server: stop, then start with new code
ssh eclabuser@130.192.238.11 "cd ~/cim && ./run-docker.sh down && ./run-docker.sh up"
```

---

## Populating the Server Database

The server DB is empty because `init_backup.sql` (~2.1 GB) is excluded from `deploy-to-server.sh`. To populate it:

### Option A: Copy init_backup + run fresh DB init

1. **Copy init_backup.sql** (one-time, ~2.1 GB):

   ```bash
   ./deploy-init-to-server.sh
   ```
   Or manually:
   ```bash
   rsync -avz --progress cim-database/init-db/init_backup.sql \
     eclabuser@130.192.238.11:~/cim/cim-database/init-db/
   ```

2. **On the server, recreate the DB** (destroys existing data):

   ```bash
   ssh eclabuser@130.192.238.11
   cd ~/cim
   ./run-docker.sh down
   cd cim-database
   docker compose -f docker-compose.cimdb.yml down -v   # -v removes volume
   docker compose -f docker-compose.cimdb.yml up -d
   cd ~/cim && ./run-docker.sh backend-up
   ```

   Init scripts run on first startup and will restore schema + data from `init_backup.sql`.

### Option B: Load PV data only (schema exists from backend)

If the backend has already created empty tables (via `create_all`), you can load PV data from your local machine:

```bash
cd pv/scripts
python load_pv_geojson.py   # targets server 130.192.238.11:15432
```

Ensure port 15432 is reachable from your machine. If not, copy `pv/` to the server and run there:

```bash
# Copy pv folder to server
rsync -avz pv/ eclabuser@130.192.238.11:~/cim/pv/

# On server (connects to localhost:15432)
ssh eclabuser@130.192.238.11
cd ~/cim/pv/scripts
DATABASE_URL="postgresql://cim_wizard_user:cim_wizard_password@localhost:15432/cim_wizard_integrated" python load_pv_geojson.py
```
