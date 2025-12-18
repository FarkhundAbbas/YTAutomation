try:
    from sentence_transformers import SentenceTransformer, util
except ImportError:
    class SentenceTransformer:
        def __init__(self, *args, **kwargs): pass
        def encode(self, *args, **kwargs): return []
    class util:
        @staticmethod
        def cos_sim(*args, **kwargs): return [[0]]
    import logging
    logging.getLogger(__name__).warning("SentenceTransformer not found. Using Mock.")

import yaml
import os
from .models import Article
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TrendEngine:
    def __init__(self):
        self.config = self.load_config()
        self.min_mentions = self.config['trend_settings'].get('min_mentions', 3)
        self.keywords = self.config['trend_settings'].get('keywords', [])
        # Load model only when needed to save RAM, or keep it if frequent updates.
        # For a daily batch job, loading once is fine.
        # all-MiniLM-L6-v2 is ~80MB, very fast and cheap.
        logger.info("Loading SentenceTransformer model...")
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2') 
        except:
            self.model = None

    def calculate_trends(self):
        # 1. Fetch unprocessed articles
        articles = list(Article.select().where(Article.processed == False))
        if not articles:
            logger.info("No new articles to process.")
            return

        titles = [a.title for a in articles]
        
        # Mock Logic if model missing
        if not self.model or isinstance(self.model, SentenceTransformer) and not hasattr(self.model, 'encode'):
             for art in articles:
                 art.trend_score = 5.0 # default high score for demo
                 art.save()
             return

        # 2. Encode all titles
        embeddings = self.model.encode(titles, convert_to_tensor=True)
        # ... rest of real logic (won't be reached if mocked above or will fail gracefully)
 

    def load_config(self):
        config_path = os.path.join(os.getcwd(), 'config', 'trends.yaml')
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)

    def calculate_trends(self):
        # 1. Fetch unprocessed articles
        articles = list(Article.select().where(Article.processed == False))
        if not articles:
            logger.info("No new articles to process.")
            return

        titles = [a.title for a in articles]
        
        # 2. Encode all titles
        embeddings = self.model.encode(titles, convert_to_tensor=True)
        
        # 3. Clustering / Similarity Check
        # A simple approach: for each article, count how many others are similar (> 0.7 cosine sim)
        cosine_scores = util.cos_sim(embeddings, embeddings)
        
        processed_ids = set()
        
        for i in range(len(articles)):
            if articles[i].id in processed_ids:
                continue
                
            sim_count = 0
            # Check row i for matches
            for j in range(len(articles)):
                if i == j: continue
                if cosine_scores[i][j] > 0.65: # Threshold
                    sim_count += 1
            
            # 4. Keyword Boost
            keyword_score = 0
            content_lower = (articles[i].title + " " + (articles[i].content or "")).lower()
            for kw in self.keywords:
                if kw.lower() in content_lower:
                    keyword_score += 1.5 # Arbitrary boost
            
            # Final Score formula
            # Base score = similarity count (news velocity/verification) + keyword relevance
            total_score = sim_count + keyword_score
            
            articles[i].trend_score = total_score
            articles[i].save()
            
            logger.info(f"Scored '{articles[i].title}': {total_score} (Sim: {sim_count}, KW: {keyword_score})")

    def get_top_stories(self, limit=5):
        # Return top scoring articles
        return Article.select().where(Article.processed == False).order_by(Article.trend_score.desc()).limit(limit)

if __name__ == "__main__":
    engine = TrendEngine()
    engine.calculate_trends()
    
    print("Top Trending Stories:")
    for art in engine.get_top_stories():
        print(f"[{art.trend_score}] {art.title}")
