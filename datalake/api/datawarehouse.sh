export DATABASE_URL="postgresql://datalake:datalake@localhost:35432/datalake"
uvicorn main:app --host 0.0.0.0 --port 8008 --reload