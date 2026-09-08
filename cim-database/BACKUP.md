# CIM Wizard database backup and restore

Two Docker Postgres instances:

| Role | Host | Compose file | Data volume |
|------|------|----------------|-------------|
| **Primary** | cloud3 `130.192.238.11` | `docker-compose.cimdb.yml` | `cim_postgres_data` |
| **Clone** | cloud4 `130.192.238.12` | `docker-compose.cimdb-replica.yml` | `cim_postgres_replica_data` |

Same image (`cim-database:latest`). Cloud4 must **not** mount `init-db/init_backup.sql`. Load it with a snapshot from cloud3.

This is **dump → copy → restore**, not WAL streaming. The clone matches the primary only at snapshot time. Cloud3 should stay the only writer unless you deliberately fail over.

Run the snapshot scripts from your **laptop**. Do not use `sudo`. Do not paste `YYYYMMDDTHHMMSSZ` — the scripts generate a real timestamp.

---

## Weekly / on demand: copy cloud3 onto cloud4

From `~/Desktop/ali/CIM_wizard`:

```bash
chmod +x cim-database/scripts/*.sh
./cim-database/scripts/snapshot-c3-to-c4.sh full
```

You will type the cloud3 password, then the cloud4 password (SSH multiplexing reuses each connection).

| Mode | Command | Result |
|------|---------|--------|
| schema + data (usual) | `./cim-database/scripts/snapshot-c3-to-c4.sh full` | Drop/recreate DB on C4, restore everything |
| schema only | `... snapshot-c3-to-c4.sh schema` | Empty tables on C4 |
| data only | `... snapshot-c3-to-c4.sh data` | Rows only; C4 schema must already match |

Timescale may print circular-FK warnings on dump. For a **full** dump that is normal.

After restore, check counts:

```bash
ssh eclabuser@130.192.238.12 \
  "docker exec cim-integrateddb psql -U cim_wizard_user -d cim_wizard_integrated -c 'SELECT count(*) FROM cim_vector.cim_wizard_building;'"
```

Dumps are kept in:

- cloud3: `~/cim/cim-database/backups/`
- laptop: `/tmp/cim-db-snapshots/`
- cloud4: `~/cim-db-backups/cloud3/` and `~/cim/cim-database/backups/` (container `/backups`)

---

## Emergency: copy cloud4 back onto cloud3

This **replaces production** on cloud3. Stop backends if you can, then:

```bash
./cim-database/scripts/snapshot-c4-to-c3.sh
# type YES
```

---

## Dump or restore on one server only

SSH to the machine that has `cim-integrateddb`, then:

```bash
cd ~/cim/cim-database/scripts
./backup-db.sh full                 # or schema | data | all
./restore-db.sh full cim_full_….dump   # type YES
```

`backup-db.sh` does **not** copy to the other cloud and does **not** rebuild Docker.

---

## First-time cloud4 clone (if the container is not up yet)

1. Copy `cim-database/Dockerfile` and `docker-compose.cimdb-replica.yml` to cloud4 `~/cim/cim-database/`.
2. Prefer `docker save` / `docker load` of `cim-database:latest` from cloud3 (avoids apt clock failures on rebuild).
3. `mkdir -p ~/cim/cim-database/backups ~/cim-db-backups/cloud3`
4. `docker compose -f docker-compose.cimdb-replica.yml -p cim-database up -d` (**no** `--build` if the image was loaded).
5. From the laptop: `./cim-database/scripts/snapshot-c3-to-c4.sh full`

Do not copy `init_backup.sql` onto cloud4.

---

## Optional: fewer password prompts

```bash
ssh-copy-id eclabuser@130.192.238.11
ssh-copy-id eclabuser@130.192.238.12
```

Do **not** set up nested SSH from cloud3 to cloud4 unless you add a key on cloud3. The laptop scripts hop through this machine on purpose.

---

## Scripts

| File | Where it runs | Purpose |
|------|----------------|---------|
| `snapshot-c3-to-c4.sh` | laptop | Dump C3, copy via laptop, restore C4 |
| `snapshot-c4-to-c3.sh` | laptop | Dump C4, copy via laptop, restore C3 |
| `apply-dump.sh` | remote (via the snapshots) | Drop/recreate + `pg_restore` |
| `backup-db.sh` | cloud3 or cloud4 | Local dump only |
| `restore-db.sh` | cloud3 or cloud4 | Local restore only |
| `cim-hosts.env` | sourced by snapshots | IPs and paths |
| `db-backup.env` | sourced by on-host scripts | Container name, keep count |
