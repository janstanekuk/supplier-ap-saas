from .routers import auth
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .middleware.auth import verify_org_access
import logging

from .config import settings
from .database import init_db, engine

logging.basicConfig(level=logging.INFO if not settings.debug else logging.DEBUG)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Supplier AP SaaS API")
    try:
        await init_db()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down API server")
    await engine.dispose()

app = FastAPI(
    title="Supplier AP Contract Manager API",
    description="Multi-tenant SaaS for invoice & VAT management",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Supplier AP Contract Manager API",
        "version": "0.1.0",
        "environment": settings.environment,
        "docs": "/docs",
        "health": "/health"
    }
# This will run for all protected routes
@app.middleware("http")
async def check_auth(request: Request, call_next):
    # Skip auth for public endpoints
    if request.url.path.startswith("/api/v1/auth"):
        return await call_next(request)
    
    # All other /api/v1 routes require auth
    if request.url.path.startswith("/api/v1"):
        await verify_org_access(request)
    
    return await call_next(request)

app.include_router(auth.router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "environment": settings.environment
    }

@app.get("/api/v1/health")
async def api_health():
    """API health endpoint"""
    return {
        "status": "healthy",
        "message": "API is running",
        "version": "0.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )