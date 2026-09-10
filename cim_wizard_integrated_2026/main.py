"""
CIM Wizard Integrated - FastAPI Application
Integrated service combining vector, census, and raster services with direct database access
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from app.api import vector_routes, pipeline_routes, census_routes, raster_routes, complete_chain_route, building_analysis_route, network_routes, cim_wizard_views, citydb_route, jobs_route
from app.models import jobs as _jobs_model  # noqa: F401 — register Job on Base.metadata
from app.db.database import engine, Base
from app.db.database import create_all_schemas
from app.core.settings import settings
from app.core.config_sync import run_config_sync


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup -- schema creation
    print("Creating database schemas...")
    create_all_schemas()
    Base.metadata.create_all(bind=engine)
    print("Database schemas created successfully")

    # Config-driven sync: add missing DB columns, update normalizer
    print("Running configuration sync...")
    sync_result = run_config_sync(engine)
    if sync_result["db_columns_created"]:
        print(f"  New DB columns: {sync_result['db_columns_created']}")
    if sync_result["normalizer_fields_added"]:
        print(f"  Normalizer fields added: {sync_result['normalizer_fields_added']}")
    print(f"  Features registered: {sync_result['feature_count']}")
    print("Configuration sync complete")

    yield
    # Shutdown
    print("Shutting down...")


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Integrated FastAPI service with vector, census, and raster capabilities",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DOCS_ENABLED else None,
    redoc_url="/redoc" if settings.DOCS_ENABLED else None,
    debug=settings.DEBUG
)

# Configure CORS
# If BACKEND_CORS_ORIGINS contains "*", we can't use credentials
# So we'll handle both cases
cors_origins = settings.BACKEND_CORS_ORIGINS
cors_credentials = True

# If wildcard is used, disable credentials (required by CORS spec)
if "*" in cors_origins:
    cors_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=cors_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    vector_routes.router,
    prefix=f"{settings.API_V1_STR}/vector",
    tags=["Vector Data"]
)

app.include_router(
    pipeline_routes.router,
    prefix=f"{settings.API_V1_STR}/pipeline",
    tags=["Pipeline Execution"]
)

app.include_router(
    census_routes.router,
    prefix=f"{settings.API_V1_STR}/census",
    tags=["Census Data"]
)

app.include_router(
    raster_routes.router,
    prefix=f"{settings.API_V1_STR}/raster",
    tags=["Raster Data"]
)

app.include_router(
    complete_chain_route.router,
    prefix=f"{settings.API_V1_STR}/complete",
    tags=["Complete Chain Execution"]
)

app.include_router(
    building_analysis_route.router,
    prefix=f"{settings.API_V1_STR}/building",
    tags=["Building Analysis"]
)

app.include_router(
    network_routes.router,
    prefix=f"{settings.API_V1_STR}/network",
    tags=["Network Data"]
)

app.include_router(
    cim_wizard_views.router,
    prefix=f"{settings.API_V1_STR}/cim-wizard",
    tags=["CIM Wizard Views"]
)

app.include_router(
    citydb_route.router,
    prefix=f"{settings.API_V1_STR}/citydb",
    tags=["3DCityDB"]
)

app.include_router(
    jobs_route.router,
    prefix=f"{settings.API_V1_STR}/jobs",
    tags=["Jobs"]
)


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "services": {
            "vector_data": f"{settings.API_V1_STR}/vector",
            "pipeline_execution": f"{settings.API_V1_STR}/pipeline",
            "census_data": f"{settings.API_V1_STR}/census",
            "raster_data": f"{settings.API_V1_STR}/raster",
            "complete_chain": f"{settings.API_V1_STR}/complete",
            "building_analysis": f"{settings.API_V1_STR}/building",
            "network_data": f"{settings.API_V1_STR}/network",
            "cim_wizard": f"{settings.API_V1_STR}/cim-wizard",
            "citydb": f"{settings.API_V1_STR}/citydb",
            "jobs": f"{settings.API_V1_STR}/jobs",
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        } if settings.DOCS_ENABLED else None
    }


@app.get("/health")
async def health():
    redis_status = "not_configured"
    broker = os.getenv("CELERY_BROKER_URL")
    if broker:
        try:
            import redis as redis_lib
            redis_lib.from_url(broker, socket_connect_timeout=1).ping()
            redis_status = "operational"
        except Exception:
            redis_status = "unavailable"
    return {
        "status": "healthy",
        "services": {
            "vector": "operational",
            "pipeline": "operational",
            "census": "operational",
            "raster": "operational",
            "network": "operational",
            "redis": redis_status,
        }
    }