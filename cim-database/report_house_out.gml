<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!-- Written by 3D City Database Importer/Exporter, version "5.5.1" -->
<!-- Chair of Geoinformatics, Technical University of Munich -->
<CityModel xmlns:xAL="urn:oasis:names:tc:ciq:xsdschema:xAL:2.0" xmlns:gml="http://www.opengis.net/gml" xmlns:wtr="http://www.opengis.net/citygml/waterbody/2.0" xmlns:app="http://www.opengis.net/citygml/appearance/2.0" xmlns="http://www.opengis.net/citygml/2.0" xmlns:veg="http://www.opengis.net/citygml/vegetation/2.0" xmlns:dem="http://www.opengis.net/citygml/relief/2.0" xmlns:tran="http://www.opengis.net/citygml/transportation/2.0" xmlns:bldg="http://www.opengis.net/citygml/building/2.0" xmlns:grp="http://www.opengis.net/citygml/cityobjectgroup/2.0" xmlns:tun="http://www.opengis.net/citygml/tunnel/2.0" xmlns:frn="http://www.opengis.net/citygml/cityfurniture/2.0" xmlns:gen="http://www.opengis.net/citygml/generics/2.0" xmlns:brid="http://www.opengis.net/citygml/bridge/2.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:luse="http://www.opengis.net/citygml/landuse/2.0" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/citygml/waterbody/2.0 http://schemas.opengis.net/citygml/waterbody/2.0/waterBody.xsd http://www.opengis.net/citygml/appearance/2.0 http://schemas.opengis.net/citygml/appearance/2.0/appearance.xsd http://www.opengis.net/citygml/2.0 http://schemas.opengis.net/citygml/2.0/cityGMLBase.xsd http://www.opengis.net/citygml/vegetation/2.0 http://schemas.opengis.net/citygml/vegetation/2.0/vegetation.xsd http://www.opengis.net/citygml/transportation/2.0 http://schemas.opengis.net/citygml/transportation/2.0/transportation.xsd http://www.opengis.net/citygml/relief/2.0 http://schemas.opengis.net/citygml/relief/2.0/relief.xsd http://www.opengis.net/citygml/building/2.0 http://schemas.opengis.net/citygml/building/2.0/building.xsd http://www.opengis.net/citygml/cityobjectgroup/2.0 http://schemas.opengis.net/citygml/cityobjectgroup/2.0/cityObjectGroup.xsd http://www.opengis.net/citygml/tunnel/2.0 http://schemas.opengis.net/citygml/tunnel/2.0/tunnel.xsd http://www.opengis.net/citygml/cityfurniture/2.0 http://schemas.opengis.net/citygml/cityfurniture/2.0/cityFurniture.xsd http://www.opengis.net/citygml/generics/2.0 http://schemas.opengis.net/citygml/generics/2.0/generics.xsd http://www.opengis.net/citygml/bridge/2.0 http://schemas.opengis.net/citygml/bridge/2.0/bridge.xsd http://www.opengis.net/citygml/landuse/2.0 http://schemas.opengis.net/citygml/landuse/2.0/landUse.xsd">
  <cityObjectMember>
    <bldg:Building gml:id="house_lod1_4">
      <gml:description>The same house as a LoD1 box: no windows and no party wall, all LoD1 may say. Its thermal zone states one average U-value for the whole shell.</gml:description>
      <gml:name>Report house - LoD1</gml:name>
      <gml:boundedBy>
        <gml:Envelope srsName="urn:ogc:def:crs:EPSG::4326" srsDimension="3">
          <gml:lowerCorner>291360.0 5041900.0 0.0</gml:lowerCorner>
          <gml:upperCorner>291370.0 5041910.0 6.0</gml:upperCorner>
        </gml:Envelope>
      </gml:boundedBy>
      <creationDate>2024-09-25</creationDate>
      <bldg:lod0FootPrint>
        <gml:MultiSurface gml:id="fx1_id_lod0_MultiSurf_20">
          <gml:surfaceMember>
            <gml:Polygon gml:id="fx1_id_lod0_Polygon_20">
              <gml:exterior>
                <gml:LinearRing gml:id="fx1_id_lod0_Polygon_20_0_">
                  <gml:posList srsDimension="3">291360.0 5041900.0 0.0 291370.0 5041900.0 0.0 291370.0 5041910.0 0.0 291360.0 5041910.0 0.0 291360.0 5041900.0 0.0</gml:posList>
                </gml:LinearRing>
              </gml:exterior>
            </gml:Polygon>
          </gml:surfaceMember>
        </gml:MultiSurface>
      </bldg:lod0FootPrint>
      <bldg:lod1Solid>
        <gml:Solid gml:id="fx1_id_lod1_Solid_20">
          <gml:exterior>
            <gml:CompositeSurface gml:id="fx1_id_lod1_CompSurf_20">
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx1_id_lod1_Polygon_1">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx1_id_lod1_Polygon_1_0_">
                      <gml:posList srsDimension="3">291360.0 5041900.0 0.0 291360.0 5041910.0 0.0 291370.0 5041910.0 0.0 291370.0 5041900.0 0.0 291360.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx1_id_lod1_Polygon_2">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx1_id_lod1_Polygon_2_0_">
                      <gml:posList srsDimension="3">291360.0 5041900.0 0.0 291370.0 5041900.0 0.0 291370.0 5041900.0 6.0 291360.0 5041900.0 6.0 291360.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx1_id_lod1_Polygon_3">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx1_id_lod1_Polygon_3_0_">
                      <gml:posList srsDimension="3">291370.0 5041900.0 0.0 291370.0 5041910.0 0.0 291370.0 5041910.0 6.0 291370.0 5041900.0 6.0 291370.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx1_id_lod1_Polygon_4">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx1_id_lod1_Polygon_4_0_">
                      <gml:posList srsDimension="3">291370.0 5041910.0 0.0 291360.0 5041910.0 0.0 291360.0 5041910.0 6.0 291370.0 5041910.0 6.0 291370.0 5041910.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx1_id_lod1_Polygon_5">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx1_id_lod1_Polygon_5_0_">
                      <gml:posList srsDimension="3">291360.0 5041910.0 0.0 291360.0 5041900.0 0.0 291360.0 5041900.0 6.0 291360.0 5041910.0 6.0 291360.0 5041910.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx1_id_lod1_Polygon_6">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx1_id_lod1_Polygon_6_0_">
                      <gml:posList srsDimension="3">291360.0 5041900.0 6.0 291370.0 5041900.0 6.0 291370.0 5041910.0 6.0 291360.0 5041910.0 6.0 291360.0 5041900.0 6.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:CompositeSurface>
          </gml:exterior>
        </gml:Solid>
      </bldg:lod1Solid>
    </bldg:Building>
  </cityObjectMember>
  <cityObjectMember>
    <bldg:Building gml:id="house_lod2_2">
      <gml:description>The same house at LoD2: no window geometry; the glass is a declared ratio on each wall.</gml:description>
      <gml:name>Report house - LoD2</gml:name>
      <gml:boundedBy>
        <gml:Envelope srsName="urn:ogc:def:crs:EPSG::4326" srsDimension="3">
          <gml:lowerCorner>291320.0 5041900.0 0.0</gml:lowerCorner>
          <gml:upperCorner>291330.0 5041910.0 9.0</gml:upperCorner>
        </gml:Envelope>
      </gml:boundedBy>
      <creationDate>2024-09-25</creationDate>
      <bldg:class codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_class.xml">habitation</bldg:class>
      <bldg:function codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_function.xml">residential building</bldg:function>
      <bldg:yearOfConstruction>1955</bldg:yearOfConstruction>
      <bldg:roofType codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_roofType.xml">gabled roof</bldg:roofType>
      <bldg:measuredHeight uom="m">9.0</bldg:measuredHeight>
      <bldg:storeysAboveGround>2</bldg:storeysAboveGround>
      <bldg:storeysBelowGround>0</bldg:storeysBelowGround>
      <bldg:storeyHeightsAboveGround uom="m">3.0</bldg:storeyHeightsAboveGround>
      <bldg:lod0FootPrint>
        <gml:MultiSurface gml:id="fx2_id_building_1_footprint_MultiSurf">
          <gml:surfaceMember>
            <gml:OrientableSurface orientation="-">
              <gml:baseSurface>
                <gml:Polygon gml:id="fx2_id_building_1_polygon_3">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx2_id_building_1_polygon_3_0_">
                      <gml:posList srsDimension="3">291320.0 5041900.0 0.0 291320.0 5041910.0 0.0 291330.0 5041910.0 0.0 291330.0 5041900.0 0.0 291320.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:baseSurface>
            </gml:OrientableSurface>
          </gml:surfaceMember>
        </gml:MultiSurface>
      </bldg:lod0FootPrint>
      <bldg:lod1Solid>
        <gml:Solid gml:id="fx2_id_building_1_lod1_Solid">
          <gml:exterior>
            <gml:CompositeSurface gml:id="fx2_id_building_1_lod1_CompSurf">
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx2_id_building_1_lod1_Polygon_1">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx2_id_building_1_lod1_Polygon_1_0_">
                      <gml:posList srsDimension="3">291320.0 5041900.0 0.0 291320.0 5041910.0 0.0 291330.0 5041910.0 0.0 291330.0 5041900.0 0.0 291320.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx2_id_building_1_lod1_Polygon_2">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx2_id_building_1_lod1_Polygon_2_0_">
                      <gml:posList srsDimension="3">291320.0 5041900.0 0.0 291330.0 5041900.0 0.0 291330.0 5041900.0 7.5 291320.0 5041900.0 7.5 291320.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx2_id_building_1_lod1_Polygon_3">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx2_id_building_1_lod1_Polygon_3_0_">
                      <gml:posList srsDimension="3">291330.0 5041900.0 0.0 291330.0 5041910.0 0.0 291330.0 5041910.0 7.5 291330.0 5041900.0 7.5 291330.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx2_id_building_1_lod1_Polygon_4">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx2_id_building_1_lod1_Polygon_4_0_">
                      <gml:posList srsDimension="3">291330.0 5041910.0 0.0 291320.0 5041910.0 0.0 291320.0 5041910.0 7.5 291330.0 5041910.0 7.5 291330.0 5041910.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx2_id_building_1_lod1_Polygon_5">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx2_id_building_1_lod1_Polygon_5_0_">
                      <gml:posList srsDimension="3">291320.0 5041910.0 0.0 291320.0 5041900.0 0.0 291320.0 5041900.0 7.5 291320.0 5041910.0 7.5 291320.0 5041910.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx2_id_building_1_lod1_Polygon_6">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx2_id_building_1_lod1_Polygon_6_0_">
                      <gml:posList srsDimension="3">291320.0 5041900.0 7.5 291330.0 5041900.0 7.5 291330.0 5041910.0 7.5 291320.0 5041910.0 7.5 291320.0 5041900.0 7.5</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:CompositeSurface>
          </gml:exterior>
        </gml:Solid>
      </bldg:lod1Solid>
      <bldg:lod2Solid>
        <gml:Solid gml:id="fx2_id_building_1_lod2_Solid">
          <gml:exterior>
            <gml:CompositeSurface gml:id="fx2_id_building_1_lod2_CompSurf">
              <gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_4"/>
              <gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_5"/>
              <gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_7"/>
              <gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_1"/>
              <gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_2"/>
              <gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_3"/>
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx2_Polygon_UUID_741a8f18-1100-467f-9c40-a919c34d2065">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx2_Polygon_UUID_741a8f18-1100-467f-9c40-a919c34d2065_0_">
                      <gml:posList srsDimension="3">291330.0 5041910.0 6.0 291330.0 5041900.0 6.0 291330.0 5041900.0 0.0 291330.0 5041910.0 0.0 291330.0 5041910.0 6.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:CompositeSurface>
          </gml:exterior>
        </gml:Solid>
      </bldg:lod2Solid>
      <bldg:boundedBy>
        <bldg:GroundSurface gml:id="fx2_id_building_1_groundsurface_1">
          <gml:description>This is GroundSurface 1 (Building 1)</gml:description>
          <gml:name>GroundSurface 1 (Building 1)</gml:name>
          <creationDate>2026-10-06</creationDate>
          <bldg:lod2MultiSurface>
            <gml:MultiSurface gml:id="fx2_id_building_1_groundsurface_1_lod2_geom">
              <gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_3"/>
            </gml:MultiSurface>
          </bldg:lod2MultiSurface>
        </bldg:GroundSurface>
      </bldg:boundedBy>
      <bldg:boundedBy>
        <bldg:RoofSurface gml:id="fx2_id_building_1_roofsurface_1">
          <gml:description>This is RoofSurface 1 (Building 1)</gml:description>
          <gml:name>RoofSurface 1 (Building 1)</gml:name>
          <creationDate>2026-10-06</creationDate>
          <bldg:lod2MultiSurface>
            <gml:MultiSurface gml:id="fx2_id_building_1_roofsurface_1_lod2_geom">
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx2_id_building_1_polygon_1">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx2_id_building_1_polygon_1_0_">
                      <gml:posList srsDimension="3">291320.0 5041900.0 6.0 291325.0 5041900.0 9.0 291325.0 5041910.0 9.0 291320.0 5041910.0 6.0 291320.0 5041900.0 6.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:MultiSurface>
          </bldg:lod2MultiSurface>
        </bldg:RoofSurface>
      </bldg:boundedBy>
      <bldg:boundedBy>
        <bldg:RoofSurface gml:id="fx2_id_building_1_roofsurface_2">
          <gml:description>This is RoofSurface 2 (Building 1)</gml:description>
          <gml:name>RoofSurface 2 (Building 1)</gml:name>
          <creationDate>2026-10-06</creationDate>
          <bldg:lod2MultiSurface>
            <gml:MultiSurface gml:id="fx2_id_building_1_roofsurface_2_lod2_geom">
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx2_id_building_1_polygon_2">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx2_id_building_1_polygon_2_0_">
                      <gml:posList srsDimension="3">291325.0 5041900.0 9.0 291330.0 5041900.0 6.0 291330.0 5041910.0 6.0 291325.0 5041910.0 9.0 291325.0 5041900.0 9.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:MultiSurface>
          </bldg:lod2MultiSurface>
        </bldg:RoofSurface>
      </bldg:boundedBy>
      <bldg:boundedBy>
        <bldg:WallSurface gml:id="fx2_id_building_1_wallsurface_1">
          <gml:description>This is WallSurface 1 (Building 1)</gml:description>
          <gml:name>WallSurface 1 (Building 1)</gml:name>
          <creationDate>2026-10-06</creationDate>
          <bldg:lod2MultiSurface>
            <gml:MultiSurface gml:id="fx2_id_building_1_wallsurface_1_lod2_geom">
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx2_id_building_1_polygon_5">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx2_id_building_1_polygon_5_0_">
                      <gml:posList srsDimension="3">291320.0 5041900.0 0.0 291330.0 5041900.0 0.0 291330.0 5041900.0 6.0 291325.0 5041900.0 9.0 291320.0 5041900.0 6.0 291320.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:MultiSurface>
          </bldg:lod2MultiSurface>
        </bldg:WallSurface>
      </bldg:boundedBy>
      <bldg:boundedBy>
        <bldg:WallSurface gml:id="fx2_id_building_1_wallsurface_2">
          <gml:description>This is WallSurface 2 (Building 1)</gml:description>
          <gml:name>WallSurface 2 (Building 1)</gml:name>
          <creationDate>2026-10-06</creationDate>
          <bldg:lod2MultiSurface>
            <gml:MultiSurface gml:id="fx2_id_building_1_wallsurface_2_lod2_geom">
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx2_id_building_1_polygon_4">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx2_id_building_1_polygon_4_0_">
                      <gml:posList srsDimension="3">291320.0 5041910.0 0.0 291320.0 5041910.0 6.0 291325.0 5041910.0 9.0 291330.0 5041910.0 6.0 291330.0 5041910.0 0.0 291320.0 5041910.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:MultiSurface>
          </bldg:lod2MultiSurface>
        </bldg:WallSurface>
      </bldg:boundedBy>
      <bldg:boundedBy>
        <bldg:WallSurface gml:id="fx2_id_building_1_wallsurface_3">
          <gml:description>This is WallSurface 3 (Building 1)</gml:description>
          <gml:name>WallSurface 3 (Building 1)</gml:name>
          <creationDate>2026-10-06</creationDate>
          <bldg:lod2MultiSurface>
            <gml:MultiSurface gml:id="fx2_id_building_1_wallsurface_3_lod2_geom">
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx2_id_building_1_polygon_7">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx2_id_building_1_polygon_7_0_">
                      <gml:posList srsDimension="3">291320.0 5041900.0 0.0 291320.0 5041900.0 6.0 291320.0 5041910.0 6.0 291320.0 5041910.0 0.0 291320.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:MultiSurface>
          </bldg:lod2MultiSurface>
        </bldg:WallSurface>
      </bldg:boundedBy>
      <bldg:address>
        <Address>
          <xalAddress>
            <xAL:AddressDetails>
              <xAL:Country>
                <xAL:CountryName>Bespin Territories</xAL:CountryName>
                <xAL:Locality Type="City">
                  <xAL:LocalityName>Alderaan</xAL:LocalityName>
                  <xAL:Thoroughfare Type="Street">
                    <xAL:ThoroughfareNumber>1</xAL:ThoroughfareNumber>
                    <xAL:ThoroughfareName>Bespin Square</xAL:ThoroughfareName>
                  </xAL:Thoroughfare>
                  <xAL:PostalCode>
                    <xAL:PostalCodeNumber>1977SW</xAL:PostalCodeNumber>
                  </xAL:PostalCode>
                </xAL:Locality>
              </xAL:Country>
            </xAL:AddressDetails>
          </xalAddress>
          <multiPoint>
            <gml:MultiPoint>
              <gml:pointMember>
                <gml:Point>
                  <gml:pos srsDimension="3">291325.0 5041905.0 0.0</gml:pos>
                </gml:Point>
              </gml:pointMember>
            </gml:MultiPoint>
          </multiPoint>
        </Address>
      </bldg:address>
    </bldg:Building>
  </cityObjectMember>
  <cityObjectMember>
    <bldg:Building gml:id="house_lod3_1">
      <gml:description>The report house at LoD3: walls, roof and floor, with three real windows.</gml:description>
      <gml:name>Report house - LoD3</gml:name>
      <gml:boundedBy>
        <gml:Envelope srsName="urn:ogc:def:crs:EPSG::4326" srsDimension="3">
          <gml:lowerCorner>291300.0 5041900.0 0.0</gml:lowerCorner>
          <gml:upperCorner>291310.0 5041910.0 9.0</gml:upperCorner>
        </gml:Envelope>
      </gml:boundedBy>
      <creationDate>2024-09-25</creationDate>
      <bldg:class codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_class.xml">habitation</bldg:class>
      <bldg:function codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_function.xml">residential building</bldg:function>
      <bldg:yearOfConstruction>1955</bldg:yearOfConstruction>
      <bldg:roofType codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_roofType.xml">gabled roof</bldg:roofType>
      <bldg:measuredHeight uom="m">9.0</bldg:measuredHeight>
      <bldg:storeysAboveGround>2</bldg:storeysAboveGround>
      <bldg:storeysBelowGround>0</bldg:storeysBelowGround>
      <bldg:storeyHeightsAboveGround uom="m">3.0</bldg:storeyHeightsAboveGround>
      <bldg:lod0FootPrint>
        <gml:MultiSurface gml:id="id_building_1_footprint_MultiSurf">
          <gml:surfaceMember>
            <gml:OrientableSurface orientation="-">
              <gml:baseSurface>
                <gml:Polygon gml:id="id_building_1_polygon_3">
                  <gml:exterior>
                    <gml:LinearRing gml:id="id_building_1_polygon_3_0_">
                      <gml:posList srsDimension="3">291300.0 5041900.0 0.0 291300.0 5041910.0 0.0 291310.0 5041910.0 0.0 291310.0 5041900.0 0.0 291300.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:baseSurface>
            </gml:OrientableSurface>
          </gml:surfaceMember>
        </gml:MultiSurface>
      </bldg:lod0FootPrint>
      <bldg:lod1Solid>
        <gml:Solid gml:id="id_building_1_lod1_Solid">
          <gml:exterior>
            <gml:CompositeSurface gml:id="id_building_1_lod1_CompSurf">
              <gml:surfaceMember>
                <gml:Polygon gml:id="id_building_1_lod1_Polygon_1">
                  <gml:exterior>
                    <gml:LinearRing gml:id="id_building_1_lod1_Polygon_1_0_">
                      <gml:posList srsDimension="3">291300.0 5041900.0 0.0 291300.0 5041910.0 0.0 291310.0 5041910.0 0.0 291310.0 5041900.0 0.0 291300.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="id_building_1_lod1_Polygon_2">
                  <gml:exterior>
                    <gml:LinearRing gml:id="id_building_1_lod1_Polygon_2_0_">
                      <gml:posList srsDimension="3">291300.0 5041900.0 0.0 291310.0 5041900.0 0.0 291310.0 5041900.0 7.5 291300.0 5041900.0 7.5 291300.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="id_building_1_lod1_Polygon_3">
                  <gml:exterior>
                    <gml:LinearRing gml:id="id_building_1_lod1_Polygon_3_0_">
                      <gml:posList srsDimension="3">291310.0 5041900.0 0.0 291310.0 5041910.0 0.0 291310.0 5041910.0 7.5 291310.0 5041900.0 7.5 291310.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="id_building_1_lod1_Polygon_4">
                  <gml:exterior>
                    <gml:LinearRing gml:id="id_building_1_lod1_Polygon_4_0_">
                      <gml:posList srsDimension="3">291310.0 5041910.0 0.0 291300.0 5041910.0 0.0 291300.0 5041910.0 7.5 291310.0 5041910.0 7.5 291310.0 5041910.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="id_building_1_lod1_Polygon_5">
                  <gml:exterior>
                    <gml:LinearRing gml:id="id_building_1_lod1_Polygon_5_0_">
                      <gml:posList srsDimension="3">291300.0 5041910.0 0.0 291300.0 5041900.0 0.0 291300.0 5041900.0 7.5 291300.0 5041910.0 7.5 291300.0 5041910.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="id_building_1_lod1_Polygon_6">
                  <gml:exterior>
                    <gml:LinearRing gml:id="id_building_1_lod1_Polygon_6_0_">
                      <gml:posList srsDimension="3">291300.0 5041900.0 7.5 291310.0 5041900.0 7.5 291310.0 5041910.0 7.5 291300.0 5041910.0 7.5 291300.0 5041900.0 7.5</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:CompositeSurface>
          </gml:exterior>
        </gml:Solid>
      </bldg:lod1Solid>
      <bldg:lod2Solid>
        <gml:Solid gml:id="id_building_1_lod2_Solid">
          <gml:exterior>
            <gml:CompositeSurface gml:id="id_building_1_lod2_CompSurf">
              <gml:surfaceMember xlink:href="#id_building_1_polygon_4"/>
              <gml:surfaceMember xlink:href="#id_building_1_polygon_5"/>
              <gml:surfaceMember xlink:href="#id_building_1_polygon_7"/>
              <gml:surfaceMember xlink:href="#id_building_1_polygon_1"/>
              <gml:surfaceMember xlink:href="#id_building_1_polygon_2"/>
              <gml:surfaceMember xlink:href="#id_building_1_polygon_3"/>
              <gml:surfaceMember>
                <gml:Polygon gml:id="Polygon_UUID_741a8f18-1100-467f-9c40-a919c34d2065">
                  <gml:exterior>
                    <gml:LinearRing gml:id="Polygon_UUID_741a8f18-1100-467f-9c40-a919c34d2065_0_">
                      <gml:posList srsDimension="3">291310.0 5041910.0 6.0 291310.0 5041900.0 6.0 291310.0 5041900.0 0.0 291310.0 5041910.0 0.0 291310.0 5041910.0 6.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:CompositeSurface>
          </gml:exterior>
        </gml:Solid>
      </bldg:lod2Solid>
      <bldg:boundedBy>
        <bldg:GroundSurface gml:id="id_building_1_groundsurface_1">
          <gml:description>This is GroundSurface 1 (Building 1)</gml:description>
          <gml:name>GroundSurface 1 (Building 1)</gml:name>
          <creationDate>2026-10-06</creationDate>
          <bldg:lod2MultiSurface>
            <gml:MultiSurface gml:id="id_building_1_groundsurface_1_lod2_geom">
              <gml:surfaceMember xlink:href="#id_building_1_polygon_3"/>
            </gml:MultiSurface>
          </bldg:lod2MultiSurface>
        </bldg:GroundSurface>
      </bldg:boundedBy>
      <bldg:boundedBy>
        <bldg:RoofSurface gml:id="id_building_1_roofsurface_1">
          <gml:description>This is RoofSurface 1 (Building 1)</gml:description>
          <gml:name>RoofSurface 1 (Building 1)</gml:name>
          <creationDate>2026-10-06</creationDate>
          <bldg:lod2MultiSurface>
            <gml:MultiSurface gml:id="id_building_1_roofsurface_1_lod2_geom">
              <gml:surfaceMember>
                <gml:Polygon gml:id="id_building_1_polygon_1">
                  <gml:exterior>
                    <gml:LinearRing gml:id="id_building_1_polygon_1_0_">
                      <gml:posList srsDimension="3">291300.0 5041900.0 6.0 291305.0 5041900.0 9.0 291305.0 5041910.0 9.0 291300.0 5041910.0 6.0 291300.0 5041900.0 6.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:MultiSurface>
          </bldg:lod2MultiSurface>
        </bldg:RoofSurface>
      </bldg:boundedBy>
      <bldg:boundedBy>
        <bldg:RoofSurface gml:id="id_building_1_roofsurface_2">
          <gml:description>This is RoofSurface 2 (Building 1)</gml:description>
          <gml:name>RoofSurface 2 (Building 1)</gml:name>
          <creationDate>2026-10-06</creationDate>
          <bldg:lod2MultiSurface>
            <gml:MultiSurface gml:id="id_building_1_roofsurface_2_lod2_geom">
              <gml:surfaceMember>
                <gml:Polygon gml:id="id_building_1_polygon_2">
                  <gml:exterior>
                    <gml:LinearRing gml:id="id_building_1_polygon_2_0_">
                      <gml:posList srsDimension="3">291305.0 5041900.0 9.0 291310.0 5041900.0 6.0 291310.0 5041910.0 6.0 291305.0 5041910.0 9.0 291305.0 5041900.0 9.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:MultiSurface>
          </bldg:lod2MultiSurface>
        </bldg:RoofSurface>
      </bldg:boundedBy>
      <bldg:boundedBy>
        <bldg:WallSurface gml:id="id_building_1_wallsurface_1">
          <gml:description>This is WallSurface 1 (Building 1)</gml:description>
          <gml:name>WallSurface 1 (Building 1)</gml:name>
          <creationDate>2026-10-06</creationDate>
          <bldg:lod2MultiSurface>
            <gml:MultiSurface gml:id="id_building_1_wallsurface_1_lod2_geom">
              <gml:surfaceMember>
                <gml:Polygon gml:id="id_building_1_polygon_5">
                  <gml:exterior>
                    <gml:LinearRing gml:id="id_building_1_polygon_5_0_">
                      <gml:posList srsDimension="3">291300.0 5041900.0 0.0 291310.0 5041900.0 0.0 291310.0 5041900.0 6.0 291305.0 5041900.0 9.0 291300.0 5041900.0 6.0 291300.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:MultiSurface>
          </bldg:lod2MultiSurface>
        </bldg:WallSurface>
      </bldg:boundedBy>
      <bldg:boundedBy>
        <bldg:WallSurface gml:id="id_building_1_wallsurface_2">
          <gml:description>This is WallSurface 2 (Building 1)</gml:description>
          <gml:name>WallSurface 2 (Building 1)</gml:name>
          <creationDate>2026-10-06</creationDate>
          <bldg:lod2MultiSurface>
            <gml:MultiSurface gml:id="id_building_1_wallsurface_2_lod2_geom">
              <gml:surfaceMember>
                <gml:Polygon gml:id="id_building_1_polygon_4">
                  <gml:exterior>
                    <gml:LinearRing gml:id="id_building_1_polygon_4_0_">
                      <gml:posList srsDimension="3">291300.0 5041910.0 0.0 291300.0 5041910.0 6.0 291305.0 5041910.0 9.0 291310.0 5041910.0 6.0 291310.0 5041910.0 0.0 291300.0 5041910.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:MultiSurface>
          </bldg:lod2MultiSurface>
        </bldg:WallSurface>
      </bldg:boundedBy>
      <bldg:boundedBy>
        <bldg:WallSurface gml:id="id_building_1_wallsurface_3">
          <gml:description>This is WallSurface 3 (Building 1)</gml:description>
          <gml:name>WallSurface 3 (Building 1)</gml:name>
          <creationDate>2026-10-06</creationDate>
          <bldg:lod2MultiSurface>
            <gml:MultiSurface gml:id="id_building_1_wallsurface_3_lod2_geom">
              <gml:surfaceMember>
                <gml:Polygon gml:id="id_building_1_polygon_7">
                  <gml:exterior>
                    <gml:LinearRing gml:id="id_building_1_polygon_7_0_">
                      <gml:posList srsDimension="3">291300.0 5041900.0 0.0 291300.0 5041900.0 6.0 291300.0 5041910.0 6.0 291300.0 5041910.0 0.0 291300.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:MultiSurface>
          </bldg:lod2MultiSurface>
        </bldg:WallSurface>
      </bldg:boundedBy>
      <bldg:address>
        <Address>
          <xalAddress>
            <xAL:AddressDetails>
              <xAL:Country>
                <xAL:CountryName>Bespin Territories</xAL:CountryName>
                <xAL:Locality Type="City">
                  <xAL:LocalityName>Alderaan</xAL:LocalityName>
                  <xAL:Thoroughfare Type="Street">
                    <xAL:ThoroughfareNumber>1</xAL:ThoroughfareNumber>
                    <xAL:ThoroughfareName>Bespin Square</xAL:ThoroughfareName>
                  </xAL:Thoroughfare>
                  <xAL:PostalCode>
                    <xAL:PostalCodeNumber>1977SW</xAL:PostalCodeNumber>
                  </xAL:PostalCode>
                </xAL:Locality>
              </xAL:Country>
            </xAL:AddressDetails>
          </xalAddress>
          <multiPoint>
            <gml:MultiPoint>
              <gml:pointMember>
                <gml:Point>
                  <gml:pos srsDimension="3">291305.0 5041905.0 0.0</gml:pos>
                </gml:Point>
              </gml:pointMember>
            </gml:MultiPoint>
          </multiPoint>
        </Address>
      </bldg:address>
    </bldg:Building>
  </cityObjectMember>
  <cityObjectMember>
    <bldg:Building gml:id="house_lod2_hull_3">
      <gml:description>The same house whose thermal zone coincides with the LoD2 hull of the building.</gml:description>
      <gml:name>Report house - LoD2 hull</gml:name>
      <gml:boundedBy>
        <gml:Envelope srsName="urn:ogc:def:crs:EPSG::4326" srsDimension="3">
          <gml:lowerCorner>291340.0 5041900.0 0.0</gml:lowerCorner>
          <gml:upperCorner>291350.0 5041910.0 9.0</gml:upperCorner>
        </gml:Envelope>
      </gml:boundedBy>
      <creationDate>2024-09-25</creationDate>
      <bldg:class codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_class.xml">habitation</bldg:class>
      <bldg:function codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_function.xml">residential building</bldg:function>
      <bldg:yearOfConstruction>1955</bldg:yearOfConstruction>
      <bldg:roofType codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_roofType.xml">gabled roof</bldg:roofType>
      <bldg:measuredHeight uom="m">9.0</bldg:measuredHeight>
      <bldg:storeysAboveGround>2</bldg:storeysAboveGround>
      <bldg:storeysBelowGround>0</bldg:storeysBelowGround>
      <bldg:storeyHeightsAboveGround uom="m">3.0</bldg:storeyHeightsAboveGround>
      <bldg:lod0FootPrint>
        <gml:MultiSurface gml:id="fx7_id_building_1_footprint_MultiSurf">
          <gml:surfaceMember>
            <gml:OrientableSurface orientation="-">
              <gml:baseSurface>
                <gml:Polygon gml:id="fx7_id_building_1_polygon_3">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx7_id_building_1_polygon_3_0_">
                      <gml:posList srsDimension="3">291340.0 5041900.0 0.0 291340.0 5041910.0 0.0 291350.0 5041910.0 0.0 291350.0 5041900.0 0.0 291340.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:baseSurface>
            </gml:OrientableSurface>
          </gml:surfaceMember>
        </gml:MultiSurface>
      </bldg:lod0FootPrint>
      <bldg:lod1Solid>
        <gml:Solid gml:id="fx7_id_building_1_lod1_Solid">
          <gml:exterior>
            <gml:CompositeSurface gml:id="fx7_id_building_1_lod1_CompSurf">
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx7_id_building_1_lod1_Polygon_4">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx7_id_building_1_lod1_Polygon_4_0_">
                      <gml:posList srsDimension="3">291350.0 5041910.0 0.0 291340.0 5041910.0 0.0 291340.0 5041910.0 7.5 291350.0 5041910.0 7.5 291350.0 5041910.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx7_id_building_1_lod1_Polygon_5">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx7_id_building_1_lod1_Polygon_5_0_">
                      <gml:posList srsDimension="3">291340.0 5041910.0 0.0 291340.0 5041900.0 0.0 291340.0 5041900.0 7.5 291340.0 5041910.0 7.5 291340.0 5041910.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx7_id_building_1_lod1_Polygon_1">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx7_id_building_1_lod1_Polygon_1_0_">
                      <gml:posList srsDimension="3">291340.0 5041900.0 0.0 291340.0 5041910.0 0.0 291350.0 5041910.0 0.0 291350.0 5041900.0 0.0 291340.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx7_id_building_1_lod1_Polygon_2">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx7_id_building_1_lod1_Polygon_2_0_">
                      <gml:posList srsDimension="3">291340.0 5041900.0 0.0 291350.0 5041900.0 0.0 291350.0 5041900.0 7.5 291340.0 5041900.0 7.5 291340.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx7_id_building_1_lod1_Polygon_3">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx7_id_building_1_lod1_Polygon_3_0_">
                      <gml:posList srsDimension="3">291350.0 5041900.0 0.0 291350.0 5041910.0 0.0 291350.0 5041910.0 7.5 291350.0 5041900.0 7.5 291350.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx7_id_building_1_lod1_Polygon_6">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx7_id_building_1_lod1_Polygon_6_0_">
                      <gml:posList srsDimension="3">291340.0 5041900.0 7.5 291350.0 5041900.0 7.5 291350.0 5041910.0 7.5 291340.0 5041910.0 7.5 291340.0 5041900.0 7.5</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:CompositeSurface>
          </gml:exterior>
        </gml:Solid>
      </bldg:lod1Solid>
      <bldg:lod2Solid>
        <gml:Solid gml:id="fx7_id_building_1_lod2_Solid">
          <gml:exterior>
            <gml:CompositeSurface gml:id="fx7_id_building_1_lod2_CompSurf">
              <gml:surfaceMember xlink:href="#fx7_id_building_1_polygon_4"/>
              <gml:surfaceMember xlink:href="#fx7_id_building_1_polygon_5"/>
              <gml:surfaceMember xlink:href="#fx7_id_building_1_polygon_7"/>
              <gml:surfaceMember xlink:href="#fx7_id_building_1_polygon_1"/>
              <gml:surfaceMember xlink:href="#fx7_id_building_1_polygon_2"/>
              <gml:surfaceMember xlink:href="#fx7_id_building_1_polygon_3"/>
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx7_Polygon_UUID_741a8f18-1100-467f-9c40-a919c34d2065">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx7_Polygon_UUID_741a8f18-1100-467f-9c40-a919c34d2065_0_">
                      <gml:posList srsDimension="3">291350.0 5041910.0 6.0 291350.0 5041900.0 6.0 291350.0 5041900.0 0.0 291350.0 5041910.0 0.0 291350.0 5041910.0 6.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:CompositeSurface>
          </gml:exterior>
        </gml:Solid>
      </bldg:lod2Solid>
      <bldg:boundedBy>
        <bldg:GroundSurface gml:id="fx7_id_building_1_groundsurface_1">
          <gml:description>This is GroundSurface 1 (Building 1)</gml:description>
          <gml:name>GroundSurface 1 (Building 1)</gml:name>
          <creationDate>2026-10-06</creationDate>
          <bldg:lod2MultiSurface>
            <gml:MultiSurface gml:id="fx7_id_building_1_groundsurface_1_lod2_geom">
              <gml:surfaceMember xlink:href="#fx7_id_building_1_polygon_3"/>
            </gml:MultiSurface>
          </bldg:lod2MultiSurface>
        </bldg:GroundSurface>
      </bldg:boundedBy>
      <bldg:boundedBy>
        <bldg:RoofSurface gml:id="fx7_id_building_1_roofsurface_1">
          <gml:description>This is RoofSurface 1 (Building 1)</gml:description>
          <gml:name>RoofSurface 1 (Building 1)</gml:name>
          <creationDate>2026-10-06</creationDate>
          <bldg:lod2MultiSurface>
            <gml:MultiSurface gml:id="fx7_id_building_1_roofsurface_1_lod2_geom">
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx7_id_building_1_polygon_1">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx7_id_building_1_polygon_1_0_">
                      <gml:posList srsDimension="3">291340.0 5041900.0 6.0 291345.0 5041900.0 9.0 291345.0 5041910.0 9.0 291340.0 5041910.0 6.0 291340.0 5041900.0 6.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:MultiSurface>
          </bldg:lod2MultiSurface>
        </bldg:RoofSurface>
      </bldg:boundedBy>
      <bldg:boundedBy>
        <bldg:RoofSurface gml:id="fx7_id_building_1_roofsurface_2">
          <gml:description>This is RoofSurface 2 (Building 1)</gml:description>
          <gml:name>RoofSurface 2 (Building 1)</gml:name>
          <creationDate>2026-10-06</creationDate>
          <bldg:lod2MultiSurface>
            <gml:MultiSurface gml:id="fx7_id_building_1_roofsurface_2_lod2_geom">
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx7_id_building_1_polygon_2">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx7_id_building_1_polygon_2_0_">
                      <gml:posList srsDimension="3">291345.0 5041900.0 9.0 291350.0 5041900.0 6.0 291350.0 5041910.0 6.0 291345.0 5041910.0 9.0 291345.0 5041900.0 9.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:MultiSurface>
          </bldg:lod2MultiSurface>
        </bldg:RoofSurface>
      </bldg:boundedBy>
      <bldg:boundedBy>
        <bldg:WallSurface gml:id="fx7_id_building_1_wallsurface_1">
          <gml:description>This is WallSurface 1 (Building 1)</gml:description>
          <gml:name>WallSurface 1 (Building 1)</gml:name>
          <creationDate>2026-10-06</creationDate>
          <bldg:lod2MultiSurface>
            <gml:MultiSurface gml:id="fx7_id_building_1_wallsurface_1_lod2_geom">
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx7_id_building_1_polygon_5">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx7_id_building_1_polygon_5_0_">
                      <gml:posList srsDimension="3">291340.0 5041900.0 0.0 291350.0 5041900.0 0.0 291350.0 5041900.0 6.0 291345.0 5041900.0 9.0 291340.0 5041900.0 6.0 291340.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:MultiSurface>
          </bldg:lod2MultiSurface>
        </bldg:WallSurface>
      </bldg:boundedBy>
      <bldg:boundedBy>
        <bldg:WallSurface gml:id="fx7_id_building_1_wallsurface_2">
          <gml:description>This is WallSurface 2 (Building 1)</gml:description>
          <gml:name>WallSurface 2 (Building 1)</gml:name>
          <creationDate>2026-10-06</creationDate>
          <bldg:lod2MultiSurface>
            <gml:MultiSurface gml:id="fx7_id_building_1_wallsurface_2_lod2_geom">
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx7_id_building_1_polygon_4">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx7_id_building_1_polygon_4_0_">
                      <gml:posList srsDimension="3">291340.0 5041910.0 0.0 291340.0 5041910.0 6.0 291345.0 5041910.0 9.0 291350.0 5041910.0 6.0 291350.0 5041910.0 0.0 291340.0 5041910.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:MultiSurface>
          </bldg:lod2MultiSurface>
        </bldg:WallSurface>
      </bldg:boundedBy>
      <bldg:boundedBy>
        <bldg:WallSurface gml:id="fx7_id_building_1_wallsurface_3">
          <gml:description>This is WallSurface 3 (Building 1)</gml:description>
          <gml:name>WallSurface 3 (Building 1)</gml:name>
          <creationDate>2026-10-06</creationDate>
          <bldg:lod2MultiSurface>
            <gml:MultiSurface gml:id="fx7_id_building_1_wallsurface_3_lod2_geom">
              <gml:surfaceMember>
                <gml:Polygon gml:id="fx7_id_building_1_polygon_7">
                  <gml:exterior>
                    <gml:LinearRing gml:id="fx7_id_building_1_polygon_7_0_">
                      <gml:posList srsDimension="3">291340.0 5041900.0 0.0 291340.0 5041900.0 6.0 291340.0 5041910.0 6.0 291340.0 5041910.0 0.0 291340.0 5041900.0 0.0</gml:posList>
                    </gml:LinearRing>
                  </gml:exterior>
                </gml:Polygon>
              </gml:surfaceMember>
            </gml:MultiSurface>
          </bldg:lod2MultiSurface>
        </bldg:WallSurface>
      </bldg:boundedBy>
      <bldg:address>
        <Address>
          <xalAddress>
            <xAL:AddressDetails>
              <xAL:Country>
                <xAL:CountryName>Bespin Territories</xAL:CountryName>
                <xAL:Locality Type="City">
                  <xAL:LocalityName>Alderaan</xAL:LocalityName>
                  <xAL:Thoroughfare Type="Street">
                    <xAL:ThoroughfareNumber>1</xAL:ThoroughfareNumber>
                    <xAL:ThoroughfareName>Bespin Square</xAL:ThoroughfareName>
                  </xAL:Thoroughfare>
                  <xAL:PostalCode>
                    <xAL:PostalCodeNumber>1977SW</xAL:PostalCodeNumber>
                  </xAL:PostalCode>
                </xAL:Locality>
              </xAL:Country>
            </xAL:AddressDetails>
          </xalAddress>
          <multiPoint>
            <gml:MultiPoint>
              <gml:pointMember>
                <gml:Point>
                  <gml:pos srsDimension="3">291345.0 5041905.0 0.0</gml:pos>
                </gml:Point>
              </gml:pointMember>
            </gml:MultiPoint>
          </multiPoint>
        </Address>
      </bldg:address>
    </bldg:Building>
  </cityObjectMember>
</CityModel>