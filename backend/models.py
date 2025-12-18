from peewee import *
import datetime
import os

# Ensure backend directory exists for relative imports if needed, 
# but we'll use a data directory for the DB.
DB_PATH = os.path.join(os.getcwd(), 'news.db')
db = SqliteDatabase(DB_PATH)

class BaseModel(Model):
    class Meta:
        database = db

class Article(BaseModel):
    url = CharField(unique=True, max_length=1024)
    title = CharField(max_length=512)
    content = TextField(null=True)  # Full text or summary
    source = CharField()
    published_date = DateTimeField()
    fetched_at = DateTimeField(default=datetime.datetime.now)
    
    # Processing Status
    processed = BooleanField(default=False)
    trend_score = FloatField(default=0.0)
    approval_status = CharField(default='pending') # pending, approved, rejected
    
    # Metadata for downstream steps
    rewrite_text = TextField(null=True)
    video_path = CharField(null=True)
    
class Trend(BaseModel):
    keyword = CharField()
    score = FloatField()
    timestamp = DateTimeField(default=datetime.datetime.now)

def init_db():
    db.connect()
    db.create_tables([Article, Trend])
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
