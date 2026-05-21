// Runs automatically when the container first initializes
// Sets up the datalake DB with geospatial indexes

db = db.getSiblingDB("datalake");

// ── datasources collection ─────────────────────────────────
db.createCollection("datasources");
db.datasources.createIndex({ name: 1 });
db.datasources.createIndex({ data_type: 1 });
db.datasources.createIndex({ is_geo: 1 });

// ── geodata collection ─────────────────────────────────────
db.createCollection("geodata");

// 2dsphere index — enables all geospatial queries ($near, $geoWithin etc.)
db.geodata.createIndex({ "geometry": "2dsphere" });
db.geodata.createIndex({ "datasource_id": 1 });

print("DataLake4Raw: collections and geo indexes created");