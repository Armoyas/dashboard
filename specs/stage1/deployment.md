# Stage 1: Deployment Process

## Overview
The dashboard system is deployed using Docker Compose with three main services behind an Nginx reverse proxy.

## Deployment Steps

### 1. Server Prerequisites
- Clean Ubuntu server with Docker and Docker Compose installed
- Domain pointing to server IP: 62.60.198.209

### 2. Application Deployment

#### Initial Setup
```bash
# Clone repository
git clone https://github.com/Armoyas/dashboard.git
cd dashboard

# Create data directory for DuckDB
mkdir -p data
```

#### Build and Deploy
```bash
# Build all services
docker compose build --no-cache

# Start services
docker compose up -d

# Verify deployment
docker compose ps
```

#### Configuration
- Frontend available at: `http://62.60.198.209/`
- Backend API at: `http://62.60.198.209/api/`
- API documentation at: `http://62.60.198.209/docs/`

### 3. Data Import
```bash
# Copy database file to server
scp data/analytics.duckdb root@62.60.198.209:/opt/data/dashboard/data/

# Restart backend to load data
docker compose restart backend
```

### 4. Updates

#### Frontend Updates
```bash
# For Next.js 15.1.3+ with standalone output
# Ensure next.config.js includes:
# output: 'standalone'

# Build fix for prerendering errors:
# Use force-dynamic in pages that query data
# Apply null-safety: (merchants || []).find(...)
```

#### Backend Updates
```bash
docker compose build backend --no-cache
docker compose up -d backend
```

#### Full Update
```bash
git pull origin main
docker compose build --no-cache
docker compose up -d
```

### 5. Monitoring
```bash
# Check container logs
docker compose logs -f

# Monitor resource usage
docker stats

# Health check
curl http://localhost:80/api/health
```

## Troubleshooting

### SSH Access Issues
- Port 22 is filtered/blocked on 62.60.198.209
- Use HTTP endpoints for deployment
- deploy.sh should install openssh-server if SSH is needed

### Build Issues
- Next.js 14→15 upgrades fix `force-dynamic` with standalone output
- Ensure `--no-cache` is used for Next.js upgrades
- Check for null reference errors in page components

### Database Issues
- DuckDB files should be in `./data/` volume
- Backup before major updates: `docker cp <container>:/app/data/analytics.duckdb ./backup.duckdb`

## Rollback Procedure
```bash
# Tag releases in git
git tag -a v1.0.0 -m "Production release"

# To rollback:
git checkout v1.0.0
docker compose build --no-cache
docker compose up -d
```
