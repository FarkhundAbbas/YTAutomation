# Ultra-Cheap VPS Deployment Guide (2GB - 4GB RAM)

## Prerequisites
- **OS**: Ubuntu 22.04 LTS
- **Specs**: 2 vCPU, 4GB RAM (2GB possible with swap and care)

## 1. System Setup
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv ffmpeg imagemagick redis-server
```

## 2. Swap File (Crucial for Low RAM)
```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## 3. Install Ollama (CPU Mode)
```bash
curl -fsSL https://ollama.com/install.sh | sh
# Pull a small model
ollama pull mistral 
# OR for even lower resources
ollama pull phi3
```

## 4. App Setup
```bash
git clone <repo_url> /opt/news-saas
cd /opt/news-saas
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 5. Systemd Services
Create `/etc/systemd/system/news-worker.service`:
```ini
[Unit]
Description=News Celery Worker
After=network.target redis.service

[Service]
User=root
WorkingDirectory=/opt/news-saas
ExecStart=/opt/news-saas/venv/bin/celery -A backend.worker worker --loglevel=info --concurrency=1
Restart=always

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/news-scheduler.service` for `main.py` similarly.

## 6. Optimization Tips
- Disable `XTTS` if crashing, switch to `coqui-tts` with a lighter model or `espeak`.
- Use `all-MiniLM-L6-v2` for trends (already default).
- Schedule tasks to run sequentially, not parallel.
