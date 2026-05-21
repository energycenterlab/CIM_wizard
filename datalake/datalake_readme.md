# Datalake Setup and Run Guide

This guide explains how to:

1. Create and use a Conda environment named `webgis`
2. Start Docker services (PostGIS and MongoDB)
3. Configure and run the Streamlit datalake UI

## 1) Conda environment (`webgis`)

From the repository root:

```bash
conda create -n webgis python=3.11 -y
conda activate webgis
pip install -r datalake/ui/requirements.txt
```

## 2) Start Docker services

The datalake stack uses Docker Compose from the `datalake/` directory.

```bash
cd datalake
docker compose up -d --build
```

### Exposed ports

- PostGIS: `localhost:35432` (container `5432`)
- MongoDB: `localhost:27018` (container `27017`)

### Persistent storage

Docker volumes are used and managed by compose:

- `postgis_data`
- `mongodb_data`
- `mongodb_config`

## 3) Configure Streamlit secrets

Create a local secrets file from the example:

```bash
cp datalake/ui/.streamlit/secrets.toml.example datalake/ui/.streamlit/secrets.toml
```

Update values in `datalake/ui/.streamlit/secrets.toml`:

- `DATABASE_URL`
- FTP settings under `[ftp]` (if file transfer to server is required)

Example:

```toml
DATABASE_URL = "postgresql://datalake:datalake@localhost:35432/datalake"

[ftp]
host = "ftp.example.com"
user = "ftpuser"
password = "secret"
root = "/uploads/datalake"
```

## 4) Run the datalake application

From repository root:

```bash
conda activate webgis
cd datalake/ui
streamlit run Home.py
```

Open the UI in your browser:

- [http://localhost:8501](http://localhost:8501)

## 5) Stop services

From `datalake/`:

```bash
docker compose down
```

To also remove named volumes (deletes database data):

```bash
docker compose down -v
```
