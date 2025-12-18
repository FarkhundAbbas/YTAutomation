import schedule
import time
import logging
import os
import yaml
from backend.models import init_db
from backend.ingestion import fetch_and_save_articles
from backend.trends import TrendEngine, Article
from backend.worker import process_article_task

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_cycle():
    logger.info("Starting Daily Cycle...")
    
    # 1. Ingest
    fetch_and_save_articles()
    
    # 2. Trends
    trend_engine = TrendEngine()
    trend_engine.calculate_trends()
    
    # 3. Select Top Stories
    top_stories = trend_engine.get_top_stories(limit=3)
    
    # 4. Queue Processing
    for story in top_stories:
        logger.info(f"Queueing story: {story.title} (Score: {story.trend_score})")
        # In a real multi-tenant app, we'd loop tenants here
        process_article_task.delay(story.id)
        
    logger.info("Cycle complete.")

def load_tenants():
    tenants_dir = os.path.join(os.getcwd(), 'tenants')
    if not os.path.exists(tenants_dir):
        os.makedirs(tenants_dir)
        return []
    # Logic to load individual tenant configs would go here
    return os.listdir(tenants_dir)

if __name__ == "__main__":
    init_db()
    
    # Run once immediately on startup
    run_cycle()
    
    # Schedule daily
    schedule.every().day.at("09:00").do(run_cycle)
    
    logger.info("Scheduler running...")
    while True:
        schedule.run_pending()
        time.sleep(60)
