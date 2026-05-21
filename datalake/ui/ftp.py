"""
FTP upload helpers for the CIM Datalake UI.

FTP configuration is read from .streamlit/secrets.toml:

    [ftp]
    host     = "ftp.example.com"
    user     = "ftpuser"
    password = "secret"
    root     = "/uploads/datalake"

All keys can also be supplied as environment variables:
    FTP_HOST, FTP_USER, FTP_PASS, FTP_ROOT
"""
from __future__ import annotations

import ftplib
import io
import os
import posixpath


def _cfg() -> dict:
    try:
        import streamlit as st
        sec = st.secrets.get("ftp", {})
        return {
            "host":     sec.get("host",     os.getenv("FTP_HOST", "")),
            "user":     sec.get("user",     os.getenv("FTP_USER", "")),
            "password": sec.get("password", os.getenv("FTP_PASS", "")),
            "root":     sec.get("root",     os.getenv("FTP_ROOT", "/uploads")),
        }
    except Exception:
        return {
            "host":     os.getenv("FTP_HOST", ""),
            "user":     os.getenv("FTP_USER", ""),
            "password": os.getenv("FTP_PASS", ""),
            "root":     os.getenv("FTP_ROOT", "/uploads"),
        }


def _mkdirs(ftp: ftplib.FTP, remote_dir: str) -> None:
    """Recursively create directories on the FTP server, ignoring existing ones."""
    parts = [p for p in remote_dir.replace("\\", "/").split("/") if p]
    current = "/"
    for part in parts:
        current = posixpath.join(current, part)
        try:
            ftp.mkd(current)
        except ftplib.error_perm:
            pass


def upload(file_bytes: bytes, filename: str, subdir: str = "") -> str:
    """
    Upload file_bytes to the configured FTP server.

    The file is stored at: {root}/{subdir}/{filename}
    Returns the full remote path.

    Raises RuntimeError when FTP credentials are not configured.
    """
    cfg = _cfg()
    if not cfg["host"]:
        raise RuntimeError(
            "FTP host is not configured. "
            "Add an [ftp] section to .streamlit/secrets.toml."
        )

    remote_dir = posixpath.join(cfg["root"], subdir) if subdir else cfg["root"]
    remote_path = posixpath.join(remote_dir, filename)

    with ftplib.FTP() as ftp:
        ftp.connect(cfg["host"])
        ftp.login(cfg["user"], cfg["password"])
        _mkdirs(ftp, remote_dir)
        ftp.storbinary(f"STOR {remote_path}", io.BytesIO(file_bytes))

    return remote_path


def is_configured() -> bool:
    """Return True when all required FTP settings are present."""
    cfg = _cfg()
    return bool(cfg["host"] and cfg["user"])
