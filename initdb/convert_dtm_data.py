#!/usr/bin/env python3
"""
CIM Wizard DTM Data Converter
Converts dtm_data.sql to new schema format with proper column ordering and schema references.
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

def main():
    """Main function to convert dtm_data.sql."""
    print("Starting DTM Data Conversion...")
    
    # Create initdb directory if it doesn't exist
    initdb_dir = Path("initdb")
    initdb_dir.mkdir(exist_ok=True)
    
    # Read source file
    source_path = initdb_dir / "dtm_data.sql"
    content = read_file_content(source_path)
    
    if content:
        # Convert content
        new_content = convert_dtm_data(content)
        
        if new_content:
            # Write target file
            target_path = initdb_dir / "16-dtm_data.sql"
            write_file_content(target_path, new_content)
            print("DTM data conversion completed!")
        else:
            print("Failed to convert dtm_data.sql")
    else:
        print("Could not read dtm_data.sql")

if __name__ == "__main__":
    main()
