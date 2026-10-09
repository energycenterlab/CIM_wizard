"""Convert report_house.gml (CityGML 2.0 + Energy ADE 3.0 beta 7) to CityJSON.

Writes two documents so they can be compared:
  report_house_v1.1.city.json  + energy-ade3-v1.1.ext.json
  report_house_v2.0.city.json  + energy-ade3-v2.0.ext.json

Core city model stays vanilla so ninja/cjval can view and validate it:
Buildings are type Building. Energy ADE 3 hangs off as +Energy-* CityObjects,
+Energy-* attributes, and +Energy-libraries. Not Tufan's energy-space-heating
schema (KIT / ADE 1), only his layout (Building stays Building).

CityJSON 1.1 has no extraSemanticSurfaces, so party walls draw as WallSurface.
CityJSON 2.0 uses +Energy-PartyWallSurface as a semantic surface.

Validate:
  cjval report_house_v1.1.city.json -e ./energy-ade3-v1.1.ext.json
  cjval report_house_v2.0.city.json -e ./energy-ade3-v2.0.ext.json
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "gml": "http://www.opengis.net/gml",
    "core": "http://www.opengis.net/citygml/2.0",
    "bldg": "http://www.opengis.net/citygml/building/2.0",
    "nrg3": "http://www.citygml.org/ade/energy/3.0",
    "gen": "http://www.opengis.net/citygml/generics/2.0",
    "xAL": "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0",
    "xlink": "http://www.w3.org/1999/xlink",
}

GML_ID = "{http://www.opengis.net/gml}id"
XLINK = "{http://www.w3.org/1999/xlink}href"

LIBRARY_TYPES = {
    "LayeredConstructionLibrary",
    "MaterialLibrary",
    "ScheduleLibrary",
}

CITYOBJECT_TYPES = {
    "Building": "Building",
    "BuildingUnit": "+Energy-BuildingUnit",
    "ThermalZone": "+Energy-ThermalZone",
    "UsageZone": "+Energy-UsageZone",
    "Occupants": "+Energy-Occupants",
    "Boiler": "+Energy-Boiler",
    "HeatPump": "+Energy-HeatPump",
    "Window": "+Energy-Window",
    "Door": "+Energy-Door",
    "GroundSurface": "+Energy-GroundSurface",
    "RoofSurface": "+Energy-RoofSurface",
    "WallSurface": "+Energy-WallSurface",
    "PartyWallSurface": "+Energy-PartyWallSurface",
}

SEMANTIC_SURFACE_CORE = {
    "GroundSurface": "GroundSurface",
    "RoofSurface": "RoofSurface",
    "WallSurface": "WallSurface",
}

ARRAY_BUILDING_ATTR = {"storeyHeightsAboveGround", "storeyHeightsBelowGround"}

BUILDING_CORE_ATTR = {
    "class",
    "function",
    "usage",
    "yearOfConstruction",
    "yearOfDemolition",
    "roofType",
    "measuredHeight",
    "storeysAboveGround",
    "storeysBelowGround",
    "storeyHeightsAboveGround",
    "storeyHeightsBelowGround",
    "description",
    "name",
    "creationDate",
}

CHILD_WRAPPERS = {
    "buildingUnit",
    "thermalZone",
    "usageZone",
    "occupiedBy",
    "device",
    "thermalBoundary",
    "opening",
}

GEOM_WRAPPER = re.compile(r"^lod(\d)(Solid|MultiSurface|FootPrint|RoofEdge)$")

SKIP_LOCAL = {
    "boundedBy",  # Envelope on CityModel; building boundedBy handled separately
}


def ln(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def href(el: ET.Element | None) -> str | None:
    if el is None:
        return None
    raw = el.get(XLINK)
    if not raw:
        return None
    return raw[1:] if raw.startswith("#") else raw


def text(el: ET.Element | None) -> str | None:
    if el is None or el.text is None:
        return None
    t = el.text.strip()
    return t if t else None


def coerce(s: str):
    if s in ("true", "false"):
        return s == "true"
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    return s


def measure(el: ET.Element) -> dict:
    out = {"value": coerce(text(el) or "")}
    if el.get("uom"):
        out["uom"] = el.get("uom")
    if el.get("codeSpace"):
        out["codeSpace"] = el.get("codeSpace")
    if el.get("unit"):
        out["unit"] = el.get("unit")
    return out


class Converter:
    def __init__(self, version: str):
        self.version = version
        self.polygons: dict[str, list] = {}
        self.city_objects: dict[str, dict] = {}
        self.raw_vertices: list[tuple[float, float, float]] = []
        self.vertex_map: dict[tuple, int] = {}
        self.libraries: dict[str, dict] = {}

    def semantic_type(self, gml_type: str) -> str:
        if gml_type == "PartyWallSurface":
            return "+Energy-PartyWallSurface" if self.version == "2.0" else "WallSurface"
        return SEMANTIC_SURFACE_CORE.get(gml_type, gml_type)

    def vidx(self, x: float, y: float, z: float) -> int:
        key = (round(x, 4), round(y, 4), round(z, 4))
        i = self.vertex_map.get(key)
        if i is None:
            i = len(self.raw_vertices)
            self.vertex_map[key] = i
            self.raw_vertices.append(key)
        return i

    def ring(self, coords: list[tuple[float, float, float]]) -> list[int]:
        if len(coords) >= 2 and coords[0] == coords[-1]:
            coords = coords[:-1]
        return [self.vidx(*c) for c in coords]

    def pos_list(self, el: ET.Element) -> list[tuple[float, float, float]]:
        nums = [float(x) for x in (text(el) or "").split()]
        return [tuple(nums[i : i + 3]) for i in range(0, len(nums), 3)]  # type: ignore

    def polygon_rings(self, poly: ET.Element) -> list[list[int]] | None:
        ext = poly.find(".//gml:exterior/gml:LinearRing/gml:posList", NS)
        if ext is None:
            return None
        rings = [self.ring(self.pos_list(ext))]
        for inter in poly.findall(".//gml:interior/gml:LinearRing/gml:posList", NS):
            rings.append(self.ring(self.pos_list(inter)))
        return rings

    def index_polygons(self, root: ET.Element):
        for poly in root.iter(f"{{{NS['gml']}}}Polygon"):
            pid = poly.get(GML_ID)
            if not pid:
                continue
            rings = self.polygon_rings(poly)
            if rings:
                self.polygons[pid] = rings

    def resolve_polygon(self, member: ET.Element) -> list[list[int]] | None:
        ref = href(member)
        if ref:
            return self.polygons.get(ref)
        poly = member.find("gml:Polygon", NS)
        if poly is None:
            poly = member.find("gml:OrientableSurface//gml:Polygon", NS)
        if poly is None:
            return None
        pid = poly.get(GML_ID)
        if pid and pid in self.polygons:
            return self.polygons[pid]
        return self.polygon_rings(poly)

    def multi_surface(self, node: ET.Element) -> list | None:
        faces = []
        for member in node.findall(".//gml:surfaceMember", NS):
            rings = self.resolve_polygon(member)
            if rings:
                faces.append(rings)
        return faces or None

    def solid(self, node: ET.Element) -> list | None:
        faces = self.multi_surface(node)
        return [faces] if faces else None

    def geom_from_wrapper(self, el: ET.Element) -> dict | None:
        m = GEOM_WRAPPER.match(ln(el.tag))
        if not m:
            return None
        lod, kind = m.group(1), m.group(2)
        lod_s = f"{lod}.0"
        if kind == "Solid":
            b = self.solid(el)
            if not b:
                return None
            return {"type": "Solid", "lod": lod_s, "boundaries": b}
        b = self.multi_surface(el)
        if not b:
            return None
        gtype = "MultiSurface"
        return {"type": gtype, "lod": lod_s, "boundaries": b}

    def point(self, el: ET.Element | None) -> list[float] | None:
        if el is None:
            return None
        pos = el.find(".//gml:pos", NS)
        if pos is None:
            return None
        return [float(x) for x in (text(pos) or "").split()]

    def simple_value(self, el: ET.Element):
        children = [c for c in list(el) if ln(c.tag) != "name"]
        if not list(el) or (
            text(el) is not None
            and not any(ln(c.tag) not in ("name",) for c in list(el))
            and el.get("uom") is None
            and el.get("codeSpace") is None
        ):
            t = text(el)
            if t is None:
                return None
            return coerce(t)
        if el.get("uom") or el.get("codeSpace") or el.get("unit"):
            if text(el) is not None and not [c for c in list(el) if ln(c.tag) not in ()]:
                return measure(el)
            if text(el) is not None and len(list(el)) == 0:
                return measure(el)
        if text(el) is not None and len(list(el)) == 0:
            if el.get("uom") or el.get("codeSpace") or el.get("unit"):
                return measure(el)
            return coerce(text(el))
        return None

    def names(self, el: ET.Element) -> str | list | None:
        found = []
        for n in el.findall("gml:name", NS):
            item = {"value": text(n)}
            if n.get("codeSpace"):
                item["codeSpace"] = n.get("codeSpace")
            found.append(item if n.get("codeSpace") else item["value"])
        if not found:
            return None
        return found[0] if len(found) == 1 else found

    def qualified(self, el: ET.Element) -> dict:
        out = {}
        for child in el:
            k = ln(child.tag)
            if k in ("description", "source"):
                out[k] = text(child)
            elif k in ("value", "type"):
                out[k] = measure(child) if (child.get("uom") or child.get("codeSpace")) else coerce(text(child) or "")
        return out

    def optical(self, el: ET.Element) -> dict:
        out = {}
        for child in el:
            k = ln(child.tag)
            t = text(child)
            if t is None:
                continue
            if child.get("uom"):
                out[k] = measure(child)
            else:
                out[k] = coerce(t)
        return out

    def generic_attrs(self, el: ET.Element) -> dict:
        out = {}
        for child in list(el):
            k = ln(child.tag)
            if k not in ("stringAttribute", "doubleAttribute", "intAttribute"):
                continue
            name = child.get("name")
            val_el = child.find("gen:value", NS)
            if name and val_el is not None:
                out[name] = coerce(text(val_el) or "")
        return out

    def address(self, el: ET.Element) -> dict:
        out = {}
        country = el.find(".//xAL:CountryName", NS)
        code = el.find(".//xAL:CountryNameCode", NS)
        loc = el.find(".//xAL:LocalityName", NS)
        street = el.find(".//xAL:ThoroughfareName", NS)
        num = el.find(".//xAL:ThoroughfareNumber", NS)
        postal = el.find(".//xAL:PostalCodeNumber", NS)
        if country is not None:
            out["country"] = text(country)
        if code is not None:
            out["countryCode"] = text(code)
        if loc is not None:
            out["city"] = text(loc)
        if street is not None:
            out["thoroughfareName"] = text(street)
        if num is not None:
            out["thoroughfareNumber"] = text(num)
        if postal is not None:
            out["postalCode"] = text(postal)
        return out

    def library_member(self, el: ET.Element) -> dict:
        obj = {"type": ln(el.tag)}
        gid = el.get(GML_ID)
        if gid:
            obj["id"] = gid
        desc = text(el.find("gml:description", NS))
        if desc:
            obj["description"] = desc
        nm = self.names(el)
        if nm is not None:
            obj["name"] = nm
        for child in list(el):
            k = ln(child.tag)
            if k in ("description", "name"):
                continue
            if k in ("emissivity", "reflectance", "transmittance"):
                inner = child[0] if len(child) else child
                obj.setdefault(k, []).append(self.optical(inner))
                continue
            if k == "layer":
                inner = child.find("nrg3:Layer", NS)
                obj.setdefault("layers", []).append(self.library_member(inner) if inner is not None else self.library_member(child))
                continue
            if k == "timeSeries":
                inner = child[0] if len(child) else child
                obj["timeSeries"] = self.library_member(inner)
                continue
            if k == "scheduleComponent":
                inner = child.find("nrg3:ScheduleComponent", NS)
                obj.setdefault("scheduleComponents", []).append(
                    self.library_member(inner) if inner is not None else self.library_member(child)
                )
                continue
            if k == "valuesList":
                nums = [coerce(x) for x in (text(child) or "").split()]
                obj[k] = {"values": nums, "uom": child.get("uom")}
                continue
            ref = href(child)
            if ref:
                obj[k] = {"href": ref}
                continue
            if len(child) == 0:
                val = measure(child) if (child.get("uom") or child.get("codeSpace") or child.get("unit")) else (
                    coerce(text(child)) if text(child) is not None else None
                )
                if val is not None:
                    obj[k] = val
                continue
            if ln(child.tag) in ("Emissivity", "Reflectance", "Transmittance"):
                obj.setdefault(k.lower(), []).append(self.optical(child))
        return obj

    def add_library(self, el: ET.Element):
        lib = {
            "type": ln(el.tag),
            "id": el.get(GML_ID),
            "description": text(el.find("gml:description", NS)),
            "name": self.names(el),
            "members": [],
        }
        for child in list(el):
            k = ln(child.tag)
            if k in ("description", "name"):
                continue
            if k == "libraryMember":
                inner = child[0] if len(child) else None
                if inner is not None:
                    lib["members"].append(self.library_member(inner))
                continue
            if k in ("type", "source", "author"):
                lib[k] = measure(child) if child.get("codeSpace") else text(child)
        key = {
            "LayeredConstructionLibrary": "layeredConstructionLibrary",
            "MaterialLibrary": "materialLibrary",
            "ScheduleLibrary": "scheduleLibrary",
        }[ln(el.tag)]
        self.libraries[key] = lib

    def surface_semantics(self, el: ET.Element) -> dict:
        # Only "type" belongs on a core semantic surface. Extra ADE fields
        # live on the +Energy-* thermal-boundary CityObjects, or cjval fails.
        return {"type": self.semantic_type(ln(el.tag))}

    def building_geometry(self, bldg: ET.Element) -> list:
        geoms = []
        for child in list(bldg):
            g = self.geom_from_wrapper(child)
            if g:
                geoms.append(g)
        by_lod: dict[str, list] = {}
        semantics_by_lod: dict[str, list] = {}
        for bb in bldg.findall("bldg:boundedBy", NS):
            surf = bb[0] if len(bb) else None
            if surf is None:
                continue
            sem = self.surface_semantics(surf)
            for gwrap in list(surf):
                gm = self.geom_from_wrapper(gwrap)
                if not gm:
                    continue
                lod = gm["lod"]
                by_lod.setdefault(lod, [])
                semantics_by_lod.setdefault(lod, [])
                for face in gm["boundaries"]:
                    by_lod[lod].append(face)
                    semantics_by_lod[lod].append(sem)
        for lod, faces in by_lod.items():
            geoms.append({
                "type": "MultiSurface",
                "lod": lod,
                "boundaries": faces,
                "semantics": {
                    "surfaces": semantics_by_lod[lod],
                    "values": list(range(len(faces))),
                },
            })
        return geoms

    def collect_attrs(self, el: ET.Element, skip: set[str]) -> dict:
        attrs: dict = {}
        desc = text(el.find("gml:description", NS))
        if desc:
            attrs["description"] = desc
        nm = self.names(el)
        if nm is not None:
            attrs["name"] = nm
        created = text(el.find("core:creationDate", NS))
        if created:
            attrs["creationDate"] = created
        gen = self.generic_attrs(el)
        if gen:
            attrs["genericAttributes"] = gen
        rp = self.point(el.find("nrg3:referencePoint", NS))
        if rp:
            attrs["referencePoint"] = rp
        for child in list(el):
            k = ln(child.tag)
            if k in skip or k in ("description", "name", "creationDate", "referencePoint") or k in (
                "stringAttribute", "doubleAttribute", "intAttribute",
            ):
                continue
            if GEOM_WRAPPER.match(k):
                continue
            if k in CHILD_WRAPPERS:
                continue
            if k == "boundedBy":
                continue
            if k == "address":
                ref = href(child)
                if ref:
                    attrs["address"] = {"href": ref}
                else:
                    addr = child.find("core:Address", NS)
                    if addr is not None:
                        attrs["address"] = self.address(addr)
                        aid = addr.get(GML_ID)
                        if aid:
                            attrs["address"]["id"] = aid
                continue
            if k in ("bdgArea", "bdgHeight", "bdgVolume", "area", "volume"):
                inner = child[0] if len(child) else child
                attrs.setdefault(k, []).append(self.qualified(inner))
                continue
            if k == "deviceOperation":
                inner = child.find("nrg3:DeviceOperation", NS)
                if inner is not None:
                    op = {"id": inner.get(GML_ID), "type": text(inner.find("nrg3:type", NS))}
                    yge = inner.find("nrg3:yearlyGlobalEfficiency", NS)
                    if yge is not None:
                        op["yearlyGlobalEfficiency"] = coerce(text(yge) or "")
                    sch = href(inner.find("nrg3:schedule", NS))
                    if sch:
                        op["schedule"] = sch
                    attrs.setdefault("deviceOperation", []).append(op)
                continue
            ref = href(child)
            if ref:
                attrs[k] = ref
                continue
            if len(child) == 0:
                val = measure(child) if (child.get("uom") or child.get("codeSpace") or child.get("unit")) else (
                    coerce(text(child)) if text(child) is not None else None
                )
                if val is not None:
                    attrs[k] = val
        return attrs

    def add_city_object(self, el: ET.Element, parent_id: str | None) -> str | None:
        gid = el.get(GML_ID)
        if not gid:
            return None
        ctype = CITYOBJECT_TYPES.get(ln(el.tag))
        if not ctype:
            return None
        attrs = self.collect_attrs(el, set())
        if ln(el.tag) == "Building":
            def _core_val(v):
                if isinstance(v, dict) and "value" in v:
                    return v["value"]
                return v

            attrs = {
                (k if k in BUILDING_CORE_ATTR else f"+Energy-{k}"): (
                    _core_val(v) if k in BUILDING_CORE_ATTR else v
                )
                for k, v in attrs.items()
            }
            for ak in ARRAY_BUILDING_ATTR:
                if ak in attrs and not isinstance(attrs[ak], list):
                    attrs[ak] = [attrs[ak]]
        obj: dict = {"type": ctype, "attributes": attrs}
        addr = obj["attributes"].pop("+Energy-address", None)
        if addr is None:
            addr = obj["attributes"].pop("address", None)
        if addr is not None and ln(el.tag) == "Building":
            obj["address"] = [addr] if isinstance(addr, dict) else addr
        if parent_id:
            obj["parents"] = [parent_id]
        geoms = []
        if ln(el.tag) == "Building":
            geoms = self.building_geometry(el)
        else:
            for child in list(el):
                g = self.geom_from_wrapper(child)
                if g:
                    geoms.append(g)
            if ln(el.tag) in SEMANTIC_SURFACE_CORE or ln(el.tag) == "PartyWallSurface":
                by_lod: dict[str, list] = {}
                for child in list(el):
                    g = self.geom_from_wrapper(child)
                    if g:
                        geoms.append(g)
        if geoms:
            obj["geometry"] = geoms
        children = []
        for child in list(el):
            k = ln(child.tag)
            if k not in CHILD_WRAPPERS:
                continue
            inner = child[0] if len(child) else None
            if inner is None:
                continue
            cid = self.add_city_object(inner, gid)
            if cid:
                children.append(cid)
        if children:
            obj["children"] = children
        self.city_objects[gid] = obj
        return gid

    def convert(self, gml_path: Path) -> dict:
        tree = ET.parse(gml_path)
        root = tree.getroot()
        self.index_polygons(root)
        desc = text(root.find("gml:description", NS))
        name = text(root.find("gml:name", NS))
        env = root.find("gml:boundedBy/gml:Envelope", NS)
        srs = env.get("srsName") if env is not None else "EPSG:32633"
        extent = None
        if env is not None:
            lo = [float(x) for x in (text(env.find("gml:lowerCorner", NS)) or "").split()]
            hi = [float(x) for x in (text(env.find("gml:upperCorner", NS)) or "").split()]
            if len(lo) == 3 and len(hi) == 3:
                extent = lo + hi
        for member in root.findall("core:cityObjectMember", NS):
            child = member[0] if len(member) else None
            if child is None:
                continue
            if ln(child.tag) in LIBRARY_TYPES:
                self.add_library(child)
            else:
                self.add_city_object(child, None)
        translate = [0.0, 0.0, 0.0]
        scale = [0.001, 0.001, 0.001]
        int_vertices = []
        if self.raw_vertices:
            xs, ys, zs = zip(*self.raw_vertices)
            translate = [min(xs), min(ys), min(zs)]
            int_vertices = [
                [
                    round((v[0] - translate[0]) / scale[0]),
                    round((v[1] - translate[1]) / scale[1]),
                    round((v[2] - translate[2]) / scale[2]),
                ]
                for v in self.raw_vertices
            ]
        epsg = srs.split(":")[-1] if srs else "32633"
        ext_name = f"./energy-ade3-v{self.version}.ext.json"
        return {
            "type": "CityJSON",
            "version": self.version,
            "extensions": {
                "EnergyADE3": {
                    "url": ext_name,
                    "version": "0.1",
                }
            },
            "metadata": {
                "identifier": "report_house",
                "title": name if not desc else f"{name}. {desc}",
                "referenceSystem": f"https://www.opengis.net/def/crs/EPSG/0/{epsg}",
                **({"geographicalExtent": extent} if extent else {}),
            },
            "transform": {"scale": scale, "translate": translate},
            "+Energy-libraries": self.libraries,
            "CityObjects": self.city_objects,
            "vertices": int_vertices,
        }


EXTRA_CITY_OBJECTS = [
    "+Energy-BuildingUnit",
    "+Energy-ThermalZone",
    "+Energy-UsageZone",
    "+Energy-Occupants",
    "+Energy-Boiler",
    "+Energy-HeatPump",
    "+Energy-Window",
    "+Energy-Door",
    "+Energy-GroundSurface",
    "+Energy-RoofSurface",
    "+Energy-WallSurface",
    "+Energy-PartyWallSurface",
]

BUILDING_EXTRA_ATTRIBUTES = {
    "+Energy-referencePoint": {"type": "array"},
    "+Energy-bdgArea": {"type": "array"},
    "+Energy-bdgHeight": {"type": "array"},
    "+Energy-bdgVolume": {"type": "array"},
    "+Energy-bdgAtticThermalStatus": {"type": "string"},
    "+Energy-bdgBasementThermalStatus": {"type": "string"},
    "+Energy-bdgConstructionWeight": {"type": "object"},
    "+Energy-bdgIsProtected": {"type": "boolean"},
    "+Energy-bdgType": {"type": "object"},
}


def extra_city_object(name: str) -> dict:
    return {
        "allOf": [
            {"$ref": "cityobjects.schema.json#/_AbstractCityObject"},
            {
                "properties": {
                    "type": {"enum": [name]},
                    "attributes": {"type": "object"},
                },
                "required": ["type"],
            },
        ]
    }


def extension_for(version: str) -> dict:
    ext = {
        "type": "CityJSONExtension",
        "name": "EnergyADE3",
        "uri": f"./energy-ade3-v{version}.ext.json",
        "version": "0.1",
        "versionCityJSON": version,
        "description": (
            f"Energy ADE 3.0 beta 7 extras on CityJSON {version}. "
            "Core objects stay Building so ninja and cjval can read the "
            "geometry. ADE 3 libraries, zones, devices and party-wall "
            "CityObjects are +Energy-* extras. Not the registry "
            "energy-space-heating extension (KIT / ADE 1)."
        ),
        "extraRootProperties": {
            "+Energy-libraries": {"type": "object"}
        },
        "extraAttributes": {
            "Building": copy.deepcopy(BUILDING_EXTRA_ATTRIBUTES)
        },
        "extraCityObjects": {name: extra_city_object(name) for name in EXTRA_CITY_OBJECTS},
    }
    if version == "2.0":
        ext["extraSemanticSurfaces"] = {
            "+Energy-PartyWallSurface": {
                "type": "object",
                "properties": {
                    "type": {"enum": ["+Energy-PartyWallSurface"]}
                },
                "required": ["type"],
            }
        }
        ext["description"] += (
            " Party walls use extraSemanticSurfaces +Energy-PartyWallSurface."
        )
    else:
        ext["description"] += (
            " Party walls draw as WallSurface (no extraSemanticSurfaces in 1.1)."
        )
    return ext


def main():
    here = Path(__file__).resolve().parent
    gml = here / "report_house.gml"
    for version in ("1.1", "2.0"):
        city = Converter(version).convert(gml)
        out = here / f"report_house_v{version}.city.json"
        ext_path = here / f"energy-ade3-v{version}.ext.json"
        out.write_text(json.dumps(city, indent=2) + "\n")
        ext_path.write_text(json.dumps(extension_for(version), indent=2) + "\n")
        types = {}
        for obj in city["CityObjects"].values():
            types[obj["type"]] = types.get(obj["type"], 0) + 1
        print(f"wrote {out.name} ({out.stat().st_size} bytes)  CityJSON {version}")
        print(f"  CityObjects: {len(city['CityObjects'])}  vertices: {len(city['vertices'])}")
        print(f"  types: {types}")
        print(f"wrote {ext_path.name}")
    stale = [
        here / "report_house.city.json",
        here / "energy-ade3.ext.json",
    ]
    for path in stale:
        if path.exists():
            path.unlink()
            print(f"removed {path.name}")


if __name__ == "__main__":
    main()
