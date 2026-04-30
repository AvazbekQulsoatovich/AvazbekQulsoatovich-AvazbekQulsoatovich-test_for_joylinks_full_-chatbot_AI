@echo off
REM GitHub Upload Script for Joylinks IT Test (Windows)

echo 🚀 GitHub ga yuklash boshlanmoqda...

REM Repository ma'lumotlari
set REPO_NAME=joylinks-it-test
set USERNAME=yourusername
set EMAIL=your.email@example.com

REM Git initialization
echo 📦 Git initialization...
git init
git config --global user.name "%USERNAME%"
git config --global user.email "%EMAIL%"

REM Create .gitignore
echo 📝 Creating .gitignore...
(
echo # Python
echo __pycache__/
echo *.py[cod]
echo *$py.class
echo *.so
echo .Python
echo build/
echo develop-eggs/
echo dist/
echo downloads/
echo eggs/
echo .eggs/
echo lib/
echo lib64/
echo parts/
echo sdist/
echo var/
echo wheels/
echo *.egg-info/
echo .installed.cfg
echo *.egg
echo.
echo # Virtual environments
echo venv/
echo env/
echo ENV/
echo.
echo # IDE
echo .vscode/
echo .idea/
echo *.swp
echo *.swo
echo.
echo # OS
echo .DS_Store
echo Thumbs.db
echo.
echo # Database ^(production^)
echo *.db
echo *.sqlite
echo *.sqlite3
echo.
echo # Environment variables
echo .env
echo .env.local
echo .env.production
echo.
echo # Logs
echo *.log
echo.
echo # Instance folder
echo instance/
echo.
echo # Uploads
echo uploads/
echo.
echo # SSL certificates
echo ssl/
echo.
echo # Docker volumes
echo postgres_data/
echo redis_data/
echo.
echo # Temporary files
echo *.tmp
echo *.bak
) > .gitignore

REM Add all files
echo 📁 Adding files to Git...
git add .

REM Initial commit
echo 💾 Creating initial commit...
git commit -m "Initial commit: Joylinks IT Test - Education Management System

🎯 Features:
- Multi-role system ^(Admin, Teacher, Student^)
- Modern UI with gray theme
- PostgreSQL database support
- Docker deployment ready
- 500+ user support
- Mobile responsive
- PDF report generation
- Secure authentication

🚀 Ready for deployment on Replit, Railway, Oracle Cloud"

REM Add remote
echo 🌐 Adding remote...
git remote add origin https://github.com/%USERNAME%/%REPO_NAME%.git
git branch -M main

echo 🎉 GitHub ga yuklash tayyor!
echo 🌐 Repository: https://github.com/%USERNAME%/%REPO_NAME%
echo.
echo 📋 Keyingi qadam - Deploy qilish:
echo 1. Repository ni GitHub da yarating
echo 2. Git push qiling: git push -u origin main
echo 3. Replit/Railway/Oracle Cloud ga deploy qiling
echo.
echo 🔗 Deploy options:
echo - Replit: https://replit.com ^(eng oson - 3 daqiqa^)
echo - Railway: https://railway.app ^(modern - 5 daqiqa^)
echo - Oracle Cloud: https://oracle.com/cloud ^(professional - bepul^)

pause
