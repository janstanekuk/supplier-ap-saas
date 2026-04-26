from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .config import settings
from .database import init_db, engine
from .middleware.auth import verify_org_access
from .routers import auth, suppliers, invoices

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

# Create app ONCE with lifespan
app = FastAPI(
    title="Supplier AP Contract Manager API",
    description="Multi-tenant SaaS for invoice & VAT management",
    version="0.1.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware ONCE
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Auth middleware
@app.middleware("http")
async def check_auth(request: Request, call_next):
    # Skip auth for OPTIONS requests (CORS preflight)
    if request.method == "OPTIONS":
        return await call_next(request)
    
    # Skip auth for public endpoints
    if request.url.path.startswith("/api/v1/auth"):
        return await call_next(request)
    
    # Skip auth for docs
    if request.url.path in ["/docs", "/openapi.json", "/", "/health"]:
        return await call_next(request)
    
    # All other /api/v1 routes require auth
    if request.url.path.startswith("/api/v1"):
        await verify_org_access(request)
    
    return await call_next(request)

# Health check endpoints
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

# Register routers
app.include_router(auth.router)
app.include_router(suppliers.router)
app.include_router(invoices.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )