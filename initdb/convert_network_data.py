#!/usr/bin/env python3
"""
Pandapowered Network Data Converter
Converts .p pickle files to PostGIS-compatible SQL format
"""

import pickle
import pandas as pd
import numpy as np
from pathlib import Path
import uuid
from datetime import datetime
import pandapower as pp

def load_network_data(file_path):
    """Load pandapowered network data from pickle file."""
    try:
        # Try pandapower first, fall back to standard pickle
        try:
            network = pp.from_pickle(file_path)
            return network
        except:
            # Fallback to standard pickle loading
            with open(file_path, 'rb') as f:
                network = pickle.load(f)
            return network
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def extract_bus_data(network):
    """Extract bus data from pandapowered network."""
    buses = []
    
    # Iterate over DataFrame rows (not columns)
    for idx, bus_row in network.bus.iterrows():
        bus_info = {
            'bus_id': str(idx),  # Use DataFrame index as bus_id
            'bus_name': bus_row.get('name', f'Bus_{idx}'),
            'bus_type': bus_row.get('type', 'unknown'),
            'voltage_kv': float(bus_row.get('vn_kv', 0.0)),
            'active_power_mw': float(bus_row.get('p_mw', 0.0)),
            'reactive_power_mvar': float(bus_row.get('q_mvar', 0.0)),
            'max_power_mw': float(bus_row.get('max_p_mw', 0.0)),
            'min_power_mw': float(bus_row.get('min_p_mw', 0.0)),
            'geometry': None  # Will be populated if coordinates exist
        }
        
        # Check for geographic coordinates
        if 'x' in bus_row and 'y' in bus_row:
            x, y = bus_row['x'], bus_row['y']
            if pd.notna(x) and pd.notna(y):
                bus_info['geometry'] = f"ST_GeomFromText('POINT({x} {y})', 4326)"
        
        buses.append(bus_info)
    
    return buses

def extract_line_data(network):
    """Extract line data from pandapowered network."""
    lines = []
    
    # Iterate over DataFrame rows (not columns)
    for idx, line_row in network.line.iterrows():
        line_info = {
            'line_id': str(idx),  # Use DataFrame index as line_id
            'line_name': line_row.get('name', f'Line_{idx}'),
            'from_bus_id': str(line_row.get('from_bus', '')),
            'to_bus_id': str(line_row.get('to_bus', '')),
            'resistance_ohm': float(line_row.get('r_ohm_per_km', 0.0)),
            'reactance_ohm': float(line_row.get('x_ohm_per_km', 0.0)),
            'susceptance_s': float(line_row.get('b_us_per_km', 0.0)),
            'max_current_ka': float(line_row.get('max_i_ka', 0.0)),
            'max_power_mw': float(line_row.get('max_p_mw', 0.0)),
            'length_km': float(line_row.get('length_km', 0.0)),
            'line_type': line_row.get('type', 'unknown'),
            'voltage_level_kv': float(line_row.get('vn_kv', 0.0)),
            'geometry': None  # Will be populated if coordinates exist
        }
        
        # Try to create line geometry from bus coordinates
        from_bus = line_row.get('from_bus')
        to_bus = line_row.get('to_bus')
        
        if pd.notna(from_bus) and pd.notna(to_bus):
            # Get bus data by index
            if from_bus in network.bus.index and to_bus in network.bus.index:
                from_bus_data = network.bus.loc[from_bus]
                to_bus_data = network.bus.loc[to_bus]
                
                if ('x' in from_bus_data and 'y' in from_bus_data and 
                    'x' in to_bus_data and 'y' in to_bus_data):
                    x1, y1 = from_bus_data['x'], from_bus_data['y']
                    x2, y2 = to_bus_data['x'], to_bus_data['y']
                    
                    if all(pd.notna(coord) for coord in [x1, y1, x2, y2]):
                        line_info['geometry'] = f"ST_GeomFromText('LINESTRING({x1} {y1}, {x2} {y2})', 4326)"
        
        lines.append(line_info)
    
    return lines

def generate_sql_schema():
    """Generate the network schema SQL."""
    return """
--
-- CIM Wizard Network Schema
-- Pandapowered network data storage
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

-- Network Buses (Nodes)
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Network Lines (Edges)
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

-- Create spatial indexes
CREATE INDEX network_buses_geometry_gist_idx ON cim_network.network_buses USING gist (geometry);
CREATE INDEX network_lines_geometry_gist_idx ON cim_network.network_lines USING gist (geometry);

-- Create performance indexes
CREATE INDEX network_buses_bus_type_idx ON cim_network.network_buses (bus_type);
CREATE INDEX network_buses_voltage_kv_idx ON cim_network.network_buses (voltage_kv);
CREATE INDEX network_lines_from_bus_idx ON cim_network.network_lines (from_bus_id);
CREATE INDEX network_lines_to_bus_idx ON cim_network.network_lines (to_bus_id);
CREATE INDEX network_lines_voltage_level_idx ON cim_network.network_lines (voltage_level_kv);

-- Comments
COMMENT ON SCHEMA cim_network IS 'Network topology and electrical data for CIM Wizard';
COMMENT ON TABLE cim_network.network_scenarios IS 'Different network scenarios (with/without PV)';
COMMENT ON TABLE cim_network.network_buses IS 'Electrical buses (nodes) in the network';
COMMENT ON TABLE cim_network.network_lines IS 'Transmission/distribution lines (edges) in the network';
"""

def generate_bus_insert_sql(buses, scenario_id):
    """Generate SQL INSERT statements for buses."""
    if not buses:
        return ""
    
    sql = f"""
-- Insert buses for scenario {scenario_id}
INSERT INTO cim_network.network_buses (bus_id, bus_name, bus_type, voltage_kv, geometry, active_power_mw, reactive_power_mvar, max_power_mw, min_power_mw) VALUES
"""
    
    for i, bus in enumerate(buses):
        geometry = bus['geometry'] if bus['geometry'] else 'NULL'
        sql += f"('{bus['bus_id']}', '{bus['bus_name']}', '{bus['bus_type']}', {bus['voltage_kv']}, {geometry}, {bus['active_power_mw']}, {bus['reactive_power_mvar']}, {bus['max_power_mw']}, {bus['min_power_mw']})"
        
        if i < len(buses) - 1:
            sql += ",\n"
        else:
            sql += ";\n"
    
    # Link buses to scenario
    sql += f"""
-- Link buses to scenario
INSERT INTO cim_network.scenario_buses (scenario_id, bus_id) VALUES
"""
    
    for i, bus in enumerate(buses):
        sql += f"('{scenario_id}', '{bus['bus_id']}')"
        if i < len(buses) - 1:
            sql += ",\n"
        else:
            sql += ";\n"
    
    return sql

def generate_line_insert_sql(lines, scenario_id):
    """Generate SQL INSERT statements for lines."""
    if not lines:
        return ""
    
    sql = f"""
-- Insert lines for scenario {scenario_id}
INSERT INTO cim_network.network_lines (line_id, line_name, from_bus_id, to_bus_id, geometry, resistance_ohm, reactance_ohm, susceptance_s, max_current_ka, max_power_mw, length_km, line_type, voltage_level_kv) VALUES
"""
    
    for i, line in enumerate(lines):
        geometry = line['geometry'] if line['geometry'] else 'NULL'
        sql += f"('{line['line_id']}', '{line['line_name']}', '{line['from_bus_id']}', '{line['to_bus_id']}', {geometry}, {line['resistance_ohm']}, {line['reactance_ohm']}, {line['susceptance_s']}, {line['max_current_ka']}, {line['max_power_mw']}, {line['length_km']}, '{line['line_type']}', {line['voltage_level_kv']})"
        
        if i < len(lines) - 1:
            sql += ",\n"
        else:
            sql += ";\n"
    
    # Link lines to scenario
    sql += f"""
-- Link lines to scenario
INSERT INTO cim_network.scenario_lines (scenario_id, line_id) VALUES
"""
    
    for i, line in enumerate(lines):
        sql += f"('{scenario_id}', '{line['line_id']}')"
        if i < len(lines) - 1:
            sql += ",\n"
        else:
            sql += ";\n"
    
    return sql

def convert_network_file(file_path, scenario_name, network_type):
    """Convert a single network file to SQL."""
    print(f"Converting {file_path}...")
    
    # Load network data
    network = load_network_data(file_path)
    if not network:
        return None
    
    # Extract data
    buses = extract_bus_data(network)
    lines = extract_line_data(network)
    
    # Generate scenario ID
    scenario_id = str(uuid.uuid4())
    
    # Generate SQL
    sql_content = f"""--
-- CIM Wizard Network Data: {scenario_name}
-- Generated from: {file_path}
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
    
    # Add bus data
    sql_content += generate_bus_insert_sql(buses, scenario_id)
    
    # Add line data
    sql_content += generate_line_insert_sql(lines, scenario_id)
    
    sql_content += f"""
-- Data insertion complete
SELECT 'Network data for {scenario_name} inserted successfully' as status;
"""
    
    return sql_content

def main():
    """Main function to convert network files."""
    print("Starting Pandapowered Network Data Conversion...")
    
    # Define network files
    network_files = [
        ("rawdata/network_PV.p", "Network with PV", "with_PV"),
        ("rawdata/network_without_PV.p", "Network without PV", "without_PV")
    ]
    
    # Create initdb directory if it doesn't exist
    initdb_dir = Path("initdb")
    initdb_dir.mkdir(exist_ok=True)
    
    # Generate schema file
    schema_sql = generate_sql_schema()
    schema_path = initdb_dir / "08-network_schema.sql"
    
    with open(schema_path, 'w', encoding='utf-8') as f:
        f.write(schema_sql)
    print(f"Created: {schema_path}")
    
    # Convert each network file
    for file_path, scenario_name, network_type in network_files:
        if Path(file_path).exists():
            sql_content = convert_network_file(file_path, scenario_name, network_type)
            
            if sql_content:
                # Determine output filename
                if "with_PV" in network_type:
                    output_file = "18-network_with_PV_data.sql"
                else:
                    output_file = "18-network_without_PV_data.sql"
                
                output_path = initdb_dir / output_file
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(sql_content)
                print(f"Created: {output_path}")
            else:
                print(f"Failed to convert {file_path}")
        else:
            print(f"File not found: {file_path}")
    
    print("\nNetwork data conversion completed!")
    print("\nGenerated files:")
    print("  - 08-network_schema.sql (Network schema)")
    print("  - 18-network_with_PV_data.sql (Network with PV data)")
    print("  - 18-network_without_PV_data.sql (Network without PV data)")

if __name__ == "__main__":
    main()
