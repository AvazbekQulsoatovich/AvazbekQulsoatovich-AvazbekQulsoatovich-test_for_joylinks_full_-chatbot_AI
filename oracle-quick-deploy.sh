#!/bin/bash

# Oracle Cloud Quick Deploy Script

echo "🚀 Oracle Cloud Quick Deploy - Joylinks IT Test"

# System update
echo "📦 Updating system..."
sudo apt update && sudo apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
echo "📥 Cloning application..."
git clone https://github.com/your-username/education_management_system.git
cd education_management_system

# Deploy application
echo "🚀 Deploying application..."
chmod +x deploy.sh
./deploy.sh

echo "✅ Deploy complete!"
echo "🌐 Access: http://$(curl -s ifconfig.me)"
echo "🔑 Username: admin"
echo "🔑 Password: secure_admin_password_2024"
