"""
CIM Wizard Integrated - FastAPI Application
Integrated service combining vector, census, and raster services with direct database access
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import vector_routes, pipeline_routes, census_routes, raster_routes, complete_chain_route
from app.db.database import engine, Base
from app.db.database import create_all_schemas
from app.core.settings import settings


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
    title=settings.PROJECT_NAME,
    description="Integrated FastAPI service with vector, census, and raster capabilities",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs" if settings.DOCS_ENABLED else None,
    redoc_url="/redoc" if settings.DOCS_ENABLED else None,
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
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


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "services": {
            "vector_data": f"{settings.API_V1_STR}/vector",
            "pipeline_execution": f"{settings.API_V1_STR}/pipeline",
            "census_data": f"{settings.API_V1_STR}/census",
            "raster_data": f"{settings.API_V1_STR}/raster"
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        } if settings.DOCS_ENABLED else None
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