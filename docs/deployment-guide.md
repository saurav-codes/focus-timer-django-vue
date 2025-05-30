# Deployment Guide for Focus Timer (Django + Vue.js)

## Overview
This guide provides a secure, production-ready deployment process for the Focus Timer application on a Linux VPS. It follows best practices at each step and includes brief explanations to help beginners understand.

## Table of Contents
- [Prerequisites](#prerequisites)
- [1. VPS Setup](#1-vps-setup)
  - [1.1 Create Unprivileged User](#11-create-unprivileged-user)
  - [1.2 Secure SSH Access](#12-secure-ssh-access)
  - [1.3 Firewall & Fail2ban](#13-firewall--fail2ban)
  - [1.4 Automatic Security Updates](#14-automatic-security-updates)
- [2. System Dependencies](#2-system-dependencies)
- [3. Database: PostgreSQL](#3-database-postgresql)
- [4. Redis for Celery](#4-redis-for-celery)
- [5. Codebase Deployment](#5-codebase-deployment)
  - [5.1 Clone Repository](#51-clone-repository)
  - [5.2 Environment Variables](#52-environment-variables)
- [6. Python Virtual Environment](#6-python-virtual-environment)
- [7. Frontend Build (Vue.js)](#7-frontend-build-vuejs)
- [8. Django Migrations & Static Files](#8-django-migrations--static-files)
- [9. Application Server: Gunicorn](#9-application-server-gunicorn)
- [10. Background Workers: Celery & Beat](#10-background-workers-celery--beat)
- [11. Reverse Proxy: Nginx](#11-reverse-proxy-nginx)
- [12. SSL/TLS with Let's Encrypt](#12-ssltls-with-lets-encrypt)
- [13. Monitoring & Logging](#13-monitoring--logging)
- [14. Automated Backups](#14-automated-backups)
- [15. Routine Maintenance](#15-routine-maintenance)
- [Appendix: Quick Command Summary](#appendix-quick-command-summary)

## Prerequisites
- A fresh Ubuntu/Debian VPS (18.04+ or 20.04+).
- Root or sudo access.
- A domain name pointing to your VPS.
- Basic familiarity with Linux shell.

## 1. VPS Setup
### 1.1 Create Unprivileged User
*Why?* Running services as non-root improves security.
```bash
# Add a user, no password login, add to sudo group
adduser --disabled-password --gecos "" focususer
usermod -aG sudo focususer
# Set up SSH access for the new user
# Copy root's authorized keys to the new user
mkdir -p /home/focususer/.ssh
cp /root/.ssh/authorized_keys /home/focususer/.ssh/authorized_keys
# Set ownership and permissions
chown -R focususer:focususer /home/focususer/.ssh
chmod 700 /home/focususer/.ssh
chmod 600 /home/focususer/.ssh/authorized_keys

```
**Explanation:**
- `adduser`: Creates a new Linux user with default settings.
- `--disabled-password`: Prevents setting a login password (forces SSH key auth only).
- `--gecos ""`: Supplies empty fields for the user's full name and contact info.
- `usermod -aG sudo`: Appends (`-a`) the user to the `sudo` group, allowing administrative commands.

### 1.2 Secure SSH Access
*Why?* Prevent unauthorized root or password-based logins.
```bash
# On your local machine, generate SSH key if needed:
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy public key to server:
ssh-copy-id focususer@your.domain.com

# On server, edit /etc/ssh/sshd_config:
#   Port 22
#   PermitRootLogin no
#   PasswordAuthentication no
#   ChallengeResponseAuthentication no
#   UsePAM yes

sudo systemctl reload ssh
```
**Explanation:**
- `ssh-keygen -t ed25519`: Generates a modern, high-security Ed25519 key pair.
- `-C "comment"`: Adds an identifying comment (often your email).
- `ssh-copy-id`: Installs your public key on the remote server's `~/.ssh/authorized_keys` file, allowing key-based logins.
- `PermitRootLogin no`: Disables SSH login as `root`, forcing administrative access via a less-privileged user plus `sudo`.
- `PasswordAuthentication no`: Turns off password-based logins entirely; only key-based auth is allowed.
- `ChallengeResponseAuthentication no`: Disables keyboard-interactive (challenge-response) methods, such as one-time passwords or other PAM-driven prompts, preventing any fallback from key-based authentication.
  - Without this setting, SSH could invoke PAM's challenge modules (e.g. OTP or custom scripts) that might allow weaker or interactive authentication paths.
- `UsePAM yes`: Enables Pluggable Authentication Modules (PAM) integration.
  - Even with password logins disabled, PAM handles account and session management after a successful key login.
  - PAM modules enforce additional security policies (e.g. account expiration, lockouts, resource limits, logging).
  - Ensures that system-wide policies (fail2ban, pam_tally2, custom modules) can apply to every SSH session.
- `systemctl reload ssh`: Applies the above SSH daemon changes without dropping existing connections.

#### 1.2.1. Logging in as focususer
*Why?* Operating as a non-root user mitigates the risk of accidental system-wide changes.

```bash
# Exit the current root SSH session:
exit

# From your local machine, SSH back in as the unprivileged user:
ssh focususer@your.domain.com
```
**Explanation:**
- `exit`: Ends the current SSH session as root and returns you to your local shell.
- `ssh focususer@your.domain.com`: Initiates a new SSH session using your key for the `focususer` account.

### 1.3 Firewall & Fail2ban
*Why?* Limit open ports and block brute-force attempts.
```bash
# Install UFW & Fail2ban
sudo apt update && sudo apt install -y ufw fail2ban

# Basic UFW rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Configure Fail2ban (e.g., /etc/fail2ban/jail.local)
sudo tee /etc/fail2ban/jail.local <<EOF
[DEFAULT]
bantime  = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
port    = 22
filter  = sshd
logpath = /var/log/auth.log
EOF
sudo systemctl restart fail2ban
```
<!-- TODO: write Jail for own app and nginx -->
**Explanation:**
- `ufw default deny incoming`: Blocks all incoming traffic by default.
- `ufw default allow outgoing`: Allows all outbound traffic.
- `ufw allow OpenSSH`: Opens SSH port (usually 22).
- `ufw allow 'Nginx Full'`: Opens HTTP (80) and HTTPS (443) for web traffic.
- `ufw enable`: Activates the firewall with the defined rules.
- `fail2ban`: Monitors log files and bans IPs after too many failed login attempts.
- In `jail.local`:
  - `bantime`: Duration (1h) to ban offenders.
  - `findtime`: Time window (10m) to track failures.
  - `maxretry`: Max allowed failures (5) before ban.

### 1.4 Automatic Security Updates
*Why?* Keep critical packages patched.
```bash
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure unattended-upgrades
```
**Explanation:**
- `unattended-upgrades`: Automatically downloads and installs security updates.
- `dpkg-reconfigure unattended-upgrades`: Opens a configuration prompt to enable auto-updates.

## 2. System Dependencies
*Install tools required for building and deployment.*
```bash
sudo apt install -y git build-essential curl libpq-dev
```
**Explanation:**
- `git`: Version control system to clone your repository.
- `build-essential`: Installs GCC, make, and other build tools for compiling native extensions.
- `curl`: Tool to transfer data from or to a server (used for downloading scripts).
- `libpq-dev`: Development headers for PostgreSQL, required by psycopg2 Python package.

## 3. Database: PostgreSQL
```bash
sudo apt install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql <<EOF
CREATE USER focusdbuser WITH PASSWORD 'StrongPassw0rd';
CREATE DATABASE focusdb OWNER focusdbuser;
\q
EOF

# Secure PostgreSQL: only listen locally and enforce password auth
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = 'localhost'/" /etc/postgresql/*/main/postgresql.conf
sudo tee -a /etc/postgresql/*/main/pg_hba.conf <<EOF
# Only allow local socket and password auth for TCP
local   all             all                                     peer
host    all             all             127.0.0.1/32            md5
EOF
sudo systemctl restart postgresql
```
*Brief:* PostgreSQL is reliable and scalable for production.

## 4. Redis for Celery
```bash
sudo apt install -y redis-server
sudo systemctl enable --now redis

# Secure Redis: bind only to localhost, enable protected mode, optional password
sudo sed -i "s/^bind .*/bind 127.0.0.1 ::1/" /etc/redis/redis.conf
sudo sed -i "s/^protected-mode no/protected-mode yes/" /etc/redis/redis.conf
sudo sed -i "s/# requirepass foobared/requirepass StrongRedisPassw0rd/" /etc/redis/redis.conf
sudo systemctl restart redis
```
*Brief:* Redis acts as broker and result backend for Celery.

## 5. Codebase Deployment
### 5.1 Clone Repository
```bash
# Switch to unprivileged user
sudo su - focususer
cd ~
git clone https://github.com/your-repo/focus-timer-django-vue.git
cd focus-timer-django-vue
```

### 5.2 Environment Variables
*Why?* Keep secrets out of source code.
```bash
# In project root, create .env
cat > .env <<EOF
SECRET_KEY=your_django_secret_key
DEBUG=False
DATABASE_NAME=focusdb
DATABASE_USER=focusdbuser
DATABASE_PASSWORD=StrongPassw0rd
DATABASE_HOST=127.0.0.1
DATABASE_PORT=5432
ALLOWED_HOSTS=your.domain.com
ALLOWED_ORIGINS=https://your.domain.com
EOF

# Secure .env file permissions
chmod 600 .env
```

## 6. Python Virtual Environment
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

## 7. Frontend Build (Vue.js)
```bash
cd ../frontend-vue
npm ci
npm run build
```
*Brief:* Outputs static assets in `dist/`.

## 8. Django Migrations & Static Files
```bash
cd ../backend
source .venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
```

## 9. Application Server: Gunicorn
```bash
pip install gunicorn
```
Create `/etc/systemd/system/gunicorn.service`:
```ini
[Unit]
Description=Gunicorn daemon for Focus Timer
After=network.target

[Service]
User=focususer
Group=www-data
WorkingDirectory=/home/focususer/focus-timer-django-vue/backend
ExecStart=/home/focususer/focus-timer-django-vue/backend/.venv/bin/gunicorn \
  backend.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers 4
EnvironmentFile=/home/focususer/focus-timer-django-vue/.env
Restart=on-failure
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```
Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now gunicorn
```

## 10. Background Workers: Celery & Beat
- Create `/etc/systemd/system/celery.service`:
```ini
[Unit]
Description=Celery worker service for Focus Timer
After=network.target

[Service]
Type=forking
User=focususer
Group=www-data
WorkingDirectory=/home/focususer/focus-timer-django-vue/backend
EnvironmentFile=/home/focususer/focus-timer-django-vue/.env
ExecStart=/home/focususer/focus-timer-django-vue/backend/.venv/bin/celery -A backend worker \
  --loglevel=info --detach
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

- Create `/etc/systemd/system/celery-beat.service`:
```ini
[Unit]
Description=Celery Beat scheduler for Focus Timer
After=network.target

[Service]
Type=simple
User=focususer
Group=www-data
WorkingDirectory=/home/focususer/focus-timer-django-vue/backend
EnvironmentFile=/home/focususer/focus-timer-django-vue/.env
ExecStart=/home/focususer/focus-timer-django-vue/backend/.venv/bin/celery -A backend beat \
  --loglevel=info --detach
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

- Enable & start both services:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now celery celery-beat
```
**Explanation:**
- `Type=forking/simple`: ensures proper startup and process tracking.
- `--detach`: runs worker/beat in background.
- `Restart=on-failure`: automatically recovers from crashes.

## 11. Reverse Proxy: Nginx
Install and configure `/etc/nginx/sites-available/focus-timer`:
```nginx
server {
    listen 80;
    server_name your.domain.com;

    root /home/focususer/focus-timer-django-vue/frontend-vue/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
    location /static/ {
        alias /home/focususer/focus-timer-django-vue/backend/staticfiles/;
    }
    location /api/    { proxy_pass http://127.0.0.1:8000/api/; include proxy_params; }
    location /auth/   { proxy_pass http://127.0.0.1:8000/auth/; include proxy_params; }
    location /admin/  { proxy_pass http://127.0.0.1:8000/admin/; include proxy_params; }
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    client_max_body_size 10M;
}
```
Enable and reload:
```bash
sudo ln -s /etc/nginx/sites-available/focus-timer /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# HTTP to HTTPS redirect (optional if not handled by certbot)
sudo tee /etc/nginx/sites-available/focus-timer-redirect <<EOF
server {
    listen 80;
    server_name your.domain.com;
    return 301 https://$host$request_uri;
}
EOF
sudo ln -s /etc/nginx/sites-available/focus-timer-redirect /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```
**Explanation:**
- Security headers prevent clickjacking, MIME-sniffing, enforce HTTPS.
- `client_max_body_size`: limits upload size to mitigate DoS.
- HTTP->HTTPS redirect ensures all traffic is encrypted.

## 12. SSL/TLS with Let's Encrypt
```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your.domain.com
```
*Brief:* Provides free, auto-renewing certificates.

## 13. Monitoring & Logging
- Use `journalctl -u gunicorn -f` and `journalctl -u celery -f`.
- Set up Logrotate for Gunicorn logs if needed.
- Consider external monitoring (Prometheus/Grafana, UptimeRobot).

## 14. Automated Backups
- Write a cron job for nightly PostgreSQL dumps:
  ```bash
  sudo crontab -u focususer -e
  # Add:
  0 2 * * * pg_dump -U focusdbuser focusdb | gzip > ~/backups/db-$(date +\%F).sql.gz
  ```
- Secure backup storage (offsite or S3).

## 15. Routine Maintenance
- Keep OS & packages updated:
  ```bash
  sudo apt update && sudo apt upgrade -y
  ```
- Review logs, monitor disk and memory.

## Appendix: Quick Command Summary
```bash
# Sample summary of key commands (omitted for brevity)
```

*End of deployment guide.* 
