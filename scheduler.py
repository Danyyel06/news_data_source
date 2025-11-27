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
    """Creates a professional HTML email that avoids spam filters."""
    if not news_list:
        return """
        <!DOCTYPE html>
        <html lang="en">
        <head><meta charset="UTF-8"></head>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h3>No new regulatory news found in this period.</h3>
        </body>
        </html>
        """
    
    # Professional HTML structure with proper DOCTYPE
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Regulatory News Digest</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f4; margin: 0; padding: 20px;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            
            <!-- Header -->
            <div style="border-bottom: 3px solid #3498db; padding-bottom: 15px; margin-bottom: 25px;">
                <h2 style="color: #2c3e50; margin: 0; font-size: 24px;">📰 Regulatory News Digest</h2>
                <p style="color: #7f8c8d; margin: 5px 0 0 0; font-size: 14px;">Latest financial regulatory updates</p>
            </div>
            
            <!-- Introduction -->
            <p style="font-size: 14px; color: #555; margin-bottom: 20px;">
                Here are the latest regulatory news articles from the past week:
            </p>
            
            <!-- News Items -->
    """
    
    for item in news_list:
        title = item.get('title', 'No Title')
        source = item.get('source_category', 'Unknown Source')
        url = item.get('source_url', '#')
        
        # Format date nicely
        pub_date = item.get('publication_date')
        if pub_date:
            pub_date_str = pub_date.strftime('%B %d, %Y')
        else:
            pub_date_str = 'Date unknown'

        html += f"""
            <div style="border: 1px solid #e0e0e0; padding: 5px; margin-bottom: 15px; border-radius: 5px; background-color: #fafafa;">
                <div style="margin-bottom: 8px;">
                    <a href="{url}" target="_blank" style="color: #2980b9; text-decoration: none; font-weight: bold; font-size: 16px; line-height: 1.4;">
                        {title}
                    </a>
                </div>
                <div style="font-size: 12px; color: #666;">
                    <span style="color: #e74c3c; font-weight: 600;">📌 {source}</span>
                    <span style="color: #95a5a6;"> • </span>
                    <span style="color: #27ae60;">📅 {pub_date_str}</span>
                </div>
            </div>
        """
    
    html += f"""
            <!-- Footer -->
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #e0e0e0; text-align: center;">
                <p style="font-size: 12px; color: #999; margin: 5px 0;">
                    This is an automated regulatory news digest
                </p>
                <p style="font-size: 12px; color: #999; margin: 5px 0;">
                    You are receiving this because you subscribed to financial news updates
                </p>
                <p style="font-size: 11px; color: #bbb; margin: 15px 0 0 0;">
                    Total articles: {len(news_list)} | Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}
                </p>
            </div>
            
        </div>
    </body>
    </html>
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