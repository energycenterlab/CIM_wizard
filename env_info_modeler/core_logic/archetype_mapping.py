"""Map archetype reference tables in archetypes/ onto a building frame.

Every assigned column gets a `<column>_method` column next to it. Sampled values use a
hash of (random_seed, building_id, variable), so a building keeps its draw however the
frame is sorted or split.
"""

import hashlib
import re
from pathlib import Path

import pandas as pd

ARCHETYPES_DIR = Path(__file__).parent / "archetypes"
METHOD = "episcope distribution"

# TABULA size class written by assign_tabula_size_class -> class used in archetypes/*.csv
SIZE_CLASS_TO_BUILDING_CLASS = {"SFH": "SFH", "MFH": "MFH", "AB": "Apartments"}


def load_reference_tables(archetypes_dir: Path = ARCHETYPES_DIR) -> dict[str, pd.DataFrame]:
    names = [
        "periods",
        "envelope_archetypes",
        "window_door_types",
        "tabula_window_door_by_archetype",
        "system_distributions",
        "episcope_refurbishment_piedmont",
        "performance_clusters",
    ]
    return {name: pd.read_csv(archetypes_dir / f"{name}.csv") for name in names}


def _year_to_period_id(year: float, periods: pd.DataFrame) -> str | None:
    for _, period in periods.iterrows():
        year_to = period["year_to"]
        if pd.isna(year_to) or year <= year_to:
            return period["period_id"]
    return None


def _construction_period_to_year(label: object) -> float | None:
    """DBGT labels: '1946 - 1960' -> midpoint, '1918 (al ..)' -> 1918, '2013' -> 2013."""
    if not isinstance(label, str):
        return None
    years = [int(value) for value in re.findall(r"\d{4}", label)]
    if not years:
        return None  # "non conosciuto"
    return sum(years) / len(years)


def assign_archetype_period_and_class(
    buildings: pd.DataFrame,
    tables: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    result = buildings.copy()
    periods = tables["periods"]

    years = result["construction_period"].map(_construction_period_to_year)
    result["archetype_period_id"] = years.map(
        lambda year: None if pd.isna(year) else _year_to_period_id(year, periods)
    )
    result["archetype_period_id_method"] = METHOD

    result["archetype_class"] = result["tabula_size_class"].map(SIZE_CLASS_TO_BUILDING_CLASS)
    result["archetype_class_method"] = METHOD
    return result


def assign_envelope_u_values(
    buildings: pd.DataFrame,
    tables: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """As-built TABULA U-values [W/m2K] for wall, roof, ceiling, floor, window and door."""
    envelope = tables["envelope_archetypes"][
        ["period_id", "building_class", "tabula_archetype",
         "u_wall_primary", "u_roof", "u_ceiling", "u_floor"]
    ]
    envelope = envelope.rename(columns={
        "period_id": "archetype_period_id",
        "building_class": "archetype_class",
        "u_wall_primary": "u_wall",
    })

    types = tables["window_door_types"].set_index("type_id")
    openings = tables["tabula_window_door_by_archetype"].copy()
    openings["u_window"] = openings["window_type_id"].map(types["u_value"])
    openings["g_window"] = openings["window_type_id"].map(types["g_gl_n"])
    # TABULA lists no external door for MFH/AB: u_door stays null there.
    openings["u_door"] = openings["door_type_id"].map(types["u_value"])
    openings = openings[
        ["tabula_archetype", "window_type_id", "u_window", "g_window", "door_type_id", "u_door"]
    ]

    result = buildings.merge(
        envelope, on=["archetype_period_id", "archetype_class"], how="left"
    )
    result = result.merge(openings, on="tabula_archetype", how="left")

    assigned = [
        "tabula_archetype", "u_wall", "u_roof", "u_ceiling", "u_floor",
        "window_type_id", "u_window", "g_window", "door_type_id", "u_door",
    ]
    for column in assigned:
        result[f"{column}_method"] = METHOD
    result.index = buildings.index
    return result


def _uniform(random_seed: int, building_id: object, variable: str) -> float:
    key = f"{random_seed}|{building_id}|{variable}".encode()
    digest = hashlib.sha256(key).digest()
    return int.from_bytes(digest[:8], "big") / 2**64


def _pick(categories: list, probabilities: list[float], draw: float) -> object:
    total = sum(probabilities)
    cumulative = 0.0
    for category, probability in zip(categories, probabilities):
        cumulative += probability / total
        if draw < cumulative:
            return category
    return categories[-1]


def assign_system_distribution(
    buildings: pd.DataFrame,
    tables: dict[str, pd.DataFrame],
    random_seed: int = 42,
) -> pd.DataFrame:
    """Sample heating system type, energy carrier and DHW system per building.

    Apartments use period-specific URBEM shares; SFH/MFH use the EPISCOPE Piedmont
    regional shares (period_id 'ALL'). The method column says which one was used.
    """
    result = buildings.copy()
    distributions = tables["system_distributions"]
    variables = ["heating_system_type", "energy_carrier", "dhw_system"]

    lookup = {}
    for key, rows in distributions.groupby(["variable", "building_class", "period_id"]):
        lookup[key] = (rows["category"].tolist(), rows["probability"].tolist(), rows["method"].iloc[0])

    for variable in variables:
        values = []
        methods = []
        for building_id, period_id, building_class in zip(
            result["building_id"], result["archetype_period_id"], result["archetype_class"]
        ):
            entry = lookup.get((variable, building_class, period_id))
            if entry is None and not pd.isna(period_id):
                entry = lookup.get((variable, building_class, "ALL"))
            if entry is None:
                values.append(None)
                methods.append(None)
                continue
            categories, probabilities, method = entry
            draw = _uniform(random_seed, building_id, variable)
            values.append(_pick(categories, probabilities, draw))
            methods.append(method)
        result[variable] = values
        result[f"{variable}_method"] = methods
    return result


def assign_refurbishment_distribution(
    buildings: pd.DataFrame,
    tables: dict[str, pd.DataFrame],
    random_seed: int = 42,
) -> pd.DataFrame:
    """Sample refurbished yes/no and, if yes, the refurbishment type (EPISCOPE S-1.2.1).

    EPISCOPE counts apartments, not buildings, and does not split by class, so every
    class in a period gets the same shares. U-values are not changed here.
    """
    result = buildings.copy()
    refurbishment = tables["episcope_refurbishment_piedmont"].set_index("period_id")
    type_columns = {
        "technical_systems": "technical_systems_share",
        "structural_elements": "structural_elements_share",
        "non_structural_elements": "non_structural_elements_share",
    }

    refurbished = []
    refurbishment_types = []
    for building_id, period_id in zip(result["building_id"], result["archetype_period_id"]):
        if pd.isna(period_id) or period_id not in refurbishment.index:
            refurbished.append(None)
            refurbishment_types.append(None)
            continue
        row = refurbishment.loc[period_id]
        is_refurbished = _uniform(random_seed, building_id, "refurbished") < row["refurbished_share"]
        refurbished.append(is_refurbished)
        if not is_refurbished:
            refurbishment_types.append("none")
            continue
        draw = _uniform(random_seed, building_id, "refurbishment_type")
        shares = [row[column] for column in type_columns.values()]
        refurbishment_types.append(_pick(list(type_columns), shares, draw))

    result["refurbished"] = pd.array(refurbished, dtype="boolean")
    result["refurbished_method"] = METHOD
    result["refurbishment_type"] = refurbishment_types
    result["refurbishment_type_method"] = METHOD
    return result


def assign_performance_cluster(
    buildings: pd.DataFrame,
    tables: dict[str, pd.DataFrame],
    random_seed: int = 42,
) -> pd.DataFrame:
    """Sample a performance level (wall U band, window type, heat generator) per building."""
    result = buildings.copy()
    clusters = tables["performance_clusters"].copy()
    clusters["period_ids"] = clusters["period_ids"].str.split(";")
    clusters = clusters.explode("period_ids")

    assigned = ["performance_level", "u_wall_min", "u_wall_max", "window_type", "heat_generator"]
    lookup = {
        period_id: (rows[assigned].to_dict("records"), rows["share"].tolist())
        for period_id, rows in clusters.groupby("period_ids")
    }

    picked_rows = []
    for building_id, period_id in zip(result["building_id"], result["archetype_period_id"]):
        if period_id not in lookup:
            picked_rows.append({column: None for column in assigned})
            continue
        levels, shares = lookup[period_id]
        draw = _uniform(random_seed, building_id, "performance_level")
        picked_rows.append(_pick(levels, shares, draw))

    picked = pd.DataFrame(picked_rows, index=result.index)
    for column in assigned:
        result[f"cluster_{column}"] = picked[column]
        result[f"cluster_{column}_method"] = METHOD
    return result
