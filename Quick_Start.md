# Quick Start Guide

Get GES Instagram Automation running in 10 minutes.

## Prerequisites

- Python 3.12+
- PostgreSQL
- Node.js 18+

## 5-Step Setup

### 1. Install Dependencies
```bash
# Backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend && npm install && cd ..
```

### 2. Configure Database
```bash
# Create database
psql postgres -c "CREATE DATABASE ges_instagram;"

# Update .env
cat > .env << 'ENVFILE'
DATABASE_URL=postgresql://postgres:password@localhost:5432/ges_instagram
SECRET_KEY=change-this-secret-key
ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
PROXY_PROVIDER_API_KEY=test-key
PROXY_PROVIDER_URL=https://api.test.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASSWORD=your-password
FRONTEND_URL=http://localhost:3000
SESSION_DIR=./sessions
ENVFILE
```

### 3. Start Backend
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Start Frontend
```bash
cd frontend && npm start
```

### 5. Test the Flow

1. **Apply**: http://localhost:3000
2. **Approve**: http://localhost:8000/docs → `POST /api/admin/approve/1`
3. **Login**: Click "Check Status" → Enter credentials

## Quick Test
```bash
python test_flow.py
```

## Done

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

EOF
