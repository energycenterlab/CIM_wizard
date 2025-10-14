#!/usr/bin/env python3
"""
CIM Wizard Data File Converter
Converts old data files to new schema format with proper column ordering and schema references.
"""

import os
import re
import uuid
from pathlib import Path

def read_file_content(file_path):
    """Read file content safely."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: File {file_path} not found")
        return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def write_file_content(file_path, content):
    """Write content to file safely."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {file_path}")
    except Exception as e:
        print(f"Error writing {file_path}: {e}")

def convert_vec_bld_data(content):
    """Convert vec_bld_data.sql to new schema format."""
    if not content:
        return None
    
    # Extract INSERT statements
    insert_pattern = r"INSERT INTO public\.cim_wizard_building VALUES \((.*?)\);"
    matches = re.findall(insert_pattern, content, re.DOTALL)
    
    if not matches:
        print("No INSERT statements found in vec_bld_data")
        return None
    
    new_content = """--
-- CIM Wizard Building Data
-- Clean version compatible with new schema structure
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: cim_wizard_building; Type: TABLE DATA; Schema: cim_vector; Owner: -
--

INSERT INTO cim_vector.cim_wizard_building (building_id, lod, building_geometry, building_geometry_source, census_id, created_at, updated_at, building_surfaces_lod12) VALUES 
"""
    
    # Process each INSERT statement
    for i, match in enumerate(matches):
        # Split the values by comma, but be careful with quoted strings
        values = []
        current_value = ""
        in_quotes = False
        quote_char = None
        
        for char in match:
            if char in ["'", '"'] and (not in_quotes or char == quote_char):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                else:
                    in_quotes = False
                    quote_char = None
            elif char == ',' and not in_quotes:
                values.append(current_value.strip())
                current_value = ""
                continue
            current_value += char
        
        if current_value.strip():
            values.append(current_value.strip())
        
        # Expected format: (id, building_id, lod, geometry, source, census_id, created_at, updated_at, surfaces)
        if len(values) >= 8:
            # Skip the first value (id) and use the rest
            building_id = values[1].strip("'\"")
            lod = values[2]
            geometry = values[3]
            source = values[4].strip("'\"")
            census_id = values[5]
            created_at = values[6]
            updated_at = values[7]
            surfaces = values[8] if len(values) > 8 else "NULL"
            
            # Format the new INSERT statement
            new_content += f"('{building_id}', {lod}, {geometry}, '{source}', {census_id}, {created_at}, {updated_at}, {surfaces})"
            
            if i < len(matches) - 1:
                new_content += ",\n"
            else:
                new_content += ";\n"
    
    new_content += """
--
-- Data insertion complete
--

SELECT 'Building data inserted successfully' as status;
"""
    
    return new_content

def convert_vec_scen_data(content):
    """Convert vec_scen_data.sql to new schema format."""
    if not content:
        return None
    
    # Extract INSERT statements
    insert_pattern = r"INSERT INTO public\.cim_wizard_project_scenario VALUES \((.*?)\);"
    matches = re.findall(insert_pattern, content, re.DOTALL)
    
    if not matches:
        print("No INSERT statements found in vec_scen_data")
        return None
    
    new_content = """--
-- CIM Wizard Project Scenario Data
-- Clean version compatible with new schema structure
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: cim_wizard_project_scenario; Type: TABLE DATA; Schema: cim_vector; Owner: -
--

INSERT INTO cim_vector.cim_wizard_project_scenario (scenario_id, project_id, scenario_name, project_name, project_boundary, project_center, project_zoom, project_crs, created_at, updated_at) VALUES 
"""
    
    # Process each INSERT statement
    for i, match in enumerate(matches):
        # Split the values by comma, but be careful with quoted strings
        values = []
        current_value = ""
        in_quotes = False
        quote_char = None
        
        for char in match:
            if char in ["'", '"'] and (not in_quotes or char == quote_char):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                else:
                    in_quotes = False
                    quote_char = None
            elif char == ',' and not in_quotes:
                values.append(current_value.strip())
                current_value = ""
                continue
            current_value += char
        
        if current_value.strip():
            values.append(current_value.strip())
        
        # Expected format: (id, project_id, scenario_name, project_name, boundary, center, zoom, crs, created_at, updated_at)
        if len(values) >= 10:
            # Generate new UUID for scenario_id
            scenario_id = str(uuid.uuid4())
            project_id = values[1].strip("'\"")
            scenario_name = values[2].strip("'\"")
            project_name = values[3].strip("'\"")
            boundary = values[4]
            center = values[5]
            zoom = values[6]
            crs = values[7]
            created_at = values[8]
            updated_at = values[9]
            
            # Format the new INSERT statement
            new_content += f"('{scenario_id}', '{project_id}', '{scenario_name}', '{project_name}', {boundary}, {center}, {zoom}, {crs}, {created_at}, {updated_at})"
            
            if i < len(matches) - 1:
                new_content += ",\n"
            else:
                new_content += ";\n"
    
    new_content += """
--
-- Data insertion complete
--

SELECT 'Project scenario data inserted successfully' as status;
"""
    
    return new_content

def convert_vec_props_data(content):
    """Convert vec_props_data.sql to new schema format."""
    if not content:
        return None
    
    # Extract INSERT statements
    insert_pattern = r"INSERT INTO public\.cim_wizard_building_properties VALUES \((.*?)\);"
    matches = re.findall(insert_pattern, content, re.DOTALL)
    
    if not matches:
        print("No INSERT statements found in vec_props_data")
        return None
    
    new_content = """--
-- CIM Wizard Building Properties Data
-- Clean version compatible with new schema structure
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: cim_wizard_building_properties; Type: TABLE DATA; Schema: cim_vector; Owner: -
--

INSERT INTO cim_vector.cim_wizard_building_properties (scenario_id, building_id, project_id, lod, height, area, volume, number_of_floors, const_period_census, n_family, n_people, type, const_TABULA, const_year, created_at, updated_at) VALUES 
"""
    
    # Process each INSERT statement
    for i, match in enumerate(matches):
        # Split the values by comma, but be careful with quoted strings
        values = []
        current_value = ""
        in_quotes = False
        quote_char = None
        
        for char in match:
            if char in ["'", '"'] and (not in_quotes or char == quote_char):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                else:
                    in_quotes = False
                    quote_char = None
            elif char == ',' and not in_quotes:
                values.append(current_value.strip())
                current_value = ""
                continue
            current_value += char
        
        if current_value.strip():
            values.append(current_value.strip())
        
        # Expected format: (id, project_id, scenario_id, lod, height, area, volume, floors, created_at, updated_at, building_id, const_period, n_family, n_people, type, const_TABULA, const_year)
        if len(values) >= 17:
            # Generate new UUIDs for scenario_id and building_id
            scenario_id = str(uuid.uuid4())
            building_id = str(uuid.uuid4())
            project_id = values[1].strip("'\"")
            lod = values[3]
            height = values[4]
            area = values[5]
            volume = values[6]
            floors = values[7]
            created_at = values[8]
            updated_at = values[9]
            const_period = values[11].strip("'\"") if values[11] != "NULL" else "NULL"
            n_family = values[12]
            n_people = values[13]
            type_val = values[14].strip("'\"") if values[14] != "NULL" else "NULL"
            const_TABULA = values[15].strip("'\"") if values[15] != "NULL" else "NULL"
            const_year = values[16]
            
            # Format the new INSERT statement
            new_content += f"('{scenario_id}', '{building_id}', '{project_id}', {lod}, {height}, {area}, {volume}, {floors}, {const_period}, {n_family}, {n_people}, {type_val}, {const_TABULA}, {const_year}, {created_at}, {updated_at})"
            
            if i < len(matches) - 1:
                new_content += ",\n"
            else:
                new_content += ";\n"
    
    new_content += """
--
-- Data insertion complete
--

SELECT 'Building properties data inserted successfully' as status;
"""
    
    return new_content

def convert_census_data(content):
    """Convert census_data.sql to new schema format."""
    if not content:
        return None
    
    # Extract INSERT statements
    insert_pattern = r"INSERT INTO public\.data_gateway_censusgeo VALUES \((.*?)\);"
    matches = re.findall(insert_pattern, content, re.DOTALL)
    
    if not matches:
        print("No INSERT statements found in census_data")
        return None
    
    new_content = """--
-- CIM Wizard Census Geography Data
-- Clean version compatible with new schema structure
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: censusgeo; Type: TABLE DATA; Schema: cim_census; Owner: -
--

INSERT INTO cim_census.censusgeo ("SEZ2011", geometry, crs, "Shape_Area", "CODREG", "REGIONE", "CODPRO", "PROVINCIA", "CODCOM", "COMUNE", "PROCOM", "NSEZ", "ACE", "CODLOC", "CODASC", "P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10", "P11", "P12", "P13", "P14", "P15", "P16", "P17", "P18", "P19", "P20", "P21", "P22", "P23", "P24", "P25", "P26", "P27", "P28", "P29", "P30", "P31", "P32", "P33", "P34", "P35", "P36", "P37", "P38", "P39", "P40", "P41", "P42", "P43", "P44", "P45", "P46", "P47", "P48", "P49", "P50", "P51", "P52", "P53", "P54", "P55", "P56", "P57", "P58", "P59", "P60", "P61", "P62", "P64", "P65", "P66", "P128", "P129", "P130", "P131", "P132", "P135", "P136", "P137", "P138", "P139", "P140", "ST1", "ST2", "ST3", "ST4", "ST5", "ST6", "ST7", "ST8", "ST9", "ST10", "ST11", "ST12", "ST13", "ST14", "ST15", "A2", "A3", "A5", "A6", "A7", "A44", "A46", "A47", "A48", "PF1", "PF2", "PF3", "PF4", "PF5", "PF6", "PF7", "PF8", "PF9", "E1", "E2", "E3", "E4", "E5", "E6", "E7", "E8", "E9", "E10", "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18", "E19", "E20", "E21", "E22", "E23", "E24", "E25", "E26", "E27", "E28", "E29", "E30", "E31", created_at, updated_at) VALUES 
"""
    
    # Process each INSERT statement
    for i, match in enumerate(matches):
        # Split the values by comma, but be careful with quoted strings
        values = []
        current_value = ""
        in_quotes = False
        quote_char = None
        
        for char in match:
            if char in ["'", '"'] and (not in_quotes or char == quote_char):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                else:
                    in_quotes = False
                    quote_char = None
            elif char == ',' and not in_quotes:
                values.append(current_value.strip())
                current_value = ""
                continue
            current_value += char
        
        if current_value.strip():
            values.append(current_value.strip())
        
        # Expected format: (id, SEZ2011, geometry, crs, shape_area, ... all other fields)
        if len(values) >= 3:
            # Skip the first value (id) and use SEZ2011 as primary key
            sez2011 = values[1]
            geometry = values[2]
            crs = values[3].strip("'\"")
            
            # Get all other values (skip id)
            other_values = values[4:] if len(values) > 4 else []
            
            # Add default timestamps
            other_values.extend(["NOW()", "NOW()"])
            
            # Format the new INSERT statement
            new_content += f"({sez2011}, {geometry}, '{crs}'"
            
            for val in other_values:
                new_content += f", {val}"
            
            new_content += ")"
            
            if i < len(matches) - 1:
                new_content += ",\n"
            else:
                new_content += ";\n"
    
    new_content += """
--
-- Data insertion complete
--

SELECT 'Census geography data inserted successfully' as status;
"""
    
    return new_content

def convert_dtm_data(content):
    """Convert dtm_data.sql to new schema format."""
    if not content:
        return None
    
    # Extract INSERT statements
    insert_pattern = r"INSERT INTO public\.dtm_raster VALUES \((.*?)\);"
    matches = re.findall(insert_pattern, content, re.DOTALL)
    
    if not matches:
        print("No INSERT statements found in dtm_data")
        return None
    
    new_content = """--
-- CIM Wizard DTM Raster Data
-- Clean version compatible with new schema structure
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: dtm_raster; Type: TABLE DATA; Schema: cim_raster; Owner: -
--

INSERT INTO cim_raster.dtm_raster (rid, rast, filename) VALUES 
"""
    
    # Process each INSERT statement
    for i, match in enumerate(matches):
        # Split the values by comma, but be careful with quoted strings
        values = []
        current_value = ""
        in_quotes = False
        quote_char = None
        
        for char in match:
            if char in ["'", '"'] and (not in_quotes or char == quote_char):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                else:
                    in_quotes = False
                    quote_char = None
            elif char == ',' and not in_quotes:
                values.append(current_value.strip())
                current_value = ""
                continue
            current_value += char
        
        if current_value.strip():
            values.append(current_value.strip())
        
        # Expected format: (rid, rast, filename)
        if len(values) >= 3:
            rid = values[0]
            rast = values[1]
            filename = values[2].strip("'\"")
            
            # Format the new INSERT statement
            new_content += f"({rid}, {rast}, '{filename}')"
            
            if i < len(matches) - 1:
                new_content += ",\n"
            else:
                new_content += ";\n"
    
    new_content += """
--
-- Data insertion complete
--

SELECT 'DTM raster data inserted successfully' as status;
"""
    
    return new_content

def convert_dsm_data(content):
    """Convert dsm_data.sql to new schema format."""
    if not content:
        return None
    
    # Extract INSERT statements
    insert_pattern = r"INSERT INTO public\.dsm_raster VALUES \((.*?)\);"
    matches = re.findall(insert_pattern, content, re.DOTALL)
    
    if not matches:
        print("No INSERT statements found in dsm_data")
        return None
    
    new_content = """--
-- CIM Wizard DSM Raster Data
-- Clean version compatible with new schema structure
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: dsm_raster; Type: TABLE DATA; Schema: cim_raster; Owner: -
--

INSERT INTO cim_raster.dsm_raster (rid, rast, filename) VALUES 
"""
    
    # Process each INSERT statement
    for i, match in enumerate(matches):
        # Split the values by comma, but be careful with quoted strings
        values = []
        current_value = ""
        in_quotes = False
        quote_char = None
        
        for char in match:
            if char in ["'", '"'] and (not in_quotes or char == quote_char):
                if not in_quotes:
                    in_quotes = True
                    quote_char = char
                else:
                    in_quotes = False
                    quote_char = None
            elif char == ',' and not in_quotes:
                values.append(current_value.strip())
                current_value = ""
                continue
            current_value += char
        
        if current_value.strip():
            values.append(current_value.strip())
        
        # Expected format: (rid, rast, filename)
        if len(values) >= 3:
            rid = values[0]
            rast = values[1]
            filename = values[2].strip("'\"")
            
            # Format the new INSERT statement
            new_content += f"({rid}, {rast}, '{filename}')"
            
            if i < len(matches) - 1:
                new_content += ",\n"
            else:
                new_content += ";\n"
    
    new_content += """
--
-- Data insertion complete
--

SELECT 'DSM raster data inserted successfully' as status;
"""
    
    return new_content

def main():
    """Main function to convert all data files."""
    print("Starting CIM Wizard Data File Conversion...")
    
    # Define file mappings
    file_mappings = [
        ("vec_bld_data.sql", "12-vec_bld_data.sql", convert_vec_bld_data),
        ("vec_scen_data.sql", "13-vec_scen_data.sql", convert_vec_scen_data),
        ("vec_props_data.sql", "14-vec_props_data.sql", convert_vec_props_data),
        ("census_data.sql", "15-census_data.sql", convert_census_data),
        ("dtm_data.sql", "16-dtm_data.sql", convert_dtm_data),
        ("dsm_data.sql", "17-dsm_data.sql", convert_dsm_data),
    ]
    
    # Create initdb directory if it doesn't exist
    initdb_dir = Path("initdb")
    initdb_dir.mkdir(exist_ok=True)
    
    for source_file, target_file, converter_func in file_mappings:
        print(f"\nProcessing {source_file}...")
        
        # Read source file
        source_path = initdb_dir / source_file
        content = read_file_content(source_path)
        
        if content:
            # Convert content
            new_content = converter_func(content)
            
            if new_content:
                # Write target file
                target_path = initdb_dir / target_file
                write_file_content(target_path, new_content)
            else:
                print(f"Failed to convert {source_file}")
        else:
            print(f"Could not read {source_file}")
    
    print("\nData file conversion completed!")
    print("\nGenerated files:")
    for _, target_file, _ in file_mappings:
        target_path = initdb_dir / target_file
        if target_path.exists():
            print(f"  OK: {target_file}")
        else:
            print(f"  FAILED: {target_file}")

if __name__ == "__main__":
    main()
