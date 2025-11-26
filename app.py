from fastapi import FastAPI, Header, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import os
from scheduler import run_all_collectors
from typing import Optional

app = FastAPI(
    title="Financial News Scraper API",
    description="API for triggering regulatory news scraper",
    version="1.0.0"
)

# Secret token for authentication
SECRET_TOKEN = os.getenv('CRON_SECRET_TOKEN', 'your-secret-token-here')

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Financial News Scraper API is running!",
        "status": "healthy",
        "endpoints": {
            "trigger_scraper": "/run-scraper?token=YOUR_TOKEN",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for Render"""
    return {"status": "healthy", "service": "news-scraper"}

@app.post("/run-scraper")
@app.get("/run-scraper")
async def trigger_scraper(
    background_tasks: BackgroundTasks,
    token: Optional[str] = None,
    x_cron_token: Optional[str] = Header(None)
):
    """
    Endpoint that cron-job.org will ping to trigger the scraper.
    
    Authentication via:
    - Query parameter: ?token=YOUR_SECRET_TOKEN
    - Header: X-Cron-Token: YOUR_SECRET_TOKEN
    """
    
    # Get token from query param or header
    provided_token = token or x_cron_token
    
    # Verify authentication
    if provided_token != SECRET_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid or missing authentication token"
        )
    
    try:
        # Run scraper in background to avoid timeout on cold start
        background_tasks.add_task(run_all_collectors)
        
        return {
            "status": "started",
            "message": "News scraper started successfully in background"
        }
        
    except Exception as e:
        print(f"Error starting scraper: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error starting scraper: {str(e)}"
        )

@app.post("/run-scraper-sync")
@app.get("/run-scraper-sync")
async def trigger_scraper_sync(
    token: Optional[str] = None,
    x_cron_token: Optional[str] = Header(None)
):
    """
    Synchronous version - waits for scraper to complete.
    Use this if you need to confirm completion before response.
    """
    
    provided_token = token or x_cron_token
    
    if provided_token != SECRET_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Invalid or missing authentication token"
        )
    
    try:
        print("Scraper triggered via web endpoint (synchronous)")
        run_all_collectors()
        
        return {
            "status": "success",
            "message": "News scraper completed successfully"
        }
        
    except Exception as e:
        print(f"Error running scraper: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error running scraper: {str(e)}"
        )

# Optional: Add a manual trigger endpoint (no auth needed for testing)
@app.get("/test")
async def test_endpoint():
    """Test endpoint to verify service is responding"""
    return {
        "status": "ok",
        "message": "Service is running",
        "note": "Use /run-scraper with valid token to trigger scraper"
    }