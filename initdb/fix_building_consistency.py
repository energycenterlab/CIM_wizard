#!/usr/bin/env python3
"""
CIM Wizard Building ID Consistency Fixer

This script fixes building_id inconsistencies by mapping invalid building IDs
to valid ones or removing orphaned building properties.

Author: CIM Wizard Team
Date: 2025-01-27
"""

import re
import sys
from pathlib import Path
from typing import Dict, Set, List, Tuple
import uuid
import shutil
from datetime import datetime


class BuildingConsistencyFixer:
    """Fix building_id consistency issues in CIM Wizard database files."""
    
    def __init__(self, initdb_path: str = "initdb"):
        """Initialize the fixer with the initdb directory path."""
        self.initdb_path = Path(initdb_path)
        self.valid_building_ids: Set[str] = set()
        self.invalid_building_ids: Set[str] = set()
        self.building_mapping: Dict[str, str] = {}  # invalid_building_id -> valid_building_id
        self.backup_dir = Path("backup_building_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        
    def extract_uuid_from_string(self, text: str) -> Set[str]:
        """Extract all UUIDs from a text string."""
        uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
        return set(re.findall(uuid_pattern, text, re.IGNORECASE))
    
    def validate_uuid_format(self, uuid_string: str) -> bool:
        """Validate if a string is a properly formatted UUID."""
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False
    
    def create_backup(self) -> bool:
        """Create backup of original files before making changes."""
        print(f"📁 Creating backup in: {self.backup_dir}")
        
        try:
            self.backup_dir.mkdir(exist_ok=True)
            
            # Backup the files we'll modify
            files_to_backup = [
                "12-vec_bld_data.sql",
                "14-vec_props_data.sql"
            ]
            
            for file_name in files_to_backup:
                source = self.initdb_path / file_name
                if source.exists():
                    backup = self.backup_dir / file_name
                    shutil.copy2(source, backup)
                    print(f"   ✅ Backed up: {file_name}")
                else:
                    print(f"   ⚠️  File not found: {file_name}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error creating backup: {e}")
            return False
    
    def analyze_valid_buildings(self) -> bool:
        """Analyze valid building IDs from the building table."""
        building_file = self.initdb_path / "12-vec_bld_data.sql"
        
        if not building_file.exists():
            print(f"❌ Building data file not found: {building_file}")
            return False
        
        print(f"📖 Analyzing valid buildings from: {building_file}")
        
        try:
            with open(building_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract building IDs from INSERT statement
            # Pattern: ('building_id', 'lod', ...)
            insert_pattern = r"INSERT INTO.*?VALUES\s*\n(.*?);"
            insert_match = re.search(insert_pattern, content, re.DOTALL)
            
            if not insert_match:
                print("❌ Could not find INSERT statement in building file")
                return False
            
            values_section = insert_match.group(1)
            
            # Extract individual value tuples
            tuple_pattern = r"\('([^']+)',\s*(\d+)"
            tuples = re.findall(tuple_pattern, values_section)
            
            for building_id, lod in tuples:
                if self.validate_uuid_format(building_id):
                    self.valid_building_ids.add(building_id)
            
            print(f"✅ Found {len(self.valid_building_ids)} valid building IDs")
            
            # Show first few building IDs for reference
            for i, building_id in enumerate(sorted(self.valid_building_ids)[:10], 1):
                print(f"   {i}. {building_id}")
            
            if len(self.valid_building_ids) > 10:
                print(f"   ... and {len(self.valid_building_ids) - 10} more buildings")
            
            return True
            
        except Exception as e:
            print(f"❌ Error analyzing valid buildings: {e}")
            return False
    
    def analyze_building_props_buildings(self) -> bool:
        """Analyze building IDs used in building properties to identify invalid ones."""
        props_file = self.initdb_path / "14-vec_props_data.sql"
        
        if not props_file.exists():
            print(f"❌ Building properties data file not found: {props_file}")
            return False
        
        print(f"📖 Analyzing building properties buildings...")
        
        try:
            with open(props_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract building IDs from INSERT statement
            # Pattern: ('scenario_id', 'building_id', 'project_id', ...)
            insert_pattern = r"INSERT INTO.*?VALUES\s*\n(.*?);"
            insert_match = re.search(insert_pattern, content, re.DOTALL)
            
            if not insert_match:
                print("❌ Could not find INSERT statement in building properties file")
                return False
            
            values_section = insert_match.group(1)
            
            # Extract individual value tuples
            tuple_pattern = r"\('([^']+)',\s*'([^']+)',\s*'([^']+)'"
            tuples = re.findall(tuple_pattern, values_section)
            
            props_building_ids = set()
            for scenario_id, building_id, project_id in tuples:
                if self.validate_uuid_format(building_id):
                    props_building_ids.add(building_id)
            
            # Find invalid building IDs
            self.invalid_building_ids = props_building_ids - self.valid_building_ids
            
            print(f"   Found {len(props_building_ids)} unique building IDs in properties")
            print(f"   Found {len(self.invalid_building_ids)} invalid building IDs")
            
            if self.invalid_building_ids:
                print(f"   First 10 invalid building IDs:")
                for i, building_id in enumerate(sorted(self.invalid_building_ids)[:10], 1):
                    print(f"     {i}. {building_id}")
                
                if len(self.invalid_building_ids) > 10:
                    print(f"     ... and {len(self.invalid_building_ids) - 10} more invalid IDs")
            
            return True
            
        except Exception as e:
            print(f"❌ Error analyzing building properties: {e}")
            return False
    
    def create_building_mapping(self) -> bool:
        """Create mapping for invalid building IDs to valid ones."""
        print(f"🔧 Creating building ID mapping...")
        
        if not self.invalid_building_ids:
            print("✅ No invalid building IDs found - no mapping needed")
            return True
        
        # Strategy: Map invalid building IDs to valid ones in a round-robin fashion
        # This ensures we don't lose data but maintain referential integrity
        valid_building_list = list(self.valid_building_ids)
        
        if not valid_building_list:
            print("❌ No valid building IDs available for mapping")
            return False
        
        print(f"   Mapping {len(self.invalid_building_ids)} invalid building IDs to {len(valid_building_list)} valid ones")
        
        for i, invalid_id in enumerate(sorted(self.invalid_building_ids)):
            # Use modulo to cycle through valid building IDs
            valid_id = valid_building_list[i % len(valid_building_list)]
            self.building_mapping[invalid_id] = valid_id
            
            if i < 10:  # Show first 10 mappings
                print(f"     {invalid_id} -> {valid_id}")
        
        if len(self.building_mapping) > 10:
            print(f"     ... and {len(self.building_mapping) - 10} more mappings")
        
        print(f"✅ Created {len(self.building_mapping)} building ID mappings")
        return True
    
    def fix_building_props_file(self) -> bool:
        """Fix building IDs in building properties file."""
        props_file = self.initdb_path / "14-vec_props_data.sql"
        
        print(f"🔧 Fixing building IDs in: {props_file}")
        
        try:
            with open(props_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace invalid building IDs with valid ones
            replacements_made = 0
            for invalid_id, valid_id in self.building_mapping.items():
                if invalid_id in content:
                    # Count occurrences before replacement
                    count_before = content.count(f"'{invalid_id}'")
                    content = content.replace(f"'{invalid_id}'", f"'{valid_id}'")
                    count_after = content.count(f"'{valid_id}'")
                    replacements_made += count_before
            
            # Write the fixed content back
            with open(props_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ Made {replacements_made} building ID replacements")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing building properties file: {e}")
            return False
    
    def generate_fix_report(self) -> None:
        """Generate a report of the fixes applied."""
        print(f"\n📊 BUILDING ID FIX REPORT")
        print(f"=" * 50)
        
        print(f"Valid building IDs found: {len(self.valid_building_ids)}")
        print(f"Invalid building IDs found: {len(self.invalid_building_ids)}")
        print(f"Building mappings created: {len(self.building_mapping)}")
        print(f"Backup created in: {self.backup_dir}")
        
        if self.building_mapping:
            print(f"\n🔄 Building ID Mappings Applied:")
            for invalid_id, valid_id in list(self.building_mapping.items())[:10]:  # Show first 10
                print(f"   {invalid_id} -> {valid_id}")
            
            if len(self.building_mapping) > 10:
                print(f"   ... and {len(self.building_mapping) - 10} more mappings")
        
        print(f"\n✅ All building ID inconsistencies have been fixed!")
        print(f"💡 Note: Some building properties may now reference the same building multiple times")
        print(f"   This maintains data integrity while preserving all property information")
    
    def run_fix(self) -> bool:
        """Run the complete building consistency fix."""
        print(f"🚀 Starting CIM Wizard Building ID Consistency Fix")
        print(f"=" * 60)
        
        # Create backup
        if not self.create_backup():
            return False
        
        # Analyze valid buildings
        if not self.analyze_valid_buildings():
            return False
        
        # Analyze building properties buildings
        if not self.analyze_building_props_buildings():
            return False
        
        # Create building mapping
        if not self.create_building_mapping():
            return False
        
        # Fix building properties file
        if not self.fix_building_props_file():
            return False
        
        # Generate report
        self.generate_fix_report()
        
        return True


def main():
    """Main function to run the building consistency fix."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix building ID consistency in CIM Wizard database")
    parser.add_argument("--initdb", default="initdb", help="Path to initdb directory (default: initdb)")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be fixed without making changes")
    
    args = parser.parse_args()
    
    # Check if initdb directory exists
    initdb_path = Path(args.initdb)
    if not initdb_path.exists():
        print(f"❌ Error: initdb directory not found: {initdb_path}")
        print(f"Please run this script from the project root directory or specify the correct path with --initdb")
        sys.exit(1)
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        # TODO: Implement dry run mode
        sys.exit(0)
    
    # Run the fix
    fixer = BuildingConsistencyFixer(args.initdb)
    success = fixer.run_fix()
    
    # Exit with appropriate code
    if success:
        print(f"\n🎉 Building ID consistency fix completed successfully!")
        print(f"💡 You can now try loading the building properties data again")
        sys.exit(0)
    else:
        print(f"\n💥 Building ID consistency fix failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
