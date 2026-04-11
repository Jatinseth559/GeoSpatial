from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import settings
from core.database import init_db
from api.routes import score, layers, clusters, accessibility, compare, export, enhanced_score
from api.websocket import websocket_endpoint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up GeoSpatial Site Readiness Analyzer...")
    try:
        await init_db()
        logger.info("Database initialized with PostGIS")
    except Exception as e:
        logger.warning(f"Could not initialize database: {e}")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="GeoSpatial Site Readiness Analyzer",
    description="AI-powered location intelligence platform for commercial real estate and infrastructure site selection",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(score.router)
app.include_router(enhanced_score.router)
app.include_router(layers.router)
app.include_router(clusters.router)
app.include_router(accessibility.router)
app.include_router(compare.router)
app.include_router(export.router)

app.add_api_websocket_route("/ws/realtime", websocket_endpoint)


@app.get("/")
async def root():
    return {
        "name": "GeoSpatial Site Readiness Analyzer",
        "version": "1.0.0",
        "docs": "/docs",
        "study_area": {
            "name": "Ahmedabad, Gujarat, India",
            "bbox": settings.STUDY_AREA_BBOX
        }
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint."""
    from core.database import comprehensive_health_check
    
    try:
        health_status = await comprehensive_health_check()
        
        if health_status['overall_healthy']:
            return {
                "status": "healthy",
                "service": "geo-site-analyzer",
                "details": health_status
            }
        else:
            return {
                "status": "degraded",
                "service": "geo-site-analyzer", 
                "details": health_status
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "geo-site-analyzer",
            "error": str(e)
        }