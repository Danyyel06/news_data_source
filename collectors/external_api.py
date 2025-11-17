# collectors/external_api.py

import feedparser 
import re # For smart filtering
from pygooglenews import GoogleNews
from datetime import datetime
import sys, os

# This path modification allows importing from the database folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from database.db_connector import connect, insert_article 

# --- CONFIGURATION ---
# Use advanced search operators (AND, OR, NOT) to maximize relevance and coverage
SEARCH_QUERIES = [
    '"CBN" AND (policy OR circular OR licensing)',
    '"SEC Nigeria" AND (enforcement OR fraud OR market)',
    '("NDIC" OR "NAICOM" OR "FIRS") AND regulation',
    'Nigeria banking fintech policy'
]
SOURCE_CATEGORY = "External-GoogleNews"

def scrape_google_news(conn):
    """Fetches news using defined search queries from Google News RSS feeds."""
    print("Starting Google News scrape...")
    
    # Initialize GoogleNews for Nigeria (ng) and English (en)
    gn = GoogleNews(lang='en', country='NG') 
    
    for query in SEARCH_QUERIES:
        try:
            # The search function returns a dictionary with feed metadata and entries (articles)
            search_result = gn.search(query, when='7d') # Search over the last 7 days
            
            for entry in search_result['entries']:
                # Extract structured data
                title = entry.get('title', 'N/A')
                url = entry.get('link', 'N/A')
                # Use feedparser's date_parsed format and convert to datetime object
                published_time = entry.get('published_parsed')
                if published_time:
                    pub_date = datetime.fromtimestamp(entry.published_parsed)
                else:
                    pub_date = datetime.now()

                # For content, we use the summary provided by the RSS feed
                content = entry.get('summary', 'No summary available.') 

                data = (title, url, pub_date, content, SOURCE_CATEGORY)
                insert_article(conn, data)
                
        except Exception as e:
            print(f"Error scraping Google News for query '{query}': {e}")



# --- CONFIGURATION ---
# Official accounts of regulatory bodies
NITTER_HANDLES = [
    'cenbank',      # CBN
    'officialSECngr', # SEC Nigeria
    'NdicNigeria',  # NDIC
    'NAICOM_Nigeria' # NAICOM (FIRS TBD)
]
NITTER_BASE_URL = "https://nitter.net/" # A common Nitter instance (may need local host if blocked)
TWITTER_SOURCE_CATEGORY = "Social-X"

# Keywords for Smart Filtering
REGULATORY_KEYWORDS = r'(circular|policy|regulation|fintech|licensing|enforcement|fraud|tax|directive)'

def scrape_twitter_nitter(conn):
    """Fetches tweets from regulatory accounts via Nitter RSS and filters them."""
    print("Starting X/Twitter Nitter scrape...")

    for handle in NITTER_HANDLES:
        rss_url = f"{NITTER_BASE_URL}{handle}/rss"
        
        try:
            # 1. Fetch and Parse the RSS Feed
            feed = feedparser.parse(rss_url)
            
            for entry in feed.entries:
                tweet_text = entry.get('title', '').strip()
                tweet_url = entry.get('link', 'N/A')
                
                # 2. Smart Filtering: Check if the tweet text is relevant
                if not re.search(REGULATORY_KEYWORDS, tweet_text, re.IGNORECASE):
                    # print(f"Skipping non-regulatory tweet: {tweet_text[:30]}...")
                    continue
                
                # 3. Normalize Data
                # Use the first 100 characters as the title for easy display
                title = f"[{handle}] {tweet_text[:100]}..." 
                pub_date = datetime.fromisoformat(entry.published) if entry.get('published') else datetime.now()
                
                # Content is the full tweet text
                content = tweet_text 
                category = TWITTER_SOURCE_CATEGORY
                
                data = (title, tweet_url, pub_date, content, category)
                
                # 4. Insert into Database
                insert_article(conn, data)

        except Exception as e:
            print(f"Error scraping X/Twitter for handle @{handle}: {e}")

# --- FINAL TEST RUNNER (Replace the temporary one) ---
if __name__ == '__main__':
    db_conn = connect()
    if db_conn:
        scrape_google_news(db_conn)
        scrape_twitter_nitter(db_conn)
        db_conn.close()
    print("External collector run complete.")


    
if __name__ == '__main__':
    db_conn = connect()
    if db_conn:
        scrape_google_news(db_conn)
        db_conn.close()
    print("Google News scrape finished.")