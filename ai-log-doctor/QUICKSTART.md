# Quick Start Guide

## Windows PowerShell

```powershell
# 1. Initialize database (first time only)
docker-compose up -d postgres
Start-Sleep -Seconds 10
docker-compose exec postgres psql -U logdoctor -d logdoctor

# 2. Start all services
docker-compose up -d

# 3. Initialize database schema and admin user
docker-compose exec api-gateway python scripts/init_db.py

# 4. Run demo
python demo/run_demo.py samples/sample_logs.txt
```

## Access the Application

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Default Credentials

- Username: `admin`
- Password: `admin123`

## Manual Testing Steps

1. **Login** to the web interface
2. **Navigate** to Error Explorer
3. **Upload** or ingest sample logs
4. **View** detected error groups
5. **Click** "Generate Fix" on any error group
6. **Review** AI-generated patterns
7. **Approve** the best pattern
8. **Apply** the fix
9. **Monitor** the dashboard

## Troubleshooting

### Services not starting
```powershell
docker-compose down
docker-compose up -d --build
```

### Database connection issues
```powershell
docker-compose restart postgres
docker-compose logs postgres
```

### Frontend not loading
```powershell
docker-compose restart frontend
docker-compose logs frontend
```

### Clear all data and restart
```powershell
docker-compose down -v
docker-compose up -d
docker-compose exec api-gateway python scripts/init_db.py
```
