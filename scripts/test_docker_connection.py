#!/usr/bin/env python3
"""
Docker PostGIS Connection Test Script
Tests connection to Docker PostGIS and verifies schema setup
"""

import psycopg2
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def test_connection():
    """Test basic connection to Docker PostGIS"""
    print("🔌 Testing Docker PostGIS connection...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="cim_wizard_integrated",
            user="cim_wizard_user",
            password="cim_wizard_password"
        )
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Connected successfully!")
        print(f"   PostgreSQL version: {version.split(',')[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Troubleshooting steps:")
        print("1. Make sure Docker is running")
        print("2. Start PostGIS container: docker-compose up postgres -d")
        print("3. Check container status: docker-compose ps")
        print("4. View logs: docker-compose logs postgres")
        return False

def test_extensions():
    """Test PostGIS extensions"""
    print("\n🗺️  Testing PostGIS extensions...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="cim_wizard_integrated",
            user="cim_wizard_user",
            password="cim_wizard_password"
        )
        cursor = conn.cursor()
        
        # Check PostGIS extensions
        cursor.execute("""
            SELECT name, installed_version 
            FROM pg_available_extensions 
            WHERE name IN ('postgis', 'postgis_raster', 'postgis_topology', 'pgrouting')
            AND installed_version IS NOT NULL
            ORDER BY name;
        """)
        
        extensions = cursor.fetchall()
        if extensions:
            print("✅ PostGIS extensions installed:")
            for name, version in extensions:
                print(f"   {name}: {version}")
        else:
            print("❌ No PostGIS extensions found")
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Extension check failed: {e}")
        return False

def test_schemas():
    """Test database schemas"""
    print("\n📊 Testing database schemas...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="cim_wizard_integrated",
            user="cim_wizard_user",
            password="cim_wizard_password"
        )
        cursor = conn.cursor()
        
        # Check schemas
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name IN ('cim_vector', 'cim_census', 'cim_raster')
            ORDER BY schema_name;
        """)
        
        schemas = [row[0] for row in cursor.fetchall()]
        expected_schemas = ['cim_census', 'cim_raster', 'cim_vector']
        
        if set(schemas) == set(expected_schemas):
            print("✅ All required schemas found:")
            for schema in schemas:
                print(f"   {schema}")
        else:
            missing = set(expected_schemas) - set(schemas)
            print(f"❌ Missing schemas: {missing}")
            return False
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Schema check failed: {e}")
        return False

def test_tables():
    """Test if tables exist"""
    print("\n📋 Testing database tables...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="cim_wizard_integrated",
            user="cim_wizard_user",
            password="cim_wizard_password"
        )
        cursor = conn.cursor()
        
        # Check tables in each schema
        cursor.execute("""
            SELECT schemaname, tablename 
            FROM pg_tables 
            WHERE schemaname IN ('cim_vector', 'cim_census', 'cim_raster')
            ORDER BY schemaname, tablename;
        """)
        
        tables = cursor.fetchall()
        if tables:
            print("✅ Tables found:")
            for schema, table in tables:
                print(f"   {schema}.{table}")
        else:
            print("⚠️  No tables found - run the application first to create tables")
            print("   python run.py")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Table check failed: {e}")
        return False

def test_sample_data():
    """Test if sample data exists"""
    print("\n🔢 Testing sample data...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="cim_wizard_integrated",
            user="cim_wizard_user",
            password="cim_wizard_password"
        )
        cursor = conn.cursor()
        
        # Check data in each schema
        data_queries = [
            ("Vector projects", "SELECT COUNT(*) FROM cim_vector.project_scenario"),
            ("Vector buildings", "SELECT COUNT(*) FROM cim_vector.building"),
            ("Census zones", "SELECT COUNT(*) FROM cim_census.census_geo"),
            ("DTM rasters", "SELECT COUNT(*) FROM cim_raster.dtm_raster"),
            ("DSM rasters", "SELECT COUNT(*) FROM cim_raster.dsm_raster"),
        ]
        
        print("📊 Data counts:")
        total_records = 0
        for name, query in data_queries:
            try:
                cursor.execute(query)
                count = cursor.fetchone()[0]
                print(f"   {name}: {count}")
                total_records += count
            except psycopg2.ProgrammingError:
                print(f"   {name}: Table not found")
        
        if total_records > 0:
            print("✅ Sample data found")
        else:
            print("⚠️  No data found - populate sample data:")
            print("   python scripts/populate_sample_data.py")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Data check failed: {e}")
        return False

def test_permissions():
    """Test database permissions"""
    print("\n🔐 Testing database permissions...")
    
    try:
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            database="cim_wizard_integrated",
            user="cim_wizard_user",
            password="cim_wizard_password"
        )
        cursor = conn.cursor()
        
        # Test write permissions
        test_table = "cim_vector.test_permissions"
        
        # Try to create a test table
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {test_table} (
                id SERIAL PRIMARY KEY,
                test_data TEXT
            );
        """)
        
        # Try to insert data
        cursor.execute(f"INSERT INTO {test_table} (test_data) VALUES ('permission_test');")
        
        # Try to read data
        cursor.execute(f"SELECT COUNT(*) FROM {test_table};")
        count = cursor.fetchone()[0]
        
        # Clean up
        cursor.execute(f"DROP TABLE {test_table};")
        
        conn.commit()
        
        print("✅ Read/write permissions working")
        
        cursor.close()
        conn.close()
        return True
        
    except psycopg2.Error as e:
        print(f"❌ Permission test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🐳 Docker PostGIS Connection & Setup Test")
    print("=" * 50)
    
    all_tests = [
        test_connection,
        test_extensions,
        test_schemas,
        test_tables,
        test_sample_data,
        test_permissions
    ]
    
    passed = 0
    for test_func in all_tests:
        if test_func():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{len(all_tests)} passed")
    
    if passed == len(all_tests):
        print("🎉 All tests passed! Docker PostGIS is ready!")
        print("\n📚 Next steps:")
        print("1. Start the application: python run.py")
        print("2. Test the API: python examples/simple_api_usage.py")
        print("3. Access pgAdmin: http://localhost:5050")
    else:
        print("⚠️  Some tests failed. Check the output above for troubleshooting.")
        
        print("\n🔧 Common fixes:")
        print("1. Restart containers: docker-compose restart")
        print("2. Rebuild containers: docker-compose down && docker-compose up --build")
        print("3. Check logs: docker-compose logs postgres")

if __name__ == "__main__":
    main()