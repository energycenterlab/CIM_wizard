#!/usr/bin/env python3
"""
Comprehensive Pandapower Network Inspector and Extractor
Thoroughly inspects pandapower network objects and extracts all available data
"""

import pickle
import pandas as pd
import numpy as np
from pathlib import Path
import uuid
from datetime import datetime
import json

def inspect_network_structure(network, network_name):
    """Comprehensive inspection of pandapower network structure."""
    print(f"\n{'='*60}")
    print(f"INSPECTING NETWORK: {network_name}")
    print(f"{'='*60}")
    
    # Basic network info
    print(f"Network type: {type(network)}")
    print(f"Network attributes: {[attr for attr in dir(network) if not attr.startswith('_')]}")
    
    # Inspect all DataFrames in the network
    dataframes = {}
    for attr_name in dir(network):
        if not attr_name.startswith('_'):
            attr = getattr(network, attr_name)
            if isinstance(attr, pd.DataFrame):
                dataframes[attr_name] = attr
                print(f"\n--- {attr_name.upper()} ---")
                print(f"Shape: {attr.shape}")
                print(f"Columns: {list(attr.columns)}")
                print(f"Index type: {type(attr.index)}")
                print(f"Index values: {list(attr.index)[:10]}...")
                print(f"Data types:\n{attr.dtypes}")
                print(f"Sample data:\n{attr.head()}")
                
                # Check for coordinate columns
                coord_cols = [col for col in attr.columns if col.lower() in ['x', 'y', 'lon', 'lat', 'longitude', 'latitude']]
                if coord_cols:
                    print(f"Coordinate columns found: {coord_cols}")
                    for col in coord_cols:
                        non_null_count = attr[col].notna().sum()
                        print(f"  {col}: {non_null_count} non-null values")
                        if non_null_count > 0:
                            print(f"    Range: {attr[col].min()} to {attr[col].max()}")
    
    return dataframes

def extract_comprehensive_bus_data(network, network_name):
    """Extract all available bus data with comprehensive information."""
    buses = []
    
    if not hasattr(network, 'bus') or network.bus.empty:
        print("No bus data found in network")
        return buses
    
    print(f"\nExtracting bus data from {network_name}...")
    print(f"Bus DataFrame shape: {network.bus.shape}")
    print(f"Bus columns: {list(network.bus.columns)}")
    
    for idx, bus_row in network.bus.iterrows():
        bus_info = {
            'bus_id': str(idx),
            'bus_name': bus_row.get('name', f'Bus_{idx}'),
            'bus_type': bus_row.get('type', 'unknown'),
            'voltage_kv': float(bus_row.get('vn_kv', 0.0)) if pd.notna(bus_row.get('vn_kv')) else 0.0,
            'geometry': None,
            'active_power_mw': float(bus_row.get('p_mw', 0.0)) if pd.notna(bus_row.get('p_mw')) else 0.0,
            'reactive_power_mvar': float(bus_row.get('q_mvar', 0.0)) if pd.notna(bus_row.get('q_mvar')) else 0.0,
            'max_power_mw': float(bus_row.get('max_p_mw', 0.0)) if pd.notna(bus_row.get('max_p_mw')) else 0.0,
            'min_power_mw': float(bus_row.get('min_p_mw', 0.0)) if pd.notna(bus_row.get('min_p_mw')) else 0.0,
            'in_service': bus_row.get('in_service', True),
            'zone': bus_row.get('zone', ''),
            'additional_data': {}
        }
        
        # Check for coordinate columns with various possible names
        coord_found = False
        for x_col in ['x', 'lon', 'longitude']:
            for y_col in ['y', 'lat', 'latitude']:
                if x_col in bus_row and y_col in bus_row:
                    x, y = bus_row[x_col], bus_row[y_col]
                    if pd.notna(x) and pd.notna(y):
                        bus_info['geometry'] = f"ST_GeomFromText('POINT({x} {y})', 4326)"
                        coord_found = True
                        print(f"Found coordinates for bus {idx}: ({x}, {y})")
                        break
            if coord_found:
                break
        
        # Store all other columns as additional data
        for col in network.bus.columns:
            if col not in ['name', 'type', 'vn_kv', 'p_mw', 'q_mvar', 'max_p_mw', 'min_p_mw', 'in_service', 'zone', 'x', 'y', 'lon', 'lat', 'longitude', 'latitude']:
                value = bus_row[col]
                if pd.notna(value):
                    bus_info['additional_data'][col] = str(value)
        
        buses.append(bus_info)
    
    print(f"Extracted {len(buses)} buses")
    return buses

def extract_comprehensive_line_data(network, network_name):
    """Extract all available line data with comprehensive information."""
    lines = []
    
    if not hasattr(network, 'line') or network.line.empty:
        print("No line data found in network")
        return lines
    
    print(f"\nExtracting line data from {network_name}...")
    print(f"Line DataFrame shape: {network.line.shape}")
    print(f"Line columns: {list(network.line.columns)}")
    
    for idx, line_row in network.line.iterrows():
        line_info = {
            'line_id': str(idx),
            'line_name': line_row.get('name', f'Line_{idx}'),
            'from_bus_id': str(line_row.get('from_bus', '')),
            'to_bus_id': str(line_row.get('to_bus', '')),
            'geometry': None,
            'resistance_ohm': float(line_row.get('r_ohm_per_km', 0.0)) if pd.notna(line_row.get('r_ohm_per_km')) else 0.0,
            'reactance_ohm': float(line_row.get('x_ohm_per_km', 0.0)) if pd.notna(line_row.get('x_ohm_per_km')) else 0.0,
            'susceptance_s': float(line_row.get('b_us_per_km', 0.0)) if pd.notna(line_row.get('b_us_per_km')) else 0.0,
            'max_current_ka': float(line_row.get('max_i_ka', 0.0)) if pd.notna(line_row.get('max_i_ka')) else 0.0,
            'max_power_mw': float(line_row.get('max_p_mw', 0.0)) if pd.notna(line_row.get('max_p_mw')) else 0.0,
            'length_km': float(line_row.get('length_km', 0.0)) if pd.notna(line_row.get('length_km')) else 0.0,
            'line_type': line_row.get('type', 'unknown'),
            'voltage_level_kv': float(line_row.get('vn_kv', 0.0)) if pd.notna(line_row.get('vn_kv')) else 0.0,
            'in_service': line_row.get('in_service', True),
            'parallel': line_row.get('parallel', 1),
            'df': line_row.get('df', 1.0),
            'additional_data': {}
        }
        
        # Try to create line geometry from bus coordinates
        from_bus = line_row.get('from_bus')
        to_bus = line_row.get('to_bus')
        
        if pd.notna(from_bus) and pd.notna(to_bus) and hasattr(network, 'bus'):
            # Get bus data by index
            if from_bus in network.bus.index and to_bus in network.bus.index:
                from_bus_data = network.bus.loc[from_bus]
                to_bus_data = network.bus.loc[to_bus]
                
                # Check for coordinate columns
                coord_found = False
                for x_col in ['x', 'lon', 'longitude']:
                    for y_col in ['y', 'lat', 'latitude']:
                        if (x_col in from_bus_data and y_col in from_bus_data and 
                            x_col in to_bus_data and y_col in to_bus_data):
                            x1, y1 = from_bus_data[x_col], from_bus_data[y_col]
                            x2, y2 = to_bus_data[x_col], to_bus_data[y_col]
                            
                            if all(pd.notna(coord) for coord in [x1, y1, x2, y2]):
                                line_info['geometry'] = f"ST_GeomFromText('LINESTRING({x1} {y1}, {x2} {y2})', 4326)"
                                coord_found = True
                                break
                    if coord_found:
                        break
        
        # Store all other columns as additional data
        for col in network.line.columns:
            if col not in ['name', 'from_bus', 'to_bus', 'r_ohm_per_km', 'x_ohm_per_km', 'b_us_per_km', 
                          'max_i_ka', 'max_p_mw', 'length_km', 'type', 'vn_kv', 'in_service', 'parallel', 'df']:
                value = line_row[col]
                if pd.notna(value):
                    line_info['additional_data'][col] = str(value)
        
        lines.append(line_info)
    
    print(f"Extracted {len(lines)} lines")
    return lines

def extract_other_components(network, network_name):
    """Extract other network components (loads, generators, transformers, etc.)."""
    components = {}
    
    # List of common pandapower components
    component_types = ['load', 'gen', 'trafo', 'trafo3w', 'switch', 'shunt', 'ext_grid', 'storage', 'sgen', 'motor', 'asymmetric_load', 'asymmetric_sgen']
    
    for comp_type in component_types:
        if hasattr(network, comp_type) and not getattr(network, comp_type).empty:
            comp_data = getattr(network, comp_type)
            print(f"\nFound {comp_type} data: {comp_data.shape}")
            print(f"Columns: {list(comp_data.columns)}")
            
            components[comp_type] = []
            for idx, row in comp_data.iterrows():
                comp_info = {
                    'id': str(idx),
                    'type': comp_type,
                    'additional_data': {}
                }
                
                # Extract all columns
                for col in comp_data.columns:
                    value = row[col]
                    if pd.notna(value):
                        comp_info['additional_data'][col] = str(value)
                
                components[comp_type].append(comp_info)
            
            print(f"Extracted {len(components[comp_type])} {comp_type} components")
    
    return components

def generate_comprehensive_schema():
    """Generate comprehensive network schema with all component types."""
    return """
--
-- CIM Wizard Comprehensive Network Schema
-- Pandapowered network data storage with all component types
--

-- Create network schema
CREATE SCHEMA IF NOT EXISTS cim_network;

-- Network Scenarios
CREATE TABLE cim_network.network_scenarios (
    scenario_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scenario_name VARCHAR(100) NOT NULL,
    description TEXT,
    network_type VARCHAR(20), -- 'with_PV', 'without_PV'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Network Buses (Nodes) - Enhanced
CREATE TABLE cim_network.network_buses (
    bus_id VARCHAR(50) PRIMARY KEY,
    bus_name VARCHAR(100),
    bus_type VARCHAR(20), -- 'PV', 'PQ', 'SLACK', 'LOAD'
    voltage_kv DECIMAL(10,3),
    geometry GEOMETRY(POINT, 4326),
    active_power_mw DECIMAL(12,6),
    reactive_power_mvar DECIMAL(12,6),
    max_power_mw DECIMAL(12,6),
    min_power_mw DECIMAL(12,6),
    in_service BOOLEAN DEFAULT TRUE,
    zone VARCHAR(50),
    additional_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Network Lines (Edges) - Enhanced
CREATE TABLE cim_network.network_lines (
    line_id VARCHAR(50) PRIMARY KEY,
    line_name VARCHAR(100),
    from_bus_id VARCHAR(50) REFERENCES cim_network.network_buses(bus_id),
    to_bus_id VARCHAR(50) REFERENCES cim_network.network_buses(bus_id),
    geometry GEOMETRY(LINESTRING, 4326),
    resistance_ohm DECIMAL(12,6),
    reactance_ohm DECIMAL(12,6),
    susceptance_s DECIMAL(12,6),
    max_current_ka DECIMAL(8,3),
    max_power_mw DECIMAL(12,6),
    length_km DECIMAL(10,3),
    line_type VARCHAR(50), -- 'overhead', 'underground', 'cable'
    voltage_level_kv DECIMAL(10,3),
    in_service BOOLEAN DEFAULT TRUE,
    parallel INTEGER DEFAULT 1,
    df DECIMAL(8,3) DEFAULT 1.0,
    additional_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Network Components (Loads, Generators, etc.)
CREATE TABLE cim_network.network_components (
    component_id VARCHAR(50) PRIMARY KEY,
    component_type VARCHAR(20) NOT NULL, -- 'load', 'gen', 'trafo', 'switch', etc.
    bus_id VARCHAR(50) REFERENCES cim_network.network_buses(bus_id),
    component_name VARCHAR(100),
    geometry GEOMETRY(POINT, 4326),
    additional_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Link buses to scenarios
CREATE TABLE cim_network.scenario_buses (
    scenario_id UUID REFERENCES cim_network.network_scenarios(scenario_id),
    bus_id VARCHAR(50) REFERENCES cim_network.network_buses(bus_id),
    PRIMARY KEY (scenario_id, bus_id)
);

-- Link lines to scenarios
CREATE TABLE cim_network.scenario_lines (
    scenario_id UUID REFERENCES cim_network.network_scenarios(scenario_id),
    line_id VARCHAR(50) REFERENCES cim_network.network_lines(line_id),
    PRIMARY KEY (scenario_id, line_id)
);

-- Link components to scenarios
CREATE TABLE cim_network.scenario_components (
    scenario_id UUID REFERENCES cim_network.network_scenarios(scenario_id),
    component_id VARCHAR(50) REFERENCES cim_network.network_components(component_id),
    PRIMARY KEY (scenario_id, component_id)
);

-- Create spatial indexes
CREATE INDEX network_buses_geometry_gist_idx ON cim_network.network_buses USING gist (geometry);
CREATE INDEX network_lines_geometry_gist_idx ON cim_network.network_lines USING gist (geometry);
CREATE INDEX network_components_geometry_gist_idx ON cim_network.network_components USING gist (geometry);

-- Create performance indexes
CREATE INDEX network_buses_bus_type_idx ON cim_network.network_buses (bus_type);
CREATE INDEX network_buses_voltage_kv_idx ON cim_network.network_buses (voltage_kv);
CREATE INDEX network_buses_in_service_idx ON cim_network.network_buses (in_service);
CREATE INDEX network_lines_from_bus_idx ON cim_network.network_lines (from_bus_id);
CREATE INDEX network_lines_to_bus_idx ON cim_network.network_lines (to_bus_id);
CREATE INDEX network_lines_voltage_level_idx ON cim_network.network_lines (voltage_level_kv);
CREATE INDEX network_lines_in_service_idx ON cim_network.network_lines (in_service);
CREATE INDEX network_components_type_idx ON cim_network.network_components (component_type);
CREATE INDEX network_components_bus_idx ON cim_network.network_components (bus_id);

-- Create JSONB indexes for additional_data
CREATE INDEX network_buses_additional_data_gin_idx ON cim_network.network_buses USING gin (additional_data);
CREATE INDEX network_lines_additional_data_gin_idx ON cim_network.network_lines USING gin (additional_data);
CREATE INDEX network_components_additional_data_gin_idx ON cim_network.network_components USING gin (additional_data);

-- Comments
COMMENT ON SCHEMA cim_network IS 'Comprehensive network topology and electrical data for CIM Wizard';
COMMENT ON TABLE cim_network.network_scenarios IS 'Different network scenarios (with/without PV)';
COMMENT ON TABLE cim_network.network_buses IS 'Electrical buses (nodes) in the network with enhanced data';
COMMENT ON TABLE cim_network.network_lines IS 'Transmission/distribution lines (edges) in the network with enhanced data';
COMMENT ON TABLE cim_network.network_components IS 'Other network components (loads, generators, transformers, etc.)';
COMMENT ON COLUMN cim_network.network_buses.additional_data IS 'Additional bus parameters as JSON';
COMMENT ON COLUMN cim_network.network_lines.additional_data IS 'Additional line parameters as JSON';
COMMENT ON COLUMN cim_network.network_components.additional_data IS 'Component-specific parameters as JSON';
"""

def generate_comprehensive_insert_sql(buses, lines, components, scenario_id, scenario_name, network_type):
    """Generate comprehensive SQL INSERT statements."""
    sql_content = f"""--
-- CIM Wizard Comprehensive Network Data: {scenario_name}
-- Network Type: {network_type}
-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
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

-- Insert scenario
INSERT INTO cim_network.network_scenarios (scenario_id, scenario_name, network_type) VALUES
('{scenario_id}', '{scenario_name}', '{network_type}');

"""
    
    # Insert buses
    if buses:
        sql_content += "\n-- Insert buses\n"
        sql_content += "INSERT INTO cim_network.network_buses (bus_id, bus_name, bus_type, voltage_kv, geometry, active_power_mw, reactive_power_mvar, max_power_mw, min_power_mw, in_service, zone, additional_data) VALUES\n"
        
        for i, bus in enumerate(buses):
            geometry = bus['geometry'] if bus['geometry'] else 'NULL'
            additional_data = json.dumps(bus['additional_data']) if bus['additional_data'] else 'NULL'
            in_service = 'TRUE' if bus['in_service'] else 'FALSE'
            zone = f"'{bus['zone']}'" if bus['zone'] else 'NULL'
            
            sql_content += f"('{bus['bus_id']}', '{bus['bus_name']}', '{bus['bus_type']}', {bus['voltage_kv']}, {geometry}, {bus['active_power_mw']}, {bus['reactive_power_mvar']}, {bus['max_power_mw']}, {bus['min_power_mw']}, {in_service}, {zone}, '{additional_data}')"
            
            if i < len(buses) - 1:
                sql_content += ",\n"
            else:
                sql_content += ";\n"
        
        # Link buses to scenario
        sql_content += "\n-- Link buses to scenario\n"
        sql_content += "INSERT INTO cim_network.scenario_buses (scenario_id, bus_id) VALUES\n"
        for i, bus in enumerate(buses):
            sql_content += f"('{scenario_id}', '{bus['bus_id']}')"
            if i < len(buses) - 1:
                sql_content += ",\n"
            else:
                sql_content += ";\n"
    
    # Insert lines
    if lines:
        sql_content += "\n-- Insert lines\n"
        sql_content += "INSERT INTO cim_network.network_lines (line_id, line_name, from_bus_id, to_bus_id, geometry, resistance_ohm, reactance_ohm, susceptance_s, max_current_ka, max_power_mw, length_km, line_type, voltage_level_kv, in_service, parallel, df, additional_data) VALUES\n"
        
        for i, line in enumerate(lines):
            geometry = line['geometry'] if line['geometry'] else 'NULL'
            additional_data = json.dumps(line['additional_data']) if line['additional_data'] else 'NULL'
            in_service = 'TRUE' if line['in_service'] else 'FALSE'
            
            sql_content += f"('{line['line_id']}', '{line['line_name']}', '{line['from_bus_id']}', '{line['to_bus_id']}', {geometry}, {line['resistance_ohm']}, {line['reactance_ohm']}, {line['susceptance_s']}, {line['max_current_ka']}, {line['max_power_mw']}, {line['length_km']}, '{line['line_type']}', {line['voltage_level_kv']}, {in_service}, {line['parallel']}, {line['df']}, '{additional_data}')"
            
            if i < len(lines) - 1:
                sql_content += ",\n"
            else:
                sql_content += ";\n"
        
        # Link lines to scenario
        sql_content += "\n-- Link lines to scenario\n"
        sql_content += "INSERT INTO cim_network.scenario_lines (scenario_id, line_id) VALUES\n"
        for i, line in enumerate(lines):
            sql_content += f"('{scenario_id}', '{line['line_id']}')"
            if i < len(lines) - 1:
                sql_content += ",\n"
            else:
                sql_content += ";\n"
    
    # Insert components
    if components:
        sql_content += "\n-- Insert network components\n"
        sql_content += "INSERT INTO cim_network.network_components (component_id, component_type, bus_id, component_name, geometry, additional_data) VALUES\n"
        
        component_count = 0
        for comp_type, comp_list in components.items():
            for comp in comp_list:
                additional_data = json.dumps(comp['additional_data']) if comp['additional_data'] else 'NULL'
                bus_id = comp['additional_data'].get('bus', 'NULL') if comp['additional_data'] else 'NULL'
                if bus_id != 'NULL':
                    bus_id = f"'{bus_id}'"
                name = comp['additional_data'].get('name', f"{comp_type}_{comp['id']}") if comp['additional_data'] else f"{comp_type}_{comp['id']}"
                
                sql_content += f"('{comp['id']}', '{comp_type}', {bus_id}, '{name}', NULL, '{additional_data}')"
                component_count += 1
                if component_count < sum(len(comp_list) for comp_list in components.values()):
                    sql_content += ",\n"
                else:
                    sql_content += ";\n"
        
        # Link components to scenario
        if component_count > 0:
            sql_content += "\n-- Link components to scenario\n"
            sql_content += "INSERT INTO cim_network.scenario_components (scenario_id, component_id) VALUES\n"
            
            comp_count = 0
            for comp_type, comp_list in components.items():
                for comp in comp_list:
                    sql_content += f"('{scenario_id}', '{comp['id']}')"
                    comp_count += 1
                    if comp_count < sum(len(comp_list) for comp_list in components.values()):
                        sql_content += ",\n"
                    else:
                        sql_content += ";\n"
    
    sql_content += """
-- Data insertion complete
SELECT 'Comprehensive network data inserted successfully' as status;
"""
    
    return sql_content

def main():
    """Main function to inspect and extract pandapower network data."""
    print("Starting Comprehensive Pandapower Network Inspection and Extraction...")
    
    # Define network files
    network_files = [
        ("rawdata/network_PV.p", "Network with PV", "with_PV"),
        ("rawdata/network_without_PV.p", "Network without PV", "without_PV")
    ]
    
    # Create initdb directory if it doesn't exist
    initdb_dir = Path("initdb")
    initdb_dir.mkdir(exist_ok=True)
    
    # Generate comprehensive schema
    schema_sql = generate_comprehensive_schema()
    schema_path = initdb_dir / "08-network_comprehensive_schema.sql"
    
    with open(schema_path, 'w', encoding='utf-8') as f:
        f.write(schema_sql)
    print(f"Created: {schema_path}")
    
    # Process each network file
    for file_path, scenario_name, network_type in network_files:
        if Path(file_path).exists():
            print(f"\nProcessing {file_path}...")
            
            # Load network data
            try:
                with open(file_path, 'rb') as f:
                    network = pickle.load(f)
                
                # Inspect network structure
                dataframes = inspect_network_structure(network, scenario_name)
                
                # Extract comprehensive data
                buses = extract_comprehensive_bus_data(network, scenario_name)
                lines = extract_comprehensive_line_data(network, scenario_name)
                components = extract_other_components(network, scenario_name)
                
                # Generate scenario ID
                scenario_id = str(uuid.uuid4())
                
                # Generate comprehensive SQL
                sql_content = generate_comprehensive_insert_sql(
                    buses, lines, components, scenario_id, scenario_name, network_type
                )
                
                # Determine output filename
                if "with_PV" in network_type:
                    output_file = "18-network_with_PV_comprehensive_data.sql"
                else:
                    output_file = "18-network_without_PV_comprehensive_data.sql"
                
                output_path = initdb_dir / output_file
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(sql_content)
                print(f"Created: {output_path}")
                
                # Print summary
                print(f"\nSUMMARY for {scenario_name}:")
                print(f"  - Buses: {len(buses)}")
                print(f"  - Lines: {len(lines)}")
                print(f"  - Components: {sum(len(comp_list) for comp_list in components.values())}")
                for comp_type, comp_list in components.items():
                    if comp_list:
                        print(f"    - {comp_type}: {len(comp_list)}")
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
        else:
            print(f"File not found: {file_path}")
    
    print("\nComprehensive network data extraction completed!")
    print("\nGenerated files:")
    print("  - 08-network_comprehensive_schema.sql (Enhanced network schema)")
    print("  - 18-network_with_PV_comprehensive_data.sql (Network with PV data)")
    print("  - 18-network_without_PV_comprehensive_data.sql (Network without PV data)")

if __name__ == "__main__":
    main()
