"""Rewrite i-UR (uro) attributes in a CityGML 2.0 file as core CityGML properties.

The geometry is left unchanged. Each uro value is copied onto elements the
stock CityGML 2.0 schema already allows, so the result can be validated and
imported into 3DCityDB without an ADE:

- uro:globalId -> core:externalReference (informationSystem IFC/<IfcClass>)
- uro:name -> gml:name when the feature has none, otherwise a string attribute
- element type, operation, shape, tag, IFC class, unit names -> gen:stringAttribute
- storey elevation -> gen:measureAttribute
- uro:buildingAddress -> bldg:address

Generic attributes and external references are inserted before the first
building or group property. They are not legal in the ADE slot after lod geometry,
which is where the uro blocks sit.
"""

from __future__ import annotations

import sys
from pathlib import Path

from lxml import etree

URO = "https://www.geospatial.jp/iur/uro/3.1"
BLDG = "http://www.opengis.net/citygml/building/2.0"
CORE = "http://www.opengis.net/citygml/2.0"
GEN = "http://www.opengis.net/citygml/generics/2.0"
GML = "http://www.opengis.net/gml"
GRP = "http://www.opengis.net/citygml/cityobjectgroup/2.0"
APP = "http://www.opengis.net/citygml/appearance/2.0"
XAL = "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0"
XLINK = "http://www.w3.org/1999/xlink"
XSI = "http://www.w3.org/2001/XMLSchema-instance"

WRAPPERS = {
    "ifcBuildingInstallationAttribute",
    "ifcBoundarySurfaceAttribute",
    "ifcBuildingAttribute",
    "ifcBuildingStoreyAttribute",
}

# Children of AbstractGML / AbstractFeature / AbstractCityObject that must
# stay ahead of gen:*Attribute. gml:boundedBy is not bldg:boundedBy.
HEADER = {
    (GML, "metaDataProperty"),
    (GML, "description"),
    (GML, "descriptionReference"),
    (GML, "identifier"),
    (GML, "name"),
    (GML, "boundedBy"),
    (GML, "location"),
    (CORE, "creationDate"),
    (CORE, "terminationDate"),
    (CORE, "externalReference"),
    (CORE, "generalizesTo"),
    (CORE, "relativeToTerrain"),
    (CORE, "relativeToWater"),
}

STRING_ATTR = {
    "elementType": "ifcElementType",
    "operationType": "ifcOperationType",
    "shapeType": "ifcShapeType",
    "tag": "ifcTag",
}

UNIT_ATTR = {
    "AREAUNIT": "ifcAreaUnit",
    "LENGTHUNIT": "ifcLengthUnit",
    "PLANEANGLEUNIT": "ifcAngleUnit",
    "VOLUMEUNIT": "ifcVolumeUnit",
}


def q(ns: str, tag: str) -> str:
    return f"{{{ns}}}{tag}"


def local(el: etree._Element) -> str:
    return etree.QName(el).localname


def ns_of(el: etree._Element) -> str | None:
    return etree.QName(el).namespace


def text_of(el: etree._Element) -> str:
    if el.text is None or not el.text.strip():
        raise ValueError(f"empty <{local(el)}> under {el.getroottree().getpath(el)}")
    return el.text.strip()


def string_attribute(name: str, value: str) -> etree._Element:
    el = etree.Element(q(GEN, "stringAttribute"))
    el.set("name", name)
    etree.SubElement(el, q(GEN, "value")).text = value
    return el


def measure_attribute(name: str, value: str, uom: str | None) -> etree._Element:
    el = etree.Element(q(GEN, "measureAttribute"))
    el.set("name", name)
    value_el = etree.SubElement(el, q(GEN, "value"))
    if uom:
        value_el.set("uom", uom)
    value_el.text = value
    return el


def external_reference(ifc_class: str, global_id: str) -> etree._Element:
    el = etree.Element(q(CORE, "externalReference"))
    etree.SubElement(el, q(CORE, "informationSystem")).text = f"IFC/{ifc_class}"
    obj = etree.SubElement(el, q(CORE, "externalObject"))
    etree.SubElement(obj, q(CORE, "name")).text = global_id
    return el


def gml_name(value: str) -> etree._Element:
    el = etree.Element(q(GML, "name"))
    el.text = value
    return el


def direct_child(parent: etree._Element, ns: str, tag: str) -> etree._Element | None:
    for child in parent:
        if ns_of(child) == ns and local(child) == tag:
            return child
    return None


def header_index(parent: etree._Element) -> int:
    """First child that is not a CityObject header property.

    gen:* attributes are not headers, so a later insert lands in front of
    them and external references stay before generic attributes.
    """
    for i, child in enumerate(parent):
        if (ns_of(child), local(child)) not in HEADER:
            return i
    return len(list(parent))


def insert_at(parent: etree._Element, index: int, nodes: list[etree._Element]) -> None:
    for offset, node in enumerate(nodes):
        parent.insert(index + offset, node)


def one_child(el: etree._Element, name: str) -> etree._Element:
    found = [child for child in el if local(child) == name and ns_of(child) == URO]
    if len(found) != 1:
        raise ValueError(f"<{local(el)}> has {len(found)} <{name}> children")
    return found[0]


def convert_units(units_el: etree._Element) -> etree._Element:
    unit = one_child(units_el, "IfcUnit")
    extra = [child for child in units_el if child is not unit]
    if extra:
        raise ValueError(f"unexpected child <{local(extra[0])}> in unitsInContext")
    unit_type_el = one_child(unit, "unitType")
    unit_name_el = one_child(unit, "name")
    extra_unit = [child for child in unit if child not in (unit_type_el, unit_name_el)]
    if extra_unit:
        raise ValueError(f"unexpected child <{local(extra_unit[0])}> in IfcUnit")
    unit_type = text_of(unit_type_el)
    attr = UNIT_ATTR.get(unit_type)
    if attr is None:
        raise ValueError(f"unknown IFC unit type {unit_type}")
    return string_attribute(attr, text_of(unit_name_el))


def take_address(address_el: etree._Element) -> etree._Element:
    addresses = [child for child in address_el if ns_of(child) == CORE and local(child) == "Address"]
    if len(addresses) != 1:
        raise ValueError(f"buildingAddress has {len(addresses)} core:Address children")
    extra = [child for child in address_el if child is not addresses[0]]
    if extra:
        raise ValueError(f"unexpected child <{local(extra[0])}> in buildingAddress")
    wrapper = etree.Element(q(BLDG, "address"))
    wrapper.append(addresses[0])
    return wrapper


def convert_ifc(ifc_el: etree._Element, feature: etree._Element) -> tuple[list[etree._Element], etree._Element | None]:
    ifc_class = local(ifc_el)
    if ns_of(ifc_el) != URO:
        raise ValueError(f"expected a uro object, found <{ifc_class}>")
    header: list[etree._Element] = []
    attrs: list[etree._Element] = [string_attribute("ifcClass", ifc_class)]
    address = None
    seen_name = False

    for child in list(ifc_el):
        if ns_of(child) != URO:
            raise ValueError(f"unexpected <{ns_of(child)}:{local(child)}> in {ifc_class}")
        name = local(child)
        if name == "globalId":
            header.append(external_reference(ifc_class, text_of(child)))
        elif name == "name":
            seen_name = True
            value = text_of(child)
            existing = direct_child(feature, GML, "name")
            if existing is None:
                feature.insert(0, gml_name(value))
            elif (existing.text or "").strip() != value:
                attrs.append(string_attribute(f"ifc{ifc_class.removeprefix('Ifc')}Name", value))
        elif name in STRING_ATTR:
            attrs.append(string_attribute(STRING_ATTR[name], text_of(child)))
        elif name == "elevation":
            attrs.append(measure_attribute("storeyElevation", text_of(child), child.get("uom")))
        elif name == "unitsInContext":
            attrs.append(convert_units(child))
        elif name == "buildingAddress":
            if address is not None:
                raise ValueError("more than one buildingAddress")
            address = take_address(child)
        else:
            raise ValueError(f"unexpected <{name}> in {ifc_class}")

    if not any(local(el) == "externalReference" for el in header):
        raise ValueError(f"{ifc_class} has no globalId")
    if seen_name and direct_child(feature, GML, "name") is None and not any(
        el.get("name", "").endswith("Name") for el in attrs
    ):
        raise ValueError(f"{ifc_class} name was not written")
    return header + attrs, address


def convert_wrapper(wrapper: etree._Element) -> str:
    feature = wrapper.getparent()
    if feature is None:
        raise ValueError("uro wrapper has no parent")
    ifc_children = [child for child in wrapper if ns_of(child) == URO]
    if len(ifc_children) != 1:
        raise ValueError(f"<{local(wrapper)}> has {len(ifc_children)} uro children")
    nodes, address = convert_ifc(ifc_children[0], feature)
    insert_at(feature, header_index(feature), nodes)
    if address is not None:
        feature.insert(list(feature).index(wrapper), address)
    ifc_class = local(ifc_children[0])
    feature.remove(wrapper)
    return ifc_class


def drop_uro_schema(root: etree._Element) -> None:
    schema = root.get(q(XSI, "schemaLocation"))
    if not schema:
        return
    parts = schema.split()
    kept: list[str] = []
    i = 0
    while i < len(parts):
        if parts[i] == URO:
            i += 2
            continue
        kept.append(parts[i])
        i += 1
    root.set(q(XSI, "schemaLocation"), " ".join(kept))


def convert(source: Path, target: Path) -> None:
    for prefix, uri in {
        "app": APP,
        "bldg": BLDG,
        "core": CORE,
        "gen": GEN,
        "gml": GML,
        "grp": GRP,
        "xAL": XAL,
        "xlink": XLINK,
        "xsi": XSI,
    }.items():
        etree.register_namespace(prefix, uri)

    tree = etree.parse(str(source))
    root = tree.getroot()
    wrappers = [
        el for el in root.iter()
        if ns_of(el) == URO and local(el) in WRAPPERS
    ]
    if not wrappers:
        raise SystemExit(f"no uro attribute blocks in {source}")

    counts: dict[str, int] = {}
    for wrapper in wrappers:
        ifc_class = convert_wrapper(wrapper)
        counts[ifc_class] = counts.get(ifc_class, 0) + 1

    leftover = [el for el in root.iter() if ns_of(el) == URO]
    if leftover:
        raise SystemExit(f"{len(leftover)} uro elements remain, first is <{local(leftover[0])}>")

    drop_uro_schema(root)
    etree.cleanup_namespaces(tree)

    target.parent.mkdir(parents=True, exist_ok=True)
    tree.write(
        str(target),
        xml_declaration=True,
        encoding="UTF-8",
        pretty_print=True,
    )

    written = etree.parse(str(target))
    written_root = written.getroot()
    still_uro = [el for el in written_root.iter() if ns_of(el) == URO or URO in (el.nsmap or {}).values()]
    schema = written_root.get(q(XSI, "schemaLocation")) or ""
    if still_uro or URO in schema or URO in (written_root.nsmap or {}).values():
        raise SystemExit("output still references the uro namespace")

    print(f"wrote {target}")
    for ifc_class, count in sorted(counts.items()):
        print(f"  {ifc_class}: {count}")
    print(f"  externalReference: {len(written_root.findall('.//' + q(CORE, 'externalReference')))}")
    print(f"  stringAttribute: {len(written_root.findall('.//' + q(GEN, 'stringAttribute')))}")
    print(f"  measureAttribute: {len(written_root.findall('.//' + q(GEN, 'measureAttribute')))}")
    print(f"  bldg:address: {len(written_root.findall('.//' + q(BLDG, 'address')))}")


def main() -> None:
    here = Path(__file__).resolve().parent
    source = here / "energy-center_v1.gml"
    target = here / "energy-center_senza-uro.gml"
    if len(sys.argv) == 3:
        source = Path(sys.argv[1])
        target = Path(sys.argv[2])
    convert(source, target)


if __name__ == "__main__":
    main()
