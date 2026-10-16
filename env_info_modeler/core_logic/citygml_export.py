"""LoD2 surfaces and a CityGML file for the residential stock.

Geometry comes from lod0_3d_footprint_32632. Walls are the footprint edges
extruded by building_height_m. The roof is that footprint lifted to the eave.
The file follows house2_lod2 in cim-database/report_house.gml: one shared
construction library, then one building whose surfaces point at it.
write_citygml_core / strip_energy_ade drop nrg3 so Importer/Exporter can
load the LoD2 buildings without the LayeredConstructionLibrary NPE.
"""

from __future__ import annotations

import math
import re
from pathlib import Path
from xml.sax.saxutils import escape

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely.geometry import Polygon

from archetype_mapping import _pick, _uniform

CRS = "EPSG:32632"
WALL_WINDOW_RATIO = 0.20
CITYMODEL_OPEN = (
    '<core:CityModel xmlns:bldg="http://www.opengis.net/citygml/building/2.0" '
    'xmlns:core="http://www.opengis.net/citygml/2.0" '
    'xmlns:gen="http://www.opengis.net/citygml/generics/2.0" '
    'xmlns:gml="http://www.opengis.net/gml" '
    'xmlns:nrg3="http://www.citygml.org/ade/energy/3.0" '
    'xmlns:xlink="http://www.w3.org/1999/xlink">'
)
CITYMODEL_OPEN_CORE = (
    '<core:CityModel xmlns:bldg="http://www.opengis.net/citygml/building/2.0" '
    'xmlns:core="http://www.opengis.net/citygml/2.0" '
    'xmlns:gml="http://www.opengis.net/gml">'
)
_NRG3_NS = re.compile(r'\sxmlns:nrg3="[^"]*"')
_LIBRARY_MEMBER = re.compile(
    r"<core:cityObjectMember><nrg3:LayeredConstructionLibrary\b.*?"
    r"</nrg3:LayeredConstructionLibrary></core:cityObjectMember>"
)
_NRG3_BLOCK = re.compile(r"<nrg3:(device|thermalZone)\b.*?</nrg3:\1>")
_NRG3_EMPTY = re.compile(r"<nrg3:[^>]*/>")
_NRG3_ELEM = re.compile(r"<nrg3:([^ >]+)[^>]*>.*?</nrg3:\1>")

# EPISCOPE / URBEM labels on the building frame -> EuReCa name parts.
# Single is one plant per dwelling. Centralized is one plant for the building.
HEATING_SCOPE = {
    "Central heating system for several dwellings": "Centralized",
    "Centralized": "Centralized",
    "Individual heating system for a single dwelling": "Single",
    "Single heating devices for dwelling as a whole": "Single",
    "Autonomous": "Single",
}
PART_OF_DWELLING = "Single heating devices for part of dwelling"

# Carrier text on the building -> the eureca_fuel word in energy_systems.csv.
CARRIER_FUEL = {
    "Natural gas": "Natural Gas",
    "Natural Gas": "Natural Gas",
    "Gas oil": "Oil",
    "Fuel oil": "Oil",
    "Electricity": "Electric",
    "District heating": "DH",
}


def _xml_bool(value: object) -> str | None:
    if value is True or str(value).lower() == "true":
        return "true"
    if value is False or str(value).lower() == "false":
        return "false"
    return None


def _storeys_above(raw: object) -> int | None:
    if not isinstance(raw, str):
        return None
    text = raw.strip().lower()
    if re.fullmatch(r"\d+", text):
        return int(text)
    match = re.fullmatch(r"(\d+)\+(\d+)", text)
    if match:
        return int(match.group(1)) + int(match.group(2))
    match = re.fullmatch(r"(\d+)\+s", text)
    if match:
        return int(match.group(1))
    return None


def _construction_year(period: object) -> str | None:
    if isinstance(period, str) and re.fullmatch(r"\d{4}", period.strip()):
        return period.strip()
    return None


def _writable(device: pd.Series) -> bool:
    element = device["device_element"]
    if element == "Boiler":
        return _xml_bool(device["has_condensation"]) is not None
    if element == "HeatPump":
        return isinstance(device["heat_source"], str) and device["heat_source"] != ""
    return isinstance(element, str) and element != ""


def _narrow(candidates: pd.DataFrame, fuel: str, cluster: object) -> pd.DataFrame:
    if fuel == "Natural Gas" and cluster == "Condensing boiler":
        narrowed = candidates[candidates["machine"].str.startswith("Condensing")]
    elif fuel == "Natural Gas" and cluster == "Standard boiler":
        narrowed = candidates[candidates["machine"].str.startswith("Traditional")]
    elif fuel == "Electric" and cluster == "Heat pump":
        machine = candidates["machine"].fillna("")
        narrowed = candidates[machine.str.contains("Heat Pump") | machine.str.contains("HP Staffel")]
    else:
        return candidates
    if narrowed.empty:
        return candidates
    return narrowed


def assign_heating_devices(
    buildings: pd.DataFrame,
    energy_systems: pd.DataFrame,
    random_seed: int = 42,
) -> pd.DataFrame:
    """One ready EuReCa heating name per building, or a reason when none is written."""
    ready = energy_systems.loc[
        energy_systems["record_kind"].eq("eureca_ready")
        & energy_systems["service"].eq("spaceHeating")
    ].copy()
    ready = ready.loc[ready.apply(_writable, axis=1)]
    grouped = {
        key: rows
        for key, rows in ready.groupby(["eureca_fuel", "plant_scope"], dropna=False)
    }

    names = []
    codespaces = []
    elements = []
    condensations = []
    heat_sources = []
    methods = []
    for building_id, heating, carrier, cluster in zip(
        buildings["building_id"],
        buildings["heating_system_type"],
        buildings["energy_carrier"],
        buildings["cluster_heat_generator"],
    ):
        if heating == PART_OF_DWELLING:
            names.append(None)
            codespaces.append(None)
            elements.append(None)
            condensations.append(None)
            heat_sources.append(None)
            methods.append("heats part of a dwelling; EuReCa names are Centralized or Single")
            continue
        scope = HEATING_SCOPE.get(heating)
        fuel = CARRIER_FUEL.get(carrier)
        candidates = grouped.get((fuel, scope))
        if scope is None or fuel is None or candidates is None or candidates.empty:
            names.append(None)
            codespaces.append(None)
            elements.append(None)
            condensations.append(None)
            heat_sources.append(None)
            methods.append("no schema-complete ready name for this carrier and heating type")
            continue
        pool = _narrow(candidates, fuel, cluster)
        chosen = _pick(
            pool.to_dict("records"),
            [1.0] * len(pool),
            _uniform(random_seed, building_id, "eureca_name"),
        )
        names.append(chosen["eureca_name"])
        codespaces.append(chosen["eureca_codespace"])
        elements.append(chosen["device_element"])
        condensations.append(_xml_bool(chosen["has_condensation"]))
        heat_sources.append(chosen["heat_source"] if isinstance(chosen["heat_source"], str) else None)
        methods.append("ready EuReCa name for this carrier, scope and cluster")

    return pd.DataFrame({
        "building_id": buildings["building_id"].to_numpy(),
        "eureca_name": names,
        "eureca_codespace": codespaces,
        "device_element": elements,
        "has_condensation": condensations,
        "heat_source": heat_sources,
        "heating_device_method": methods,
    })


def _poslist(coordinates: np.ndarray) -> str:
    closed = coordinates
    if not np.allclose(coordinates[0], coordinates[-1]):
        closed = np.vstack([coordinates, coordinates[0]])
    return " ".join(
        f"{point[0]:.4f} {point[1]:.4f} {point[2]:.4f}" for point in closed
    )


def _azimuth(start: np.ndarray, end: np.ndarray, outward_to_the_right: bool) -> float:
    dx = float(end[0] - start[0])
    dy = float(end[1] - start[1])
    if outward_to_the_right:
        east, north = dy, -dx
    else:
        east, north = -dy, dx
    return math.degrees(math.atan2(east, north)) % 360.0


def _wall(start: np.ndarray, end: np.ndarray, height: float) -> Polygon:
    top_end = end.copy()
    top_start = start.copy()
    top_end[2] = end[2] + height
    top_start[2] = start[2] + height
    return Polygon([start, end, top_end, top_start])


def _raised(polygon: Polygon, height: float) -> Polygon:
    coordinates = shapely.get_coordinates(polygon, include_z=True)
    coordinates[:, 2] += height
    return shapely.set_coordinates(polygon, coordinates)


def build_surfaces(buildings: pd.DataFrame) -> gpd.GeoDataFrame:
    """Ground, wall and roof polygons in EPSG:32632, one row per face."""
    records = []
    heights = pd.to_numeric(buildings["building_height_m"], errors="coerce").to_numpy()
    for building, height in zip(buildings.itertuples(index=False), heights):
        footprint = building.lod0_3d_footprint_32632
        if footprint is None or footprint.is_empty:
            continue
        archetype = building.building_architype
        ground_id = None if pd.isna(archetype) else f"{archetype}_floor"
        wall_id = None if pd.isna(archetype) else f"{archetype}_wall"
        roof_id = None if pd.isna(archetype) else f"{archetype}_roof"
        records.append({
            "building_id": building.building_id,
            "surface_id": f"b_{building.building_id}_ground",
            "surface_type": "GroundSurface",
            "construction_id": ground_id,
            "u_value": building.u_floor,
            "azimuth_deg": -1.0,
            "inclination_deg": 180.0,
            "opening_ratio": 0.0,
            "area_m2": float(shapely.force_2d(footprint).area),
            "is_adiabatic": False,
            "geometry": footprint,
        })
        if not np.isfinite(height) or height <= 0:
            continue
        shell = shapely.get_exterior_ring(footprint)
        records.extend(_walls(building.building_id, shell, height, wall_id, building.u_wall, True))
        for hole in footprint.interiors:
            records.extend(_walls(building.building_id, hole, height, wall_id, building.u_wall, False))
        records.append({
            "building_id": building.building_id,
            "surface_id": f"b_{building.building_id}_roof",
            "surface_type": "RoofSurface",
            "construction_id": roof_id,
            "u_value": building.u_roof,
            "azimuth_deg": -1.0,
            "inclination_deg": 0.0,
            "opening_ratio": 0.0,
            "area_m2": float(shapely.force_2d(footprint).area),
            "is_adiabatic": False,
            "geometry": _raised(footprint, float(height)),
        })
    surfaces = gpd.GeoDataFrame(records, geometry="geometry", crs=CRS)
    surfaces["surface_id"] = _unique_surface_ids(surfaces)
    return surfaces


def _walls(building_id, ring, height, construction_id, u_value, outward_to_the_right):
    coordinates = shapely.get_coordinates(ring, include_z=True)
    rows = []
    index = 0
    for start, end in zip(coordinates[:-1], coordinates[1:]):
        length = math.hypot(float(end[0] - start[0]), float(end[1] - start[1]))
        if length < 1e-6:
            continue
        rows.append({
            "building_id": building_id,
            "surface_id": f"b_{building_id}_wall_{index}",
            "surface_type": "WallSurface",
            "construction_id": construction_id,
            "u_value": u_value,
            "azimuth_deg": _azimuth(start, end, outward_to_the_right),
            "inclination_deg": 90.0,
            "opening_ratio": WALL_WINDOW_RATIO,
            "area_m2": length * float(height),
            "is_adiabatic": False,
            "geometry": _wall(start, end, float(height)),
        })
        index += 1
    return rows


def _unique_surface_ids(surfaces: gpd.GeoDataFrame) -> pd.Series:
    """Courtyard walls reuse the exterior counter, so make every id unique."""
    counts: dict[str, int] = {}
    unique = []
    for surface_id in surfaces["surface_id"]:
        seen = counts.get(surface_id, 0)
        counts[surface_id] = seen + 1
        unique.append(surface_id if seen == 0 else f"{surface_id}_hole_{seen}")
    return pd.Series(unique, index=surfaces.index)


def _polygon_xml(polygon: Polygon, polygon_id: str) -> str:
    exterior = shapely.get_coordinates(shapely.get_exterior_ring(polygon), include_z=True)
    parts = [
        f'<gml:Polygon gml:id="{polygon_id}" srsName="{CRS}" srsDimension="3">',
        "<gml:exterior><gml:LinearRing>",
        f"<gml:posList>{_poslist(exterior)}</gml:posList>",
        "</gml:LinearRing></gml:exterior>",
    ]
    for interior in polygon.interiors:
        hole = shapely.get_coordinates(interior, include_z=True)
        parts.append("<gml:interior><gml:LinearRing>")
        parts.append(f"<gml:posList>{_poslist(hole)}</gml:posList>")
        parts.append("</gml:LinearRing></gml:interior>")
    parts.append("</gml:Polygon>")
    return "".join(parts)


def _surface_xml(surface: pd.Series, energy_ade: bool = True) -> str:
    tag = surface["surface_type"]
    surface_id = surface["surface_id"]
    lines = [
        "<bldg:boundedBy>",
        f'<bldg:{tag} gml:id="{surface_id}">',
    ]
    construction_id = surface["construction_id"]
    u_value = surface["u_value"]
    if energy_ade and isinstance(construction_id, str) and pd.notna(u_value):
        lines.append(f'<nrg3:layeredConstruction xlink:href="#{escape(construction_id)}"/>')
    lines.append("<bldg:lod2MultiSurface>")
    lines.append(f'<gml:MultiSurface gml:id="{surface_id}_lod2" srsName="{CRS}" srsDimension="3">')
    lines.append("<gml:surfaceMember>")
    lines.append(_polygon_xml(surface.geometry, f"{surface_id}_polygon"))
    lines.append("</gml:surfaceMember></gml:MultiSurface></bldg:lod2MultiSurface>")
    if energy_ade:
        lines.append(
            f'<nrg3:bdgBdrySurfAzimuth uom="decimal degree">{surface["azimuth_deg"]:.4f}</nrg3:bdgBdrySurfAzimuth>'
        )
        lines.append(
            f'<nrg3:bdgBdrySurfInclination uom="decimal degree">{surface["inclination_deg"]:.1f}</nrg3:bdgBdrySurfInclination>'
        )
        adiabatic = "true" if surface["is_adiabatic"] else "false"
        lines.append(f"<nrg3:bdgBdrySurfIsAdiabatic>{adiabatic}</nrg3:bdgBdrySurfIsAdiabatic>")
        lines.append(
            f'<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">{surface["opening_ratio"]:.4f}</nrg3:bdgBdrySurfOpeningToSurfaceRatio>'
        )
        lines.append(
            f'<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">{surface["area_m2"]:.4f}</nrg3:bdgBdrySurfTotalSurfaceArea>'
        )
    lines.append(f"</bldg:{tag}></bldg:boundedBy>")
    return "".join(lines)


def _measure(value) -> str:
    return value if isinstance(value, str) else f"{float(value):.4f}"


def _qualified_area(kind: str, square_metres, description: str | None = None) -> str:
    note = f"<nrg3:description>{escape(description)}</nrg3:description>" if description else ""
    return (
        "<nrg3:area><nrg3:QualifiedArea>"
        f"{note}<nrg3:value uom=\"m^2\">{_measure(square_metres)}</nrg3:value>"
        f"<nrg3:type codeSpace=\"area_codeSpace\">{kind}</nrg3:type>"
        "</nrg3:QualifiedArea></nrg3:area>"
    )


def _qualified_volume(kind: str, cubic_metres, description: str | None = None) -> str:
    note = f"<nrg3:description>{escape(description)}</nrg3:description>" if description else ""
    return (
        "<nrg3:volume><nrg3:QualifiedVolume>"
        f"{note}<nrg3:value uom=\"m^3\">{_measure(cubic_metres)}</nrg3:value>"
        f"<nrg3:type codeSpace=\"volume_codeSpace\">{kind}</nrg3:type>"
        "</nrg3:QualifiedVolume></nrg3:volume>"
    )


def _zone_boundary(surface: dict) -> str:
    """One shell face, geometry reused from the building polygon."""
    surface_id = surface["surface_id"]
    tag = surface["surface_type"]
    lines = [
        "<nrg3:thermalBoundary>",
        f'<bldg:{tag} gml:id="{surface_id}_tz">',
    ]
    construction = surface.get("construction_href")
    if construction:
        lines.append(f'<nrg3:layeredConstruction xlink:href="{construction}"/>')
    lines.append(
        "<bldg:lod2MultiSurface>"
        f'<gml:MultiSurface gml:id="{surface_id}_tz_lod2" srsName="{CRS}" srsDimension="3">'
        f'<gml:surfaceMember xlink:href="#{surface["polygon_id"]}"/>'
        "</gml:MultiSurface></bldg:lod2MultiSurface>"
    )
    lines.append(
        f'<nrg3:bdgBdrySurfAzimuth uom="decimal degree">{_measure(surface["azimuth"])}</nrg3:bdgBdrySurfAzimuth>'
    )
    lines.append(
        f'<nrg3:bdgBdrySurfInclination uom="decimal degree">{_measure(surface["inclination"])}</nrg3:bdgBdrySurfInclination>'
    )
    lines.append(f'<nrg3:bdgBdrySurfIsAdiabatic>{surface["adiabatic"]}</nrg3:bdgBdrySurfIsAdiabatic>')
    lines.append(
        '<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">'
        f'{_measure(surface["opening"])}</nrg3:bdgBdrySurfOpeningToSurfaceRatio>'
    )
    lines.append(
        f'<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">{_measure(surface["area"])}</nrg3:bdgBdrySurfTotalSurfaceArea>'
    )
    lines.append(f"</bldg:{tag}></nrg3:thermalBoundary>")
    return "".join(lines)


def _thermal_zone_markup(
    building_gml_id: str,
    footprint_m2,
    height_m,
    storeys: int | None,
    surfaces: list[dict],
) -> str:
    """One heated zone. Area and volume are the extruded footprint, not a copied house."""
    lines = [
        "<nrg3:thermalZone>",
        f'<nrg3:ThermalZone gml:id="{building_gml_id}_zone">',
        "<gml:name>Thermal zone</gml:name>",
    ]
    if footprint_m2 is not None:
        lines.append(_qualified_area("footprintArea", footprint_m2))
        if storeys is not None:
            lines.append(_qualified_area(
                "grossFloorArea",
                float(footprint_m2) * storeys,
                "footprint area times storeysAboveGround",
            ))
        if height_m is not None:
            lines.append(_qualified_volume(
                "grossVolume",
                float(footprint_m2) * float(height_m),
                "footprint area times measuredHeight",
            ))
    if surfaces:
        members = "".join(
            f'<gml:surfaceMember xlink:href="#{surface["polygon_id"]}"/>' for surface in surfaces
        )
        lines.append(
            "<nrg3:lod2Solid>"
            f'<gml:Solid gml:id="{building_gml_id}_zone_solid">'
            "<gml:exterior>"
            f'<gml:CompositeSurface gml:id="{building_gml_id}_zone_shell">{members}</gml:CompositeSurface>'
            "</gml:exterior></gml:Solid></nrg3:lod2Solid>"
        )
    lines.append("<nrg3:isCooled>false</nrg3:isCooled>")
    lines.append("<nrg3:isHeated>true</nrg3:isHeated>")
    lines.append("<nrg3:coincidesWithLod2Hull>false</nrg3:coincidesWithLod2Hull>")
    lines.append("<nrg3:coincidesWithLod3Hull>false</nrg3:coincidesWithLod3Hull>")
    lines.extend(_zone_boundary(surface) for surface in surfaces)
    lines.append("</nrg3:ThermalZone></nrg3:thermalZone>")
    return "".join(lines)


def _thermal_zone_from_faces(building_gml_id: str, height, storeys: int | None, faces: gpd.GeoDataFrame) -> str:
    ground = faces.loc[faces["surface_type"].eq("GroundSurface"), "area_m2"]
    footprint = float(ground.sum()) if len(ground) else None
    height_m = float(height) if height is not None and np.isfinite(height) else None
    surfaces = []
    for face in faces.itertuples(index=False):
        construction = face.construction_id
        href = None
        if isinstance(construction, str) and pd.notna(face.u_value):
            href = f"#{escape(construction)}"
        surfaces.append({
            "surface_type": face.surface_type,
            "surface_id": face.surface_id,
            "construction_href": href,
            "polygon_id": f"{face.surface_id}_polygon",
            "azimuth": face.azimuth_deg,
            "inclination": f"{face.inclination_deg:.1f}",
            "adiabatic": "true" if face.is_adiabatic else "false",
            "opening": face.opening_ratio,
            "area": face.area_m2,
        })
    return _thermal_zone_markup(building_gml_id, footprint, height_m, storeys, surfaces)


_SURFACE_BLOCK = re.compile(
    r'<bldg:boundedBy><bldg:(GroundSurface|WallSurface|RoofSurface) gml:id="([^"]+)">(.*?)</bldg:\1></bldg:boundedBy>'
)
_HEIGHT = re.compile(r'<bldg:measuredHeight uom="m">([^<]+)</bldg:measuredHeight>')
_STOREYS = re.compile(r"<bldg:storeysAboveGround>(\d+)</bldg:storeysAboveGround>")
_AREA = re.compile(r'<nrg3:bdgBdrySurfTotalSurfaceArea uom="m\^2">([^<]+)</nrg3:bdgBdrySurfTotalSurfaceArea>')
_CONSTRUCTION = re.compile(r'<nrg3:layeredConstruction xlink:href="([^"]+)"/>')
_POLYGON = re.compile(r'<gml:Polygon gml:id="([^"]+)"')
_AZIMUTH = re.compile(r'<nrg3:bdgBdrySurfAzimuth uom="decimal degree">([^<]+)</nrg3:bdgBdrySurfAzimuth>')
_INCLINATION = re.compile(r'<nrg3:bdgBdrySurfInclination uom="decimal degree">([^<]+)</nrg3:bdgBdrySurfInclination>')
_ADIABATIC = re.compile(r"<nrg3:bdgBdrySurfIsAdiabatic>([^<]+)</nrg3:bdgBdrySurfIsAdiabatic>")
_OPENING = re.compile(
    r'<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">([^<]+)</nrg3:bdgBdrySurfOpeningToSurfaceRatio>'
)


def _zone_for_building_line(line: str) -> str:
    """Append one thermal zone to a building that does not have one yet."""
    if "<bldg:Building " not in line or "<nrg3:thermalZone>" in line:
        return line
    building_gml_id = re.search(r'<bldg:Building gml:id="([^"]+)"', line).group(1)
    height = _HEIGHT.search(line)
    storeys = _STOREYS.search(line)
    surfaces = []
    footprint = None
    for kind, surface_id, body in _SURFACE_BLOCK.findall(line):
        area = _AREA.search(body).group(1)
        if kind == "GroundSurface":
            footprint = float(area) if footprint is None else footprint + float(area)
        construction = _CONSTRUCTION.search(body)
        surfaces.append({
            "surface_type": kind,
            "surface_id": surface_id,
            "construction_href": construction.group(1) if construction else None,
            "polygon_id": _POLYGON.search(body).group(1),
            "azimuth": _AZIMUTH.search(body).group(1),
            "inclination": _INCLINATION.search(body).group(1),
            "adiabatic": _ADIABATIC.search(body).group(1),
            "opening": _OPENING.search(body).group(1),
            "area": area,
        })
    zone = _thermal_zone_markup(
        building_gml_id,
        footprint,
        float(height.group(1)) if height else None,
        int(storeys.group(1)) if storeys else None,
        surfaces,
    )
    return line.replace("</bldg:Building>", zone + "</bldg:Building>", 1)


def add_thermal_zones(path: str | Path) -> Path:
    """Write one thermal zone onto every building. Leaves a building that already has one."""
    source = Path(path)
    temporary = source.with_suffix(source.suffix + ".tmp")
    buildings = 0
    with source.open(encoding="utf-8") as incoming, temporary.open("w", encoding="utf-8") as outgoing:
        for line in incoming:
            updated = _zone_for_building_line(line)
            if updated is not line and "<nrg3:thermalZone>" in updated:
                buildings += 1
            outgoing.write(updated)
    temporary.replace(source)
    return source


def _device_xml(device: pd.Series) -> str:
    name = device["eureca_name"]
    if not isinstance(name, str):
        return ""
    element = device["device_element"]
    device_id = f"b_{device['building_id']}_heating"
    lines = [
        "<nrg3:device>",
        f'<nrg3:{element} gml:id="{device_id}">',
        f'<gml:name codeSpace="{escape(device["eureca_codespace"])}">{escape(name)}</gml:name>',
        "<nrg3:deviceOperation>",
        f'<nrg3:DeviceOperation gml:id="{device_id}_operation">',
        "<nrg3:type>spaceHeating</nrg3:type>",
        "</nrg3:DeviceOperation></nrg3:deviceOperation>",
    ]
    if element == "Boiler":
        lines.append(f'<nrg3:hasCondensation>{device["has_condensation"]}</nrg3:hasCondensation>')
    if element == "HeatPump":
        lines.append(f'<nrg3:heatSource>{escape(device["heat_source"])}</nrg3:heatSource>')
    lines.append(f"</nrg3:{element}></nrg3:device>")
    return "".join(lines)


def _library_xml(surfaces: gpd.GeoDataFrame) -> str:
    library = (
        surfaces.dropna(subset=["construction_id"])
        [["construction_id", "u_value", "surface_type"]]
        .dropna(subset=["u_value"])
        .drop_duplicates()
    )
    clashing = library.groupby("construction_id")["u_value"].nunique()
    if (clashing > 1).any():
        offenders = clashing[clashing > 1].index.tolist()
        raise ValueError(
            "One construction id has more than one U-value: " + ", ".join(map(str, offenders))
        )
    lines = [
        "<core:cityObjectMember>",
        '<nrg3:LayeredConstructionLibrary gml:id="torino_constructions">',
        "<gml:name>Torino residential constructions</gml:name>",
        "<nrg3:source>TABULA U-values on the building archetype</nrg3:source>",
    ]
    for construction in library.itertuples(index=False):
        lines.append("<nrg3:libraryMember>")
        lines.append(f'<nrg3:LayeredConstruction gml:id="{escape(construction.construction_id)}">')
        lines.append(f"<gml:name>{escape(construction.construction_id)}</gml:name>")
        lines.append(f'<nrg3:uValue uom="W/(K*m^2)">{construction.u_value}</nrg3:uValue>')
        lines.append("</nrg3:LayeredConstruction></nrg3:libraryMember>")
    lines.append("</nrg3:LayeredConstructionLibrary></core:cityObjectMember>")
    return "".join(lines)


def write_citygml(
    buildings: pd.DataFrame,
    surfaces: gpd.GeoDataFrame,
    devices: pd.DataFrame,
    path: str | Path,
    energy_ade: bool = True,
) -> Path:
    """Write one LoD2 building per row that has a wall.

    energy_ade=True keeps the construction library, devices and thermal zones
    (FME / Energy ADE 3). energy_ade=False is CityGML 2 Building only, which
    Importer/Exporter can load without the LayeredConstructionLibrary NPE.
    """
    output = Path(path)
    usable = surfaces.loc[surfaces["surface_type"].eq("WallSurface"), "building_id"].unique()
    selected = surfaces.loc[surfaces["building_id"].isin(usable)].sort_values(
        ["building_id", "surface_type", "surface_id"]
    )
    attributes = buildings.drop(columns=["lod0_3d_footprint_32632"], errors="ignore")
    attributes = attributes.drop_duplicates("building_id").set_index("building_id", drop=False)
    device_rows = devices.set_index("building_id", drop=False)
    minimum = selected.total_bounds
    z_values = shapely.get_coordinates(selected.geometry.to_numpy(), include_z=True)[:, 2]
    with output.open("w", encoding="utf-8") as handle:
        handle.write('<?xml version="1.0" encoding="utf-8"?>\n')
        handle.write(CITYMODEL_OPEN if energy_ade else CITYMODEL_OPEN_CORE)
        handle.write(
            f'<gml:boundedBy><gml:Envelope srsName="{CRS}" srsDimension="3">'
            f"<gml:lowerCorner>{minimum[0]:.4f} {minimum[1]:.4f} {z_values.min():.4f}</gml:lowerCorner>"
            f"<gml:upperCorner>{minimum[2]:.4f} {minimum[3]:.4f} {z_values.max():.4f}</gml:upperCorner>"
            "</gml:Envelope></gml:boundedBy>"
        )
        if energy_ade:
            handle.write(_library_xml(selected) + "\n")
        else:
            handle.write("\n")
        for building_id, faces in selected.groupby("building_id", sort=False):
            handle.write(
                _building_xml(
                    attributes.loc[building_id],
                    device_rows.loc[building_id],
                    faces,
                    energy_ade=energy_ade,
                )
                + "\n"
            )
        handle.write("</core:CityModel>\n")
    return output


def write_citygml_core(
    buildings: pd.DataFrame,
    surfaces: gpd.GeoDataFrame,
    devices: pd.DataFrame,
    path: str | Path,
) -> Path:
    """CityGML 2 LoD2 buildings for Importer/Exporter. No Energy ADE objects."""
    return write_citygml(buildings, surfaces, devices, path, energy_ade=False)


def strip_energy_ade(source: str | Path, destination: str | Path | None = None) -> Path:
    """Drop nrg3 from an existing CityGML file. Streaming, one line at a time.

    Default destination is the source stem plus _core.gml. Use this on a
    torino_residenziale.gml that already includes the construction library.
    """
    incoming = Path(source)
    outgoing = Path(destination) if destination else incoming.with_name(
        incoming.stem + "_core" + incoming.suffix
    )
    with incoming.open(encoding="utf-8") as reader, outgoing.open("w", encoding="utf-8") as writer:
        for line in reader:
            writer.write(_without_nrg3(line))
    return outgoing


def _without_nrg3(xml: str) -> str:
    xml = _NRG3_NS.sub("", xml)
    xml = _LIBRARY_MEMBER.sub("", xml)
    xml = _NRG3_BLOCK.sub("", xml)
    xml = _NRG3_EMPTY.sub("", xml)
    xml = _NRG3_ELEM.sub("", xml)
    return xml


def _building_xml(
    building: pd.Series,
    device: pd.Series,
    faces: gpd.GeoDataFrame,
    energy_ade: bool = True,
) -> str:
    building_id = building["building_id"]
    lines = [
        "<core:cityObjectMember>",
        f'<bldg:Building gml:id="b_{building_id}">',
        f"<gml:name>building {building_id}</gml:name>",
    ]
    if energy_ade:
        lines.append(_device_xml(device))
    lines.append(
        '<bldg:class codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_class.xml">habitation</bldg:class>'
    )
    lines.append(
        '<bldg:function codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_function.xml">residential building</bldg:function>'
    )
    year = _construction_year(building["construction_period"])
    if year is not None:
        lines.append(f"<bldg:yearOfConstruction>{year}</bldg:yearOfConstruction>")
    height = pd.to_numeric(building["building_height_m"], errors="coerce")
    if np.isfinite(height):
        lines.append(f'<bldg:measuredHeight uom="m">{float(height):.4f}</bldg:measuredHeight>')
    storeys = _storeys_above(building["floor_count_raw"])
    if storeys is not None:
        lines.append(f"<bldg:storeysAboveGround>{storeys}</bldg:storeysAboveGround>")
    for face in faces.itertuples(index=False):
        lines.append(_surface_xml(pd.Series(face._asdict()), energy_ade=energy_ade))
    if energy_ade:
        zone_height = float(height) if np.isfinite(height) else None
        lines.append(_thermal_zone_from_faces(f"b_{building_id}", zone_height, storeys, faces))
    lines.append("</bldg:Building></core:cityObjectMember>")
    return "".join(lines)
