# CIM Database - Backup-based Initialization

The database initializes from `init-db/init_backup.sql` on **first startup**.

## Quick Start

```bash
cd cim-database
docker compose -f docker-compose.cimdb.yml up --build -d
```

On first run, the plain SQL backup in `init-db/init_backup.sql` is executed automatically.

## Requirements

- `init-db/init_backup.sql` – plain SQL backup from `pg_dump -F p`
- Create with: `pg_dump -U cim_wizard_user -d cim_wizard_integrated -F p -f init_backup.sql --no-owner --no-acl`

## Fresh Start (re-run init)

```bash
docker compose -f docker-compose.cimdb.yml down -v
docker compose -f docker-compose.cimdb.yml up -d
```

## Connection

| Host     | Port  | Database              | User             | Password           |
|----------|-------|-----------------------|------------------|--------------------|
| localhost| 15432 | cim_wizard_integrated | cim_wizard_user  | cim_wizard_password |
