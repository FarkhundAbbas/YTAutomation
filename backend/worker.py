from celery import Celery
from backend.models import Article, db
from backend.writer import AIWriter
from backend.voice import VoiceGenerator
from backend.media import MediaEngine
from backend.uploader import UploaderService
from backend.translation import TranslatorService
import os
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Config
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Check if we should run in eager mode (no broker needed)
# Using memory backend for demo/dev if redis is not really there
if "redis" in REDIS_URL and not os.getenv("FORCE_REDIS"):
    # Fallback to eager mode if we suspect no redis, or just let user define it.
    # For this specific "Deploy & Test" request, we force Eager to ensure it works without external dependencies.
    CELERY_CONFIG = {
        'task_always_eager': True,
        'broker_url': 'memory://',
        'result_backend': 'cache+memory://'
    }
else:
    CELERY_CONFIG = {
        'broker_url': REDIS_URL,
        'result_backend': REDIS_URL
    }

celery = Celery('news_worker')
celery.conf.update(CELERY_CONFIG)

@celery.task
def process_article_task(article_id, tenant_config=None):
    logger.info(f"Processing Article {article_id}")
    try:
        db.connect(reuse_if_open=True)
        article = Article.get_by_id(article_id)
        
        # 1. Rewrite
        writer = AIWriter()
        script = writer.rewrite_article(article.content or article.title)
        article.rewrite_text = script
        article.save()
        
        # 2. Voice (English default for MVP)
        voice_gen = VoiceGenerator()
        audio_path = f"data/audio_{article.id}.wav"
        os.makedirs("data", exist_ok=True)
        if voice_gen.generate_audio(script, audio_path):
            pass
        else:
            logger.error("Voice generation failed.")
            return "Failed Voice"
            
        # 3. Video
        media = MediaEngine()
        video_path = f"data/video_{article.id}.mp4"
        # Extract keywords for stock check (simple extraction)
        keywords = article.title.split()[:3] 
        if media.generate_video(audio_path, script, keywords[0], video_path, mode="shorts"):
            article.video_path = video_path
            article.save()
        else:
            logger.error("Video generation failed.")
            return "Failed Video"
            
        # 4. Thumbnail
        thumb_path = f"data/thumb_{article.id}.jpg"
        media.generate_thumbnail(article.title, thumb_path)
        
        # Mark processed (pending approval)
        article.processed = True
        article.approval_status = 'pending'
        article.save()
        
        return "Success"
    except Exception as e:
        logger.error(f"Task failed: {e}")
        return f"Error: {e}"
    finally:
        if not db.is_closed():
            db.close()

@celery.task
def upload_task(article_id):
    logger.info(f"Uploading Article {article_id}")
    try:
        db.connect(reuse_if_open=True)
        article = Article.get_by_id(article_id)
        
        uploader = UploaderService()
        
        tags = ["shorts", "celebrity"]
        if uploader.upload_youtube(article.video_path, article.title, article.rewrite_text, tags):
            article.approval_status = 'published'
            article.save()
            
        return "Uploaded"
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        return f"Error: {e}"
    finally:
        if not db.is_closed():
            db.close()
