# Supplier AP Contract Manager

Multi-tenant SaaS for invoice management & VAT compliance for SMBs.

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL (or Neon account)
- Supabase account

### Setup

1. Clone repo
```bash
git clone https://github.com/YOUR_USERNAME/supplier-ap-saas.git
cd supplier-ap-saas
```

2. Create Python venv
```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# or
venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Create .env file
```bash
cp .env.example .env
# Edit .env with your Neon and Supabase keys
```

5. Start backend
```bash
uvicorn backend.main:app --reload
```

Backend runs at: http://localhost:8000/docs

6. Start frontend (new terminal)
```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:5173

## Tech Stack

- Backend: FastAPI + SQLAlchemy + PostgreSQL
- Frontend: React 18 + TypeScript + Vite
- Auth: Supabase
- Hosting: Railway (backend) + Vercel (frontend)

## Architecture

Multi-tenant SaaS with:
- Organization isolation (org_id on all tables)
- Immutable audit logs
- VAT calculation
- Approval workflows
- Segregation of duties

## Deployment

Auto-deploys on git push to main:
- Backend: Railway.app
- Frontend: Vercel
- Database: Neon