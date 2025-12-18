# System Architecture

```mermaid
graph TD
    RSS[RSS Feeds / APIs] -->|Ingest| DB[(SQLite Database)]
    DB -->|Unprocessed Articles| Trend[Trend Engine]
    Trend -->|Top Stories| Queue[Processing Queue]
    
    subgraph "Worker Node (Celery)"
        Queue -->|Fetch| AI[Ollama Rewriter]
        AI -->|Script| TTS[Voice Generator (Coqui/XTTS)]
        TTS -->|Audio| Video[Media Engine]
        Stock[Pexels API] -->|Footage| Video
        Video -->|MP4| Storage[File Storage]
    end
    
    Storage -->|Wait Approval| Dashboard[Flask Admin UI]
    Dashboard -->|Approve| Upload[Uploader Service]
    Upload -->|Publish| Platform[YouTube / TikTok]
```

## Data Flow
1. **Ingestion**: `ingestion.py` runs periodically, saving raw articles to SQLite.
2. **Analysis**: `trends.py` scores articles based on velocity and keywords.
3. **Drafting**: `writer.py` uses Ollama to rewrite with specific personas.
4. **Production**:
   - `voice.py` generates audio.
   - `media.py` fetches stock video and stitches it together.
5. **Review**: Admin approves video via Web UI.
6. **Distribution**: `uploader.py` pushes to platforms.
