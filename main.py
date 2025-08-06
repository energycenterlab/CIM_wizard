"""
CIM Wizard Integrated - FastAPI Application
Integrated service combining vector, census, and raster services with direct database access
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import vector_routes, pipeline_routes, census_routes, raster_routes
from app.db.database import engine, Base
from app.db.database import create_all_schemas


# Create database schemas on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Creating database schemas...")
    create_all_schemas()
    Base.metadata.create_all(bind=engine)
    print("Database schemas created successfully")
    yield
    # Shutdown
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="CIM Wizard Integrated",
    description="Integrated FastAPI service with vector, census, and raster capabilities",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    vector_routes.router,
    prefix="/api/vector",
    tags=["Vector Data"]
)

app.include_router(
    pipeline_routes.router,
    prefix="/api/pipeline",
    tags=["Pipeline Execution"]
)

app.include_router(
    census_routes.router,
    prefix="/api/census",
    tags=["Census Data"]
)

app.include_router(
    raster_routes.router,
    prefix="/api/raster",
    tags=["Raster Data"]
)


@app.get("/")
async def root():
    return {
        "message": "Welcome to CIM Wizard Integrated API",
        "version": "2.0.0",
        "services": {
            "vector_data": "/api/vector",
            "pipeline_execution": "/api/pipeline",
            "census_data": "/api/census",
            "raster_data": "/api/raster"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "services": {
            "vector": "operational",
            "pipeline": "operational", 
            "census": "operational",
            "raster": "operational"
        }
    }