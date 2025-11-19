# scheduler.py

import sys, os
from datetime import datetime
 
from utils.email_sender import send_news_digest
# Add the project root to the path for correct imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from database.db_connector import connect
from database.db_connector import connect, fetch_latest_news
from collectors.external_api import scrape_google_news, scrape_twitter_nitter 
from utils.email_sender import send_news_digest

# scheduler.py (Place this function definition at the top, after imports)

def format_news_to_html(news_list: list) -> str:
    """Creates a basic HTML table/list from the news data."""
    if not news_list:
        return "<h3>No new regulatory news found in this cycle.</h3>"
        
    html = "<h2>Regulatory News Digest</h2>"
    
    for item in news_list:
        title = item.get('title', 'No Title')
        source = item.get('source_category', 'Unknown Source')
        url = item.get('source_url', '#')
        
        # Ensure publication_date is handled correctly
        pub_date_str = item.get('publication_date').strftime('%Y-%m-%d %H:%M') if item.get('publication_date') else 'N/A'

        html += f"""
        <div style="border: 1px solid #ddd; padding: 10px; margin-bottom: 10px;">
            <p style="font-weight: bold; font-size: 16px;">
                <a href="{url}" target="_blank">{title}</a>
            </p>
            <p style="font-size: 12px; color: #555;">Source: {source} | Time: {pub_date_str}</p>
        </div>
        """
    return html



def run_all_collectors():
    """Connects to DB, runs collectors, and logs the start/end time."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"--- Scheduler: Starting Collection Run at {timestamp} ---")
    
    db_conn = None
    try:
        # 1. Connect to the database
        db_conn = connect()
        if not db_conn:
            print("ERROR: Could not establish database connection. Skipping scrape.")
            return

        # 2. Run the collectors
        scrape_google_news(db_conn)
        scrape_twitter_nitter(db_conn)

        # --- START: NEW EMAIL DIGEST LOGIC BLOCK ---
        if db_conn:
            try:
                # Fetch the top 20 latest articles 
                latest_news = fetch_latest_news(db_conn, limit=20) 
                
                # 1. Format the data into HTML body
                email_body = format_news_to_html(latest_news)
                
                # 2. Send the email digest
                current_date = datetime.now().strftime("%Y-%m-%d")
                send_news_digest(f"Regulatory News Digest for {current_date}", email_body)

            except Exception as e:
                # Log any error specifically related to fetching or sending the email
                print(f"ERROR: Failed to fetch/send email digest: {e}")
        # --- END: NEW EMAIL DIGEST LOGIC BLOCK ---
                
        print(f"--- Scheduler: Collection Run Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

    except Exception as e:
        # Crucial for cron jobs: Log any unexpected failures
        print(f"FATAL ERROR during scheduled run: {e}")
    finally:
        # 3. Ensure connection is closed
        if db_conn:
            db_conn.close()

if __name__ == '__main__':
    run_all_collectors()