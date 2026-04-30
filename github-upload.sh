#!/bin/bash

# GitHub Upload Script for Joylinks IT Test

echo "🚀 GitHub ga yuklash boshlanmoqda..."

# Repository ma'lumotlari
REPO_NAME="joylinks-it-test"
USERNAME="yourusername"  # O'z GitHub usernameingizni kiriting
EMAIL="your.email@example.com"  # O'z emailingizni kiriting

# Git initialization
echo "📦 Git initialization..."
git init
git config --global user.name "$USERNAME"
git config --global user.email "$EMAIL"

# Create .gitignore
echo "📝 Creating .gitignore..."
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual environments
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Database (production)
*.db
*.sqlite
*.sqlite3

# Environment variables
.env
.env.local
.env.production

# Logs
*.log

# Instance folder
instance/

# Uploads
uploads/

# SSL certificates
ssl/

# Docker volumes
postgres_data/
redis_data/

# Temporary files
*.tmp
*.bak
EOF

# Add all files
echo "📁 Adding files to Git..."
git add .

# Initial commit
echo "💾 Creating initial commit..."
git commit -m "Initial commit: Joylinks IT Test - Education Management System

🎯 Features:
- Multi-role system (Admin, Teacher, Student)
- Modern UI with gray theme
- PostgreSQL database support
- Docker deployment ready
- 500+ user support
- Mobile responsive
- PDF report generation
- Secure authentication

🚀 Ready for deployment on Replit, Railway, Oracle Cloud"

# GitHub repository creation (GitHub CLI)
echo "🌐 Creating GitHub repository..."
if command -v gh &> /dev/null; then
    gh repo create $USERNAME/$REPO_NAME --public --push
    echo "✅ GitHub repository created and pushed!"
else
    echo "⚠️  GitHub CLI not found. Manual steps:"
    echo "1. Go to https://github.com/new"
    echo "2. Repository name: $REPO_NAME"
    echo "3. Description: Joylinks IT Test - Education Management System"
    echo "4. Make it Public"
    echo "5. Click 'Create repository'"
    echo "6. Run these commands:"
    echo "   git remote add origin https://github.com/$USERNAME/$REPO_NAME.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
    
    # Add remote manually
    git remote add origin https://github.com/$USERNAME/$REPO_NAME.git
    git branch -M main
    
    echo "🔗 Repository ready at: https://github.com/$USERNAME/$REPO_NAME"
fi

echo "🎉 GitHub ga yuklash tugadi!"
echo "🌐 Repository: https://github.com/$USERNAME/$REPO_NAME"
echo ""
echo "📋 Keyingi qadam - Deploy qilish:"
echo "1. Replit: https://replit.com (eng oson - 3 daqiqa)"
echo "2. Railway: https://railway.app (modern - 5 daqiqa)"
echo "3. Oracle Cloud: https://oracle.com/cloud (professional - bepul)"
