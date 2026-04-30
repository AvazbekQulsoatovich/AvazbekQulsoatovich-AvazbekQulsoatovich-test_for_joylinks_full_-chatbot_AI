# 🚀 Joylinks IT Test - Production Deployment Guide

## 📋 Prerequisites

- Docker & Docker Compose
- Git
- Domain name (for production)
- SSL certificates (optional but recommended)

## 🏗️ Quick Deploy

### 1. Clone and Setup
```bash
git clone <your-repo-url>
cd education_management_system
```

### 2. Deploy with Docker Compose
```bash
chmod +x deploy.sh
./deploy.sh
```

### 3. Access the Application
- **Local**: http://localhost
- **Production**: http://your-domain.com

## 🔧 Manual Deploy

### Using Gunicorn (without Docker)
```bash
# Install dependencies
pip install -r requirements.txt

# Run with Gunicorn
gunicorn --config gunicorn_config.py app:app
```

### Using Docker
```bash
# Build image
docker build -t joylinks-it-test .

# Run container
docker run -d -p 5000:5000 -v $(pwd)/instance:/app/instance joylinks-it-test
```

## 🔒 Security Setup

### SSL/HTTPS Setup
1. Get SSL certificates (Let's Encrypt recommended)
2. Place certificates in `ssl/` directory
3. Uncomment HTTPS section in `nginx.conf`
4. Update `docker-compose.yml` for SSL volumes

### Environment Variables
Create `.env` file:
```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///joylinks_test.db
```

## 📊 Monitoring

### Check Logs
```bash
# Docker logs
docker-compose logs -f

# Application logs
docker-compose logs web
```

### Health Check
```bash
curl http://localhost:5000/
```

## 🔧 Configuration

### Gunicorn Settings
Edit `gunicorn_config.py` for:
- Worker processes
- Timeout settings
- Logging configuration

### Nginx Settings
Edit `nginx.conf` for:
- Domain configuration
- SSL settings
- Caching rules

## 📈 Performance Optimization

### Database Optimization
- Consider PostgreSQL for production
- Add connection pooling
- Implement database indexing

### Caching
- Redis for session storage
- CDN for static assets
- Browser caching headers

## 🔄 Updates

### Update Application
```bash
git pull
docker-compose build
docker-compose up -d
```

### Backup Database
```bash
docker-compose exec web cp instance/joylinks_test.db backup/
```

## 🛠️ Troubleshooting

### Common Issues
1. **Port conflicts**: Change port in docker-compose.yml
2. **Permission errors**: Check file permissions
3. **Database errors**: Ensure instance directory exists

### Reset Application
```bash
docker-compose down
docker system prune -f
./deploy.sh
```

## 📞 Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify configuration files
3. Check resource usage

## 🌐 Production Checklist

- [ ] Domain configured
- [ ] SSL certificates installed
- [ ] Environment variables set
- [ ] Database backed up
- [ ] Monitoring configured
- [ ] Firewall rules set
- [ ] Backup strategy implemented

---

**Default Login**: admin / secure_admin_password_2024

🎉 **Your Joylinks IT Test is now production-ready!**
