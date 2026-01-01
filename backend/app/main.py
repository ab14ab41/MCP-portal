"""
FastAPI main application entry point.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

# Set log level for specific loggers
logger = logging.getLogger(__name__)
logger.info(f"Log level set to: {settings.log_level.upper()}")

# Initialize FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await init_db()

    # Reload all deployed MCP servers
    print("Loading deployed MCP servers...")
    try:
        from app.services.mcp_serving import mcp_serving_service
        from app.database import AsyncSessionLocal
        async with AsyncSessionLocal() as db:
            await mcp_serving_service.reload_deployed_servers_from_db(db)
        print(f"Active MCP servers: {len(mcp_serving_service.active_servers)}")
    except Exception as e:
        print(f"Error loading MCP servers: {e}")
        import traceback
        traceback.print_exc()

    print(f"{settings.app_name} v{settings.app_version} started")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print(f"{settings.app_name} shutting down")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "MCP Portal API",
        "version": settings.app_version,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Import and include routers
from app.api.v1.router import api_router
app.include_router(api_router, prefix=settings.api_v1_prefix)
