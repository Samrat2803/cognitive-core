"""
Application entry point for AWS Elastic Beanstalk / production deployment
This file is required by Procfile to find the FastAPI app instance
"""

from app import app

# Expose app as 'application' for AWS EB / Gunicorn
application = app

if __name__ == "__main__":
    import uvicorn
    import os
    
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "application:application",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

