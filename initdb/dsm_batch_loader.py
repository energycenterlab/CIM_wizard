#!/usr/bin/env python3
"""
DSM Data Batch Loader
Splits large DSM SQL file into manageable batches for PostgreSQL loading
"""

import os
import re
from pathlib import Path

def split_dsm_file(input_file, output_dir, batch_size_mb=50):
    """Split large DSM SQL file into smaller batches, preserving complete INSERT statements."""
    
    batch_size_bytes = batch_size_mb * 1024 * 1024
    batch_count = 0
    current_batch_size = 0
    current_batch = []
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    print("Processing DSM file in chunks to avoid memory issues...")
    
    # First, find the header and INSERT start position
    header_lines = []
    insert_start_pos = 0
    values_start_pos = 0
    
    print("Finding INSERT statement start...")
    with open(input_file, 'r', encoding='utf-8') as f:
        line_num = 0
        while True:
            line = f.readline()
            if not line:
                break
            
            header_lines.append(line)
            line_num += 1
            
            if 'INSERT INTO cim_raster.dsm_raster (rid, rast, filename) VALUES' in line:
                insert_start_pos = f.tell() - len(line)
                values_start_pos = f.tell()
                print(f"Found INSERT statement at line {line_num}")
                break
    
    if insert_start_pos == 0:
        print("Error: Could not find INSERT statement start")
        return 0
    
    print(f"Found INSERT statement at position {insert_start_pos}")
    
    # Start new batch with header
    current_batch = header_lines.copy()
    current_batch.append("INSERT INTO cim_raster.dsm_raster (rid, rast, filename) VALUES\n")
    current_batch_size = sum(len(l.encode('utf-8')) for l in current_batch)
    
    # Process the VALUES section in chunks
    print("Processing INSERT values...")
    chunk_size = 1024 * 1024  # 1MB chunks
    buffer = ""
    value_count = 0
    first_value = True
    
    with open(input_file, 'r', encoding='utf-8') as f:
        f.seek(values_start_pos)
        
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            
            buffer += chunk
            
            # Process complete value tuples in buffer
            while True:
                # Find the next complete value tuple
                # Pattern: (number, 'hex_string', 'filename')
                import re
                pattern = r"\(\d+,\s*'[^']+',\s*'[^']+'\)"
                match = re.search(pattern, buffer)
                
                if not match:
                    # No complete tuple found, keep reading
                    break
                
                # Extract the complete tuple
                value_tuple = match.group(0)
                buffer = buffer[match.end():]
                
                # Add comma and newline for all but the first value
                if not first_value:
                    value_line = ",\n" + value_tuple
                else:
                    value_line = value_tuple
                    first_value = False
                
                line_size = len(value_line.encode('utf-8'))
                
                # Check if adding this value would exceed batch size
                if current_batch_size + line_size > batch_size_bytes and current_batch:
                    # Close current batch
                    current_batch.append(";\n")
                    write_batch(current_batch, output_path, batch_count)
                    batch_count += 1
                    
                    # Start new batch
                    current_batch = ["INSERT INTO cim_raster.dsm_raster (rid, rast, filename) VALUES\n"]
                    current_batch.append(value_tuple)
                    current_batch_size = len("INSERT INTO cim_raster.dsm_raster (rid, rast, filename) VALUES\n") + len(value_tuple)
                else:
                    current_batch.append(value_line)
                    current_batch_size += line_size
                
                value_count += 1
                
                if value_count % 1000 == 0:
                    print(f"Processed {value_count} value tuples...")
    
    # Write final batch
    if current_batch:
        current_batch.append(";\n")
        write_batch(current_batch, output_path, batch_count)
        batch_count += 1
    
    print(f"Split {input_file} into {batch_count} batches")
    print(f"Total value tuples processed: {value_count}")
    return batch_count

def write_batch(batch_lines, output_dir, batch_num):
    """Write a batch of lines to a file."""
    
    # Add footer to the batch
    footer = [
        ";\n",
        "--\n",
        "-- Batch loading complete\n",
        "--\n",
        "SELECT 'DSM raster batch loaded successfully' as status;\n"
    ]
    
    batch_lines.extend(footer)
    
    # Write to file
    output_file = output_dir / f"dsm_batch_{batch_num:03d}.sql"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(batch_lines)
    
    print(f"Created: {output_file}")

def load_batches_to_database(batch_dir, container_name="integrateddb"):
    """Load all batches to the database using streaming approach to avoid Docker copy issues."""
    
    batch_files = sorted(Path(batch_dir).glob("dsm_batch_*.sql"))
    
    print(f"Found {len(batch_files)} batch files to load")
    
    successful_batches = 0
    failed_batches = 0
    
    for i, batch_file in enumerate(batch_files):
        print(f"Loading batch {i+1}/{len(batch_files)}: {batch_file.name}")
        
        try:
            # Method 1: Try direct streaming (bypasses Docker copy issues)
            print(f"  Attempting direct streaming...")
            cmd = f"docker exec -i {container_name} psql -U cim_wizard_user -d cim_wizard_integrated"
            result = os.system(f"type {batch_file} | {cmd}")
            
            if result == 0:
                print(f"✓ Batch {i+1} loaded successfully (streaming)")
                successful_batches += 1
                continue
            
            # Method 2: Try copying with absolute path
            print(f"  Attempting copy with absolute path...")
            abs_path = batch_file.resolve()
            copy_result = os.system(f"docker cp \"{abs_path}\" {container_name}:/tmp/")
            
            if copy_result == 0:
                # Execute in container
                exec_cmd = f"docker exec -i {container_name} psql -U cim_wizard_user -d cim_wizard_integrated -f /tmp/{batch_file.name}"
                result = os.system(exec_cmd)
                
                if result == 0:
                    print(f"✓ Batch {i+1} loaded successfully (copy)")
                    successful_batches += 1
                else:
                    print(f"✗ Batch {i+1} failed to execute (exit code: {result})")
                    failed_batches += 1
            else:
                print(f"✗ Failed to copy batch {i+1} (copy result: {copy_result})")
                failed_batches += 1
                
                # Method 3: Try with PowerShell
                print(f"  Attempting PowerShell copy...")
                ps_cmd = f"powershell -Command \"docker cp '{abs_path}' {container_name}:/tmp/\""
                ps_result = os.system(ps_cmd)
                
                if ps_result == 0:
                    exec_cmd = f"docker exec -i {container_name} psql -U cim_wizard_user -d cim_wizard_integrated -f /tmp/{batch_file.name}"
                    result = os.system(exec_cmd)
                    
                    if result == 0:
                        print(f"✓ Batch {i+1} loaded successfully (PowerShell)")
                        successful_batches += 1
                    else:
                        print(f"✗ Batch {i+1} failed to execute (exit code: {result})")
                        failed_batches += 1
                else:
                    print(f"✗ All copy methods failed for batch {i+1}")
                    failed_batches += 1
                
                # Check if we should continue or stop
                if failed_batches > 5:  # Stop after 5 consecutive failures
                    print(f"Too many failures ({failed_batches}), stopping batch loading")
                    break
                    
        except Exception as e:
            print(f"✗ Error loading batch {i+1}: {e}")
            failed_batches += 1
    
    print(f"\nBatch loading completed:")
    print(f"  Successful: {successful_batches}")
    print(f"  Failed: {failed_batches}")
    print(f"  Total: {len(batch_files)}")
    
    return successful_batches, failed_batches

def clean_existing_batches(batch_dir):
    """Clean up existing batch files."""
    batch_path = Path(batch_dir)
    if batch_path.exists():
        print(f"Cleaning existing batch files in {batch_dir}...")
        for batch_file in batch_path.glob("dsm_batch_*.sql"):
            batch_file.unlink()
            print(f"Removed: {batch_file}")
        print("Cleanup completed")

if __name__ == "__main__":
    # Clean existing batches first
    clean_existing_batches("initdb/dsm_batches")
    
    # Split the large file with improved logic
    batch_count = split_dsm_file("initdb/17-dsm_data.sql", "initdb/dsm_batches", batch_size_mb=50)
    
    if batch_count > 0:
        # Load batches to database
        successful, failed = load_batches_to_database("initdb/dsm_batches")
        
        if failed == 0:
            print("🎉 All DSM batches loaded successfully!")
        else:
            print(f"⚠️  {failed} batches failed to load")
    else:
        print("❌ Failed to split DSM file into batches")