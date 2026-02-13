"""
Field Normalizer - Centralized field name normalization and validation.

This module loads normalization_config.json and provides:
  - normalize_input():  Convert any known alias → canonical field name
  - normalize_output(): Ensure response uses canonical names (identity by default)
  - validate():         Type-check and enforce required/value_range constraints
  - get_schema():       Return the config for a given entity (for /schema endpoint)

The config file is the single source of truth.  Every client (frontend, Postman,
external scripts) can query GET /api/v1/vector/schema to discover canonical names.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

_CONFIG_PATH = Path(__file__).parent / "normalization_config.json"
_config: Optional[Dict] = None
# Pre-built lookup:  (entity, alias_lower) → canonical_name
_alias_lookup: Dict[Tuple[str, str], str] = {}


def _load_config() -> Dict:
    """Load and cache the normalization config, build alias lookup table."""
    global _config, _alias_lookup

    if _config is not None:
        return _config

    with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
        _config = json.load(f)

    # Build fast alias → canonical lookup (case-insensitive aliases)
    _alias_lookup.clear()
    for entity_name, entity_def in _config.get("entities", {}).items():
        for canonical, field_def in entity_def.get("fields", {}).items():
            # The canonical name itself is always a valid input
            _alias_lookup[(entity_name, canonical.lower())] = canonical
            for alias in field_def.get("aliases", []):
                key = (entity_name, alias.lower())
                if key in _alias_lookup and _alias_lookup[key] != canonical:
                    logger.warning(
                        "Alias conflict: '%s' in entity '%s' maps to both '%s' and '%s'. "
                        "Keeping first mapping '%s'.",
                        alias, entity_name, _alias_lookup[key], canonical,
                        _alias_lookup[key],
                    )
                else:
                    _alias_lookup[key] = canonical

    logger.info(
        "Normalization config loaded: %d entities, %d alias mappings",
        len(_config.get("entities", {})),
        len(_alias_lookup),
    )
    return _config


def reload_config() -> Dict:
    """Force-reload the config (useful after editing the JSON at runtime)."""
    global _config
    _config = None
    _alias_lookup.clear()
    return _load_config()


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def get_config() -> Dict:
    """Return the full normalization config dict."""
    return _load_config()


def get_entity_names() -> List[str]:
    """Return list of entity names defined in the config."""
    cfg = _load_config()
    return list(cfg.get("entities", {}).keys())


def get_schema(entity_name: str) -> Optional[Dict]:
    """
    Return the config block for a single entity.

    Useful for the /schema endpoint so clients can auto-discover field names.
    Returns None if the entity is not found.
    """
    cfg = _load_config()
    return cfg.get("entities", {}).get(entity_name)


def get_canonical_name(entity_name: str, field_name: str) -> Optional[str]:
    """
    Resolve a single field name (possibly an alias) to its canonical name.

    Returns None if the field is not recognised for this entity.
    """
    _load_config()
    return _alias_lookup.get((entity_name, field_name.lower()))


def get_canonical_fields(entity_name: str) -> List[str]:
    """Return list of canonical field names for an entity."""
    schema = get_schema(entity_name)
    if schema is None:
        return []
    return list(schema.get("fields", {}).keys())


# ---------------------------------------------------------------------------
# Input normalisation
# ---------------------------------------------------------------------------

def normalize_input(
    entity_name: str,
    data: Dict[str, Any],
    *,
    strict: bool = False,
    drop_unknown: bool = False,
) -> Dict[str, Any]:
    """
    Normalize a dict's keys from any known alias to the canonical field name.

    Parameters
    ----------
    entity_name : str
        One of the entity names in normalization_config.json
        (e.g. "building_properties", "project_scenario", "building").
    data : dict
        Input data whose keys may be aliases.
    strict : bool
        If True, raise ValueError when an unrecognised key is found.
    drop_unknown : bool
        If True, silently remove keys that don't map to any canonical field.
        If False (default), unknown keys are passed through unchanged.

    Returns
    -------
    dict
        New dict with canonical keys.
    """
    _load_config()
    normalized: Dict[str, Any] = {}
    warnings: List[str] = []

    for key, value in data.items():
        canonical = _alias_lookup.get((entity_name, key.lower()))

        if canonical is not None:
            if canonical in normalized:
                # Canonical field already set (e.g. two aliases for same field in input)
                warnings.append(
                    f"Duplicate: '{key}' maps to '{canonical}' which was already set. Keeping first value."
                )
                continue
            normalized[canonical] = value
        else:
            # Unknown field
            if strict:
                raise ValueError(
                    f"Unknown field '{key}' for entity '{entity_name}'. "
                    f"Valid fields: {get_canonical_fields(entity_name)}"
                )
            if not drop_unknown:
                normalized[key] = value
            else:
                warnings.append(f"Dropped unknown field '{key}' for entity '{entity_name}'.")

    if warnings:
        for w in warnings:
            logger.warning(w)

    return normalized


def normalize_input_list(
    entity_name: str,
    items: List[Dict[str, Any]],
    **kwargs,
) -> List[Dict[str, Any]]:
    """Convenience: normalize a list of dicts."""
    return [normalize_input(entity_name, item, **kwargs) for item in items]


def normalize_geojson_properties(
    entity_name: str,
    geojson: Dict[str, Any],
    **kwargs,
) -> Dict[str, Any]:
    """
    Normalize field names inside GeoJSON Feature or FeatureCollection properties.

    Accepts a GeoJSON dict and returns a new dict with normalized properties.
    The geometry is left untouched.
    """
    geojson = dict(geojson)  # shallow copy

    if geojson.get("type") == "FeatureCollection":
        features = geojson.get("features", [])
        geojson["features"] = [
            _normalize_feature_properties(entity_name, f, **kwargs)
            for f in features
        ]
    elif geojson.get("type") == "Feature":
        geojson = _normalize_feature_properties(entity_name, geojson, **kwargs)

    return geojson


def _normalize_feature_properties(
    entity_name: str,
    feature: Dict[str, Any],
    **kwargs,
) -> Dict[str, Any]:
    """Normalize the properties dict inside a single GeoJSON Feature."""
    feature = dict(feature)
    props = feature.get("properties", {})
    if props:
        feature["properties"] = normalize_input(entity_name, props, **kwargs)
    return feature


# ---------------------------------------------------------------------------
# Output normalisation (canonical → canonical, plus optional enrichment)
# ---------------------------------------------------------------------------

def normalize_output(
    entity_name: str,
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Ensure output dict uses canonical field names.

    Since backend already uses canonical names from the DB, this is mostly a
    pass-through.  But it will catch any ad-hoc keys that crept in and
    optionally strip internal-only fields.
    """
    # For now this is identity; it exists so the pattern is established
    # and can be extended (e.g. exclude internal fields, add computed fields).
    return data


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

_TYPE_MAP = {
    "string":   str,
    "integer":  int,
    "float":    (int, float),
    "boolean":  bool,
    "datetime": str,       # datetimes arrive as ISO strings from clients
    "geometry": (dict,),   # GeoJSON dicts
    "json":     (dict, list),
}


def validate(
    entity_name: str,
    data: Dict[str, Any],
    *,
    partial: bool = False,
) -> List[str]:
    """
    Validate a dict against the entity schema.

    Parameters
    ----------
    entity_name : str
        Entity name from the config.
    data : dict
        Data dict with **canonical** field names (run normalize_input first).
    partial : bool
        If True, skip required-field checks (useful for PATCH / partial updates).

    Returns
    -------
    list[str]
        List of validation error messages. Empty list means valid.
    """
    schema = get_schema(entity_name)
    if schema is None:
        return [f"Unknown entity '{entity_name}'"]

    errors: List[str] = []
    fields = schema.get("fields", {})

    # Check required fields
    if not partial:
        for fname, fdef in fields.items():
            if fdef.get("required", False) and fname not in data:
                errors.append(f"Missing required field '{fname}'")

    # Check types and value ranges
    for key, value in data.items():
        fdef = fields.get(key)
        if fdef is None:
            continue  # unknown field, skip

        if value is None:
            continue  # nullable

        # Type check
        expected = fdef.get("type")
        if expected and expected in _TYPE_MAP:
            py_types = _TYPE_MAP[expected]
            if not isinstance(py_types, tuple):
                py_types = (py_types,)
            if not isinstance(value, py_types):
                errors.append(
                    f"Field '{key}': expected {expected}, got {type(value).__name__}"
                )
                continue

        # Value range
        vr = fdef.get("value_range")
        if vr and isinstance(value, (int, float)):
            lo, hi = vr
            if value < lo or value > hi:
                errors.append(
                    f"Field '{key}': value {value} outside range [{lo}, {hi}]"
                )

    return errors


# ---------------------------------------------------------------------------
# Client-facing schema summary
# ---------------------------------------------------------------------------

def get_client_schema() -> Dict[str, Any]:
    """
    Build a client-friendly schema dict suitable for the /schema endpoint.

    Returns a structure that any client can use to discover:
    - Which entities exist
    - Canonical field names and their types
    - Accepted aliases
    - Required / optional status
    - Value ranges and descriptions
    """
    cfg = _load_config()
    result = {
        "version": cfg.get("_meta", {}).get("version", "unknown"),
        "description": cfg.get("_meta", {}).get("description", ""),
        "entities": {},
    }

    for entity_name, entity_def in cfg.get("entities", {}).items():
        entity_out = {
            "description": entity_def.get("description", ""),
            "table": entity_def.get("table", ""),
            "fields": {},
        }
        for fname, fdef in entity_def.get("fields", {}).items():
            entity_out["fields"][fname] = {
                "type": fdef.get("type"),
                "required": fdef.get("required", False),
                "description": fdef.get("description", ""),
                "aliases": fdef.get("aliases", []),
            }
            # Include optional metadata
            if "default" in fdef:
                entity_out["fields"][fname]["default"] = fdef["default"]
            if "value_range" in fdef:
                entity_out["fields"][fname]["value_range"] = fdef["value_range"]
            if "unit" in fdef:
                entity_out["fields"][fname]["unit"] = fdef["unit"]
            if "geometry_type" in fdef:
                entity_out["fields"][fname]["geometry_type"] = fdef["geometry_type"]
            if "srid" in fdef:
                entity_out["fields"][fname]["srid"] = fdef["srid"]

        result["entities"][entity_name] = entity_out

    return result
