"""
Configuration Synchronizer -- runs once at application startup.

Reads configuration.json and ensures that:
  1. Every feature with an ``output`` section has matching DB columns
     (ALTER TABLE ADD COLUMN IF NOT EXISTS).
  2. The normalization_config.json ``building_properties`` entity is
     extended with entries for any new output columns.
  3. Feature proxies and _data attributes are returned for data_manager
     dynamic initialization.

No separate codegen scripts are needed.  Stop the backend, edit
configuration.json (and add a calculator file), restart -- everything
is picked up automatically.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

from sqlalchemy import text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).parent / "configuration.json"
_NORM_CONFIG_PATH = Path(__file__).parent / "normalization_config.json"

# Maps configuration type strings to PostgreSQL DDL type strings
_PG_TYPE_MAP = {
    "Float": "DOUBLE PRECISION",
    "Integer": "INTEGER",
    "String": "VARCHAR",
    "Boolean": "BOOLEAN",
    "JSON": "JSONB",
}


def load_pipeline_config() -> Dict[str, Any]:
    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------
# 1.  DB column sync
# ------------------------------------------------------------------

def _column_exists(conn, schema: str, table: str, column: str) -> bool:
    result = conn.execute(
        text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_schema = :schema "
            "AND table_name = :table "
            "AND column_name = :col"
        ),
        {"schema": schema, "table": table, "col": column},
    )
    return result.fetchone() is not None


def sync_db_columns(engine: Engine, config: Dict[str, Any]) -> List[str]:
    """
    For every feature that declares ``output`` columns, ensure they exist
    in the database.  Uses ``ALTER TABLE ... ADD COLUMN IF NOT EXISTS``.

    Returns a list of columns that were created.
    """
    created: List[str] = []
    features = config.get("features", {})

    with engine.connect() as conn:
        for feature_name, feat_def in features.items():
            for col_def in feat_def.get("output", []):
                schema = col_def["schema"]
                table = col_def["table"]
                column = col_def["column"]
                col_type = col_def["type"]
                length = col_def.get("length")

                if _column_exists(conn, schema, table, column):
                    continue

                pg_type = _PG_TYPE_MAP.get(col_type, col_type)
                if pg_type == "VARCHAR" and length:
                    pg_type = f"VARCHAR({length})"

                fqn = f"{schema}.{table}"
                ddl = f'ALTER TABLE {fqn} ADD COLUMN "{column}" {pg_type}'
                try:
                    conn.execute(text(ddl))
                    created.append(f"{fqn}.{column}")
                    logger.info("Created column %s.%s (%s)", fqn, column, pg_type)
                except Exception as exc:
                    logger.error(
                        "Failed to create column %s.%s: %s", fqn, column, exc
                    )
        conn.commit()

    return created


# ------------------------------------------------------------------
# 2.  Normalizer sync
# ------------------------------------------------------------------

def _datatype_to_norm_type(datatype: str) -> str:
    mapping = {
        "float": "float",
        "int": "integer",
        "string": "string",
        "boolean": "boolean",
        "dict": "json",
        "geometry": "geometry",
    }
    return mapping.get(datatype, "string")


def sync_normalizer(config: Dict[str, Any]) -> int:
    """
    Read normalization_config.json, ensure every output column declared in
    configuration.json has a matching entry in the ``building_properties``
    entity.  Write back only if something changed.

    Returns the number of fields that were added.
    """
    try:
        with open(_NORM_CONFIG_PATH, "r", encoding="utf-8") as f:
            norm_cfg = json.load(f)
    except FileNotFoundError:
        logger.warning("normalization_config.json not found; skipping sync")
        return 0

    bp_entity = norm_cfg.get("entities", {}).get("building_properties")
    if bp_entity is None:
        logger.warning(
            "No 'building_properties' entity in normalization_config.json; skipping"
        )
        return 0

    fields = bp_entity.setdefault("fields", {})
    added = 0
    features = config.get("features", {})

    for feature_name, feat_def in features.items():
        constraints = feat_def.get("constraints", {})
        norm_type = _datatype_to_norm_type(constraints.get("datatype", "string"))

        for col_def in feat_def.get("output", []):
            column = col_def["column"]
            if column in fields:
                continue

            entry: Dict[str, Any] = {
                "type": norm_type,
                "required": False,
                "description": f"Auto-synced from feature '{feature_name}'",
                "aliases": [],
            }
            vr = constraints.get("value_range")
            if vr:
                entry["value_range"] = vr

            fields[column] = entry
            added += 1
            logger.info(
                "Added normalizer field '%s' for feature '%s'", column, feature_name
            )

    if added:
        with open(_NORM_CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(norm_cfg, f, indent=2, ensure_ascii=False)
            f.write("\n")
        # Force the normalizer module to reload its cache
        try:
            from app.core.normalizer import reload_config
            reload_config()
        except ImportError:
            pass

    return added


# ------------------------------------------------------------------
# 3.  Feature names for dynamic proxy / _data generation
# ------------------------------------------------------------------

def get_feature_names(config: Dict[str, Any]) -> List[str]:
    """Return all feature names from configuration."""
    return list(config.get("features", {}).keys())


# ------------------------------------------------------------------
# Public entry point (called from lifespan)
# ------------------------------------------------------------------

def run_config_sync(engine: Engine) -> Dict[str, Any]:
    """
    Master sync function.  Call once during app startup.

    Returns a summary dict with sync results.
    """
    config = load_pipeline_config()

    created_cols = sync_db_columns(engine, config)
    norm_added = sync_normalizer(config)
    feature_names = get_feature_names(config)

    summary = {
        "db_columns_created": created_cols,
        "normalizer_fields_added": norm_added,
        "feature_count": len(feature_names),
        "feature_names": feature_names,
    }

    logger.info(
        "Config sync complete: %d DB columns created, %d normalizer fields added, "
        "%d features registered",
        len(created_cols),
        norm_added,
        len(feature_names),
    )

    return summary
