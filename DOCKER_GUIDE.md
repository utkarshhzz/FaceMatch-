# 🐳 Docker Quick Reference for FaceMatch

## 📦 What We Built

Your FaceMatch application now has:
- ✅ Backend Dockerfile (Python/FastAPI)
- ✅ Frontend Dockerfile (React/Vite)
- ✅ Docker Compose (orchestrates everything)
- ✅ .dockerignore files (faster builds)
- ✅ Auto-configured networking
- ✅ Persistent data volumes

---

## 🚀 Essential Commands

### Starting the Application
```bash
# Start all services (first time - builds images)
docker-compose up --build

# Start in background (detached mode)
docker-compose up -d

# Start specific service
docker-compose up backend
```

### Stopping the Application
```bash
# Stop all services (Ctrl+C if running in foreground)
docker-compose down

# Stop and remove volumes (⚠️ deletes all data!)
docker-compose down -v
```

### Viewing Logs
```bash
# See all logs
docker-compose logs

# Follow logs (live updates)
docker-compose logs -f

# Logs for specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs database
docker-compose logs redis
```

### Rebuilding
```bash
# Rebuild all images
docker-compose build

# Rebuild specific service
docker-compose build backend

# Rebuild and restart
docker-compose up -d --build backend
```

---

## 🔍 Checking Status

```bash
# List running containers
docker-compose ps

# Show resource usage
docker stats

# Check container health
docker inspect facematch_db | grep Health
```

---

## 🛠️ Accessing Containers

```bash
# Open shell in backend
docker exec -it facematch_backend bash

# Open shell in database
docker exec -it facematch_db bash

# Run PostgreSQL commands
docker exec -it facematch_db psql -U facematch_user -d facematch_db

# Check Redis
docker exec -it facematch_redis redis-cli ping
```

---

## 🧹 Cleaning Up

```bash
# Remove stopped containers
docker-compose rm

# Remove unused images
docker image prune

# Remove everything (⚠️ careful!)
docker system prune -a --volumes
```

---

## 🌐 Access URLs

After starting with `docker-compose up`:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

---

## 🐛 Troubleshooting

### Problem: Port already in use
```bash
# Stop local services first
# Stop PostgreSQL on host
# Stop Redis on host
# Or change ports in docker-compose.yml
```

### Problem: Changes not reflecting
```bash
# For backend Python changes: Auto-reload enabled (just save)
# For frontend React changes: Auto-reload enabled (just save)
# For Dockerfile changes: Rebuild
docker-compose up -d --build
```

### Problem: Database not connecting
```bash
# Check database is healthy
docker-compose ps

# View database logs
docker-compose logs database

# Recreate database
docker-compose down
docker-compose up database
```

### Problem: Out of disk space
```bash
# Clean up Docker
docker system prune -a --volumes
```

---

## 📝 Important Notes

1. **First Run**: Takes 5-10 minutes (downloading images, installing packages)
2. **Subsequent Runs**: Takes ~30 seconds (using cached images)
3. **Code Changes**: Auto-reload enabled for both backend and frontend
4. **Data Persistence**: Database and uploads are saved in Docker volumes
5. **Stop Services**: Always use `docker-compose down` to stop cleanly

---

## ✅ Success Indicators

When everything works correctly:
```
✅ facematch_db      Up (healthy)
✅ facematch_redis   Up (healthy)
✅ facematch_backend Up
✅ facematch_frontend Up
```

---

## 🎯 Quick Testing Checklist

After `docker-compose up`:

1. Check all containers running: `docker-compose ps`
2. Open frontend: http://localhost:5173
3. Check backend docs: http://localhost:8000/docs
4. Test database: `docker exec -it facematch_db psql -U facematch_user -d facematch_db -c "SELECT 1;"`
5. Test Redis: `docker exec -it facematch_redis redis-cli ping`

All working? You're good to go! 🚀
