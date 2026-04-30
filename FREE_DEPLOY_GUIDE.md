# 🆓 Oracle Cloud Free Tier Deploy Guide

## 📋 Oracle Cloud Free Tier Benefits
- **4GB RAM**
- **2 CPU cores**
- **200GB Storage**
- **10TB Network bandwidth**
- **2 VM instances**
- **Autonomous Database (PostgreSQL)**
- **Load Balancer**
- **Always Free!**

## 🔧 Installation Steps

### 1. Oracle Cloud Hisob Ochish
1. https://www.oracle.com/cloud/free/ ga boring
2. Email bilan ro'yxatdan o'ting
3. Credit card kiritish (hech qanday pul yechilmaydi, faqat tekshirish uchun)
4. Account tasdiqlansin (24 soat ichida)

### 2. VM Instance Yaratish
1. Oracle Cloud Console ga kirish
2. "Compute" → "Instances" → "Create Instance"
3. Quyi parametrlarni tanlang:
   - **Name**: joylinks-test
   - **Compartment**: Your compartment
   - **Shape**: VM.Standard.E2.1.Micro (Free)
   - **Image**: Ubuntu 22.04
   - **SSH Key**: SSH key yaratish va qo'shish
   - **VNIC**: Create VNIC
   - **Boot Volume**: 50GB (free tier da 200GB gacha)

### 3. Network Sozlamalari
1. Virtual Cloud Network (VCN) yaratish
2. Security Rule qo'shish:
   - Port 22 (SSH)
   - Port 80 (HTTP)
   - Port 443 (HTTPS)
   - Port 5000 (Flask app)

### 4. Serverga SSH Orqali Kirish
```bash
ssh -i ~/.ssh/your-key.pem ubuntu@your-public-ip
```

### 5. Docker O'rnatish
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Reboot
sudo reboot
```

### 6. Application Deploy
```bash
# Qayta SSH ulanish
ssh -i ~/.ssh/your-key.pem ubuntu@your-public-ip

# Repository klonlash
git clone https://github.com/your-username/education_management_system.git
cd education_management_system

# Deploy qilish
chmod +x deploy.sh
./deploy.sh
```

### 7. Domain Setup (Bepul)
1. Freenom.com dan bepul domain oling:
   - joylinkstest.tk
   - joylinkstest.ml
   - joylinkstest.ga
   - joylinkstest.cf

2. DNS sozlamalari:
   - A record: @ → your-oracle-ip
   - CNAME: www → @

### 8. SSL Certificate (Bepul)
```bash
# CertBot o'rnatish
sudo apt install certbot python3-certbot-nginx

# SSL olish
sudo certbot --nginx -d joylinkstest.tk -d www.joylinkstest.tk

# Auto-renewal
sudo crontab -e
# Qo'shish: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 🌐 Access Information
- **URL**: https://joylinkstest.tk
- **Username**: admin
- **Password**: secure_admin_password_2024

## 📊 Resource Monitoring
```bash
# System resources
htop
df -h
free -h

# Docker stats
docker stats

# Application logs
docker-compose logs -f
```

## 🔄 Auto-Deploy Script
```bash
# auto-deploy.sh
#!/bin/bash
cd /home/ubuntu/education_management_system
git pull
docker-compose build
docker-compose up -d
```

# Cron job qo'shish
# 0 2 * * * /home/ubuntu/auto-deploy.sh
```

## 🛠️ Troubleshooting

### Common Issues:
1. **Memory limit**: Free tier 4GB RAM
2. **Network**: 10TB bandwidth (yetarli)
3. **Storage**: 200GB (yetarli)

### Solutions:
1. **Optimize app**: Redis caching
2. **Monitor usage**: docker stats
3. **Clean logs**:定期清理

## 💰 Cost Breakdown
- **Oracle Cloud**: $0 (free tier)
- **Domain**: $0 (freenom)
- **SSL**: $0 (let's encrypt)
- **Total**: $0/oy!

## 🎉 Benefits
- ✅ Har doim bepul
- ✅ 500+ users support
- ✅ Professional infrastructure
- ✅ Auto-scaling possible
- ✅ Full control

---

**🎉 Sizning Joylinks IT Test Oracle Cloud da har doim bepul ishlaydi!**
