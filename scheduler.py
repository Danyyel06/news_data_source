# scheduler.py

import sys
import os
from datetime import datetime, timedelta  # ← MOVED TO TOP, ADDED timedelta

# Add the project root to the path for correct imports
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# All imports together at the top (clean and organized)
from database.db_connector import connect, fetch_news_by_date_range  # ← FIXED THIS
from collectors.external_api import scrape_google_news, scrape_twitter_nitter 
from utils.email_sender import send_news_digest


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
        print("Running Google News scraper...")
        scrape_google_news(db_conn)
        print("Google News scraper completed")
        
        print("Running Twitter/Nitter scraper...")
        scrape_twitter_nitter(db_conn)
        print("Twitter/Nitter scraper completed")

        # 3. Fetch and send email - GET NEWS FROM LAST 7 DAYS
        if db_conn:
            try:
                print("Fetching news from the last 7 days...")
                
                # Calculate date 7 days ago
                seven_days_ago = datetime.now() - timedelta(days=7)
                
                # Fetch news from last 7 days
                latest_news = fetch_news_by_date_range(db_conn, seven_days_ago, limit=50)
                
                print(f"Found {len(latest_news)} articles from the last 7 days")
                
                if not latest_news:
                    print("⚠️ No news found in database!")
                else:
                    # Format email
                    email_body = format_news_to_html(latest_news)
                    
                    # Send email
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    print(f"Sending email digest with {len(latest_news)} articles...")
                    send_news_digest(f"Regulatory News Digest for {current_date}", email_body)

            except Exception as e:
                print(f"ERROR: Failed to fetch/send email digest: {e}")
                import traceback
                traceback.print_exc()
                
        print(f"--- Scheduler: Collection Run Finished at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

    except Exception as e:
        print(f"FATAL ERROR during scheduled run: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if db_conn:
            db_conn.close()
            
if __name__ == '__main__':
    run_all_collectors()