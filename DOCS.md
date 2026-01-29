# FaceMatch++ Documentation

## Overview

FaceMatch++ is an enterprise-grade facial recognition attendance system with real-time camera matching capabilities. Built with FastAPI and React, it provides a complete solution for employee attendance management using AI-powered face recognition.

## Features

### Core Capabilities
- 👤 **Face Registration**: Upload and register multiple face images per employee
- 🎥 **Real-time Matching**: Live camera-based attendance marking
- 🔐 **Secure Authentication**: JWT-based authentication with role-based access
- 📊 **Quality Assessment**: Automated blur detection and brightness analysis
- 🧠 **Advanced AI**: ArcFace model with 512-dimensional embeddings
- 📈 **Admin Dashboard**: Complete employee and attendance management
- 📤 **Report Export**: Download attendance reports as Excel files

### User Roles
- **Admin**: Full system access, employee management, attendance oversight
- **Employee**: Self-service attendance marking and viewing

## Architecture

### Technology Stack

**Backend**
- FastAPI (Python 3.11+)
- PostgreSQL 15
- SQLAlchemy ORM
- Redis (caching)
- DeepFace + ArcFace model
- OpenCV for image processing

**Frontend**
- React + Vite
- TailwindCSS + shadcn/ui
- Axios for API calls
- React Router

**DevOps**
- Docker & Docker Compose
- Nginx (production)
- Health check monitoring

### Database Schema

**Users Table**
- Authentication and user information
- Role-based access control (admin/employee)

**Faces Table**
- Employee face metadata
- Quality metrics and confidence scores
- Foreign key to users

**Face_Encodings Table**
- 512-dimensional ArcFace embeddings
- Used for similarity matching

**Attendance Table**
- Daily attendance records
- Timestamps and confidence scores

## API Endpoints

### Authentication
```
POST /api/v1/auth/register - Register new user
POST /api/v1/auth/login    - User login
GET  /api/v1/auth/me       - Get current user
```

### Face Management
```
POST   /api/v1/faces/register          - Upload face image
POST   /api/v1/faces/match              - Match face against database
GET    /api/v1/faces/my-faces           - Get user's registered faces
DELETE /api/v1/faces/{id}               - Delete a face
GET    /api/v1/faces/employees          - Get all employees (admin)
DELETE /api/v1/faces/employees/{id}     - Delete employee (admin)
POST   /api/v1/faces/register-multiple  - Upload multiple faces
```

### Attendance
```
POST /api/v1/attendance/mark         - Mark attendance
GET  /api/v1/attendance/my-records   - Get user's attendance
GET  /api/v1/attendance/all          - Get all records (admin)
GET  /api/v1/attendance/export       - Export to Excel (admin)
```

## Setup Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15
- Docker & Docker Compose (optional)

### Quick Start with Docker

1. Clone repository:
```bash
git clone <your-repo-url>
cd FaceMatch
```

2. Create `.env` file:
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/facematch
SECRET_KEY=your-secure-secret-key-change-this
ACCESS_TOKEN_EXPIRE_DAYS=7
REDIS_URL=redis://redis:6379/0
```

3. Start services:
```bash
docker-compose up -d
```

4. Access application:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Manual Setup

**Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

## Configuration

### Environment Variables

**Backend (.env)**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/facematch
SECRET_KEY=your-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_DAYS=7
REDIS_URL=redis://localhost:6379/0
ENVIRONMENT=development
```

**Frontend (.env)**
```env
VITE_API_URL=http://localhost:8000
```

### Quality Thresholds

The system uses the following thresholds for face quality assessment:

- **Blur Detection**: Laplacian variance < 100 (image is too blurry)
- **Brightness**: Optimal range 80-200 (too dark or too bright)
- **Match Threshold**: Cosine similarity > 0.6 (minimum for positive match)
- **Confidence Score**: > 0.7 recommended for high accuracy

## Usage Guide

### For Admins

1. **Register Employees**
   - Navigate to Register Face page
   - Enter employee details
   - Upload clear, well-lit face photos
   - System validates quality automatically

2. **Manage Employees**
   - View all registered employees
   - Delete employees if needed
   - Monitor registration quality

3. **View Attendance**
   - Access Admin Dashboard
   - View all employee attendance
   - Filter by date range
   - Export reports to Excel

### For Employees

1. **Mark Attendance**
   - Navigate to Live Attendance page
   - Allow camera access
   - Stand in front of camera
   - System automatically recognizes and marks attendance

2. **View History**
   - Access Employee Dashboard
   - View attendance history
   - Check timestamps and confidence scores

## Face Recognition Details

### How It Works

1. **Face Detection**: OpenCV Haar Cascades detect faces in images
2. **Quality Check**: Blur and brightness analysis ensure good quality
3. **Embedding Generation**: ArcFace model creates 512-dim vector
4. **Storage**: Embedding stored in PostgreSQL with metadata
5. **Matching**: Cosine similarity compares new face with stored embeddings
6. **Threshold**: Match score > 0.6 considered a positive match

### Best Practices for Face Registration

- Use well-lit environment (natural light preferred)
- Face directly towards camera
- Remove glasses if possible (system works with glasses too)
- Neutral expression
- Upload multiple photos from different angles
- Ensure minimum 200x200 pixel resolution

## Deployment

### Docker Production Deployment

1. Update `docker-compose.yml` for production settings
2. Set strong secrets in `.env`
3. Configure proper database backup
4. Set up reverse proxy (Nginx)
5. Enable SSL/TLS certificates

### Health Checks

The system includes automated health monitoring:
```bash
python backend/system_health_check.py
```

Checks:
- Database connectivity
- Face detection functionality
- Model loading
- API endpoints
- Cache availability

## Troubleshooting

### Common Issues

**Face not detected**
- Ensure good lighting
- Face camera directly
- Check image quality (not too blurry)

**Low match confidence**
- Register more face images
- Improve lighting conditions
- Ensure consistent image quality

**Camera not working**
- Check browser permissions
- Use HTTPS for production
- Verify camera drivers

**Database connection failed**
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database exists

## Security Considerations

- JWT tokens expire after configured days
- Passwords hashed with bcrypt
- SQL injection protection via ORM
- CORS configured for production
- File upload validation
- Rate limiting recommended for production

## Performance Optimization

- Redis caching for face embeddings (10-minute TTL)
- Connection pooling for database
- Lazy loading for ML models
- Image compression before processing
- Batch processing for multiple faces

## Contributing

This is a private project. For questions or issues, contact the development team.

## License

Private - Internal Use Only

## Credits

- **Face Recognition**: DeepFace library with ArcFace model
- **Backend Framework**: FastAPI
- **Frontend**: React + Vite
- **UI Components**: shadcn/ui

---

**Version**: 2.1.0  
**Last Updated**: January 29, 2026  
**Status**: Production Ready
