# Database initialization & restore

## Why "unsupported version (1.15)" happens

Your `db_backup.sql` was created with **pg_dump** from a **newer PostgreSQL** (17+) than the Docker image (PostgreSQL 15). Custom format dumps are **not backward compatible**.

## Why "invalid command \restrict" happens

`pg_restore -f file.sql` outputs a **restore script**, not plain SQL. That script contains `\restrict` markers that **psql cannot run**. You must restore into a temp DB and re-dump as plain SQL.

## Solutions

### Option 1: Convert backup to plain SQL (recommended)

The script restores into a temp PG 17 container, then `pg_dump -F p` for true plain SQL:

```bash
cd cim-database/cim-database

# If you have the bad \restrict file, restore original first:
# mv db/db_backup.sql db/db_backup.sql.bad && mv db/db_backup.sql.custom db/db_backup.sql

./scripts/convert-backup-to-plain-sql.sh
```

Then:

```bash
cd ..  # to cim-database/
mv db/db_backup.sql db/db_backup.sql.custom
mv db/db_backup_plain.sql db/db_backup.sql
cd cim-database
docker compose -f docker-compose.cimdb.yml down -v
docker compose -f docker-compose.cimdb.yml up -d
```

### Option 2: Re-create backup as plain SQL

If you have access to the source database:

```bash
pg_dump -F p -f db_backup.sql -U your_user -d your_database
```

Replace `db/db_backup.sql` and restart Docker.

### Option 3: Schemas only (no data)

The init already creates `cim_vector`, `cim_census`, `cim_raster` schemas. If restore fails, you still get empty schemas. You can then load data manually via pgAdmin or other tools.

## Init order

1. `00-init-schemas.sql` – creates schemas and PostGIS extensions
2. `01-restore-backup.sh` – restores `db/db_backup.sql` (plain SQL or compatible custom format)
