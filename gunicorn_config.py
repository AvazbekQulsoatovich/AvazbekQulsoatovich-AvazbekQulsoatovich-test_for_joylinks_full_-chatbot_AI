#!/usr/bin/env python3
# Gunicorn configuration for Joylinks IT Test (500+ Users)

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes (optimized for 500+ concurrent users)
workers = multiprocessing.cpu_count() * 4 + 1  # More workers for high traffic
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True
worker_tmp_dir = "/dev/shm"  # Use memory for temp files

# Timeout settings
timeout = 30
keepalive = 2
graceful_timeout = 30

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "joylinks_test"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Performance tuning for 500+ users
max_requests = 500  # Restart workers after 500 requests
preload_app = True
worker_connections = 2000  # More connections per worker

# Memory optimization
worker_memory_limit = 1024 * 1024 * 1024  # 1GB per worker
