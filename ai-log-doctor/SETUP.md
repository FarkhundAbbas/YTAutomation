# AI Log Doctor - Setup and Run Instructions

## Quick Setup (Windows)

### Step 1: Start Database

```powershell
cd C:\Users\asnaq\.gemini\antigravity\scratch\ai-log-doctor
docker-compose up -d postgres redis
```

Wait 10 seconds for database to be ready.

### Step 2: Initialize Database

```powershell
# Create tables and admin user
docker-compose run --rm api-gateway python scripts/init_db.py
```

### Step 3: Start All Services

```powershell
docker-compose up -d
```

### Step 4: Verify Services

```powershell
# Check all services are running
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 5: Access Application

Open browser to **http://localhost:3000**

Login with:
- Username: `admin`
- Password: `admin123`

## Testing the Demo

### Option 1: Automated Demo Script

```powershell
# Make sure services are running first
docker-compose up -d

# Wait for services to be healthy
Start-Sleep -Seconds 15

# Run demo
python demo/run_demo.py samples/sample_logs.txt
```

### Option 2: Manual Testing

1. **Login** to http://localhost:3000
2. **Generate test error groups**:
   ```powershell
   curl -X POST http://localhost:8002/detect-errors `
     -H "Content-Type: application/json" `
     -H "Authorization: Bearer YOUR_TOKEN" `
     -d '{\"logs\": [\"2025/01/01 12:00:00 [app] User:test ip-10-0-0-1 Failed auth\"], \"platform\": \"generic\"}'
   ```
3. Navigate to **Error Explorer** in the UI
4. Click **"Generate Fix"** on any error group
5. View the generated patterns

## Troubleshooting

### Services won't start
```powershell
docker-compose down -v
docker-compose up -d --build
```

### Database connection errors
```powershell
docker-compose restart postgres
docker-compose logs postgres
```

### Frontend shows blank page
Check browser console for errors. Make sure API Gateway is running:
```powershell
docker-compose logs api-gateway
```

### Port already in use
Change ports in `docker-compose.yml` if needed.

## Stopping the System

```powershell
# Stop all services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```
