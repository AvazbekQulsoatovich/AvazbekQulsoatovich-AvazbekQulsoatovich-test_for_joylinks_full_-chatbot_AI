# 🚀 Heroku Deploy Guide (Bepul Alternative)

## 📋 Heroku Free Tier Limitations
- **RAM**: 512MB (limit)
- **CPU**: Shared
- **Database**: PostgreSQL 10,000 rows (free)
- **Sleep**: 30 daqiqada uxlash
- **Custom Domain**: $7/oy

## 🔧 Heroku Deploy

### 1. Heroku CLI O'rnatish
```bash
# Windows
# Download from: https://devcenter.heroku.com/articles/heroku-cli

# macOS/Linux
brew tap heroku/brew && brew install heroku
```

### 2. Heroku Login
```bash
heroku login
heroku create joylinks-test
```

### 3. Procfile Yaratish
```bash
# Procfile
web: gunicorn --config gunicorn_config.py app:app
```

### 4. Requirements Update
```bash
# requirements.txt ga qo'shish
psycopg2-binary==2.9.7
gunicorn==21.2.0
```

### 5. Deploy
```bash
git add .
git commit -m "Deploy to Heroku"
git push heroku main
```

## ⚠️ Heroku Cheklovlari
- 500+ user uchun yetmaydi
- 30 daqiqada uxlash
- 512MB RAM limit
- Database rows limit

## 💰 Narx
- **Basic**: $0/oy (limitlar bilan)
- **Hobby**: $7/oy (custom domain)
- **Standard**: $25/oy (production)

---

**🎯 Tavsiya: Oracle Cloud Free Tier dan foydalaning!**
