"""
Friends Finder API - Main Application

This is the entry point for the FastAPI application.
It sets up the app, middleware, routes, and startup events.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from datetime import datetime

from app.core.config import settings
from app.core.database import Base, engine
from app.api.v1.api import api_router

import os

# Create database tables on startup
Base.metadata.create_all(bind=engine)

# Initialize FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc documentation
)

# CORS Middleware - Allow frontend to communicate with API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Root endpoint
#@app.get("/", tags=["Root"])
#def root():
#    """
#    Root endpoint - Welcome message with API info.
#    """
#    return {
#        "message": "Welcome to Friends Finder API!",
#        "version": settings.VERSION,
#        "docs": "/docs",
#        "redoc": "/redoc",
#        "description": "Find friends based on shared interests and location"
#    }

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
static_path = os.path.join(BASE_DIR, "static")

app.mount("/static", StaticFiles(directory=static_path), name="static")

# Root endpoint
@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint - Welcome message with API info.
    """
    return FileResponse(os.path.join(static_path,"index.html"))

@app.get("/admin", tags=["Admin Panel"])
def admin_panel():
    return FileResponse(os.path.join(static_path, "admin.html"))

# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint - Returns API status.
    Useful for monitoring and container orchestration.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


# Include all API routes with /api/v1 prefix
app.include_router(api_router, prefix="/api/v1")


# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Runs when the application starts.
    You can add initialization logic here.
    """
    print("=" * 60)
    print(f"🚀 {settings.PROJECT_NAME} v{settings.VERSION} is starting...")
    print(f"📚 API Documentation: http://localhost:8000/docs")
    print(f"🔧 Database: {settings.DATABASE_URL}")
    print("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Runs when the application shuts down.
    You can add cleanup logic here.
    """
    print(f"👋 {settings.PROJECT_NAME} is shutting down...")


# Optional: Custom exception handlers for better error messages
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Custom handler for HTTP exceptions.
    Returns a consistent JSON error format.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for validation errors.
    Returns detailed error information in a JSON-serializable format.
    """
    def sanitize_error(obj):
        if isinstance(obj, (str, int, float, bool, type(None))):
            return obj
        if isinstance(obj, list):
            return [sanitize_error(v) for v in obj]
        if isinstance(obj, dict):
            return {k: sanitize_error(v) for k, v in obj.items()}
        if isinstance(obj, bytes):
            return obj.decode('utf-8', errors='replace')
        return str(obj)

    errors = [sanitize_error(error) for error in exc.errors()]
    
    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "message": "Validation error",
            "details": errors
        }
    )


# Run with: uvicorn app.main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes
    )
