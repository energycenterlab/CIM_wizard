#!/usr/bin/env python3
"""
Sample Data Population Script for CIM Wizard Integrated
Populates Docker PostGIS with sample census and raster data for testing
"""

import psycopg2
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def get_db_connection():
    """Get database connection to Docker PostGIS"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="cim_wizard_integrated",
            user="cim_wizard_user",
            password="cim_wizard_password"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
        print("Make sure Docker PostGIS container is running:")
        print("  docker-compose up postgres -d")
        sys.exit(1)

def populate_census_data(cursor):
    """Populate sample census data for Florence area"""
    print("Populating census data...")
    
    census_data = [
        (480001001001, 'MULTIPOLYGON(((11.2 43.7, 11.25 43.7, 11.25 43.75, 11.2 43.75, 11.2 43.7)))', 'Toscana', 'Firenze', 'Firenze', 1500, 750, 750),
        (480001001002, 'MULTIPOLYGON(((11.25 43.7, 11.3 43.7, 11.3 43.75, 11.25 43.75, 11.25 43.7)))', 'Toscana', 'Firenze', 'Firenze', 1200, 600, 600),
        (480001001003, 'MULTIPOLYGON(((11.2 43.75, 11.25 43.75, 11.25 43.8, 11.2 43.8, 11.2 43.75)))', 'Toscana', 'Firenze', 'Firenze', 800, 400, 400),
        (480001001004, 'MULTIPOLYGON(((11.25 43.75, 11.3 43.75, 11.3 43.8, 11.25 43.8, 11.25 43.75)))', 'Toscana', 'Firenze', 'Firenze', 950, 475, 475),
        (480001002001, 'MULTIPOLYGON(((11.3 43.7, 11.35 43.7, 11.35 43.75, 11.3 43.75, 11.3 43.7)))', 'Toscana', 'Firenze', 'Sesto Fiorentino', 1100, 550, 550),
        (480001002002, 'MULTIPOLYGON(((11.3 43.75, 11.35 43.75, 11.35 43.8, 11.3 43.8, 11.3 43.75)))', 'Toscana', 'Firenze', 'Sesto Fiorentino', 750, 375, 375)
    ]
    
    for data in census_data:
        cursor.execute("""
            INSERT INTO cim_census.census_geo 
            (SEZ2011, geometry, REGIONE, PROVINCIA, COMUNE, P1, P2, P3)
            VALUES (%s, ST_GeomFromText(%s, 4326), %s, %s, %s, %s, %s, %s)
            ON CONFLICT (SEZ2011) DO UPDATE SET
                P1 = EXCLUDED.P1,
                P2 = EXCLUDED.P2,
                P3 = EXCLUDED.P3
        """, data)
    
    print(f"✅ Inserted {len(census_data)} census zones")

def populate_raster_data(cursor):
    """Populate sample raster data"""
    print("Populating raster data...")
    
    # Sample binary data (minimal PNG header)
    sample_raster = bytes.fromhex('89504E470D0A1A0A0000000D494844520000001000000010080600000028A0DB6F0000001974455874536F6674776172650041646F626520496D616765526561647971C9653C0000000D49444154789C63F8CFCCC0C060008007000E0C027C86FB1E0000000049454E44AE426082')
    
    # DTM data
    cursor.execute("""
        INSERT INTO cim_raster.dtm_raster 
        (filename, srid, min_elevation, max_elevation, rast)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (filename) DO UPDATE SET
            min_elevation = EXCLUDED.min_elevation,
            max_elevation = EXCLUDED.max_elevation
    """, ('florence_sample_dtm.tif', 4326, 45.0, 150.0, sample_raster))
    
    # DSM data  
    cursor.execute("""
        INSERT INTO cim_raster.dsm_raster 
        (filename, srid, min_elevation, max_elevation, rast)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (filename) DO UPDATE SET
            min_elevation = EXCLUDED.min_elevation,
            max_elevation = EXCLUDED.max_elevation
    """, ('florence_sample_dsm.tif', 4326, 45.0, 180.0, sample_raster))
    
    print("✅ Inserted DTM and DSM sample data")

def populate_vector_data(cursor):
    """Populate sample vector data"""
    print("Populating vector data...")
    
    # Project scenario
    cursor.execute("""
        INSERT INTO cim_vector.project_scenario 
        (project_id, scenario_id, project_name, scenario_name, project_boundary, project_center, project_zoom, project_crs)
        VALUES (%s, %s, %s, %s, ST_GeomFromText(%s, 4326), ST_GeomFromText(%s, 4326), %s, %s)
        ON CONFLICT (project_id, scenario_id) DO UPDATE SET
            project_name = EXCLUDED.project_name,
            scenario_name = EXCLUDED.scenario_name
    """, (
        'sample_florence_project', 'scenario_001', 
        'Sample Florence Project', 'Default Scenario',
        'POLYGON((11.2 43.7, 11.35 43.7, 11.35 43.8, 11.2 43.8, 11.2 43.7))',
        'POINT(11.275 43.75)',
        15, 4326
    ))
    
    # Buildings
    buildings_data = [
        ('florence_building_001', 'POLYGON((11.24 43.74, 11.26 43.74, 11.26 43.76, 11.24 43.76, 11.24 43.74))'),
        ('florence_building_002', 'POLYGON((11.27 43.72, 11.29 43.72, 11.29 43.74, 11.27 43.74, 11.27 43.72))'),
        ('florence_building_003', 'POLYGON((11.31 43.76, 11.33 43.76, 11.33 43.78, 11.31 43.78, 11.31 43.76))'),
    ]
    
    for building_id, geom_wkt in buildings_data:
        cursor.execute("""
            INSERT INTO cim_vector.building 
            (building_id, lod, building_geometry, building_geometry_source, census_id)
            VALUES (%s, %s, ST_GeomFromText(%s, 4326), %s, %s)
            ON CONFLICT DO NOTHING
        """, (building_id, 0, geom_wkt, 'sample_data', 480001001001))
        
        # Building properties
        cursor.execute("""
            INSERT INTO cim_vector.building_properties 
            (building_id, project_id, scenario_id, lod, height, area, volume, type, n_people, n_family)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT DO NOTHING
        """, (
            building_id, 'sample_florence_project', 'scenario_001', 0,
            15.5, 120.0, 1860.0, 'residential', 4, 1
        ))
    
    print(f"✅ Inserted {len(buildings_data)} buildings with properties")

def create_indexes(cursor):
    """Create optimized indexes for better performance"""
    print("Creating indexes...")
    
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_census_geometry ON cim_census.census_geo USING GIST(geometry)",
        "CREATE INDEX IF NOT EXISTS idx_census_sez2011 ON cim_census.census_geo(SEZ2011)",
        "CREATE INDEX IF NOT EXISTS idx_census_comune ON cim_census.census_geo(COMUNE)",
        "CREATE INDEX IF NOT EXISTS idx_building_geometry ON cim_vector.building USING GIST(building_geometry)",
        "CREATE INDEX IF NOT EXISTS idx_building_id ON cim_vector.building(building_id)",
        "CREATE INDEX IF NOT EXISTS idx_building_properties_project ON cim_vector.building_properties(project_id, scenario_id)",
    ]
    
    for index_sql in indexes:
        cursor.execute(index_sql)
    
    print(f"✅ Created {len(indexes)} indexes")

def verify_data(cursor):
    """Verify data was inserted correctly"""
    print("\nVerifying data...")
    
    queries = [
        ("Vector projects", "SELECT COUNT(*) FROM cim_vector.project_scenario"),
        ("Vector buildings", "SELECT COUNT(*) FROM cim_vector.building"),
        ("Building properties", "SELECT COUNT(*) FROM cim_vector.building_properties"),
        ("Census zones", "SELECT COUNT(*) FROM cim_census.census_geo"),
        ("DTM rasters", "SELECT COUNT(*) FROM cim_raster.dtm_raster"),
        ("DSM rasters", "SELECT COUNT(*) FROM cim_raster.dsm_raster"),
    ]
    
    for name, query in queries:
        cursor.execute(query)
        count = cursor.fetchone()[0]
        print(f"  {name}: {count}")
    
    print("\n✅ Sample data population completed successfully!")

def main():
    """Main function to populate all sample data"""
    print("🐳 CIM Wizard Integrated - Sample Data Population")
    print("=" * 60)
    
    # Connect to database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Populate all data types
        populate_vector_data(cursor)
        populate_census_data(cursor)
        populate_raster_data(cursor)
        create_indexes(cursor)
        
        # Commit all changes
        conn.commit()
        
        # Verify the data
        verify_data(cursor)
        
        print("\n🎉 Ready to test the API!")
        print("Start the application: python run.py")
        print("Test the API: python examples/simple_api_usage.py")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Error populating data: {e}")
        sys.exit(1)
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()