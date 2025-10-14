#!/usr/bin/env python3
"""
CIM Wizard Vector Building Data Converter
Converts vec_bld_data.sql to new schema format with proper column ordering and schema references.
"""

import os
import re
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
            geometry_raw = values[3].strip("'\"")
            source = values[4].strip("'\"")
            census_id = values[5]
            created_at = values[6]
            updated_at = values[7]
            surfaces = values[8] if len(values) > 8 else "NULL"
            
            # Format geometry as plain strings (same as building data)
            if geometry_raw and geometry_raw != 'NULL':
                geometry = f"'{geometry_raw}'"
            else:
                geometry = "NULL"
            
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

def main():
    """Main function to convert vec_bld_data.sql."""
    print("Starting Vector Building Data Conversion...")
    
    # Create initdb directory if it doesn't exist
    initdb_dir = Path("initdb")
    initdb_dir.mkdir(exist_ok=True)
    
    # Read source file
    source_path = initdb_dir / "vec_bld_data.sql"
    content = read_file_content(source_path)
    
    if content:
        # Convert content
        new_content = convert_vec_bld_data(content)
        
        if new_content:
            # Write target file
            target_path = initdb_dir / "12-vec_bld_data.sql"
            write_file_content(target_path, new_content)
            print("Vector building data conversion completed!")
        else:
            print("Failed to convert vec_bld_data.sql")
    else:
        print("Could not read vec_bld_data.sql")

if __name__ == "__main__":
    main()
