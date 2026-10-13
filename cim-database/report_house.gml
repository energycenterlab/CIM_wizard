<?xml version='1.0' encoding='utf-8'?>
<!--
  REPORT HOUSE - the sample of this project. One house in Venice (10 x 10 m, 2 storeys,
  gabled roof, standing alone), written nine times, 20 m apart. Every house is the same
  house with ONE difference, so their results can be compared.

    house1_lod3               LoD3: real windows cut into the walls
    house2_lod2               LoD2: the glass only as a share of each wall. THE BASELINE
    house3_lod2_hull          LoD2: the thermal zone coincides with the building's LoD2 hull
    house4_lod1               LoD1: a plain box, no windows, one average U-value (0.489)
    house5_lod2_ready_plant   house2_lod2 + a heat pump by its EuReCa name, 6 kW
    house6_lod2_own_plant     house2_lod2 + a gas boiler (15 kW) and a chiller (10 kW)
                              by their own values (EuReCa's "From manual parameters")
    house7_lod3_hull          LoD3: the thermal zone coincides with the building's LoD3 hull
    house8_lod2_two_zones     house2_lod2 as two dwellings side by side: two thermal zones,
                              the party wall written in both (the one house that runs 2C)
    house9_lod2_no_window     house2_lod2 with no glass: every wall is fully opaque

  Only houses 5 and 6 state a plant; the others take theirs from the run file.
  House 8 has two thermal zones, each 90 m2 and 243 m3, with the party wall as its internal
  surface. Every other house has one: 180 m2 of heated floor, 486 m3, no internal surface.

  Derived from the Energy ADE 3.0 test dataset 'Alderaan' (Giorgio Agugiaro, 3D
  Geoinformation, TU Delft). We moved it to Venice, made it 2 storeys high and standing
  alone, and gave it the material values of a real house.

  Keep this comment short: QGIS opens a GML file only if its first 4096 bytes reach the
  namespaces on the CityModel line below.
-->
<core:CityModel xmlns:bldg="http://www.opengis.net/citygml/building/2.0" xmlns:core="http://www.opengis.net/citygml/2.0" xmlns:gen="http://www.opengis.net/citygml/generics/2.0" xmlns:gml="http://www.opengis.net/gml" xmlns:nrg3="http://www.citygml.org/ade/energy/3.0" xmlns:ns5="urn:oasis:names:tc:ciq:xsdschema:xAL:2.0" xmlns:xlink="http://www.w3.org/1999/xlink">
	<gml:description>One house standing alone, in Venice, written at LoD3, LoD2, LoD2-hull, LoD1 and LoD3-hull, twice more at LoD2 with its plant stated, once at LoD2 as two dwellings, and once at LoD2 with no glass. Derived from the Energy ADE 3.0 test dataset 'Alderaan' created by Giorgio Agugiaro (g.agugiaro@tudelft.nl).</gml:description>
	<gml:name>Report house, Venice</gml:name>
	<gml:boundedBy>
		<gml:Envelope srsName="EPSG:32633" srsDimension="3">
			<gml:lowerCorner>291300.0000 5041900.0000 0.0000</gml:lowerCorner>
			<gml:upperCorner>291470.0000 5041910.0000 9.0000</gml:upperCorner>
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
					<nrg3:gValue uom="unit interval">0.6</nrg3:gValue>
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
							<nrg3:fraction uom="unit interval">0.5</nrg3:fraction>
							<nrg3:wavelengthRange>solar</nrg3:wavelengthRange>
						</nrg3:Transmittance>
					</nrg3:transmittance>
					<nrg3:transmittance>
						<nrg3:Transmittance>
							<nrg3:fraction uom="unit interval">0.7</nrg3:fraction>
							<nrg3:wavelengthRange>visible</nrg3:wavelengthRange>
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
					<nrg3:emissivity>
						<nrg3:Emissivity>
							<nrg3:fraction uom="unit interval">0.9</nrg3:fraction>
							<nrg3:surface>outside</nrg3:surface>
						</nrg3:Emissivity>
					</nrg3:emissivity>
					<nrg3:emissivity>
						<nrg3:Emissivity>
							<nrg3:fraction uom="unit interval">0.9</nrg3:fraction>
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
					<nrg3:emissivity>
						<nrg3:Emissivity>
							<nrg3:fraction uom="unit interval">0.9</nrg3:fraction>
							<nrg3:surface>outside</nrg3:surface>
						</nrg3:Emissivity>
					</nrg3:emissivity>
					<nrg3:emissivity>
						<nrg3:Emissivity>
							<nrg3:fraction uom="unit interval">0.9</nrg3:fraction>
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
					<nrg3:emissivity>
						<nrg3:Emissivity>
							<nrg3:fraction uom="unit interval">0.9</nrg3:fraction>
							<nrg3:surface>outside</nrg3:surface>
						</nrg3:Emissivity>
					</nrg3:emissivity>
					<nrg3:emissivity>
						<nrg3:Emissivity>
							<nrg3:fraction uom="unit interval">0.9</nrg3:fraction>
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
					<nrg3:emissivity>
						<nrg3:Emissivity>
							<nrg3:fraction uom="unit interval">0.9</nrg3:fraction>
							<nrg3:surface>outside</nrg3:surface>
						</nrg3:Emissivity>
					</nrg3:emissivity>
					<nrg3:emissivity>
						<nrg3:Emissivity>
							<nrg3:fraction uom="unit interval">0.9</nrg3:fraction>
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
					<nrg3:uValue uom="W/(K*m^2)">0.489</nrg3:uValue>
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
					<nrg3:rValue uom="m^2*K/W">0.18</nrg3:rValue>
				</nrg3:Gas>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:Gas gml:id="id_gas_2">
					<gml:description>This is Gas 2</gml:description>
					<gml:name>Gas 2</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">gas_code_2</nrg3:libraryCode>
					<nrg3:isVentilated>false</nrg3:isVentilated>
					<nrg3:rValue uom="m^2*K/W">0.18</nrg3:rValue>
				</nrg3:Gas>
			</nrg3:libraryMember>
			<nrg3:libraryMember>
				<nrg3:SolidMaterial gml:id="id_solid_material_1">
					<gml:description>This is SolidMaterial 1</gml:description>
					<gml:name>SolidMaterial 1</gml:name>
					<nrg3:libraryCode codeSpace="gascode_codeSpace">solid_material_code_1</nrg3:libraryCode>
					<nrg3:thermalConductivity uom="W/(K*m)">3.5</nrg3:thermalConductivity>
					<nrg3:density uom="kg/m^3">2500</nrg3:density>
					<nrg3:specificHeatCapacity uom="J/(kg*K)">1000</nrg3:specificHeatCapacity>
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
					<nrg3:specificHeatCapacity uom="J/(kg*K)">1000</nrg3:specificHeatCapacity>
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
					<nrg3:specificHeatCapacity uom="J/(kg*K)">1220</nrg3:specificHeatCapacity>
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
					<nrg3:specificHeatCapacity uom="J/(kg*K)">1000</nrg3:specificHeatCapacity>
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
					<nrg3:specificHeatCapacity uom="J/(kg*K)">1000</nrg3:specificHeatCapacity>
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
					<nrg3:specificHeatCapacity uom="J/(kg*K)">1000</nrg3:specificHeatCapacity>
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
					<nrg3:specificHeatCapacity uom="J/(kg*K)">1000</nrg3:specificHeatCapacity>
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
					<nrg3:specificHeatCapacity uom="J/(kg*K)">1220</nrg3:specificHeatCapacity>
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
					<nrg3:specificHeatCapacity uom="J/(kg*K)">910</nrg3:specificHeatCapacity>
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
					<nrg3:specificHeatCapacity uom="J/(kg*K)">1000</nrg3:specificHeatCapacity>
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
					<nrg3:specificHeatCapacity uom="J/(kg*K)">1000</nrg3:specificHeatCapacity>
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
					<nrg3:specificHeatCapacity uom="J/(kg*K)">670</nrg3:specificHeatCapacity>
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
					<nrg3:specificHeatCapacity uom="J/(kg*K)">1000</nrg3:specificHeatCapacity>
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
					<nrg3:specificHeatCapacity uom="J/(kg*K)">1000</nrg3:specificHeatCapacity>
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
					<nrg3:specificHeatCapacity uom="J/(kg*K)">1000</nrg3:specificHeatCapacity>
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
					<nrg3:specificHeatCapacity uom="J/(kg*K)">1000</nrg3:specificHeatCapacity>
					<nrg3:porosity uom="ratio">0.05</nrg3:porosity>
					<nrg3:embodiedEnergy uom="kWh/kg">9.4</nrg3:embodiedEnergy>
					<nrg3:embodiedCarbon uom="kgCO2/kg">0.5</nrg3:embodiedCarbon>
				</nrg3:SolidMaterial>
			</nrg3:libraryMember>
		</nrg3:MaterialLibrary>
	</core:cityObjectMember>
	<core:cityObjectMember>
		<bldg:Building gml:id="house1_lod3">
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
							<gml:surfaceMember xlink:href="#id_building_1_polygon_cs1"/>
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
					<nrg3:bdgBdrySurfHeatCapacity uom="kJ/(m^2*K)">508</nrg3:bdgBdrySurfHeatCapacity>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">30.9638</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfOpaqueSurfaceArea>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfThickness uom="mm">365</nrg3:bdgBdrySurfThickness>
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
				<bldg:WallSurface gml:id="id_building_1_wallsurface_4">
					<gml:description>This is WallSurface 4 (Building 1)</gml:description>
					<gml:name>WallSurface 4 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="id_building_1_wallsurface_4_lod2_geom" srsName="EPSG:32633" srsDimension="3">
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
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:address>
				<core:Address gml:id="id_address_1">
					<core:xalAddress>
						<ns5:AddressDetails>
							<ns5:Country>
								<ns5:CountryNameCode>ALD</ns5:CountryNameCode>
								<ns5:CountryName>Bespin Territories</ns5:CountryName>
								<ns5:Locality Type="Town">
									<ns5:LocalityName>Alderaan</ns5:LocalityName>
									<ns5:Thoroughfare Type="Street">
										<ns5:ThoroughfareNumber>1</ns5:ThoroughfareNumber>
										<ns5:ThoroughfareName>Bespin Square</ns5:ThoroughfareName>
									</ns5:Thoroughfare>
									<ns5:PostalCode>
										<ns5:PostalCodeNumber>1977SW</ns5:PostalCodeNumber>
									</ns5:PostalCode>
								</ns5:Locality>
							</ns5:Country>
						</ns5:AddressDetails>
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
			<nrg3:bdgType codeSpace="bdgType_codeSpace">singleFamilyHouse</nrg3:bdgType>
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
							<nrg3:value uom="m^2">180</nrg3:value>
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
							<nrg3:value uom="m^3">486</nrg3:value>
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
									<gml:surfaceMember xlink:href="#id_building_1_polygon_cs1"/>
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
					<nrg3:heatCapacity uom="J/K">46800000</nrg3:heatCapacity>
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
						<bldg:WallSurface gml:id="id_thermal_zone_1_wallsurface_4">
							<gml:description>This is (ThermalBoundary) WallSurface 4 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 4 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291305.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="id_thermal_zone_1_wallsurface_4_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#id_building_1_polygon_cs1"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<bldg:lod3MultiSurface>
								<gml:MultiSurface gml:id="id_thermal_zone_1_wallsurface_4_lod3_geom" srsName="EPSG:32633" srsDimension="3">
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
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
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
					<nrg3:internalHeatGains uom="W/m^2">1.4</nrg3:internalHeatGains>
					<nrg3:internalHeatGainsConvectiveFraction uom="unit interval">0.3</nrg3:internalHeatGainsConvectiveFraction>
					<nrg3:internalHeatGainsLatentFraction uom="unit interval">0.2</nrg3:internalHeatGainsLatentFraction>
					<nrg3:internalHeatGainsRadiantFraction uom="unit interval">0.5</nrg3:internalHeatGainsRadiantFraction>
					<nrg3:occupiedBy>
						<nrg3:Occupants gml:id="id_occupants_1">
							<gml:description>This is Occupants 1</gml:description>
							<gml:name>Occupants 1</gml:name>
							<nrg3:type codeSpace="occ_codeSpace_xyz">residents</nrg3:type>
							<nrg3:numberOfOccupants>4</nrg3:numberOfOccupants>
							<nrg3:heatDissipation uom="W/m^2">0.7</nrg3:heatDissipation>
							<nrg3:heatDissipationConvectiveFraction uom="unit interval">0.3</nrg3:heatDissipationConvectiveFraction>
							<nrg3:heatDissipationLatentFraction uom="unit interval">0.2</nrg3:heatDissipationLatentFraction>
							<nrg3:heatDissipationRadiantFraction uom="unit interval">0.5</nrg3:heatDissipationRadiantFraction>
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
		<bldg:Building gml:id="house2_lod2">
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
							<gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_cs1"/>
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
					<nrg3:bdgBdrySurfHeatCapacity uom="kJ/(m^2*K)">508</nrg3:bdgBdrySurfHeatCapacity>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">30.9638</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfOpaqueSurfaceArea>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfThickness uom="mm">365</nrg3:bdgBdrySurfThickness>
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
				<bldg:WallSurface gml:id="fx2_id_building_1_wallsurface_4">
					<gml:description>This is WallSurface 4 (Building 1)</gml:description>
					<gml:name>WallSurface 4 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx2_id_building_1_wallsurface_4_lod2_geom" srsName="EPSG:32633" srsDimension="3">
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
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:address>
				<core:Address gml:id="fx2_id_address_1">
					<core:xalAddress>
						<ns5:AddressDetails>
							<ns5:Country>
								<ns5:CountryNameCode>ALD</ns5:CountryNameCode>
								<ns5:CountryName>Bespin Territories</ns5:CountryName>
								<ns5:Locality Type="Town">
									<ns5:LocalityName>Alderaan</ns5:LocalityName>
									<ns5:Thoroughfare Type="Street">
										<ns5:ThoroughfareNumber>1</ns5:ThoroughfareNumber>
										<ns5:ThoroughfareName>Bespin Square</ns5:ThoroughfareName>
									</ns5:Thoroughfare>
									<ns5:PostalCode>
										<ns5:PostalCodeNumber>1977SW</ns5:PostalCodeNumber>
									</ns5:PostalCode>
								</ns5:Locality>
							</ns5:Country>
						</ns5:AddressDetails>
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
			<nrg3:bdgType codeSpace="bdgType_codeSpace">singleFamilyHouse</nrg3:bdgType>
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
							<nrg3:value uom="m^2">180</nrg3:value>
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
							<nrg3:value uom="m^3">486</nrg3:value>
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
									<gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_cs1"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:heatCapacity uom="J/K">46800000</nrg3:heatCapacity>
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
						<bldg:WallSurface gml:id="fx2_id_thermal_zone_1_wallsurface_4">
							<gml:description>This is (ThermalBoundary) WallSurface 4 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 4 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291325.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx2_id_thermal_zone_1_wallsurface_4_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx2_id_building_1_polygon_cs1"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
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
					<nrg3:internalHeatGains uom="W/m^2">1.4</nrg3:internalHeatGains>
					<nrg3:internalHeatGainsConvectiveFraction uom="unit interval">0.3</nrg3:internalHeatGainsConvectiveFraction>
					<nrg3:internalHeatGainsLatentFraction uom="unit interval">0.2</nrg3:internalHeatGainsLatentFraction>
					<nrg3:internalHeatGainsRadiantFraction uom="unit interval">0.5</nrg3:internalHeatGainsRadiantFraction>
					<nrg3:occupiedBy>
						<nrg3:Occupants gml:id="fx2_id_occupants_1">
							<gml:description>This is Occupants 1</gml:description>
							<gml:name>Occupants 1</gml:name>
							<nrg3:type codeSpace="occ_codeSpace_xyz">residents</nrg3:type>
							<nrg3:numberOfOccupants>4</nrg3:numberOfOccupants>
							<nrg3:heatDissipation uom="W/m^2">0.7</nrg3:heatDissipation>
							<nrg3:heatDissipationConvectiveFraction uom="unit interval">0.3</nrg3:heatDissipationConvectiveFraction>
							<nrg3:heatDissipationLatentFraction uom="unit interval">0.2</nrg3:heatDissipationLatentFraction>
							<nrg3:heatDissipationRadiantFraction uom="unit interval">0.5</nrg3:heatDissipationRadiantFraction>
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
		<bldg:Building gml:id="house3_lod2_hull">
			<gml:description>The same house whose thermal zone coincides with the LoD2 hull of the building.</gml:description>
			<gml:name>Report house - LoD2 hull</gml:name>
			<core:creationDate>2024-09-25</core:creationDate>
			<nrg3:referencePoint>
				<gml:Point srsName="EPSG:32633" srsDimension="3">
					<gml:pos>291345.0000 5041905.0000 4.5000</gml:pos>
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
							<gml:surfaceMember xlink:href="#fx7_id_building_1_polygon_cs1"/>
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
					<nrg3:bdgBdrySurfHeatCapacity uom="kJ/(m^2*K)">508</nrg3:bdgBdrySurfHeatCapacity>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">30.9638</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfOpaqueSurfaceArea>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfThickness uom="mm">365</nrg3:bdgBdrySurfThickness>
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
				<bldg:WallSurface gml:id="fx7_id_building_1_wallsurface_4">
					<gml:description>This is WallSurface 4 (Building 1)</gml:description>
					<gml:name>WallSurface 4 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291345.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx7_id_building_1_wallsurface_4_lod2_geom" srsName="EPSG:32633" srsDimension="3">
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
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:address>
				<core:Address gml:id="fx7_id_address_1">
					<core:xalAddress>
						<ns5:AddressDetails>
							<ns5:Country>
								<ns5:CountryNameCode>ALD</ns5:CountryNameCode>
								<ns5:CountryName>Bespin Territories</ns5:CountryName>
								<ns5:Locality Type="Town">
									<ns5:LocalityName>Alderaan</ns5:LocalityName>
									<ns5:Thoroughfare Type="Street">
										<ns5:ThoroughfareNumber>1</ns5:ThoroughfareNumber>
										<ns5:ThoroughfareName>Bespin Square</ns5:ThoroughfareName>
									</ns5:Thoroughfare>
									<ns5:PostalCode>
										<ns5:PostalCodeNumber>1977SW</ns5:PostalCodeNumber>
									</ns5:PostalCode>
								</ns5:Locality>
							</ns5:Country>
						</ns5:AddressDetails>
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
			<nrg3:bdgType codeSpace="bdgType_codeSpace">singleFamilyHouse</nrg3:bdgType>
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
							<nrg3:value uom="m^2">180</nrg3:value>
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
							<nrg3:value uom="m^3">486</nrg3:value>
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
									<gml:surfaceMember xlink:href="#fx7_id_building_1_polygon_cs1"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:heatCapacity uom="J/K">46800000</nrg3:heatCapacity>
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
					<nrg3:internalHeatGains uom="W/m^2">1.4</nrg3:internalHeatGains>
					<nrg3:internalHeatGainsConvectiveFraction uom="unit interval">0.3</nrg3:internalHeatGainsConvectiveFraction>
					<nrg3:internalHeatGainsLatentFraction uom="unit interval">0.2</nrg3:internalHeatGainsLatentFraction>
					<nrg3:internalHeatGainsRadiantFraction uom="unit interval">0.5</nrg3:internalHeatGainsRadiantFraction>
					<nrg3:occupiedBy>
						<nrg3:Occupants gml:id="fx7_id_occupants_1">
							<gml:description>This is Occupants 1</gml:description>
							<gml:name>Occupants 1</gml:name>
							<nrg3:type codeSpace="occ_codeSpace_xyz">residents</nrg3:type>
							<nrg3:numberOfOccupants>4</nrg3:numberOfOccupants>
							<nrg3:heatDissipation uom="W/m^2">0.7</nrg3:heatDissipation>
							<nrg3:heatDissipationConvectiveFraction uom="unit interval">0.3</nrg3:heatDissipationConvectiveFraction>
							<nrg3:heatDissipationLatentFraction uom="unit interval">0.2</nrg3:heatDissipationLatentFraction>
							<nrg3:heatDissipationRadiantFraction uom="unit interval">0.5</nrg3:heatDissipationRadiantFraction>
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
		<bldg:Building gml:id="house4_lod1">
			<gml:description>The same house as a LoD1 box: no windows, all LoD1 may say. Its thermal zone states one average U-value for the whole shell.</gml:description>
			<gml:name>Report house - LoD1</gml:name>
			<core:creationDate>2024-09-25</core:creationDate>
			<nrg3:referencePoint>
				<gml:Point srsName="EPSG:32633" srsDimension="3">
					<gml:pos>291365.0000 5041905.0000 3.0000</gml:pos>
				</gml:Point>
			</nrg3:referencePoint>
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
					<nrg3:heatCapacity uom="J/K">46800000</nrg3:heatCapacity>
					<nrg3:infiltrationRate uom="1/h">0.3</nrg3:infiltrationRate>
					<nrg3:isCooled>false</nrg3:isCooled>
					<nrg3:isHeated>true</nrg3:isHeated>
					<nrg3:coincidesWithLod2Hull>false</nrg3:coincidesWithLod2Hull>
					<nrg3:coincidesWithLod3Hull>false</nrg3:coincidesWithLod3Hull>
				</nrg3:ThermalZone>
			</nrg3:thermalZone>
		</bldg:Building>
	</core:cityObjectMember>
	<core:cityObjectMember>
		<bldg:Building gml:id="house5_lod2_ready_plant">
			<gml:description>The LoD2 house again, with one difference: it states its heating plant, a ready EuReCa heat pump of 6 kW.</gml:description>
			<gml:name>Report house - LoD2, ready plant</gml:name>
			<core:creationDate>2024-09-25</core:creationDate>
			<nrg3:referencePoint>
				<gml:Point srsName="EPSG:32633" srsDimension="3">
					<gml:pos>291385.0000 5041905.0000 4.5000</gml:pos>
				</gml:Point>
			</nrg3:referencePoint>
			<nrg3:device>
				<nrg3:HeatPump gml:id="house5_lod2_ready_plant_heat_pump">
					<gml:description>A test device: the plant of this house, read from the file instead of the run file.</gml:description>
					<gml:name>Heat pump (test device)</gml:name>
					<gml:name codeSpace="urn:eureca:heating-system">A-W Heat Pump, Centralized, Low Temp Radiator</gml:name>
					<core:creationDate>2026-10-03</core:creationDate>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291391.0000 5041905.0000 0.5000</gml:pos>
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
						<nrg3:DeviceOperation gml:id="house5_lod2_ready_plant_heat_pump_operation">
							<nrg3:type>spaceHeating</nrg3:type>
							<nrg3:yearlyGlobalEfficiency>2.6</nrg3:yearlyGlobalEfficiency>
						</nrg3:DeviceOperation>
					</nrg3:deviceOperation>
					<nrg3:heatSource>ambientAir</nrg3:heatSource>
					<nrg3:copSourceTemperature uom="degrees Celsius">7</nrg3:copSourceTemperature>
					<nrg3:copOperationTemperature uom="degrees Celsius">35</nrg3:copOperationTemperature>
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
				<gml:MultiSurface gml:id="fx5_id_building_1_footprint_MultiSurf" srsName="EPSG:32633" srsDimension="3">
					<gml:surfaceMember>
						<gml:OrientableSurface orientation="-">
							<gml:baseSurface xlink:href="#fx5_id_building_1_polygon_3"/>
						</gml:OrientableSurface>
					</gml:surfaceMember>
				</gml:MultiSurface>
			</bldg:lod0FootPrint>
			<bldg:lod1Solid>
				<gml:Solid gml:id="fx5_id_building_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
					<gml:exterior>
						<gml:CompositeSurface gml:id="fx5_id_building_1_lod1_CompSurf">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx5_id_building_1_lod1_Polygon_1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291380.0000 5041900.0000 0.0000 291380.0000 5041910.0000 0.0000 291390.0000 5041910.0000 0.0000 291390.0000 5041900.0000 0.0000 291380.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx5_id_building_1_lod1_Polygon_2">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291380.0000 5041900.0000 0.0000 291390.0000 5041900.0000 0.0000 291390.0000 5041900.0000 7.5000 291380.0000 5041900.0000 7.5000 291380.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx5_id_building_1_lod1_Polygon_3">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291390.0000 5041900.0000 0.0000 291390.0000 5041910.0000 0.0000 291390.0000 5041910.0000 7.5000 291390.0000 5041900.0000 7.5000 291390.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx5_id_building_1_lod1_Polygon_4">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291390.0000 5041910.0000 0.0000 291380.0000 5041910.0000 0.0000 291380.0000 5041910.0000 7.5000 291390.0000 5041910.0000 7.5000 291390.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx5_id_building_1_lod1_Polygon_5">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291380.0000 5041910.0000 0.0000 291380.0000 5041900.0000 0.0000 291380.0000 5041900.0000 7.5000 291380.0000 5041910.0000 7.5000 291380.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx5_id_building_1_lod1_Polygon_6">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291380.0000 5041900.0000 7.5000 291390.0000 5041900.0000 7.5000 291390.0000 5041910.0000 7.5000 291380.0000 5041910.0000 7.5000 291380.0000 5041900.0000 7.5000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:CompositeSurface>
					</gml:exterior>
				</gml:Solid>
			</bldg:lod1Solid>
			<bldg:lod2Solid>
				<gml:Solid gml:id="fx5_id_building_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
					<gml:exterior>
						<gml:CompositeSurface gml:id="fx5_id_building_1_lod2_CompSurf">
							<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_4"/>
							<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_5"/>
							<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_7"/>
							<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_1"/>
							<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_2"/>
							<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_3"/>
							<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_cs1"/>
						</gml:CompositeSurface>
					</gml:exterior>
				</gml:Solid>
			</bldg:lod2Solid>
			<bldg:boundedBy>
				<bldg:GroundSurface gml:id="fx5_id_building_1_groundsurface_1">
					<gml:description>This is GroundSurface 1 (Building 1)</gml:description>
					<gml:name>GroundSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_ground_1"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291385.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx5_id_building_1_groundsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx5_id_building_1_polygon_3">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291380.0000 5041900.0000 0.0000 291380.0000 5041910.0000 0.0000 291390.0000 5041910.0000 0.0000 291390.0000 5041900.0000 0.0000 291380.0000 5041900.0000 0.0000</gml:posList>
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
				<bldg:RoofSurface gml:id="fx5_id_building_1_roofsurface_1">
					<gml:description>This is RoofSurface 1 (Building 1)</gml:description>
					<gml:name>RoofSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291385.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx5_id_building_1_roofsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx5_id_building_1_polygon_1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291380.0000 5041900.0000 6.0000 291385.0000 5041900.0000 9.0000 291385.0000 5041910.0000 9.0000 291380.0000 5041910.0000 6.0000 291380.0000 5041900.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">270</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfHeatCapacity uom="kJ/(m^2*K)">508</nrg3:bdgBdrySurfHeatCapacity>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">30.9638</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfOpaqueSurfaceArea>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfThickness uom="mm">365</nrg3:bdgBdrySurfThickness>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:RoofSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:RoofSurface gml:id="fx5_id_building_1_roofsurface_2">
					<gml:description>This is RoofSurface 2 (Building 1)</gml:description>
					<gml:name>RoofSurface 2 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291385.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx5_id_building_1_roofsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx5_id_building_1_polygon_2">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291385.0000 5041900.0000 9.0000 291390.0000 5041900.0000 6.0000 291390.0000 5041910.0000 6.0000 291385.0000 5041910.0000 9.0000 291385.0000 5041900.0000 9.0000</gml:posList>
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
				<bldg:WallSurface gml:id="fx5_id_building_1_wallsurface_1">
					<gml:description>This is WallSurface 1 (Building 1)</gml:description>
					<gml:name>WallSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291385.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx5_id_building_1_wallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx5_id_building_1_polygon_5">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291380.0000 5041900.0000 0.0000 291390.0000 5041900.0000 0.0000 291390.0000 5041900.0000 6.0000 291385.0000 5041900.0000 9.0000 291380.0000 5041900.0000 6.0000 291380.0000 5041900.0000 0.0000</gml:posList>
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
				<bldg:WallSurface gml:id="fx5_id_building_1_wallsurface_2">
					<gml:description>This is WallSurface 2 (Building 1)</gml:description>
					<gml:name>WallSurface 2 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291385.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx5_id_building_1_wallsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx5_id_building_1_polygon_4">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291380.0000 5041910.0000 0.0000 291380.0000 5041910.0000 6.0000 291385.0000 5041910.0000 9.0000 291390.0000 5041910.0000 6.0000 291390.0000 5041910.0000 0.0000 291380.0000 5041910.0000 0.0000</gml:posList>
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
				<bldg:WallSurface gml:id="fx5_id_building_1_wallsurface_3">
					<gml:description>This is WallSurface 3 (Building 1)</gml:description>
					<gml:name>WallSurface 3 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291385.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx5_id_building_1_wallsurface_3_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx5_id_building_1_polygon_7">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291380.0000 5041900.0000 0.0000 291380.0000 5041900.0000 6.0000 291380.0000 5041910.0000 6.0000 291380.0000 5041910.0000 0.0000 291380.0000 5041900.0000 0.0000</gml:posList>
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
				<bldg:WallSurface gml:id="fx5_id_building_1_wallsurface_4">
					<gml:description>This is WallSurface 4 (Building 1)</gml:description>
					<gml:name>WallSurface 4 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291385.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx5_id_building_1_wallsurface_4_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx5_id_building_1_polygon_cs1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291390.0000 5041910.0000 6.0000 291390.0000 5041900.0000 6.0000 291390.0000 5041900.0000 0.0000 291390.0000 5041910.0000 0.0000 291390.0000 5041910.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:address>
				<core:Address gml:id="fx5_id_address_1">
					<core:xalAddress>
						<ns5:AddressDetails>
							<ns5:Country>
								<ns5:CountryNameCode>ALD</ns5:CountryNameCode>
								<ns5:CountryName>Bespin Territories</ns5:CountryName>
								<ns5:Locality Type="Town">
									<ns5:LocalityName>Alderaan</ns5:LocalityName>
									<ns5:Thoroughfare Type="Street">
										<ns5:ThoroughfareNumber>1</ns5:ThoroughfareNumber>
										<ns5:ThoroughfareName>Bespin Square</ns5:ThoroughfareName>
									</ns5:Thoroughfare>
									<ns5:PostalCode>
										<ns5:PostalCodeNumber>1977SW</ns5:PostalCodeNumber>
									</ns5:PostalCode>
								</ns5:Locality>
							</ns5:Country>
						</ns5:AddressDetails>
					</core:xalAddress>
					<core:multiPoint>
						<gml:MultiPoint srsName="EPSG:32633" srsDimension="3">
							<gml:pointMember>
								<gml:Point>
									<gml:pos>291385.0000 5041905.0000 0.0000</gml:pos>
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
			<nrg3:bdgType codeSpace="bdgType_codeSpace">singleFamilyHouse</nrg3:bdgType>
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
				<nrg3:BuildingUnit gml:id="fx5_id_building_unit_1">
					<gml:description>This is BuildingUnit 1</gml:description>
					<gml:name>BuildingUnit 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291385.0000 5041905.0000 4.5000</gml:pos>
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
							<nrg3:value uom="m^2">180</nrg3:value>
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
							<nrg3:value uom="m^3">486</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">energyReferenceVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:lod1Solid>
						<gml:Solid gml:id="fx5_id_building_unit_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx5_id_building_unit_1_lod1_CompSurf">
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_42e7489a-e3f6-4a45-be2a-fbe735cd2ef8"/>
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_3f00920e-17c2-41f1-acb7-e223b1199044"/>
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_ba78c9d7-0ed7-49b8-b107-d939f0186284"/>
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_1406dd4c-f070-4022-835b-50018fdc6c54"/>
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_694c7871-d386-4e68-9c88-f62140080992"/>
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_945a1c0f-31f2-4bad-9599-9aaecf0ac7ac"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="fx5_id_building_unit_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx5_id_building_unit_1_lod2_CompSurf">
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_6e3e783e-b75a-4436-9f49-ed7d5346bca0"/>
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_ed5e64ff-65d6-4da8-bd65-a726d53494fa"/>
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_b7a25cfb-c3c6-490c-8628-42c50627d42c"/>
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_204ef154-fa62-4200-b3f2-4bb427b7b42e"/>
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_1f26fb83-a013-4528-9b75-b7eed4d07b70"/>
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_0f7e6a7d-4c78-4f23-a531-482e254f1aae"/>
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_8c107b31-166a-4b7c-aec1-4800b9dd396c"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:lod3Solid>
						<gml:Solid gml:id="fx5_id_building_unit_1_lod3_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx5_id_building_unit_1_lod3_CompSurf">
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_b9c018da-8461-4762-99c2-1cae1fc6dfa2"/>
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_efca560a-2e79-4536-9e21-4e23aacef253"/>
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_80ecaada-e49a-4e7d-8955-367405f503fb"/>
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_4dbfd338-5c11-42cd-b60d-68038c5dc78f"/>
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_5103fb6c-6d3f-4756-aa3a-586039a1938f"/>
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_2d5f403b-eac9-46ff-abbe-579c1416747a"/>
									<gml:surfaceMember xlink:href="#fx5_Polygon_UUID_934e4b6a-022d-4cf7-8426-883da175edd4"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod3Solid>
					<nrg3:type codeSpace="buildingUnit_codeSpace_123">residential</nrg3:type>
					<nrg3:numberOfRooms>4</nrg3:numberOfRooms>
					<nrg3:ownershipType codeSpace="ownership_type_codeSpace_abc">corporation</nrg3:ownershipType>
					<nrg3:address xlink:href="#fx5_id_address_1"/>
				</nrg3:BuildingUnit>
			</nrg3:buildingUnit>
			<nrg3:thermalZone>
				<nrg3:ThermalZone gml:id="fx5_id_thermal_zone_1">
					<gml:description>This is ThermalZone 1</gml:description>
					<gml:name>ThermalZone 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291385.0000 5041905.0000 4.5000</gml:pos>
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
						<gml:Solid gml:id="fx5_id_thermal_zone_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx5_id_thermal_zone_1_lod1_CompSurf">
									<gml:surfaceMember xlink:href="#fx5_id_building_1_lod1_Polygon_1"/>
									<gml:surfaceMember xlink:href="#fx5_id_building_1_lod1_Polygon_2"/>
									<gml:surfaceMember xlink:href="#fx5_id_building_1_lod1_Polygon_3"/>
									<gml:surfaceMember xlink:href="#fx5_id_building_1_lod1_Polygon_4"/>
									<gml:surfaceMember xlink:href="#fx5_id_building_1_lod1_Polygon_5"/>
									<gml:surfaceMember xlink:href="#fx5_id_building_1_lod1_Polygon_6"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="fx5_id_thermal_zone_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx5_id_thermal_zone_1_lod2_CompSurf">
									<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_4"/>
									<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_5"/>
									<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_7"/>
									<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_1"/>
									<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_2"/>
									<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_3"/>
									<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_cs1"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:heatCapacity uom="J/K">46800000</nrg3:heatCapacity>
					<nrg3:infiltrationRate uom="1/h">0.3</nrg3:infiltrationRate>
					<nrg3:isCooled>false</nrg3:isCooled>
					<nrg3:isHeated>true</nrg3:isHeated>
					<nrg3:coincidesWithLod2Hull>false</nrg3:coincidesWithLod2Hull>
					<nrg3:coincidesWithLod3Hull>false</nrg3:coincidesWithLod3Hull>
					<nrg3:thermalBoundary>
						<bldg:GroundSurface gml:id="fx5_id_thermal_zone_1_groundsurface_1">
							<gml:description>This is (ThermalBoundary) GroundSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) GroundSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_ground_1"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291385.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx5_id_thermal_zone_1_groundsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_3"/>
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
						<bldg:RoofSurface gml:id="fx5_id_thermal_zone_1_roofsurface_1">
							<gml:description>This is (ThermalBoundary) RoofSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) RoofSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291385.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx5_id_thermal_zone_1_roofsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_1"/>
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
						<bldg:RoofSurface gml:id="fx5_id_thermal_zone_1_roofsurface_2">
							<gml:description>This is (ThermalBoundary) RoofSurface 2 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) RoofSurface 2 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291385.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx5_id_thermal_zone_1_roofsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_2"/>
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
						<bldg:WallSurface gml:id="fx5_id_thermal_zone_1_wallsurface_1">
							<gml:description>This is (ThermalBoundary) WallSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291385.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx5_id_thermal_zone_1_wallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_5"/>
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
						<bldg:WallSurface gml:id="fx5_id_thermal_zone_1_wallsurface_2">
							<gml:description>This is (ThermalBoundary) WallSurface 2 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 2 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291385.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx5_id_thermal_zone_1_wallsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_4"/>
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
						<bldg:WallSurface gml:id="fx5_id_thermal_zone_1_wallsurface_3">
							<gml:description>This is (ThermalBoundary) WallSurface 3 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 3 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291385.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx5_id_thermal_zone_1_wallsurface_3_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_7"/>
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
						<bldg:WallSurface gml:id="fx5_id_thermal_zone_1_wallsurface_4">
							<gml:description>This is (ThermalBoundary) WallSurface 4 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 4 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291385.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx5_id_thermal_zone_1_wallsurface_4_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx5_id_building_1_polygon_cs1"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
					</nrg3:thermalBoundary>
				</nrg3:ThermalZone>
			</nrg3:thermalZone>
			<nrg3:usageZone>
				<nrg3:UsageZone gml:id="fx5_id_usage_zone_1">
					<gml:description>This is UsageZone 1</gml:description>
					<gml:name>UsageZone 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291385.0000 5041905.0000 4.5000</gml:pos>
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
							<nrg3:type codeSpace="volume_codeSpace">energyReferenceVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:lod1Solid>
						<gml:Solid gml:id="fx5_id_usage_zone_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx5_id_usage_zone_1_lod1_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_42e7489a-e3f6-4a45-be2a-fbe735cd2ef8">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291380.0000 5041900.0000 0.0000 291380.0000 5041910.0000 0.0000 291390.0000 5041910.0000 0.0000 291390.0000 5041900.0000 0.0000 291380.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_3f00920e-17c2-41f1-acb7-e223b1199044">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291380.0000 5041900.0000 0.0000 291390.0000 5041900.0000 0.0000 291390.0000 5041900.0000 7.5000 291380.0000 5041900.0000 7.5000 291380.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_ba78c9d7-0ed7-49b8-b107-d939f0186284">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291390.0000 5041900.0000 0.0000 291390.0000 5041910.0000 0.0000 291390.0000 5041910.0000 7.5000 291390.0000 5041900.0000 7.5000 291390.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_1406dd4c-f070-4022-835b-50018fdc6c54">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291390.0000 5041910.0000 0.0000 291380.0000 5041910.0000 0.0000 291380.0000 5041910.0000 7.5000 291390.0000 5041910.0000 7.5000 291390.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_694c7871-d386-4e68-9c88-f62140080992">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291380.0000 5041910.0000 0.0000 291380.0000 5041900.0000 0.0000 291380.0000 5041900.0000 7.5000 291380.0000 5041910.0000 7.5000 291380.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_945a1c0f-31f2-4bad-9599-9aaecf0ac7ac">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291380.0000 5041900.0000 7.5000 291390.0000 5041900.0000 7.5000 291390.0000 5041910.0000 7.5000 291380.0000 5041910.0000 7.5000 291380.0000 5041900.0000 7.5000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="fx5_id_usage_zone_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx5_id_usage_zone_1_lod2_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_b9c018da-8461-4762-99c2-1cae1fc6dfa2">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291380.0000 5041910.0000 0.0000 291380.0000 5041910.0000 6.0000 291385.0000 5041910.0000 9.0000 291390.0000 5041910.0000 6.0000 291390.0000 5041910.0000 0.0000 291380.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_efca560a-2e79-4536-9e21-4e23aacef253">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291380.0000 5041900.0000 0.0000 291390.0000 5041900.0000 0.0000 291390.0000 5041900.0000 6.0000 291385.0000 5041900.0000 9.0000 291380.0000 5041900.0000 6.0000 291380.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_80ecaada-e49a-4e7d-8955-367405f503fb">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291380.0000 5041900.0000 0.0000 291380.0000 5041900.0000 6.0000 291380.0000 5041910.0000 6.0000 291380.0000 5041910.0000 0.0000 291380.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_4dbfd338-5c11-42cd-b60d-68038c5dc78f">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291380.0000 5041900.0000 6.0000 291385.0000 5041900.0000 9.0000 291385.0000 5041910.0000 9.0000 291380.0000 5041910.0000 6.0000 291380.0000 5041900.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_5103fb6c-6d3f-4756-aa3a-586039a1938f">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291385.0000 5041900.0000 9.0000 291390.0000 5041900.0000 6.0000 291390.0000 5041910.0000 6.0000 291385.0000 5041910.0000 9.0000 291385.0000 5041900.0000 9.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_2d5f403b-eac9-46ff-abbe-579c1416747a">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291380.0000 5041900.0000 0.0000 291380.0000 5041910.0000 0.0000 291390.0000 5041910.0000 0.0000 291390.0000 5041900.0000 0.0000 291380.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_934e4b6a-022d-4cf7-8426-883da175edd4">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291390.0000 5041910.0000 6.0000 291390.0000 5041900.0000 6.0000 291390.0000 5041900.0000 0.0000 291390.0000 5041910.0000 0.0000 291390.0000 5041910.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:lod3Solid>
						<gml:Solid gml:id="fx5_id_usage_zone_1_lod3_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx5_id_usage_zone_1_lod3_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_6e3e783e-b75a-4436-9f49-ed7d5346bca0">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291380.0000 5041910.0000 0.0000 291380.0000 5041910.0000 6.0000 291385.0000 5041910.0000 9.0000 291390.0000 5041910.0000 6.0000 291390.0000 5041910.0000 0.0000 291380.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_ed5e64ff-65d6-4da8-bd65-a726d53494fa">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291380.0000 5041900.0000 0.0000 291390.0000 5041900.0000 0.0000 291390.0000 5041900.0000 6.0000 291385.0000 5041900.0000 9.0000 291380.0000 5041900.0000 6.0000 291380.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_b7a25cfb-c3c6-490c-8628-42c50627d42c">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291380.0000 5041900.0000 0.0000 291380.0000 5041900.0000 6.0000 291380.0000 5041910.0000 6.0000 291380.0000 5041910.0000 0.0000 291380.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_204ef154-fa62-4200-b3f2-4bb427b7b42e">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291380.0000 5041900.0000 6.0000 291385.0000 5041900.0000 9.0000 291385.0000 5041910.0000 9.0000 291380.0000 5041910.0000 6.0000 291380.0000 5041900.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_1f26fb83-a013-4528-9b75-b7eed4d07b70">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291385.0000 5041900.0000 9.0000 291390.0000 5041900.0000 6.0000 291390.0000 5041910.0000 6.0000 291385.0000 5041910.0000 9.0000 291385.0000 5041900.0000 9.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_0f7e6a7d-4c78-4f23-a531-482e254f1aae">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291380.0000 5041900.0000 0.0000 291380.0000 5041910.0000 0.0000 291390.0000 5041910.0000 0.0000 291390.0000 5041900.0000 0.0000 291380.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx5_Polygon_UUID_8c107b31-166a-4b7c-aec1-4800b9dd396c">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291390.0000 5041910.0000 6.0000 291390.0000 5041900.0000 6.0000 291390.0000 5041900.0000 0.0000 291390.0000 5041910.0000 0.0000 291390.0000 5041910.0000 6.0000</gml:posList>
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
					<nrg3:internalHeatGains uom="W/m^2">1.4</nrg3:internalHeatGains>
					<nrg3:internalHeatGainsConvectiveFraction uom="unit interval">0.3</nrg3:internalHeatGainsConvectiveFraction>
					<nrg3:internalHeatGainsLatentFraction uom="unit interval">0.2</nrg3:internalHeatGainsLatentFraction>
					<nrg3:internalHeatGainsRadiantFraction uom="unit interval">0.5</nrg3:internalHeatGainsRadiantFraction>
					<nrg3:occupiedBy>
						<nrg3:Occupants gml:id="fx5_id_occupants_1">
							<gml:description>This is Occupants 1</gml:description>
							<gml:name>Occupants 1</gml:name>
							<nrg3:type codeSpace="occ_codeSpace_xyz">residents</nrg3:type>
							<nrg3:numberOfOccupants>4</nrg3:numberOfOccupants>
							<nrg3:heatDissipation uom="W/m^2">0.7</nrg3:heatDissipation>
							<nrg3:heatDissipationConvectiveFraction uom="unit interval">0.3</nrg3:heatDissipationConvectiveFraction>
							<nrg3:heatDissipationLatentFraction uom="unit interval">0.2</nrg3:heatDissipationLatentFraction>
							<nrg3:heatDissipationRadiantFraction uom="unit interval">0.5</nrg3:heatDissipationRadiantFraction>
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
		<bldg:Building gml:id="house6_lod2_own_plant">
			<gml:description>The LoD2 house again, with one difference: it states its plant by its own values, a gas boiler of 15 kW and a chiller of 10 kW.</gml:description>
			<gml:name>Report house - LoD2, own plant</gml:name>
			<core:creationDate>2024-09-25</core:creationDate>
			<nrg3:referencePoint>
				<gml:Point srsName="EPSG:32633" srsDimension="3">
					<gml:pos>291405.0000 5041905.0000 4.5000</gml:pos>
				</gml:Point>
			</nrg3:referencePoint>
			<nrg3:device>
				<nrg3:Boiler gml:id="house6_lod2_own_plant_boiler">
					<gml:description>A test device: a heating plant described by its own values (EuReCa's "From manual parameters"), read from the file instead of the run file.</gml:description>
					<gml:name>Own gas boiler (test device)</gml:name>
					<gml:name codeSpace="urn:eureca:heating-system">From manual parameters</gml:name>
					<core:creationDate>2026-10-03</core:creationDate>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291405.0000 5041905.0000 1.0000</gml:pos>
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
						<nrg3:DeviceOperation gml:id="house6_lod2_own_plant_boiler_heating">
							<nrg3:type>spaceHeating</nrg3:type>
							<nrg3:yearlyGlobalEfficiency>0.8</nrg3:yearlyGlobalEfficiency>
						</nrg3:DeviceOperation>
					</nrg3:deviceOperation>
					<nrg3:deviceOperation>
						<nrg3:DeviceOperation gml:id="house6_lod2_own_plant_boiler_hot_water">
							<nrg3:type>domesticHotWater</nrg3:type>
							<nrg3:yearlyGlobalEfficiency>0.8</nrg3:yearlyGlobalEfficiency>
						</nrg3:DeviceOperation>
					</nrg3:deviceOperation>
					<nrg3:hasCondensation>true</nrg3:hasCondensation>
				</nrg3:Boiler>
			</nrg3:device>
			<nrg3:device>
				<nrg3:HeatPump gml:id="house6_lod2_own_plant_chiller">
					<gml:description>A test device: a cooling plant described by its own values (EuReCa's "From manual parameters"), read from the file instead of the run file.</gml:description>
					<gml:name>Own chiller (test device)</gml:name>
					<gml:name codeSpace="urn:eureca:cooling-system">From manual parameters</gml:name>
					<core:creationDate>2026-10-03</core:creationDate>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291411.0000 5041905.0000 0.5000</gml:pos>
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
						<nrg3:DeviceOperation gml:id="house6_lod2_own_plant_chiller_cooling">
							<nrg3:type>spaceCooling</nrg3:type>
							<nrg3:yearlyGlobalEfficiency>1.96</nrg3:yearlyGlobalEfficiency>
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
				<gml:MultiSurface gml:id="fx6_id_building_1_footprint_MultiSurf" srsName="EPSG:32633" srsDimension="3">
					<gml:surfaceMember>
						<gml:OrientableSurface orientation="-">
							<gml:baseSurface xlink:href="#fx6_id_building_1_polygon_3"/>
						</gml:OrientableSurface>
					</gml:surfaceMember>
				</gml:MultiSurface>
			</bldg:lod0FootPrint>
			<bldg:lod1Solid>
				<gml:Solid gml:id="fx6_id_building_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
					<gml:exterior>
						<gml:CompositeSurface gml:id="fx6_id_building_1_lod1_CompSurf">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx6_id_building_1_lod1_Polygon_1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291400.0000 5041900.0000 0.0000 291400.0000 5041910.0000 0.0000 291410.0000 5041910.0000 0.0000 291410.0000 5041900.0000 0.0000 291400.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx6_id_building_1_lod1_Polygon_2">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291400.0000 5041900.0000 0.0000 291410.0000 5041900.0000 0.0000 291410.0000 5041900.0000 7.5000 291400.0000 5041900.0000 7.5000 291400.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx6_id_building_1_lod1_Polygon_3">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291410.0000 5041900.0000 0.0000 291410.0000 5041910.0000 0.0000 291410.0000 5041910.0000 7.5000 291410.0000 5041900.0000 7.5000 291410.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx6_id_building_1_lod1_Polygon_4">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291410.0000 5041910.0000 0.0000 291400.0000 5041910.0000 0.0000 291400.0000 5041910.0000 7.5000 291410.0000 5041910.0000 7.5000 291410.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx6_id_building_1_lod1_Polygon_5">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291400.0000 5041910.0000 0.0000 291400.0000 5041900.0000 0.0000 291400.0000 5041900.0000 7.5000 291400.0000 5041910.0000 7.5000 291400.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx6_id_building_1_lod1_Polygon_6">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291400.0000 5041900.0000 7.5000 291410.0000 5041900.0000 7.5000 291410.0000 5041910.0000 7.5000 291400.0000 5041910.0000 7.5000 291400.0000 5041900.0000 7.5000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:CompositeSurface>
					</gml:exterior>
				</gml:Solid>
			</bldg:lod1Solid>
			<bldg:lod2Solid>
				<gml:Solid gml:id="fx6_id_building_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
					<gml:exterior>
						<gml:CompositeSurface gml:id="fx6_id_building_1_lod2_CompSurf">
							<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_4"/>
							<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_5"/>
							<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_7"/>
							<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_1"/>
							<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_2"/>
							<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_3"/>
							<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_cs1"/>
						</gml:CompositeSurface>
					</gml:exterior>
				</gml:Solid>
			</bldg:lod2Solid>
			<bldg:boundedBy>
				<bldg:GroundSurface gml:id="fx6_id_building_1_groundsurface_1">
					<gml:description>This is GroundSurface 1 (Building 1)</gml:description>
					<gml:name>GroundSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_ground_1"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291405.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx6_id_building_1_groundsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx6_id_building_1_polygon_3">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291400.0000 5041900.0000 0.0000 291400.0000 5041910.0000 0.0000 291410.0000 5041910.0000 0.0000 291410.0000 5041900.0000 0.0000 291400.0000 5041900.0000 0.0000</gml:posList>
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
				<bldg:RoofSurface gml:id="fx6_id_building_1_roofsurface_1">
					<gml:description>This is RoofSurface 1 (Building 1)</gml:description>
					<gml:name>RoofSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291405.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx6_id_building_1_roofsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx6_id_building_1_polygon_1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291400.0000 5041900.0000 6.0000 291405.0000 5041900.0000 9.0000 291405.0000 5041910.0000 9.0000 291400.0000 5041910.0000 6.0000 291400.0000 5041900.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">270</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfHeatCapacity uom="kJ/(m^2*K)">508</nrg3:bdgBdrySurfHeatCapacity>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">30.9638</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfOpaqueSurfaceArea>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfThickness uom="mm">365</nrg3:bdgBdrySurfThickness>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:RoofSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:RoofSurface gml:id="fx6_id_building_1_roofsurface_2">
					<gml:description>This is RoofSurface 2 (Building 1)</gml:description>
					<gml:name>RoofSurface 2 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291405.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx6_id_building_1_roofsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx6_id_building_1_polygon_2">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291405.0000 5041900.0000 9.0000 291410.0000 5041900.0000 6.0000 291410.0000 5041910.0000 6.0000 291405.0000 5041910.0000 9.0000 291405.0000 5041900.0000 9.0000</gml:posList>
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
				<bldg:WallSurface gml:id="fx6_id_building_1_wallsurface_1">
					<gml:description>This is WallSurface 1 (Building 1)</gml:description>
					<gml:name>WallSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291405.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx6_id_building_1_wallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx6_id_building_1_polygon_5">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291400.0000 5041900.0000 0.0000 291410.0000 5041900.0000 0.0000 291410.0000 5041900.0000 6.0000 291405.0000 5041900.0000 9.0000 291400.0000 5041900.0000 6.0000 291400.0000 5041900.0000 0.0000</gml:posList>
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
				<bldg:WallSurface gml:id="fx6_id_building_1_wallsurface_2">
					<gml:description>This is WallSurface 2 (Building 1)</gml:description>
					<gml:name>WallSurface 2 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291405.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx6_id_building_1_wallsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx6_id_building_1_polygon_4">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291400.0000 5041910.0000 0.0000 291400.0000 5041910.0000 6.0000 291405.0000 5041910.0000 9.0000 291410.0000 5041910.0000 6.0000 291410.0000 5041910.0000 0.0000 291400.0000 5041910.0000 0.0000</gml:posList>
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
				<bldg:WallSurface gml:id="fx6_id_building_1_wallsurface_3">
					<gml:description>This is WallSurface 3 (Building 1)</gml:description>
					<gml:name>WallSurface 3 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291405.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx6_id_building_1_wallsurface_3_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx6_id_building_1_polygon_7">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291400.0000 5041900.0000 0.0000 291400.0000 5041900.0000 6.0000 291400.0000 5041910.0000 6.0000 291400.0000 5041910.0000 0.0000 291400.0000 5041900.0000 0.0000</gml:posList>
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
				<bldg:WallSurface gml:id="fx6_id_building_1_wallsurface_4">
					<gml:description>This is WallSurface 4 (Building 1)</gml:description>
					<gml:name>WallSurface 4 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291405.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="fx6_id_building_1_wallsurface_4_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="fx6_id_building_1_polygon_cs1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291410.0000 5041910.0000 6.0000 291410.0000 5041900.0000 6.0000 291410.0000 5041900.0000 0.0000 291410.0000 5041910.0000 0.0000 291410.0000 5041910.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:address>
				<core:Address gml:id="fx6_id_address_1">
					<core:xalAddress>
						<ns5:AddressDetails>
							<ns5:Country>
								<ns5:CountryNameCode>ALD</ns5:CountryNameCode>
								<ns5:CountryName>Bespin Territories</ns5:CountryName>
								<ns5:Locality Type="Town">
									<ns5:LocalityName>Alderaan</ns5:LocalityName>
									<ns5:Thoroughfare Type="Street">
										<ns5:ThoroughfareNumber>1</ns5:ThoroughfareNumber>
										<ns5:ThoroughfareName>Bespin Square</ns5:ThoroughfareName>
									</ns5:Thoroughfare>
									<ns5:PostalCode>
										<ns5:PostalCodeNumber>1977SW</ns5:PostalCodeNumber>
									</ns5:PostalCode>
								</ns5:Locality>
							</ns5:Country>
						</ns5:AddressDetails>
					</core:xalAddress>
					<core:multiPoint>
						<gml:MultiPoint srsName="EPSG:32633" srsDimension="3">
							<gml:pointMember>
								<gml:Point>
									<gml:pos>291405.0000 5041905.0000 0.0000</gml:pos>
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
			<nrg3:bdgType codeSpace="bdgType_codeSpace">singleFamilyHouse</nrg3:bdgType>
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
				<nrg3:BuildingUnit gml:id="fx6_id_building_unit_1">
					<gml:description>This is BuildingUnit 1</gml:description>
					<gml:name>BuildingUnit 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291405.0000 5041905.0000 4.5000</gml:pos>
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
							<nrg3:value uom="m^2">180</nrg3:value>
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
							<nrg3:value uom="m^3">486</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">energyReferenceVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:lod1Solid>
						<gml:Solid gml:id="fx6_id_building_unit_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx6_id_building_unit_1_lod1_CompSurf">
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_42e7489a-e3f6-4a45-be2a-fbe735cd2ef8"/>
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_3f00920e-17c2-41f1-acb7-e223b1199044"/>
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_ba78c9d7-0ed7-49b8-b107-d939f0186284"/>
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_1406dd4c-f070-4022-835b-50018fdc6c54"/>
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_694c7871-d386-4e68-9c88-f62140080992"/>
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_945a1c0f-31f2-4bad-9599-9aaecf0ac7ac"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="fx6_id_building_unit_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx6_id_building_unit_1_lod2_CompSurf">
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_6e3e783e-b75a-4436-9f49-ed7d5346bca0"/>
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_ed5e64ff-65d6-4da8-bd65-a726d53494fa"/>
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_b7a25cfb-c3c6-490c-8628-42c50627d42c"/>
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_204ef154-fa62-4200-b3f2-4bb427b7b42e"/>
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_1f26fb83-a013-4528-9b75-b7eed4d07b70"/>
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_0f7e6a7d-4c78-4f23-a531-482e254f1aae"/>
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_8c107b31-166a-4b7c-aec1-4800b9dd396c"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:lod3Solid>
						<gml:Solid gml:id="fx6_id_building_unit_1_lod3_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx6_id_building_unit_1_lod3_CompSurf">
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_b9c018da-8461-4762-99c2-1cae1fc6dfa2"/>
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_efca560a-2e79-4536-9e21-4e23aacef253"/>
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_80ecaada-e49a-4e7d-8955-367405f503fb"/>
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_4dbfd338-5c11-42cd-b60d-68038c5dc78f"/>
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_5103fb6c-6d3f-4756-aa3a-586039a1938f"/>
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_2d5f403b-eac9-46ff-abbe-579c1416747a"/>
									<gml:surfaceMember xlink:href="#fx6_Polygon_UUID_934e4b6a-022d-4cf7-8426-883da175edd4"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod3Solid>
					<nrg3:type codeSpace="buildingUnit_codeSpace_123">residential</nrg3:type>
					<nrg3:numberOfRooms>4</nrg3:numberOfRooms>
					<nrg3:ownershipType codeSpace="ownership_type_codeSpace_abc">corporation</nrg3:ownershipType>
					<nrg3:address xlink:href="#fx6_id_address_1"/>
				</nrg3:BuildingUnit>
			</nrg3:buildingUnit>
			<nrg3:thermalZone>
				<nrg3:ThermalZone gml:id="fx6_id_thermal_zone_1">
					<gml:description>This is ThermalZone 1</gml:description>
					<gml:name>ThermalZone 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291405.0000 5041905.0000 4.5000</gml:pos>
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
						<gml:Solid gml:id="fx6_id_thermal_zone_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx6_id_thermal_zone_1_lod1_CompSurf">
									<gml:surfaceMember xlink:href="#fx6_id_building_1_lod1_Polygon_1"/>
									<gml:surfaceMember xlink:href="#fx6_id_building_1_lod1_Polygon_2"/>
									<gml:surfaceMember xlink:href="#fx6_id_building_1_lod1_Polygon_3"/>
									<gml:surfaceMember xlink:href="#fx6_id_building_1_lod1_Polygon_4"/>
									<gml:surfaceMember xlink:href="#fx6_id_building_1_lod1_Polygon_5"/>
									<gml:surfaceMember xlink:href="#fx6_id_building_1_lod1_Polygon_6"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="fx6_id_thermal_zone_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx6_id_thermal_zone_1_lod2_CompSurf">
									<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_4"/>
									<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_5"/>
									<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_7"/>
									<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_1"/>
									<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_2"/>
									<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_3"/>
									<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_cs1"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:heatCapacity uom="J/K">46800000</nrg3:heatCapacity>
					<nrg3:infiltrationRate uom="1/h">0.3</nrg3:infiltrationRate>
					<nrg3:isCooled>false</nrg3:isCooled>
					<nrg3:isHeated>true</nrg3:isHeated>
					<nrg3:coincidesWithLod2Hull>false</nrg3:coincidesWithLod2Hull>
					<nrg3:coincidesWithLod3Hull>false</nrg3:coincidesWithLod3Hull>
					<nrg3:thermalBoundary>
						<bldg:GroundSurface gml:id="fx6_id_thermal_zone_1_groundsurface_1">
							<gml:description>This is (ThermalBoundary) GroundSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) GroundSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_ground_1"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291405.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx6_id_thermal_zone_1_groundsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_3"/>
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
						<bldg:RoofSurface gml:id="fx6_id_thermal_zone_1_roofsurface_1">
							<gml:description>This is (ThermalBoundary) RoofSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) RoofSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291405.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx6_id_thermal_zone_1_roofsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_1"/>
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
						<bldg:RoofSurface gml:id="fx6_id_thermal_zone_1_roofsurface_2">
							<gml:description>This is (ThermalBoundary) RoofSurface 2 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) RoofSurface 2 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291405.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx6_id_thermal_zone_1_roofsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_2"/>
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
						<bldg:WallSurface gml:id="fx6_id_thermal_zone_1_wallsurface_1">
							<gml:description>This is (ThermalBoundary) WallSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291405.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx6_id_thermal_zone_1_wallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_5"/>
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
						<bldg:WallSurface gml:id="fx6_id_thermal_zone_1_wallsurface_2">
							<gml:description>This is (ThermalBoundary) WallSurface 2 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 2 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291405.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx6_id_thermal_zone_1_wallsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_4"/>
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
						<bldg:WallSurface gml:id="fx6_id_thermal_zone_1_wallsurface_3">
							<gml:description>This is (ThermalBoundary) WallSurface 3 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 3 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291405.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx6_id_thermal_zone_1_wallsurface_3_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_7"/>
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
						<bldg:WallSurface gml:id="fx6_id_thermal_zone_1_wallsurface_4">
							<gml:description>This is (ThermalBoundary) WallSurface 4 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 4 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291405.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="fx6_id_thermal_zone_1_wallsurface_4_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#fx6_id_building_1_polygon_cs1"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
					</nrg3:thermalBoundary>
				</nrg3:ThermalZone>
			</nrg3:thermalZone>
			<nrg3:usageZone>
				<nrg3:UsageZone gml:id="fx6_id_usage_zone_1">
					<gml:description>This is UsageZone 1</gml:description>
					<gml:name>UsageZone 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291405.0000 5041905.0000 4.5000</gml:pos>
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
							<nrg3:type codeSpace="volume_codeSpace">energyReferenceVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:lod1Solid>
						<gml:Solid gml:id="fx6_id_usage_zone_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx6_id_usage_zone_1_lod1_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_42e7489a-e3f6-4a45-be2a-fbe735cd2ef8">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291400.0000 5041900.0000 0.0000 291400.0000 5041910.0000 0.0000 291410.0000 5041910.0000 0.0000 291410.0000 5041900.0000 0.0000 291400.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_3f00920e-17c2-41f1-acb7-e223b1199044">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291400.0000 5041900.0000 0.0000 291410.0000 5041900.0000 0.0000 291410.0000 5041900.0000 7.5000 291400.0000 5041900.0000 7.5000 291400.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_ba78c9d7-0ed7-49b8-b107-d939f0186284">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291410.0000 5041900.0000 0.0000 291410.0000 5041910.0000 0.0000 291410.0000 5041910.0000 7.5000 291410.0000 5041900.0000 7.5000 291410.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_1406dd4c-f070-4022-835b-50018fdc6c54">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291410.0000 5041910.0000 0.0000 291400.0000 5041910.0000 0.0000 291400.0000 5041910.0000 7.5000 291410.0000 5041910.0000 7.5000 291410.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_694c7871-d386-4e68-9c88-f62140080992">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291400.0000 5041910.0000 0.0000 291400.0000 5041900.0000 0.0000 291400.0000 5041900.0000 7.5000 291400.0000 5041910.0000 7.5000 291400.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_945a1c0f-31f2-4bad-9599-9aaecf0ac7ac">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291400.0000 5041900.0000 7.5000 291410.0000 5041900.0000 7.5000 291410.0000 5041910.0000 7.5000 291400.0000 5041910.0000 7.5000 291400.0000 5041900.0000 7.5000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="fx6_id_usage_zone_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx6_id_usage_zone_1_lod2_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_b9c018da-8461-4762-99c2-1cae1fc6dfa2">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291400.0000 5041910.0000 0.0000 291400.0000 5041910.0000 6.0000 291405.0000 5041910.0000 9.0000 291410.0000 5041910.0000 6.0000 291410.0000 5041910.0000 0.0000 291400.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_efca560a-2e79-4536-9e21-4e23aacef253">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291400.0000 5041900.0000 0.0000 291410.0000 5041900.0000 0.0000 291410.0000 5041900.0000 6.0000 291405.0000 5041900.0000 9.0000 291400.0000 5041900.0000 6.0000 291400.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_80ecaada-e49a-4e7d-8955-367405f503fb">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291400.0000 5041900.0000 0.0000 291400.0000 5041900.0000 6.0000 291400.0000 5041910.0000 6.0000 291400.0000 5041910.0000 0.0000 291400.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_4dbfd338-5c11-42cd-b60d-68038c5dc78f">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291400.0000 5041900.0000 6.0000 291405.0000 5041900.0000 9.0000 291405.0000 5041910.0000 9.0000 291400.0000 5041910.0000 6.0000 291400.0000 5041900.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_5103fb6c-6d3f-4756-aa3a-586039a1938f">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291405.0000 5041900.0000 9.0000 291410.0000 5041900.0000 6.0000 291410.0000 5041910.0000 6.0000 291405.0000 5041910.0000 9.0000 291405.0000 5041900.0000 9.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_2d5f403b-eac9-46ff-abbe-579c1416747a">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291400.0000 5041900.0000 0.0000 291400.0000 5041910.0000 0.0000 291410.0000 5041910.0000 0.0000 291410.0000 5041900.0000 0.0000 291400.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_934e4b6a-022d-4cf7-8426-883da175edd4">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291410.0000 5041910.0000 6.0000 291410.0000 5041900.0000 6.0000 291410.0000 5041900.0000 0.0000 291410.0000 5041910.0000 0.0000 291410.0000 5041910.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:lod3Solid>
						<gml:Solid gml:id="fx6_id_usage_zone_1_lod3_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="fx6_id_usage_zone_1_lod3_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_6e3e783e-b75a-4436-9f49-ed7d5346bca0">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291400.0000 5041910.0000 0.0000 291400.0000 5041910.0000 6.0000 291405.0000 5041910.0000 9.0000 291410.0000 5041910.0000 6.0000 291410.0000 5041910.0000 0.0000 291400.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_ed5e64ff-65d6-4da8-bd65-a726d53494fa">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291400.0000 5041900.0000 0.0000 291410.0000 5041900.0000 0.0000 291410.0000 5041900.0000 6.0000 291405.0000 5041900.0000 9.0000 291400.0000 5041900.0000 6.0000 291400.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_b7a25cfb-c3c6-490c-8628-42c50627d42c">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291400.0000 5041900.0000 0.0000 291400.0000 5041900.0000 6.0000 291400.0000 5041910.0000 6.0000 291400.0000 5041910.0000 0.0000 291400.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_204ef154-fa62-4200-b3f2-4bb427b7b42e">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291400.0000 5041900.0000 6.0000 291405.0000 5041900.0000 9.0000 291405.0000 5041910.0000 9.0000 291400.0000 5041910.0000 6.0000 291400.0000 5041900.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_1f26fb83-a013-4528-9b75-b7eed4d07b70">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291405.0000 5041900.0000 9.0000 291410.0000 5041900.0000 6.0000 291410.0000 5041910.0000 6.0000 291405.0000 5041910.0000 9.0000 291405.0000 5041900.0000 9.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_0f7e6a7d-4c78-4f23-a531-482e254f1aae">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291400.0000 5041900.0000 0.0000 291400.0000 5041910.0000 0.0000 291410.0000 5041910.0000 0.0000 291410.0000 5041900.0000 0.0000 291400.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="fx6_Polygon_UUID_8c107b31-166a-4b7c-aec1-4800b9dd396c">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291410.0000 5041910.0000 6.0000 291410.0000 5041900.0000 6.0000 291410.0000 5041900.0000 0.0000 291410.0000 5041910.0000 0.0000 291410.0000 5041910.0000 6.0000</gml:posList>
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
					<nrg3:internalHeatGains uom="W/m^2">1.4</nrg3:internalHeatGains>
					<nrg3:internalHeatGainsConvectiveFraction uom="unit interval">0.3</nrg3:internalHeatGainsConvectiveFraction>
					<nrg3:internalHeatGainsLatentFraction uom="unit interval">0.2</nrg3:internalHeatGainsLatentFraction>
					<nrg3:internalHeatGainsRadiantFraction uom="unit interval">0.5</nrg3:internalHeatGainsRadiantFraction>
					<nrg3:occupiedBy>
						<nrg3:Occupants gml:id="fx6_id_occupants_1">
							<gml:description>This is Occupants 1</gml:description>
							<gml:name>Occupants 1</gml:name>
							<nrg3:type codeSpace="occ_codeSpace_xyz">residents</nrg3:type>
							<nrg3:numberOfOccupants>4</nrg3:numberOfOccupants>
							<nrg3:heatDissipation uom="W/m^2">0.7</nrg3:heatDissipation>
							<nrg3:heatDissipationConvectiveFraction uom="unit interval">0.3</nrg3:heatDissipationConvectiveFraction>
							<nrg3:heatDissipationLatentFraction uom="unit interval">0.2</nrg3:heatDissipationLatentFraction>
							<nrg3:heatDissipationRadiantFraction uom="unit interval">0.5</nrg3:heatDissipationRadiantFraction>
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
		<bldg:Building gml:id="house7_lod3_hull">
			<gml:description>The LoD3 house again, with one difference: its thermal zone coincides with the LoD3 hull, so the zone uses the building's own surfaces and windows.</gml:description>
			<gml:name>Report house - LoD3 hull</gml:name>
			<core:creationDate>2024-09-25</core:creationDate>
			<nrg3:referencePoint>
				<gml:Point srsName="EPSG:32633" srsDimension="3">
					<gml:pos>291425.0000 5041905.0000 4.5000</gml:pos>
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
				<gml:MultiSurface gml:id="h7_id_building_1_footprint_MultiSurf" srsName="EPSG:32633" srsDimension="3">
					<gml:surfaceMember>
						<gml:OrientableSurface orientation="-">
							<gml:baseSurface xlink:href="#h7_id_building_1_polygon_3"/>
						</gml:OrientableSurface>
					</gml:surfaceMember>
				</gml:MultiSurface>
			</bldg:lod0FootPrint>
			<bldg:lod1Solid>
				<gml:Solid gml:id="h7_id_building_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
					<gml:exterior>
						<gml:CompositeSurface gml:id="h7_id_building_1_lod1_CompSurf">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_id_building_1_lod1_Polygon_1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291420.0000 5041900.0000 0.0000 291420.0000 5041910.0000 0.0000 291430.0000 5041910.0000 0.0000 291430.0000 5041900.0000 0.0000 291420.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_id_building_1_lod1_Polygon_2">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291420.0000 5041900.0000 0.0000 291430.0000 5041900.0000 0.0000 291430.0000 5041900.0000 7.5000 291420.0000 5041900.0000 7.5000 291420.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_id_building_1_lod1_Polygon_3">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291430.0000 5041900.0000 0.0000 291430.0000 5041910.0000 0.0000 291430.0000 5041910.0000 7.5000 291430.0000 5041900.0000 7.5000 291430.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_id_building_1_lod1_Polygon_4">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291430.0000 5041910.0000 0.0000 291420.0000 5041910.0000 0.0000 291420.0000 5041910.0000 7.5000 291430.0000 5041910.0000 7.5000 291430.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_id_building_1_lod1_Polygon_5">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291420.0000 5041910.0000 0.0000 291420.0000 5041900.0000 0.0000 291420.0000 5041900.0000 7.5000 291420.0000 5041910.0000 7.5000 291420.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_id_building_1_lod1_Polygon_6">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291420.0000 5041900.0000 7.5000 291430.0000 5041900.0000 7.5000 291430.0000 5041910.0000 7.5000 291420.0000 5041910.0000 7.5000 291420.0000 5041900.0000 7.5000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:CompositeSurface>
					</gml:exterior>
				</gml:Solid>
			</bldg:lod1Solid>
			<bldg:lod2Solid>
				<gml:Solid gml:id="h7_id_building_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
					<gml:exterior>
						<gml:CompositeSurface gml:id="h7_id_building_1_lod2_CompSurf">
							<gml:surfaceMember xlink:href="#h7_id_building_1_polygon_4"/>
							<gml:surfaceMember xlink:href="#h7_id_building_1_polygon_5"/>
							<gml:surfaceMember xlink:href="#h7_id_building_1_polygon_7"/>
							<gml:surfaceMember xlink:href="#h7_id_building_1_polygon_1"/>
							<gml:surfaceMember xlink:href="#h7_id_building_1_polygon_2"/>
							<gml:surfaceMember xlink:href="#h7_id_building_1_polygon_3"/>
							<gml:surfaceMember xlink:href="#h7_id_building_1_polygon_cs1"/>
						</gml:CompositeSurface>
					</gml:exterior>
				</gml:Solid>
			</bldg:lod2Solid>
			<bldg:boundedBy>
				<bldg:GroundSurface gml:id="h7_id_building_1_groundsurface_1">
					<gml:description>This is GroundSurface 1 (Building 1)</gml:description>
					<gml:name>GroundSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_ground_1"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291425.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h7_id_building_1_groundsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_id_building_1_polygon_3">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291420.0000 5041900.0000 0.0000 291420.0000 5041910.0000 0.0000 291430.0000 5041910.0000 0.0000 291430.0000 5041900.0000 0.0000 291420.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<bldg:lod3MultiSurface>
						<gml:MultiSurface gml:id="h7_id_building_1_groundsurface_1_lod3_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_Polygon_UUID_4a5ef73e-04b2-4e8e-81f5-1ddb2838823e">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291420.0000 5041900.0000 0.0000 291420.0000 5041910.0000 0.0000 291430.0000 5041910.0000 0.0000 291430.0000 5041900.0000 0.0000 291420.0000 5041900.0000 0.0000</gml:posList>
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
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:RoofSurface gml:id="h7_id_building_1_roofsurface_1">
					<gml:description>This is RoofSurface 1 (Building 1)</gml:description>
					<gml:name>RoofSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291425.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h7_id_building_1_roofsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_id_building_1_polygon_1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291420.0000 5041900.0000 6.0000 291425.0000 5041900.0000 9.0000 291425.0000 5041910.0000 9.0000 291420.0000 5041910.0000 6.0000 291420.0000 5041900.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<bldg:lod3MultiSurface>
						<gml:MultiSurface gml:id="h7_id_building_1_roofsurface_1_lod3_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_Polygon_UUID_9454055e-f9f2-46c6-8c3d-f1de8e5b54ce">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291420.0000 5041900.0000 6.0000 291425.0000 5041900.0000 9.0000 291425.0000 5041910.0000 9.0000 291420.0000 5041910.0000 6.0000 291420.0000 5041900.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod3MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">270</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfHeatCapacity uom="kJ/(m^2*K)">508</nrg3:bdgBdrySurfHeatCapacity>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">30.9638</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfOpaqueSurfaceArea>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfThickness uom="mm">365</nrg3:bdgBdrySurfThickness>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:RoofSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:RoofSurface gml:id="h7_id_building_1_roofsurface_2">
					<gml:description>This is RoofSurface 2 (Building 1)</gml:description>
					<gml:name>RoofSurface 2 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291425.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h7_id_building_1_roofsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_id_building_1_polygon_2">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291425.0000 5041900.0000 9.0000 291430.0000 5041900.0000 6.0000 291430.0000 5041910.0000 6.0000 291425.0000 5041910.0000 9.0000 291425.0000 5041900.0000 9.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<bldg:lod3MultiSurface>
						<gml:MultiSurface gml:id="h7_id_building_1_roofsurface_2_lod3_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_Polygon_UUID_e8e3d62c-1bb4-48d2-8415-346cb2dff634">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291425.0000 5041900.0000 9.0000 291430.0000 5041900.0000 6.0000 291430.0000 5041910.0000 6.0000 291425.0000 5041910.0000 9.0000 291425.0000 5041900.0000 9.0000</gml:posList>
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
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface gml:id="h7_id_building_1_wallsurface_1">
					<gml:description>This is WallSurface 1 (Building 1)</gml:description>
					<gml:name>WallSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291425.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h7_id_building_1_wallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_id_building_1_polygon_5">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291420.0000 5041900.0000 0.0000 291430.0000 5041900.0000 0.0000 291430.0000 5041900.0000 6.0000 291425.0000 5041900.0000 9.0000 291420.0000 5041900.0000 6.0000 291420.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<bldg:lod3MultiSurface>
						<gml:MultiSurface gml:id="h7_id_building_1_wallsurface_1_lod3_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_Polygon_UUID_2240fbcc-7699-48dd-93b4-1668ac44224f">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291420.0000 5041900.0000 0.0000 291430.0000 5041900.0000 0.0000 291430.0000 5041900.0000 6.0000 291425.0000 5041900.0000 9.0000 291420.0000 5041900.0000 6.0000 291420.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
									<gml:interior>
										<gml:LinearRing>
											<gml:posList>291423.0000 5041900.0000 1.8000 291423.0000 5041900.0000 5.2542 291425.0000 5041900.0000 6.4542 291427.0000 5041900.0000 5.2542 291427.0000 5041900.0000 1.8000 291423.0000 5041900.0000 1.8000</gml:posList>
										</gml:LinearRing>
									</gml:interior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod3MultiSurface>
					<bldg:opening>
						<bldg:Window gml:id="h7_id_building_1_wallsurface_1_thermal_opening_1">
							<gml:description>This is Thermal Opening 1</gml:description>
							<gml:name>Thermal Opening 1</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_glazing_5"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291425.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod3MultiSurface>
								<gml:MultiSurface gml:id="h7_id_building_1_wallsurface_1_thermal_opening_1_lod3_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_536d7500-8d81-490c-885e-78951e4a26d5">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291423.0000 5041900.0000 1.8000 291427.0000 5041900.0000 1.8000 291427.0000 5041900.0000 5.2542 291425.0000 5041900.0000 6.4542 291423.0000 5041900.0000 5.2542 291423.0000 5041900.0000 1.8000</gml:posList>
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
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.2162</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">75</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface gml:id="h7_id_building_1_wallsurface_2">
					<gml:description>This is WallSurface 2 (Building 1)</gml:description>
					<gml:name>WallSurface 2 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291425.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h7_id_building_1_wallsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_id_building_1_polygon_4">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291420.0000 5041910.0000 0.0000 291420.0000 5041910.0000 6.0000 291425.0000 5041910.0000 9.0000 291430.0000 5041910.0000 6.0000 291430.0000 5041910.0000 0.0000 291420.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<bldg:lod3MultiSurface>
						<gml:MultiSurface gml:id="h7_id_building_1_wallsurface_2_lod3_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_Polygon_UUID_1a85715e-a92d-405b-adf8-1e402415cc90">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291420.0000 5041910.0000 0.0000 291420.0000 5041910.0000 6.0000 291425.0000 5041910.0000 9.0000 291430.0000 5041910.0000 6.0000 291430.0000 5041910.0000 0.0000 291420.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
									<gml:interior>
										<gml:LinearRing>
											<gml:posList>291423.0000 5041910.0000 1.8000 291427.0000 5041910.0000 1.8000 291427.0000 5041910.0000 5.2542 291425.0000 5041910.0000 6.4542 291423.0000 5041910.0000 5.2542 291423.0000 5041910.0000 1.8000</gml:posList>
										</gml:LinearRing>
									</gml:interior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod3MultiSurface>
					<bldg:opening>
						<bldg:Window gml:id="h7_id_building_1_wallsurface_2_thermal_opening_2">
							<gml:description>This is Thermal Opening 2</gml:description>
							<gml:name>Thermal Opening 2</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_glazing_5"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291425.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod3MultiSurface>
								<gml:MultiSurface gml:id="h7_id_building_1_wallsurface_2_thermal_opening_2_lod3_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_fe6f9547-d5e5-45d6-8db4-3faaf56296e1">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291423.0000 5041910.0000 1.8000 291423.0000 5041910.0000 5.2542 291425.0000 5041910.0000 6.4542 291427.0000 5041910.0000 5.2542 291427.0000 5041910.0000 1.8000 291423.0000 5041910.0000 1.8000</gml:posList>
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
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.2162</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">75</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface gml:id="h7_id_building_1_wallsurface_3">
					<gml:description>This is WallSurface 3 (Building 1)</gml:description>
					<gml:name>WallSurface 3 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291425.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h7_id_building_1_wallsurface_3_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_id_building_1_polygon_7">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291420.0000 5041900.0000 0.0000 291420.0000 5041900.0000 6.0000 291420.0000 5041910.0000 6.0000 291420.0000 5041910.0000 0.0000 291420.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<bldg:lod3MultiSurface>
						<gml:MultiSurface gml:id="h7_id_building_1_wallsurface_3_lod3_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_Polygon_UUID_148e7131-25d1-4de1-9092-c89d73a2b927">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291420.0000 5041900.0000 0.0000 291420.0000 5041900.0000 6.0000 291420.0000 5041910.0000 6.0000 291420.0000 5041910.0000 0.0000 291420.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
									<gml:interior>
										<gml:LinearRing>
											<gml:posList>291420.0000 5041903.0000 1.8000 291420.0000 5041907.0000 1.8000 291420.0000 5041907.0000 4.2000 291420.0000 5041903.0000 4.2000 291420.0000 5041903.0000 1.8000</gml:posList>
										</gml:LinearRing>
									</gml:interior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod3MultiSurface>
					<bldg:opening>
						<bldg:Window gml:id="h7_id_building_1_wallsurface_3_thermal_opening_3">
							<gml:description>This is Thermal Opening 3</gml:description>
							<gml:name>Thermal Opening 3</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_glazing_5"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291425.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod3MultiSurface>
								<gml:MultiSurface gml:id="h7_id_building_1_wallsurface_3_thermal_opening_3_lod3_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_0ef2fcc0-3192-4ccf-a218-f3de9fe3c153">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291420.0000 5041903.0000 1.8000 291420.0000 5041903.0000 4.2000 291420.0000 5041907.0000 4.2000 291420.0000 5041907.0000 1.8000 291420.0000 5041903.0000 1.8000</gml:posList>
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
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.16</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface gml:id="h7_id_building_1_wallsurface_4">
					<gml:description>This is WallSurface 4 (Building 1)</gml:description>
					<gml:name>WallSurface 4 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291425.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h7_id_building_1_wallsurface_4_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_id_building_1_polygon_cs1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291430.0000 5041910.0000 6.0000 291430.0000 5041900.0000 6.0000 291430.0000 5041900.0000 0.0000 291430.0000 5041910.0000 0.0000 291430.0000 5041910.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<bldg:lod3MultiSurface>
						<gml:MultiSurface gml:id="h7_id_building_1_wallsurface_4_lod3_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h7_Polygon_UUID_5931fe6f-0875-464c-a020-17addd8f9fe5">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291430.0000 5041910.0000 6.0000 291430.0000 5041900.0000 6.0000 291430.0000 5041900.0000 0.0000 291430.0000 5041910.0000 0.0000 291430.0000 5041910.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod3MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:address>
				<core:Address gml:id="h7_id_address_1">
					<core:xalAddress>
						<ns5:AddressDetails>
							<ns5:Country>
								<ns5:CountryNameCode>ALD</ns5:CountryNameCode>
								<ns5:CountryName>Bespin Territories</ns5:CountryName>
								<ns5:Locality Type="Town">
									<ns5:LocalityName>Alderaan</ns5:LocalityName>
									<ns5:Thoroughfare Type="Street">
										<ns5:ThoroughfareNumber>1</ns5:ThoroughfareNumber>
										<ns5:ThoroughfareName>Bespin Square</ns5:ThoroughfareName>
									</ns5:Thoroughfare>
									<ns5:PostalCode>
										<ns5:PostalCodeNumber>1977SW</ns5:PostalCodeNumber>
									</ns5:PostalCode>
								</ns5:Locality>
							</ns5:Country>
						</ns5:AddressDetails>
					</core:xalAddress>
					<core:multiPoint>
						<gml:MultiPoint srsName="EPSG:32633" srsDimension="3">
							<gml:pointMember>
								<gml:Point>
									<gml:pos>291425.0000 5041905.0000 0.0000</gml:pos>
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
			<nrg3:bdgType codeSpace="bdgType_codeSpace">singleFamilyHouse</nrg3:bdgType>
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
				<nrg3:BuildingUnit gml:id="h7_id_building_unit_1">
					<gml:description>This is BuildingUnit 1</gml:description>
					<gml:name>BuildingUnit 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291425.0000 5041905.0000 4.5000</gml:pos>
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
							<nrg3:value uom="m^2">180</nrg3:value>
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
							<nrg3:value uom="m^3">486</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">energyReferenceVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:lod1Solid>
						<gml:Solid gml:id="h7_id_building_unit_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="h7_id_building_unit_1_lod1_CompSurf">
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_42e7489a-e3f6-4a45-be2a-fbe735cd2ef8"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_3f00920e-17c2-41f1-acb7-e223b1199044"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_ba78c9d7-0ed7-49b8-b107-d939f0186284"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_1406dd4c-f070-4022-835b-50018fdc6c54"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_694c7871-d386-4e68-9c88-f62140080992"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_945a1c0f-31f2-4bad-9599-9aaecf0ac7ac"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="h7_id_building_unit_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="h7_id_building_unit_1_lod2_CompSurf">
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_6e3e783e-b75a-4436-9f49-ed7d5346bca0"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_ed5e64ff-65d6-4da8-bd65-a726d53494fa"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_b7a25cfb-c3c6-490c-8628-42c50627d42c"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_204ef154-fa62-4200-b3f2-4bb427b7b42e"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_1f26fb83-a013-4528-9b75-b7eed4d07b70"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_0f7e6a7d-4c78-4f23-a531-482e254f1aae"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_8c107b31-166a-4b7c-aec1-4800b9dd396c"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:lod3Solid>
						<gml:Solid gml:id="h7_id_building_unit_1_lod3_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="h7_id_building_unit_1_lod3_CompSurf">
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_b9c018da-8461-4762-99c2-1cae1fc6dfa2"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_efca560a-2e79-4536-9e21-4e23aacef253"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_80ecaada-e49a-4e7d-8955-367405f503fb"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_4dbfd338-5c11-42cd-b60d-68038c5dc78f"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_5103fb6c-6d3f-4756-aa3a-586039a1938f"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_2d5f403b-eac9-46ff-abbe-579c1416747a"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_934e4b6a-022d-4cf7-8426-883da175edd4"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod3Solid>
					<nrg3:type codeSpace="buildingUnit_codeSpace_123">residential</nrg3:type>
					<nrg3:numberOfRooms>4</nrg3:numberOfRooms>
					<nrg3:ownershipType codeSpace="ownership_type_codeSpace_abc">corporation</nrg3:ownershipType>
					<nrg3:address xlink:href="#h7_id_address_1"/>
				</nrg3:BuildingUnit>
			</nrg3:buildingUnit>
			<nrg3:thermalZone>
				<nrg3:ThermalZone gml:id="h7_id_thermal_zone_1">
					<gml:description>This is ThermalZone 1</gml:description>
					<gml:name>ThermalZone 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291425.0000 5041905.0000 4.5000</gml:pos>
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
						<gml:Solid gml:id="h7_id_thermal_zone_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="h7_id_thermal_zone_1_lod1_CompSurf">
									<gml:surfaceMember xlink:href="#h7_id_building_1_lod1_Polygon_1"/>
									<gml:surfaceMember xlink:href="#h7_id_building_1_lod1_Polygon_2"/>
									<gml:surfaceMember xlink:href="#h7_id_building_1_lod1_Polygon_3"/>
									<gml:surfaceMember xlink:href="#h7_id_building_1_lod1_Polygon_4"/>
									<gml:surfaceMember xlink:href="#h7_id_building_1_lod1_Polygon_5"/>
									<gml:surfaceMember xlink:href="#h7_id_building_1_lod1_Polygon_6"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="h7_id_thermal_zone_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="h7_id_thermal_zone_1_lod2_CompSurf">
									<gml:surfaceMember xlink:href="#h7_id_building_1_polygon_4"/>
									<gml:surfaceMember xlink:href="#h7_id_building_1_polygon_5"/>
									<gml:surfaceMember xlink:href="#h7_id_building_1_polygon_7"/>
									<gml:surfaceMember xlink:href="#h7_id_building_1_polygon_1"/>
									<gml:surfaceMember xlink:href="#h7_id_building_1_polygon_2"/>
									<gml:surfaceMember xlink:href="#h7_id_building_1_polygon_3"/>
									<gml:surfaceMember xlink:href="#h7_id_building_1_polygon_cs1"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:lod3Solid>
						<gml:Solid gml:id="h7_id_thermal_zone_1_lod3_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="h7_id_thermal_zone_1_lod3_CompSurf">
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_5931fe6f-0875-464c-a020-17addd8f9fe5"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_4a5ef73e-04b2-4e8e-81f5-1ddb2838823e"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_9454055e-f9f2-46c6-8c3d-f1de8e5b54ce"/>
									<gml:surfaceMember xlink:href="#h7_Polygon_UUID_e8e3d62c-1bb4-48d2-8415-346cb2dff634"/>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_da00ca7d-c958-4d8a-87c6-a6a016ff5478">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291420.0000 5041900.0000 0.0000 291430.0000 5041900.0000 0.0000 291430.0000 5041900.0000 6.0000 291425.0000 5041900.0000 9.0000 291420.0000 5041900.0000 6.0000 291420.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_56f104ce-3b55-46ff-9ea3-463b83ecea23">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291420.0000 5041910.0000 0.0000 291420.0000 5041910.0000 6.0000 291425.0000 5041910.0000 9.0000 291430.0000 5041910.0000 6.0000 291430.0000 5041910.0000 0.0000 291420.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_ef9093c6-d213-448d-ba14-c41ff8143a6d">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291420.0000 5041900.0000 0.0000 291420.0000 5041900.0000 6.0000 291420.0000 5041910.0000 6.0000 291420.0000 5041910.0000 0.0000 291420.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod3Solid>
					<nrg3:heatCapacity uom="J/K">46800000</nrg3:heatCapacity>
					<nrg3:infiltrationRate uom="1/h">0.3</nrg3:infiltrationRate>
					<nrg3:isCooled>false</nrg3:isCooled>
					<nrg3:isHeated>true</nrg3:isHeated>
					<nrg3:coincidesWithLod2Hull>false</nrg3:coincidesWithLod2Hull>
					<nrg3:coincidesWithLod3Hull>true</nrg3:coincidesWithLod3Hull>
				</nrg3:ThermalZone>
			</nrg3:thermalZone>
			<nrg3:usageZone>
				<nrg3:UsageZone gml:id="h7_id_usage_zone_1">
					<gml:description>This is UsageZone 1</gml:description>
					<gml:name>UsageZone 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291425.0000 5041905.0000 4.5000</gml:pos>
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
							<nrg3:type codeSpace="volume_codeSpace">energyReferenceVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:lod1Solid>
						<gml:Solid gml:id="h7_id_usage_zone_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="h7_id_usage_zone_1_lod1_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_42e7489a-e3f6-4a45-be2a-fbe735cd2ef8">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291420.0000 5041900.0000 0.0000 291420.0000 5041910.0000 0.0000 291430.0000 5041910.0000 0.0000 291430.0000 5041900.0000 0.0000 291420.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_3f00920e-17c2-41f1-acb7-e223b1199044">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291420.0000 5041900.0000 0.0000 291430.0000 5041900.0000 0.0000 291430.0000 5041900.0000 7.5000 291420.0000 5041900.0000 7.5000 291420.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_ba78c9d7-0ed7-49b8-b107-d939f0186284">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291430.0000 5041900.0000 0.0000 291430.0000 5041910.0000 0.0000 291430.0000 5041910.0000 7.5000 291430.0000 5041900.0000 7.5000 291430.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_1406dd4c-f070-4022-835b-50018fdc6c54">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291430.0000 5041910.0000 0.0000 291420.0000 5041910.0000 0.0000 291420.0000 5041910.0000 7.5000 291430.0000 5041910.0000 7.5000 291430.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_694c7871-d386-4e68-9c88-f62140080992">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291420.0000 5041910.0000 0.0000 291420.0000 5041900.0000 0.0000 291420.0000 5041900.0000 7.5000 291420.0000 5041910.0000 7.5000 291420.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_945a1c0f-31f2-4bad-9599-9aaecf0ac7ac">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291420.0000 5041900.0000 7.5000 291430.0000 5041900.0000 7.5000 291430.0000 5041910.0000 7.5000 291420.0000 5041910.0000 7.5000 291420.0000 5041900.0000 7.5000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="h7_id_usage_zone_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="h7_id_usage_zone_1_lod2_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_b9c018da-8461-4762-99c2-1cae1fc6dfa2">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291420.0000 5041910.0000 0.0000 291420.0000 5041910.0000 6.0000 291425.0000 5041910.0000 9.0000 291430.0000 5041910.0000 6.0000 291430.0000 5041910.0000 0.0000 291420.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_efca560a-2e79-4536-9e21-4e23aacef253">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291420.0000 5041900.0000 0.0000 291430.0000 5041900.0000 0.0000 291430.0000 5041900.0000 6.0000 291425.0000 5041900.0000 9.0000 291420.0000 5041900.0000 6.0000 291420.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_80ecaada-e49a-4e7d-8955-367405f503fb">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291420.0000 5041900.0000 0.0000 291420.0000 5041900.0000 6.0000 291420.0000 5041910.0000 6.0000 291420.0000 5041910.0000 0.0000 291420.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_4dbfd338-5c11-42cd-b60d-68038c5dc78f">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291420.0000 5041900.0000 6.0000 291425.0000 5041900.0000 9.0000 291425.0000 5041910.0000 9.0000 291420.0000 5041910.0000 6.0000 291420.0000 5041900.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_5103fb6c-6d3f-4756-aa3a-586039a1938f">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291425.0000 5041900.0000 9.0000 291430.0000 5041900.0000 6.0000 291430.0000 5041910.0000 6.0000 291425.0000 5041910.0000 9.0000 291425.0000 5041900.0000 9.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_2d5f403b-eac9-46ff-abbe-579c1416747a">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291420.0000 5041900.0000 0.0000 291420.0000 5041910.0000 0.0000 291430.0000 5041910.0000 0.0000 291430.0000 5041900.0000 0.0000 291420.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_934e4b6a-022d-4cf7-8426-883da175edd4">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291430.0000 5041910.0000 6.0000 291430.0000 5041900.0000 6.0000 291430.0000 5041900.0000 0.0000 291430.0000 5041910.0000 0.0000 291430.0000 5041910.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:lod3Solid>
						<gml:Solid gml:id="h7_id_usage_zone_1_lod3_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="h7_id_usage_zone_1_lod3_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_6e3e783e-b75a-4436-9f49-ed7d5346bca0">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291420.0000 5041910.0000 0.0000 291420.0000 5041910.0000 6.0000 291425.0000 5041910.0000 9.0000 291430.0000 5041910.0000 6.0000 291430.0000 5041910.0000 0.0000 291420.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_ed5e64ff-65d6-4da8-bd65-a726d53494fa">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291420.0000 5041900.0000 0.0000 291430.0000 5041900.0000 0.0000 291430.0000 5041900.0000 6.0000 291425.0000 5041900.0000 9.0000 291420.0000 5041900.0000 6.0000 291420.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_b7a25cfb-c3c6-490c-8628-42c50627d42c">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291420.0000 5041900.0000 0.0000 291420.0000 5041900.0000 6.0000 291420.0000 5041910.0000 6.0000 291420.0000 5041910.0000 0.0000 291420.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_204ef154-fa62-4200-b3f2-4bb427b7b42e">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291420.0000 5041900.0000 6.0000 291425.0000 5041900.0000 9.0000 291425.0000 5041910.0000 9.0000 291420.0000 5041910.0000 6.0000 291420.0000 5041900.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_1f26fb83-a013-4528-9b75-b7eed4d07b70">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291425.0000 5041900.0000 9.0000 291430.0000 5041900.0000 6.0000 291430.0000 5041910.0000 6.0000 291425.0000 5041910.0000 9.0000 291425.0000 5041900.0000 9.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_0f7e6a7d-4c78-4f23-a531-482e254f1aae">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291420.0000 5041900.0000 0.0000 291420.0000 5041910.0000 0.0000 291430.0000 5041910.0000 0.0000 291430.0000 5041900.0000 0.0000 291420.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h7_Polygon_UUID_8c107b31-166a-4b7c-aec1-4800b9dd396c">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291430.0000 5041910.0000 6.0000 291430.0000 5041900.0000 6.0000 291430.0000 5041900.0000 0.0000 291430.0000 5041910.0000 0.0000 291430.0000 5041910.0000 6.0000</gml:posList>
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
					<nrg3:internalHeatGains uom="W/m^2">1.4</nrg3:internalHeatGains>
					<nrg3:internalHeatGainsConvectiveFraction uom="unit interval">0.3</nrg3:internalHeatGainsConvectiveFraction>
					<nrg3:internalHeatGainsLatentFraction uom="unit interval">0.2</nrg3:internalHeatGainsLatentFraction>
					<nrg3:internalHeatGainsRadiantFraction uom="unit interval">0.5</nrg3:internalHeatGainsRadiantFraction>
					<nrg3:occupiedBy>
						<nrg3:Occupants gml:id="h7_id_occupants_1">
							<gml:description>This is Occupants 1</gml:description>
							<gml:name>Occupants 1</gml:name>
							<nrg3:type codeSpace="occ_codeSpace_xyz">residents</nrg3:type>
							<nrg3:numberOfOccupants>4</nrg3:numberOfOccupants>
							<nrg3:heatDissipation uom="W/m^2">0.7</nrg3:heatDissipation>
							<nrg3:heatDissipationConvectiveFraction uom="unit interval">0.3</nrg3:heatDissipationConvectiveFraction>
							<nrg3:heatDissipationLatentFraction uom="unit interval">0.2</nrg3:heatDissipationLatentFraction>
							<nrg3:heatDissipationRadiantFraction uom="unit interval">0.5</nrg3:heatDissipationRadiantFraction>
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
		<bldg:Building gml:id="house8_lod2_two_zones">
			<gml:description>The LoD2 house again, with one difference: it holds two dwellings side by side, one thermal zone each, with a party wall between them.</gml:description>
			<gml:name>Report house - LoD2, two dwellings</gml:name>
			<core:creationDate>2024-09-25</core:creationDate>
			<nrg3:referencePoint>
				<gml:Point srsName="EPSG:32633" srsDimension="3">
					<gml:pos>291445.0000 5041905.0000 4.5000</gml:pos>
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
				<gml:MultiSurface gml:id="h8_id_building_1_footprint_MultiSurf" srsName="EPSG:32633" srsDimension="3">
					<gml:surfaceMember>
						<gml:OrientableSurface orientation="-">
							<gml:baseSurface xlink:href="#h8_id_building_1_polygon_3"/>
						</gml:OrientableSurface>
					</gml:surfaceMember>
				</gml:MultiSurface>
			</bldg:lod0FootPrint>
			<bldg:lod1Solid>
				<gml:Solid gml:id="h8_id_building_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
					<gml:exterior>
						<gml:CompositeSurface gml:id="h8_id_building_1_lod1_CompSurf">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h8_id_building_1_lod1_Polygon_1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291440.0000 5041900.0000 0.0000 291440.0000 5041910.0000 0.0000 291450.0000 5041910.0000 0.0000 291450.0000 5041900.0000 0.0000 291440.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="h8_id_building_1_lod1_Polygon_2">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291440.0000 5041900.0000 0.0000 291450.0000 5041900.0000 0.0000 291450.0000 5041900.0000 7.5000 291440.0000 5041900.0000 7.5000 291440.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="h8_id_building_1_lod1_Polygon_3">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291450.0000 5041900.0000 0.0000 291450.0000 5041910.0000 0.0000 291450.0000 5041910.0000 7.5000 291450.0000 5041900.0000 7.5000 291450.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="h8_id_building_1_lod1_Polygon_4">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291450.0000 5041910.0000 0.0000 291440.0000 5041910.0000 0.0000 291440.0000 5041910.0000 7.5000 291450.0000 5041910.0000 7.5000 291450.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="h8_id_building_1_lod1_Polygon_5">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291440.0000 5041910.0000 0.0000 291440.0000 5041900.0000 0.0000 291440.0000 5041900.0000 7.5000 291440.0000 5041910.0000 7.5000 291440.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="h8_id_building_1_lod1_Polygon_6">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291440.0000 5041900.0000 7.5000 291450.0000 5041900.0000 7.5000 291450.0000 5041910.0000 7.5000 291440.0000 5041910.0000 7.5000 291440.0000 5041900.0000 7.5000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:CompositeSurface>
					</gml:exterior>
				</gml:Solid>
			</bldg:lod1Solid>
			<bldg:lod2Solid>
				<gml:Solid gml:id="h8_id_building_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
					<gml:exterior>
						<gml:CompositeSurface gml:id="h8_id_building_1_lod2_CompSurf">
							<gml:surfaceMember xlink:href="#h8_id_building_1_polygon_4"/>
							<gml:surfaceMember xlink:href="#h8_id_building_1_polygon_5"/>
							<gml:surfaceMember xlink:href="#h8_id_building_1_polygon_7"/>
							<gml:surfaceMember xlink:href="#h8_id_building_1_polygon_1"/>
							<gml:surfaceMember xlink:href="#h8_id_building_1_polygon_2"/>
							<gml:surfaceMember xlink:href="#h8_id_building_1_polygon_3"/>
							<gml:surfaceMember xlink:href="#h8_id_building_1_polygon_cs1"/>
						</gml:CompositeSurface>
					</gml:exterior>
				</gml:Solid>
			</bldg:lod2Solid>
			<bldg:boundedBy>
				<bldg:GroundSurface gml:id="h8_id_building_1_groundsurface_1">
					<gml:description>This is GroundSurface 1 (Building 1)</gml:description>
					<gml:name>GroundSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_ground_1"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291445.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h8_id_building_1_groundsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h8_id_building_1_polygon_3">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291440.0000 5041900.0000 0.0000 291440.0000 5041910.0000 0.0000 291450.0000 5041910.0000 0.0000 291450.0000 5041900.0000 0.0000 291440.0000 5041900.0000 0.0000</gml:posList>
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
				<bldg:RoofSurface gml:id="h8_id_building_1_roofsurface_1">
					<gml:description>This is RoofSurface 1 (Building 1)</gml:description>
					<gml:name>RoofSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291445.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h8_id_building_1_roofsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h8_id_building_1_polygon_1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291440.0000 5041900.0000 6.0000 291445.0000 5041900.0000 9.0000 291445.0000 5041910.0000 9.0000 291440.0000 5041910.0000 6.0000 291440.0000 5041900.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">270</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfHeatCapacity uom="kJ/(m^2*K)">508</nrg3:bdgBdrySurfHeatCapacity>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">30.9638</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfOpaqueSurfaceArea>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfThickness uom="mm">365</nrg3:bdgBdrySurfThickness>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:RoofSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:RoofSurface gml:id="h8_id_building_1_roofsurface_2">
					<gml:description>This is RoofSurface 2 (Building 1)</gml:description>
					<gml:name>RoofSurface 2 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291445.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h8_id_building_1_roofsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h8_id_building_1_polygon_2">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291445.0000 5041900.0000 9.0000 291450.0000 5041900.0000 6.0000 291450.0000 5041910.0000 6.0000 291445.0000 5041910.0000 9.0000 291445.0000 5041900.0000 9.0000</gml:posList>
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
				<bldg:WallSurface gml:id="h8_id_building_1_wallsurface_1">
					<gml:description>This is WallSurface 1 (Building 1)</gml:description>
					<gml:name>WallSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291445.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h8_id_building_1_wallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h8_id_building_1_polygon_5">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291440.0000 5041900.0000 0.0000 291450.0000 5041900.0000 0.0000 291450.0000 5041900.0000 6.0000 291445.0000 5041900.0000 9.0000 291440.0000 5041900.0000 6.0000 291440.0000 5041900.0000 0.0000</gml:posList>
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
				<bldg:WallSurface gml:id="h8_id_building_1_wallsurface_2">
					<gml:description>This is WallSurface 2 (Building 1)</gml:description>
					<gml:name>WallSurface 2 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291445.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h8_id_building_1_wallsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h8_id_building_1_polygon_4">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291440.0000 5041910.0000 0.0000 291440.0000 5041910.0000 6.0000 291445.0000 5041910.0000 9.0000 291450.0000 5041910.0000 6.0000 291450.0000 5041910.0000 0.0000 291440.0000 5041910.0000 0.0000</gml:posList>
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
				<bldg:WallSurface gml:id="h8_id_building_1_wallsurface_3">
					<gml:description>This is WallSurface 3 (Building 1)</gml:description>
					<gml:name>WallSurface 3 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291445.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h8_id_building_1_wallsurface_3_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h8_id_building_1_polygon_7">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291440.0000 5041900.0000 0.0000 291440.0000 5041900.0000 6.0000 291440.0000 5041910.0000 6.0000 291440.0000 5041910.0000 0.0000 291440.0000 5041900.0000 0.0000</gml:posList>
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
				<bldg:WallSurface gml:id="h8_id_building_1_wallsurface_4">
					<gml:description>This is WallSurface 4 (Building 1)</gml:description>
					<gml:name>WallSurface 4 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291445.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h8_id_building_1_wallsurface_4_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h8_id_building_1_polygon_cs1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291450.0000 5041910.0000 6.0000 291450.0000 5041900.0000 6.0000 291450.0000 5041900.0000 0.0000 291450.0000 5041910.0000 0.0000 291450.0000 5041910.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:address>
				<core:Address gml:id="h8_id_address_1">
					<core:xalAddress>
						<ns5:AddressDetails>
							<ns5:Country>
								<ns5:CountryNameCode>ALD</ns5:CountryNameCode>
								<ns5:CountryName>Bespin Territories</ns5:CountryName>
								<ns5:Locality Type="Town">
									<ns5:LocalityName>Alderaan</ns5:LocalityName>
									<ns5:Thoroughfare Type="Street">
										<ns5:ThoroughfareNumber>1</ns5:ThoroughfareNumber>
										<ns5:ThoroughfareName>Bespin Square</ns5:ThoroughfareName>
									</ns5:Thoroughfare>
									<ns5:PostalCode>
										<ns5:PostalCodeNumber>1977SW</ns5:PostalCodeNumber>
									</ns5:PostalCode>
								</ns5:Locality>
							</ns5:Country>
						</ns5:AddressDetails>
					</core:xalAddress>
					<core:multiPoint>
						<gml:MultiPoint srsName="EPSG:32633" srsDimension="3">
							<gml:pointMember>
								<gml:Point>
									<gml:pos>291445.0000 5041905.0000 0.0000</gml:pos>
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
			<nrg3:bdgType codeSpace="bdgType_codeSpace">multiFamilyHouse</nrg3:bdgType>
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
				<nrg3:BuildingUnit gml:id="h8_id_building_unit_1">
					<gml:description>This is BuildingUnit 1, the west dwelling</gml:description>
					<gml:name>BuildingUnit 1 (west dwelling)</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291442.5000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source</nrg3:source>
							<nrg3:value uom="m^2">100</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source</nrg3:source>
							<nrg3:value uom="m^2">90</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">energyReferenceArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source</nrg3:source>
							<nrg3:value uom="m^3">375</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source</nrg3:source>
							<nrg3:value uom="m^3">243</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">energyReferenceVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:type codeSpace="buildingUnit_codeSpace_123">residential</nrg3:type>
					<nrg3:numberOfRooms>2</nrg3:numberOfRooms>
					<nrg3:ownershipType codeSpace="ownership_type_codeSpace_abc">corporation</nrg3:ownershipType>
					<nrg3:address xlink:href="#h8_id_address_1"/>
				</nrg3:BuildingUnit>
			</nrg3:buildingUnit>
			<nrg3:buildingUnit>
				<nrg3:BuildingUnit gml:id="h8_id_building_unit_2">
					<gml:description>This is BuildingUnit 2, the east dwelling</gml:description>
					<gml:name>BuildingUnit 2 (east dwelling)</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291447.5000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source</nrg3:source>
							<nrg3:value uom="m^2">100</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source</nrg3:source>
							<nrg3:value uom="m^2">90</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">energyReferenceArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source</nrg3:source>
							<nrg3:value uom="m^3">375</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source</nrg3:source>
							<nrg3:value uom="m^3">243</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">energyReferenceVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:type codeSpace="buildingUnit_codeSpace_123">residential</nrg3:type>
					<nrg3:numberOfRooms>2</nrg3:numberOfRooms>
					<nrg3:ownershipType codeSpace="ownership_type_codeSpace_abc">corporation</nrg3:ownershipType>
					<nrg3:address xlink:href="#h8_id_address_1"/>
				</nrg3:BuildingUnit>
			</nrg3:buildingUnit>
			<nrg3:thermalZone>
				<nrg3:ThermalZone gml:id="h8_id_thermal_zone_1">
					<gml:description>This is ThermalZone 1, the west dwelling</gml:description>
					<gml:name>ThermalZone 1 (west dwelling)</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291442.5000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">100</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">50</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">footprintArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">90</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">energyReferenceArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">375</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">243</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">netVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:usageZone xlink:href="#h8_id_usage_zone_1"/>
					<nrg3:heatCapacity uom="J/K">23400000</nrg3:heatCapacity>
					<nrg3:infiltrationRate uom="1/h">0.3</nrg3:infiltrationRate>
					<nrg3:isCooled>false</nrg3:isCooled>
					<nrg3:isHeated>true</nrg3:isHeated>
					<nrg3:coincidesWithLod2Hull>false</nrg3:coincidesWithLod2Hull>
					<nrg3:coincidesWithLod3Hull>false</nrg3:coincidesWithLod3Hull>
					<nrg3:thermalBoundary>
						<bldg:GroundSurface gml:id="h8_id_thermal_zone_1_groundsurface_1">
							<gml:description>This is (ThermalBoundary) GroundSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) GroundSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_ground_1"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291442.5000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h8_id_thermal_zone_1_groundsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember>
										<gml:Polygon gml:id="h8_id_thermal_zone_1_polygon_ground">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291440.0000 5041900.0000 0.0000 291440.0000 5041910.0000 0.0000 291445.0000 5041910.0000 0.0000 291445.0000 5041900.0000 0.0000 291440.0000 5041900.0000 0.0000</gml:posList>
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
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">50</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:GroundSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:RoofSurface gml:id="h8_id_thermal_zone_1_roofsurface_1">
							<gml:description>This is (ThermalBoundary) RoofSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) RoofSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291442.5000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h8_id_thermal_zone_1_roofsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#h8_id_building_1_polygon_1"/>
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
						<bldg:WallSurface gml:id="h8_id_thermal_zone_1_wallsurface_1">
							<gml:description>This is (ThermalBoundary) WallSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291442.5000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h8_id_thermal_zone_1_wallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember>
										<gml:Polygon gml:id="h8_id_thermal_zone_1_polygon_south">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291440.0000 5041900.0000 0.0000 291445.0000 5041900.0000 0.0000 291445.0000 5041900.0000 9.0000 291440.0000 5041900.0000 6.0000 291440.0000 5041900.0000 0.0000</gml:posList>
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
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">29.3912</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.2162</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">37.5</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:WallSurface gml:id="h8_id_thermal_zone_1_wallsurface_2">
							<gml:description>This is (ThermalBoundary) WallSurface 2 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 2 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291442.5000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h8_id_thermal_zone_1_wallsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember>
										<gml:Polygon gml:id="h8_id_thermal_zone_1_polygon_north">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291445.0000 5041910.0000 0.0000 291440.0000 5041910.0000 0.0000 291440.0000 5041910.0000 6.0000 291445.0000 5041910.0000 9.0000 291445.0000 5041910.0000 0.0000</gml:posList>
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
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">29.3912</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.2162</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">37.5</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:WallSurface gml:id="h8_id_thermal_zone_1_wallsurface_3">
							<gml:description>This is (ThermalBoundary) WallSurface 3 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 3 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291442.5000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h8_id_thermal_zone_1_wallsurface_3_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#h8_id_building_1_polygon_7"/>
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
						<nrg3:PartyWallSurface gml:id="h8_id_thermal_zone_1_partywallsurface_1">
							<gml:description>This is (ThermalBoundary) PartyWallSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) PartyWallSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_iwall_4"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291442.5000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h8_id_thermal_zone_1_partywallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember>
										<gml:Polygon gml:id="h8_id_thermal_zone_1_polygon_party">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291445.0000 5041910.0000 9.0000 291445.0000 5041900.0000 9.0000 291445.0000 5041900.0000 0.0000 291445.0000 5041910.0000 0.0000 291445.0000 5041910.0000 9.0000</gml:posList>
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
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">90</nrg3:bdgBdrySurfTotalSurfaceArea>
						</nrg3:PartyWallSurface>
					</nrg3:thermalBoundary>
				</nrg3:ThermalZone>
			</nrg3:thermalZone>
			<nrg3:thermalZone>
				<nrg3:ThermalZone gml:id="h8_id_thermal_zone_2">
					<gml:description>This is ThermalZone 2, the east dwelling</gml:description>
					<gml:name>ThermalZone 2 (east dwelling)</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291447.5000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">100</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">50</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">footprintArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">90</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">energyReferenceArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">375</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">243</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">netVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:usageZone xlink:href="#h8_id_usage_zone_2"/>
					<nrg3:heatCapacity uom="J/K">23400000</nrg3:heatCapacity>
					<nrg3:infiltrationRate uom="1/h">0.3</nrg3:infiltrationRate>
					<nrg3:isCooled>false</nrg3:isCooled>
					<nrg3:isHeated>true</nrg3:isHeated>
					<nrg3:coincidesWithLod2Hull>false</nrg3:coincidesWithLod2Hull>
					<nrg3:coincidesWithLod3Hull>false</nrg3:coincidesWithLod3Hull>
					<nrg3:thermalBoundary>
						<bldg:GroundSurface gml:id="h8_id_thermal_zone_2_groundsurface_1">
							<gml:description>This is (ThermalBoundary) GroundSurface 1 (ThermalZone 2)</gml:description>
							<gml:name>(ThermalBoundary) GroundSurface 1 (ThermalZone 2)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_ground_1"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291447.5000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h8_id_thermal_zone_2_groundsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember>
										<gml:Polygon gml:id="h8_id_thermal_zone_2_polygon_ground">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291445.0000 5041900.0000 0.0000 291445.0000 5041910.0000 0.0000 291450.0000 5041910.0000 0.0000 291450.0000 5041900.0000 0.0000 291445.0000 5041900.0000 0.0000</gml:posList>
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
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">50</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:GroundSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:RoofSurface gml:id="h8_id_thermal_zone_2_roofsurface_2">
							<gml:description>This is (ThermalBoundary) RoofSurface 2 (ThermalZone 2)</gml:description>
							<gml:name>(ThermalBoundary) RoofSurface 2 (ThermalZone 2)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291447.5000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h8_id_thermal_zone_2_roofsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#h8_id_building_1_polygon_2"/>
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
						<bldg:WallSurface gml:id="h8_id_thermal_zone_2_wallsurface_1">
							<gml:description>This is (ThermalBoundary) WallSurface 1 (ThermalZone 2)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 1 (ThermalZone 2)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291447.5000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h8_id_thermal_zone_2_wallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember>
										<gml:Polygon gml:id="h8_id_thermal_zone_2_polygon_south">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291445.0000 5041900.0000 0.0000 291450.0000 5041900.0000 0.0000 291450.0000 5041900.0000 6.0000 291445.0000 5041900.0000 9.0000 291445.0000 5041900.0000 0.0000</gml:posList>
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
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">29.3912</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.2162</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">37.5</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:WallSurface gml:id="h8_id_thermal_zone_2_wallsurface_2">
							<gml:description>This is (ThermalBoundary) WallSurface 2 (ThermalZone 2)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 2 (ThermalZone 2)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291447.5000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h8_id_thermal_zone_2_wallsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember>
										<gml:Polygon gml:id="h8_id_thermal_zone_2_polygon_north">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291450.0000 5041910.0000 0.0000 291445.0000 5041910.0000 0.0000 291445.0000 5041910.0000 9.0000 291450.0000 5041910.0000 6.0000 291450.0000 5041910.0000 0.0000</gml:posList>
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
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">29.3912</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0.2162</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">37.5</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:WallSurface gml:id="h8_id_thermal_zone_2_wallsurface_4">
							<gml:description>This is (ThermalBoundary) WallSurface 4 (ThermalZone 2)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 4 (ThermalZone 2)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291447.5000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h8_id_thermal_zone_2_wallsurface_4_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#h8_id_building_1_polygon_cs1"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<nrg3:PartyWallSurface gml:id="h8_id_thermal_zone_2_partywallsurface_1">
							<gml:description>This is (ThermalBoundary) PartyWallSurface 1 (ThermalZone 2)</gml:description>
							<gml:name>(ThermalBoundary) PartyWallSurface 1 (ThermalZone 2)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_reverse_layered_construction_iwall_4"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291447.5000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h8_id_thermal_zone_2_partywallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember>
										<gml:Polygon gml:id="h8_id_thermal_zone_2_polygon_party">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291445.0000 5041910.0000 0.0000 291445.0000 5041900.0000 0.0000 291445.0000 5041900.0000 9.0000 291445.0000 5041910.0000 9.0000 291445.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">270</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">90</nrg3:bdgBdrySurfTotalSurfaceArea>
						</nrg3:PartyWallSurface>
					</nrg3:thermalBoundary>
				</nrg3:ThermalZone>
			</nrg3:thermalZone>
			<nrg3:usageZone>
				<nrg3:UsageZone gml:id="h8_id_usage_zone_1">
					<gml:description>This is UsageZone 1, the west dwelling</gml:description>
					<gml:name>UsageZone 1 (west dwelling)</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291442.5000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">100</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">90</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">energyReferenceArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">375</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">243</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">energyReferenceVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:buildingUnit xlink:href="#h8_id_building_unit_1"/>
					<nrg3:type codeSpace="usageZone_codeSpace_123">residential</nrg3:type>
					<nrg3:isPrimary>true</nrg3:isPrimary>
					<nrg3:numberOfBuildingUnits>1</nrg3:numberOfBuildingUnits>
					<nrg3:internalHeatGains uom="W/m^2">1.4</nrg3:internalHeatGains>
					<nrg3:internalHeatGainsConvectiveFraction uom="unit interval">0.3</nrg3:internalHeatGainsConvectiveFraction>
					<nrg3:internalHeatGainsLatentFraction uom="unit interval">0.2</nrg3:internalHeatGainsLatentFraction>
					<nrg3:internalHeatGainsRadiantFraction uom="unit interval">0.5</nrg3:internalHeatGainsRadiantFraction>
					<nrg3:occupiedBy>
						<nrg3:Occupants gml:id="h8_id_occupants_1">
							<gml:description>This is Occupants 1</gml:description>
							<gml:name>Occupants 1</gml:name>
							<nrg3:type codeSpace="occ_codeSpace_xyz">residents</nrg3:type>
							<nrg3:numberOfOccupants>2</nrg3:numberOfOccupants>
							<nrg3:heatDissipation uom="W/m^2">0.7</nrg3:heatDissipation>
							<nrg3:heatDissipationConvectiveFraction uom="unit interval">0.3</nrg3:heatDissipationConvectiveFraction>
							<nrg3:heatDissipationLatentFraction uom="unit interval">0.2</nrg3:heatDissipationLatentFraction>
							<nrg3:heatDissipationRadiantFraction uom="unit interval">0.5</nrg3:heatDissipationRadiantFraction>
							<nrg3:averageDietType codeSpace="diet_codeSpace">omnivorous</nrg3:averageDietType>
							<nrg3:averageIncomeLevel codeSpace="income_level codeSpace">middle</nrg3:averageIncomeLevel>
							<nrg3:averageInstructionLevel codeSpace="instruction_level_codeSpace">university</nrg3:averageInstructionLevel>
						</nrg3:Occupants>
					</nrg3:occupiedBy>
				</nrg3:UsageZone>
			</nrg3:usageZone>
			<nrg3:usageZone>
				<nrg3:UsageZone gml:id="h8_id_usage_zone_2">
					<gml:description>This is UsageZone 2, the east dwelling</gml:description>
					<gml:name>UsageZone 2 (east dwelling)</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291447.5000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">100</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">grossFloorArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:area>
						<nrg3:QualifiedArea>
							<nrg3:description>This is a type of floor area</nrg3:description>
							<nrg3:source>Area value source text</nrg3:source>
							<nrg3:value uom="m^2">90</nrg3:value>
							<nrg3:type codeSpace="area_codeSpace">energyReferenceArea</nrg3:type>
						</nrg3:QualifiedArea>
					</nrg3:area>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">375</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">grossVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:volume>
						<nrg3:QualifiedVolume>
							<nrg3:description>This is a type of volume</nrg3:description>
							<nrg3:source>Volume value source text</nrg3:source>
							<nrg3:value uom="m^3">243</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">energyReferenceVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:buildingUnit xlink:href="#h8_id_building_unit_2"/>
					<nrg3:type codeSpace="usageZone_codeSpace_123">residential</nrg3:type>
					<nrg3:isPrimary>true</nrg3:isPrimary>
					<nrg3:numberOfBuildingUnits>1</nrg3:numberOfBuildingUnits>
					<nrg3:internalHeatGains uom="W/m^2">1.4</nrg3:internalHeatGains>
					<nrg3:internalHeatGainsConvectiveFraction uom="unit interval">0.3</nrg3:internalHeatGainsConvectiveFraction>
					<nrg3:internalHeatGainsLatentFraction uom="unit interval">0.2</nrg3:internalHeatGainsLatentFraction>
					<nrg3:internalHeatGainsRadiantFraction uom="unit interval">0.5</nrg3:internalHeatGainsRadiantFraction>
					<nrg3:occupiedBy>
						<nrg3:Occupants gml:id="h8_id_occupants_2">
							<gml:description>This is Occupants 2</gml:description>
							<gml:name>Occupants 2</gml:name>
							<nrg3:type codeSpace="occ_codeSpace_xyz">residents</nrg3:type>
							<nrg3:numberOfOccupants>2</nrg3:numberOfOccupants>
							<nrg3:heatDissipation uom="W/m^2">0.7</nrg3:heatDissipation>
							<nrg3:heatDissipationConvectiveFraction uom="unit interval">0.3</nrg3:heatDissipationConvectiveFraction>
							<nrg3:heatDissipationLatentFraction uom="unit interval">0.2</nrg3:heatDissipationLatentFraction>
							<nrg3:heatDissipationRadiantFraction uom="unit interval">0.5</nrg3:heatDissipationRadiantFraction>
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
		<bldg:Building gml:id="house9_lod2_no_window">
			<gml:description>The LoD2 house again, with one difference: no glass. Every wall states that all of its area is opaque.</gml:description>
			<gml:name>Report house - LoD2 no window</gml:name>
			<core:creationDate>2024-09-25</core:creationDate>
			<nrg3:referencePoint>
				<gml:Point srsName="EPSG:32633" srsDimension="3">
					<gml:pos>291465.0000 5041905.0000 4.5000</gml:pos>
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
				<gml:MultiSurface gml:id="h9_id_building_1_footprint_MultiSurf" srsName="EPSG:32633" srsDimension="3">
					<gml:surfaceMember>
						<gml:OrientableSurface orientation="-">
							<gml:baseSurface xlink:href="#h9_id_building_1_polygon_3"/>
						</gml:OrientableSurface>
					</gml:surfaceMember>
				</gml:MultiSurface>
			</bldg:lod0FootPrint>
			<bldg:lod1Solid>
				<gml:Solid gml:id="h9_id_building_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
					<gml:exterior>
						<gml:CompositeSurface gml:id="h9_id_building_1_lod1_CompSurf">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h9_id_building_1_lod1_Polygon_1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291460.0000 5041900.0000 0.0000 291460.0000 5041910.0000 0.0000 291470.0000 5041910.0000 0.0000 291470.0000 5041900.0000 0.0000 291460.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="h9_id_building_1_lod1_Polygon_2">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291460.0000 5041900.0000 0.0000 291470.0000 5041900.0000 0.0000 291470.0000 5041900.0000 7.5000 291460.0000 5041900.0000 7.5000 291460.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="h9_id_building_1_lod1_Polygon_3">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291470.0000 5041900.0000 0.0000 291470.0000 5041910.0000 0.0000 291470.0000 5041910.0000 7.5000 291470.0000 5041900.0000 7.5000 291470.0000 5041900.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="h9_id_building_1_lod1_Polygon_4">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291470.0000 5041910.0000 0.0000 291460.0000 5041910.0000 0.0000 291460.0000 5041910.0000 7.5000 291470.0000 5041910.0000 7.5000 291470.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="h9_id_building_1_lod1_Polygon_5">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291460.0000 5041910.0000 0.0000 291460.0000 5041900.0000 0.0000 291460.0000 5041900.0000 7.5000 291460.0000 5041910.0000 7.5000 291460.0000 5041910.0000 0.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
							<gml:surfaceMember>
								<gml:Polygon gml:id="h9_id_building_1_lod1_Polygon_6">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291460.0000 5041900.0000 7.5000 291470.0000 5041900.0000 7.5000 291470.0000 5041910.0000 7.5000 291460.0000 5041910.0000 7.5000 291460.0000 5041900.0000 7.5000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:CompositeSurface>
					</gml:exterior>
				</gml:Solid>
			</bldg:lod1Solid>
			<bldg:lod2Solid>
				<gml:Solid gml:id="h9_id_building_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
					<gml:exterior>
						<gml:CompositeSurface gml:id="h9_id_building_1_lod2_CompSurf">
							<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_4"/>
							<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_5"/>
							<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_7"/>
							<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_1"/>
							<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_2"/>
							<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_3"/>
							<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_cs1"/>
						</gml:CompositeSurface>
					</gml:exterior>
				</gml:Solid>
			</bldg:lod2Solid>
			<bldg:boundedBy>
				<bldg:GroundSurface gml:id="h9_id_building_1_groundsurface_1">
					<gml:description>This is GroundSurface 1 (Building 1)</gml:description>
					<gml:name>GroundSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_ground_1"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291465.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h9_id_building_1_groundsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h9_id_building_1_polygon_3">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291460.0000 5041900.0000 0.0000 291460.0000 5041910.0000 0.0000 291470.0000 5041910.0000 0.0000 291470.0000 5041900.0000 0.0000 291460.0000 5041900.0000 0.0000</gml:posList>
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
				<bldg:RoofSurface gml:id="h9_id_building_1_roofsurface_1">
					<gml:description>This is RoofSurface 1 (Building 1)</gml:description>
					<gml:name>RoofSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291465.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h9_id_building_1_roofsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h9_id_building_1_polygon_1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291460.0000 5041900.0000 6.0000 291465.0000 5041900.0000 9.0000 291465.0000 5041910.0000 9.0000 291460.0000 5041910.0000 6.0000 291460.0000 5041900.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">270</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfHeatCapacity uom="kJ/(m^2*K)">508</nrg3:bdgBdrySurfHeatCapacity>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">30.9638</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfOpaqueSurfaceArea>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfThickness uom="mm">365</nrg3:bdgBdrySurfThickness>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">58.3095</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:RoofSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:RoofSurface gml:id="h9_id_building_1_roofsurface_2">
					<gml:description>This is RoofSurface 2 (Building 1)</gml:description>
					<gml:name>RoofSurface 2 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291465.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h9_id_building_1_roofsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h9_id_building_1_polygon_2">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291465.0000 5041900.0000 9.0000 291470.0000 5041900.0000 6.0000 291470.0000 5041910.0000 6.0000 291465.0000 5041910.0000 9.0000 291465.0000 5041900.0000 9.0000</gml:posList>
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
				<bldg:WallSurface gml:id="h9_id_building_1_wallsurface_1">
					<gml:description>This is WallSurface 1 (Building 1)</gml:description>
					<gml:name>WallSurface 1 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291465.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h9_id_building_1_wallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h9_id_building_1_polygon_5">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291460.0000 5041900.0000 0.0000 291470.0000 5041900.0000 0.0000 291470.0000 5041900.0000 6.0000 291465.0000 5041900.0000 9.0000 291460.0000 5041900.0000 6.0000 291460.0000 5041900.0000 0.0000</gml:posList>
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
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">75</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface gml:id="h9_id_building_1_wallsurface_2">
					<gml:description>This is WallSurface 2 (Building 1)</gml:description>
					<gml:name>WallSurface 2 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291465.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h9_id_building_1_wallsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h9_id_building_1_polygon_4">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291460.0000 5041910.0000 0.0000 291460.0000 5041910.0000 6.0000 291465.0000 5041910.0000 9.0000 291470.0000 5041910.0000 6.0000 291470.0000 5041910.0000 0.0000 291460.0000 5041910.0000 0.0000</gml:posList>
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
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">75</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface gml:id="h9_id_building_1_wallsurface_3">
					<gml:description>This is WallSurface 3 (Building 1)</gml:description>
					<gml:name>WallSurface 3 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291465.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h9_id_building_1_wallsurface_3_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h9_id_building_1_polygon_7">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291460.0000 5041900.0000 0.0000 291460.0000 5041900.0000 6.0000 291460.0000 5041910.0000 6.0000 291460.0000 5041910.0000 0.0000 291460.0000 5041900.0000 0.0000</gml:posList>
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
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:boundedBy>
				<bldg:WallSurface gml:id="h9_id_building_1_wallsurface_4">
					<gml:description>This is WallSurface 4 (Building 1)</gml:description>
					<gml:name>WallSurface 4 (Building 1)</gml:name>
					<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291465.0000 5041905.0000 4.5000</gml:pos>
						</gml:Point>
					</nrg3:referencePoint>
					<bldg:lod2MultiSurface>
						<gml:MultiSurface gml:id="h9_id_building_1_wallsurface_4_lod2_geom" srsName="EPSG:32633" srsDimension="3">
							<gml:surfaceMember>
								<gml:Polygon gml:id="h9_id_building_1_polygon_cs1">
									<gml:exterior>
										<gml:LinearRing>
											<gml:posList>291470.0000 5041910.0000 6.0000 291470.0000 5041900.0000 6.0000 291470.0000 5041900.0000 0.0000 291470.0000 5041910.0000 0.0000 291470.0000 5041910.0000 6.0000</gml:posList>
										</gml:LinearRing>
									</gml:exterior>
								</gml:Polygon>
							</gml:surfaceMember>
						</gml:MultiSurface>
					</bldg:lod2MultiSurface>
					<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
					<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
					<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
					<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
					<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
					<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
					<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
				</bldg:WallSurface>
			</bldg:boundedBy>
			<bldg:address>
				<core:Address gml:id="h9_id_address_1">
					<core:xalAddress>
						<ns5:AddressDetails>
							<ns5:Country>
								<ns5:CountryNameCode>ALD</ns5:CountryNameCode>
								<ns5:CountryName>Bespin Territories</ns5:CountryName>
								<ns5:Locality Type="Town">
									<ns5:LocalityName>Alderaan</ns5:LocalityName>
									<ns5:Thoroughfare Type="Street">
										<ns5:ThoroughfareNumber>1</ns5:ThoroughfareNumber>
										<ns5:ThoroughfareName>Bespin Square</ns5:ThoroughfareName>
									</ns5:Thoroughfare>
									<ns5:PostalCode>
										<ns5:PostalCodeNumber>1977SW</ns5:PostalCodeNumber>
									</ns5:PostalCode>
								</ns5:Locality>
							</ns5:Country>
						</ns5:AddressDetails>
					</core:xalAddress>
					<core:multiPoint>
						<gml:MultiPoint srsName="EPSG:32633" srsDimension="3">
							<gml:pointMember>
								<gml:Point>
									<gml:pos>291465.0000 5041905.0000 0.0000</gml:pos>
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
			<nrg3:bdgType codeSpace="bdgType_codeSpace">singleFamilyHouse</nrg3:bdgType>
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
				<nrg3:BuildingUnit gml:id="h9_id_building_unit_1">
					<gml:description>This is BuildingUnit 1</gml:description>
					<gml:name>BuildingUnit 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291465.0000 5041905.0000 4.5000</gml:pos>
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
							<nrg3:value uom="m^2">180</nrg3:value>
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
							<nrg3:value uom="m^3">486</nrg3:value>
							<nrg3:type codeSpace="volume_codeSpace">energyReferenceVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:lod1Solid>
						<gml:Solid gml:id="h9_id_building_unit_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="h9_id_building_unit_1_lod1_CompSurf">
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_42e7489a-e3f6-4a45-be2a-fbe735cd2ef8"/>
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_3f00920e-17c2-41f1-acb7-e223b1199044"/>
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_ba78c9d7-0ed7-49b8-b107-d939f0186284"/>
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_1406dd4c-f070-4022-835b-50018fdc6c54"/>
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_694c7871-d386-4e68-9c88-f62140080992"/>
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_945a1c0f-31f2-4bad-9599-9aaecf0ac7ac"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="h9_id_building_unit_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="h9_id_building_unit_1_lod2_CompSurf">
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_6e3e783e-b75a-4436-9f49-ed7d5346bca0"/>
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_ed5e64ff-65d6-4da8-bd65-a726d53494fa"/>
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_b7a25cfb-c3c6-490c-8628-42c50627d42c"/>
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_204ef154-fa62-4200-b3f2-4bb427b7b42e"/>
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_1f26fb83-a013-4528-9b75-b7eed4d07b70"/>
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_0f7e6a7d-4c78-4f23-a531-482e254f1aae"/>
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_8c107b31-166a-4b7c-aec1-4800b9dd396c"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:lod3Solid>
						<gml:Solid gml:id="h9_id_building_unit_1_lod3_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="h9_id_building_unit_1_lod3_CompSurf">
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_b9c018da-8461-4762-99c2-1cae1fc6dfa2"/>
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_efca560a-2e79-4536-9e21-4e23aacef253"/>
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_80ecaada-e49a-4e7d-8955-367405f503fb"/>
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_4dbfd338-5c11-42cd-b60d-68038c5dc78f"/>
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_5103fb6c-6d3f-4756-aa3a-586039a1938f"/>
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_2d5f403b-eac9-46ff-abbe-579c1416747a"/>
									<gml:surfaceMember xlink:href="#h9_Polygon_UUID_934e4b6a-022d-4cf7-8426-883da175edd4"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod3Solid>
					<nrg3:type codeSpace="buildingUnit_codeSpace_123">residential</nrg3:type>
					<nrg3:numberOfRooms>4</nrg3:numberOfRooms>
					<nrg3:ownershipType codeSpace="ownership_type_codeSpace_abc">corporation</nrg3:ownershipType>
					<nrg3:address xlink:href="#h9_id_address_1"/>
				</nrg3:BuildingUnit>
			</nrg3:buildingUnit>
			<nrg3:thermalZone>
				<nrg3:ThermalZone gml:id="h9_id_thermal_zone_1">
					<gml:description>This is ThermalZone 1</gml:description>
					<gml:name>ThermalZone 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291465.0000 5041905.0000 4.5000</gml:pos>
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
						<gml:Solid gml:id="h9_id_thermal_zone_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="h9_id_thermal_zone_1_lod1_CompSurf">
									<gml:surfaceMember xlink:href="#h9_id_building_1_lod1_Polygon_1"/>
									<gml:surfaceMember xlink:href="#h9_id_building_1_lod1_Polygon_2"/>
									<gml:surfaceMember xlink:href="#h9_id_building_1_lod1_Polygon_3"/>
									<gml:surfaceMember xlink:href="#h9_id_building_1_lod1_Polygon_4"/>
									<gml:surfaceMember xlink:href="#h9_id_building_1_lod1_Polygon_5"/>
									<gml:surfaceMember xlink:href="#h9_id_building_1_lod1_Polygon_6"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="h9_id_thermal_zone_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="h9_id_thermal_zone_1_lod2_CompSurf">
									<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_4"/>
									<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_5"/>
									<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_7"/>
									<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_1"/>
									<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_2"/>
									<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_3"/>
									<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_cs1"/>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:heatCapacity uom="J/K">46800000</nrg3:heatCapacity>
					<nrg3:infiltrationRate uom="1/h">0.3</nrg3:infiltrationRate>
					<nrg3:isCooled>false</nrg3:isCooled>
					<nrg3:isHeated>true</nrg3:isHeated>
					<nrg3:coincidesWithLod2Hull>false</nrg3:coincidesWithLod2Hull>
					<nrg3:coincidesWithLod3Hull>false</nrg3:coincidesWithLod3Hull>
					<nrg3:thermalBoundary>
						<bldg:GroundSurface gml:id="h9_id_thermal_zone_1_groundsurface_1">
							<gml:description>This is (ThermalBoundary) GroundSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) GroundSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_ground_1"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291465.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h9_id_thermal_zone_1_groundsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_3"/>
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
						<bldg:RoofSurface gml:id="h9_id_thermal_zone_1_roofsurface_1">
							<gml:description>This is (ThermalBoundary) RoofSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) RoofSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291465.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h9_id_thermal_zone_1_roofsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_1"/>
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
						<bldg:RoofSurface gml:id="h9_id_thermal_zone_1_roofsurface_2">
							<gml:description>This is (ThermalBoundary) RoofSurface 2 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) RoofSurface 2 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_roof_3"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291465.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h9_id_thermal_zone_1_roofsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_2"/>
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
						<bldg:WallSurface gml:id="h9_id_thermal_zone_1_wallsurface_1">
							<gml:description>This is (ThermalBoundary) WallSurface 1 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 1 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291465.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h9_id_thermal_zone_1_wallsurface_1_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_5"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">180</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">75</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">75</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:WallSurface gml:id="h9_id_thermal_zone_1_wallsurface_2">
							<gml:description>This is (ThermalBoundary) WallSurface 2 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 2 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291465.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h9_id_thermal_zone_1_wallsurface_2_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_4"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">0</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">75</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">75</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:WallSurface gml:id="h9_id_thermal_zone_1_wallsurface_3">
							<gml:description>This is (ThermalBoundary) WallSurface 3 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 3 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291465.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h9_id_thermal_zone_1_wallsurface_3_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_7"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">270</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
					</nrg3:thermalBoundary>
					<nrg3:thermalBoundary>
						<bldg:WallSurface gml:id="h9_id_thermal_zone_1_wallsurface_4">
							<gml:description>This is (ThermalBoundary) WallSurface 4 (ThermalZone 1)</gml:description>
							<gml:name>(ThermalBoundary) WallSurface 4 (ThermalZone 1)</gml:name>
							<nrg3:layeredConstruction xlink:href="#id_layered_construction_wall_2"/>
							<nrg3:referencePoint>
								<gml:Point srsName="EPSG:32633" srsDimension="3">
									<gml:pos>291465.0000 5041905.0000 4.5000</gml:pos>
								</gml:Point>
							</nrg3:referencePoint>
							<bldg:lod2MultiSurface>
								<gml:MultiSurface gml:id="h9_id_thermal_zone_1_wallsurface_4_lod2_geom" srsName="EPSG:32633" srsDimension="3">
									<gml:surfaceMember xlink:href="#h9_id_building_1_polygon_cs1"/>
								</gml:MultiSurface>
							</bldg:lod2MultiSurface>
							<nrg3:bdgBdrySurfAzimuth uom="decimal degree">90</nrg3:bdgBdrySurfAzimuth>
							<nrg3:bdgBdrySurfGroundViewFactor uom="unit interval">0.5</nrg3:bdgBdrySurfGroundViewFactor>
							<nrg3:bdgBdrySurfInclination uom="decimal degree">90</nrg3:bdgBdrySurfInclination>
							<nrg3:bdgBdrySurfIsAdiabatic>false</nrg3:bdgBdrySurfIsAdiabatic>
							<nrg3:bdgBdrySurfOpaqueSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfOpaqueSurfaceArea>
							<nrg3:bdgBdrySurfOpeningToSurfaceRatio uom="unit interval">0</nrg3:bdgBdrySurfOpeningToSurfaceRatio>
							<nrg3:bdgBdrySurfSkyViewFactor uom="unit interval">0.6</nrg3:bdgBdrySurfSkyViewFactor>
							<nrg3:bdgBdrySurfTotalSurfaceArea uom="m^2">60</nrg3:bdgBdrySurfTotalSurfaceArea>
						</bldg:WallSurface>
					</nrg3:thermalBoundary>
				</nrg3:ThermalZone>
			</nrg3:thermalZone>
			<nrg3:usageZone>
				<nrg3:UsageZone gml:id="h9_id_usage_zone_1">
					<gml:description>This is UsageZone 1</gml:description>
					<gml:name>UsageZone 1</gml:name>
					<nrg3:referencePoint>
						<gml:Point srsName="EPSG:32633" srsDimension="3">
							<gml:pos>291465.0000 5041905.0000 4.5000</gml:pos>
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
							<nrg3:type codeSpace="volume_codeSpace">energyReferenceVolume</nrg3:type>
						</nrg3:QualifiedVolume>
					</nrg3:volume>
					<nrg3:lod1Solid>
						<gml:Solid gml:id="h9_id_usage_zone_1_lod1_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="h9_id_usage_zone_1_lod1_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_42e7489a-e3f6-4a45-be2a-fbe735cd2ef8">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291460.0000 5041900.0000 0.0000 291460.0000 5041910.0000 0.0000 291470.0000 5041910.0000 0.0000 291470.0000 5041900.0000 0.0000 291460.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_3f00920e-17c2-41f1-acb7-e223b1199044">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291460.0000 5041900.0000 0.0000 291470.0000 5041900.0000 0.0000 291470.0000 5041900.0000 7.5000 291460.0000 5041900.0000 7.5000 291460.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_ba78c9d7-0ed7-49b8-b107-d939f0186284">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291470.0000 5041900.0000 0.0000 291470.0000 5041910.0000 0.0000 291470.0000 5041910.0000 7.5000 291470.0000 5041900.0000 7.5000 291470.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_1406dd4c-f070-4022-835b-50018fdc6c54">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291470.0000 5041910.0000 0.0000 291460.0000 5041910.0000 0.0000 291460.0000 5041910.0000 7.5000 291470.0000 5041910.0000 7.5000 291470.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_694c7871-d386-4e68-9c88-f62140080992">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291460.0000 5041910.0000 0.0000 291460.0000 5041900.0000 0.0000 291460.0000 5041900.0000 7.5000 291460.0000 5041910.0000 7.5000 291460.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_945a1c0f-31f2-4bad-9599-9aaecf0ac7ac">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291460.0000 5041900.0000 7.5000 291470.0000 5041900.0000 7.5000 291470.0000 5041910.0000 7.5000 291460.0000 5041910.0000 7.5000 291460.0000 5041900.0000 7.5000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod1Solid>
					<nrg3:lod2Solid>
						<gml:Solid gml:id="h9_id_usage_zone_1_lod2_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="h9_id_usage_zone_1_lod2_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_b9c018da-8461-4762-99c2-1cae1fc6dfa2">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291460.0000 5041910.0000 0.0000 291460.0000 5041910.0000 6.0000 291465.0000 5041910.0000 9.0000 291470.0000 5041910.0000 6.0000 291470.0000 5041910.0000 0.0000 291460.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_efca560a-2e79-4536-9e21-4e23aacef253">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291460.0000 5041900.0000 0.0000 291470.0000 5041900.0000 0.0000 291470.0000 5041900.0000 6.0000 291465.0000 5041900.0000 9.0000 291460.0000 5041900.0000 6.0000 291460.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_80ecaada-e49a-4e7d-8955-367405f503fb">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291460.0000 5041900.0000 0.0000 291460.0000 5041900.0000 6.0000 291460.0000 5041910.0000 6.0000 291460.0000 5041910.0000 0.0000 291460.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_4dbfd338-5c11-42cd-b60d-68038c5dc78f">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291460.0000 5041900.0000 6.0000 291465.0000 5041900.0000 9.0000 291465.0000 5041910.0000 9.0000 291460.0000 5041910.0000 6.0000 291460.0000 5041900.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_5103fb6c-6d3f-4756-aa3a-586039a1938f">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291465.0000 5041900.0000 9.0000 291470.0000 5041900.0000 6.0000 291470.0000 5041910.0000 6.0000 291465.0000 5041910.0000 9.0000 291465.0000 5041900.0000 9.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_2d5f403b-eac9-46ff-abbe-579c1416747a">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291460.0000 5041900.0000 0.0000 291460.0000 5041910.0000 0.0000 291470.0000 5041910.0000 0.0000 291470.0000 5041900.0000 0.0000 291460.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_934e4b6a-022d-4cf7-8426-883da175edd4">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291470.0000 5041910.0000 6.0000 291470.0000 5041900.0000 6.0000 291470.0000 5041900.0000 0.0000 291470.0000 5041910.0000 0.0000 291470.0000 5041910.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
								</gml:CompositeSurface>
							</gml:exterior>
						</gml:Solid>
					</nrg3:lod2Solid>
					<nrg3:lod3Solid>
						<gml:Solid gml:id="h9_id_usage_zone_1_lod3_Solid" srsName="EPSG:32633" srsDimension="3">
							<gml:exterior>
								<gml:CompositeSurface gml:id="h9_id_usage_zone_1_lod3_CompSurf">
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_6e3e783e-b75a-4436-9f49-ed7d5346bca0">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291460.0000 5041910.0000 0.0000 291460.0000 5041910.0000 6.0000 291465.0000 5041910.0000 9.0000 291470.0000 5041910.0000 6.0000 291470.0000 5041910.0000 0.0000 291460.0000 5041910.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_ed5e64ff-65d6-4da8-bd65-a726d53494fa">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291460.0000 5041900.0000 0.0000 291470.0000 5041900.0000 0.0000 291470.0000 5041900.0000 6.0000 291465.0000 5041900.0000 9.0000 291460.0000 5041900.0000 6.0000 291460.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_b7a25cfb-c3c6-490c-8628-42c50627d42c">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291460.0000 5041900.0000 0.0000 291460.0000 5041900.0000 6.0000 291460.0000 5041910.0000 6.0000 291460.0000 5041910.0000 0.0000 291460.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_204ef154-fa62-4200-b3f2-4bb427b7b42e">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291460.0000 5041900.0000 6.0000 291465.0000 5041900.0000 9.0000 291465.0000 5041910.0000 9.0000 291460.0000 5041910.0000 6.0000 291460.0000 5041900.0000 6.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_1f26fb83-a013-4528-9b75-b7eed4d07b70">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291465.0000 5041900.0000 9.0000 291470.0000 5041900.0000 6.0000 291470.0000 5041910.0000 6.0000 291465.0000 5041910.0000 9.0000 291465.0000 5041900.0000 9.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_0f7e6a7d-4c78-4f23-a531-482e254f1aae">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291460.0000 5041900.0000 0.0000 291460.0000 5041910.0000 0.0000 291470.0000 5041910.0000 0.0000 291470.0000 5041900.0000 0.0000 291460.0000 5041900.0000 0.0000</gml:posList>
												</gml:LinearRing>
											</gml:exterior>
										</gml:Polygon>
									</gml:surfaceMember>
									<gml:surfaceMember>
										<gml:Polygon gml:id="h9_Polygon_UUID_8c107b31-166a-4b7c-aec1-4800b9dd396c">
											<gml:exterior>
												<gml:LinearRing>
													<gml:posList>291470.0000 5041910.0000 6.0000 291470.0000 5041900.0000 6.0000 291470.0000 5041900.0000 0.0000 291470.0000 5041910.0000 0.0000 291470.0000 5041910.0000 6.0000</gml:posList>
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
					<nrg3:internalHeatGains uom="W/m^2">1.4</nrg3:internalHeatGains>
					<nrg3:internalHeatGainsConvectiveFraction uom="unit interval">0.3</nrg3:internalHeatGainsConvectiveFraction>
					<nrg3:internalHeatGainsLatentFraction uom="unit interval">0.2</nrg3:internalHeatGainsLatentFraction>
					<nrg3:internalHeatGainsRadiantFraction uom="unit interval">0.5</nrg3:internalHeatGainsRadiantFraction>
					<nrg3:occupiedBy>
						<nrg3:Occupants gml:id="h9_id_occupants_1">
							<gml:description>This is Occupants 1</gml:description>
							<gml:name>Occupants 1</gml:name>
							<nrg3:type codeSpace="occ_codeSpace_xyz">residents</nrg3:type>
							<nrg3:numberOfOccupants>4</nrg3:numberOfOccupants>
							<nrg3:heatDissipation uom="W/m^2">0.7</nrg3:heatDissipation>
							<nrg3:heatDissipationConvectiveFraction uom="unit interval">0.3</nrg3:heatDissipationConvectiveFraction>
							<nrg3:heatDissipationLatentFraction uom="unit interval">0.2</nrg3:heatDissipationLatentFraction>
							<nrg3:heatDissipationRadiantFraction uom="unit interval">0.5</nrg3:heatDissipationRadiantFraction>
							<nrg3:averageDietType codeSpace="diet_codeSpace">omnivorous</nrg3:averageDietType>
							<nrg3:averageIncomeLevel codeSpace="income_level codeSpace">middle</nrg3:averageIncomeLevel>
							<nrg3:averageInstructionLevel codeSpace="instruction_level_codeSpace">university</nrg3:averageInstructionLevel>
						</nrg3:Occupants>
					</nrg3:occupiedBy>
				</nrg3:UsageZone>
			</nrg3:usageZone>
		</bldg:Building>
	</core:cityObjectMember>
	</core:CityModel>
