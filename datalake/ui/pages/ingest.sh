#!/usr/bin/env bash
# Launch ingest_api.py with remote FastAPI + MinIO settings.
# Edit the exports below — they override .streamlit/secrets.toml.

set -euo pipefail
cd "$(dirname "$0")"

# ── FastAPI warehouse API ────────────────────────────────────────────────────
# export API_BASE_URL=http://localhost:8008
export API_BASE_URL="${API_BASE_URL:-http://130.192.238.11:8008}"

# ── MinIO object storage (boto3 / S3 API) ─────────────────────────────────────
# Combined URI (preferred):  scheme://ACCESS:SECRET@HOST:PORT/BUCKET
#   http://minioadmin:minioadmin@localhost:9000/datawh
#   http://minioadmin:minioadmin@130.192.238.11:9000/datawh
export MINIO_URI="${MINIO_URI:-http://minioadmin:minioadmin@localhost:9000/datawh}"

# Optional overrides (win over fields inside MINIO_URI / secrets.toml):
# export MINIO_ENDPOINT=localhost:9000
# export MINIO_ACCESS_KEY=minioadmin
# export MINIO_SECRET_KEY=minioadmin
# export MINIO_BUCKET=datawh
# export MINIO_SECURE=false

# Streamlit loads ./.streamlit/config.toml (maxUploadSize=500) automatically.
streamlit run ingest_api.py
