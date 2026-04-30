#!/bin/bash

# Joylinks IT Test Production Deploy Script (500+ Users)

echo "🚀 Starting Joylinks IT Test Production Deployment..."

# Check system requirements
check_requirements() {
    echo "🔍 Checking system requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check available disk space (need at least 10GB)
    available_space=$(df . | tail -1 | awk '{print $4}')
    if [ $available_space -lt 10485760 ]; then  # 10GB in KB
        echo "❌ Insufficient disk space. Need at least 10GB available."
        exit 1
    fi
    
    # Check available memory (need at least 4GB)
    available_memory=$(free -m | awk 'NR==2{print $7}')
    if [ $available_memory -lt 4096 ]; then
        echo "⚠️  Warning: Less than 4GB RAM available. Performance may be affected."
    fi
    
    echo "✅ System requirements check passed"
}

# Create necessary directories
create_directories() {
    echo "📁 Creating necessary directories..."
    mkdir -p instance
    mkdir -p ssl
    mkdir -p uploads
    mkdir -p static
    mkdir -p logs
    
    # Set permissions
    chmod 755 instance ssl uploads static logs
    
    echo "✅ Directories created"
}

# Build and start containers
deploy_application() {
    echo "📦 Building Docker containers..."
    docker-compose build --no-cache
    
    echo "🔄 Starting services..."
    docker-compose up -d
    
    echo "⏳ Waiting for services to start..."
    sleep 15
    
    # Wait for database to be ready
    echo "🗄️  Waiting for database..."
    until docker-compose exec postgres pg_isready -U joylinks_user -d joylinks_test; do
        echo "Database not ready, waiting..."
        sleep 2
    done
    
    # Wait for Redis to be ready
    echo "🔴 Waiting for Redis..."
    until docker-compose exec redis redis-cli ping; do
        echo "Redis not ready, waiting..."
        sleep 2
    done
    
    echo "✅ Services are ready"
}

# Initialize database
initialize_database() {
    echo "🗄️  Initializing database..."
    
    # Create tables
    docker-compose exec web python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created')
"
    
    # Create default admin user
    docker-compose exec web python -c "
from app import app, db, User
from werkzeug.security import generate_password_hash
with app.app_context():
    if not User.query.filter_by(username='admin').first():
        admin_user = User(
            username='admin',
            password_hash=generate_password_hash('secure_admin_password_2024'),
            role='admin',
            full_name='System Administrator'
        )
        db.session.add(admin_user)
        db.session.commit()
        print('Default admin user created')
    else:
        print('Admin user already exists')
"
    
    echo "✅ Database initialized"
}

# Health checks
health_check() {
    echo "🔍 Performing health checks..."
    
    # Check if all services are running
    echo "📊 Service status:"
    docker-compose ps
    
    # Check web application
    echo "🌐 Checking web application..."
    if curl -f http://localhost:5000/ > /dev/null 2>&1; then
        echo "✅ Web application is responding"
    else
        echo "❌ Web application is not responding"
        return 1
    fi
    
    # Check database connection
    echo "�️  Checking database connection..."
    if docker-compose exec postgres pg_isready -U joylinks_user -d joylinks_test > /dev/null 2>&1; then
        echo "✅ Database connection is working"
    else
        echo "❌ Database connection failed"
        return 1
    fi
    
    # Check Redis connection
    echo "🔴 Checking Redis connection..."
    if docker-compose exec redis redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis connection is working"
    else
        echo "❌ Redis connection failed"
        return 1
    fi
    
    echo "✅ All health checks passed"
}

# Show deployment info
show_deployment_info() {
    echo ""
    echo "🎉 Joylinks IT Test Deployment Complete!"
    echo ""
    echo "📊 Resource Usage:"
    echo "CPU Cores: $(nproc)"
    echo "Memory: $(free -h | awk 'NR==2{print $2}')"
    echo "Disk Space: $(df -h . | tail -1 | awk '{print $4}')"
    echo ""
    echo "🌐 Access Information:"
    echo "Local: http://localhost"
    echo "Network: http://$(hostname -I | awk '{print $1}')"
    echo ""
    echo "🔑 Login Credentials:"
    echo "Username: admin"
    echo "Password: secure_admin_password_2024"
    echo ""
    echo "📊 Monitoring Commands:"
    echo "View logs: docker-compose logs -f"
    echo "Check status: docker-compose ps"
    echo "Resource usage: docker stats"
    echo ""
    echo "�️ Management Commands:"
    echo "Stop: docker-compose down"
    echo "Restart: docker-compose restart"
    echo "Update: git pull && docker-compose build && docker-compose up -d"
    echo ""
    echo "� Database Backup:"
    echo "Backup: docker-compose exec postgres pg_dump -U joylinks_user joylinks_test > backup.sql"
    echo "Restore: docker-compose exec -T postgres psql -U joylinks_user joylinks_test < backup.sql"
    echo ""
    echo "📈 Expected Performance:"
    echo "- Concurrent Users: 500+"
    echo "- Database: PostgreSQL (persistent)"
    echo "- Cache: Redis (fast responses)"
    echo "- Workers: $(($(nproc) * 4 + 1)) processes"
    echo "- Memory Usage: ~2-4GB"
    echo "- Disk Usage: ~10GB (including database)"
}

# Main execution
main() {
    check_requirements
    create_directories
    deploy_application
    initialize_database
    health_check
    show_deployment_info
}

# Run main function
main
