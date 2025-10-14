#!/usr/bin/env python3
"""
CIM Wizard Census Data Converter
Converts census_data.sql to new schema format with proper column ordering and schema references.
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
            geometry_raw = values[2].strip("'\"")
            crs = values[3].strip("'\"")
            
            # Format geometry as plain strings (same as building data)
            if geometry_raw and geometry_raw != 'NULL':
                geometry = f"'{geometry_raw}'"
            else:
                geometry = "NULL"
            
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

def main():
    """Main function to convert census_data.sql."""
    print("Starting Census Data Conversion...")
    
    # Create initdb directory if it doesn't exist
    initdb_dir = Path("initdb")
    initdb_dir.mkdir(exist_ok=True)
    
    # Read source file
    source_path = initdb_dir / "census_data.sql"
    content = read_file_content(source_path)
    
    if content:
        # Convert content
        new_content = convert_census_data(content)
        
        if new_content:
            # Write target file
            target_path = initdb_dir / "15-census_data.sql"
            write_file_content(target_path, new_content)
            print("Census data conversion completed!")
        else:
            print("Failed to convert census_data.sql")
    else:
        print("Could not read census_data.sql")

if __name__ == "__main__":
    main()
