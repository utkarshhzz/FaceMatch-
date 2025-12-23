# FaceMatch++

Enterprise-grade face recognition system with real-time camera matching capabilities.

## Features

- 👤 **Face Detection & Registration**: Upload and register faces with quality assessment
- 🎥 **Real-time Camera Matching**: Match faces in real-time using webcam
- 🔐 **JWT Authentication**: Secure API with token-based authentication
- 📊 **Quality Metrics**: Blur detection, brightness analysis, and confidence scoring
- 🧠 **ArcFace Model**: State-of-the-art 512-dimensional face embeddings
- 🐘 **PostgreSQL Storage**: Robust database for faces and embeddings

## Tech Stack

- **Backend**: FastAPI, Python 3.11
- **Face Recognition**: DeepFace, ArcFace, OpenCV
- **Database**: PostgreSQL 15
- **ML Framework**: TensorFlow/Keras
- **Authentication**: JWT (7-day tokens)

## Setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd FaceMatch
```

2. Create virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r backend\requirements.txt
```

4. Start PostgreSQL:
```bash
docker-compose up -d
```

5. Create database tables:
```bash
cd backend
python create_tables.py
```

6. Run the server:
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Usage

### Register User
```bash
POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "yourpassword",
  "full_name": "Your Name"
}
```

### Login
```bash
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

### Upload Face
```bash
POST /api/v1/faces/register
Authorization: Bearer <token>
Content-Type: multipart/form-data
file: <image-file>
```

### Real-time Camera Matching

Open browser: `http://localhost:8000/static/camera.html`

## Project Structure

```
FaceMatch/
├── backend/
│   ├── app/
│   │   ├── api/v1/        # API routes
│   │   ├── core/          # Config, security, logger
│   │   ├── db/            # Database session
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   └── utils/         # Face detection/encoding
│   ├── data/              # Uploads & temp files
│   ├── logs/              # Application logs
│   └── static/            # Frontend files
├── data/                  # Data directory
└── venv/                  # Virtual environment
```

## Configuration

Environment variables (`.env`):
```
DATABASE_URL=postgresql://user:password@localhost:5432/facematch
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_DAYS=7
```

## Quality Thresholds

- **Blur**: Laplacian variance < 100 = blurry
- **Brightness**: Optimal range 80-200
- **Match Threshold**: Cosine similarity > 0.6

## License

Private - Internal Use Only

## Author

Built with ❤️ for enterprise face recognition
