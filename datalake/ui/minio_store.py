"""
MinIO (S3-compatible) helpers for the CIM Datalake UI — boto3 backend.

Configuration (first match wins for each field):

  1. Environment variables (handy from ingest.sh):
       MINIO_URI=http://minioadmin:minioadmin@localhost:9000/datawh
       # or discrete:
       MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, MINIO_BUCKET, MINIO_SECURE

  2. .streamlit/secrets.toml:

       [minio]
       endpoint   = "localhost:9000"
       access_key = "minioadmin"
       secret_key = "minioadmin"
       bucket     = "datawh"
       secure     = false
"""
from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse


def _truthy(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("1", "true", "yes", "on")


def _parse_minio_uri(uri: str) -> dict[str, Any]:
    """
    Parse MINIO_URI forms:
      http://user:pass@host:9000/bucket
      https://user:pass@host:9000/bucket
      s3://user:pass@host:9000/bucket
    """
    raw = uri.strip()
    if raw.startswith("s3://"):
        raw = "http://" + raw[len("s3://"):]
    p = urlparse(raw)
    if not p.hostname:
        raise ValueError(f"Invalid MINIO_URI (no host): {uri!r}")
    port = p.port or (443 if p.scheme == "https" else 9000)
    bucket = (p.path or "").strip("/").split("/")[0]
    if not bucket:
        raise ValueError(f"Invalid MINIO_URI (no bucket path): {uri!r}")
    return {
        "endpoint":   f"{p.hostname}:{port}",
        "access_key": p.username or "",
        "secret_key": p.password or "",
        "bucket":     bucket,
        "secure":     p.scheme == "https",
    }


def _secrets_minio() -> dict[str, Any]:
    try:
        import streamlit as st
        return dict(st.secrets.get("minio", {}) or {})
    except Exception:
        return {}


def _cfg() -> dict[str, Any]:
    """Resolve MinIO config: MINIO_URI → env vars → secrets.toml → defaults."""
    uri = os.getenv("MINIO_URI", "").strip()
    if uri:
        base = _parse_minio_uri(uri)
    else:
        base = {
            "endpoint":   "localhost:9000",
            "access_key": "",
            "secret_key": "",
            "bucket":     "datawh",
            "secure":     False,
        }

    sec = _secrets_minio()

    endpoint = (
        os.getenv("MINIO_ENDPOINT")
        or sec.get("endpoint")
        or base["endpoint"]
    )
    access_key = (
        os.getenv("MINIO_ACCESS_KEY")
        or sec.get("access_key")
        or base["access_key"]
    )
    secret_key = (
        os.getenv("MINIO_SECRET_KEY")
        or sec.get("secret_key")
        or base["secret_key"]
    )
    bucket = (
        os.getenv("MINIO_BUCKET")
        or sec.get("bucket")
        or base["bucket"]
    )

    if "MINIO_SECURE" in os.environ:
        secure = _truthy(os.environ["MINIO_SECURE"])
    elif "secure" in sec:
        secure = _truthy(sec.get("secure"))
    else:
        secure = bool(base.get("secure"))

    return {
        "endpoint":   str(endpoint).strip(),
        "access_key": str(access_key).strip(),
        "secret_key": str(secret_key).strip(),
        "bucket":     str(bucket).strip(),
        "secure":     secure,
    }


def is_configured() -> bool:
    cfg = _cfg()
    return bool(cfg["endpoint"] and cfg["access_key"] and cfg["secret_key"] and cfg["bucket"])


def endpoint_url(cfg: dict[str, Any] | None = None) -> str:
    c = cfg or _cfg()
    scheme = "https" if c["secure"] else "http"
    return f"{scheme}://{c['endpoint']}"


def _client():
    import boto3
    from botocore.client import Config

    cfg = _cfg()
    if not cfg["access_key"] or not cfg["secret_key"]:
        raise RuntimeError(
            "MinIO is not configured. Set MINIO_URI in ingest.sh "
            "or add a [minio] section to .streamlit/secrets.toml."
        )
    client = boto3.client(
        "s3",
        endpoint_url=endpoint_url(cfg),
        aws_access_key_id=cfg["access_key"],
        aws_secret_access_key=cfg["secret_key"],
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )
    return client, cfg


def upload(
    file_bytes: bytes,
    filename: str,
    *,
    prefix: str = "",
    content_type: str = "application/octet-stream",
) -> str:
    """
    Upload bytes to the configured MinIO bucket via boto3.

    Object key: {prefix}/{filename}  (prefix optional)
    Returns: s3://{bucket}/{object_key}
    """
    client, cfg = _client()
    bucket = cfg["bucket"]
    object_key = f"{prefix.rstrip('/')}/{filename}" if prefix else filename

    try:
        client.head_bucket(Bucket=bucket)
    except Exception as exc:
        raise RuntimeError(
            f"MinIO bucket '{bucket}' is not reachable at {endpoint_url(cfg)}. "
            f"Create it in the console or check MINIO_URI. Detail: {exc}"
        ) from exc

    client.put_object(
        Bucket=bucket,
        Key=object_key,
        Body=file_bytes,
        ContentType=content_type,
    )
    return f"s3://{bucket}/{object_key}"
