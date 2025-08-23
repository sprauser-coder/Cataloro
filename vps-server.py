#!/usr/bin/env python3
"""
VPS-specific server entry point for Cataloro marketplace
This file is used by PM2 on the production VPS deployment
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

# Change working directory to backend
os.chdir(backend_dir)

# Import the FastAPI app from the backend server
from server import app

if __name__ == "__main__":
    # Get port from environment or default to 8001
    port = int(os.environ.get("PORT", 8001))
    
    # Run the server
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        workers=1,
        log_level="info"
    )