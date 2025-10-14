#!/usr/bin/env python3
"""
CIM Wizard DSM Data Converter
Converts dsm_data.sql to new schema format with proper column ordering and schema references.
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

def process_large_file_chunked(file_path, output_path):
    """Process large file in chunks to avoid memory issues."""
    encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
    
    for encoding in encodings:
        try:
            print(f"Attempting to process {file_path} with {encoding} encoding...")
            
            # Write header to output file
            with open(output_path, 'w', encoding='utf-8') as out_f:
                out_f.write("""--
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
""")
            
            # Process file in chunks
            chunk_size = 1024 * 1024  # 1MB chunks
            buffer = ""
            insert_count = 0
            first_insert = True
            
            with open(file_path, 'r', encoding=encoding) as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    
                    buffer += chunk
                    
                    # Process complete INSERT statements in buffer
                    while True:
                        # Find the next complete INSERT statement
                        insert_start = buffer.find("INSERT INTO public.dsm_raster VALUES (")
                        if insert_start == -1:
                            break
                        
                        # Find the end of this INSERT statement
                        insert_end = buffer.find(");", insert_start)
                        if insert_end == -1:
                            # Incomplete statement, keep in buffer
                            break
                        
                        # Extract the complete INSERT statement
                        insert_statement = buffer[insert_start:insert_end + 2]
                        buffer = buffer[insert_end + 2:]
                        
                        # Process this INSERT statement
                        processed = process_single_insert(insert_statement)
                        if processed:
                            with open(output_path, 'a', encoding='utf-8') as out_f:
                                if not first_insert:
                                    out_f.write(",\n")
                                out_f.write(processed)
                                first_insert = False
                            insert_count += 1
                            
                            if insert_count % 100 == 0:
                                print(f"Processed {insert_count} INSERT statements...")
            
            # Write footer
            with open(output_path, 'a', encoding='utf-8') as out_f:
                out_f.write(""";
--
-- Data insertion complete
--

SELECT 'DSM raster data inserted successfully' as status;
""")
            
            print(f"Successfully processed {file_path} with {encoding} encoding")
            print(f"Total INSERT statements processed: {insert_count}")
            return True
            
        except UnicodeDecodeError:
            continue
        except FileNotFoundError:
            print(f"Warning: File {file_path} not found")
            return False
        except Exception as e:
            print(f"Error processing {file_path} with {encoding}: {e}")
            continue
    
    print(f"Could not process {file_path} with any of the attempted encodings: {encodings}")
    return False

def process_single_insert(insert_statement):
    """Process a single INSERT statement and return the new format."""
    # Extract values from INSERT INTO public.dsm_raster VALUES (values);
    pattern = r"INSERT INTO public\.dsm_raster VALUES \((.*?)\);"
    match = re.search(pattern, insert_statement, re.DOTALL)
    
    if not match:
        return None
    
    values_str = match.group(1)
    
    # Parse values (handle quoted strings properly)
    values = []
    current_value = ""
    in_quotes = False
    quote_char = None
    
    for char in values_str:
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
        
        return f"({rid}, {rast}, '{filename}')"
    
    return None

def write_file_content(file_path, content):
    """Write content to file safely."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Created: {file_path}")
    except Exception as e:
        print(f"Error writing {file_path}: {e}")

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
    """Main function to convert dsm_data.sql."""
    print("Starting DSM Data Conversion...")
    
    # Create initdb directory if it doesn't exist
    initdb_dir = Path("initdb")
    initdb_dir.mkdir(exist_ok=True)
    
    # Define source and target paths
    source_path = initdb_dir / "dsm_data.sql"
    target_path = initdb_dir / "17-dsm_data.sql"
    
    # Check if source file exists
    if not source_path.exists():
        print(f"Error: Source file {source_path} not found")
        return
    
    # Get file size for progress indication
    file_size = source_path.stat().st_size
    print(f"Processing file: {source_path}")
    print(f"File size: {file_size / (1024*1024):.1f} MB")
    
    # Use chunked processing for large files
    if file_size > 50 * 1024 * 1024:  # If file is larger than 50MB
        print("Large file detected, using chunked processing...")
        success = process_large_file_chunked(source_path, target_path)
        if success:
            print("DSM data conversion completed!")
        else:
            print("Failed to convert dsm_data.sql")
    else:
        # Use original method for smaller files
        print("Small file detected, using standard processing...")
        content = read_file_content(source_path)
        
        if content:
            # Convert content
            new_content = convert_dsm_data(content)
            
            if new_content:
                # Write target file
                write_file_content(target_path, new_content)
                print("DSM data conversion completed!")
            else:
                print("Failed to convert dsm_data.sql")
        else:
            print("Could not read dsm_data.sql")

if __name__ == "__main__":
    main()
