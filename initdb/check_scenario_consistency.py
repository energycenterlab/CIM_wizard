#!/usr/bin/env python3
"""
CIM Wizard Scenario ID Consistency Checker

This script checks if scenario_id values used in building properties and network tables
exist in the scenario table. It validates data integrity across the database.

Author: CIM Wizard Team
Date: 2025-01-27
"""

import re
import sys
from pathlib import Path
from typing import Set, Dict, List, Tuple
import uuid


class ScenarioConsistencyChecker:
    """Check scenario_id consistency across CIM Wizard database tables."""
    
    def __init__(self, initdb_path: str = "initdb"):
        """Initialize the checker with the initdb directory path."""
        self.initdb_path = Path(initdb_path)
        self.scenario_ids_in_scenario_table: Set[str] = set()
        self.scenario_ids_in_props_table: Set[str] = set()
        self.scenario_ids_in_network_tables: Set[str] = set()
        self.invalid_scenario_ids: List[Tuple[str, str, str]] = []  # (scenario_id, table, file)
        
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
    
    def read_scenario_data(self) -> bool:
        """Read scenario IDs from the scenario table data file."""
        scenario_file = self.initdb_path / "13-vec_scen_data.sql"
        
        if not scenario_file.exists():
            print(f"❌ Scenario data file not found: {scenario_file}")
            return False
        
        print(f"📖 Reading scenario data from: {scenario_file}")
        
        try:
            with open(scenario_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract UUIDs from the INSERT statement
            uuids = self.extract_uuid_from_string(content)
            
            # Filter valid UUIDs (should be scenario_id values)
            for uuid_str in uuids:
                if self.validate_uuid_format(uuid_str):
                    self.scenario_ids_in_scenario_table.add(uuid_str)
            
            print(f"✅ Found {len(self.scenario_ids_in_scenario_table)} valid scenario IDs in scenario table")
            
            # Print the scenario IDs for reference
            for i, scenario_id in enumerate(sorted(self.scenario_ids_in_scenario_table), 1):
                print(f"   {i}. {scenario_id}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error reading scenario data: {e}")
            return False
    
    def read_building_props_data(self) -> bool:
        """Read scenario IDs from the building properties table data file."""
        props_file = self.initdb_path / "14-vec_props_data.sql"
        
        if not props_file.exists():
            print(f"❌ Building properties data file not found: {props_file}")
            return False
        
        print(f"📖 Reading building properties data from: {props_file}")
        
        try:
            with open(props_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract UUIDs from the INSERT statement
            uuids = self.extract_uuid_from_string(content)
            
            # Filter valid UUIDs (should be scenario_id values)
            for uuid_str in uuids:
                if self.validate_uuid_format(uuid_str):
                    self.scenario_ids_in_props_table.add(uuid_str)
            
            print(f"✅ Found {len(self.scenario_ids_in_props_table)} unique scenario IDs in building properties table")
            
            return True
            
        except Exception as e:
            print(f"❌ Error reading building properties data: {e}")
            return False
    
    def read_network_data(self) -> bool:
        """Read scenario IDs from network data files."""
        network_files = [
            "18-network_with_PV_data.sql",
            "18-network_without_PV_data.sql"
        ]
        
        print(f"📖 Reading network data files...")
        
        for network_file in network_files:
            file_path = self.initdb_path / network_file
            
            if not file_path.exists():
                print(f"⚠️  Network data file not found: {file_path}")
                continue
            
            print(f"   Reading: {network_file}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Extract UUIDs from the INSERT statement
                uuids = self.extract_uuid_from_string(content)
                
                # Filter valid UUIDs (should be scenario_id values)
                for uuid_str in uuids:
                    if self.validate_uuid_format(uuid_str):
                        self.scenario_ids_in_network_tables.add(uuid_str)
                
                print(f"   ✅ Found {len(uuids)} UUIDs in {network_file}")
                
            except Exception as e:
                print(f"   ❌ Error reading {network_file}: {e}")
                return False
        
        print(f"✅ Found {len(self.scenario_ids_in_network_tables)} unique scenario IDs in network tables")
        return True
    
    def check_consistency(self) -> bool:
        """Check if all scenario IDs in props and network tables exist in scenario table."""
        print(f"\n🔍 Checking scenario ID consistency...")
        
        all_consistent = True
        
        # Check building properties table
        print(f"\n📋 Checking building properties table:")
        props_missing = self.scenario_ids_in_props_table - self.scenario_ids_in_scenario_table
        
        if props_missing:
            print(f"❌ Found {len(props_missing)} scenario IDs in building properties that don't exist in scenario table:")
            for scenario_id in sorted(props_missing):
                print(f"   - {scenario_id}")
                self.invalid_scenario_ids.append((scenario_id, "building_properties", "14-vec_props_data.sql"))
            all_consistent = False
        else:
            print(f"✅ All scenario IDs in building properties table exist in scenario table")
        
        # Check network tables
        print(f"\n🌐 Checking network tables:")
        network_missing = self.scenario_ids_in_network_tables - self.scenario_ids_in_scenario_table
        
        if network_missing:
            print(f"❌ Found {len(network_missing)} scenario IDs in network tables that don't exist in scenario table:")
            for scenario_id in sorted(network_missing):
                print(f"   - {scenario_id}")
                self.invalid_scenario_ids.append((scenario_id, "network_tables", "18-network_*_data.sql"))
            all_consistent = False
        else:
            print(f"✅ All scenario IDs in network tables exist in scenario table")
        
        # Check for orphaned scenario IDs (in scenario table but not used elsewhere)
        print(f"\n🔍 Checking for orphaned scenario IDs:")
        props_used = self.scenario_ids_in_props_table
        network_used = self.scenario_ids_in_network_tables
        all_used = props_used | network_used
        
        orphaned = self.scenario_ids_in_scenario_table - all_used
        
        if orphaned:
            print(f"⚠️  Found {len(orphaned)} scenario IDs in scenario table that are not used in other tables:")
            for scenario_id in sorted(orphaned):
                print(f"   - {scenario_id}")
        else:
            print(f"✅ All scenario IDs in scenario table are being used")
        
        return all_consistent
    
    def generate_report(self) -> None:
        """Generate a detailed consistency report."""
        print(f"\n📊 CONSISTENCY REPORT")
        print(f"=" * 50)
        
        print(f"Scenario IDs in scenario table: {len(self.scenario_ids_in_scenario_table)}")
        print(f"Scenario IDs in building properties: {len(self.scenario_ids_in_props_table)}")
        print(f"Scenario IDs in network tables: {len(self.scenario_ids_in_network_tables)}")
        print(f"Invalid scenario IDs found: {len(self.invalid_scenario_ids)}")
        
        if self.invalid_scenario_ids:
            print(f"\n❌ INVALID SCENARIO IDs:")
            for scenario_id, table, file in self.invalid_scenario_ids:
                print(f"   {scenario_id} (used in {table}, file: {file})")
        else:
            print(f"\n✅ All scenario IDs are consistent across tables!")
    
    def run_check(self) -> bool:
        """Run the complete consistency check."""
        print(f"🚀 Starting CIM Wizard Scenario ID Consistency Check")
        print(f"=" * 60)
        
        # Read data from all tables
        if not self.read_scenario_data():
            return False
        
        if not self.read_building_props_data():
            return False
        
        if not self.read_network_data():
            return False
        
        # Check consistency
        is_consistent = self.check_consistency()
        
        # Generate report
        self.generate_report()
        
        return is_consistent


def main():
    """Main function to run the scenario consistency check."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check scenario ID consistency in CIM Wizard database")
    parser.add_argument("--initdb", default="initdb", help="Path to initdb directory (default: initdb)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")
    
    args = parser.parse_args()
    
    # Check if initdb directory exists
    initdb_path = Path(args.initdb)
    if not initdb_path.exists():
        print(f"❌ Error: initdb directory not found: {initdb_path}")
        print(f"Please run this script from the project root directory or specify the correct path with --initdb")
        sys.exit(1)
    
    # Run the consistency check
    checker = ScenarioConsistencyChecker(args.initdb)
    is_consistent = checker.run_check()
    
    # Exit with appropriate code
    if is_consistent:
        print(f"\n🎉 All scenario IDs are consistent!")
        sys.exit(0)
    else:
        print(f"\n💥 Found inconsistent scenario IDs!")
        sys.exit(1)


if __name__ == "__main__":
    main()
