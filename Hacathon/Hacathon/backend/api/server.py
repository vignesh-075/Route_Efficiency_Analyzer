"""
FastAPI server for Jupiter Smart Swap backend API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from backend.api.routes import router

# Create FastAPI app
app = FastAPI(
    title="Jupiter Smart Swap API",
    description="Backend API for analyzing and executing token swaps via Jupiter",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware for web UI integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1", tags=["jupiter-swap"])

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Jupiter Smart Swap Backend API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
        "endpoints": {
            "analyze": "/api/v1/analyze",
            "auto_swap": "/api/v1/auto-swap", 
            "manual_swap": "/api/v1/manual-swap",
            "demo": "/api/v1/demo"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 