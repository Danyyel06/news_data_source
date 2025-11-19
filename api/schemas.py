# api/schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional # Use Optional for fields that might be null

class NewsArticle(BaseModel):
    """Defines the structure of a news article returned by the API."""
    
    # These fields must match the columns in your 'news_article' table
    id: Optional[int] = None
    title: str
    source_url: str
    publication_date: Optional[datetime] = None
    content: Optional[str] = None
    source_category: str
    created_at: Optional[datetime] = None

    class Config:
        # Allows FastAPI to read data from database objects (ORM mode) 
        # which is useful when mapping database results (like DictCursor) to this model.
        from_attributes = True