#!/usr/bin/env python3
"""
CIM Wizard Scenario ID Consistency Fixer

This script fixes scenario_id inconsistencies by mapping invalid scenario IDs
to valid ones based on project_id relationships.

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


class ScenarioConsistencyFixer:
    """Fix scenario_id consistency issues in CIM Wizard database files."""
    
    def __init__(self, initdb_path: str = "initdb"):
        """Initialize the fixer with the initdb directory path."""
        self.initdb_path = Path(initdb_path)
        self.valid_scenarios: Dict[str, str] = {}  # project_id -> scenario_id
        self.scenario_mapping: Dict[str, str] = {}  # invalid_scenario_id -> valid_scenario_id
        self.backup_dir = Path("backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
        
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
                "13-vec_scen_data.sql",
                "14-vec_props_data.sql", 
                "18-network_with_PV_data.sql",
                "18-network_without_PV_data.sql"
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
    
    def analyze_valid_scenarios(self) -> bool:
        """Analyze valid scenarios from the scenario table."""
        scenario_file = self.initdb_path / "13-vec_scen_data.sql"
        
        if not scenario_file.exists():
            print(f"❌ Scenario data file not found: {scenario_file}")
            return False
        
        print(f"📖 Analyzing valid scenarios from: {scenario_file}")
        
        try:
            with open(scenario_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract scenario_id and project_id pairs from INSERT statement
            # Pattern: ('scenario_id', 'project_id', 'scenario_name', ...)
            insert_pattern = r"INSERT INTO.*?VALUES\s*\n(.*?);"
            insert_match = re.search(insert_pattern, content, re.DOTALL)
            
            if not insert_match:
                print("❌ Could not find INSERT statement in scenario file")
                return False
            
            values_section = insert_match.group(1)
            
            # Extract individual value tuples
            tuple_pattern = r"\('([^']+)',\s*'([^']+)',\s*'([^']+)',\s*'([^']+)'"
            tuples = re.findall(tuple_pattern, values_section)
            
            for scenario_id, project_id, scenario_name, project_name in tuples:
                if self.validate_uuid_format(scenario_id) and self.validate_uuid_format(project_id):
                    self.valid_scenarios[project_id] = scenario_id
                    print(f"   ✅ Project: {project_id} -> Scenario: {scenario_id} ({scenario_name})")
            
            print(f"✅ Found {len(self.valid_scenarios)} valid scenario mappings")
            return True
            
        except Exception as e:
            print(f"❌ Error analyzing valid scenarios: {e}")
            return False
    
    def analyze_building_props_scenarios(self) -> bool:
        """Analyze scenario IDs used in building properties to create mapping."""
        props_file = self.initdb_path / "14-vec_props_data.sql"
        
        if not props_file.exists():
            print(f"❌ Building properties data file not found: {props_file}")
            return False
        
        print(f"📖 Analyzing building properties scenarios...")
        
        try:
            with open(props_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract scenario_id and project_id pairs from INSERT statement
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
            
            invalid_scenarios = set()
            project_scenario_mapping = {}  # project_id -> set of scenario_ids used
            
            for scenario_id, building_id, project_id in tuples:
                if self.validate_uuid_format(scenario_id) and self.validate_uuid_format(project_id):
                    if scenario_id not in self.valid_scenarios.values():
                        invalid_scenarios.add(scenario_id)
                        
                        if project_id not in project_scenario_mapping:
                            project_scenario_mapping[project_id] = set()
                        project_scenario_mapping[project_id].add(scenario_id)
            
            print(f"   Found {len(invalid_scenarios)} invalid scenario IDs")
            print(f"   Found {len(project_scenario_mapping)} projects with invalid scenarios")
            
            # Create mapping: invalid_scenario_id -> valid_scenario_id
            for project_id, invalid_scenarios_set in project_scenario_mapping.items():
                if project_id in self.valid_scenarios:
                    valid_scenario_id = self.valid_scenarios[project_id]
                    for invalid_scenario_id in invalid_scenarios_set:
                        self.scenario_mapping[invalid_scenario_id] = valid_scenario_id
                        print(f"   🔄 Mapping: {invalid_scenario_id} -> {valid_scenario_id} (project: {project_id})")
                else:
                    print(f"   ⚠️  Project {project_id} not found in valid scenarios")
            
            print(f"✅ Created {len(self.scenario_mapping)} scenario mappings")
            return True
            
        except Exception as e:
            print(f"❌ Error analyzing building properties: {e}")
            return False
    
    def fix_building_props_file(self) -> bool:
        """Fix scenario IDs in building properties file."""
        props_file = self.initdb_path / "14-vec_props_data.sql"
        
        print(f"🔧 Fixing scenario IDs in: {props_file}")
        
        try:
            with open(props_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace invalid scenario IDs with valid ones
            replacements_made = 0
            for invalid_id, valid_id in self.scenario_mapping.items():
                if invalid_id in content:
                    content = content.replace(f"'{invalid_id}'", f"'{valid_id}'")
                    replacements_made += content.count(f"'{valid_id}'") - content.count(f"'{invalid_id}'")
            
            # Write the fixed content back
            with open(props_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"   ✅ Made {replacements_made} scenario ID replacements")
            return True
            
        except Exception as e:
            print(f"❌ Error fixing building properties file: {e}")
            return False
    
    def fix_network_files(self) -> bool:
        """Fix scenario IDs in network files."""
        network_files = [
            "18-network_with_PV_data.sql",
            "18-network_without_PV_data.sql"
        ]
        
        print(f"🔧 Fixing scenario IDs in network files...")
        
        for network_file in network_files:
            file_path = self.initdb_path / network_file
            
            if not file_path.exists():
                print(f"   ⚠️  Network file not found: {network_file}")
                continue
            
            print(f"   Fixing: {network_file}")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace invalid scenario IDs with valid ones
                replacements_made = 0
                for invalid_id, valid_id in self.scenario_mapping.items():
                    if invalid_id in content:
                        content = content.replace(f"'{invalid_id}'", f"'{valid_id}'")
                        replacements_made += 1
                
                # Write the fixed content back
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"     ✅ Made {replacements_made} scenario ID replacements")
                
            except Exception as e:
                print(f"     ❌ Error fixing {network_file}: {e}")
                return False
        
        return True
    
    def generate_fix_report(self) -> None:
        """Generate a report of the fixes applied."""
        print(f"\n📊 FIX REPORT")
        print(f"=" * 50)
        
        print(f"Valid scenarios found: {len(self.valid_scenarios)}")
        print(f"Scenario mappings created: {len(self.scenario_mapping)}")
        print(f"Backup created in: {self.backup_dir}")
        
        if self.scenario_mapping:
            print(f"\n🔄 Scenario ID Mappings Applied:")
            for invalid_id, valid_id in list(self.scenario_mapping.items())[:10]:  # Show first 10
                print(f"   {invalid_id} -> {valid_id}")
            
            if len(self.scenario_mapping) > 10:
                print(f"   ... and {len(self.scenario_mapping) - 10} more mappings")
        
        print(f"\n✅ All scenario ID inconsistencies have been fixed!")
    
    def run_fix(self) -> bool:
        """Run the complete scenario consistency fix."""
        print(f"🚀 Starting CIM Wizard Scenario ID Consistency Fix")
        print(f"=" * 60)
        
        # Create backup
        if not self.create_backup():
            return False
        
        # Analyze valid scenarios
        if not self.analyze_valid_scenarios():
            return False
        
        # Analyze building properties scenarios
        if not self.analyze_building_props_scenarios():
            return False
        
        # Fix building properties file
        if not self.fix_building_props_file():
            return False
        
        # Fix network files
        if not self.fix_network_files():
            return False
        
        # Generate report
        self.generate_fix_report()
        
        return True


def main():
    """Main function to run the scenario consistency fix."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Fix scenario ID consistency in CIM Wizard database")
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
    fixer = ScenarioConsistencyFixer(args.initdb)
    success = fixer.run_fix()
    
    # Exit with appropriate code
    if success:
        print(f"\n🎉 Scenario ID consistency fix completed successfully!")
        print(f"💡 Run the consistency checker again to verify the fixes")
        sys.exit(0)
    else:
        print(f"\n💥 Scenario ID consistency fix failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
