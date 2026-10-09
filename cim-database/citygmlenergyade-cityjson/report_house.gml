<?xml version='1.0' encoding='utf-8'?>
<!--
  REPORT HOUSE - one terraced house, described four ways, in Venice
  ==============================================================================
  What it is for: the capability report. Path A reads the SAME house at every level
  of detail the Energy ADE allows; Path B runs them, so their results can be compared.

    house_lod3_1        LoD3: three real windows cut into the walls
    house_lod2_2        the same house at LoD2: no window geometry, the glass only as
                        declared numbers on each wall
    house_lod2_hull_3   the same house whose thermal zone coincides with the LoD2 hull,
                        so the zone uses the building's own surfaces
    house_lod1_4        a plain LoD1 box of the same size: no windows and no party
                        wall, which is all LoD1 may say. Its zone states one average
                        U-value for the whole shell (0.514: the LoD3 house's walls,
                        windows, roof and floor, weighted by area)

  Each id ends in its own number, as in 'Alderaan': QGIS numbers a feature from the
  digits at the end of its gml:id, so two ids ending in the same digit would show as one.

  HOW IT WAS MADE - nothing hand-written. Copied from an earlier test file,
  fixture_lod1_lod2_lod3.gml (now removed; it is in the git history), itself cut from
  the Energy ADE 3.0 test dataset 'Alderaan', Giorgio Agugiaro, 3D Geoinformation,
  TU Delft: the four buildings above, element for element, and the three libraries
  they reference. Only NUMBERS were changed:

    place     moved to Venice-Mestre, EPSG:32633 (UTM 33N), the four in a row 20 m
              apart; the source sat at the origin of EPSG:32632
    height    every height x 0.6: walls 10 -> 6 m (2 storeys of 3 m), ridge 15 -> 9 m,
              roof pitch 45 -> 31 deg; measuredHeight, storeysAboveGround (3 -> 2) and
              highestRoofEdge follow
    areas     wall and window areas x 0.6 (they are as wide and 0.6 as high); each roof
              pitch 70.7 -> 58.3 m2; building gross floor 300 -> 200 m2
    glass     roof glass removed (the source declared 25 % of each roof, and one roof
              stated 5 m2 opaque of 70.7); each wall's stated ratio set to what its
              window measures (0.216 and 0.16), so LoD3 and LoD2 carry the same glass
    zone      the thermal zone now states its heated floor area, 180 m2
              (energyReferenceArea: 2 storeys x 90 m2 net), beside its unchanged
              100 m2 footprint; net volume 875 -> 486 m3 (180 m2 x 2.7 m); gross
              volume 1250 -> 750 m3 (600 m3 for the LoD1 box)

  Everything else - constructions, U-values, usage and occupancy values - is as in
  the source, except ONE ADDED construction, id_layered_construction_hull_6: the
  average U-value the LoD1 zone states (Energy ADE 3.0 Table 1: at LoD1 a thermal zone
  may carry a LayeredConstruction). Without it the LoD1 box stated no construction at
  all and fell back to a default, so it differed for a reason that is not LoD1's.

  TEST DEVICES, ADDED BY HAND (2026-10-03), to test reading a building's plant from the file
  (nothing else was changed for them):
    house_lod1_4        a heat pump with a EuReCa plant name, 6 kW, heating only
    house_lod2_hull_3   a gas boiler and a chiller described by their own values
                        (EuReCa's "From manual parameters"); they need the generics
                        namespace (gen:) declared on the CityModel below
  house_lod3_1 and house_lod2_2 have no device, so their plant comes from the run file.
-->
<!-- Energy ADE 3.0 beta 7: xmlns:nrg3 + xsi:schemaLocation to Energy_ADE_3.0_beta7.xsd in this folder. -->
<core:CityModel
	xmlns:app="http://www.opengis.net/citygml/appearance/2.0"
	xmlns:bldg="http://www.opengis.net/citygml/building/2.0"
	xmlns:brid="http://www.opengis.net/citygml/bridge/2.0"
	xmlns:core="http://www.opengis.net/citygml/2.0"
	xmlns:dem="http://www.opengis.net/citygml/relief/2.0"
	xmlns:frn="http://www.opengis.net/citygml/cityfurniture/2.0"
	xmlns:gen="http://www.opengis.net/citygml/generics/2.0"
	xmlns:gml="http://www.opengis.net/gml"
	xmlns:grp="http://www.opengis.net/citygml/cityobjectgroup/2.0"
	xmlns:luse="http://www.opengis.net/citygml/landuse/2.0"
	xmlns:nrg3="http://www.citygml.org/ade/energy/3.0"
	xmlns:pbase="http://www.opengis.net/citygml/profiles/base/2.0"
	xmlns:sch="http://www.ascc.net/xml/schematron"
	xmlns:smil20="http://www.w3.org/2001/SMIL20/"
	xmlns:smil20lang="http://www.w3.org/2001/SMIL20/Language"
	xmlns:tex="http://www.opengis.net/citygml/texturedsurface/2.0"
	xmlns:tran="http://www.opengis.net/citygml/transportation/2.0"
	xmlns:tun="http://www.opengis.net/citygml/tunnel/2.0"
	xmlns:veg="http://www.opengis.net/citygml/vegetation/2.0"
	xmlns:wtr="http://www.opengis.net/citygml/waterbody/2.0"
	xmlns:xAL="urn:oasis:names:tc:ciq:xsdschema:xAL:2.0"
	xmlns:xlink="http://www.w3.org/1999/xlink"
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
	xsi:schemaLocation="http://www.citygml.org/ade/energy/3.0 Energy_ADE_3.0_beta7.xsd">
	<gml:description>One terraced house described at LoD3, LoD2, LoD2-hull and LoD1, in Venice. Derived from the Energy ADE 3.0 test dataset 'Alderaan' created by Giorgio Agugiaro (g.agugiaro@tudelft.nl).</gml:description>
	<gml:name>Report house, Venice</gml:name>
	<gml:boundedBy>
		<gml:Envelope srsName="EPSG:32633" srsDimension="3">
			<gml:lowerCorner>291300.0000 5041900.0000 0.0000</gml:lowerCorner>
			<gml:upperCorner>291370.0000 5041910.0000 9.0000</gml:upperCorner>
		</gml:Envelope>
	</gml:boundedBy>
	<core:cityObjectMember>
		<nrg3:LayeredConstructionLibrary gml:id="id_layered_construction_library_1">
			<gml:description>This is Layered Construction Library 1</gml:description>
			<gml:name>Layered Construction Library 1</gml:name>
			<nrg3:type codeSpace="layered_construction_library_type_codeSpace">layered_construction_library_type</nrg3:type>
			<nrg3:source>TABULA</nrg3:source>
			<nrg3:author>Giorgio Agugiaro</nrg3:author>
			<nrg3:libraryMember>
				<nrg3:LayeredConstruction gml:id="id_layered_construction_glazing_5">
					<gml:description>This is LayeredConstruction Glazing 5 (without layers as children objects)</gml:description>
					<gml:name>LayeredConstruction Glazing 5 (no layers)</gml:name>
					<nrg3:libraryCode codeSpace="layered_constr_library_codeSpace">layered_constr_library_code_5</nrg3:libraryCode>
					<nrg3:uValue uom="W/(K*m^2)">1.9</nrg3:uValue>
					<nrg3:glazingRatio uom="unit interval">0.95</nrg3:glazingRatio>
					<nrg3:emissivity>
						<nrg3:Emissivity>
							<nrg3:fraction uom="unit interval">0.1</nrg3:fraction>
							<nrg3:surface>outside</nrg3:surface>
						</nrg3:Emissivity>
					</nrg3:emissivity>
					<nrg3:emissivity>
						<nrg3:Emissivity>
							<nrg3:fraction uom="unit interval">0.2</nrg3:fraction>
							<nrg3:surface>inside</nrg3:surface>
						</nrg3:Emissivity>
					</nrg3:emissivity>
					<nrg3:reflectance>
						<nrg3:Reflectance>
							<nrg3:fraction uom="unit interval">0.2</nrg3:fraction>
							<nrg3:surface>outside</nrg3:surface>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Reflectance>
					</nrg3:reflectance>
					<nrg3:reflectance>
						<nrg3:Reflectance>
							<nrg3:fraction uom="unit interval">0.3</nrg3:fraction>
							<nrg3:surface>inside</nrg3:surface>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Reflectance>
					</nrg3:reflectance>
					<nrg3:transmittance>
						<nrg3:Transmittance>
							<nrg3:fraction uom="unit interval">0.7</nrg3:fraction>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Transmittance>
					</nrg3:transmittance>
					<nrg3:transmittance>
						<nrg3:Transmittance>
							<nrg3:fraction uom="unit interval">0.5</nrg3:fraction>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Transmittance>
					</nrg3:transmittance>
				</nrg3:LayeredConstruction>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:LayeredConstruction gml:id="id_layered_construction_ground_1">
					<gml:description>This is LayeredConstruction Ground 1 (from inside to outside)</gml:description>
					<gml:name>LayeredConstruction Ground 1</gml:name>
					<nrg3:libraryCode codeSpace="layered_constr_library_codeSpace">layered_constr_library_code_1</nrg3:libraryCode>
					<nrg3:uValue uom="W/(K*m^2)">0.42</nrg3:uValue>
					<nrg3:glazingRatio uom="unit interval">0.95</nrg3:glazingRatio>
					<nrg3:emissivity>
						<nrg3:Emissivity>
							<nrg3:fraction uom="unit interval">0.1</nrg3:fraction>
							<nrg3:surface>outside</nrg3:surface>
						</nrg3:Emissivity>
					</nrg3:emissivity>
					<nrg3:emissivity>
						<nrg3:Emissivity>
							<nrg3:fraction uom="unit interval">0.2</nrg3:fraction>
							<nrg3:surface>inside</nrg3:surface>
						</nrg3:Emissivity>
					</nrg3:emissivity>
					<nrg3:reflectance>
						<nrg3:Reflectance>
							<nrg3:fraction uom="unit interval">0.2</nrg3:fraction>
							<nrg3:surface>outside</nrg3:surface>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Reflectance>
					</nrg3:reflectance>
					<nrg3:reflectance>
						<nrg3:Reflectance>
							<nrg3:fraction uom="unit interval">0.3</nrg3:fraction>
							<nrg3:surface>inside</nrg3:surface>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Reflectance>
					</nrg3:reflectance>
					<nrg3:transmittance>
						<nrg3:Transmittance>
							<nrg3:fraction uom="unit interval">0.7</nrg3:fraction>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Transmittance>
					</nrg3:transmittance>
					<nrg3:transmittance>
						<nrg3:Transmittance>
							<nrg3:fraction uom="unit interval">0.5</nrg3:fraction>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Transmittance>
					</nrg3:transmittance>
					<nrg3:layer>
						<nrg3:Layer gml:id="id_layer_1">
							<gml:description>This is Layer 1</gml:description>
							<gml:name>Layer 1</gml:name>
							<nrg3:thickness uom="mm">40</nrg3:thickness>
							<nrg3:material xlink:href="id_solid_material_1"/>
						</nrg3:Layer>
					</nrg3:layer>
					<nrg3:layer>
						<nrg3:Layer gml:id="id_layer_2">
							<gml:description>This is Layer 2</gml:description>
							<gml:name>Layer 2</gml:name>
							<nrg3:thickness uom="mm">45</nrg3:thickness>
							<nrg3:material xlink:href="id_solid_material_2"/>
						</nrg3:Layer>
					</nrg3:layer>
					<nrg3:layer>
						<nrg3:Layer gml:id="id_layer_3">
							<gml:description>This is Layer 3</gml:description>
							<gml:name>Layer 3</gml:name>
							<nrg3:thickness uom="mm">80</nrg3:thickness>
							<nrg3:material xlink:href="id_solid_material_3"/>
						</nrg3:Layer>
					</nrg3:layer>
					<nrg3:layer>
						<nrg3:Layer gml:id="id_layer_4">
							<gml:description>This is Layer 4</gml:description>
							<gml:name>Layer 4</gml:name>
							<nrg3:thickness uom="mm">5</nrg3:thickness>
							<nrg3:material xlink:href="id_solid_material_4"/>
						</nrg3:Layer>
					</nrg3:layer>
					<nrg3:layer>
						<nrg3:Layer gml:id="id_layer_5">
							<gml:description>This is Layer 5</gml:description>
							<gml:name>Layer 5</gml:name>
							<nrg3:thickness uom="mm">300</nrg3:thickness>
							<nrg3:material xlink:href="id_solid_material_5"/>
						</nrg3:Layer>
					</nrg3:layer>
				</nrg3:LayeredConstruction>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:LayeredConstruction gml:id="id_layered_construction_iwall_4">
					<gml:description>This is LayeredConstruction Internal Wall 4 (from inside to outside)</gml:description>
					<gml:name>LayeredConstruction Internal Wall 4</gml:name>
					<nrg3:libraryCode codeSpace="layered_constr_library_codeSpace">layered_constr_library_code_4</nrg3:libraryCode>
					<nrg3:uValue uom="W/(K*m^2)">0.42</nrg3:uValue>
					<nrg3:glazingRatio uom="unit interval">0.95</nrg3:glazingRatio>
					<nrg3:emissivity>
						<nrg3:Emissivity>
							<nrg3:fraction uom="unit interval">0.1</nrg3:fraction>
							<nrg3:surface>outside</nrg3:surface>
						</nrg3:Emissivity>
					</nrg3:emissivity>
					<nrg3:emissivity>
						<nrg3:Emissivity>
							<nrg3:fraction uom="unit interval">0.2</nrg3:fraction>
							<nrg3:surface>inside</nrg3:surface>
						</nrg3:Emissivity>
					</nrg3:emissivity>
					<nrg3:reflectance>
						<nrg3:Reflectance>
							<nrg3:fraction uom="unit interval">0.2</nrg3:fraction>
							<nrg3:surface>outside</nrg3:surface>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Reflectance>
					</nrg3:reflectance>
					<nrg3:reflectance>
						<nrg3:Reflectance>
							<nrg3:fraction uom="unit interval">0.3</nrg3:fraction>
							<nrg3:surface>inside</nrg3:surface>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Reflectance>
					</nrg3:reflectance>
					<nrg3:transmittance>
						<nrg3:Transmittance>
							<nrg3:fraction uom="unit interval">0.7</nrg3:fraction>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Transmittance>
					</nrg3:transmittance>
					<nrg3:transmittance>
						<nrg3:Transmittance>
							<nrg3:fraction uom="unit interval">0.5</nrg3:fraction>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Transmittance>
					</nrg3:transmittance>
					<nrg3:layer>
						<nrg3:Layer gml:id="id_layer_16">
							<gml:description>This is Layer 16</gml:description>
							<gml:name>Layer 16</gml:name>
							<nrg3:thickness uom="mm">10</nrg3:thickness>
							<nrg3:material xlink:href="id_solid_material_16"/>
						</nrg3:Layer>
					</nrg3:layer>
					<nrg3:layer>
						<nrg3:Layer gml:id="id_layer_17">
							<gml:description>This is Layer 17</gml:description>
							<gml:name>Layer 17</gml:name>
							<nrg3:thickness uom="mm">200</nrg3:thickness>
							<nrg3:material xlink:href="id_solid_material_17"/>
						</nrg3:Layer>
					</nrg3:layer>
					<nrg3:layer>
						<nrg3:Layer gml:id="id_layer_18">
							<gml:description>This is Layer 18</gml:description>
							<gml:name>Layer 18</gml:name>
							<nrg3:thickness uom="mm">120</nrg3:thickness>
							<nrg3:material xlink:href="id_solid_material_18"/>
						</nrg3:Layer>
					</nrg3:layer>
				</nrg3:LayeredConstruction>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:LayeredConstruction gml:id="id_layered_construction_roof_3">
					<gml:description>This is LayeredConstruction Roof 3 (from inside to outside)</gml:description>
					<gml:name>LayeredConstruction Roof 3</gml:name>
					<nrg3:libraryCode codeSpace="layered_constr_library_codeSpace">layered_constr_library_code_3</nrg3:libraryCode>
					<nrg3:uValue uom="W/(K*m^2)">0.39</nrg3:uValue>
					<nrg3:glazingRatio uom="unit interval">0.95</nrg3:glazingRatio>
					<nrg3:emissivity>
						<nrg3:Emissivity>
							<nrg3:fraction uom="unit interval">0.1</nrg3:fraction>
							<nrg3:surface>outside</nrg3:surface>
						</nrg3:Emissivity>
					</nrg3:emissivity>
					<nrg3:emissivity>
						<nrg3:Emissivity>
							<nrg3:fraction uom="unit interval">0.2</nrg3:fraction>
							<nrg3:surface>inside</nrg3:surface>
						</nrg3:Emissivity>
					</nrg3:emissivity>
					<nrg3:reflectance>
						<nrg3:Reflectance>
							<nrg3:fraction uom="unit interval">0.2</nrg3:fraction>
							<nrg3:surface>outside</nrg3:surface>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Reflectance>
					</nrg3:reflectance>
					<nrg3:reflectance>
						<nrg3:Reflectance>
							<nrg3:fraction uom="unit interval">0.3</nrg3:fraction>
							<nrg3:surface>inside</nrg3:surface>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Reflectance>
					</nrg3:reflectance>
					<nrg3:transmittance>
						<nrg3:Transmittance>
							<nrg3:fraction uom="unit interval">0.7</nrg3:fraction>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Transmittance>
					</nrg3:transmittance>
					<nrg3:transmittance>
						<nrg3:Transmittance>
							<nrg3:fraction uom="unit interval">0.5</nrg3:fraction>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Transmittance>
					</nrg3:transmittance>
					<nrg3:layer>
						<nrg3:Layer gml:id="id_layer_11">
							<gml:description>This is Layer 11</gml:description>
							<gml:name>Layer 11</gml:name>
							<nrg3:thickness uom="mm">10</nrg3:thickness>
							<nrg3:material xlink:href="id_solid_material_11"/>
						</nrg3:Layer>
					</nrg3:layer>
					<nrg3:layer>
						<nrg3:Layer gml:id="id_layer_12">
							<gml:description>This is Layer 12</gml:description>
							<gml:name>Layer 12</gml:name>
							<nrg3:thickness uom="mm">200</nrg3:thickness>
							<nrg3:material xlink:href="id_solid_material_12"/>
						</nrg3:Layer>
					</nrg3:layer>
					<nrg3:layer>
						<nrg3:Layer gml:id="id_layer_13">
							<gml:description>This is Layer 13</gml:description>
							<gml:name>Layer 13</gml:name>
							<nrg3:thickness uom="mm">30</nrg3:thickness>
							<nrg3:material xlink:href="id_gas_2"/>
						</nrg3:Layer>
					</nrg3:layer>
					<nrg3:layer>
						<nrg3:Layer gml:id="id_layer_14">
							<gml:description>This is Layer 14</gml:description>
							<gml:name>Layer 14</gml:name>
							<nrg3:thickness uom="mm">120</nrg3:thickness>
							<nrg3:material xlink:href="id_solid_material_14"/>
						</nrg3:Layer>
					</nrg3:layer>
					<nrg3:layer>
						<nrg3:Layer gml:id="id_layer_15">
							<gml:description>This is Layer 15</gml:description>
							<gml:name>Layer 15</gml:name>
							<nrg3:thickness uom="mm">5</nrg3:thickness>
							<nrg3:material xlink:href="id_solid_material_15"/>
						</nrg3:Layer>
					</nrg3:layer>
				</nrg3:LayeredConstruction>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:LayeredConstruction gml:id="id_layered_construction_wall_2">
					<gml:description>This is LayeredConstruction Wall 2 (from inside to outside)</gml:description>
					<gml:name>LayeredConstruction Wall 2</gml:name>
					<nrg3:libraryCode codeSpace="layered_constr_library_codeSpace">layered_constr_library_code_2</nrg3:libraryCode>
					<nrg3:uValue uom="W/(K*m^2)">0.31</nrg3:uValue>
					<nrg3:glazingRatio uom="unit interval">0.95</nrg3:glazingRatio>
					<nrg3:emissivity>
						<nrg3:Emissivity>
							<nrg3:fraction uom="unit interval">0.1</nrg3:fraction>
							<nrg3:surface>outside</nrg3:surface>
						</nrg3:Emissivity>
					</nrg3:emissivity>
					<nrg3:emissivity>
						<nrg3:Emissivity>
							<nrg3:fraction uom="unit interval">0.2</nrg3:fraction>
							<nrg3:surface>inside</nrg3:surface>
						</nrg3:Emissivity>
					</nrg3:emissivity>
					<nrg3:reflectance>
						<nrg3:Reflectance>
							<nrg3:fraction uom="unit interval">0.2</nrg3:fraction>
							<nrg3:surface>outside</nrg3:surface>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Reflectance>
					</nrg3:reflectance>
					<nrg3:reflectance>
						<nrg3:Reflectance>
							<nrg3:fraction uom="unit interval">0.3</nrg3:fraction>
							<nrg3:surface>inside</nrg3:surface>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Reflectance>
					</nrg3:reflectance>
					<nrg3:transmittance>
						<nrg3:Transmittance>
							<nrg3:fraction uom="unit interval">0.7</nrg3:fraction>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Transmittance>
					</nrg3:transmittance>
					<nrg3:transmittance>
						<nrg3:Transmittance>
							<nrg3:fraction uom="unit interval">0.5</nrg3:fraction>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Transmittance>
					</nrg3:transmittance>
					<nrg3:layer>
						<nrg3:Layer gml:id="id_layer_6">
							<gml:description>This is Layer 6</gml:description>
							<gml:name>Layer 6</gml:name>
							<nrg3:thickness uom="mm">10</nrg3:thickness>
							<nrg3:material xlink:href="id_solid_material_6"/>
						</nrg3:Layer>
					</nrg3:layer>
					<nrg3:layer>
						<nrg3:Layer gml:id="id_layer_7">
							<gml:description>This is Layer 7</gml:description>
							<gml:name>Layer 7</gml:name>
							<nrg3:thickness uom="mm">300</nrg3:thickness>
							<nrg3:material xlink:href="id_solid_material_7"/>
						</nrg3:Layer>
					</nrg3:layer>
					<nrg3:layer>
						<nrg3:Layer gml:id="id_layer_8">
							<gml:description>This is Layer 8</gml:description>
							<gml:name>Layer 8</gml:name>
							<nrg3:thickness uom="mm">30</nrg3:thickness>
							<nrg3:material xlink:href="id_gas_1"/>
						</nrg3:Layer>
					</nrg3:layer>
					<nrg3:layer>
						<nrg3:Layer gml:id="id_layer_9">
							<gml:description>This is Layer 9</gml:description>
							<gml:name>Layer 9</gml:name>
							<nrg3:thickness uom="mm">80</nrg3:thickness>
							<nrg3:material xlink:href="id_solid_material_9"/>
						</nrg3:Layer>
					</nrg3:layer>
					<nrg3:layer>
						<nrg3:Layer gml:id="id_layer_10">
							<gml:description>This is Layer 10</gml:description>
							<gml:name>Layer 10</gml:name>
							<nrg3:thickness uom="mm">20</nrg3:thickness>
							<nrg3:material xlink:href="id_solid_material_10"/>
						</nrg3:Layer>
					</nrg3:layer>
				</nrg3:LayeredConstruction>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:ReverseLayeredConstruction gml:id="id_reverse_layered_construction_ground_1">
					<gml:description>ReverseLayeredConstruction Ground 1 (from inside to outside) (reverse the order of the layers of the linked LayeredConstruction)</gml:description>
					<gml:name>ReverseLayeredConstruction Ground 1</gml:name>
					<nrg3:baseLayeredConstruction xlink:href="#id_layered_construction_ground_1"/>
				</nrg3:ReverseLayeredConstruction>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:ReverseLayeredConstruction gml:id="id_reverse_layered_construction_iwall_4">
					<gml:description>ReverseLayeredConstruction Internal Wall 4 (from inside to outside) (reverse the order of the layers of the linked LayeredConstruction)</gml:description>
					<gml:name>ReverseLayeredConstruction Internal Wall 4</gml:name>
					<nrg3:baseLayeredConstruction xlink:href="#id_layered_construction_iwall_4"/>
				</nrg3:ReverseLayeredConstruction>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:LayeredConstruction gml:id="id_layered_construction_hull_6">
					<gml:description>The whole outer shell of this house as one average: walls, windows, roof and ground floor of the LoD3 house, weighted by area. One U-value for a LoD1 zone, which may state no more (Energy ADE 3.0, Table 1).</gml:description>
					<gml:name>LayeredConstruction Hull 6 (average of the whole shell, no layers)</gml:name>
					<nrg3:uValue uom="W/(K*m^2)">0.514</nrg3:uValue>
				</nrg3:LayeredConstruction>
			</nrg3:libraryMember>
		</nrg3:LayeredConstructionLibrary>
	</core:cityObjectMember>
	<core:cityObjectMember>
		<nrg3:MaterialLibrary gml:id="id_material_library_1">
			<gml:description>This is Material Library 1</gml:description>
			<gml:name>Material Library 1</gml:name>
			<nrg3:type codeSpace="material_library_type_codeSpace">material_library_type</nrg3:type>
			<nrg3:source>TABULA</nrg3:source>
			<nrg3:author>Giorgio Agugiaro</nrg3:author>
			<nrg3:libraryMember>
				<nrg3:Gas gml:id="id_gas_1">
					<gml:description>This is Gas 1</gml:description>
					<gml:name>Gas 1</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">gas_code_1</nrg3:libraryCode>
					<nrg3:isVentilated>false</nrg3:isVentilated>
					<nrg3:rValue uom="J/K/mol">8.314</nrg3:rValue>
				</nrg3:Gas>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:Gas gml:id="id_gas_2">
					<gml:description>This is Gas 2</gml:description>
					<gml:name>Gas 2</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">gas_code_2</nrg3:libraryCode>
					<nrg3:isVentilated>false</nrg3:isVentilated>
					<nrg3:rValue uom="J/K/mol">8.314</nrg3:rValue>
				</nrg3:Gas>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:SolidMaterial gml:id="id_solid_material_1">
					<gml:description>This is SolidMaterial 1</gml:description>
					<gml:name>SolidMaterial 1</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">solid_material_code_1</nrg3:libraryCode>
					<nrg3:thermalConductivity uom="W/(K*m)">3.5</nrg3:thermalConductivity>
					<nrg3:density uom="kg/m^3">2500</nrg3:density>
					<nrg3:specificHeatCapacity uom="J/(kg*K)">0.9</nrg3:specificHeatCapacity>
					<nrg3:permeance uom="xxx">0.9</nrg3:permeance>
					<nrg3:porosity uom="ratio">0.05</nrg3:porosity>
					<nrg3:embodiedEnergy uom="kWh/kg">15.4</nrg3:embodiedEnergy>
					<nrg3:embodiedCarbon uom="kgCO2/kg">1.9</nrg3:embodiedCarbon>
				</nrg3:SolidMaterial>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:SolidMaterial gml:id="id_solid_material_2">
					<gml:description>This is SolidMaterial 2</gml:description>
					<gml:name>SolidMaterial 2</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">solid_material_code_2</nrg3:libraryCode>
					<nrg3:thermalConductivity uom="W/(K*m)">1.4</nrg3:thermalConductivity>
					<nrg3:density uom="kg/m^3">2000</nrg3:density>
					<nrg3:specificHeatCapacity uom="J/(kg*K)">0.9</nrg3:specificHeatCapacity>
					<nrg3:permeance uom="xxx">0.9</nrg3:permeance>
					<nrg3:porosity uom="ratio">0.1</nrg3:porosity>
					<nrg3:embodiedEnergy uom="kWh/kg">15.1</nrg3:embodiedEnergy>
					<nrg3:embodiedCarbon uom="kgCO2/kg">1.2</nrg3:embodiedCarbon>
				</nrg3:SolidMaterial>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:SolidMaterial gml:id="id_solid_material_3">
					<gml:description>This is SolidMaterial 3</gml:description>
					<gml:name>SolidMaterial 3</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">solid_material_code_3</nrg3:libraryCode>
					<nrg3:thermalConductivity uom="W/(K*m)">0.04</nrg3:thermalConductivity>
					<nrg3:density uom="kg/m^3">20</nrg3:density>
					<nrg3:specificHeatCapacity uom="J/(kg*K)">0.9</nrg3:specificHeatCapacity>
					<nrg3:permeance uom="xxx">0.9</nrg3:permeance>
					<nrg3:porosity uom="ratio">0.01</nrg3:porosity>
					<nrg3:embodiedEnergy uom="kWh/kg">2.1</nrg3:embodiedEnergy>
					<nrg3:embodiedCarbon uom="kgCO2/kg">2.1</nrg3:embodiedCarbon>
				</nrg3:SolidMaterial>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:SolidMaterial gml:id="id_solid_material_4">
					<gml:description>This is SolidMaterial 4</gml:description>
					<gml:name>SolidMaterial 4</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">solid_material_code_4</nrg3:libraryCode>
					<nrg3:thermalConductivity uom="W/(K*m)">0.23</nrg3:thermalConductivity>
					<nrg3:density uom="kg/m^3">1100</nrg3:density>
					<nrg3:specificHeatCapacity uom="J/(kg*K)">0.9</nrg3:specificHeatCapacity>
					<nrg3:permeance uom="xxx">0.9</nrg3:permeance>
					<nrg3:porosity uom="ratio">0.01</nrg3:porosity>
					<nrg3:embodiedEnergy uom="kWh/kg">9.8</nrg3:embodiedEnergy>
					<nrg3:embodiedCarbon uom="kgCO2/kg">7.3</nrg3:embodiedCarbon>
				</nrg3:SolidMaterial>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:SolidMaterial gml:id="id_solid_material_5">
					<gml:description>This is SolidMaterial 5</gml:description>
					<gml:name>SolidMaterial 5</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">solid_material_code_5</nrg3:libraryCode>
					<nrg3:thermalConductivity uom="W/(K*m)">2.3</nrg3:thermalConductivity>
					<nrg3:density uom="kg/m^3">2300</nrg3:density>
					<nrg3:specificHeatCapacity uom="J/(kg*K)">0.9</nrg3:specificHeatCapacity>
					<nrg3:permeance uom="xxx">0.9</nrg3:permeance>
					<nrg3:porosity uom="ratio">0.1</nrg3:porosity>
					<nrg3:embodiedEnergy uom="kWh/kg">0</nrg3:embodiedEnergy>
					<nrg3:embodiedCarbon uom="kgCO2/kg">2.8</nrg3:embodiedCarbon>
				</nrg3:SolidMaterial>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:SolidMaterial gml:id="id_solid_material_6">
					<gml:description>This is SolidMaterial 6</gml:description>
					<gml:name>SolidMaterial 6</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">solid_material_code_6</nrg3:libraryCode>
					<nrg3:thermalConductivity uom="W/(K*m)">0.7</nrg3:thermalConductivity>
					<nrg3:density uom="kg/m^3">1400</nrg3:density>
					<nrg3:specificHeatCapacity uom="J/(kg*K)">0.9</nrg3:specificHeatCapacity>
					<nrg3:permeance uom="xxx">0.9</nrg3:permeance>
					<nrg3:porosity uom="ratio">0.05</nrg3:porosity>
					<nrg3:embodiedEnergy uom="kWh/kg">8</nrg3:embodiedEnergy>
					<nrg3:embodiedCarbon uom="kgCO2/kg">3.3</nrg3:embodiedCarbon>
				</nrg3:SolidMaterial>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:SolidMaterial gml:id="id_solid_material_7">
					<gml:description>This is SolidMaterial 7</gml:description>
					<gml:name>SolidMaterial 7</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">solid_material_code_7</nrg3:libraryCode>
					<nrg3:thermalConductivity uom="W/(K*m)">0.8</nrg3:thermalConductivity>
					<nrg3:density uom="kg/m^3">1800</nrg3:density>
					<nrg3:specificHeatCapacity uom="J/(kg*K)">0.9</nrg3:specificHeatCapacity>
					<nrg3:permeance uom="xxx">0.9</nrg3:permeance>
					<nrg3:porosity uom="ratio">0.05</nrg3:porosity>
					<nrg3:embodiedEnergy uom="kWh/kg">2.2</nrg3:embodiedEnergy>
					<nrg3:embodiedCarbon uom="kgCO2/kg">1.4</nrg3:embodiedCarbon>
				</nrg3:SolidMaterial>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:SolidMaterial gml:id="id_solid_material_9">
					<gml:description>This is SolidMaterial 9</gml:description>
					<gml:name>SolidMaterial 9</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">solid_material_code_9</nrg3:libraryCode>
					<nrg3:thermalConductivity uom="W/(K*m)">0.035</nrg3:thermalConductivity>
					<nrg3:density uom="kg/m^3">20</nrg3:density>
					<nrg3:specificHeatCapacity uom="J/(kg*K)">0.9</nrg3:specificHeatCapacity>
					<nrg3:permeance uom="xxx">0.9</nrg3:permeance>
					<nrg3:porosity uom="ratio">0.01</nrg3:porosity>
					<nrg3:embodiedEnergy uom="kWh/kg">6.9</nrg3:embodiedEnergy>
					<nrg3:embodiedCarbon uom="kgCO2/kg">6.7</nrg3:embodiedCarbon>
				</nrg3:SolidMaterial>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:SolidMaterial gml:id="id_solid_material_10">
					<gml:description>This is SolidMaterial 10</gml:description>
					<gml:name>SolidMaterial 10</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">solid_material_code_10</nrg3:libraryCode>
					<nrg3:thermalConductivity uom="W/(K*m)">0.87</nrg3:thermalConductivity>
					<nrg3:density uom="kg/m^3">1800</nrg3:density>
					<nrg3:specificHeatCapacity uom="J/(kg*K)">0.9</nrg3:specificHeatCapacity>
					<nrg3:permeance uom="xxx">0.9</nrg3:permeance>
					<nrg3:porosity uom="ratio">0.05</nrg3:porosity>
					<nrg3:embodiedEnergy uom="kWh/kg">6.7</nrg3:embodiedEnergy>
					<nrg3:embodiedCarbon uom="kgCO2/kg">6.9</nrg3:embodiedCarbon>
				</nrg3:SolidMaterial>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:SolidMaterial gml:id="id_solid_material_11">
					<gml:description>This is SolidMaterial 11</gml:description>
					<gml:name>SolidMaterial 11</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">solid_material_code_11</nrg3:libraryCode>
					<nrg3:thermalConductivity uom="W/(K*m)">0.7</nrg3:thermalConductivity>
					<nrg3:density uom="kg/m^3">1400</nrg3:density>
					<nrg3:specificHeatCapacity uom="J/(kg*K)">0.9</nrg3:specificHeatCapacity>
					<nrg3:permeance uom="xxx">0.9</nrg3:permeance>
					<nrg3:porosity uom="ratio">0.05</nrg3:porosity>
					<nrg3:embodiedEnergy uom="kWh/kg">14.9</nrg3:embodiedEnergy>
					<nrg3:embodiedCarbon uom="kgCO2/kg">3.4</nrg3:embodiedCarbon>
				</nrg3:SolidMaterial>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:SolidMaterial gml:id="id_solid_material_12">
					<gml:description>This is SolidMaterial 12</gml:description>
					<gml:name>SolidMaterial 12</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">solid_material_code_12</nrg3:libraryCode>
					<nrg3:thermalConductivity uom="W/(K*m)">2.3</nrg3:thermalConductivity>
					<nrg3:density uom="kg/m^3">2400</nrg3:density>
					<nrg3:specificHeatCapacity uom="J/(kg*K)">0.9</nrg3:specificHeatCapacity>
					<nrg3:permeance uom="xxx">0.9</nrg3:permeance>
					<nrg3:porosity uom="ratio">0.1</nrg3:porosity>
					<nrg3:embodiedEnergy uom="kWh/kg">11.9</nrg3:embodiedEnergy>
					<nrg3:embodiedCarbon uom="kgCO2/kg">1.7</nrg3:embodiedCarbon>
				</nrg3:SolidMaterial>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:SolidMaterial gml:id="id_solid_material_14">
					<gml:description>This is SolidMaterial 14</gml:description>
					<gml:name>SolidMaterial 14</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">solid_material_code_14</nrg3:libraryCode>
					<nrg3:thermalConductivity uom="W/(K*m)">0.04</nrg3:thermalConductivity>
					<nrg3:density uom="kg/m^3">110</nrg3:density>
					<nrg3:specificHeatCapacity uom="J/(kg*K)">0.9</nrg3:specificHeatCapacity>
					<nrg3:permeance uom="xxx">0.9</nrg3:permeance>
					<nrg3:porosity uom="ratio">0.01</nrg3:porosity>
					<nrg3:embodiedEnergy uom="kWh/kg">19.9</nrg3:embodiedEnergy>
					<nrg3:embodiedCarbon uom="kgCO2/kg">1.4</nrg3:embodiedCarbon>
				</nrg3:SolidMaterial>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:SolidMaterial gml:id="id_solid_material_15">
					<gml:description>This is SolidMaterial 15</gml:description>
					<gml:name>SolidMaterial 15</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">solid_material_code_15</nrg3:libraryCode>
					<nrg3:thermalConductivity uom="W/(K*m)">0.23</nrg3:thermalConductivity>
					<nrg3:density uom="kg/m^3">1100</nrg3:density>
					<nrg3:specificHeatCapacity uom="J/(kg*K)">0.9</nrg3:specificHeatCapacity>
					<nrg3:permeance uom="xxx">0.9</nrg3:permeance>
					<nrg3:porosity uom="ratio">0.05</nrg3:porosity>
					<nrg3:embodiedEnergy uom="kWh/kg">19.2</nrg3:embodiedEnergy>
					<nrg3:embodiedCarbon uom="kgCO2/kg">9.8</nrg3:embodiedCarbon>
				</nrg3:SolidMaterial>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:SolidMaterial gml:id="id_solid_material_16">
					<gml:description>This is SolidMaterial 16</gml:description>
					<gml:name>SolidMaterial 16</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">solid_material_code_16</nrg3:libraryCode>
					<nrg3:thermalConductivity uom="W/(K*m)">0.7</nrg3:thermalConductivity>
					<nrg3:density uom="kg/m^3">1400</nrg3:density>
					<nrg3:specificHeatCapacity uom="J/(kg*K)">0.9</nrg3:specificHeatCapacity>
					<nrg3:permeance uom="xxx">0.9</nrg3:permeance>
					<nrg3:porosity uom="ratio">0.05</nrg3:porosity>
					<nrg3:embodiedEnergy uom="kWh/kg">14.1</nrg3:embodiedEnergy>
					<nrg3:embodiedCarbon uom="kgCO2/kg">3.9</nrg3:embodiedCarbon>
				</nrg3:SolidMaterial>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:SolidMaterial gml:id="id_solid_material_17">
					<gml:description>This is SolidMaterial 17</gml:description>
					<gml:name>SolidMaterial 17</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">solid_material_code_17</nrg3:libraryCode>
					<nrg3:thermalConductivity uom="W/(K*m)">0.8</nrg3:thermalConductivity>
					<nrg3:density uom="kg/m^3">1800</nrg3:density>
					<nrg3:specificHeatCapacity uom="J/(kg*K)">0.9</nrg3:specificHeatCapacity>
					<nrg3:permeance uom="xxx">0.9</nrg3:permeance>
					<nrg3:porosity uom="ratio">0.05</nrg3:porosity>
					<nrg3:embodiedEnergy uom="kWh/kg">1.1</nrg3:embodiedEnergy>
					<nrg3:embodiedCarbon uom="kgCO2/kg">5.2</nrg3:embodiedCarbon>
				</nrg3:SolidMaterial>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:SolidMaterial gml:id="id_solid_material_18">
					<gml:description>This is SolidMaterial 18</gml:description>
					<gml:name>SolidMaterial 18</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">solid_material_code_18</nrg3:libraryCode>
					<nrg3:thermalConductivity uom="W/(K*m)">0.7</nrg3:thermalConductivity>
					<nrg3:density uom="kg/m^3">1400</nrg3:density>
					<nrg3:specificHeatCapacity uom="J/(kg*K)">0.9</nrg3:specificHeatCapacity>
					<nrg3:permeance uom="xxx">0.9</nrg3:permeance>
					<nrg3:porosity uom="ratio">0.05</nrg3:porosity>
					<nrg3:embodiedEnergy uom="kWh/kg">9.4</nrg3:embodiedEnergy>
					<nrg3:embodiedCarbon uom="kgCO2/kg">0.5</nrg3:embodiedCarbon>
				</nrg3:SolidMaterial>
			</nrg3:libraryMember>
		</nrg3:MaterialLibrary>
	</core:cityObjectMember>
	<core:cityObjectMember>
		<nrg3:ScheduleLibrary gml:id="id_schedule_library_1">
			<gml:description>This is Schedule Library 1</gml:description>
			<gml:name>Schedule Library 1</gml:name>
			<nrg3:type codeSpace="schedule_library_type_codeSpace">schedule_library_type</nrg3:type>
			<nrg3:source>Coruscant Schedule Library</nrg3:source>
			<nrg3:author>Giorgio Agugiaro</nrg3:author>
			<nrg3:libraryMember>
				<nrg3:AtomicSchedule gml:id="id_atomic_schedule_1">
					<gml:description>This is AtomicSchedule 1 for a year, connected to a timeseries of 1 yearly value</gml:description>
					<gml:name>AtomicSchedule 1</gml:name>
					<nrg3:libraryCode codeSpace="schedule_library_codeSpace">atom_sched_code_1</nrg3:libraryCode>
					<nrg3:type codeSpace="schedule_type_codeSpace">year</nrg3:type>
					<nrg3:startTime>00:00:00</nrg3:startTime>
					<nrg3:startDay>1</nrg3:startDay>
					<nrg3:startMonth>1</nrg3:startMonth>
					<nrg3:temporalExtent unit="year">1</nrg3:temporalExtent>
					<nrg3:timeSeries>
						<nrg3:TypicalValuesTimeSeries gml:id="id_default_values_time_series_2">
							<gml:description>This is DefaultValuesTimeSeries 2</gml:description>
							<gml:name>DefaultValuesTimeSeries 2</gml:name>
							<nrg3:acquisitionMethod codeSpace="codespace_18">calibratedSimulation</nrg3:acquisitionMethod>
							<nrg3:interpolationType>discontinuous</nrg3:interpolationType>
							<nrg3:source>source_18</nrg3:source>
							<nrg3:temporalExtent unit="year">1</nrg3:temporalExtent>
							<nrg3:timeInterval unit="year">1</nrg3:timeInterval>
							<nrg3:valuesList uom="unit">100</nrg3:valuesList>
						</nrg3:TypicalValuesTimeSeries>
					</nrg3:timeSeries>
				</nrg3:AtomicSchedule>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:AtomicSchedule gml:id="id_atomic_schedule_2">
					<gml:description>This is AtomicSchedule 2 for a year, connected to a timeseries of 12 monthly values</gml:description>
					<gml:name>AtomicSchedule 2</gml:name>
					<nrg3:libraryCode codeSpace="schedule_library_codeSpace">atom_sched_code_2</nrg3:libraryCode>
					<nrg3:type codeSpace="schedule_type_codeSpace">year</nrg3:type>
					<nrg3:startTime>00:00:00</nrg3:startTime>
					<nrg3:startDay>1</nrg3:startDay>
					<nrg3:startMonth>1</nrg3:startMonth>
					<nrg3:temporalExtent unit="year">1</nrg3:temporalExtent>
					<nrg3:timeSeries>
						<nrg3:TypicalValuesTimeSeries gml:id="id_default_values_time_series_3">
							<gml:description>This is DefaultValuesTimeSeries 3</gml:description>
							<gml:name>DefaultValuesTimeSeries 3</gml:name>
							<nrg3:acquisitionMethod codeSpace="codespace_19">estimation</nrg3:acquisitionMethod>
							<nrg3:interpolationType>instantaneousTotal</nrg3:interpolationType>
							<nrg3:source>source_19</nrg3:source>
							<nrg3:temporalExtent unit="year">1</nrg3:temporalExtent>
							<nrg3:timeInterval unit="year">0.083</nrg3:timeInterval>
							<nrg3:valuesList uom="unit">101 102 103 104 105 106 107 108 109 110 111 112</nrg3:valuesList>
						</nrg3:TypicalValuesTimeSeries>
					</nrg3:timeSeries>
				</nrg3:AtomicSchedule>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:AtomicSchedule gml:id="id_atomic_schedule_6">
					<gml:description>This is AtomicSchedule 6</gml:description>
					<gml:name>AtomicSchedule 6</gml:name>
					<nrg3:libraryCode codeSpace="schedule_library_codeSpace">atom_sched_code_6</nrg3:libraryCode>
					<nrg3:type codeSpace="schedule_type_codeSpace">weekDay</nrg3:type>
					<nrg3:startTime>00:00:00</nrg3:startTime>
					<nrg3:temporalExtent unit="day">1</nrg3:temporalExtent>
					<nrg3:timeSeries>
						<nrg3:TypicalValuesTimeSeries gml:id="id_default_values_time_series_7">
							<gml:description>This is DefaultValuesTimeSeries 7</gml:description>
							<gml:name>DefaultValuesTimeSeries 7</gml:name>
							<nrg3:acquisitionMethod codeSpace="codespace_23">estimation</nrg3:acquisitionMethod>
							<nrg3:interpolationType>instantaneousTotal</nrg3:interpolationType>
							<nrg3:source>source_23</nrg3:source>
							<nrg3:temporalExtent unit="day">1</nrg3:temporalExtent>
							<nrg3:timeInterval unit="hour">1</nrg3:timeInterval>
							<nrg3:valuesList uom="unit">1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24</nrg3:valuesList>
						</nrg3:TypicalValuesTimeSeries>
					</nrg3:timeSeries>
				</nrg3:AtomicSchedule>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:AtomicSchedule gml:id="id_atomic_schedule_7">
					<gml:description>This is AtomicSchedule 7</gml:description>
					<gml:name>AtomicSchedule 7</gml:name>
					<nrg3:libraryCode codeSpace="schedule_library_codeSpace">atom_sched_code_7</nrg3:libraryCode>
					<nrg3:type codeSpace="schedule_type_codeSpace">weekendDay</nrg3:type>
					<nrg3:startTime>00:00:00</nrg3:startTime>
					<nrg3:temporalExtent unit="day">1</nrg3:temporalExtent>
					<nrg3:timeSeries>
						<nrg3:TypicalValuesTimeSeries gml:id="id_default_values_time_series_8">
							<gml:description>This is DefaultValuesTimeSeries 8</gml:description>
							<gml:name>DefaultValuesTimeSeries 8</gml:name>
							<nrg3:acquisitionMethod codeSpace="codespace_24">unknown</nrg3:acquisitionMethod>
							<nrg3:interpolationType>maximumInPrecedingInterval</nrg3:interpolationType>
							<nrg3:source>source_24</nrg3:source>
							<nrg3:temporalExtent unit="day">1</nrg3:temporalExtent>
							<nrg3:timeInterval unit="hour">1</nrg3:timeInterval>
							<nrg3:valuesList uom="unit">11 12 13 14 15 16 17 18 19 110 111 112 113 114 115 116 117 118 119 120 121 122 123 124</nrg3:valuesList>
						</nrg3:TypicalValuesTimeSeries>
					</nrg3:timeSeries>
				</nrg3:AtomicSchedule>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:CompositeSchedule gml:id="id_composite_schedule_1">
					<gml:description>This is CompositeSchedule 1, for 1 typical week, composed of 5 typical days and 2 weekend days</gml:description>
					<gml:name>CompositeSchedule 1</gml:name>
					<nrg3:libraryCode codeSpace="schedule_library_codeSpace">comp_sched_code_1</nrg3:libraryCode>
					<nrg3:type codeSpace="schedule_type_codeSpace">week</nrg3:type>
					<nrg3:startTime>00:00:00</nrg3:startTime>
					<nrg3:temporalExtent unit="day">7</nrg3:temporalExtent>
					<nrg3:scheduleComponent>
						<nrg3:ScheduleComponent gml:id="id_schedule_component_1">
							<gml:description>This is ScheduleComponent 1</gml:description>
							<gml:name>ScheduleComponent 1 containing a repetition of 5 times a daily schedule of timeseries of 24 hourly values for a week day</gml:name>
							<nrg3:type codeSpace="schedule_type_codeSpace">weekDay</nrg3:type>
							<nrg3:repetitions>5</nrg3:repetitions>
							<nrg3:additionalGap unit="day">0</nrg3:additionalGap>
							<nrg3:scheduleComponentMember xlink:href="#id_atomic_schedule_6"/>
						</nrg3:ScheduleComponent>
					</nrg3:scheduleComponent>
					<nrg3:scheduleComponent>
						<nrg3:ScheduleComponent gml:id="id_schedule_component_2">
							<gml:description>This is ScheduleComponent 2</gml:description>
							<gml:name>ScheduleComponent 2 containing a repetition of 2 times a daily schedule of timeseries of 24 hourly values for a weekend day</gml:name>
							<nrg3:type codeSpace="schedule_type_codeSpace">weekendDay</nrg3:type>
							<nrg3:repetitions>2</nrg3:repetitions>
							<nrg3:additionalGap unit="day">0</nrg3:additionalGap>
							<nrg3:scheduleComponentMember xlink:href="#id_atomic_schedule_7"/>
						</nrg3:ScheduleComponent>
					</nrg3:scheduleComponent>
				</nrg3:CompositeSchedule>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:DualValueSchedule gml:id="id_dual_value_schedule_1">
					<gml:description>This is DualValueSchedule 1 for a Monday</gml:description>
					<gml:name>DualValueSchedule 1</gml:name>
					<nrg3:libraryCode codeSpace="schedule_library_codeSpace">dual_value_sched_code_1</nrg3:libraryCode>
					<nrg3:type codeSpace="schedule_type_codeSpace">monday</nrg3:type>
					<nrg3:startTime>00:00:00</nrg3:startTime>
					<nrg3:temporalExtent unit="day">1</nrg3:temporalExtent>
					<nrg3:idleValue uom="degrees Celsius">12</nrg3:idleValue>
					<nrg3:usageValue uom="degrees Celsius">19</nrg3:usageValue>
					<nrg3:startUsageTime>07:00:00</nrg3:startUsageTime>
					<nrg3:endUsageTime>21:00:00</nrg3:endUsageTime>
				</nrg3:DualValueSchedule>
			</nrg3:libraryMember>
		</nrg3:ScheduleLibrary>
	</core:cityObjectMember>
	<core:cityObjectMember>
		<bldg:Building gml:id="house_lod3_1">
			<gml:description>The report house at LoD3: walls, roof and floor, with three real windows.</gml:description>
			<gml:name>Report house - LoD3</gml:name>
			<core:creationDate>2024-09-25</core:creationDate>
			<nrg3:referencePoint>
				<gml:Point srsName="EPSG:32633" srsDimension="3">
					<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
				</gml:Point>
			</nrg3:referencePoint>
			<bldg:class codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_class.xml">habitation</bldg:class>
			<bldg:function codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_function.xml">residential building</bldg:function>
			<bldg:yearOfConstruction>1955</bldg:yearOfConstruction>
			<bldg:roofType codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_roofType.xml">gabled roof</bldg:roofType>
			<bldg:measuredHeight uom="m">9</bldg:measuredHeight>
			<bldg:storeysAboveGround>2</bldg:storeysAboveGround>
			<bldg:storeysBelowGround>0</bldg:storeysBelowGround>
			<bldg:storeyHeightsAboveGround uom="m">3</bldg:storeyHeightsAboveGround>
			<bldg:lod0FootPrint>
				<gml:MultiSurface gml:id="id_building_1_footprint_MultiSurf" srsName="EPSG:32633" srsDimension="3">
					<gml:surfaceMember>
						<gml:OrientableSurface orientation="-">
							<gml:baseSurface xlink:href="#id_building_1_polygon_3"/>
						</gml:OrientableSurface>
					</gml:surfaceMember>
				</gml:MultiSurface>
			</bldg:lod0FootPrint>
			<bldg:lod1Solid>
				<gml:Solid gml:id="id_building_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
					<gml:exterior>
						<gml:CompositeSurface gml:id="id_building_1_lod1_CompSurf">
							<gml:surfaceMember>
								<gml:Polygon gml:id="id_building_1_lod1_Polygon_1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291300.0000 5041900.0000 0.0000 291300.0000 5041910.0000 0.0000 291310.0000 5041910.0000 0.0000 291310.0000 5041900.0000 0.0000 291300.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="id_building_1_lod1_Polygon_2">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291300.0000 5041900.0000 0.0000 291310.0000 5041900.0000 0.0000 291310.0000 5041900.0000 7.5000 291300.0000 5041900.0000 7.5000 291300.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="id_building_1_lod1_Polygon_3">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291310.0000 5041900.0000 0.0000 291310.0000 5041910.0000 0.0000 291310.0000 5041910.0000 7.5000 291310.0000 5041900.0000 7.5000 291310.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="id_building_1_lod1_Polygon_4">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291310.0000 5041910.0000 0.0000 291300.0000 5041910.0000 0.0000 291300.0000 5041910.0000 7.5000 291310.0000 5041910.0000 7.5000 291310.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="id_building_1_lod1_Polygon_5">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291300.0000 5041910.0000 0.0000 291300.0000 5041900.0000 0.0000 291300.0000 5041900.0000 7.5000 291300.0000 5041910.0000 7.5000 291300.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="id_building_1_lod1_Polygon_6">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291300.0000 5041900.0000 7.5000 291310.0000 5041900.0000 7.5000 291310.0000 5041910.0000 7.5000 291300.0000 5041910.0000 7.5000 291300.0000 5041900.0000 7.5000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:CompositeSurface>
					</gml:exterior>
				</gml:Solid>
			</bldg:lod1Solid>
			<bldg:lod2Solid>
				<gml:Solid gml:id="id_building_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
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
										<gml:LinearRing>
											<gml:posList>291310.0000 5041910.0000 6.0000 291310.0000 5041900.0000 6.0000 291310.0000 5041900.0000 0.0000 291310.0000 5041910.0000 0.0000 291310.0000 5041910.0000 6.0000</gml:posList>
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
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_ground_1"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="id_building_1_groundsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="id_building_1_polygon_3">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291300.0000 5041900.0000 0.0000 291300.0000 5041910.0000 0.0000 291310.0000 5041910.0000 0.0000 291310.0000 5041900.0000 0.0000 291300.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">-1</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">1</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">180</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">100</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:GroundSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:RoofSurface gml:id="id_building_1_roofsurface_1">
					<gml:description>This is RoofSurface 1 (Building 1)</gml:description>
					<gml:name>RoofSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="id_building_1_roofsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="id_building_1_polygon_1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291300.0000 5041900.0000 6.0000 291305.0000 5041900.0000 9.0000 291305.0000 5041910.0000 9.0000 291300.0000 5041910.0000 6.0000 291300.0000 5041900.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">270</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfHeatCapacity uom="kJ/(m^2*K)">1.26</nrg3:bdgBdrySurfHeatCapacity>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">30.9638</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfOpaqueSurfaceArea>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfThickness uom="mm">250</nrg3:bdgBdrySurfThickness>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:RoofSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:RoofSurface gml:id="id_building_1_roofsurface_2">
					<gml:description>This is RoofSurface 2 (Building 1)</gml:description>
					<gml:name>RoofSurface 2 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="id_building_1_roofsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="id_building_1_polygon_2">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291305.0000 5041900.0000 9.0000 291310.0000 5041900.0000 6.0000 291310.0000 5041910.0000 6.0000 291305.0000 5041910.0000 9.0000 291305.0000 5041900.0000 9.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">30.9638</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:RoofSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface gml:id="id_building_1_wallsurface_1">
					<gml:description>This is WallSurface 1 (Building 1)</gml:description>
					<gml:name>WallSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="id_building_1_wallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="id_building_1_polygon_5">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291300.0000 5041900.0000 0.0000 291310.0000 5041900.0000 0.0000 291310.0000 5041900.0000 6.0000 291305.0000 5041900.0000 9.0000 291300.0000 5041900.0000 6.0000 291300.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">180</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.2162</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">75</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface gml:id="id_building_1_wallsurface_2">
					<gml:description>This is WallSurface 2 (Building 1)</gml:description>
					<gml:name>WallSurface 2 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="id_building_1_wallsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="id_building_1_polygon_4">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291300.0000 5041910.0000 0.0000 291300.0000 5041910.0000 6.0000 291305.0000 5041910.0000 9.0000 291310.0000 5041910.0000 6.0000 291310.0000 5041910.0000 0.0000 291300.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">0</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.2162</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">75</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface gml:id="id_building_1_wallsurface_3">
					<gml:description>This is WallSurface 3 (Building 1)</gml:description>
					<gml:name>WallSurface 3 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="id_building_1_wallsurface_3_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="id_building_1_polygon_7">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291300.0000 5041900.0000 0.0000 291300.0000 5041900.0000 6.0000 291300.0000 5041910.0000 6.0000 291300.0000 5041910.0000 0.0000 291300.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">270</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.16</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<nrg3:PartyWallSurface gml:id="id_building_1_partywallsurface_1">
					<gml:description>This is WallSurface 8 (shared)</gml:description>
					<gml:name>WallSurface 8 (shared)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="id_building_1_partywallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="id_building_1_polygon_cs1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291310.0000 5041910.0000 6.0000 291310.0000 5041900.0000 6.0000 291310.0000 5041900.0000 0.0000 291310.0000 5041910.0000 0.0000 291310.0000 5041910.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
				</nrg3:PartyWallSurface>
			</bldg:boundedBy>
			<bldg:address>
				<core:Address gml:id="id_address_1">
					<core:xalAddress>
						<xAL:AddressDetails>
							<xAL:Country>
								<xAL:CountryNameCode>ALD</xAL:CountryNameCode>
								<xAL:CountryName>Bespin Territories</xAL:CountryName>
								<xAL:Locality Type="Town">
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
					</core:xalAddress>
					<core:multiPoint>
						<gml:MultiPoint srsName="EPSG:32633" srsDimension="3">
							<gml:pointMember>
								<gml:Point>
									<gml:pos>291305.0000 5041905.0000 0.0000</gml:pos>
								</gml:Point>
							</gml:pointMember>
						</gml:MultiPoint>
					</core:multiPoint>
				</core:Address>
			</bldg:address>
			<nrg3:bdgArea>
				<nrg3:QualifiedArea>
					<nrg3:description>This is a type of floor area</nrg3:description>
					<nrg3:source>Area value source text</nrg3:source>
					<nrg3:value uom="m^2">200</nrg3:value>
					<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
				</nrg3:QualifiedArea>
			</nrg3:bdgArea>
			<nrg3:bdgArea>
				<nrg3:QualifiedArea>
					<nrg3:description>This is a type of floor area</nrg3:description>
					<nrg3:source>Area value source text</nrg3:source>
					<nrg3:value uom="m^2">100</nrg3:value>
					<nrg3:type codeSpace="area_codeSpace">footprintArea</nrg3:type>
				</nrg3:QualifiedArea>
			</nrg3:bdgArea>
			<nrg3:bdgAtticThermalStatus>isOnlyCooled</nrg3:bdgAtticThermalStatus>
			<nrg3:bdgBasementThermalStatus>isOnlyHeated</nrg3:bdgBasementThermalStatus>
			<nrg3:bdgConstructionWeight codeSpace="constrWeight_codeSpace">heavy</nrg3:bdgConstructionWeight>
			<nrg3:bdgHeight>
				<nrg3:QualifiedHeight>
					<nrg3:description>This is a type of height</nrg3:description>
					<nrg3:source>Height value source text</nrg3:source>
					<nrg3:value uom="m">9</nrg3:value>
					<nrg3:type codeSpace="height_codeSpace">highestRoofEdge</nrg3:type>
				</nrg3:QualifiedHeight>
			</nrg3:bdgHeight>
			<nrg3:bdgHeight>
				<nrg3:QualifiedHeight>
					<nrg3:description>This is a type of height</nrg3:description>
					<nrg3:source>Height value source text</nrg3:source>
					<nrg3:value uom="m">0</nrg3:value>
					<nrg3:type codeSpace="height_codeSpace">bottomOfConstruction</nrg3:type>
				</nrg3:QualifiedHeight>
			</nrg3:bdgHeight>
			<nrg3:bdgIsProtected>false</nrg3:bdgIsProtected>
			<nrg3:bdgType codeSpace="bdgType_codeSpace">terracedHouse</nrg3:bdgType>
			<nrg3:bdgVolume>
				<nrg3:QualifiedVolume>
					<nrg3:description>This is a type of volume</nrg3:description>
					<nrg3:source>Volume value source text</nrg3:source>
					<nrg3:value uom="m^3">750</nrg3:value>
					<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
				</nrg3:QualifiedVolume>
			</nrg3:bdgVolume>
			<nrg3:bdgVolume>
				<nrg3:QualifiedVolume>
					<nrg3:description>This is a type of volume</nrg3:description>
					<nrg3:source>Volume value source text</nrg3:source>
					<nrg3:value uom="m^3">486</nrg3:value>
					<nrg3:type codeSpace="volume_codeSpace">netVolume</nrg3:type>
				</nrg3:QualifiedVolume>
			</nrg3:bdgVolume>
			<nrg3:buildingUnit>
				<nrg3:BuildingUnit gml:id="id_building_unit_1">
					<gml:description>This is BuildingUnit 1</gml:description>
					<gml:name>BuildingUnit 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source</nrg3:source>
							<nrg3:value uom="m^2">200</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source</nrg3:source>
							<nrg3:value uom="m^2">100</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">energyReferenceArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source</nrg3:source>
							<nrg3:value uom="m^3">750</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source</nrg3:source>
							<nrg3:value uom="m^3">875</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">energyReferenceVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:lod1Solid>
						<gml:Solid gml:id="id_building_unit_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="id_building_unit_1_lod1_CompSurf">
									<gml:surfaceMember xlink:href="#Polygon_UUID_42e7489a-e3f6-4a45-be2a-fbe735cd2ef8"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_3f00920e-17c2-41f1-acb7-e223b1199044"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_ba78c9d7-0ed7-49b8-b107-d939f0186284"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_1406dd4c-f070-4022-835b-50018fdc6c54"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_694c7871-d386-4e68-9c88-f62140080992"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_945a1c0f-31f2-4bad-9599-9aaecf0ac7ac"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="id_building_unit_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="id_building_unit_1_lod2_CompSurf">
									<gml:surfaceMember xlink:href="#Polygon_UUID_6e3e783e-b75a-4436-9f49-ed7d5346bca0"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_ed5e64ff-65d6-4da8-bd65-a726d53494fa"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_b7a25cfb-c3c6-490c-8628-42c50627d42c"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_204ef154-fa62-4200-b3f2-4bb427b7b42e"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_1f26fb83-a013-4528-9b75-b7eed4d07b70"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_0f7e6a7d-4c78-4f23-a531-482e254f1aae"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_8c107b31-166a-4b7c-aec1-4800b9dd396c"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:lod3Solid>
						<gml:Solid gml:id="id_building_unit_1_lod3_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="id_building_unit_1_lod3_CompSurf">
									<gml:surfaceMember xlink:href="#Polygon_UUID_b9c018da-8461-4762-99c2-1cae1fc6dfa2"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_efca560a-2e79-4536-9e21-4e23aacef253"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_80ecaada-e49a-4e7d-8955-367405f503fb"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_4dbfd338-5c11-42cd-b60d-68038c5dc78f"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_5103fb6c-6d3f-4756-aa3a-586039a1938f"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_2d5f403b-eac9-46ff-abbe-579c1416747a"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_934e4b6a-022d-4cf7-8426-883da175edd4"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod3Solid>
					<nrg3:type codeSpace="buildingUnit_codeSpace_123">residential</nrg3:type>
					<nrg3:numberOfRooms>4</nrg3:numberOfRooms>
					<nrg3:ownershipType codeSpace="ownership_type_codeSpace_abc">corporation</nrg3:ownershipType>
					<nrg3:address xlink:href="#id_address_1"/>
				</nrg3:BuildingUnit>
			</nrg3:buildingUnit>
			<nrg3:thermalZone>
				<nrg3:ThermalZone gml:id="id_thermal_zone_1">
					<gml:description>This is ThermalZone 1</gml:description>
					<gml:name>ThermalZone 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">200</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">100</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">footprintArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">180</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">energyReferenceArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">750</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">486</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">netVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:lod1Solid>
						<gml:Solid gml:id="id_thermal_zone_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="id_thermal_zone_1_lod1_CompSurf">
									<gml:surfaceMember xlink:href="#id_building_1_lod1_Polygon_1"/>
									<gml:surfaceMember xlink:href="#id_building_1_lod1_Polygon_2"/>
									<gml:surfaceMember xlink:href="#id_building_1_lod1_Polygon_3"/>
									<gml:surfaceMember xlink:href="#id_building_1_lod1_Polygon_4"/>
									<gml:surfaceMember xlink:href="#id_building_1_lod1_Polygon_5"/>
									<gml:surfaceMember xlink:href="#id_building_1_lod1_Polygon_6"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="id_thermal_zone_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="id_thermal_zone_1_lod2_CompSurf">
									<gml:surfaceMember xlink:href="#id_building_1_polygon_4"/>
									<gml:surfaceMember xlink:href="#id_building_1_polygon_5"/>
									<gml:surfaceMember xlink:href="#id_building_1_polygon_7"/>
									<gml:surfaceMember xlink:href="#id_building_1_polygon_1"/>
									<gml:surfaceMember xlink:href="#id_building_1_polygon_2"/>
									<gml:surfaceMember xlink:href="#id_building_1_polygon_3"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_741a8f18-1100-467f-9c40-a919c34d2065"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:lod3Solid>
						<gml:Solid gml:id="id_thermal_zone_1_lod3_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="id_thermal_zone_1_lod3_CompSurf">
									<gml:surfaceMember xlink:href="#Polygon_UUID_5931fe6f-0875-464c-a020-17addd8f9fe5"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_4a5ef73e-04b2-4e8e-81f5-1ddb2838823e"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_9454055e-f9f2-46c6-8c3d-f1de8e5b54ce"/>
									<gml:surfaceMember xlink:href="#Polygon_UUID_e8e3d62c-1bb4-48d2-8415-346cb2dff634"/>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_da00ca7d-c958-4d8a-87c6-a6a016ff5478">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041900.0000 0.0000 291310.0000 5041900.0000 0.0000 291310.0000 5041900.0000 6.0000 291305.0000 5041900.0000 9.0000 291300.0000 5041900.0000 6.0000 291300.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_56f104ce-3b55-46ff-9ea3-463b83ecea23">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041910.0000 0.0000 291300.0000 5041910.0000 6.0000 291305.0000 5041910.0000 9.0000 291310.0000 5041910.0000 6.0000 291310.0000 5041910.0000 0.0000 291300.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_ef9093c6-d213-448d-ba14-c41ff8143a6d">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041900.0000 0.0000 291300.0000 5041900.0000 6.0000 291300.0000 5041910.0000 6.0000 291300.0000 5041910.0000 0.0000 291300.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod3Solid>
					<nrg3:heatCapacity uom="J/K">500</nrg3:heatCapacity>
					<nrg3:infiltrationRate uom="1/h">0.3</nrg3:infiltrationRate>
					<nrg3:isCooled>false</nrg3:isCooled>
					<nrg3:isHeated>true</nrg3:isHeated>
					<nrg3:coincidesWithLod2Hull>false</nrg3:coincidesWithLod2Hull>
					<nrg3:coincidesWithLod3Hull>false</nrg3:coincidesWithLod3Hull>
					<nrg3:thermalBoundary>
						<bldg:GroundSurface gml:id="id_thermal_zone_1_groundsurface_1">
							<gml:description>This is (ThermalBoundary) GroundSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) GroundSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_ground_1"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="id_thermal_zone_1_groundsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#id_building_1_polygon_3"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<bldg:lod3MultiSurface>
								<gml:MultiSurface gml:id="id_thermal_zone_1_groundsurface_1_lod3_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_4a5ef73e-04b2-4e8e-81f5-1ddb2838823e">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041900.0000 0.0000 291300.0000 5041910.0000 0.0000 291310.0000 5041910.0000 0.0000 291310.0000 5041900.0000 0.0000 291300.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:MultiSurface>
							</bldg:lod3MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">-1</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">1</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">180</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">100</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:GroundSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:RoofSurface gml:id="id_thermal_zone_1_roofsurface_1">
							<gml:description>This is (ThermalBoundary) RoofSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) RoofSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="id_thermal_zone_1_roofsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#id_building_1_polygon_1"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<bldg:lod3MultiSurface>
								<gml:MultiSurface gml:id="id_thermal_zone_1_roofsurface_1_lod3_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_9454055e-f9f2-46c6-8c3d-f1de8e5b54ce">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041900.0000 6.0000 291305.0000 5041900.0000 9.0000 291305.0000 5041910.0000 9.0000 291300.0000 5041910.0000 6.0000 291300.0000 5041900.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:MultiSurface>
							</bldg:lod3MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">270</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">30.9638</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:RoofSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:RoofSurface gml:id="id_thermal_zone_1_roofsurface_2">
							<gml:description>This is (ThermalBoundary) RoofSurface 2 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) RoofSurface 2 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="id_thermal_zone_1_roofsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#id_building_1_polygon_2"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<bldg:lod3MultiSurface>
								<gml:MultiSurface gml:id="id_thermal_zone_1_roofsurface_2_lod3_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_e8e3d62c-1bb4-48d2-8415-346cb2dff634">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291305.0000 5041900.0000 9.0000 291310.0000 5041900.0000 6.0000 291310.0000 5041910.0000 6.0000 291305.0000 5041910.0000 9.0000 291305.0000 5041900.0000 9.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:MultiSurface>
							</bldg:lod3MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">30.9638</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:RoofSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:WallSurface gml:id="id_thermal_zone_1_wallsurface_1">
							<gml:description>This is (ThermalBoundary) WallSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="id_thermal_zone_1_wallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#id_building_1_polygon_5"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<bldg:lod3MultiSurface>
								<gml:MultiSurface gml:id="id_thermal_zone_1_wallsurface_1_lod3_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_2240fbcc-7699-48dd-93b4-1668ac44224f">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041900.0000 0.0000 291310.0000 5041900.0000 0.0000 291310.0000 5041900.0000 6.0000 291305.0000 5041900.0000 9.0000 291300.0000 5041900.0000 6.0000 291300.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
											<gml:interior>
												<gml:LinearRing>
													<gml:posList>291303.0000 5041900.0000 1.8000 291303.0000 5041900.0000 5.2542 291305.0000 5041900.0000 6.4542 291307.0000 5041900.0000 5.2542 291307.0000 5041900.0000 1.8000 291303.0000 5041900.0000 1.8000</gml:posList>
												</gml:LinearRing>
											</gml:interior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:MultiSurface>
							</bldg:lod3MultiSurface>
							<bldg:opening>
								<bldg:Window gml:id="id_thermal_zone_1_wallsurface_1_thermal_opening_1">
									<gml:description>This is Thermal Opening 1</gml:description>
									<gml:name>Thermal Opening 1</gml:name>
									<nrg3:layeredConstruction xlink:href="#id_layered_construction_glazing_5"/>
									<nrg3:referencePoint>
										<gml:Point srsName="EPSG:32633" srsDimension="3">
											<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
										</gml:Point>
									</nrg3:referencePoint>
									<bldg:lod3MultiSurface>
										<gml:MultiSurface gml:id="id_thermal_zone_1_wallsurface_1_thermal_opening_1_lod3_geom" srsName="EPSG:32633" srsDimension="3">
											<gml:surfaceMember>
												<gml:Polygon gml:id="Polygon_UUID_536d7500-8d81-490c-885e-78951e4a26d5">
													<gml:exterior>
														<gml:LinearRing>
															<gml:posList>291303.0000 5041900.0000 1.8000 291307.0000 5041900.0000 1.8000 291307.0000 5041900.0000 5.2542 291305.0000 5041900.0000 6.4542 291303.0000 5041900.0000 5.2542 291303.0000 5041900.0000 1.8000</gml:posList>
														</gml:LinearRing>
													</gml:exterior>
												</gml:Polygon>
											</gml:surfaceMember>
										</gml:MultiSurface>
									</bldg:lod3MultiSurface>
									<nrg3:bdgOpnArea uom="m^2">16.2176</nrg3:bdgOpnArea>
									<nrg3:bdgOpnAzimuth uom="decimal degree">180</nrg3:bdgOpnAzimuth>
									<nrg3:bdgOpnGroundViewFactor uom="unit interval">0.5</nrg3:bdgOpnGroundViewFactor>
									<nrg3:bdgOpnInclination uom="decimal degree">90</nrg3:bdgOpnInclination>
									<nrg3:bdgOpnSkyViewFactor uom="unit interval">0.6</nrg3:bdgOpnSkyViewFactor>
								</bldg:Window>
							</bldg:opening>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">180</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">58.7824</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.2162</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">75</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:WallSurface gml:id="id_thermal_zone_1_wallsurface_2">
							<gml:description>This is (ThermalBoundary) WallSurface 2 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 2 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="id_thermal_zone_1_wallsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#id_building_1_polygon_4"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<bldg:lod3MultiSurface>
								<gml:MultiSurface gml:id="id_thermal_zone_1_wallsurface_2_lod3_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_1a85715e-a92d-405b-adf8-1e402415cc90">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041910.0000 0.0000 291300.0000 5041910.0000 6.0000 291305.0000 5041910.0000 9.0000 291310.0000 5041910.0000 6.0000 291310.0000 5041910.0000 0.0000 291300.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
											<gml:interior>
												<gml:LinearRing>
													<gml:posList>291303.0000 5041910.0000 1.8000 291307.0000 5041910.0000 1.8000 291307.0000 5041910.0000 5.2542 291305.0000 5041910.0000 6.4542 291303.0000 5041910.0000 5.2542 291303.0000 5041910.0000 1.8000</gml:posList>
												</gml:LinearRing>
											</gml:interior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:MultiSurface>
							</bldg:lod3MultiSurface>
							<bldg:opening>
								<bldg:Window gml:id="id_thermal_zone_1_wallsurface_2_thermal_opening_2">
									<gml:description>This is Thermal Opening 2</gml:description>
									<gml:name>Thermal Opening 2</gml:name>
									<nrg3:layeredConstruction xlink:href="#id_layered_construction_glazing_5"/>
									<nrg3:referencePoint>
										<gml:Point srsName="EPSG:32633" srsDimension="3">
											<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
										</gml:Point>
									</nrg3:referencePoint>
									<bldg:lod3MultiSurface>
										<gml:MultiSurface gml:id="id_thermal_zone_1_wallsurface_2_thermal_opening_2_lod3_geom" srsName="EPSG:32633" srsDimension="3">
											<gml:surfaceMember>
												<gml:Polygon gml:id="Polygon_UUID_fe6f9547-d5e5-45d6-8db4-3faaf56296e1">
													<gml:exterior>
														<gml:LinearRing>
															<gml:posList>291303.0000 5041910.0000 1.8000 291303.0000 5041910.0000 5.2542 291305.0000 5041910.0000 6.4542 291307.0000 5041910.0000 5.2542 291307.0000 5041910.0000 1.8000 291303.0000 5041910.0000 1.8000</gml:posList>
														</gml:LinearRing>
													</gml:exterior>
												</gml:Polygon>
											</gml:surfaceMember>
										</gml:MultiSurface>
									</bldg:lod3MultiSurface>
									<nrg3:bdgOpnArea uom="m^2">16.2176</nrg3:bdgOpnArea>
									<nrg3:bdgOpnAzimuth uom="decimal degree">0</nrg3:bdgOpnAzimuth>
									<nrg3:bdgOpnGroundViewFactor uom="unit interval">0.5</nrg3:bdgOpnGroundViewFactor>
									<nrg3:bdgOpnInclination uom="decimal degree">90</nrg3:bdgOpnInclination>
									<nrg3:bdgOpnSkyViewFactor uom="unit interval">0.6</nrg3:bdgOpnSkyViewFactor>
								</bldg:Window>
							</bldg:opening>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">0</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">58.7824</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.2162</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">75</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:WallSurface gml:id="id_thermal_zone_1_wallsurface_3">
							<gml:description>This is (ThermalBoundary) WallSurface 3 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 3 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="id_thermal_zone_1_wallsurface_3_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#id_building_1_polygon_7"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<bldg:lod3MultiSurface>
								<gml:MultiSurface gml:id="id_thermal_zone_1_wallsurface_3_lod3_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_148e7131-25d1-4de1-9092-c89d73a2b927">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041900.0000 0.0000 291300.0000 5041900.0000 6.0000 291300.0000 5041910.0000 6.0000 291300.0000 5041910.0000 0.0000 291300.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
											<gml:interior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041903.0000 1.8000 291300.0000 5041907.0000 1.8000 291300.0000 5041907.0000 4.2000 291300.0000 5041903.0000 4.2000 291300.0000 5041903.0000 1.8000</gml:posList>
												</gml:LinearRing>
											</gml:interior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:MultiSurface>
							</bldg:lod3MultiSurface>
							<bldg:opening>
								<bldg:Window gml:id="id_thermal_zone_1_wallsurface_3_thermal_opening_3">
									<gml:description>This is Thermal Opening 3</gml:description>
									<gml:name>Thermal Opening 3</gml:name>
									<nrg3:layeredConstruction xlink:href="#id_layered_construction_glazing_5"/>
									<nrg3:referencePoint>
										<gml:Point srsName="EPSG:32633" srsDimension="3">
											<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
										</gml:Point>
									</nrg3:referencePoint>
									<bldg:lod3MultiSurface>
										<gml:MultiSurface gml:id="id_thermal_zone_1_wallsurface_3_thermal_opening_3_lod3_geom" srsName="EPSG:32633" srsDimension="3">
											<gml:surfaceMember>
												<gml:Polygon gml:id="Polygon_UUID_0ef2fcc0-3192-4ccf-a218-f3de9fe3c153">
													<gml:exterior>
														<gml:LinearRing>
															<gml:posList>291300.0000 5041903.0000 1.8000 291300.0000 5041903.0000 4.2000 291300.0000 5041907.0000 4.2000 291300.0000 5041907.0000 1.8000 291300.0000 5041903.0000 1.8000</gml:posList>
														</gml:LinearRing>
													</gml:exterior>
												</gml:Polygon>
											</gml:surfaceMember>
										</gml:MultiSurface>
									</bldg:lod3MultiSurface>
									<nrg3:bdgOpnArea uom="m^2">9.6</nrg3:bdgOpnArea>
									<nrg3:bdgOpnAzimuth uom="decimal degree">270</nrg3:bdgOpnAzimuth>
									<nrg3:bdgOpnGroundViewFactor uom="unit interval">0.5</nrg3:bdgOpnGroundViewFactor>
									<nrg3:bdgOpnInclination uom="decimal degree">90</nrg3:bdgOpnInclination>
									<nrg3:bdgOpnSkyViewFactor uom="unit interval">0.6</nrg3:bdgOpnSkyViewFactor>
								</bldg:Window>
							</bldg:opening>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">270</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">50.4</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.16</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<nrg3:PartyWallSurface gml:id="id_thermal_zone_1_partywallsurface_1">
							<gml:description>This is (ThermalBoundary) PartyWallSurface 8</gml:description>
							<gml:name>(ThermalBoundary) PartyWallSurface 8</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="id_thermal_zone_1_partywallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#id_building_1_polygon_cs1"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<bldg:lod3MultiSurface>
								<gml:MultiSurface gml:id="id_thermal_zone_1_partywallsurface_1_lod3_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_5931fe6f-0875-464c-a020-17addd8f9fe5">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291310.0000 5041910.0000 6.0000 291310.0000 5041900.0000 6.0000 291310.0000 5041900.0000 0.0000 291310.0000 5041910.0000 0.0000 291310.0000 5041910.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:MultiSurface>
							</bldg:lod3MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
						</nrg3:PartyWallSurface>
					</nrg3:thermalBoundary>
				</nrg3:ThermalZone>
			</nrg3:thermalZone>
			<nrg3:usageZone>
				<nrg3:UsageZone gml:id="id_usage_zone_1">
					<gml:description>This is UsageZone 1</gml:description>
					<gml:name>UsageZone 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">200</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">100</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">energyReferenceArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">750</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">875</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">energyReferenceVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:lod1Solid>
						<gml:Solid gml:id="id_usage_zone_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="id_usage_zone_1_lod1_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_42e7489a-e3f6-4a45-be2a-fbe735cd2ef8">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041900.0000 0.0000 291300.0000 5041910.0000 0.0000 291310.0000 5041910.0000 0.0000 291310.0000 5041900.0000 0.0000 291300.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_3f00920e-17c2-41f1-acb7-e223b1199044">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041900.0000 0.0000 291310.0000 5041900.0000 0.0000 291310.0000 5041900.0000 7.5000 291300.0000 5041900.0000 7.5000 291300.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_ba78c9d7-0ed7-49b8-b107-d939f0186284">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291310.0000 5041900.0000 0.0000 291310.0000 5041910.0000 0.0000 291310.0000 5041910.0000 7.5000 291310.0000 5041900.0000 7.5000 291310.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_1406dd4c-f070-4022-835b-50018fdc6c54">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291310.0000 5041910.0000 0.0000 291300.0000 5041910.0000 0.0000 291300.0000 5041910.0000 7.5000 291310.0000 5041910.0000 7.5000 291310.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_694c7871-d386-4e68-9c88-f62140080992">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041910.0000 0.0000 291300.0000 5041900.0000 0.0000 291300.0000 5041900.0000 7.5000 291300.0000 5041910.0000 7.5000 291300.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_945a1c0f-31f2-4bad-9599-9aaecf0ac7ac">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041900.0000 7.5000 291310.0000 5041900.0000 7.5000 291310.0000 5041910.0000 7.5000 291300.0000 5041910.0000 7.5000 291300.0000 5041900.0000 7.5000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="id_usage_zone_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="id_usage_zone_1_lod2_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_b9c018da-8461-4762-99c2-1cae1fc6dfa2">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041910.0000 0.0000 291300.0000 5041910.0000 6.0000 291305.0000 5041910.0000 9.0000 291310.0000 5041910.0000 6.0000 291310.0000 5041910.0000 0.0000 291300.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_efca560a-2e79-4536-9e21-4e23aacef253">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041900.0000 0.0000 291310.0000 5041900.0000 0.0000 291310.0000 5041900.0000 6.0000 291305.0000 5041900.0000 9.0000 291300.0000 5041900.0000 6.0000 291300.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_80ecaada-e49a-4e7d-8955-367405f503fb">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041900.0000 0.0000 291300.0000 5041900.0000 6.0000 291300.0000 5041910.0000 6.0000 291300.0000 5041910.0000 0.0000 291300.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_4dbfd338-5c11-42cd-b60d-68038c5dc78f">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041900.0000 6.0000 291305.0000 5041900.0000 9.0000 291305.0000 5041910.0000 9.0000 291300.0000 5041910.0000 6.0000 291300.0000 5041900.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_5103fb6c-6d3f-4756-aa3a-586039a1938f">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291305.0000 5041900.0000 9.0000 291310.0000 5041900.0000 6.0000 291310.0000 5041910.0000 6.0000 291305.0000 5041910.0000 9.0000 291305.0000 5041900.0000 9.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_2d5f403b-eac9-46ff-abbe-579c1416747a">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041900.0000 0.0000 291300.0000 5041910.0000 0.0000 291310.0000 5041910.0000 0.0000 291310.0000 5041900.0000 0.0000 291300.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_934e4b6a-022d-4cf7-8426-883da175edd4">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291310.0000 5041910.0000 6.0000 291310.0000 5041900.0000 6.0000 291310.0000 5041900.0000 0.0000 291310.0000 5041910.0000 0.0000 291310.0000 5041910.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:lod3Solid>
						<gml:Solid gml:id="id_usage_zone_1_lod3_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="id_usage_zone_1_lod3_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_6e3e783e-b75a-4436-9f49-ed7d5346bca0">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041910.0000 0.0000 291300.0000 5041910.0000 6.0000 291305.0000 5041910.0000 9.0000 291310.0000 5041910.0000 6.0000 291310.0000 5041910.0000 0.0000 291300.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_ed5e64ff-65d6-4da8-bd65-a726d53494fa">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041900.0000 0.0000 291310.0000 5041900.0000 0.0000 291310.0000 5041900.0000 6.0000 291305.0000 5041900.0000 9.0000 291300.0000 5041900.0000 6.0000 291300.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_b7a25cfb-c3c6-490c-8628-42c50627d42c">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041900.0000 0.0000 291300.0000 5041900.0000 6.0000 291300.0000 5041910.0000 6.0000 291300.0000 5041910.0000 0.0000 291300.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_204ef154-fa62-4200-b3f2-4bb427b7b42e">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041900.0000 6.0000 291305.0000 5041900.0000 9.0000 291305.0000 5041910.0000 9.0000 291300.0000 5041910.0000 6.0000 291300.0000 5041900.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_1f26fb83-a013-4528-9b75-b7eed4d07b70">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291305.0000 5041900.0000 9.0000 291310.0000 5041900.0000 6.0000 291310.0000 5041910.0000 6.0000 291305.0000 5041910.0000 9.0000 291305.0000 5041900.0000 9.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_0f7e6a7d-4c78-4f23-a531-482e254f1aae">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291300.0000 5041900.0000 0.0000 291300.0000 5041910.0000 0.0000 291310.0000 5041910.0000 0.0000 291310.0000 5041900.0000 0.0000 291300.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="Polygon_UUID_8c107b31-166a-4b7c-aec1-4800b9dd396c">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291310.0000 5041910.0000 6.0000 291310.0000 5041900.0000 6.0000 291310.0000 5041900.0000 0.0000 291310.0000 5041910.0000 0.0000 291310.0000 5041910.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod3Solid>
					<nrg3:type codeSpace="usageZone_codeSpace_123">residential</nrg3:type>
					<nrg3:isPrimary>true</nrg3:isPrimary>
					<nrg3:numberOfBuildingUnits>1</nrg3:numberOfBuildingUnits>
					<nrg3:internalHeatGains uom="W/m^2">100</nrg3:internalHeatGains>
					<nrg3:internalHeatGainsConvectiveFraction uom="unit interval">0.3</nrg3:internalHeatGainsConvectiveFraction>
					<nrg3:internalHeatGainsLatentFraction uom="unit interval">0.2</nrg3:internalHeatGainsLatentFraction>
					<nrg3:internalHeatGainsRadiantFraction uom="unit interval">0.5</nrg3:internalHeatGainsRadiantFraction>
					<nrg3:coolingSchedule xlink:href="#id_atomic_schedule_1"/>
					<nrg3:heatingSchedule xlink:href="#id_dual_value_schedule_1"/>
					<nrg3:ventilationSchedule xlink:href="#id_composite_schedule_1"/>
					<nrg3:occupiedBy>
						<nrg3:Occupants gml:id="id_occupants_1">
							<gml:description>This is Occupants 1</gml:description>
							<gml:name>Occupants 1</gml:name>
							<nrg3:type codeSpace="occ_codeSpace_xyz">residents</nrg3:type>
							<nrg3:numberOfOccupants>12</nrg3:numberOfOccupants>
							<nrg3:heatDissipation uom="W/m^2">100</nrg3:heatDissipation>
							<nrg3:heatDissipationConvectiveFraction uom="unit interval">0.3</nrg3:heatDissipationConvectiveFraction>
							<nrg3:heatDissipationLatentFraction uom="unit interval">0.2</nrg3:heatDissipationLatentFraction>
							<nrg3:heatDissipationRadiantFraction uom="unit interval">0.5</nrg3:heatDissipationRadiantFraction>
							<nrg3:occupancyRate xlink:href="#id_atomic_schedule_2"/>
							<nrg3:averageDietType codeSpace="diet_codeSpace">omnivorous</nrg3:averageDietType>
							<nrg3:averageIncomeLevel codeSpace="income_level codeSpace">middle</nrg3:averageIncomeLevel>
							<nrg3:averageInstructionLevel codeSpace="instruction_level_codeSpace">university</nrg3:averageInstructionLevel>
						</nrg3:Occupants>
					</nrg3:occupiedBy>
				</nrg3:UsageZone>
			</nrg3:usageZone>
		</bldg:Building>
	</core:cityObjectMember>
	<core:cityObjectMember>
		<bldg:Building gml:id="house_lod2_2">
			<gml:description>The same house at LoD2: no window geometry; the glass is a declared ratio on each wall.</gml:description>
			<gml:name>Report house - LoD2</gml:name>
			<core:creationDate>2024-09-25</core:creationDate>
			<nrg3:referencePoint>
				<gml:Point srsName="EPSG:32633" srsDimension="3">
					<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
				</gml:Point>
			</nrg3:referencePoint>
			<bldg:class codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_class.xml">habitation</bldg:class>
			<bldg:function codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_function.xml">residential building</bldg:function>
			<bldg:yearOfConstruction>1955</bldg:yearOfConstruction>
			<bldg:roofType codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_roofType.xml">gabled roof</bldg:roofType>
			<bldg:measuredHeight uom="m">9</bldg:measuredHeight>
			<bldg:storeysAboveGround>2</bldg:storeysAboveGround>
			<bldg:storeysBelowGround>0</bldg:storeysBelowGround>
			<bldg:storeyHeightsAboveGround uom="m">3</bldg:storeyHeightsAboveGround>
			<bldg:lod0FootPrint>
				<gml:MultiSurface gml:id="fx2_id_building_1_footprint_MultiSurf" srsName="EPSG:32633" srsDimension="3">
					<gml:surfaceMember>
						<gml:OrientableSurface orientation="-">
							<gml:baseSurface xlink:href="#fx2_id_building_1_polygon_3"/>
						</gml:OrientableSurface>
					</gml:surfaceMember>
				</gml:MultiSurface>
			</bldg:lod0FootPrint>
			<bldg:lod1Solid>
				<gml:Solid gml:id="fx2_id_building_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
					<gml:exterior>
						<gml:CompositeSurface gml:id="fx2_id_building_1_lod1_CompSurf">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx2_id_building_1_lod1_Polygon_1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291320.0000 5041900.0000 0.0000 291320.0000 5041910.0000 0.0000 291330.0000 5041910.0000 0.0000 291330.0000 5041900.0000 0.0000 291320.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx2_id_building_1_lod1_Polygon_2">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291320.0000 5041900.0000 0.0000 291330.0000 5041900.0000 0.0000 291330.0000 5041900.0000 7.5000 291320.0000 5041900.0000 7.5000 291320.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx2_id_building_1_lod1_Polygon_3">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291330.0000 5041900.0000 0.0000 291330.0000 5041910.0000 0.0000 291330.0000 5041910.0000 7.5000 291330.0000 5041900.0000 7.5000 291330.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx2_id_building_1_lod1_Polygon_4">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291330.0000 5041910.0000 0.0000 291320.0000 5041910.0000 0.0000 291320.0000 5041910.0000 7.5000 291330.0000 5041910.0000 7.5000 291330.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx2_id_building_1_lod1_Polygon_5">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291320.0000 5041910.0000 0.0000 291320.0000 5041900.0000 0.0000 291320.0000 5041900.0000 7.5000 291320.0000 5041910.0000 7.5000 291320.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx2_id_building_1_lod1_Polygon_6">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291320.0000 5041900.0000 7.5000 291330.0000 5041900.0000 7.5000 291330.0000 5041910.0000 7.5000 291320.0000 5041910.0000 7.5000 291320.0000 5041900.0000 7.5000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:CompositeSurface>
					</gml:exterior>
				</gml:Solid>
			</bldg:lod1Solid>
			<bldg:lod2Solid>
				<gml:Solid gml:id="fx2_id_building_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
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
										<gml:LinearRing>
											<gml:posList>291330.0000 5041910.0000 6.0000 291330.0000 5041900.0000 6.0000 291330.0000 5041900.0000 0.0000 291330.0000 5041910.0000 0.0000 291330.0000 5041910.0000 6.0000</gml:posList>
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
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_ground_1"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx2_id_building_1_groundsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx2_id_building_1_polygon_3">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291320.0000 5041900.0000 0.0000 291320.0000 5041910.0000 0.0000 291330.0000 5041910.0000 0.0000 291330.0000 5041900.0000 0.0000 291320.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">-1</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">1</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">180</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">100</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:GroundSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:RoofSurface gml:id="fx2_id_building_1_roofsurface_1">
					<gml:description>This is RoofSurface 1 (Building 1)</gml:description>
					<gml:name>RoofSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx2_id_building_1_roofsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx2_id_building_1_polygon_1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291320.0000 5041900.0000 6.0000 291325.0000 5041900.0000 9.0000 291325.0000 5041910.0000 9.0000 291320.0000 5041910.0000 6.0000 291320.0000 5041900.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">270</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfHeatCapacity uom="kJ/(m^2*K)">1.26</nrg3:bdgBdrySurfHeatCapacity>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">30.9638</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfOpaqueSurfaceArea>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfThickness uom="mm">250</nrg3:bdgBdrySurfThickness>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:RoofSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:RoofSurface gml:id="fx2_id_building_1_roofsurface_2">
					<gml:description>This is RoofSurface 2 (Building 1)</gml:description>
					<gml:name>RoofSurface 2 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx2_id_building_1_roofsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx2_id_building_1_polygon_2">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291325.0000 5041900.0000 9.0000 291330.0000 5041900.0000 6.0000 291330.0000 5041910.0000 6.0000 291325.0000 5041910.0000 9.0000 291325.0000 5041900.0000 9.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">30.9638</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:RoofSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface gml:id="fx2_id_building_1_wallsurface_1">
					<gml:description>This is WallSurface 1 (Building 1)</gml:description>
					<gml:name>WallSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx2_id_building_1_wallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx2_id_building_1_polygon_5">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291320.0000 5041900.0000 0.0000 291330.0000 5041900.0000 0.0000 291330.0000 5041900.0000 6.0000 291325.0000 5041900.0000 9.0000 291320.0000 5041900.0000 6.0000 291320.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">180</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.2162</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">75</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface gml:id="fx2_id_building_1_wallsurface_2">
					<gml:description>This is WallSurface 2 (Building 1)</gml:description>
					<gml:name>WallSurface 2 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx2_id_building_1_wallsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx2_id_building_1_polygon_4">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291320.0000 5041910.0000 0.0000 291320.0000 5041910.0000 6.0000 291325.0000 5041910.0000 9.0000 291330.0000 5041910.0000 6.0000 291330.0000 5041910.0000 0.0000 291320.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">0</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.2162</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">75</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface gml:id="fx2_id_building_1_wallsurface_3">
					<gml:description>This is WallSurface 3 (Building 1)</gml:description>
					<gml:name>WallSurface 3 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx2_id_building_1_wallsurface_3_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx2_id_building_1_polygon_7">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291320.0000 5041900.0000 0.0000 291320.0000 5041900.0000 6.0000 291320.0000 5041910.0000 6.0000 291320.0000 5041910.0000 0.0000 291320.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">270</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.16</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<nrg3:PartyWallSurface gml:id="fx2_id_building_1_partywallsurface_1">
					<gml:description>This is WallSurface 8 (shared)</gml:description>
					<gml:name>WallSurface 8 (shared)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx2_id_building_1_partywallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx2_id_building_1_polygon_cs1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291330.0000 5041910.0000 6.0000 291330.0000 5041900.0000 6.0000 291330.0000 5041900.0000 0.0000 291330.0000 5041910.0000 0.0000 291330.0000 5041910.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
				</nrg3:PartyWallSurface>
			</bldg:boundedBy>
			<bldg:address>
				<core:Address gml:id="fx2_id_address_1">
					<core:xalAddress>
						<xAL:AddressDetails>
							<xAL:Country>
								<xAL:CountryNameCode>ALD</xAL:CountryNameCode>
								<xAL:CountryName>Bespin Territories</xAL:CountryName>
								<xAL:Locality Type="Town">
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
					</core:xalAddress>
					<core:multiPoint>
						<gml:MultiPoint srsName="EPSG:32633" srsDimension="3">
							<gml:pointMember>
								<gml:Point>
									<gml:pos>291325.0000 5041905.0000 0.0000</gml:pos>
								</gml:Point>
							</gml:pointMember>
						</gml:MultiPoint>
					</core:multiPoint>
				</core:Address>
			</bldg:address>
			<nrg3:bdgArea>
				<nrg3:QualifiedArea>
					<nrg3:description>This is a type of floor area</nrg3:description>
					<nrg3:source>Area value source text</nrg3:source>
					<nrg3:value uom="m^2">200</nrg3:value>
					<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
				</nrg3:QualifiedArea>
			</nrg3:bdgArea>
			<nrg3:bdgArea>
				<nrg3:QualifiedArea>
					<nrg3:description>This is a type of floor area</nrg3:description>
					<nrg3:source>Area value source text</nrg3:source>
					<nrg3:value uom="m^2">100</nrg3:value>
					<nrg3:type codeSpace="area_codeSpace">footprintArea</nrg3:type>
				</nrg3:QualifiedArea>
			</nrg3:bdgArea>
			<nrg3:bdgAtticThermalStatus>isOnlyCooled</nrg3:bdgAtticThermalStatus>
			<nrg3:bdgBasementThermalStatus>isOnlyHeated</nrg3:bdgBasementThermalStatus>
			<nrg3:bdgConstructionWeight codeSpace="constrWeight_codeSpace">heavy</nrg3:bdgConstructionWeight>
			<nrg3:bdgHeight>
				<nrg3:QualifiedHeight>
					<nrg3:description>This is a type of height</nrg3:description>
					<nrg3:source>Height value source text</nrg3:source>
					<nrg3:value uom="m">9</nrg3:value>
					<nrg3:type codeSpace="height_codeSpace">highestRoofEdge</nrg3:type>
				</nrg3:QualifiedHeight>
			</nrg3:bdgHeight>
			<nrg3:bdgHeight>
				<nrg3:QualifiedHeight>
					<nrg3:description>This is a type of height</nrg3:description>
					<nrg3:source>Height value source text</nrg3:source>
					<nrg3:value uom="m">0</nrg3:value>
					<nrg3:type codeSpace="height_codeSpace">bottomOfConstruction</nrg3:type>
				</nrg3:QualifiedHeight>
			</nrg3:bdgHeight>
			<nrg3:bdgIsProtected>false</nrg3:bdgIsProtected>
			<nrg3:bdgType codeSpace="bdgType_codeSpace">terracedHouse</nrg3:bdgType>
			<nrg3:bdgVolume>
				<nrg3:QualifiedVolume>
					<nrg3:description>This is a type of volume</nrg3:description>
					<nrg3:source>Volume value source text</nrg3:source>
					<nrg3:value uom="m^3">750</nrg3:value>
					<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
				</nrg3:QualifiedVolume>
			</nrg3:bdgVolume>
			<nrg3:bdgVolume>
				<nrg3:QualifiedVolume>
					<nrg3:description>This is a type of volume</nrg3:description>
					<nrg3:source>Volume value source text</nrg3:source>
					<nrg3:value uom="m^3">486</nrg3:value>
					<nrg3:type codeSpace="volume_codeSpace">netVolume</nrg3:type>
				</nrg3:QualifiedVolume>
			</nrg3:bdgVolume>
			<nrg3:buildingUnit>
				<nrg3:BuildingUnit gml:id="fx2_id_building_unit_1">
					<gml:description>This is BuildingUnit 1</gml:description>
					<gml:name>BuildingUnit 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source</nrg3:source>
							<nrg3:value uom="m^2">200</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source</nrg3:source>
							<nrg3:value uom="m^2">100</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">energyReferenceArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source</nrg3:source>
							<nrg3:value uom="m^3">750</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source</nrg3:source>
							<nrg3:value uom="m^3">875</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">energyReferenceVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:lod1Solid>
						<gml:Solid gml:id="fx2_id_building_unit_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx2_id_building_unit_1_lod1_CompSurf">
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_42e7489a-e3f6-4a45-be2a-fbe735cd2ef8"/>
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_3f00920e-17c2-41f1-acb7-e223b1199044"/>
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_ba78c9d7-0ed7-49b8-b107-d939f0186284"/>
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_1406dd4c-f070-4022-835b-50018fdc6c54"/>
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_694c7871-d386-4e68-9c88-f62140080992"/>
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_945a1c0f-31f2-4bad-9599-9aaecf0ac7ac"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="fx2_id_building_unit_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx2_id_building_unit_1_lod2_CompSurf">
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_6e3e783e-b75a-4436-9f49-ed7d5346bca0"/>
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_ed5e64ff-65d6-4da8-bd65-a726d53494fa"/>
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_b7a25cfb-c3c6-490c-8628-42c50627d42c"/>
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_204ef154-fa62-4200-b3f2-4bb427b7b42e"/>
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_1f26fb83-a013-4528-9b75-b7eed4d07b70"/>
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_0f7e6a7d-4c78-4f23-a531-482e254f1aae"/>
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_8c107b31-166a-4b7c-aec1-4800b9dd396c"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:lod3Solid>
						<gml:Solid gml:id="fx2_id_building_unit_1_lod3_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx2_id_building_unit_1_lod3_CompSurf">
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_b9c018da-8461-4762-99c2-1cae1fc6dfa2"/>
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_efca560a-2e79-4536-9e21-4e23aacef253"/>
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_80ecaada-e49a-4e7d-8955-367405f503fb"/>
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_4dbfd338-5c11-42cd-b60d-68038c5dc78f"/>
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_5103fb6c-6d3f-4756-aa3a-586039a1938f"/>
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_2d5f403b-eac9-46ff-abbe-579c1416747a"/>
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_934e4b6a-022d-4cf7-8426-883da175edd4"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod3Solid>
					<nrg3:type codeSpace="buildingUnit_codeSpace_123">residential</nrg3:type>
					<nrg3:numberOfRooms>4</nrg3:numberOfRooms>
					<nrg3:ownershipType codeSpace="ownership_type_codeSpace_abc">corporation</nrg3:ownershipType>
					<nrg3:address xlink:href="#fx2_id_address_1"/>
				</nrg3:BuildingUnit>
			</nrg3:buildingUnit>
			<nrg3:thermalZone>
				<nrg3:ThermalZone gml:id="fx2_id_thermal_zone_1">
					<gml:description>This is ThermalZone 1</gml:description>
					<gml:name>ThermalZone 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">200</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">100</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">footprintArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">180</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">energyReferenceArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">750</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">486</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">netVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:lod1Solid>
						<gml:Solid gml:id="fx2_id_thermal_zone_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx2_id_thermal_zone_1_lod1_CompSurf">
									<gml:surfaceMember xlink:href="#fx2_id_building_1_lod1_Polygon_1"/>
									<gml:surfaceMember xlink:href="#fx2_id_building_1_lod1_Polygon_2"/>
									<gml:surfaceMember xlink:href="#fx2_id_building_1_lod1_Polygon_3"/>
									<gml:surfaceMember xlink:href="#fx2_id_building_1_lod1_Polygon_4"/>
									<gml:surfaceMember xlink:href="#fx2_id_building_1_lod1_Polygon_5"/>
									<gml:surfaceMember xlink:href="#fx2_id_building_1_lod1_Polygon_6"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="fx2_id_thermal_zone_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx2_id_thermal_zone_1_lod2_CompSurf">
									<gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_4"/>
									<gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_5"/>
									<gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_7"/>
									<gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_1"/>
									<gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_2"/>
									<gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_3"/>
									<gml:surfaceMember xlink:href="#fx2_Polygon_UUID_741a8f18-1100-467f-9c40-a919c34d2065"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:heatCapacity uom="J/K">500</nrg3:heatCapacity>
					<nrg3:infiltrationRate uom="1/h">0.3</nrg3:infiltrationRate>
					<nrg3:isCooled>false</nrg3:isCooled>
					<nrg3:isHeated>true</nrg3:isHeated>
					<nrg3:coincidesWithLod2Hull>false</nrg3:coincidesWithLod2Hull>
					<nrg3:coincidesWithLod3Hull>false</nrg3:coincidesWithLod3Hull>
					<nrg3:thermalBoundary>
						<bldg:GroundSurface gml:id="fx2_id_thermal_zone_1_groundsurface_1">
							<gml:description>This is (ThermalBoundary) GroundSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) GroundSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_ground_1"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx2_id_thermal_zone_1_groundsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_3"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">-1</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">1</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">180</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">100</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:GroundSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:RoofSurface gml:id="fx2_id_thermal_zone_1_roofsurface_1">
							<gml:description>This is (ThermalBoundary) RoofSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) RoofSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx2_id_thermal_zone_1_roofsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_1"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">270</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">30.9638</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:RoofSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:RoofSurface gml:id="fx2_id_thermal_zone_1_roofsurface_2">
							<gml:description>This is (ThermalBoundary) RoofSurface 2 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) RoofSurface 2 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx2_id_thermal_zone_1_roofsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_2"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">30.9638</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:RoofSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:WallSurface gml:id="fx2_id_thermal_zone_1_wallsurface_1">
							<gml:description>This is (ThermalBoundary) WallSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx2_id_thermal_zone_1_wallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_5"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">180</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">58.7824</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.2162</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">75</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:WallSurface gml:id="fx2_id_thermal_zone_1_wallsurface_2">
							<gml:description>This is (ThermalBoundary) WallSurface 2 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 2 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx2_id_thermal_zone_1_wallsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_4"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">0</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">58.7824</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.2162</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">75</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:WallSurface gml:id="fx2_id_thermal_zone_1_wallsurface_3">
							<gml:description>This is (ThermalBoundary) WallSurface 3 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 3 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx2_id_thermal_zone_1_wallsurface_3_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_7"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">270</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">50.4</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.16</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<nrg3:PartyWallSurface gml:id="fx2_id_thermal_zone_1_partywallsurface_1">
							<gml:description>This is (ThermalBoundary) PartyWallSurface 8</gml:description>
							<gml:name>(ThermalBoundary) PartyWallSurface 8</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx2_id_thermal_zone_1_partywallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_cs1"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
						</nrg3:PartyWallSurface>
					</nrg3:thermalBoundary>
				</nrg3:ThermalZone>
			</nrg3:thermalZone>
			<nrg3:usageZone>
				<nrg3:UsageZone gml:id="fx2_id_usage_zone_1">
					<gml:description>This is UsageZone 1</gml:description>
					<gml:name>UsageZone 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">200</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">100</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">energyReferenceArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">750</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">875</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">energyReferenceVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:lod1Solid>
						<gml:Solid gml:id="fx2_id_usage_zone_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx2_id_usage_zone_1_lod1_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_42e7489a-e3f6-4a45-be2a-fbe735cd2ef8">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291320.0000 5041900.0000 0.0000 291320.0000 5041910.0000 0.0000 291330.0000 5041910.0000 0.0000 291330.0000 5041900.0000 0.0000 291320.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_3f00920e-17c2-41f1-acb7-e223b1199044">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291320.0000 5041900.0000 0.0000 291330.0000 5041900.0000 0.0000 291330.0000 5041900.0000 7.5000 291320.0000 5041900.0000 7.5000 291320.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_ba78c9d7-0ed7-49b8-b107-d939f0186284">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291330.0000 5041900.0000 0.0000 291330.0000 5041910.0000 0.0000 291330.0000 5041910.0000 7.5000 291330.0000 5041900.0000 7.5000 291330.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_1406dd4c-f070-4022-835b-50018fdc6c54">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291330.0000 5041910.0000 0.0000 291320.0000 5041910.0000 0.0000 291320.0000 5041910.0000 7.5000 291330.0000 5041910.0000 7.5000 291330.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_694c7871-d386-4e68-9c88-f62140080992">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291320.0000 5041910.0000 0.0000 291320.0000 5041900.0000 0.0000 291320.0000 5041900.0000 7.5000 291320.0000 5041910.0000 7.5000 291320.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_945a1c0f-31f2-4bad-9599-9aaecf0ac7ac">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291320.0000 5041900.0000 7.5000 291330.0000 5041900.0000 7.5000 291330.0000 5041910.0000 7.5000 291320.0000 5041910.0000 7.5000 291320.0000 5041900.0000 7.5000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="fx2_id_usage_zone_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx2_id_usage_zone_1_lod2_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_b9c018da-8461-4762-99c2-1cae1fc6dfa2">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291320.0000 5041910.0000 0.0000 291320.0000 5041910.0000 6.0000 291325.0000 5041910.0000 9.0000 291330.0000 5041910.0000 6.0000 291330.0000 5041910.0000 0.0000 291320.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_efca560a-2e79-4536-9e21-4e23aacef253">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291320.0000 5041900.0000 0.0000 291330.0000 5041900.0000 0.0000 291330.0000 5041900.0000 6.0000 291325.0000 5041900.0000 9.0000 291320.0000 5041900.0000 6.0000 291320.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_80ecaada-e49a-4e7d-8955-367405f503fb">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291320.0000 5041900.0000 0.0000 291320.0000 5041900.0000 6.0000 291320.0000 5041910.0000 6.0000 291320.0000 5041910.0000 0.0000 291320.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_4dbfd338-5c11-42cd-b60d-68038c5dc78f">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291320.0000 5041900.0000 6.0000 291325.0000 5041900.0000 9.0000 291325.0000 5041910.0000 9.0000 291320.0000 5041910.0000 6.0000 291320.0000 5041900.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_5103fb6c-6d3f-4756-aa3a-586039a1938f">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291325.0000 5041900.0000 9.0000 291330.0000 5041900.0000 6.0000 291330.0000 5041910.0000 6.0000 291325.0000 5041910.0000 9.0000 291325.0000 5041900.0000 9.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_2d5f403b-eac9-46ff-abbe-579c1416747a">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291320.0000 5041900.0000 0.0000 291320.0000 5041910.0000 0.0000 291330.0000 5041910.0000 0.0000 291330.0000 5041900.0000 0.0000 291320.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_934e4b6a-022d-4cf7-8426-883da175edd4">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291330.0000 5041910.0000 6.0000 291330.0000 5041900.0000 6.0000 291330.0000 5041900.0000 0.0000 291330.0000 5041910.0000 0.0000 291330.0000 5041910.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:lod3Solid>
						<gml:Solid gml:id="fx2_id_usage_zone_1_lod3_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx2_id_usage_zone_1_lod3_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_6e3e783e-b75a-4436-9f49-ed7d5346bca0">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291320.0000 5041910.0000 0.0000 291320.0000 5041910.0000 6.0000 291325.0000 5041910.0000 9.0000 291330.0000 5041910.0000 6.0000 291330.0000 5041910.0000 0.0000 291320.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_ed5e64ff-65d6-4da8-bd65-a726d53494fa">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291320.0000 5041900.0000 0.0000 291330.0000 5041900.0000 0.0000 291330.0000 5041900.0000 6.0000 291325.0000 5041900.0000 9.0000 291320.0000 5041900.0000 6.0000 291320.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_b7a25cfb-c3c6-490c-8628-42c50627d42c">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291320.0000 5041900.0000 0.0000 291320.0000 5041900.0000 6.0000 291320.0000 5041910.0000 6.0000 291320.0000 5041910.0000 0.0000 291320.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_204ef154-fa62-4200-b3f2-4bb427b7b42e">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291320.0000 5041900.0000 6.0000 291325.0000 5041900.0000 9.0000 291325.0000 5041910.0000 9.0000 291320.0000 5041910.0000 6.0000 291320.0000 5041900.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_1f26fb83-a013-4528-9b75-b7eed4d07b70">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291325.0000 5041900.0000 9.0000 291330.0000 5041900.0000 6.0000 291330.0000 5041910.0000 6.0000 291325.0000 5041910.0000 9.0000 291325.0000 5041900.0000 9.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_0f7e6a7d-4c78-4f23-a531-482e254f1aae">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291320.0000 5041900.0000 0.0000 291320.0000 5041910.0000 0.0000 291330.0000 5041910.0000 0.0000 291330.0000 5041900.0000 0.0000 291320.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx2_Polygon_UUID_8c107b31-166a-4b7c-aec1-4800b9dd396c">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291330.0000 5041910.0000 6.0000 291330.0000 5041900.0000 6.0000 291330.0000 5041900.0000 0.0000 291330.0000 5041910.0000 0.0000 291330.0000 5041910.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod3Solid>
					<nrg3:type codeSpace="usageZone_codeSpace_123">residential</nrg3:type>
					<nrg3:isPrimary>true</nrg3:isPrimary>
					<nrg3:numberOfBuildingUnits>1</nrg3:numberOfBuildingUnits>
					<nrg3:internalHeatGains uom="W/m^2">100</nrg3:internalHeatGains>
					<nrg3:internalHeatGainsConvectiveFraction uom="unit interval">0.3</nrg3:internalHeatGainsConvectiveFraction>
					<nrg3:internalHeatGainsLatentFraction uom="unit interval">0.2</nrg3:internalHeatGainsLatentFraction>
					<nrg3:internalHeatGainsRadiantFraction uom="unit interval">0.5</nrg3:internalHeatGainsRadiantFraction>
					<nrg3:coolingSchedule xlink:href="#id_atomic_schedule_1"/>
					<nrg3:heatingSchedule xlink:href="#id_dual_value_schedule_1"/>
					<nrg3:ventilationSchedule xlink:href="#id_composite_schedule_1"/>
					<nrg3:occupiedBy>
						<nrg3:Occupants gml:id="fx2_id_occupants_1">
							<gml:description>This is Occupants 1</gml:description>
							<gml:name>Occupants 1</gml:name>
							<nrg3:type codeSpace="occ_codeSpace_xyz">residents</nrg3:type>
							<nrg3:numberOfOccupants>12</nrg3:numberOfOccupants>
							<nrg3:heatDissipation uom="W/m^2">100</nrg3:heatDissipation>
							<nrg3:heatDissipationConvectiveFraction uom="unit interval">0.3</nrg3:heatDissipationConvectiveFraction>
							<nrg3:heatDissipationLatentFraction uom="unit interval">0.2</nrg3:heatDissipationLatentFraction>
							<nrg3:heatDissipationRadiantFraction uom="unit interval">0.5</nrg3:heatDissipationRadiantFraction>
							<nrg3:occupancyRate xlink:href="#id_atomic_schedule_2"/>
							<nrg3:averageDietType codeSpace="diet_codeSpace">omnivorous</nrg3:averageDietType>
							<nrg3:averageIncomeLevel codeSpace="income_level codeSpace">middle</nrg3:averageIncomeLevel>
							<nrg3:averageInstructionLevel codeSpace="instruction_level_codeSpace">university</nrg3:averageInstructionLevel>
						</nrg3:Occupants>
					</nrg3:occupiedBy>
				</nrg3:UsageZone>
			</nrg3:usageZone>
		</bldg:Building>
	</core:cityObjectMember>
	<core:cityObjectMember>
		<bldg:Building gml:id="house_lod2_hull_3">
			<gml:description>The same house whose thermal zone coincides with the LoD2 hull of the building.</gml:description>
			<gml:name>Report house - LoD2 hull</gml:name>
			<core:creationDate>2024-09-25</core:creationDate>
			<nrg3:referencePoint>
				<gml:Point srsName="EPSG:32633" srsDimension="3">
					<gml:pos>291345.0000 5041905.0000 4.5000</gml:pos>
				</gml:Point>
			</nrg3:referencePoint>
			<nrg3:device>
				<nrg3:Boiler gml:id="house_lod2_hull_3_boiler">
					<gml:description>A test device: a heating plant described by its own values (EuReCa's "From manual parameters"), read from the file instead of the run file.</gml:description>
					<gml:name>Own gas boiler (test device)</gml:name>
					<gml:name codeSpace="urn:eureca:heating-system">From manual parameters</gml:name>
					<core:creationDate>2026-10-03</core:creationDate>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291345.0000 5041905.0000 1.0000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<gen:stringAttribute name="name">
						<gen:value>Own gas boiler</gen:value>
					</gen:stringAttribute>
					<gen:stringAttribute name="description">
						<gen:value>a gas boiler with radiators, described by its own values</gen:value>
					</gen:stringAttribute>
					<gen:doubleAttribute name="SH generation efficiency [-]">
						<gen:value>0.99</gen:value>
					</gen:doubleAttribute>
					<gen:doubleAttribute name="SH distribution efficiency [-]">
						<gen:value>0.92</gen:value>
					</gen:doubleAttribute>
					<gen:doubleAttribute name="SH emission efficiency [-]">
						<gen:value>0.882</gen:value>
					</gen:doubleAttribute>
					<gen:doubleAttribute name="SH regulation efficiency [-]">
						<gen:value>1.0</gen:value>
					</gen:doubleAttribute>
					<gen:doubleAttribute name="SH emission convective fraction [-]">
						<gen:value>0.6</gen:value>
					</gen:doubleAttribute>
					<gen:doubleAttribute name="SH emission target temperature [°C]">
						<gen:value>45</gen:value>
					</gen:doubleAttribute>
					<gen:stringAttribute name="SH fuel">
						<gen:value>Natural Gas</gen:value>
					</gen:stringAttribute>
					<gen:doubleAttribute name="DHW generation efficiency [-]">
						<gen:value>0.99</gen:value>
					</gen:doubleAttribute>
					<gen:doubleAttribute name="DHW distribution efficiency [-]">
						<gen:value>0.92</gen:value>
					</gen:doubleAttribute>
					<gen:doubleAttribute name="DHW emission efficiency [-]">
						<gen:value>0.882</gen:value>
					</gen:doubleAttribute>
					<gen:doubleAttribute name="DHW regulation efficiency [-]">
						<gen:value>1.0</gen:value>
					</gen:doubleAttribute>
					<gen:stringAttribute name="DHW fuel">
						<gen:value>Natural Gas</gen:value>
					</gen:stringAttribute>
					<nrg3:model>Condensing gas boiler, 15 kW (generic)</nrg3:model>
					<nrg3:yearOfManufacture>2018</nrg3:yearOfManufacture>
					<nrg3:numberOfDevices>1</nrg3:numberOfDevices>
					<nrg3:installedPower uom="kW">15</nrg3:installedPower>
					<nrg3:nominalEfficiency uom="dimensionless">0.99</nrg3:nominalEfficiency>
					<nrg3:efficiencyIndicator>generation efficiency: share of the gas energy that becomes heat</nrg3:efficiencyIndicator>
					<nrg3:heatDissipation uom="W">0</nrg3:heatDissipation>
					<nrg3:heatDissipationConvectiveFraction uom="unit interval">1</nrg3:heatDissipationConvectiveFraction>
					<nrg3:heatDissipationLatentFraction uom="unit interval">0</nrg3:heatDissipationLatentFraction>
					<nrg3:heatDissipationRadiantFraction uom="unit interval">0</nrg3:heatDissipationRadiantFraction>
					<nrg3:deviceOperation>
						<nrg3:DeviceOperation gml:id="house_lod2_hull_3_boiler_heating">
							<nrg3:type>spaceHeating</nrg3:type>
							<nrg3:yearlyGlobalEfficiency>0.8</nrg3:yearlyGlobalEfficiency>
							<nrg3:schedule xlink:href="#id_dual_value_schedule_1"/>
						</nrg3:DeviceOperation>
					</nrg3:deviceOperation>
					<nrg3:deviceOperation>
						<nrg3:DeviceOperation gml:id="house_lod2_hull_3_boiler_hot_water">
							<nrg3:type>domesticHotWater</nrg3:type>
							<nrg3:yearlyGlobalEfficiency>0.8</nrg3:yearlyGlobalEfficiency>
						</nrg3:DeviceOperation>
					</nrg3:deviceOperation>
					<nrg3:hasCondensation>true</nrg3:hasCondensation>
				</nrg3:Boiler>
			</nrg3:device>
			<nrg3:device>
				<nrg3:HeatPump gml:id="house_lod2_hull_3_chiller">
					<gml:description>A test device: a cooling plant described by its own values (EuReCa's "From manual parameters"), read from the file instead of the run file.</gml:description>
					<gml:name>Own chiller (test device)</gml:name>
					<gml:name codeSpace="urn:eureca:cooling-system">From manual parameters</gml:name>
					<core:creationDate>2026-10-03</core:creationDate>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291351.0000 5041905.0000 0.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<gen:doubleAttribute name="SC generation efficiency [-]">
						<gen:value>2.7</gen:value>
					</gen:doubleAttribute>
					<gen:doubleAttribute name="SC distribution efficiency [-]">
						<gen:value>0.97</gen:value>
					</gen:doubleAttribute>
					<gen:doubleAttribute name="SC emission efficiency [-]">
						<gen:value>0.748</gen:value>
					</gen:doubleAttribute>
					<gen:doubleAttribute name="SC regulation efficiency [-]">
						<gen:value>1.0</gen:value>
					</gen:doubleAttribute>
					<gen:doubleAttribute name="SC emission convective fraction [-]">
						<gen:value>1.0</gen:value>
					</gen:doubleAttribute>
					<gen:doubleAttribute name="SC emission target temperature [°C]">
						<gen:value>12</gen:value>
					</gen:doubleAttribute>
					<gen:stringAttribute name="SC fuel">
						<gen:value>Electric</gen:value>
					</gen:stringAttribute>
					<nrg3:model>Air-to-water chiller, 10 kW (generic)</nrg3:model>
					<nrg3:yearOfManufacture>2018</nrg3:yearOfManufacture>
					<nrg3:numberOfDevices>1</nrg3:numberOfDevices>
					<nrg3:installedPower uom="kW">10</nrg3:installedPower>
					<nrg3:nominalEfficiency uom="dimensionless">2.7</nrg3:nominalEfficiency>
					<nrg3:efficiencyIndicator>seasonal performance factor: cooling delivered per unit of electricity</nrg3:efficiencyIndicator>
					<nrg3:heatDissipation uom="W">0</nrg3:heatDissipation>
					<nrg3:heatDissipationConvectiveFraction uom="unit interval">1</nrg3:heatDissipationConvectiveFraction>
					<nrg3:heatDissipationLatentFraction uom="unit interval">0</nrg3:heatDissipationLatentFraction>
					<nrg3:heatDissipationRadiantFraction uom="unit interval">0</nrg3:heatDissipationRadiantFraction>
					<nrg3:deviceOperation>
						<nrg3:DeviceOperation gml:id="house_lod2_hull_3_chiller_cooling">
							<nrg3:type>spaceCooling</nrg3:type>
							<nrg3:yearlyGlobalEfficiency>1.96</nrg3:yearlyGlobalEfficiency>
							<nrg3:schedule xlink:href="#id_atomic_schedule_1"/>
						</nrg3:DeviceOperation>
					</nrg3:deviceOperation>
					<nrg3:heatSource>ambientAir</nrg3:heatSource>
					<nrg3:copSourceTemperature uom="degrees Celsius">35</nrg3:copSourceTemperature>
					<nrg3:copOperationTemperature uom="degrees Celsius">7</nrg3:copOperationTemperature>
				</nrg3:HeatPump>
			</nrg3:device>
			<bldg:class codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_class.xml">habitation</bldg:class>
			<bldg:function codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_function.xml">residential building</bldg:function>
			<bldg:yearOfConstruction>1955</bldg:yearOfConstruction>
			<bldg:roofType codeSpace="http://www.sig3d.org/codelists/standard/building/2.0/_AbstractBuilding_roofType.xml">gabled roof</bldg:roofType>
			<bldg:measuredHeight uom="m">9</bldg:measuredHeight>
			<bldg:storeysAboveGround>2</bldg:storeysAboveGround>
			<bldg:storeysBelowGround>0</bldg:storeysBelowGround>
			<bldg:storeyHeightsAboveGround uom="m">3</bldg:storeyHeightsAboveGround>
			<bldg:lod0FootPrint>
				<gml:MultiSurface gml:id="fx7_id_building_1_footprint_MultiSurf" srsName="EPSG:32633" srsDimension="3">
					<gml:surfaceMember>
						<gml:OrientableSurface orientation="-">
							<gml:baseSurface xlink:href="#fx7_id_building_1_polygon_3"/>
						</gml:OrientableSurface>
					</gml:surfaceMember>
				</gml:MultiSurface>
			</bldg:lod0FootPrint>
			<bldg:lod1Solid>
				<gml:Solid gml:id="fx7_id_building_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
					<gml:exterior>
						<gml:CompositeSurface gml:id="fx7_id_building_1_lod1_CompSurf">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx7_id_building_1_lod1_Polygon_1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291340.0000 5041900.0000 0.0000 291340.0000 5041910.0000 0.0000 291350.0000 5041910.0000 0.0000 291350.0000 5041900.0000 0.0000 291340.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx7_id_building_1_lod1_Polygon_2">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291340.0000 5041900.0000 0.0000 291350.0000 5041900.0000 0.0000 291350.0000 5041900.0000 7.5000 291340.0000 5041900.0000 7.5000 291340.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx7_id_building_1_lod1_Polygon_3">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291350.0000 5041900.0000 0.0000 291350.0000 5041910.0000 0.0000 291350.0000 5041910.0000 7.5000 291350.0000 5041900.0000 7.5000 291350.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx7_id_building_1_lod1_Polygon_4">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291350.0000 5041910.0000 0.0000 291340.0000 5041910.0000 0.0000 291340.0000 5041910.0000 7.5000 291350.0000 5041910.0000 7.5000 291350.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx7_id_building_1_lod1_Polygon_5">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291340.0000 5041910.0000 0.0000 291340.0000 5041900.0000 0.0000 291340.0000 5041900.0000 7.5000 291340.0000 5041910.0000 7.5000 291340.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx7_id_building_1_lod1_Polygon_6">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291340.0000 5041900.0000 7.5000 291350.0000 5041900.0000 7.5000 291350.0000 5041910.0000 7.5000 291340.0000 5041910.0000 7.5000 291340.0000 5041900.0000 7.5000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:CompositeSurface>
					</gml:exterior>
				</gml:Solid>
			</bldg:lod1Solid>
			<bldg:lod2Solid>
				<gml:Solid gml:id="fx7_id_building_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
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
										<gml:LinearRing>
											<gml:posList>291350.0000 5041910.0000 6.0000 291350.0000 5041900.0000 6.0000 291350.0000 5041900.0000 0.0000 291350.0000 5041910.0000 0.0000 291350.0000 5041910.0000 6.0000</gml:posList>
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
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_ground_1"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291345.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx7_id_building_1_groundsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx7_id_building_1_polygon_3">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291340.0000 5041900.0000 0.0000 291340.0000 5041910.0000 0.0000 291350.0000 5041910.0000 0.0000 291350.0000 5041900.0000 0.0000 291340.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">-1</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">1</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">180</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">100</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:GroundSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:RoofSurface gml:id="fx7_id_building_1_roofsurface_1">
					<gml:description>This is RoofSurface 1 (Building 1)</gml:description>
					<gml:name>RoofSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291345.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx7_id_building_1_roofsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx7_id_building_1_polygon_1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291340.0000 5041900.0000 6.0000 291345.0000 5041900.0000 9.0000 291345.0000 5041910.0000 9.0000 291340.0000 5041910.0000 6.0000 291340.0000 5041900.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">270</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfHeatCapacity uom="kJ/(m^2*K)">1.26</nrg3:bdgBdrySurfHeatCapacity>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">30.9638</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfOpaqueSurfaceArea>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfThickness uom="mm">250</nrg3:bdgBdrySurfThickness>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:RoofSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:RoofSurface gml:id="fx7_id_building_1_roofsurface_2">
					<gml:description>This is RoofSurface 2 (Building 1)</gml:description>
					<gml:name>RoofSurface 2 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291345.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx7_id_building_1_roofsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx7_id_building_1_polygon_2">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291345.0000 5041900.0000 9.0000 291350.0000 5041900.0000 6.0000 291350.0000 5041910.0000 6.0000 291345.0000 5041910.0000 9.0000 291345.0000 5041900.0000 9.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">30.9638</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:RoofSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface gml:id="fx7_id_building_1_wallsurface_1">
					<gml:description>This is WallSurface 1 (Building 1)</gml:description>
					<gml:name>WallSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291345.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx7_id_building_1_wallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx7_id_building_1_polygon_5">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291340.0000 5041900.0000 0.0000 291350.0000 5041900.0000 0.0000 291350.0000 5041900.0000 6.0000 291345.0000 5041900.0000 9.0000 291340.0000 5041900.0000 6.0000 291340.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">180</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.2162</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">75</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface gml:id="fx7_id_building_1_wallsurface_2">
					<gml:description>This is WallSurface 2 (Building 1)</gml:description>
					<gml:name>WallSurface 2 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291345.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx7_id_building_1_wallsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx7_id_building_1_polygon_4">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291340.0000 5041910.0000 0.0000 291340.0000 5041910.0000 6.0000 291345.0000 5041910.0000 9.0000 291350.0000 5041910.0000 6.0000 291350.0000 5041910.0000 0.0000 291340.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">0</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.2162</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">75</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface gml:id="fx7_id_building_1_wallsurface_3">
					<gml:description>This is WallSurface 3 (Building 1)</gml:description>
					<gml:name>WallSurface 3 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291345.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx7_id_building_1_wallsurface_3_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx7_id_building_1_polygon_7">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291340.0000 5041900.0000 0.0000 291340.0000 5041900.0000 6.0000 291340.0000 5041910.0000 6.0000 291340.0000 5041910.0000 0.0000 291340.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">270</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.16</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<nrg3:PartyWallSurface gml:id="fx7_id_building_1_partywallsurface_1">
					<gml:description>This is WallSurface 8 (shared)</gml:description>
					<gml:name>WallSurface 8 (shared)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291345.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx7_id_building_1_partywallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx7_id_building_1_polygon_cs1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291350.0000 5041910.0000 6.0000 291350.0000 5041900.0000 6.0000 291350.0000 5041900.0000 0.0000 291350.0000 5041910.0000 0.0000 291350.0000 5041910.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
				</nrg3:PartyWallSurface>
			</bldg:boundedBy>
			<bldg:address>
				<core:Address gml:id="fx7_id_address_1">
					<core:xalAddress>
						<xAL:AddressDetails>
							<xAL:Country>
								<xAL:CountryNameCode>ALD</xAL:CountryNameCode>
								<xAL:CountryName>Bespin Territories</xAL:CountryName>
								<xAL:Locality Type="Town">
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
					</core:xalAddress>
					<core:multiPoint>
						<gml:MultiPoint srsName="EPSG:32633" srsDimension="3">
							<gml:pointMember>
								<gml:Point>
									<gml:pos>291345.0000 5041905.0000 0.0000</gml:pos>
								</gml:Point>
							</gml:pointMember>
						</gml:MultiPoint>
					</core:multiPoint>
				</core:Address>
			</bldg:address>
			<nrg3:bdgArea>
				<nrg3:QualifiedArea>
					<nrg3:description>This is a type of floor area</nrg3:description>
					<nrg3:source>Area value source text</nrg3:source>
					<nrg3:value uom="m^2">200</nrg3:value>
					<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
				</nrg3:QualifiedArea>
			</nrg3:bdgArea>
			<nrg3:bdgArea>
				<nrg3:QualifiedArea>
					<nrg3:description>This is a type of floor area</nrg3:description>
					<nrg3:source>Area value source text</nrg3:source>
					<nrg3:value uom="m^2">100</nrg3:value>
					<nrg3:type codeSpace="area_codeSpace">footprintArea</nrg3:type>
				</nrg3:QualifiedArea>
			</nrg3:bdgArea>
			<nrg3:bdgAtticThermalStatus>isOnlyCooled</nrg3:bdgAtticThermalStatus>
			<nrg3:bdgBasementThermalStatus>isOnlyHeated</nrg3:bdgBasementThermalStatus>
			<nrg3:bdgConstructionWeight codeSpace="constrWeight_codeSpace">heavy</nrg3:bdgConstructionWeight>
			<nrg3:bdgHeight>
				<nrg3:QualifiedHeight>
					<nrg3:description>This is a type of height</nrg3:description>
					<nrg3:source>Height value source text</nrg3:source>
					<nrg3:value uom="m">9</nrg3:value>
					<nrg3:type codeSpace="height_codeSpace">highestRoofEdge</nrg3:type>
				</nrg3:QualifiedHeight>
			</nrg3:bdgHeight>
			<nrg3:bdgHeight>
				<nrg3:QualifiedHeight>
					<nrg3:description>This is a type of height</nrg3:description>
					<nrg3:source>Height value source text</nrg3:source>
					<nrg3:value uom="m">0</nrg3:value>
					<nrg3:type codeSpace="height_codeSpace">bottomOfConstruction</nrg3:type>
				</nrg3:QualifiedHeight>
			</nrg3:bdgHeight>
			<nrg3:bdgIsProtected>false</nrg3:bdgIsProtected>
			<nrg3:bdgType codeSpace="bdgType_codeSpace">terracedHouse</nrg3:bdgType>
			<nrg3:bdgVolume>
				<nrg3:QualifiedVolume>
					<nrg3:description>This is a type of volume</nrg3:description>
					<nrg3:source>Volume value source text</nrg3:source>
					<nrg3:value uom="m^3">750</nrg3:value>
					<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
				</nrg3:QualifiedVolume>
			</nrg3:bdgVolume>
			<nrg3:bdgVolume>
				<nrg3:QualifiedVolume>
					<nrg3:description>This is a type of volume</nrg3:description>
					<nrg3:source>Volume value source text</nrg3:source>
					<nrg3:value uom="m^3">486</nrg3:value>
					<nrg3:type codeSpace="volume_codeSpace">netVolume</nrg3:type>
				</nrg3:QualifiedVolume>
			</nrg3:bdgVolume>
			<nrg3:buildingUnit>
				<nrg3:BuildingUnit gml:id="fx7_id_building_unit_1">
					<gml:description>This is BuildingUnit 1</gml:description>
					<gml:name>BuildingUnit 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291345.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source</nrg3:source>
							<nrg3:value uom="m^2">200</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source</nrg3:source>
							<nrg3:value uom="m^2">100</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">energyReferenceArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source</nrg3:source>
							<nrg3:value uom="m^3">750</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source</nrg3:source>
							<nrg3:value uom="m^3">875</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">energyReferenceVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:lod1Solid>
						<gml:Solid gml:id="fx7_id_building_unit_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx7_id_building_unit_1_lod1_CompSurf">
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_42e7489a-e3f6-4a45-be2a-fbe735cd2ef8"/>
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_3f00920e-17c2-41f1-acb7-e223b1199044"/>
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_ba78c9d7-0ed7-49b8-b107-d939f0186284"/>
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_1406dd4c-f070-4022-835b-50018fdc6c54"/>
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_694c7871-d386-4e68-9c88-f62140080992"/>
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_945a1c0f-31f2-4bad-9599-9aaecf0ac7ac"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="fx7_id_building_unit_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx7_id_building_unit_1_lod2_CompSurf">
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_6e3e783e-b75a-4436-9f49-ed7d5346bca0"/>
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_ed5e64ff-65d6-4da8-bd65-a726d53494fa"/>
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_b7a25cfb-c3c6-490c-8628-42c50627d42c"/>
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_204ef154-fa62-4200-b3f2-4bb427b7b42e"/>
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_1f26fb83-a013-4528-9b75-b7eed4d07b70"/>
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_0f7e6a7d-4c78-4f23-a531-482e254f1aae"/>
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_8c107b31-166a-4b7c-aec1-4800b9dd396c"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:lod3Solid>
						<gml:Solid gml:id="fx7_id_building_unit_1_lod3_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx7_id_building_unit_1_lod3_CompSurf">
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_b9c018da-8461-4762-99c2-1cae1fc6dfa2"/>
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_efca560a-2e79-4536-9e21-4e23aacef253"/>
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_80ecaada-e49a-4e7d-8955-367405f503fb"/>
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_4dbfd338-5c11-42cd-b60d-68038c5dc78f"/>
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_5103fb6c-6d3f-4756-aa3a-586039a1938f"/>
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_2d5f403b-eac9-46ff-abbe-579c1416747a"/>
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_934e4b6a-022d-4cf7-8426-883da175edd4"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod3Solid>
					<nrg3:type codeSpace="buildingUnit_codeSpace_123">residential</nrg3:type>
					<nrg3:numberOfRooms>4</nrg3:numberOfRooms>
					<nrg3:ownershipType codeSpace="ownership_type_codeSpace_abc">corporation</nrg3:ownershipType>
					<nrg3:address xlink:href="#fx7_id_address_1"/>
				</nrg3:BuildingUnit>
			</nrg3:buildingUnit>
			<nrg3:thermalZone>
				<nrg3:ThermalZone gml:id="fx7_id_thermal_zone_1">
					<gml:description>This is ThermalZone 1</gml:description>
					<gml:name>ThermalZone 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291345.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">200</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">100</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">footprintArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">180</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">energyReferenceArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">750</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">486</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">netVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:lod1Solid>
						<gml:Solid gml:id="fx7_id_thermal_zone_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx7_id_thermal_zone_1_lod1_CompSurf">
									<gml:surfaceMember xlink:href="#fx7_id_building_1_lod1_Polygon_1"/>
									<gml:surfaceMember xlink:href="#fx7_id_building_1_lod1_Polygon_2"/>
									<gml:surfaceMember xlink:href="#fx7_id_building_1_lod1_Polygon_3"/>
									<gml:surfaceMember xlink:href="#fx7_id_building_1_lod1_Polygon_4"/>
									<gml:surfaceMember xlink:href="#fx7_id_building_1_lod1_Polygon_5"/>
									<gml:surfaceMember xlink:href="#fx7_id_building_1_lod1_Polygon_6"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="fx7_id_thermal_zone_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx7_id_thermal_zone_1_lod2_CompSurf">
									<gml:surfaceMember xlink:href="#fx7_id_building_1_polygon_4"/>
									<gml:surfaceMember xlink:href="#fx7_id_building_1_polygon_5"/>
									<gml:surfaceMember xlink:href="#fx7_id_building_1_polygon_7"/>
									<gml:surfaceMember xlink:href="#fx7_id_building_1_polygon_1"/>
									<gml:surfaceMember xlink:href="#fx7_id_building_1_polygon_2"/>
									<gml:surfaceMember xlink:href="#fx7_id_building_1_polygon_3"/>
									<gml:surfaceMember xlink:href="#fx7_Polygon_UUID_741a8f18-1100-467f-9c40-a919c34d2065"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:heatCapacity uom="J/K">500</nrg3:heatCapacity>
					<nrg3:infiltrationRate uom="1/h">0.3</nrg3:infiltrationRate>
					<nrg3:isCooled>false</nrg3:isCooled>
					<nrg3:isHeated>true</nrg3:isHeated>
					<nrg3:coincidesWithLod2Hull>true</nrg3:coincidesWithLod2Hull>
					<nrg3:coincidesWithLod3Hull>false</nrg3:coincidesWithLod3Hull>
				</nrg3:ThermalZone>
			</nrg3:thermalZone>
			<nrg3:usageZone>
				<nrg3:UsageZone gml:id="fx7_id_usage_zone_1">
					<gml:description>This is UsageZone 1</gml:description>
					<gml:name>UsageZone 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291345.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">200</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">100</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">energyReferenceArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">750</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">875</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">energyReferenceVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:lod1Solid>
						<gml:Solid gml:id="fx7_id_usage_zone_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx7_id_usage_zone_1_lod1_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_42e7489a-e3f6-4a45-be2a-fbe735cd2ef8">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291340.0000 5041900.0000 0.0000 291340.0000 5041910.0000 0.0000 291350.0000 5041910.0000 0.0000 291350.0000 5041900.0000 0.0000 291340.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_3f00920e-17c2-41f1-acb7-e223b1199044">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291340.0000 5041900.0000 0.0000 291350.0000 5041900.0000 0.0000 291350.0000 5041900.0000 7.5000 291340.0000 5041900.0000 7.5000 291340.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_ba78c9d7-0ed7-49b8-b107-d939f0186284">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291350.0000 5041900.0000 0.0000 291350.0000 5041910.0000 0.0000 291350.0000 5041910.0000 7.5000 291350.0000 5041900.0000 7.5000 291350.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_1406dd4c-f070-4022-835b-50018fdc6c54">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291350.0000 5041910.0000 0.0000 291340.0000 5041910.0000 0.0000 291340.0000 5041910.0000 7.5000 291350.0000 5041910.0000 7.5000 291350.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_694c7871-d386-4e68-9c88-f62140080992">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291340.0000 5041910.0000 0.0000 291340.0000 5041900.0000 0.0000 291340.0000 5041900.0000 7.5000 291340.0000 5041910.0000 7.5000 291340.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_945a1c0f-31f2-4bad-9599-9aaecf0ac7ac">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291340.0000 5041900.0000 7.5000 291350.0000 5041900.0000 7.5000 291350.0000 5041910.0000 7.5000 291340.0000 5041910.0000 7.5000 291340.0000 5041900.0000 7.5000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="fx7_id_usage_zone_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx7_id_usage_zone_1_lod2_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_b9c018da-8461-4762-99c2-1cae1fc6dfa2">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291340.0000 5041910.0000 0.0000 291340.0000 5041910.0000 6.0000 291345.0000 5041910.0000 9.0000 291350.0000 5041910.0000 6.0000 291350.0000 5041910.0000 0.0000 291340.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_efca560a-2e79-4536-9e21-4e23aacef253">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291340.0000 5041900.0000 0.0000 291350.0000 5041900.0000 0.0000 291350.0000 5041900.0000 6.0000 291345.0000 5041900.0000 9.0000 291340.0000 5041900.0000 6.0000 291340.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_80ecaada-e49a-4e7d-8955-367405f503fb">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291340.0000 5041900.0000 0.0000 291340.0000 5041900.0000 6.0000 291340.0000 5041910.0000 6.0000 291340.0000 5041910.0000 0.0000 291340.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_4dbfd338-5c11-42cd-b60d-68038c5dc78f">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291340.0000 5041900.0000 6.0000 291345.0000 5041900.0000 9.0000 291345.0000 5041910.0000 9.0000 291340.0000 5041910.0000 6.0000 291340.0000 5041900.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_5103fb6c-6d3f-4756-aa3a-586039a1938f">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291345.0000 5041900.0000 9.0000 291350.0000 5041900.0000 6.0000 291350.0000 5041910.0000 6.0000 291345.0000 5041910.0000 9.0000 291345.0000 5041900.0000 9.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_2d5f403b-eac9-46ff-abbe-579c1416747a">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291340.0000 5041900.0000 0.0000 291340.0000 5041910.0000 0.0000 291350.0000 5041910.0000 0.0000 291350.0000 5041900.0000 0.0000 291340.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_934e4b6a-022d-4cf7-8426-883da175edd4">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291350.0000 5041910.0000 6.0000 291350.0000 5041900.0000 6.0000 291350.0000 5041900.0000 0.0000 291350.0000 5041910.0000 0.0000 291350.0000 5041910.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:lod3Solid>
						<gml:Solid gml:id="fx7_id_usage_zone_1_lod3_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx7_id_usage_zone_1_lod3_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_6e3e783e-b75a-4436-9f49-ed7d5346bca0">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291340.0000 5041910.0000 0.0000 291340.0000 5041910.0000 6.0000 291345.0000 5041910.0000 9.0000 291350.0000 5041910.0000 6.0000 291350.0000 5041910.0000 0.0000 291340.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_ed5e64ff-65d6-4da8-bd65-a726d53494fa">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291340.0000 5041900.0000 0.0000 291350.0000 5041900.0000 0.0000 291350.0000 5041900.0000 6.0000 291345.0000 5041900.0000 9.0000 291340.0000 5041900.0000 6.0000 291340.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_b7a25cfb-c3c6-490c-8628-42c50627d42c">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291340.0000 5041900.0000 0.0000 291340.0000 5041900.0000 6.0000 291340.0000 5041910.0000 6.0000 291340.0000 5041910.0000 0.0000 291340.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_204ef154-fa62-4200-b3f2-4bb427b7b42e">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291340.0000 5041900.0000 6.0000 291345.0000 5041900.0000 9.0000 291345.0000 5041910.0000 9.0000 291340.0000 5041910.0000 6.0000 291340.0000 5041900.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_1f26fb83-a013-4528-9b75-b7eed4d07b70">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291345.0000 5041900.0000 9.0000 291350.0000 5041900.0000 6.0000 291350.0000 5041910.0000 6.0000 291345.0000 5041910.0000 9.0000 291345.0000 5041900.0000 9.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_0f7e6a7d-4c78-4f23-a531-482e254f1aae">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291340.0000 5041900.0000 0.0000 291340.0000 5041910.0000 0.0000 291350.0000 5041910.0000 0.0000 291350.0000 5041900.0000 0.0000 291340.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx7_Polygon_UUID_8c107b31-166a-4b7c-aec1-4800b9dd396c">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291350.0000 5041910.0000 6.0000 291350.0000 5041900.0000 6.0000 291350.0000 5041900.0000 0.0000 291350.0000 5041910.0000 0.0000 291350.0000 5041910.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod3Solid>
					<nrg3:type codeSpace="usageZone_codeSpace_123">residential</nrg3:type>
					<nrg3:isPrimary>true</nrg3:isPrimary>
					<nrg3:numberOfBuildingUnits>1</nrg3:numberOfBuildingUnits>
					<nrg3:internalHeatGains uom="W/m^2">100</nrg3:internalHeatGains>
					<nrg3:internalHeatGainsConvectiveFraction uom="unit interval">0.3</nrg3:internalHeatGainsConvectiveFraction>
					<nrg3:internalHeatGainsLatentFraction uom="unit interval">0.2</nrg3:internalHeatGainsLatentFraction>
					<nrg3:internalHeatGainsRadiantFraction uom="unit interval">0.5</nrg3:internalHeatGainsRadiantFraction>
					<nrg3:coolingSchedule xlink:href="#id_atomic_schedule_1"/>
					<nrg3:heatingSchedule xlink:href="#id_dual_value_schedule_1"/>
					<nrg3:ventilationSchedule xlink:href="#id_composite_schedule_1"/>
					<nrg3:occupiedBy>
						<nrg3:Occupants gml:id="fx7_id_occupants_1">
							<gml:description>This is Occupants 1</gml:description>
							<gml:name>Occupants 1</gml:name>
							<nrg3:type codeSpace="occ_codeSpace_xyz">residents</nrg3:type>
							<nrg3:numberOfOccupants>12</nrg3:numberOfOccupants>
							<nrg3:heatDissipation uom="W/m^2">100</nrg3:heatDissipation>
							<nrg3:heatDissipationConvectiveFraction uom="unit interval">0.3</nrg3:heatDissipationConvectiveFraction>
							<nrg3:heatDissipationLatentFraction uom="unit interval">0.2</nrg3:heatDissipationLatentFraction>
							<nrg3:heatDissipationRadiantFraction uom="unit interval">0.5</nrg3:heatDissipationRadiantFraction>
							<nrg3:occupancyRate xlink:href="#id_atomic_schedule_2"/>
							<nrg3:averageDietType codeSpace="diet_codeSpace">omnivorous</nrg3:averageDietType>
							<nrg3:averageIncomeLevel codeSpace="income_level codeSpace">middle</nrg3:averageIncomeLevel>
							<nrg3:averageInstructionLevel codeSpace="instruction_level_codeSpace">university</nrg3:averageInstructionLevel>
						</nrg3:Occupants>
					</nrg3:occupiedBy>
				</nrg3:UsageZone>
			</nrg3:usageZone>
		</bldg:Building>
	</core:cityObjectMember>
	<core:cityObjectMember>
		<bldg:Building gml:id="house_lod1_4">
			<gml:description>The same house as a LoD1 box: no windows and no party wall, all LoD1 may say. Its thermal zone states one average U-value for the whole shell.</gml:description>
			<gml:name>Report house - LoD1</gml:name>
			<core:creationDate>2024-09-25</core:creationDate>
			<nrg3:referencePoint>
				<gml:Point srsName="EPSG:32633" srsDimension="3">
					<gml:pos>291365.0000 5041905.0000 3.0000</gml:pos>
				</gml:Point>
			</nrg3:referencePoint>
			<nrg3:device>
				<nrg3:HeatPump gml:id="house_lod1_4_heat_pump">
					<gml:description>A test device: the plant of this house, read from the file instead of the run file.</gml:description>
					<gml:name>Heat pump (test device)</gml:name>
					<gml:name codeSpace="urn:eureca:heating-system">A-W Heat Pump, Centralized, Low Temp Radiator</gml:name>
					<core:creationDate>2026-10-03</core:creationDate>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291371.0000 5041905.0000 0.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<nrg3:model>Air-to-water heat pump, 6 kW (generic)</nrg3:model>
					<nrg3:yearOfManufacture>2020</nrg3:yearOfManufacture>
					<nrg3:numberOfDevices>1</nrg3:numberOfDevices>
					<nrg3:installedPower uom="kW">6</nrg3:installedPower>
					<nrg3:nominalEfficiency uom="dimensionless">3.2</nrg3:nominalEfficiency>
					<nrg3:efficiencyIndicator>COP at 7 degC outdoor air and 35 degC water</nrg3:efficiencyIndicator>
					<nrg3:heatDissipation uom="W">0</nrg3:heatDissipation>
					<nrg3:heatDissipationConvectiveFraction uom="unit interval">1</nrg3:heatDissipationConvectiveFraction>
					<nrg3:heatDissipationLatentFraction uom="unit interval">0</nrg3:heatDissipationLatentFraction>
					<nrg3:heatDissipationRadiantFraction uom="unit interval">0</nrg3:heatDissipationRadiantFraction>
					<nrg3:deviceOperation>
						<nrg3:DeviceOperation gml:id="house_lod1_4_heat_pump_operation">
							<nrg3:type>spaceHeating</nrg3:type>
							<nrg3:yearlyGlobalEfficiency>2.6</nrg3:yearlyGlobalEfficiency>
							<nrg3:schedule xlink:href="#id_dual_value_schedule_1"/>
						</nrg3:DeviceOperation>
					</nrg3:deviceOperation>
					<nrg3:heatSource>ambientAir</nrg3:heatSource>
					<nrg3:copSourceTemperature uom="degrees Celsius">7</nrg3:copSourceTemperature>
					<nrg3:copOperationTemperature uom="degrees Celsius">35</nrg3:copOperationTemperature>
				</nrg3:HeatPump>
			</nrg3:device>
			<bldg:lod0FootPrint>
				<gml:MultiSurface gml:id="fx1_id_lod0_MultiSurf_20" srsName="EPSG:32633" srsDimension="3">
					<gml:surfaceMember>
						<gml:Polygon gml:id="fx1_id_lod0_Polygon_20">
							<gml:exterior>
								<gml:LinearRing>
									<gml:posList>291360.0000 5041900.0000 0.0000 291370.0000 5041900.0000 0.0000 291370.0000 5041910.0000 0.0000 291360.0000 5041910.0000 0.0000 291360.0000 5041900.0000 0.0000</gml:posList>
								</gml:LinearRing>
							</gml:exterior>
						</gml:Polygon>
					</gml:surfaceMember>
				</gml:MultiSurface>
			</bldg:lod0FootPrint>
			<bldg:lod1Solid>
				<gml:Solid gml:id="fx1_id_lod1_Solid_20" srsName="EPSG:32633" srsDimension="3">
					<gml:exterior>
						<gml:CompositeSurface gml:id="fx1_id_lod1_CompSurf_20">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx1_id_lod1_Polygon_1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291360.0000 5041900.0000 0.0000 291360.0000 5041910.0000 0.0000 291370.0000 5041910.0000 0.0000 291370.0000 5041900.0000 0.0000 291360.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx1_id_lod1_Polygon_2">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291360.0000 5041900.0000 0.0000 291370.0000 5041900.0000 0.0000 291370.0000 5041900.0000 6.0000 291360.0000 5041900.0000 6.0000 291360.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx1_id_lod1_Polygon_3">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291370.0000 5041900.0000 0.0000 291370.0000 5041910.0000 0.0000 291370.0000 5041910.0000 6.0000 291370.0000 5041900.0000 6.0000 291370.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx1_id_lod1_Polygon_4">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291370.0000 5041910.0000 0.0000 291360.0000 5041910.0000 0.0000 291360.0000 5041910.0000 6.0000 291370.0000 5041910.0000 6.0000 291370.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx1_id_lod1_Polygon_5">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291360.0000 5041910.0000 0.0000 291360.0000 5041900.0000 0.0000 291360.0000 5041900.0000 6.0000 291360.0000 5041910.0000 6.0000 291360.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx1_id_lod1_Polygon_6">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291360.0000 5041900.0000 6.0000 291370.0000 5041900.0000 6.0000 291370.0000 5041910.0000 6.0000 291360.0000 5041910.0000 6.0000 291360.0000 5041900.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:CompositeSurface>
					</gml:exterior>
				</gml:Solid>
			</bldg:lod1Solid>
			<nrg3:thermalZone>
				<nrg3:ThermalZone gml:id="fx_lod1_thermal_zone">
					<gml:description>This is ThermalZone 1</gml:description>
					<gml:name>ThermalZone 1</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_hull_6"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291365.0000 5041905.0000 3.0000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">200</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">100</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">footprintArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">180</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">energyReferenceArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">600</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">486</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">netVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:lod1Solid>
						<gml:Solid gml:id="fx_lod1_thermal_zone_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx_lod1_thermal_zone_lod1_CompSurf">
									<gml:surfaceMember xlink:href="#fx1_id_lod1_Polygon_1"/>
									<gml:surfaceMember xlink:href="#fx1_id_lod1_Polygon_2"/>
									<gml:surfaceMember xlink:href="#fx1_id_lod1_Polygon_3"/>
									<gml:surfaceMember xlink:href="#fx1_id_lod1_Polygon_4"/>
									<gml:surfaceMember xlink:href="#fx1_id_lod1_Polygon_5"/>
									<gml:surfaceMember xlink:href="#fx1_id_lod1_Polygon_6"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:heatCapacity uom="J/K">500</nrg3:heatCapacity>
					<nrg3:infiltrationRate uom="1/h">0.3</nrg3:infiltrationRate>
					<nrg3:isCooled>false</nrg3:isCooled>
					<nrg3:isHeated>true</nrg3:isHeated>
					<nrg3:coincidesWithLod2Hull>false</nrg3:coincidesWithLod2Hull>
					<nrg3:coincidesWithLod3Hull>false</nrg3:coincidesWithLod3Hull>
				</nrg3:ThermalZone>
			</nrg3:thermalZone>
		</bldg:Building>
	</core:cityObjectMember>
	</core:CityModel>
