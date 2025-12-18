# Automated Celebrity News SaaS

A fully automated, multi-tenant system that collects celebrity news, predicts trends, rewrites content using AI personalities, and generates video content for YouTube Shorts, TikTok, etc.

## Features
- **Auto-Ingestion**: Fetches RSS feeds from TMZ, PageSix, etc.
- **Trend Prediction**: Uses Sentence Transformers to rank rising stories.
- **AI Personas**: Rewrites stories with unique personalities (e.g., Gossip Queen) using Ollama.
- **Multi-Language**: Integrates translation (NLLB/MarianMT) and TTS (XTTS/Coqui).
- **Video Generation**: Creates videos from stock footage + audio + captions.
- **Approval Dashboard**: Flask-based UI to review videos before upload.

## Installation

1. **Clone & Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
2. **Setup Directories**
   ```bash
   mkdir -p data tenants logs
   ```
   
3. **Configure**
   - Edit `config/sources.yaml` to add RSS feeds.
   - Edit `config/platforms.yaml` with API keys.
   - Edit `config/media.yaml` with Pexels/Pixabay keys.

4. **Run**
   - **Start Redis**: `redis-server`
   - **Start Ollama**: `ollama serve` (Pull a model: `ollama pull mistral`)
   - **Start Worker**: `celery -A backend.worker worker --loglevel=info`
   - **Start Dashboard**: `python app.py`
   - **Start Scheduler**: `python main.py`

## Architecture
See [ARCHITECTURE.md](ARCHITECTURE.md) for details.

## Deployment
See [DEPLOY_VPS.md](DEPLOY_VPS.md) for ultra-cheap VPS setup.
