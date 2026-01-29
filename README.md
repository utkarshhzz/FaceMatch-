# FaceMatch++

AI-powered facial recognition attendance system with real-time camera matching capabilities. Built for enterprise use with FastAPI backend and React frontend.

## ✨ Features

- 👤 **Face Registration**: Multi-image upload with automatic quality assessment
- 🎥 **Live Attendance**: Real-time camera-based attendance marking
- 🔐 **Secure Auth**: JWT-based authentication with role management
- 📊 **Smart Analytics**: Admin dashboard with attendance reports and Excel export
- 🧠 **Advanced AI**: ArcFace model (512-dim embeddings) with 0.6+ match threshold
- ⚡ **Redis Caching**: Optimized performance with 10-minute embedding cache
- 🐘 **PostgreSQL**: Robust relational database with proper schema design

## 🚀 Tech Stack

- **Backend**: FastAPI, Python 3.11+, SQLAlchemy, Redis
- **Frontend**: React, Vite, TailwindCSS, shadcn/ui
- **AI/ML**: DeepFace, ArcFace, OpenCV, TensorFlow
- **Database**: PostgreSQL 15
- **DevOps**: Docker, Docker Compose, Nginx

## 📦 Quick Start

### Using Docker (Recommended)

1. **Clone and configure**:
```bash
git clone <your-repo-url>
cd FaceMatch
cp .env.example .env
# Edit .env with your configuration
```

2. **Start services**:
```bash
docker-compose up -d
```

3. **Access application**:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/docs
- Admin login: Create via registration endpoint

### Manual Setup

### Manual Setup

**Prerequisites**: Python 3.11+, Node.js 18+, PostgreSQL 15

1. **Backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. **Frontend**:
```bash
cd frontend
npm install
npm run dev
```

## 📖 Documentation

See [DOCS.md](DOCS.md) for complete documentation including:
- Detailed API endpoints
- Database schema
- Configuration options
- Deployment guide
- Troubleshooting

## 🔑 Key API Endpoints

```bash
# Authentication
POST /api/v1/auth/register
POST /api/v1/auth/login

# Face Management
POST /api/v1/faces/register
POST /api/v1/faces/match
GET  /api/v1/faces/employees (admin)

# Attendance
POST /api/v1/attendance/mark
GET  /api/v1/attendance/all (admin)
GET  /api/v1/attendance/export (admin)
```

Full API docs: http://localhost:8000/docs

## ⚙️ Configuration

Create `.env` file:
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/facematch
SECRET_KEY=your-secret-key-minimum-32-characters
ACCESS_TOKEN_EXPIRE_DAYS=7
REDIS_URL=redis://localhost:6379/0
```

## 🎯 How It Works

1. **Face Registration**: Admin uploads employee photos → System detects face → Generates 512-dim embedding → Stores in DB
2. **Attendance Marking**: Employee stands before camera → Face detected → Embedding generated → Compared with database (cosine similarity) → If match > 0.6 threshold → Attendance marked
3. **Quality Checks**: Automatic blur detection (Laplacian < 100) and brightness validation (80-200 range)

## 📁 Project Structure

```
FaceMatch/
├── backend/
│   ├── app/
│   │   ├── api/v1/        # API routes
│   │   ├── core/          # Config, security, logger
│   │   ├── db/            # Database session & init
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── utils/         # Face detection/encoding
│   ├── data/              # Uploads & temp files
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Application pages
│   │   └── services/      # API integration
│   └── Dockerfile
├── docker-compose.yml
└── .env.example
```

## 🧪 Testing

Run system health check:
```bash
python backend/system_health_check.py
```

Checks: Database, Face Detection, Model Loading, API Endpoints, Cache

## 🚀 Deployment

1. Set production environment variables
2. Use `docker-compose.yml` for containerized deployment
3. Configure Nginx as reverse proxy
4. Enable SSL/TLS certificates
5. Set up database backups

See [DOCS.md](DOCS.md) for detailed deployment instructions.

## 🔒 Security

- JWT authentication with configurable expiry
- Bcrypt password hashing
- SQL injection protection via SQLAlchemy ORM
- CORS configuration
- File upload validation
- Role-based access control

## 📊 Performance

- Redis caching for embeddings (10-min TTL)
- Database connection pooling
- Lazy model loading
- Image preprocessing optimization

## 🤝 Contributing

This is a private project. For inquiries, contact the development team.

## 📄 License

Private - Internal Use Only

## 👤 Author

Utkarsh Kumar

---

**Version**: 2.1.0  
**Status**: Production Ready ✅  
**Last Updated**: January 2026
