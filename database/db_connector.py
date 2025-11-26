# database/db_connector.py

import psycopg2.extras
import psycopg2
import os
from urllib.parse import urlparse
from .models import CREATE_TABLE_QUERY, INSERT_ARTICLE_QUERY

def connect():
    """Connects to PostgreSQL using DATABASE_URL environment variable."""
    conn = None
    try:
        # Get DATABASE_URL from environment (Render provides this)
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            print("ERROR: DATABASE_URL environment variable not set!")
            return None
        
        # Parse the DATABASE_URL
        result = urlparse(database_url)
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=result.hostname,
            port=result.port,
            user=result.username,
            password=result.password,
            database=result.path[1:]  # Remove leading '/'
        )
        
        print(f"✅ Connected to PostgreSQL database: {result.hostname}")
        
        # Create table if it doesn't exist
        cur = conn.cursor()
        cur.execute(CREATE_TABLE_QUERY)
        conn.commit()
        cur.close()
        
        print("✅ Table structure verified")
        return conn
        
    except (Exception, psycopg2.Error) as error:
        print(f"❌ Error connecting to PostgreSQL: {error}")
        return None

def insert_article(conn, data):
    """Inserts a single news article, preventing duplicates based on URL."""
    if conn is None:
        return

    title, url, date, content, category = data
    try:
        cur = conn.cursor()
        cur.execute(INSERT_ARTICLE_QUERY, (title, url, date, content, category))
        conn.commit()
        if cur.rowcount == 1:
            print(f"✅ Successfully inserted: {title}")
        else:
            print(f"⏭️  Skipped duplicate (URL exists): {title}")
        cur.close()
    except (Exception, psycopg2.Error) as error:
        print(f"❌ Error during insert: {error}")
        conn.rollback()

def fetch_latest_news(conn, limit: int = 20, category_filter=None):
    """Fetches the latest news articles, optionally filtered by category."""
    if conn is None:
        print("ERROR: No database connection provided to fetch_latest_news")
        return []
    
    cursor = None
    results = []
    
    try:
        # Use DictCursor to return results as dictionaries
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
        
        # Build the query dynamically
        query = "SELECT id, title, source_url, publication_date, content, source_category, created_at FROM news_article"
        params = []

        if category_filter:
            query += " WHERE source_category LIKE %s"
            params.append(f'{category_filter}%')

        query += " ORDER BY publication_date DESC LIMIT %s"
        params.append(limit)

        cursor.execute(query, params)
        
        # Fetch results and convert to list of dictionaries
        for row in cursor.fetchall():
            results.append(dict(row))
        
        print(f"📰 Fetched {len(results)} articles from database")
            
    except (Exception, psycopg2.Error) as error:
        print(f"❌ Error fetching news: {error}")
    finally:
        if cursor:
            cursor.close()
    
    return results


def fetch_news_by_date_range(conn, start_date, limit: int = 50):
    """Fetches news articles from a specific date range."""
    if conn is None:
        print("ERROR: No database connection provided")
        return []
    
    cursor = None
    results = []
    
    try:
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
        
        query = """
            SELECT id, title, source_url, publication_date, content, source_category, created_at 
            FROM news_article
            WHERE publication_date >= %s
            ORDER BY publication_date DESC 
            LIMIT %s
        """
        
        cursor.execute(query, (start_date, limit))
        
        for row in cursor.fetchall():
            results.append(dict(row))
        
        print(f"📰 Fetched {len(results)} articles from {start_date.strftime('%Y-%m-%d')} onwards")
            
    except (Exception, psycopg2.Error) as error:
        print(f"❌ Error fetching news: {error}")
    finally:
        if cursor:
            cursor.close()
    
    return results


if __name__ == '__main__':
    # --- Verification Step ---
    print("Attempting to connect and create table...")
    test_conn = connect()
    if test_conn:
        print("SUCCESS: Connection established and table structure verified.")
        test_conn.close()
    else:
        print("FAILURE: Could not connect. Check DATABASE_URL environment variable.")