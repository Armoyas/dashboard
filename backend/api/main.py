"""
ZarrinPal Analytics Dashboard API
FastAPI backend for analytical dashboard
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import database connection for initialization
from api.database.connection import get_connection, close_connection

# Import routers
from api.routers import merchants, analytics, sessions

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown events"""
    logger.info("Starting ZarrinPal Analytics Dashboard API...")
    # Initialize database connection (loads CSV data on first connection)
    try:
        get_connection()
        logger.info("Database initialized and CSV data loaded successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    yield
    logger.info("Shutting down API...")
    # Close database connection
    close_connection()


app = FastAPI(
    title="ZarrinPal Analytics Dashboard API",
    description="Backend API for ZarrinPal payment analytics dashboard",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(merchants.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "zarrinpal-analytics-dashboard",
        "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "ZarrinPal Analytics Dashboard API", "version": "1.0.0"}