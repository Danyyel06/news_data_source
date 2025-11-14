# database/db_connector.py

import psycopg2
from configparser import ConfigParser
# Note: We use relative import for models.py
from .models import CREATE_TABLE_QUERY, INSERT_ARTICLE_QUERY
import os

# Helper function to read database config
def config(filename='config/database.ini', section='postgresql'):
    # Correct path for reading config from the main project root
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', filename)

    parser = ConfigParser()
    parser.read(config_path)

    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in the {filename} file')
    return db

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


if __name__ == '__main__':
    # --- Verification Step ---
    print("Attempting to connect and create table...")
    test_conn = connect()
    if test_conn:
        print("SUCCESS: Connection established and table structure verified.")
        test_conn.close()
    else:
        print("FAILURE: Could not connect. Check credentials in config/database.ini and ensure PostgreSQL is running.")