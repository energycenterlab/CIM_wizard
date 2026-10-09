# What to write in the CityGML for EuReCa

The schema allows hundreds of elements. Our pipeline reads only the ones on this page. Write these, and leave out everything else.

Your file is checked twice. First against the schema: one mistake there and the whole file is not read. Then by our reader: a building it cannot read is left out and listed in `_refused.json`.

**The column "Needed?"**

| It says | It means |
| --- | --- |
| **yes** | Without it the file, or the building, is not read. |
| **schema only** | We do not read it. But the schema demands it, so without it the whole file is not read. |
| **no:** and a value | You may leave it out. We then use the value shown. |

Write the elements of each table in the order of the table: the schema checks the order.

## The three levels of detail

We read a building at LoD1, LoD2 or LoD3. One file may hold buildings of different levels. This table says what changes from one level to the next; the sections below give the elements.

| | LoD1 | LoD2 | LoD3 |
| --- | --- | --- | --- |
| The building is | a plain box | walls, roofs and floors | the same, with real windows |
| Its shape is written in | `nrg3:lod1Solid`, in the thermal zone (section 4) | `bldg:lod2MultiSurface`, in each wall, roof and floor (section 3) | `bldg:lod3MultiSurface`, in each wall, roof and floor (section 3) |
| The thermal zone gets its walls from | its `nrg3:lod1Solid` | `nrg3:coincidesWithLod2Hull` = `true`, or a list of `nrg3:thermalBoundary` | `nrg3:coincidesWithLod3Hull` = `true`, or a list of `nrg3:thermalBoundary` |
| The glass | none | on each wall, one of two ways: `nrg3:bdgBdrySurfOpeningToSurfaceRatio`; or the pair `nrg3:bdgBdrySurfOpaqueSurfaceArea` and `nrg3:bdgBdrySurfTotalSurfaceArea` (section 3 explains both) | a hole (`gml:interior`) in the wall's `gml:Polygon`, and a `bldg:opening` with a `bldg:Window` (section 3) |
| What the glass is like | no glass | always U 2.8 and g 0.7 | `nrg3:uValue` and `nrg3:gValue` on the window's `nrg3:layeredConstruction` |
| What it is made of | one `nrg3:layeredConstruction`, on the thermal zone | one on each wall, roof and floor | one on each wall, roof and floor, and one on each window |
| Inner walls and floors | none | the ones you write | the ones you write |
| Our run can use | the 1C model | 1C; and 2C when every zone has an inner wall or floor | the same as LoD2 |

## 1. The file

| Write | What to put in it | Needed? |
| --- | --- | --- |
| the attribute `srsName`, on the `gml:Envelope` at the top or on the geometries | The coordinate system, the same in the whole file. Coordinates in metres, east first. Example: `srsName="EPSG:32633"`. | **yes** |

The frame of the file:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<core:CityModel xmlns:core="http://www.opengis.net/citygml/2.0"
    xmlns:bldg="http://www.opengis.net/citygml/building/2.0"
    xmlns:gen="http://www.opengis.net/citygml/generics/2.0"
    xmlns:gml="http://www.opengis.net/gml"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:nrg3="http://www.citygml.org/ade/energy/3.0">
  <core:cityObjectMember>
    <bldg:Building gml:id="my_building">
      ...the elements of section 2...
    </bldg:Building>
  </core:cityObjectMember>
</core:CityModel>
```

## 2. The building: `bldg:Building`

One `bldg:Building` in a `core:cityObjectMember`. Do not split it into `bldg:BuildingPart`.

| Write | What to put in it | Needed? |
| --- | --- | --- |
| the attribute `gml:id` | A name with no spaces. Our output file gets this name. | **yes** |
| `nrg3:device` | The heating or cooling plant: section 7. | no: the plant of our run settings |
| `bldg:storeysAboveGround` | A whole number. Used only when the floor area is given as `footprintArea`. | no |
| `bldg:boundedBy` | One for each wall, roof and ground floor: section 3. | **yes**, for LoD2 and LoD3 |
| `nrg3:bdgConstructionWeight` | `veryLight`, `light`, `medium` or `heavy`. | no: medium |
| `nrg3:thermalZone` | The thermal zone, written inside it: section 4. | **yes** |
| `nrg3:usageZone` | The usage zone, written inside it: section 6. | no: 1 dwelling |

## 3. A wall, a roof, a floor

Each one is written as one of these elements, inside a `bldg:boundedBy`:

| Element | It is |
| --- | --- |
| `bldg:WallSurface` | an outer wall |
| `bldg:RoofSurface` | a roof |
| `bldg:GroundSurface` | a floor on the ground |
| `bldg:OuterFloorSurface` | a flat part of the outer shell with the outdoors above it, for example the floor of a loggia. We treat it as a roof. |
| `bldg:OuterCeilingSurface` | a flat part of the outer shell with the outdoors below it, for example the ceiling of a passage. We treat it like a floor on the ground. |
| `nrg3:PartyWallSurface` | a wall shared with the next building |
| `nrg3:IntermediateFloorSurface` | a floor between two storeys |
| `nrg3:AtticFloorSurface` | the floor under an unheated attic |
| `nrg3:BasementCeilingSurface` | the ceiling over an unheated basement |

These four kinds we do not read, and a building that uses one is left out:

| Element | Why not |
| --- | --- |
| `bldg:ClosureSurface` | It is a virtual surface that closes an opening, not a real wall. It has no material. |
| `bldg:InteriorWallSurface`, `bldg:CeilingSurface`, `bldg:FloorSurface` | They are the inside of a room, used at LoD4 only. For an inner wall or floor, use the four `nrg3:` kinds above. |

Inside each of them:

| Write | What to put in it | Needed? |
| --- | --- | --- |
| the attribute `gml:id` | A name. Needed when something points at this element with `xlink:href`. | no: we make a name |
| `nrg3:layeredConstruction` | What it is made of: section 5. | no: a U-value of 1.0 |
| `bldg:lod2MultiSurface` (LoD2) or `bldg:lod3MultiSurface` (LoD3) | Its shape: `gml:MultiSurface` > `gml:surfaceMember` > `gml:Polygon` > `gml:exterior` > `gml:LinearRing` > `gml:posList`. | **yes** |
| `gml:posList` | The corner points of the polygon: three numbers for each point (east, north, height), in metres. The last point repeats the first. Instead of one `gml:posList` you may write one `gml:pos` for each point. | **yes** |
| `gml:interior`, in the same `gml:Polygon` (LoD3) | One hole for each window. | only for a wall with windows, at LoD3 |
| `bldg:opening` > `bldg:Window` (LoD3) | The window. Its size: its own `bldg:lod3MultiSurface` with a polygon, or `nrg3:bdgOpnArea uom="m^2"`. Its glass: a `nrg3:layeredConstruction` (section 5). A `bldg:Door` may be written the same way; it is not counted as glass. | only at LoD3 |
| `nrg3:bdgBdrySurfOpeningToSurfaceRatio` (LoD2, way 1) | How much of the wall is glass. Either from 0 to 1 with `uom="unit interval"` (0.25 for a quarter), or from 0 to 100 with `uom="percent"` (25 for a quarter). Do not write the sign `%` as the unit: the schema refuses it. | no: no glass |
| `nrg3:bdgBdrySurfOpaqueSurfaceArea` (LoD2, way 2) | The area of the wall **without** its glass, with `uom="m^2"`. Write it together with the next element. | way 2 needs both |
| `nrg3:bdgBdrySurfTotalSurfaceArea` (LoD2, way 2) | The area of the **whole** wall, glass included, with `uom="m^2"`. We work out the glass as 1 − opaque ÷ total. A wall of 30 m² with 7.5 m² of glass: opaque 22.5, total 30. | way 2 needs both |

Write way 1 or way 2, not both. With neither, the wall has no glass.

A wall at LoD2, with a quarter of it glass (way 1):

```xml
<bldg:boundedBy>
  <bldg:WallSurface gml:id="wall_south">
    <nrg3:layeredConstruction xlink:href="#wall_construction"/>
    <bldg:lod2MultiSurface>
      <gml:MultiSurface srsName="EPSG:32633" srsDimension="3">
        <gml:surfaceMember>
          <gml:Polygon gml:id="wall_south_polygon">
            <gml:exterior>
              <gml:LinearRing>
                <gml:posList>291340 5041900 0  291350 5041900 0  291350 5041900 3  291340 5041900 3  291340 5041900 0</gml:posList>
              </gml:LinearRing>
            </gml:exterior>
          </gml:Polygon>
        </gml:surfaceMember>
      </gml:MultiSurface>
    </bldg:lod2MultiSurface>
    <nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.25</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
  </bldg:WallSurface>
</bldg:boundedBy>
```

The same glass in way 2: in place of the `nrg3:bdgBdrySurfOpeningToSurfaceRatio` line, write these two lines.

```xml
    <nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">22.5</nrg3:bdgBdrySurfOpaqueSurfaceArea>
    <nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">30</nrg3:bdgBdrySurfTotalSurfaceArea>
```

A wall at LoD3, with one window: the wall's polygon gets a hole, and the window is written after the wall's shape.

```xml
<bldg:boundedBy>
  <bldg:WallSurface gml:id="wall_south">
    <nrg3:layeredConstruction xlink:href="#wall_construction"/>
    <bldg:lod3MultiSurface>
      <gml:MultiSurface srsName="EPSG:32633" srsDimension="3">
        <gml:surfaceMember>
          <gml:Polygon gml:id="wall_south_polygon">
            <gml:exterior>
              <gml:LinearRing>
                <gml:posList>291340 5041900 0  291350 5041900 0  291350 5041900 3  291340 5041900 3  291340 5041900 0</gml:posList>
              </gml:LinearRing>
            </gml:exterior>
            <gml:interior>
              <gml:LinearRing>
                <gml:posList>291344 5041900 1  291344 5041900 2  291346 5041900 2  291346 5041900 1  291344 5041900 1</gml:posList>
              </gml:LinearRing>
            </gml:interior>
          </gml:Polygon>
        </gml:surfaceMember>
      </gml:MultiSurface>
    </bldg:lod3MultiSurface>
    <bldg:opening>
      <bldg:Window gml:id="window_south">
        <nrg3:layeredConstruction xlink:href="#glass_construction"/>
        <bldg:lod3MultiSurface>
          <gml:MultiSurface srsName="EPSG:32633" srsDimension="3">
            <gml:surfaceMember>
              <gml:Polygon gml:id="window_south_polygon">
                <gml:exterior>
                  <gml:LinearRing>
                    <gml:posList>291344 5041900 1  291346 5041900 1  291346 5041900 2  291344 5041900 2  291344 5041900 1</gml:posList>
                  </gml:LinearRing>
                </gml:exterior>
              </gml:Polygon>
            </gml:surfaceMember>
          </gml:MultiSurface>
        </bldg:lod3MultiSurface>
      </bldg:Window>
    </bldg:opening>
  </bldg:WallSurface>
</bldg:boundedBy>
```

We also read these, if your data comes that way:

- a `gml:Polygon` written once and pointed at from another place with `xlink:href="#its id"`;
- several polygons in one `gml:surfaceMembers`, or in a `gml:CompositeSurface`;
- `bldg:lod4MultiSurface`: when a wall has its shape at several levels, we take the most detailed one;
- the attribute `srsDimension="3"` on a geometry, or no `srsDimension` at all.

## 4. The thermal zone: `nrg3:ThermalZone`

Written inside the building's `nrg3:thermalZone`.

| Write | What to put in it | Needed? |
| --- | --- | --- |
| the attribute `gml:id` | A name. | no |
| `nrg3:layeredConstruction` | LoD1 only: one construction for all the walls of the zone (section 5). | no: a U-value of 1.0 |
| `nrg3:area` > `nrg3:QualifiedArea` > `nrg3:value uom="m^2"`, then `nrg3:type` | The floor area of every floor. The type is one of `energyReferenceArea`, `netFloorArea`, `heatedArea`, `grossFloorArea`, `footprintArea`. | no: only the ground floor is counted. **Please write it.** |
| `nrg3:volume` > `nrg3:QualifiedVolume` > `nrg3:value uom="m^3"`, then `nrg3:type` | The air volume. The type is `netVolume` or `energyReferenceVolume`. | **yes** |
| `nrg3:lod1Solid` | LoD1 only: the box of the zone: `gml:Solid` > `gml:exterior` > `gml:CompositeSurface` > one `gml:surfaceMember` for each of its six `gml:Polygon`. | **yes**, for LoD1 |
| `nrg3:usageZone xlink:href="#..."` | Points at the usage zone of section 6. | no: 1 dwelling |
| `nrg3:isCooled` | `true` or `false`. | **schema only** |
| `nrg3:isHeated` | `true` or `false`. | **schema only** |
| `nrg3:coincidesWithLod2Hull` | `true` when the zone is the whole building at LoD2. We then take every `bldg:boundedBy` of the building as the zone's walls, roofs and floors. Otherwise `false`. | **yes** |
| `nrg3:coincidesWithLod3Hull` | The same at LoD3. | **yes** |
| `nrg3:thermalBoundary` | One for each wall, roof and floor of the zone: the element of section 3 written inside it, or `xlink:href="#its id"`. Leave it out when a hull value above is `true`, and at LoD1. | **yes**, when both hull values are `false` at LoD2 or LoD3 |

The simplest building with one zone at LoD2: write the walls, roofs and floors in the building (section 3), set `nrg3:coincidesWithLod2Hull` to `true`, and write no `nrg3:thermalBoundary`:

```xml
<nrg3:thermalZone>
  <nrg3:ThermalZone gml:id="zone_1">
    <nrg3:area>
      <nrg3:QualifiedArea>
        <nrg3:value uom="m^2">80</nrg3:value>
        <nrg3:type>netFloorArea</nrg3:type>
      </nrg3:QualifiedArea>
    </nrg3:area>
    <nrg3:volume>
      <nrg3:QualifiedVolume>
        <nrg3:value uom="m^3">240</nrg3:value>
        <nrg3:type>netVolume</nrg3:type>
      </nrg3:QualifiedVolume>
    </nrg3:volume>
    <nrg3:usageZone xlink:href="#usage_1"/>
    <nrg3:isCooled>false</nrg3:isCooled>
    <nrg3:isHeated>true</nrg3:isHeated>
    <nrg3:coincidesWithLod2Hull>true</nrg3:coincidesWithLod2Hull>
    <nrg3:coincidesWithLod3Hull>false</nrg3:coincidesWithLod3Hull>
  </nrg3:ThermalZone>
</nrg3:thermalZone>
```

The other way, for a building with several zones: both hull values `false`, and after them one line for each wall, roof and floor of this zone, pointing at its `gml:id`:

```xml
    <nrg3:coincidesWithLod2Hull>false</nrg3:coincidesWithLod2Hull>
    <nrg3:coincidesWithLod3Hull>false</nrg3:coincidesWithLod3Hull>
    <nrg3:thermalBoundary xlink:href="#wall_south"/>
    <nrg3:thermalBoundary xlink:href="#wall_east"/>
```

At LoD1 the zone holds its box, written between the volume and `nrg3:isCooled`:

```xml
    <nrg3:lod1Solid>
      <gml:Solid srsName="EPSG:32633" srsDimension="3">
        <gml:exterior>
          <gml:CompositeSurface>
            <gml:surfaceMember>
              <gml:Polygon gml:id="box_ground">
                <gml:exterior>
                  <gml:LinearRing>
                    <gml:posList>291340 5041900 0  291340 5041908 0  291350 5041908 0  291350 5041900 0  291340 5041900 0</gml:posList>
                  </gml:LinearRing>
                </gml:exterior>
              </gml:Polygon>
            </gml:surfaceMember>
            ...five more gml:surfaceMember: the roof and the four walls...
          </gml:CompositeSurface>
        </gml:exterior>
      </gml:Solid>
    </nrg3:lod1Solid>
```

## 5. A construction: `nrg3:LayeredConstruction`

Write it with layers, or with only a U-value. One of the two is needed.

| Write | What to put in it | Needed? |
| --- | --- | --- |
| the attribute `gml:id` | A name. Needed when a `nrg3:layeredConstruction` points at it. | |
| `nrg3:uValue` | The U-value, with `uom="W/(m^2*K)"`. | **yes**, when there are no layers. For a window: no: 2.8 |
| `nrg3:gValue` | For a window only: how much of the sun's heat comes through, from 0 to 1, with `uom="unit interval"`. | no: 0.7 |
| `nrg3:transmittance` > `nrg3:Transmittance` > `nrg3:fraction`, then `nrg3:wavelengthRange` = `visible` | For a window only: how much light comes through. | no: 0.9 |
| `nrg3:layer` > `nrg3:Layer`, one for each layer, from the inside of the room to the outside | Inside it: `nrg3:thickness` with `uom="m"`, `"cm"` or `"mm"`, then `nrg3:material` with the material inside or `xlink:href="#its id"`. | **yes**, when there is no U-value |

The material of a layer is one of these two:

| Element | Write | Unit to write | Needed? |
| --- | --- | --- | --- |
| `nrg3:SolidMaterial` | `nrg3:thermalConductivity` | `uom="W/(m*K)"` | no: 1.0 |
| | `nrg3:density` | `uom="kg/m^3"` | no: 1000 |
| | `nrg3:specificHeatCapacity` | `uom="J/(kg*K)"` (brick and concrete are about 800 to 1000) | no: 1000 |
| `nrg3:Gas` (an air layer) | `nrg3:rValue` | `uom="m^2*K/W"` | no: 1.0 |

Write the units exactly as shown. A material value in another unit is not read, and the default is used with no message.

**The same construction, seen from the other side: `nrg3:ReverseLayeredConstruction`.** A floor or a wall between two thermal zones belongs to both. Give it the construction in one zone, and its reverse in the other.

| Write | What to put in it | Needed? |
| --- | --- | --- |
| the attribute `gml:id` | A name, so that a `nrg3:layeredConstruction` can point at it. | **yes** |
| `nrg3:baseLayeredConstruction xlink:href="#..."` | Points at the `nrg3:LayeredConstruction` it turns round. | **yes** |

**Where to write constructions and materials.** Either inside the element that uses them, or once in a library and pointed at with `xlink:href="#its id"`. Our sample file uses two libraries, each in its own `core:cityObjectMember`:

| Library | Each `nrg3:libraryMember` holds |
| --- | --- |
| `nrg3:LayeredConstructionLibrary` | one `nrg3:LayeredConstruction` or `nrg3:ReverseLayeredConstruction`, with a `gml:id` |
| `nrg3:MaterialLibrary` | one `nrg3:SolidMaterial` or `nrg3:Gas`, with a `gml:id` |

A library with three constructions: a wall with layers, a roof with only a U-value, and the glass of a window. The walls and the window of section 3 point at them.

```xml
<core:cityObjectMember>
  <nrg3:LayeredConstructionLibrary gml:id="constructions">
    <nrg3:libraryMember>
      <nrg3:LayeredConstruction gml:id="wall_construction">
        <nrg3:layer>
          <nrg3:Layer>
            <nrg3:thickness uom="cm">2</nrg3:thickness>
            <nrg3:material>
              <nrg3:SolidMaterial>
                <nrg3:thermalConductivity uom="W/(m*K)">0.7</nrg3:thermalConductivity>
                <nrg3:density uom="kg/m^3">1400</nrg3:density>
                <nrg3:specificHeatCapacity uom="J/(kg*K)">1000</nrg3:specificHeatCapacity>
              </nrg3:SolidMaterial>
            </nrg3:material>
          </nrg3:Layer>
        </nrg3:layer>
        <nrg3:layer>
          <nrg3:Layer>
            <nrg3:thickness uom="m">0.05</nrg3:thickness>
            <nrg3:material>
              <nrg3:Gas>
                <nrg3:rValue uom="m^2*K/W">0.18</nrg3:rValue>
              </nrg3:Gas>
            </nrg3:material>
          </nrg3:Layer>
        </nrg3:layer>
        <nrg3:layer>
          <nrg3:Layer>
            <nrg3:thickness uom="mm">250</nrg3:thickness>
            <nrg3:material>
              <nrg3:SolidMaterial>
                <nrg3:thermalConductivity uom="W/(m*K)">0.6</nrg3:thermalConductivity>
                <nrg3:density uom="kg/m^3">1600</nrg3:density>
                <nrg3:specificHeatCapacity uom="J/(kg*K)">900</nrg3:specificHeatCapacity>
              </nrg3:SolidMaterial>
            </nrg3:material>
          </nrg3:Layer>
        </nrg3:layer>
      </nrg3:LayeredConstruction>
    </nrg3:libraryMember>
    <nrg3:libraryMember>
      <nrg3:LayeredConstruction gml:id="roof_construction">
        <nrg3:uValue uom="W/(m^2*K)">0.4</nrg3:uValue>
      </nrg3:LayeredConstruction>
    </nrg3:libraryMember>
    <nrg3:libraryMember>
      <nrg3:LayeredConstruction gml:id="glass_construction">
        <nrg3:uValue uom="W/(m^2*K)">1.4</nrg3:uValue>
        <nrg3:gValue uom="unit interval">0.6</nrg3:gValue>
        <nrg3:transmittance>
          <nrg3:Transmittance>
            <nrg3:fraction uom="unit interval">0.7</nrg3:fraction>
            <nrg3:wavelengthRange>visible</nrg3:wavelengthRange>
          </nrg3:Transmittance>
        </nrg3:transmittance>
      </nrg3:LayeredConstruction>
    </nrg3:libraryMember>
  </nrg3:LayeredConstructionLibrary>
</core:cityObjectMember>
```

## 6. The usage zone: `nrg3:UsageZone`

Only needed to say how many dwellings the building has.

| Write | What to put in it | Needed? |
| --- | --- | --- |
| the attribute `gml:id` | A name: the thermal zone points at it. | **yes** |
| `nrg3:type` | For example `residential`. | **schema only** |
| `nrg3:numberOfBuildingUnits` | The number of dwellings, a whole number. | no: 1 |

It is written in the building, after `nrg3:thermalZone`, and the thermal zone points at it with `nrg3:usageZone xlink:href="#usage_1"`:

```xml
<nrg3:usageZone>
  <nrg3:UsageZone gml:id="usage_1">
    <nrg3:type>residential</nrg3:type>
    <nrg3:numberOfBuildingUnits>2</nrg3:numberOfBuildingUnits>
  </nrg3:UsageZone>
</nrg3:usageZone>
```

## 7. The plant: a device

Only when you want to say which plant the building has. The full list of names and values is in `EuReCa plants in CityGML.md`.

| Write | What to put in it | Needed? |
| --- | --- | --- |
| `nrg3:Boiler`, `nrg3:HeatPump` or `nrg3:GenericDevice`, inside `nrg3:device` | We do not read which of the three it is. | **yes** |
| `gml:name codeSpace="urn:eureca:heating-system"` (or `urn:eureca:cooling-system`) | One of EuReCa's plant names, copied exactly. | **yes** |
| `nrg3:numberOfDevices` | A whole number. | no: 1 |
| `nrg3:installedPower` | The size, with `uom="W"` or `uom="kW"`. | no: the size of our run settings |
| `nrg3:deviceOperation` > `nrg3:DeviceOperation` > `nrg3:type` | `spaceHeating` or `spaceCooling`. | **yes** |
| `nrg3:hasCondensation` (in a `nrg3:Boiler`) or `nrg3:heatSource` (in a `nrg3:HeatPump`) | Any allowed value. | **schema only** |
| `gen:doubleAttribute` and `gen:stringAttribute`, each with the attribute `name` and a `gen:value` | Only for your own plant, named `From manual parameters`: one for each of its values. The names are listed in the plant page. | only for your own plant |

A gas boiler of 12 kW, written first in the building:

```xml
<nrg3:device>
  <nrg3:GenericDevice>
    <gml:name codeSpace="urn:eureca:heating-system">Condensing Gas Boiler, Centralized, Low Temp Radiator</gml:name>
    <nrg3:numberOfDevices>1</nrg3:numberOfDevices>
    <nrg3:installedPower uom="kW">12</nrg3:installedPower>
    <nrg3:deviceOperation>
      <nrg3:DeviceOperation>
        <nrg3:type>spaceHeating</nrg3:type>
      </nrg3:DeviceOperation>
    </nrg3:deviceOperation>
  </nrg3:GenericDevice>
</nrg3:device>
```

## 8. What you can leave out

We read none of these, so you do not need to fill them:

- names and descriptions: `gml:name`, `gml:description`;
- facts about the building: `bldg:function`, `bldg:class`, `bldg:yearOfConstruction`, `bldg:roofType`, `bldg:measuredHeight`, `bldg:address`;
- the building's own `bldg:lod1Solid` and `bldg:lod2Solid`;
- on a wall, roof or floor: `nrg3:bdgBdrySurfAzimuth`, `nrg3:bdgBdrySurfInclination`, `nrg3:bdgBdrySurfSkyViewFactor`, `nrg3:bdgBdrySurfGroundViewFactor`, `nrg3:bdgBdrySurfIsAdiabatic`, `nrg3:bdgBdrySurfThickness`, `nrg3:bdgBdrySurfHeatCapacity`;
- on a zone: `nrg3:heatCapacity`, `nrg3:infiltrationRate`, `nrg3:referencePoint`;
- people, schedules, setpoints, internal heat gains, weather, energy demand, colours and textures.

People, schedules, setpoints and the air leakage are given to our run, in an Excel file, not in the CityGML.

## 9. Check your file

```bash
python scripts/write_contracts.py your_file.gml
```

- If the schema check fails, it prints the mistakes with their line numbers, and reads nothing.
- If the schema is fine, it writes one JSON for each building it could read, and `_refused.json` with the reason for each building it could not.
