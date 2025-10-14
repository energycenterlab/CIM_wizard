#!/usr/bin/env python3
"""
CIM Wizard Data Converter Runner
Runs all individual data converters in sequence.
"""

import subprocess
import sys
from pathlib import Path

def run_converter(script_name):
    """Run a single converter script."""
    print(f"\n{'='*60}")
    print(f"Running {script_name}...")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, 
                              text=True, 
                              cwd=Path.cwd())
        
        if result.returncode == 0:
            print(f"✅ {script_name} completed successfully")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ {script_name} failed with return code {result.returncode}")
            if result.stderr:
                print(f"Error: {result.stderr}")
            if result.stdout:
                print(f"Output: {result.stdout}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def main():
    """Main function to run all converters."""
    print("Starting CIM Wizard Data Conversion Process...")
    print("This will run all individual data converters in sequence.")
    
    # List of converter scripts in order
    converters = [
        "convert_vec_bld_data.py",
        "convert_vec_scen_data.py", 
        "convert_vec_props_data.py",
        "convert_census_data.py",
        "convert_dtm_data.py",
        "convert_dsm_data.py"
    ]
    
    success_count = 0
    total_count = len(converters)
    
    for converter in converters:
        if Path(converter).exists():
            if run_converter(converter):
                success_count += 1
        else:
            print(f"❌ Converter script not found: {converter}")
    
    # Summary
    print(f"\n{'='*60}")
    print("CONVERSION SUMMARY")
    print(f"{'='*60}")
    print(f"Total converters: {total_count}")
    print(f"Successful: {success_count}")
    print(f"Failed: {total_count - success_count}")
    
    if success_count == total_count:
        print("\n🎉 All data conversions completed successfully!")
        print("\nGenerated files:")
        print("  - 12-vec_bld_data.sql")
        print("  - 13-vec_scen_data.sql") 
        print("  - 14-vec_props_data.sql")
        print("  - 15-census_data.sql")
        print("  - 16-dtm_data.sql")
        print("  - 17-dsm_data.sql")
    else:
        print(f"\n⚠️  {total_count - success_count} converter(s) failed. Check the output above for details.")
    
    return success_count == total_count

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
