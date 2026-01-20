# FaceMatch++ Deployment Checklist

## ✅ Pre-Deployment Checklist

### 1. Configuration
- [ ] Copy `.env.example` to `.env`
- [ ] Update database credentials in `.env`
- [ ] Configure email service (SMTP credentials)
- [ ] Generate secure `SECRET_KEY`
- [ ] Set `ROOT_ADMIN_ID` and `ROOT_ADMIN_PASSWORD`
- [ ] Set `ENVIRONMENT=production` for production

### 2. Database Setup
- [ ] PostgreSQL 15 installed and running
- [ ] Database created: `facematch_db`
- [ ] User created with proper permissions
- [ ] Run migrations: `alembic upgrade head`
- [ ] Run admin setup: `python setup_admin_system.py`

### 3. Redis Setup
- [ ] Redis installed and running
- [ ] Test connection with `redis-cli ping`
- [ ] Configure password if needed

### 4. Face Recognition Models
- [ ] Download models: `python download_models.py`
- [ ] Verify models in `~/.deepface/weights/`
- [ ] Test model loading

### 5. Dependencies
- [ ] Python 3.11+ installed
- [ ] Install requirements: `pip install -r requirements.txt`
- [ ] Node.js 20+ installed (for frontend)
- [ ] Install frontend packages: `cd frontend && npm install`

### 6. File Permissions
- [ ] Create directories: `data/uploads`, `data/temp`, `logs`
- [ ] Ensure write permissions
- [ ] Configure appropriate ownership

### 7. Security
- [ ] Change default passwords
- [ ] Enable HTTPS (production)
- [ ] Configure firewall rules
- [ ] Set rate limiting
- [ ] Review CORS settings

### 8. Testing
- [ ] Run health check: `python system_health_check.py`
- [ ] Test admin login
- [ ] Test face registration
- [ ] Test face matching
- [ ] Test attendance marking
- [ ] Test report export

## 🐳 Docker Deployment

### Quick Start
```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env with your values
nano .env

# 3. Build and start services
docker-compose up -d

# 4. Check service health
docker-compose ps

# 5. View logs
docker-compose logs -f

# 6. Setup admin (first time only)
docker-compose exec backend python setup_admin_system.py

# 7. Download models (first time only)
docker-compose exec backend python download_models.py
```

### Container Health Checks
```bash
# Check all services
docker-compose ps

# Check backend logs
docker-compose logs backend --tail 50

# Check database
docker-compose exec database psql -U facematch_user -d facematch_db -c "SELECT COUNT(*) FROM users;"

# Check Redis
docker-compose exec redis redis-cli ping

# Run health check
docker-compose exec backend python system_health_check.py
```

## 📝 Common Issues

### Issue: Database connection failed
**Solution:**
- Check PostgreSQL is running: `docker-compose ps`
- Verify credentials in `.env`
- Check database exists: `docker-compose exec database psql -U facematch_user -l`

### Issue: Redis connection failed
**Solution:**
- Check Redis is running: `docker-compose ps`
- Test connection: `docker-compose exec redis redis-cli ping`
- Verify REDIS_HOST in `.env` (should be `redis` in Docker)

### Issue: Face detection not working
**Solution:**
- Download models: `docker-compose exec backend python download_models.py`
- Check model files exist: `docker-compose exec backend ls -la ~/.deepface/weights/`
- Restart backend: `docker-compose restart backend`

### Issue: Email not sending
**Solution:**
- Verify SMTP credentials in `.env`
- For Gmail: Use App Password, not regular password
- Check logs: `docker-compose logs backend | grep -i email`

### Issue: Frontend can't connect to backend
**Solution:**
- Check backend is running: `curl http://localhost:8000/health`
- Verify VITE_API_BASE_URL in frontend environment
- Check CORS settings in `backend/app/main.py`

## 🔄 Maintenance

### Backup Database
```bash
# Create backup
docker-compose exec database pg_dump -U facematch_user facematch_db > backup_$(date +%Y%m%d).sql

# Restore backup
docker-compose exec -T database psql -U facematch_user facematch_db < backup_20260119.sql
```

### Update Application
```bash
# Pull latest changes
git pull

# Rebuild containers
docker-compose down
docker-compose up -d --build

# Run migrations
docker-compose exec backend alembic upgrade head
```

### Clean Up
```bash
# Remove old logs
find logs/ -name "*.log" -mtime +30 -delete

# Clean temp files
find data/temp/ -mtime +1 -delete

# Prune Docker
docker system prune -a --volumes
```

## 📊 Monitoring

### Key Metrics to Monitor
- CPU usage
- Memory usage
- Disk space (especially `data/uploads`)
- Database connections
- Redis memory
- API response times
- Error rates

### Log Locations
- Backend logs: `./logs/facematch.log`
- Docker logs: `docker-compose logs`
- PostgreSQL logs: Inside container
- Redis logs: Inside container

### Health Endpoints
- API Health: `http://localhost:8000/health`
- API Docs: `http://localhost:8000/docs`
- Frontend: `http://localhost:5173`

## 🚀 Production Recommendations

1. **Use environment-specific configs**
   - Set `ENVIRONMENT=production`
   - Use strong passwords
   - Enable rate limiting

2. **Set up monitoring**
   - Application monitoring (New Relic, DataDog)
   - Log aggregation (ELK, CloudWatch)
   - Uptime monitoring

3. **Configure backups**
   - Daily database backups
   - Backup face images
   - Off-site backup storage

4. **Security hardening**
   - Use HTTPS only
   - Implement API gateway
   - Set up WAF
   - Regular security audits

5. **Scalability**
   - Use load balancer
   - Scale containers horizontally
   - Use managed database (RDS)
   - Use managed Redis (ElastiCache)

## 📞 Support

For issues or questions:
1. Check logs first
2. Run `system_health_check.py`
3. Review this checklist
4. Check documentation in `DETAILED_DOCUMENTATION.md`
