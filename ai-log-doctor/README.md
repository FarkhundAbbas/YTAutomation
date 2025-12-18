# AI Log Doctor 🏥

> **Self-Healing Log Intelligence System** - Automatically detect, analyze, and fix log parsing failures using AI

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.11-blue)
![React](https://img.shields.io/badge/react-18-blue)

## 🌟 Features

- **Automatic Error Detection** - Detects unparsed logs across any platform
- **AI-Powered Pattern Generation** - Generates regex, grok patterns, and decoders using lightweight AI
- **Multi-SIEM Support** - Integrates with QRadar, Wazuh, Splunk, and Elastic Stack
- **Self-Healing Workflow** - Auto-validates, applies fixes, and rolls back if needed
- **Modern Dashboard** - Beautiful React UI with real-time monitoring
- **Microservices Architecture** - Scalable and production-ready

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- 8GB RAM minimum
- Ports 3000, 8000-8004, 5432, 6379 available

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ai-log-doctor.git
cd ai-log-doctor
```

2. **Initialize the database**
```bash
# Using Docker
docker-compose up -d postgres
docker-compose exec postgres psql -U logdoctor -d logdoctor -f /init.sql

# Or locally with Python
python scripts/init_db.py
```

3. **Start all services**
```bash
docker-compose up -d
```

4. **Access the application**
- Frontend: http://localhost:3000
- API Gateway: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Default Credentials

- **Username:** `admin`
- **Password:** `admin123`

## 📊 Architecture

```
┌─────────────┐
│   Frontend  │ (React + TypeScript)
│  Port 3000  │
└──────┬──────┘
       │
┌──────▼───────────────────────────────────────┐
│          API Gateway (FastAPI)                │
│  Authentication, RBAC, Request Routing        │
└──┬─────┬─────┬─────┬─────┬─────────────────┬─┘
   │     │     │     │     │                 │
   ▼     ▼     ▼     ▼     ▼                 ▼
┌──────┐┌──────┐┌──────┐┌──────┐┌──────┐  ┌──────┐
│Detect││Infer ││Valid.││Synth ││Orches│  │ SIEM │
│ or   ││ er   ││ator  ││etic  ││trator│  │Connec│
└──────┘└──────┘└──────┘└──────┘└──────┘  └──────┘
   │        │        │
   └────────┴────────┴─────────┐
                            ┌───▼────┐    ┌───────┐
                            │ Postgre│────│ Redis │
                            │  SQL   │    └───────┘
                            └────────┘
```

## 🔧 Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | React dashboard |
| API Gateway | 8000 | Main REST API |
| Detector | 8002 | Error detection & clustering |
| Inferer | 8003 | AI pattern generation |
| Validator | 8004 | Pattern validation |
| PostgreSQL | 5432 | Metadata database |
| Redis | 6379 | Cache & queue |

## 📖 Usage

### 1. Ingest Sample Logs

Load test logs into the system:
```bash
python demo/ingest_logs.py samples/sample_logs.txt
```

### 2. View Errors

Navigate to **Error Explorer** in the UI to see detected error groups.

### 3. Generate Fix

Click **"Generate Fix"** on any error group to create pattern proposals.

### 4. Review & Approve

Go to **Proposals** page, review the AI-generated patterns, and approve the best one.

### 5. Apply Fix

Apply the fix to your SIEM platform. The system will validate and deploy.

### 6. Monitor

Use the **Dashboard** to track success rates and system health.

## 🛠️ Development

### Backend Services

```bash
# Install dependencies
poetry install

# Run a service locally
python -m services.api-gateway.main
python -m services.detector.main
python -m services.inferer.main
python -m services.validator.main
```

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## 🧪 Running Tests

```bash
# Backend tests
pytest

# Frontend tests
cd frontend && npm test

# Integration tests
pytest tests/integration/
```

## 📦 Docker Deployment

### Development
```bash
docker-compose up
```

### Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🔌 SIEM Integration

### Elastic Stack
```python
connector = {
    "name": "My Elastic",
    "platform": "elastic",
    "base_url": "https://elasticsearch:9200",
    "credentials": {
        "username": "elastic",
        "password": "password"
    }
}
```

### Wazuh
```python
connector = {
    "name": "My Wazuh",
    "platform": "wazuh",
    "base_url": "https://wazuh-manager:55000",
    "credentials": {
        "username": "admin",
        "password": "admin"
    }
}
```

### Splunk
```python
connector = {
    "name": "My Splunk",
    "platform": "splunk",
    "base_url": "https://splunk:8089",
    "credentials": {
        "username": "admin",
        "password": "password"
    }
}
```

## 📚 API Documentation

Full API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

## 🙏 Acknowledgments

- Built with FastAPI, React, PostgreSQL, and Docker
- AI inference powered by lightweight pattern matching algorithms
- Inspired by real-world SIEM challenges

## 📞 Support

- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/yourusername/ai-log-doctor/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/ai-log-doctor/discussions)

---

**Made with ❤️ for SOC teams worldwide**
