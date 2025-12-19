# GES Instagram Automation Platform

A specialized SaaS platform for the nightlife industry that provides smooth Instagram automation with dedicated mobile proxies and seamless user onboarding.

##  Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Future Enhancements](#future-enhancements)
- [License](#license)

---

## Overview

GES (Global Entertainment System) is an Instagram automation platform specifically designed for nightlife businesses. It solves the critical problem of high drop-off rates during user onboarding by implementing a **classic login + 2FA flow** instead of requiring backup codes.

### The Problem We Solve

**Traditional Approach:**
- Users must provide Instagram backup codes
- 80% drop-off rate (most users don't have backup codes)
- Requires pre-planning and technical knowledge

**Our Solution:**
- Classic password login + 2FA (SMS/App)
- 85%+ conversion rate expected
- Familiar, trusted user experience
- No technical knowledge required

---

## Key Features

### User Features
-  **Simple Application Process** - Email + Instagram username + City
-  **Classic Login Flow** - Password → 2FA code → Done
-  **Automatic 2FA Handling** - SMS or authenticator app support
-  **Challenge Resolution** - Handles Instagram security challenges
-  **Session Persistence** - Never get logged out (device fingerprint saved)
-  **Dedicated Proxy** - One mobile 4G proxy per user in their city

### Admin Features
-  **User Management** - Approve/reject applications
-  **Proxy Management** - Automatic proxy purchasing per user
-  **Status Tracking** - Monitor onboarding stages
-  **Checkpoint Monitoring** - Track Instagram security challenges
-  **Login Analytics** - View success rates and errors

### Technical Features
-  **Proxy-First Architecture** - Each user uses their dedicated proxy
-  **Device Fingerprinting** - Consistent device_id, uuid, phone_id
-  **Challenge Loop Prevention** - Smart retry logic and proxy rotation
-  **Session Management** - Encrypted session storage
-  **RESTful API** - Clean, documented endpoints

---

##  Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                     │
│  - Application Form                                     │
│  - Onboarding Flow (Password → 2FA → Success)          │
│  - Status Checking                                      │
└────────────────────┬───────────────────────────────────┘
                     │ HTTP/REST API
┌────────────────────▼───────────────────────────────────┐
│               BACKEND (FastAPI)                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Routes                                          │   │
│  │  - /api/onboarding (apply, login, 2fa)        │   │
│  │  - /api/admin (approve, manage users)          │   │
│  │  - /api/settings (backup codes)                │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Instagram Integration (instagrapi)             │   │
│  │  - Login Handler                               │   │
│  │  - 2FA Handler                                 │   │
│  │  - Challenge Resolver                          │   │
│  │  - Session Manager                             │   │
│  └─────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Proxy Manager                                   │   │
│  │  - Purchase proxies per user                   │   │
│  │  - Health checks                               │   │
│  │  - Rotation strategy                           │   │
│  └─────────────────────────────────────────────────┘   │
└────────────────────┬───────────────────────────────────┘
                     │
┌────────────────────▼───────────────────────────────────┐
│            DATABASE (PostgreSQL)                        │
│  - Users (email, instagram_username, city, status)     │
│  - Login Attempts (tracking, debugging)                │
│  - Sessions (device_id, uuid, cookies)                 │
└─────────────────────────────────────────────────────────┘
```

---

##  Technology Stack

### Backend
- **Framework**: FastAPI 0.95.0
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0.23
- **Instagram API**: instagrapi 2.0.0
- **Authentication**: python-jose, passlib
- **Encryption**: cryptography (Fernet)

### Frontend
- **Framework**: React 18.2.0
- **HTTP Client**: Axios 1.6.0
- **Styling**: Custom CSS (no framework)

### Infrastructure
- **ASGI Server**: Uvicorn
- **Python**: 3.12+
- **Node.js**: 18+

---

##  Installation

### Prerequisites
```bash
# System Requirements
- Python 3.12+
- PostgreSQL 12+
- Node.js 18+
- npm or yarn

# Optional (for production)
- Docker
- Redis (for background tasks)
```

### Step 1: Clone Repository
```bash
git clone https://github.com/yourusername/ges-instagram-automation.git
cd ges-instagram-automation
```

### Step 2: Backend Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install system dependencies for instagrapi (Ubuntu/Debian)
sudo apt-get install -y libjpeg-dev zlib1g-dev
```

### Step 3: Database Setup
```bash
# Create PostgreSQL database
psql postgres
CREATE DATABASE ges_instagram;
CREATE USER ges_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ges_instagram TO ges_user;
\q
```

### Step 4: Frontend Setup
```bash
cd frontend
npm install
cd ..
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file in root directory:
```bash
# Database
DATABASE_URL=postgresql://ges_user:your_password@localhost:5432/ges_instagram

# Security Keys (generate new ones!)
SECRET_KEY=your-super-secret-key-change-in-production
ENCRYPTION_KEY=xK8Jv2mP9nR6tY3wE5qA8bC1dF4gH7jL0oN2pQ5sT9u=

# Proxy Provider (configure based on your provider)
PROXY_PROVIDER_API_KEY=your-proxy-api-key
PROXY_PROVIDER_URL=https://api.yourproxyprovider.com

# Email (for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Frontend URL
FRONTEND_URL=http://localhost:3000

# Instagram Session Settings
SESSION_DIR=./sessions
```

### Generate Encryption Key
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Initialize Database
```bash
# Database tables are created automatically on first run
# Or manually:
python -c "from app.database import init_db; init_db()"
```

---

## Usage

### Start Backend
```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Start Frontend
```bash
cd frontend
npm start
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## API Documentation

### User Onboarding Endpoints

#### 1. Apply for Account
```http
POST /api/onboarding/apply
Content-Type: application/json

{
  "email": "user@example.com",
  "instagram_username": "nightclub_official",
  "city": "Paris"
}

Response:
{
  "status": "success",
  "message": "Application submitted successfully!",
  "user_id": 1
}
```

#### 2. Check Application Status
```http
GET /api/onboarding/status/{user_id}

Response:
{
  "status": "pending" | "approved" | "active",
  "instagram_username": "nightclub_official",
  "city": "Paris",
  "can_login": false,
  "approved_at": "2025-12-19T03:01:20.153952"
}
```

#### 3. Start Login
```http
POST /api/onboarding/login
Content-Type: application/json

{
  "user_id": 1,
  "password": "instagram_password"
}

Response:
{
  "status": "2fa_required" | "challenge_required" | "success",
  "message": "Please enter your 2FA code",
  "next_step": "submit_2fa"
}
```

#### 4. Submit 2FA Code
```http
POST /api/onboarding/submit-2fa
Content-Type: application/json

{
  "user_id": 1,
  "code": "123456"
}

Response:
{
  "status": "success",
  "message": "Login successful!",
  "next_step": "complete"
}
```

#### 5. Submit Challenge Code
```http
POST /api/onboarding/submit-challenge
Content-Type: application/json

{
  "user_id": 1,
  "code": "123456"
}
```

### Admin Endpoints

#### 1. Get Pending Users
```http
GET /api/admin/pending-users

Response:
{
  "count": 5,
  "users": [...]
}
```

#### 2. Approve User
```http
POST /api/admin/approve/{user_id}
Content-Type: application/json

{
  "use_mock_proxy": false
}

Response:
{
  "status": "success",
  "message": "User approved and proxy purchased for Paris",
  "data": {
    "user_id": 1,
    "proxy_city": "Paris"
  }
}
```

#### 3. Get All Users
```http
GET /api/admin/users?status=active

Response:
{
  "count": 10,
  "users": [...]
}
```

---

##  Testing

### Run Test Script
```bash
# Activate virtual environment
source venv/bin/activate

# Run complete flow test
python test_flow.py
```

### Manual Testing Steps

#### 1. Test Application Flow

1. Open http://localhost:3000
2. Fill form:
   - Email: test@nightclub.com
   - Instagram: test_nightclub
   - City: Paris
3. Click "Apply Now"
4. Verify "Application Submitted" screen appears

#### 2. Test Admin Approval

1. Open http://localhost:8000/docs
2. Execute `POST /api/admin/approve/1` with:
```json
   {"use_mock_proxy": true}
```
3. Verify response: `"status": "success"`

#### 3. Test Login Flow

1. Click "Check Status" in frontend
2. Enter Instagram password
3. If 2FA enabled: Enter 6-digit code
4. Verify "Success" screen

### Database Queries for Testing
```sql
-- View all users
SELECT id, email, instagram_username, status, city, checkpoint_count 
FROM users 
ORDER BY created_at DESC;

-- View login attempts
SELECT user_id, attempt_type, success, error_message, created_at 
FROM login_attempts 
ORDER BY created_at DESC 
LIMIT 20;

-- Check active users
SELECT COUNT(*) FROM users WHERE status = 'active';
```

---

### Deployment

#### Backend (Systemd Service)
```bash
# Create service file
sudo nano /etc/systemd/system/ges-api.service

[Unit]
Description=GES Instagram Automation API
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/ges-instagram-automation
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable ges-api
sudo systemctl start ges-api
```

#### Frontend (Nginx)
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    root /path/to/ges-instagram-automation/frontend/build;
    index index.html;
    
    location / {
        try_files $uri /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## User Journey Flow
```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: USER APPLICATION                                    │
├─────────────────────────────────────────────────────────────┤
│ User visits: http://localhost:3000                          │
│ Fills: Email, Instagram Username, City                      │
│ Clicks: "Apply Now"                                         │
│ Status: PENDING                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: ADMIN APPROVAL (Background)                         │
├─────────────────────────────────────────────────────────────┤
│ Admin reviews application                                    │
│ System purchases dedicated proxy for user's city           │
│ Status: APPROVED                                            │
│ User receives email notification                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: PASSWORD ENTRY                                      │
├─────────────────────────────────────────────────────────────┤
│ User clicks "Check Status" → sees login screen             │
│ Enters Instagram password                                   │
│ System uses dedicated proxy for authentication             │
│ Status: ONBOARDING (password stage)                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: TWO-FACTOR AUTHENTICATION (if enabled)              │
├─────────────────────────────────────────────────────────────┤
│ User receives SMS or app code                               │
│ Enters 6-digit code                                         │
│ System completes authentication                             │
│ Status: ONBOARDING (2fa stage)                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: SUCCESS                                             │
├─────────────────────────────────────────────────────────────┤
│ Session saved (device_id, uuid, cookies)                   │
│ Status: ACTIVE                                              │
│ Automation starts                                           │
│ User sees: "You're All Set! "                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Future Enhancements

### Phase 1: Core Improvements
- [ ] Real proxy provider integration (Bright Data, IPRoyal)
- [ ] Email notification system (SendGrid, AWS SES)
- [ ] Admin dashboard UI (React)
- [ ] User dashboard (view automation stats)
- [ ] JWT authentication for API

### Phase 2: Advanced Features
- [ ] Backup code support (optional upgrade)
- [ ] Proxy health monitoring and auto-rotation
- [ ] Multi-account management per user
- [ ] DM automation engine
- [ ] Analytics dashboard (engagement metrics)
- [ ] Billing system integration (Stripe)

### Phase 3: Scale & Optimization
- [ ] Redis caching layer
- [ ] Celery background tasks
- [ ] Docker containerization
- [ ] Kubernetes deployment
- [ ] CDN for frontend assets
- [ ] Monitoring (Datadog, Sentry)
- [ ] A/B testing framework

### Phase 4: AI Features
- [ ] Smart DM content generation
- [ ] Best time to post prediction
- [ ] Target audience optimization
- [ ] Engagement rate forecasting

---

### Database Schema

**Users Table:**
```sql
- id (primary key)
- email (unique)
- instagram_username (unique)
- city
- proxy_url
- proxy_provider_id
- device_id
- uuid
- phone_id
- session_file_path
- backup_code_encrypted
- status (pending, approved, onboarding, active, suspended, banned)
- onboarding_stage (password, 2fa, challenge, complete)
- checkpoint_count
- created_at, approved_at, last_login_at
```

**Login Attempts Table:**
```sql
- id
- user_id
- attempt_type (password, 2fa, challenge)
- success (boolean)
- error_message
- created_at
```
---

## Project Status

**Current Version**: 1.0.0 (MVP)
**Status**:  Production Ready (Onboarding Flow)
**Last Updated**: December 2025

### Completed Features
 User application system
 Admin approval workflow  
 Instagram login (password + 2FA + challenge)
 Session persistence
 Proxy architecture (mock for testing)
 Beautiful frontend UI
 Complete API documentation
---

*Making Instagram automation accessible, smooth, and reliable.*
