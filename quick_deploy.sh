#!/bin/bash
# Tez Deploy Script - VPS/Server uchun

echo "🚀 Joylinks IT Test System - Quick Deploy"
echo "=========================================="

# 1. Dependencies o'rnatish
echo "📦 Installing dependencies..."
pip install -r requirements.txt
pip install gunicorn

# 2. Database tekshirish
echo "🗄️ Checking database..."
if [ ! -f "instance/joylinks_test.db" ]; then
    echo "⚠️ Database yo'q! Creating..."
    python3 << EOF
from app import app, db
with app.app_context():
    db.create_all()
    print("✅ Database created!")
EOF
fi

# 3. Production mode tekshirish
echo "🔧 Setting production environment..."
export FLASK_ENV=production

# 4. Gunicorn bilan ishga tushirish
echo "🎯 Starting Gunicorn server..."
gunicorn -b 0.0.0.0:8000 -w 4 app:app --daemon

echo ""
echo "✅ Deployment complete!"
echo "🌐 Server running on http://your-ip:8000"
echo "👑 Admin login: admin / admin123"
echo ""
echo "⚠️ MUHIM: Production'da admin parolini o'zgartiring!"
echo ""
echo "📋 Keyingi qadamlar:"
echo "  1. Nginx sozlang (deployment_guide.md'ga qarang)"
echo "  2. SSL sertifikat o'rnating"
echo "  3. Admin parolini o'zgartiring"
echo "  4. Database backup sozlang"
