#!/usr/bin/env bash
# Start the MongoDB-backed FastAPI service on port 8001.
# Requires: pip install -r requirements.txt
# Requires: datalake_mongodb container on localhost:27018

export MONGO_URI="${MONGO_URI:-mongodb://localhost:27018/}"
export MONGO_DB="${MONGO_DB:-datalake}"
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
