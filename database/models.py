# database/models.py

TABLE_NAME = "news_article"

# Defines the SQL command to create the table
CREATE_TABLE_QUERY = f"""
CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    source_url TEXT UNIQUE NOT NULL,  -- UNIQUE constraint is critical for de-duplication
    publication_date TIMESTAMP,
    content TEXT,
    source_category TEXT NOT NULL,    -- E.g., 'Social-X', 'External-GoogleNews'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Defines the SQL command to insert data, skipping if the URL already exists
INSERT_ARTICLE_QUERY = f"""
INSERT INTO {TABLE_NAME} (title, source_url, publication_date, content, source_category)
VALUES (%s, %s, %s, %s, %s)
ON CONFLICT (source_url) DO NOTHING;
"""