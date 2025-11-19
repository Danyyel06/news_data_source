# api/news_routes.py

from fastapi import FastAPI, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime

# Import database functions and schema model
import sys, os
# Adjust path to import from the 'database' folder in the project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db_connector import connect, fetch_latest_news 
from .schemas import NewsArticle 

# --- FastAPI App Setup ---
app = FastAPI(
    title="Regulatory News Aggregation API",
    description="Provides filtered and aggregated financial regulatory news.",
    version="1.0.0"
)

# Dependency to handle DB connection/closure per request
def get_db_connection():
    """Connects to the database and ensures the connection is closed."""
    conn = connect()
    if conn is None:
        raise HTTPException(status_code=503, detail="Database service unavailable. Check config.")
    try:
        yield conn
    finally:
        if conn:
            conn.close()

# --- Endpoint 1: Get all latest news (Unfiltered) ---
@app.get("/api/news", response_model=List[NewsArticle]) 
def get_latest_news(
    conn = Depends(get_db_connection),
    limit: int = Query(20, description="Number of articles to return (max 100)")
):
    """Retrieves the latest collected news articles (Default: 20)."""
    # Fetch results using the function you added to db_connector
    return fetch_latest_news(conn, min(limit, 100)) # Limit to 100 to prevent overload

# --- Endpoint 2: Filter by Social Sources (X/Twitter) ---
@app.get("/api/news/social", response_model=List[NewsArticle])
def get_social_news(
    conn = Depends(get_db_connection),
    limit: int = Query(20, description="Number of social media articles to return (max 100)")
):
    """Retrieves the latest news from social media sources (X/Twitter)."""
    return fetch_latest_news(conn, min(limit, 100), category_filter="Social")


# --- Endpoint 3: Filter by External Sources (Google News) ---
@app.get("/api/news/external", response_model=List[NewsArticle])
def get_external_news(
    conn = Depends(get_db_connection),
    limit: int = Query(20, description="Number of external/aggregator articles to return (max 100)")
):
    """Retrieves the latest news from external aggregators (Google News)."""
    return fetch_latest_news(conn, min(limit, 100), category_filter="External")