import feedparser
import yaml
import os
import datetime
from .models import Article, init_db
import time
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from newspaper import Article as NewspaperArticle
except ImportError:
    logger.warning("newspaper3k not found. Using MockArticle.")
    class NewspaperArticle:
        def __init__(self, url):
            self.url = url
            self.title = "Mock Content"
            self.text = "This is mock text because newspaper library failed to load."
            self.top_image = None
            self.publish_date = datetime.datetime.now()
        def download(self): pass
        def parse(self): pass 
        def nlp(self): pass
        @property
        def summary(self): return self.text


def load_config():
    config_path = os.path.join(os.getcwd(), 'config', 'sources.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def fetch_and_save_articles():
    config = load_config()
    sources = config.get('sources', [])
    
    new_articles_count = 0
    
    for source in sources:
        if not source.get('enabled', False):
            continue
            
        logger.info(f"Fetching from {source['name']}...")
        feed = feedparser.parse(source['url'])
        
        for entry in feed.entries:
            # Basic Deduplication by URL
            url = entry.link
            try:
                if Article.select().where(Article.url == url).exists():
                    continue
            except Exception as e:
                # If DB error, might need init
                logger.error(f"DB Error checking duplicate: {e}")
                continue
                
            # Extract content
            try:
                # Use newspaper3k for better extraction if needed, 
                # but valid RSS usually has summary or content.
                # For now, quick ingest, full parse later or on demand to save time.
                
                published = None
                if hasattr(entry, 'published_parsed'):
                     published = datetime.datetime.fromtimestamp(time.mktime(entry.published_parsed))
                else:
                    published = datetime.datetime.now()

                article = Article.create(
                    url=url,
                    title=entry.title,
                    content=entry.get('summary', '') or entry.get('description', ''),
                    source=source['name'],
                    published_date=published
                )
                new_articles_count += 1
                logger.info(f"Saved: {entry.title}")
                
            except Exception as e:
                logger.error(f"Failed to save article {url}: {e}")

    logger.info(f"Ingestion complete. {new_articles_count} new articles.")
    
    # MOCK DATA FOR DEMO IF EMPTY
    try:
        if Article.select().count() == 0:
            logger.warning("No articles fetched (network issue?). Inserting MOCK article for demo.")
            Article.create(
                url="http://mock.com/1",
                title="Celebrity Mock: AI Takes Over Hollywood!",
                content="In a shocking turn of events, AI agents are now writing all celebrity news. The stars are reportedly 'thrilled' to have perfect coverage every time. This is a mock article to ensure the dashboard has data.",
                source="Mock Source",
                published_date=datetime.datetime.now()
            )
            Article.create(
                url="http://mock.com/2",
                title="Viral Trend: Cats Watching TikTok",
                content="A new trend has emerged where cats are glued to TikTok screens. Experts say it's the end of productivity for felines everywhere.",
                source="Mock Source",
                published_date=datetime.datetime.now()
            )
    except Exception as e:
        logger.error(f"Mock insertion failed: {e}")

if __name__ == "__main__":
    # Ensure DB is created
    init_db()
    fetch_and_save_articles()
