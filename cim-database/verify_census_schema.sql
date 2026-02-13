-- Verification queries for cim_census.censusgeo schema
-- Run these in pgAdmin or using: docker exec -it cim-integrateddb psql -U cim_wizard_user -d cim_wizard_integrated -f verify_census_schema.sql

-- 1. Check all column names and data types
SELECT 
    column_name, 
    data_type,
    udt_name,
    is_nullable,
    column_default
FROM information_schema.columns 
WHERE table_schema = 'cim_census' 
  AND table_name = 'censusgeo'
ORDER BY ordinal_position;

-- 2. Verify data counts for key columns
SELECT 
    COUNT(*) as total_rows,
    COUNT("SEZ2011") as sez2011_count,
    COUNT(geometry) as geometry_count,
    COUNT("P1") as p1_total_population,
    COUNT("E8") as e8_buildings_pre1918,
    COUNT("E12") as e12_buildings_1971_1980,
    COUNT("E16") as e16_buildings_post2005,
    COUNT("ST1") as st1_housing_units,
    COUNT("A2") as a2_building_attr,
    COUNT("PF1") as pf1_families
FROM cim_census.censusgeo;

-- 3. Sample data to verify population
SELECT 
    "SEZ2011",
    "COMUNE",
    "REGIONE",
    "P1" as total_population,
    "P2" as male,
    "P3" as female,
    "E8" as buildings_pre1918,
    "E12" as buildings_1971_1980,
    "E16" as buildings_post2005
FROM cim_census.censusgeo
WHERE "P1" > 0
ORDER BY "P1" DESC
LIMIT 10;

-- 4. Check geometry validity
SELECT 
    COUNT(*) as total_geoms,
    COUNT(CASE WHEN ST_IsValid(geometry) THEN 1 END) as valid_geoms,
    COUNT(CASE WHEN NOT ST_IsValid(geometry) THEN 1 END) as invalid_geoms,
    ST_SRID(geometry) as srid
FROM cim_census.censusgeo
GROUP BY ST_SRID(geometry);

-- 5. Administrative hierarchy check
SELECT DISTINCT 
    "REGIONE",
    COUNT(DISTINCT "PROVINCIA") as province_count,
    COUNT(DISTINCT "COMUNE") as comune_count,
    COUNT(*) as census_sections
FROM cim_census.censusgeo
GROUP BY "REGIONE"
ORDER BY census_sections DESC
LIMIT 10;

