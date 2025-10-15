#!/usr/bin/env python3
"""
Convert Turin powergrid GeoJSON files to SQL - Fixed version with proper order
"""

import json
import uuid
from datetime import datetime

def generate_schema():
    """Generate the network schema SQL."""
    return """
--
-- CIM Wizard Turin Network Schema
-- Powergrid data for Turin
--

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create network schema
CREATE SCHEMA IF NOT EXISTS cim_network;

-- Network Scenarios
CREATE TABLE IF NOT EXISTS cim_network.network_scenarios (
    scenario_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_name VARCHAR(100) NOT NULL,
    description TEXT,
    network_type VARCHAR(20),
    city VARCHAR(50) DEFAULT 'Turin',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Network Buses (Nodes)
CREATE TABLE IF NOT EXISTS cim_network.network_buses (
    bus_id VARCHAR(50) PRIMARY KEY,
    bus_name VARCHAR(100),
    bus_type VARCHAR(20),
    voltage_kv DECIMAL(10,3),
    geometry public.geometry(POINT, 4326),
    zone VARCHAR(50),
    in_service BOOLEAN DEFAULT TRUE,
    min_vm_pu DECIMAL(8,3),
    max_vm_pu DECIMAL(8,3),
    additional_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Network Lines (Edges)
CREATE TABLE IF NOT EXISTS cim_network.network_lines (
    line_id VARCHAR(50) PRIMARY KEY,
    line_name VARCHAR(100),
    from_bus_id VARCHAR(50),
    to_bus_id VARCHAR(50),
    geometry public.geometry(LINESTRING, 4326),
    length_km DECIMAL(10,3),
    r_ohm_per_km DECIMAL(12,6),
    x_ohm_per_km DECIMAL(12,6),
    c_nf_per_km DECIMAL(12,6),
    g_us_per_km DECIMAL(12,6),
    max_i_ka DECIMAL(8,3),
    df DECIMAL(8,3) DEFAULT 1.0,
    parallel INTEGER DEFAULT 1,
    line_type VARCHAR(50),
    in_service BOOLEAN DEFAULT TRUE,
    max_loading_percent DECIMAL(5,2),
    length_km_rnm DECIMAL(10,3),
    additional_data JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Link buses to scenarios
CREATE TABLE IF NOT EXISTS cim_network.scenario_buses (
    scenario_id UUID REFERENCES cim_network.network_scenarios(scenario_id),
    bus_id VARCHAR(50) REFERENCES cim_network.network_buses(bus_id),
    PRIMARY KEY (scenario_id, bus_id)
);

-- Link lines to scenarios
CREATE TABLE IF NOT EXISTS cim_network.scenario_lines (
    scenario_id UUID REFERENCES cim_network.network_scenarios(scenario_id),
    line_id VARCHAR(50) REFERENCES cim_network.network_lines(line_id),
    PRIMARY KEY (scenario_id, line_id)
);

-- Create spatial indexes
CREATE INDEX IF NOT EXISTS network_buses_geometry_gist_idx ON cim_network.network_buses USING gist (geometry);
CREATE INDEX IF NOT EXISTS network_lines_geometry_gist_idx ON cim_network.network_lines USING gist (geometry);

-- Create performance indexes
CREATE INDEX IF NOT EXISTS network_buses_bus_type_idx ON cim_network.network_buses (bus_type);
CREATE INDEX IF NOT EXISTS network_buses_voltage_kv_idx ON cim_network.network_buses (voltage_kv);
CREATE INDEX IF NOT EXISTS network_buses_in_service_idx ON cim_network.network_buses (in_service);
CREATE INDEX IF NOT EXISTS network_lines_from_bus_idx ON cim_network.network_lines (from_bus_id);
CREATE INDEX IF NOT EXISTS network_lines_to_bus_idx ON cim_network.network_lines (to_bus_id);
CREATE INDEX IF NOT EXISTS network_lines_in_service_idx ON cim_network.network_lines (in_service);

-- Create JSONB indexes
CREATE INDEX IF NOT EXISTS network_buses_additional_data_gin_idx ON cim_network.network_buses USING gin (additional_data);
CREATE INDEX IF NOT EXISTS network_lines_additional_data_gin_idx ON cim_network.network_lines USING gin (additional_data);

-- Comments
COMMENT ON SCHEMA cim_network IS 'Network topology and electrical data for Turin powergrid';
COMMENT ON TABLE cim_network.network_scenarios IS 'Different network scenarios for Turin';
COMMENT ON TABLE cim_network.network_buses IS 'Electrical buses (nodes) in Turin network';
COMMENT ON TABLE cim_network.network_lines IS 'Transmission/distribution lines (edges) in Turin network';
"""

def generate_scenario_data():
    """Generate scenario data SQL."""
    scenario_id = str(uuid.uuid4())
    
    sql_content = f"""--
-- Turin Network Scenario Data
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

-- Insert Turin scenario
INSERT INTO cim_network.network_scenarios (scenario_id, scenario_name, network_type, city) VALUES
('{scenario_id}', 'Turin Powergrid', 'turin_grid', 'Turin');

SELECT 'Turin scenario data inserted successfully' as status;
"""
    
    return sql_content, scenario_id

def convert_buses_geojson(scenario_id):
    """Convert buses.geojson to SQL."""
    print("Converting buses.geojson...")
    
    with open('rawdata/buses.geojson', 'r') as f:
        data = json.load(f)
    
    sql_content = f"""--
-- Turin Network Buses Data
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

-- Insert buses
INSERT INTO cim_network.network_buses (bus_id, bus_name, bus_type, voltage_kv, geometry, zone, in_service, min_vm_pu, max_vm_pu, additional_data) VALUES
"""
    
    buses = []
    for i, feature in enumerate(data['features']):
        props = feature['properties']
        geom = feature['geometry']
        
        # Extract coordinates
        coords = geom['coordinates']
        geometry = f"public.ST_GeomFromText('POINT({coords[0]} {coords[1]})', 4326)::public.geometry"
        
        # Extract properties
        bus_id = str(i)
        bus_name = props.get('name', f'Bus_{i}')
        bus_type = props.get('type', 'unknown')
        voltage_kv = props.get('vn_kv', 0.0)
        zone = props.get('zone', 'Turin')
        in_service = props.get('in_service', True)
        min_vm_pu = props.get('min_vm_pu', 0.9)
        max_vm_pu = props.get('max_vm_pu', 1.1)
        
        # Additional data
        additional_data = {}
        for key, value in props.items():
            if key not in ['name', 'type', 'vn_kv', 'zone', 'in_service', 'min_vm_pu', 'max_vm_pu', 'geo']:
                additional_data[key] = value
        
        additional_data_json = json.dumps(additional_data) if additional_data else None
        in_service_str = 'TRUE' if in_service else 'FALSE'
        
        additional_data_sql = f"'{additional_data_json}'" if additional_data_json else 'NULL'
        buses.append(f"('{bus_id}', '{bus_name}', '{bus_type}', {voltage_kv}, {geometry}, '{zone}', {in_service_str}, {min_vm_pu}, {max_vm_pu}, {additional_data_sql})")
    
    sql_content += ',\n'.join(buses) + ';\n\n'
    
    sql_content += "SELECT 'Turin buses data inserted successfully' as status;\n"
    
    return sql_content

def convert_lines_geojson():
    """Convert lines.geojson to SQL."""
    print("Converting lines.geojson...")
    
    with open('rawdata/lines.geojson', 'r') as f:
        data = json.load(f)
    
    sql_content = f"""--
-- Turin Network Lines Data
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

-- Insert lines
INSERT INTO cim_network.network_lines (line_id, line_name, from_bus_id, to_bus_id, geometry, length_km, r_ohm_per_km, x_ohm_per_km, c_nf_per_km, g_us_per_km, max_i_ka, df, parallel, line_type, in_service, max_loading_percent, length_km_rnm, additional_data) VALUES
"""
    
    lines = []
    for i, feature in enumerate(data['features']):
        props = feature['properties']
        geom = feature['geometry']
        
        # Extract coordinates for LineString
        coords = geom['coordinates']
        coord_pairs = [f"{coord[0]} {coord[1]}" for coord in coords]
        geometry = f"public.ST_GeomFromText('LINESTRING({', '.join(coord_pairs)})', 4326)::public.geometry"
        
        # Extract properties
        line_id = str(i)
        line_name = props.get('name', f'Line_{i}')
        from_bus_id = str(props.get('from_bus', ''))
        to_bus_id = str(props.get('to_bus', ''))
        length_km = props.get('length_km', 0.0)
        r_ohm_per_km = props.get('r_ohm_per_km', 0.0)
        x_ohm_per_km = props.get('x_ohm_per_km', 0.0)
        c_nf_per_km = props.get('c_nf_per_km', 0.0)
        g_us_per_km = props.get('g_us_per_km', 0.0)
        max_i_ka = props.get('max_i_ka', 0.0)
        df = props.get('df', 1.0)
        parallel = props.get('parallel', 1)
        line_type = props.get('type', 'unknown')
        in_service = props.get('in_service', True)
        max_loading_percent = props.get('max_loading_percent', 100.0)
        length_km_rnm = props.get('length_km_RNM', 0.0)
        
        # Additional data
        additional_data = {}
        for key, value in props.items():
            if key not in ['name', 'from_bus', 'to_bus', 'length_km', 'r_ohm_per_km', 'x_ohm_per_km', 'c_nf_per_km', 'g_us_per_km', 'max_i_ka', 'df', 'parallel', 'type', 'in_service', 'max_loading_percent', 'length_km_RNM', 'coordinates', 'geo']:
                additional_data[key] = value
        
        additional_data_json = json.dumps(additional_data) if additional_data else None
        in_service_str = 'TRUE' if in_service else 'FALSE'
        
        additional_data_sql = f"'{additional_data_json}'" if additional_data_json else 'NULL'
        lines.append(f"('{line_id}', '{line_name}', '{from_bus_id}', '{to_bus_id}', {geometry}, {length_km}, {r_ohm_per_km}, {x_ohm_per_km}, {c_nf_per_km}, {g_us_per_km}, {max_i_ka}, {df}, {parallel}, '{line_type}', {in_service_str}, {max_loading_percent}, {length_km_rnm}, {additional_data_sql})")
    
    sql_content += ',\n'.join(lines) + ';\n\n'
    
    sql_content += "SELECT 'Turin lines data inserted successfully' as status;\n"
    
    return sql_content

def generate_scenario_buses_data(scenario_id):
    """Generate scenario_buses linking data."""
    print("Generating scenario_buses data...")
    
    with open('rawdata/buses.geojson', 'r') as f:
        data = json.load(f)
    
    sql_content = f"""--
-- Turin Network Scenario-Buses Linking Data
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

-- Link buses to scenario
INSERT INTO cim_network.scenario_buses (scenario_id, bus_id) VALUES
"""
    
    scenario_links = []
    for i in range(len(data['features'])):
        scenario_links.append(f"('{scenario_id}', '{i}')")
    
    sql_content += ',\n'.join(scenario_links) + ';\n\n'
    
    sql_content += "SELECT 'Turin scenario-buses linking data inserted successfully' as status;\n"
    
    return sql_content

def generate_scenario_lines_data(scenario_id):
    """Generate scenario_lines linking data."""
    print("Generating scenario_lines data...")
    
    with open('rawdata/lines.geojson', 'r') as f:
        data = json.load(f)
    
    sql_content = f"""--
-- Turin Network Scenario-Lines Linking Data
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

-- Link lines to scenario
INSERT INTO cim_network.scenario_lines (scenario_id, line_id) VALUES
"""
    
    scenario_links = []
    for i in range(len(data['features'])):
        scenario_links.append(f"('{scenario_id}', '{i}')")
    
    sql_content += ',\n'.join(scenario_links) + ';\n\n'
    
    sql_content += "SELECT 'Turin scenario-lines linking data inserted successfully' as status;\n"
    
    return sql_content

def main():
    """Main function."""
    print("Converting Turin GeoJSON files to SQL with proper order...")
    
    # Generate schema
    schema_sql = generate_schema()
    with open('08-turin_network_schema.sql', 'w') as f:
        f.write(schema_sql)
    print("Created: 08-turin_network_schema.sql")
    
    # Generate scenario data
    scenario_sql, scenario_id = generate_scenario_data()
    with open('18-turin_scenario_data.sql', 'w') as f:
        f.write(scenario_sql)
    print("Created: 18-turin_scenario_data.sql")
    
    # Convert buses
    buses_sql = convert_buses_geojson(scenario_id)
    with open('18-turin_buses_data.sql', 'w') as f:
        f.write(buses_sql)
    print("Created: 18-turin_buses_data.sql")
    
    # Convert lines
    lines_sql = convert_lines_geojson()
    with open('18-turin_lines_data.sql', 'w') as f:
        f.write(lines_sql)
    print("Created: 18-turin_lines_data.sql")
    
    # Generate scenario-buses linking
    scenario_buses_sql = generate_scenario_buses_data(scenario_id)
    with open('18-turin_scenario_buses_data.sql', 'w') as f:
        f.write(scenario_buses_sql)
    print("Created: 18-turin_scenario_buses_data.sql")
    
    # Generate scenario-lines linking
    scenario_lines_sql = generate_scenario_lines_data(scenario_id)
    with open('18-turin_scenario_lines_data.sql', 'w') as f:
        f.write(scenario_lines_sql)
    print("Created: 18-turin_scenario_lines_data.sql")
    
    print("\nConversion completed!")
    print("Generated files in correct order:")
    print("  1. 08-turin_network_schema.sql (Schema)")
    print("  2. 18-turin_scenario_data.sql (Scenario)")
    print("  3. 18-turin_buses_data.sql (Buses)")
    print("  4. 18-turin_lines_data.sql (Lines)")
    print("  5. 18-turin_scenario_buses_data.sql (Scenario-Buses linking)")
    print("  6. 18-turin_scenario_lines_data.sql (Scenario-Lines linking)")

if __name__ == "__main__":
    main()
