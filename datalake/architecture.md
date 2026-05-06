i want to create a local (not bigdata cluster) datalake for our company to let everyone share their datasets

postgis + fastapi
Database Reflection -> Automating SQLAlchemy


SQLAlchemy can inspect the database schema at runtime and automatically generate objects to interact with it. there are two main ways to do this:

Option A: Using SQLAlchemy Core (Recommended for highly dynamic data)
Instead of relying on ORM classes, map the table metadata directly. This is generally safer and more performant for dynamic structures.

from sqlalchemy import create_engine, MetaData, Table, select

engine = create_engine("postgresql://user:pass@localhost/postgis_db")

def get_dynamic_table(schema_name: str, table_name: str):
    # Bind metadata to the specific schema
    metadata = MetaData(schema=schema_name)
    
    # Reflect only the specific table from the database
    table = Table(table_name, metadata, autoload_with=engine)
    return table

# Usage in a FastAPI route:
# dynamic_table = get_dynamic_table("user_schema_1", "custom_points")
# query = select(dynamic_table).where(dynamic_table.c.id == 1)

Option B: Using Automap (If you strictly want ORM Classes)
If you prefer working with ORM objects instead of Core tables, SQLAlchemy provides automap_base.
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

engine = create_engine("postgresql://user:pass@localhost/postgis_db")

def get_dynamic_orm_class(schema_name: str, table_name: str):
    Base = automap_base()
    
    # Reflect the schema
    Base.prepare(autoload_with=engine, schema=schema_name)
    
    # Get the automatically generated Python class
    # Note: the table MUST have a primary key for automap to work
    return getattr(Base.classes, table_name)

FastAPI relies on Pydantic models to validate incoming JSON requests and format outgoing responses.
The Simple Way: Accept and Return Dictionaries
Bypass strict Pydantic validation and let FastAPI accept raw JSON.
from fastapi import APIRouter, Body
from typing import Dict, Any

@app.post("/api/{schema_name}/{table_name}")
async def insert_data(
    schema_name: str, 
    table_name: str, 
    payload: Dict[str, Any] = Body(...)
):
    # payload is a normal dictionary. 
    # Pass this directly to your SQLAlchemy Core insert statement.
    pass

The Advanced Way: Dynamic Pydantic Models
You can use Pydantic's create_model function to generate validation schemas on the fly by reading the SQLAlchemy column types, but this is complex and adds overhead to your API requests. For most dynamic table use-cases, accepting Dict[str, Any] is the standard approach.



The Single Collection Architecture (The MongoDB Way)
put all spatial data into one giant collection and use a dataset_id to separate them.
// One giant collection called "spatial_features"
{
  "_id": "...",
  "dataset_id": "user_123_custom_points", 
  "geometry": { "type": "Point", "coordinates": [ -73.97, 40.77 ] },
  "properties": { "custom_field": "anything", "color": "blue" }
}

Feature / Requirement,PostGIS (Relational Spatial),MongoDB (NoSQL Document),MinIO + pgSTAC (Data Lake)
Where does the data live?,Geometries and attributes are stored as rows in database tables.,GeoJSON and attributes are stored as JSON documents in collections.,"Raw files (GeoTIFF, CSV, Shapefile) sit in MinIO; STAC JSON metadata sits in pgSTAC."
Handling Dynamic Schemas (User uploads random forms),Difficult. Requires dynamically creating tables or stuffing everything into a single JSONB column.,Excellent. Schemaless by design. Users can insert whatever JSON structure they want instantly.,Excellent. MinIO accepts any file type. You map the core info to a standard STAC JSON format for the database.
"Spatial Joins (e.g., intersecting User A's points with User B's polygons)",Excellent. Native support via ST_Intersects and JOIN. Handles massive datasets efficiently.,Poor. Cannot perform spatial operators across different collections in a single $lookup query.,"Varies. pgSTAC can easily intersect metadata bounding boxes, but intersecting actual features inside the files requires a background processing worker."
"Handling Massive Files (Rasters, Point Clouds, Heavy Vectors)",Poor. Storing large binary files or massive multipolygons in a relational DB causes bloat and slows down backups.,Poor. Hard limit of 16MB per document. GridFS is clunky for geospatial data.,Excellent. Cloud-native object storage is explicitly designed for massive files. It is infinitely scalable and cheap.
Standardized Ecosystem,"Very high. Standard SQL and widely supported by all GIS tools (QGIS, GeoServer).",Low. Most GIS tools require custom connectors or middleware to read MongoDB spatial data natively.,"Very high. STAC is the modern industry standard. Massive open-source ecosystem (pystac, stac-fastapi, QGIS plugins)."
Best Used For...,"Heavy vector-math, routing (pgRouting), complex spatial relationships, and highly structured transactional data.","Highly dynamic user forms, simple point-based apps, and apps where JSON flexibility is prioritized over complex spatial math.","Managing massive libraries of imagery, user-uploaded files, drone surveys, and creating a scalable search engine for diverse datasets."