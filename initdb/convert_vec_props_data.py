#!/usr/bin/env python3
"""
CIM Wizard Vector Properties Data Converter
Converts vec_props_data.sql to new schema format with proper column ordering and schema references.
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
            
            # Format string values with proper quotes
            const_period_formatted = f"'{const_period}'" if const_period != "NULL" else "NULL"
            type_val_formatted = f"'{type_val}'" if type_val != "NULL" else "NULL"
            const_TABULA_formatted = f"'{const_TABULA}'" if const_TABULA != "NULL" else "NULL"
            
            # Format the new INSERT statement
            new_content += f"('{scenario_id}', '{building_id}', '{project_id}', {lod}, {height}, {area}, {volume}, {floors}, {const_period_formatted}, {n_family}, {n_people}, {type_val_formatted}, {const_TABULA_formatted}, {const_year}, {created_at}, {updated_at})"
            
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

def main():
    """Main function to convert vec_props_data.sql."""
    print("Starting Vector Properties Data Conversion...")
    
    # Create initdb directory if it doesn't exist
    initdb_dir = Path("initdb")
    initdb_dir.mkdir(exist_ok=True)
    
    # Read source file
    source_path = initdb_dir / "vec_props_data.sql"
    content = read_file_content(source_path)
    
    if content:
        # Convert content
        new_content = convert_vec_props_data(content)
        
        if new_content:
            # Write target file
            target_path = initdb_dir / "14-vec_props_data.sql"
            write_file_content(target_path, new_content)
            print("Vector properties data conversion completed!")
        else:
            print("Failed to convert vec_props_data.sql")
    else:
        print("Could not read vec_props_data.sql")

if __name__ == "__main__":
    main()
