#!/usr/bin/env python3
"""
CIM Wizard Vector Scenario Data Converter
Converts vec_scen_data.sql to new schema format with proper column ordering and schema references.
"""

import os
import re
import uuid
from pathlib import Path

def read_file_content(file_path):
    """Read file content safely with multiple encoding attempts."""
    encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"Successfully read {file_path} with {encoding} encoding")
            return content
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            print(f"Warning: File {file_path} not found")
            return None
        except Exception as e:
            print(f"Error reading {file_path} with {encoding}: {e}")
            continue
    
    print(f"Could not read {file_path} with any of the attempted encodings: {encodings}")
    return None

def write_file_content(file_path, content):
    """Write content to file safely."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {file_path}")
    except Exception as e:
        print(f"Error writing {file_path}: {e}")

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
        
        # Expected format: (id, project_id, scenario_name, project_name, 'baseline', boundary_geom, center_geom, zoom, crs, census_boundary_geom, created_at, updated_at)
        if len(values) >= 12:
            # Generate new UUID for scenario_id
            scenario_id = str(uuid.uuid4())
            project_id = values[1].strip("'\"")
            scenario_name = values[2].strip("'\"")
            project_name = values[3].strip("'\"")
            # Skip values[4] which is 'baseline'
            
            # Handle geometry values properly
            boundary_geom = values[5].strip("'\"")
            center_geom = values[6].strip("'\"")
            census_boundary_geom = values[9].strip("'\"")
            
            # Format geometry as plain strings (same as building data)
            if boundary_geom and boundary_geom != 'NULL':
                boundary = f"'{boundary_geom}'"
            else:
                boundary = "NULL"
                
            if center_geom and center_geom != 'NULL':
                center = f"'{center_geom}'"
            else:
                center = "NULL"
            
            # Skip census_boundary_geom for now (not in new schema)
            
            zoom = values[7]
            crs = values[8]
            created_at = values[10]
            updated_at = values[11]
            
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

def main():
    """Main function to convert vec_scen_data.sql."""
    print("Starting Vector Scenario Data Conversion...")
    
    # Create initdb directory if it doesn't exist
    initdb_dir = Path("initdb")
    initdb_dir.mkdir(exist_ok=True)
    
    # Read source file
    source_path = initdb_dir / "vec_scen_data.sql"
    content = read_file_content(source_path)
    
    if content:
        # Convert content
        new_content = convert_vec_scen_data(content)
        
        if new_content:
            # Write target file
            target_path = initdb_dir / "13-vec_scen_data.sql"
            write_file_content(target_path, new_content)
            print("Vector scenario data conversion completed!")
        else:
            print("Failed to convert vec_scen_data.sql")
    else:
        print("Could not read vec_scen_data.sql")

if __name__ == "__main__":
    main()
