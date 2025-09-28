#!/usr/bin/env python3
"""
AWS Elastic Beanstalk entry point for cognitive-core
Multi-Agent Web Research System - FastAPI with Uvicorn
"""
import os
import logging
import uvicorn
from app import app

# Expose the FastAPI app for WSGI/ASGI servers
# This is the app that Elastic Beanstalk will import
application = app

# Setup logging for production
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Ensure we're using the correct environment
os.environ['FASTAPI_ENV'] = 'production'

if __name__ == "__main__":
    # Production server configuration
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    
    logger.info(f"Starting cognitive-core FastAPI application on {host}:{port}")
    logger.info(f"Environment: {os.environ.get('FASTAPI_ENV', 'development')}")
    
    # Run with Uvicorn for FastAPI
    uvicorn.run(
        "app:app",
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        workers=1  # EB manages scaling with multiple instances
    )
