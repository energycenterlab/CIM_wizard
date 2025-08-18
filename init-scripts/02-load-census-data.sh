#!/bin/bash
# Load census data from GPKG file into cim_census schema using ogr2ogr
# This approach avoids ogr_fdw issues

set -e

echo "Loading census data from GPKG file..."

# Database connection parameters
export PGHOST=localhost
export PGPORT=5432
export PGDATABASE=${POSTGRES_DB}
export PGUSER=${POSTGRES_USER}
export PGPASSWORD=${POSTGRES_PASSWORD}

# Check if GPKG file exists
if [ ! -f "/rawdata/sansalva_census.gpkg" ]; then
    echo "Error: Census GPKG file not found at /rawdata/sansalva_census.gpkg"
    exit 1
fi

# Check GDAL formats
echo "Checking GDAL formats..."
ogrinfo --formats | grep -i gpkg || echo "Warning: GPKG format may not be available"

# Get layer information
echo "Inspecting GPKG file..."
ogrinfo /rawdata/sansalva_census.gpkg

# Load census data using ogr2ogr
echo "Loading census data into database..."

# Create the target table with proper schema
psql -c "
CREATE TABLE IF NOT EXISTS cim_census.census_geo (
    id SERIAL PRIMARY KEY,
    SEZ2011 BIGINT UNIQUE,
    geometry GEOMETRY(MULTIPOLYGON, 4326),
    
    -- Census administrative attributes
    Shape_Area FLOAT,
    CODREG VARCHAR(10), REGIONE VARCHAR(50), CODPRO VARCHAR(10), PROVINCIA VARCHAR(50),
    CODCOM VARCHAR(10), COMUNE VARCHAR(50), PROCOM VARCHAR(10), NSEZ VARCHAR(10), 
    ACE VARCHAR(10), CODLOC VARCHAR(10), CODASC VARCHAR(10),
    
    -- Population attributes
    P1 INTEGER, P2 INTEGER, P3 INTEGER, P4 INTEGER, P5 INTEGER,
    P6 INTEGER, P7 INTEGER, P8 INTEGER, P9 INTEGER, P10 INTEGER,
    P11 INTEGER, P12 INTEGER, P13 INTEGER, P14 INTEGER, P15 INTEGER,
    P16 INTEGER, P17 INTEGER, P18 INTEGER, P19 INTEGER, P20 INTEGER,
    P21 INTEGER, P22 INTEGER, P23 INTEGER, P24 INTEGER, P25 INTEGER,
    P26 INTEGER, P27 INTEGER, P28 INTEGER, P29 INTEGER, P30 INTEGER,
    P31 INTEGER, P32 INTEGER, P33 INTEGER, P34 INTEGER, P35 INTEGER,
    P36 INTEGER, P37 INTEGER, P38 INTEGER, P39 INTEGER, P40 INTEGER,
    P41 INTEGER, P42 INTEGER, P43 INTEGER, P44 INTEGER, P45 INTEGER,
    P46 INTEGER, P47 INTEGER, P48 INTEGER, P49 INTEGER, P50 INTEGER,
    P51 INTEGER, P52 INTEGER, P53 INTEGER, P54 INTEGER, P55 INTEGER,
    P56 INTEGER, P57 INTEGER, P58 INTEGER, P59 INTEGER, P60 INTEGER,
    P61 INTEGER, P62 INTEGER, P64 INTEGER, P65 INTEGER, P66 INTEGER,
    P128 INTEGER, P129 INTEGER, P130 INTEGER, P131 INTEGER, P132 INTEGER,
    P135 INTEGER, P136 INTEGER, P137 INTEGER, P138 INTEGER, P139 INTEGER, P140 INTEGER,
    
    -- Housing statistics
    ST1 INTEGER, ST2 INTEGER, ST3 INTEGER, ST4 INTEGER, ST5 INTEGER,
    ST6 INTEGER, ST7 INTEGER, ST8 INTEGER, ST9 INTEGER, ST10 INTEGER,
    ST11 INTEGER, ST12 INTEGER, ST13 INTEGER, ST14 INTEGER, ST15 INTEGER,
    
    -- Building age attributes
    A2 INTEGER, A3 INTEGER, A5 INTEGER, A6 INTEGER, A7 INTEGER,
    A44 INTEGER, A46 INTEGER, A47 INTEGER, A48 INTEGER,
    
    -- Family attributes
    PF1 INTEGER, PF2 INTEGER, PF3 INTEGER, PF4 INTEGER, PF5 INTEGER,
    PF6 INTEGER, PF7 INTEGER, PF8 INTEGER, PF9 INTEGER,
    
    -- Building period attributes
    E1 INTEGER, E2 INTEGER, E3 INTEGER, E4 INTEGER, E5 INTEGER,
    E6 INTEGER, E7 INTEGER, E8 INTEGER, E9 INTEGER, E10 INTEGER,
    E11 INTEGER, E12 INTEGER, E13 INTEGER, E14 INTEGER, E15 INTEGER,
    E16 INTEGER, E17 INTEGER, E18 INTEGER, E19 INTEGER, E20 INTEGER,
    E21 INTEGER, E22 INTEGER, E23 INTEGER, E24 INTEGER, E25 INTEGER,
    E26 INTEGER, E27 INTEGER, E28 INTEGER, E29 INTEGER, E30 INTEGER, E31 INTEGER
);"

# Use ogr2ogr to load data directly into PostgreSQL
# Use the correct layer name from the GPKG file
ogr2ogr -f "PostgreSQL" \
    PG:"host=localhost port=5432 dbname=${POSTGRES_DB} user=${POSTGRES_USER} password=${POSTGRES_PASSWORD}" \
    /rawdata/sansalva_census.gpkg \
    Torino_sezCens_data \
    -nln cim_census.census_geo_temp \
    -t_srs EPSG:4326 \
    -overwrite \
    -lco GEOMETRY_NAME=geometry \
    -lco SPATIAL_INDEX=NO \
    -nlt MULTIPOLYGON

# Copy data from temp table to final table
echo "Inspecting temp table structure..."
psql -c "\d cim_census.census_geo_temp"

echo "Copying data with type casting..."
psql -c "
INSERT INTO cim_census.census_geo (
    SEZ2011, geometry, Shape_Area, CODREG, REGIONE, CODPRO, PROVINCIA,
    CODCOM, COMUNE, PROCOM, NSEZ, ACE, CODLOC, CODASC,
    P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11, P12, P13, P14, P15, P16, P17, P18, P19, P20,
    P21, P22, P23, P24, P25, P26, P27, P28, P29, P30, P31, P32, P33, P34, P35, P36, P37, P38, P39, P40,
    P41, P42, P43, P44, P45, P46, P47, P48, P49, P50, P51, P52, P53, P54, P55, P56, P57, P58, P59, P60,
    P61, P62, P64, P65, P66, P128, P129, P130, P131, P132, P135, P136, P137, P138, P139, P140,
    ST1, ST2, ST3, ST4, ST5, ST6, ST7, ST8, ST9, ST10, ST11, ST12, ST13, ST14, ST15,
    A2, A3, A5, A6, A7, A44, A46, A47, A48,
    PF1, PF2, PF3, PF4, PF5, PF6, PF7, PF8, PF9,
    E1, E2, E3, E4, E5, E6, E7, E8, E9, E10, E11, E12, E13, E14, E15, E16, E17, E18, E19, E20,
    E21, E22, E23, E24, E25, E26, E27, E28, E29, E30, E31
)
SELECT 
    sez2011::bigint, 
    CASE 
        WHEN ST_GeometryType(geometry) = 'ST_Polygon' THEN ST_Multi(geometry)
        ELSE geometry
    END,
    shape_area::float, codreg, regione, codpro, provincia, codcom, comune, procom, nsez, ace, codloc, codasc,
    NULLIF(p1,'')::integer, NULLIF(p2,'')::integer, NULLIF(p3,'')::integer, NULLIF(p4,'')::integer, NULLIF(p5,'')::integer,
    NULLIF(p6,'')::integer, NULLIF(p7,'')::integer, NULLIF(p8,'')::integer, NULLIF(p9,'')::integer, NULLIF(p10,'')::integer,
    NULLIF(p11,'')::integer, NULLIF(p12,'')::integer, NULLIF(p13,'')::integer, NULLIF(p14,'')::integer, NULLIF(p15,'')::integer,
    NULLIF(p16,'')::integer, NULLIF(p17,'')::integer, NULLIF(p18,'')::integer, NULLIF(p19,'')::integer, NULLIF(p20,'')::integer,
    NULLIF(p21,'')::integer, NULLIF(p22,'')::integer, NULLIF(p23,'')::integer, NULLIF(p24,'')::integer, NULLIF(p25,'')::integer,
    NULLIF(p26,'')::integer, NULLIF(p27,'')::integer, NULLIF(p28,'')::integer, NULLIF(p29,'')::integer, NULLIF(p30,'')::integer,
    NULLIF(p31,'')::integer, NULLIF(p32,'')::integer, NULLIF(p33,'')::integer, NULLIF(p34,'')::integer, NULLIF(p35,'')::integer,
    NULLIF(p36,'')::integer, NULLIF(p37,'')::integer, NULLIF(p38,'')::integer, NULLIF(p39,'')::integer, NULLIF(p40,'')::integer,
    NULLIF(p41,'')::integer, NULLIF(p42,'')::integer, NULLIF(p43,'')::integer, NULLIF(p44,'')::integer, NULLIF(p45,'')::integer,
    NULLIF(p46,'')::integer, NULLIF(p47,'')::integer, NULLIF(p48,'')::integer, NULLIF(p49,'')::integer, NULLIF(p50,'')::integer,
    NULLIF(p51,'')::integer, NULLIF(p52,'')::integer, NULLIF(p53,'')::integer, NULLIF(p54,'')::integer, NULLIF(p55,'')::integer,
    NULLIF(p56,'')::integer, NULLIF(p57,'')::integer, NULLIF(p58,'')::integer, NULLIF(p59,'')::integer, NULLIF(p60,'')::integer,
    NULLIF(p61,'')::integer, NULLIF(p62,'')::integer, NULLIF(p64,'')::integer, NULLIF(p65,'')::integer, NULLIF(p66,'')::integer,
    NULLIF(p128,'')::integer, NULLIF(p129,'')::integer, NULLIF(p130,'')::integer, NULLIF(p131,'')::integer, NULLIF(p132,'')::integer,
    NULLIF(p135,'')::integer, NULLIF(p136,'')::integer, NULLIF(p137,'')::integer, NULLIF(p138,'')::integer, NULLIF(p139,'')::integer, NULLIF(p140,'')::integer,
    NULLIF(st1,'')::integer, NULLIF(st2,'')::integer, NULLIF(st3,'')::integer, NULLIF(st4,'')::integer, NULLIF(st5,'')::integer,
    NULLIF(st6,'')::integer, NULLIF(st7,'')::integer, NULLIF(st8,'')::integer, NULLIF(st9,'')::integer, NULLIF(st10,'')::integer,
    NULLIF(st11,'')::integer, NULLIF(st12,'')::integer, NULLIF(st13,'')::integer, NULLIF(st14,'')::integer, NULLIF(st15,'')::integer,
    NULLIF(a2,'')::integer, NULLIF(a3,'')::integer, NULLIF(a5,'')::integer, NULLIF(a6,'')::integer, NULLIF(a7,'')::integer,
    NULLIF(a44,'')::integer, NULLIF(a46,'')::integer, NULLIF(a47,'')::integer, NULLIF(a48,'')::integer,
    NULLIF(pf1,'')::integer, NULLIF(pf2,'')::integer, NULLIF(pf3,'')::integer, NULLIF(pf4,'')::integer, NULLIF(pf5,'')::integer,
    NULLIF(pf6,'')::integer, NULLIF(pf7,'')::integer, NULLIF(pf8,'')::integer, NULLIF(pf9,'')::integer,
    NULLIF(e1,'')::integer, NULLIF(e2,'')::integer, NULLIF(e3,'')::integer, NULLIF(e4,'')::integer, NULLIF(e5,'')::integer,
    NULLIF(e6,'')::integer, NULLIF(e7,'')::integer, NULLIF(e8,'')::integer, NULLIF(e9,'')::integer, NULLIF(e10,'')::integer,
    NULLIF(e11,'')::integer, NULLIF(e12,'')::integer, NULLIF(e13,'')::integer, NULLIF(e14,'')::integer, NULLIF(e15,'')::integer,
    NULLIF(e16,'')::integer, NULLIF(e17,'')::integer, NULLIF(e18,'')::integer, NULLIF(e19,'')::integer, NULLIF(e20,'')::integer,
    NULLIF(e21,'')::integer, NULLIF(e22,'')::integer, NULLIF(e23,'')::integer, NULLIF(e24,'')::integer, NULLIF(e25,'')::integer,
    NULLIF(e26,'')::integer, NULLIF(e27,'')::integer, NULLIF(e28,'')::integer, NULLIF(e29,'')::integer, NULLIF(e30,'')::integer, NULLIF(e31,'')::integer
FROM cim_census.census_geo_temp
ON CONFLICT (SEZ2011) DO NOTHING;

-- Clean up temp table
DROP TABLE IF EXISTS cim_census.census_geo_temp;
"

# Create spatial indexes
psql -c "
CREATE INDEX IF NOT EXISTS idx_census_geo_geometry ON cim_census.census_geo USING GIST(geometry);
CREATE INDEX IF NOT EXISTS idx_census_geo_sez2011 ON cim_census.census_geo(SEZ2011);
CREATE INDEX IF NOT EXISTS idx_census_geo_comune ON cim_census.census_geo(COMUNE);
"

# Verify data loading
echo "Verifying census data loading..."
psql -c "
SELECT 'Census data loaded successfully' as status;
SELECT 'Loaded ' || COUNT(*) || ' census records' as census_count FROM cim_census.census_geo;
SELECT 'Sample data - First 3 records:' as info;
SELECT SEZ2011, COMUNE, P1 as total_population FROM cim_census.census_geo LIMIT 3;
"

echo "Census data loading completed!"
