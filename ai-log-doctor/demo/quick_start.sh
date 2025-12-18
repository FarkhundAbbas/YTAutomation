#!/bin/bash

# AI Log Doctor - Quick Start Script

set -e

echo "=========================================="
echo " AI LOG DOCTOR - QUICK START "
echo "=========================================="
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose found"
echo ""

# Start services
echo "🚀 Starting services..."
docker-compose up -d

echo "⏳ Waiting for services to be healthy..."
sleep 10

# Initialize database
echo "📊 Initializing database..."
docker-compose exec -T postgres psql -U logdoctor -d logdoctor << EOF
-- Database is auto-initialized by SQLAlchemy
SELECT 'Database ready';
EOF

# Run init script
echo "🔧 Creating default admin user..."
docker-compose exec -T api-gateway python /app/scripts/init_db.py

echo ""
echo "=========================================="
echo " ✅ AI LOG DOCTOR IS READY! "
echo "=========================================="
echo ""
echo "🌐 Frontend:  http://localhost:3000"
echo "🔌 API:       http://localhost:8000"
echo "📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "🔑 Default Login:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "🚀 Run demo:"
echo "   python demo/run_demo.py"
echo ""
echo "=========================================="
