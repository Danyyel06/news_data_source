# database/db_connector.py

import psycopg2.extras
import psycopg2
from configparser import ConfigParser
# Note: We use relative import for models.py
from .models import CREATE_TABLE_QUERY, INSERT_ARTICLE_QUERY
import os

# Helper function to read database config
# database/db_connector.py

# ... ensure 'import os' is at the top of the file
# ... ensure 'from configparser import ConfigParser' is at the top of the file

def config(filename='config/database.ini', section='postgresql'):
    """
    Reads database configuration, prioritizing environment variables 
    (set on PythonAnywhere) over the local INI file.
    """
    db = {}

    # --- 1. PRIORITY: Check Environment Variables (For Deployment) ---
    # This checks for the variables you set on the PythonAnywhere Tasks page.
    if os.environ.get('DB_HOST'):
        db['host'] = os.environ.get('DB_HOST')
        db['database'] = os.environ.get('DB_NAME')
        db['user'] = os.environ.get('DB_USER')
        db['password'] = os.environ.get('DB_PASSWORD')
        # Check for port, default to 5432 if not explicitly set
        db['port'] = os.environ.get('DB_PORT', '5432') 
        return db

    # --- 2. FALLBACK: Read from local INI file (For Local Development) ---
    else:
        # (This is the original logic you had to read the local INI file)
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, '..', filename)

        parser = ConfigParser()
        parser.read(config_path)

        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                db[param[0]] = param[1]
            return db
        else:
            # Raise exception if neither environment variables nor the config file works
            raise Exception(f'Database config not found. Set env vars or check {filename}.')


def connect():
    """ Connects to the PostgreSQL server and ensures the table exists. """
    conn = None
    try:
        params = config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        # Execute table creation query
        cur.execute(CREATE_TABLE_QUERY)
        conn.commit()
        cur.close()
        return conn
    except (Exception, psycopg2.Error) as error:
        print(f"Error connecting to or initializing PostgreSQL: {error}")
        return None

def insert_article(conn, data):
    """ Inserts a single news article, preventing duplicates based on URL. """
    if conn is None:
        return

    title, url, date, content, category = data
    try:
        cur = conn.cursor()
        cur.execute(INSERT_ARTICLE_QUERY, (title, url, date, content, category))
        conn.commit()
        if cur.rowcount == 1:
            print(f"Successfully inserted: {title}")
        else:
            print(f"Skipped duplicate (URL exists): {title}")
        cur.close()
    except (Exception, psycopg2.Error) as error:
        print(f"Error during insert: {error}")
        conn.rollback()

def fetch_latest_news(conn, limit: int, category_filter=None):
    """Fetches the latest news articles, optionally filtered by category."""
    if conn is None:
        return []
    
    cursor = None
    results = []
    
    try:
        # Use DictCursor to return results as dictionaries (easier for FastAPI/Pydantic)
        cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
        
        # Build the query dynamically
        query = "SELECT id, title, source_url, publication_date, content, source_category, created_at FROM news_article"
        params = [limit]

        if category_filter:
            query += " WHERE source_category LIKE %s"
            # Use LIKE to match categories like 'Social-X' or 'External-GoogleNews'
            params.insert(0, f'{category_filter}%')

        query += " ORDER BY publication_date DESC LIMIT %s"

        cursor.execute(query, params)
        
        # Fetch results and map them to a list of dictionaries
        for row in cursor.fetchall():
            # Convert DictRow to standard dictionary for Pydantic compatibility
            results.append(dict(row)) 
            
    except (Exception, psycopg2.Error) as error:
        print(f"Error fetching news: {error}")
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
        print("FAILURE: Could not connect. Check credentials in config/database.ini and ensure PostgreSQL is running.")