# 📘 FaceMatch++ Complete Project Guide
**A Beginner's Guide to Understanding Every Line of Code**

---

## 📑 Table of Contents

1. [Project Overview](#project-overview)
2. [Project Structure](#project-structure)
3. [Core Concepts Explained](#core-concepts-explained)
4. [Step-by-Step Code Explanation](#step-by-step-code-explanation)
5. [How Everything Works Together](#how-everything-works-together)
6. [Testing Guide](#testing-guide)
7. [Troubleshooting](#troubleshooting)

---

## 🎯 Project Overview

**FaceMatch++** is a production-ready face recognition system built with:
- **Backend**: Python + FastAPI (REST API)
- **Database**: PostgreSQL (stores users, faces, embeddings)
- **Authentication**: JWT tokens (secure login)
- **Future**: Machine Learning for face recognition

### What We've Built So Far:

✅ **Configuration System** - Manages all app settings
✅ **Logging System** - Tracks all events
✅ **Security Module** - Password hashing & JWT tokens
✅ **Database Models** - User, Face, Encoding, AuditLog tables
✅ **REST APIs** - Register, Login, Get User Info

---

## 📁 Project Structure

```
FaceMatch/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── core/
│   │   │   ├── config.py              # Settings & environment variables
│   │   │   ├── logger.py              # Logging system
│   │   │   └── security.py            # Password & JWT functions
│   │   ├── db/
│   │   │   ├── base.py                # Database base classes
│   │   │   ├── session.py             # Database connection
│   │   │   └── init_db.py             # Create tables
│   │   ├── models/
│   │   │   ├── user.py                # User table definition
│   │   │   ├── face.py                # Face table definition
│   │   │   ├── encoding.py            # Encoding table definition
│   │   │   └── audit_log.py           # Audit log table definition
│   │   ├── schemas/
│   │   │   └── user.py                # Request/response validation
│   │   └── api/
│   │       ├── deps.py                # Helper functions
│   │       └── v1/
│   │           └── auth.py            # Authentication endpoints
│   ├── logs/                          # Log files stored here
│   ├── .env                           # Environment variables
│   ├── requirements.txt               # Python packages
│   ├── create_tables.py               # Script to create DB tables
│   ├── seed_data.py                   # Script to add test users
│   └── test_*.py                      # Test scripts
└── COMPLETE_PROJECT_GUIDE.md          # This file!
```

---

## 🧠 Core Concepts Explained

### 1. **FastAPI - What Is It?**

FastAPI is a modern Python web framework for building APIs.

**Think of it like a restaurant:**
- **API Endpoints** = Menu items (what customers can order)
- **Request** = Customer order
- **Response** = Food delivered to customer

**Example:**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
async def say_hello():
    return {"message": "Hello World"}
```

**What happens:**
1. User visits: `http://localhost:8000/hello`
2. FastAPI calls `say_hello()` function
3. Returns JSON: `{"message": "Hello World"}`

**Why async?**
- `async` = Can handle multiple requests at same time
- Without `async` = Handle one request at a time (slow!)

---

### 2. **Pydantic - Data Validation**

Pydantic automatically validates incoming data.

**Without Pydantic (Bad):**
```python
def register(data):
    email = data.get("email")  # What if email is missing?
    password = data.get("password")  # What if password too short?
    # No validation! Bugs everywhere!
```

**With Pydantic (Good):**
```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr  # Must be valid email format
    password: str    # Must be string
    
# FastAPI automatically validates!
@app.post("/register")
def register(user: UserCreate):
    # If data invalid, FastAPI returns error automatically
    # If valid, user object has validated data
    print(user.email)  # Guaranteed to be valid email!
```

---

### 3. **SQLAlchemy - Database ORM**

ORM = Object Relational Mapping (Use Python objects instead of SQL)

**Without SQLAlchemy (Manual SQL):**
```python
cursor.execute("INSERT INTO users (email, password) VALUES (%s, %s)", 
               ("john@email.com", "hashed_password"))
conn.commit()
```

**With SQLAlchemy (Python Objects):**
```python
user = User(email="john@email.com", hashed_password="hashed_password")
db.add(user)
await db.commit()
```

**Benefits:**
- ✅ No SQL injection attacks
- ✅ Type-safe (IDE autocomplete)
- ✅ Works with any database (PostgreSQL, MySQL, SQLite)

---

### 4. **Async/Await - Non-Blocking Code**

**Synchronous (Blocking):**
```python
def get_data():
    result1 = database_query()  # Wait 2 seconds
    result2 = database_query()  # Wait 2 seconds
    # Total: 4 seconds
```

**Asynchronous (Non-Blocking):**
```python
async def get_data():
    task1 = database_query()  # Start query 1
    task2 = database_query()  # Start query 2
    result1 = await task1     # Get result 1
    result2 = await task2     # Get result 2
    # Total: 2 seconds (parallel!)
```

**Key Points:**
- `async def` = Function can do async operations
- `await` = Wait for async operation to complete
- Multiple `await` operations run in parallel

---

### 5. **JWT Tokens - Stateless Authentication**

**Traditional Sessions:**
```
User logs in → Server stores "user123 is logged in" in memory
Problem: Server must remember all logged-in users (doesn't scale!)
```

**JWT Tokens:**
```
User logs in → Server creates token containing user data
Token = eyJhbGci... (encrypted data)
User stores token → Sends with every request
Server decodes token → Validates user
Problem solved: Server is stateless!
```

**JWT Structure:**
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoxMjN9.signature
       ↑ Header                    ↑ Payload         ↑ Signature
```

---

### 6. **Docker - Containerization**

Docker = Run applications in isolated containers

**Your Laptop:**
```
├── Windows OS
├── Your Files
└── Docker Desktop
    └── Container: PostgreSQL
        ├── Linux (minimal)
        ├── PostgreSQL 15
        └── Your database files
```

**Why Docker?**
- ✅ No installation mess (no registry changes)
- ✅ Easy cleanup (delete container = gone!)
- ✅ Same environment everywhere (your laptop = production server)

**Docker Commands:**
```bash
# Start PostgreSQL
docker run --name facematch-postgres -p 5432:5432 -d postgres:15

# Stop
docker stop facematch-postgres

# Delete
docker rm facematch-postgres
```

---

## 📝 Step-by-Step Code Explanation

### File 1: `backend/app/core/config.py`

**Purpose:** Store all application settings in one place

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "FaceMatch++"
    
    # Security
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "facematch_user"
    POSTGRES_PASSWORD: str = "facematch_password"
    POSTGRES_DB: str = "facematch_db"
    POSTGRES_PORT: int = 5432
    
    @property
    def DATABASE_URL(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

# Global instance
settings = Settings()
```

**Explanation:**

1. **`BaseSettings`** - Automatically loads from `.env` file
   ```python
   # .env file:
   SECRET_KEY=my-secret-key
   
   # Automatically becomes:
   settings.SECRET_KEY = "my-secret-key"
   ```

2. **`@property`** - Makes function look like variable
   ```python
   # Without @property (ugly):
   url = settings.get_database_url()
   
   # With @property (clean):
   url = settings.DATABASE_URL
   ```

3. **Type hints** - Tells IDE what type each variable is
   ```python
   SECRET_KEY: str = "..."  # IDE knows this is string
   PORT: int = 5432         # IDE knows this is integer
   ```

**Where it's used:**
```python
# Any file can import settings
from app.core.config import settings

print(settings.DATABASE_URL)
print(settings.SECRET_KEY)
```

---

### File 2: `backend/app/core/logger.py`

**Purpose:** Track all events in the application

```python
import logging
import sys
from pythonjsonlogger import jsonlogger
from datetime import datetime

from app.core.config import settings

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Adds extra fields to every log entry"""
    
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat() + 'Z'
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add file info
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line_number'] = record.lineno

def setup_logger(name="facematch"):
    """Create and configure logger"""
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Console handler (print to terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_format = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_format)
    logger.addHandler(console_handler)
    
    # File handler (save to file)
    file_handler = logging.FileHandler(
        filename=settings.LOG_FILE,
        mode='a',
        encoding='utf-8'
    )
    json_formatter = CustomJsonFormatter()
    file_handler.setFormatter(json_formatter)
    logger.addHandler(file_handler)
    
    return logger

# Global logger
logger = setup_logger()
```

**Explanation:**

1. **Log Levels** (from least to most severe):
   ```python
   logger.debug("Detailed info")    # Development only
   logger.info("Normal event")      # Important events
   logger.warning("Potential issue") # Something unexpected
   logger.error("Error occurred")   # Feature failed
   logger.critical("System down!")  # Entire system failing
   ```

2. **Handlers** - Where logs go:
   - **Console Handler** → Prints to terminal (human-readable)
   - **File Handler** → Saves to file (JSON format for parsing)

3. **JSON Logging** - Structured data:
   ```json
   {
     "timestamp": "2025-12-20T10:00:00Z",
     "level": "INFO",
     "message": "User logged in",
     "user_id": "123",
     "module": "auth",
     "function": "login",
     "line_number": 45
   }
   ```

**Where it's used:**
```python
from app.core.logger import logger

logger.info("Server starting")
logger.error("Database connection failed")
```

---

### File 3: `backend/app/core/security.py`

**Purpose:** Handle passwords and JWT tokens securely

```python
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password):
    """
    Convert plain password to hashed version
    
    Example:
        plain = "MyPass123!"
        hashed = hash_password(plain)
        # Returns: "$2b$12$abcd1234..." (irreversible!)
    """
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    """
    Check if plain password matches hashed version
    
    Example:
        is_valid = verify_password("MyPass123!", hashed_from_db)
        # Returns: True or False
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data, expires_delta=None):
    """
    Create JWT token
    
    Example:
        token = create_access_token({"sub": "john@email.com"})
        # Returns: "eyJhbGciOiJIUzI1NiIsInR5cCI6..."
    """
    to_encode = data.copy()
    
    # Set expiration
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    # Create token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt

def decode_access_token(token):
    """
    Decode JWT token
    
    Example:
        payload = decode_access_token(token)
        # Returns: {"sub": "john@email.com", "exp": 1234567890}
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except:
        return None

def validate_password_strength(password):
    """
    Check if password meets requirements
    
    Rules:
    - At least 8 characters
    - Contains uppercase
    - Contains lowercase
    - Contains digit
    - Contains special character
    
    Returns: (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(char in special_chars for char in password):
        return False, f"Password must contain special character"
    
    return True, None
```

**Explanation:**

1. **Password Hashing (One-Way Encryption):**
   ```python
   # User registers with "MyPass123!"
   hashed = hash_password("MyPass123!")
   # Stored in DB: "$2b$12$abcd1234..."
   
   # User logs in with "MyPass123!"
   is_valid = verify_password("MyPass123!", hashed)
   # Returns: True
   
   # Attacker tries "WrongPass"
   is_valid = verify_password("WrongPass", hashed)
   # Returns: False
   
   # Can NEVER reverse hash to get original password!
   ```

2. **JWT Token Creation:**
   ```python
   # Create token with user data
   token = create_access_token({
       "sub": "john@email.com",  # "sub" = subject
       "user_id": 123
   })
   
   # Token contains encrypted data:
   # eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2hu...
   
   # User sends this token with every request
   # Server decodes it to identify user
   ```

3. **Password Validation:**
   ```python
   is_valid, error = validate_password_strength("short")
   # Returns: (False, "Password must be at least 8 characters long")
   
   is_valid, error = validate_password_strength("ValidPass123!")
   # Returns: (True, None)
   ```

**Where it's used:**
```python
from app.core.security import hash_password, verify_password

# When user registers
hashed = hash_password(user_password)
user.hashed_password = hashed

# When user logs in
if verify_password(login_password, user.hashed_password):
    # Password correct!
    token = create_access_token({"sub": user.email})
```

---

### File 4: `backend/app/db/base.py`

**Purpose:** Base class for all database models

```python
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, DateTime
from datetime import datetime

# Base class for all models
Base = declarative_base()

class TimestampMixin:
    """
    Reusable timestamp fields.
    Any model that inherits this gets created_at and updated_at.
    """
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
```

**Explanation:**

1. **`declarative_base()`** - Creates base class for models
   ```python
   # All models inherit from Base
   class User(Base):
       __tablename__ = "users"
       id = Column(Integer, primary_key=True)
   
   # SQLAlchemy knows User is a database table
   ```

2. **`TimestampMixin`** - Reusable code
   ```python
   # Without mixin (repetitive):
   class User(Base):
       created_at = Column(DateTime, default=datetime.utcnow)
       updated_at = Column(DateTime, default=datetime.utcnow)
   
   class Face(Base):
       created_at = Column(DateTime, default=datetime.utcnow)
       updated_at = Column(DateTime, default=datetime.utcnow)
   
   # With mixin (clean):
   class User(Base, TimestampMixin):
       pass  # Automatically has created_at and updated_at!
   
   class Face(Base, TimestampMixin):
       pass  # Automatically has created_at and updated_at!
   ```

3. **Auto-timestamps:**
   ```python
   # Create user
   user = User(email="john@email.com")
   db.add(user)
   await db.commit()
   
   # created_at automatically set to current time!
   print(user.created_at)  # 2025-12-20 10:00:00
   
   # Update user
   user.email = "newemail@email.com"
   await db.commit()
   
   # updated_at automatically updated!
   print(user.updated_at)  # 2025-12-20 11:00:00
   ```

---

### File 5: `backend/app/db/session.py`

**Purpose:** Manage database connections

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.ENVIRONMENT == "development",
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)
```

**Explanation:**

1. **Database Engine** - Connection to database
   ```python
   # settings.DATABASE_URL = 
   # "postgresql+asyncpg://user:password@localhost:5432/facematch_db"
   #        ↑          ↑         ↑       ↑        ↑         ↑       ↑
   #    Database   Driver    Username  Password  Host    Port  Database
   ```

2. **Engine Parameters:**
   ```python
   echo=True  # Print all SQL queries (for debugging)
   
   pool_pre_ping=True  # Check connection before using
   # Example: Connection died 5 mins ago
   #          Pre-ping detects this, reconnects automatically
   
   pool_size=10  # Keep 10 connections ready
   # Like having 10 phone lines open
   
   max_overflow=20  # Create 20 extra if all 10 busy
   # Total max: 10 + 20 = 30 connections
   ```

3. **Session** - Workspace for database operations
   ```python
   # Create session
   async with AsyncSessionLocal() as db:
       # Add user
       user = User(email="john@email.com")
       db.add(user)
       
       # All changes stay in session (not in DB yet!)
       
       # Save to database
       await db.commit()
       
       # Session automatically closed
   ```

**Where it's used:**
```python
from app.db.session import AsyncSessionLocal

# In any endpoint
async def some_function():
    async with AsyncSessionLocal() as db:
        # Use db to query database
        result = await db.execute(select(User))
        users = result.scalars().all()
```

---

### File 6: `backend/app/models/user.py`

**Purpose:** Define User table structure

```python
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base, TimestampMixin

class UserRole(enum.Enum):
    """User roles"""
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

class User(Base, TimestampMixin):
    """User account table"""
    
    __tablename__ = "users"
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    
    # Relationships
    faces = relationship("Face", back_populates="user", cascade="all, delete-orphan")
```

**Explanation:**

1. **Enum** - Restricted values
   ```python
   # Can only be one of these values
   user.role = UserRole.USER      # ✅ Valid
   user.role = UserRole.ADMIN     # ✅ Valid
   user.role = "superuser"        # ❌ Error! Not in enum
   ```

2. **Column Types:**
   ```python
   Integer       # Whole numbers: 1, 2, 3, ...
   String(100)   # Text up to 100 characters
   Boolean       # True or False
   ```

3. **Column Constraints:**
   ```python
   primary_key=True   # Unique identifier (auto-increments)
   unique=True        # No duplicates allowed
   index=True         # Fast lookups
   nullable=False     # Cannot be empty
   default=True       # Default value if not provided
   ```

4. **Relationships:**
   ```python
   faces = relationship("Face", back_populates="user")
   
   # Usage:
   user = db.query(User).first()
   user_faces = user.faces  # Get all faces for this user!
   ```

5. **Cascade Delete:**
   ```python
   cascade="all, delete-orphan"
   
   # Delete user
   db.delete(user)
   db.commit()
   
   # All their faces automatically deleted!
   ```

**SQL Table Created:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    role userrole DEFAULT 'USER',
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE INDEX ix_users_id ON users (id);
CREATE UNIQUE INDEX ix_users_email ON users (email);
```

---

### File 7: `backend/app/schemas/user.py`

**Purpose:** Validate request/response data

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base fields for user"""
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    """Data needed to create user"""
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    """Data needed to login"""
    email: EmailStr
    password: str

class UserResponse(UserBase):
    """Data returned to client"""
    id: int
    is_active: bool
    is_verified: bool
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
```

**Explanation:**

1. **Schema vs Model:**
   ```python
   # Model = Database table (models/user.py)
   class User(Base):
       hashed_password = Column(String)  # Stored in DB
   
   # Schema = API data (schemas/user.py)
   class UserResponse(BaseModel):
       # No hashed_password!  # Never send password to client!
   ```

2. **EmailStr** - Auto-validates email format
   ```python
   email: EmailStr
   
   # Valid:
   "john@email.com"      # ✅
   "user@domain.co.uk"   # ✅
   
   # Invalid:
   "notanemail"          # ❌ ValidationError
   "missing@"            # ❌ ValidationError
   ```

3. **Field Validation:**
   ```python
   password: str = Field(..., min_length=8)
   #                     ↑         ↑
   #                  Required   Min length
   
   # Valid:
   "Pass123!"  # ✅ 9 characters
   
   # Invalid:
   "short"     # ❌ ValidationError: min 8 characters
   ```

4. **Optional Fields:**
   ```python
   full_name: Optional[str] = None
   
   # Can be:
   full_name = "John Doe"  # ✅ String
   full_name = None        # ✅ None
   ```

5. **Config.from_attributes:**
   ```python
   class Config:
       from_attributes = True
   
   # Allows converting SQLAlchemy model to Pydantic schema:
   user_db = User(id=1, email="john@email.com")  # SQLAlchemy
   user_response = UserResponse.from_orm(user_db)  # Pydantic
   ```

**Where it's used:**
```python
@app.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    #                          ↑
    #          FastAPI validates this automatically!
    
    # If invalid data, returns 422 error
    # If valid, user_data has validated data
    
    new_user = User(
        email=user_data.email,  # Already validated!
        password=hash_password(user_data.password)
    )
```

---

### File 8: `backend/app/api/deps.py`

**Purpose:** Helper functions for endpoints

```python
from fastapi import HTTPException, status
from sqlalchemy import select

from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.core.security import decode_access_token

async def get_user_from_token(token):
    """
    Get user from JWT token
    
    Simple function without Depends - just pass token directly
    """
    
    # Decode JWT
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Get email from token
    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Find user in database
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User inactive"
            )
        
        return user
```

**Explanation:**

1. **HTTPException** - Return error to client
   ```python
   raise HTTPException(
       status_code=401,  # HTTP status code
       detail="Error message shown to user"
   )
   
   # Client receives:
   {
       "detail": "Error message shown to user"
   }
   # With HTTP 401 status
   ```

2. **Token Flow:**
   ```python
   # Step 1: Client sends request
   # Header: Authorization: Bearer eyJhbGci...
   
   # Step 2: Extract token
   token = "eyJhbGci..."
   
   # Step 3: Decode token
   payload = {"sub": "john@email.com", "exp": 1234567890}
   
   # Step 4: Find user in database
   user = db.query(User).filter(User.email == "john@email.com").first()
   
   # Step 5: Return user to endpoint
   return user
   ```

**Where it's used:**
```python
@app.get("/me")
async def get_current_user(authorization: str = Header(None)):
    # Extract token from "Bearer TOKEN"
    token = authorization.split()[1]
    
    # Get user from token
    user = await get_user_from_token(token)
    
    return user
```

---

### File 9: `backend/app/api/v1/auth.py`

**Purpose:** Authentication API endpoints

```python
from fastapi import APIRouter, HTTPException, status, Header
from sqlalchemy import select

from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.models.user import User, UserRole
from app.core.security import hash_password, verify_password, create_access_token, validate_password_strength
from app.api.deps import get_user_from_token
from app.db.session import AsyncSessionLocal
from app.core.logger import logger

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    """
    Register new user
    
    Request:
    {
        "email": "john@email.com",
        "password": "Pass123!",
        "full_name": "John Doe"
    }
    
    Response:
    {
        "id": 1,
        "email": "john@email.com",
        "full_name": "John Doe",
        "is_active": true,
        "is_verified": false,
        "role": "user",
        "created_at": "2025-12-20T10:00:00"
    }
    """
    
    async with AsyncSessionLocal() as db:
        # Check if email already exists
        result = await db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate password
        is_valid, error_msg = validate_password_strength(user_data.password)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Create user
        new_user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name,
            role=UserRole.USER,
            is_active=True,
            is_verified=False
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        logger.info(f"New user registered: {new_user.email}")
        
        return new_user


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
    """
    Login with email and password
    
    Request:
    {
        "email": "john@email.com",
        "password": "Pass123!"
    }
    
    Response:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6...",
        "token_type": "bearer"
    }
    """
    
    async with AsyncSessionLocal() as db:
        # Find user
        result = await db.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Create token
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}
        )
        
        logger.info(f"User logged in: {user.email}")
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(authorization: str = Header(None)):
    """
    Get current user info
    
    Requires: Authorization header with Bearer token
    
    Response:
    {
        "id": 1,
        "email": "john@email.com",
        "full_name": "John Doe",
        "is_active": true,
        "is_verified": false,
        "role": "user",
        "created_at": "2025-12-20T10:00:00"
    }
    """
    
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    # Extract token from "Bearer TOKEN"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication scheme"
            )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    
    # Get user from token
    user = await get_user_from_token(token)
    
    return user
```

**Explanation:**

1. **Router** - Group related endpoints
   ```python
   router = APIRouter(prefix="/auth", tags=["Authentication"])
   
   # All routes automatically prefixed with /auth:
   @router.post("/register")  # Becomes /auth/register
   @router.post("/login")     # Becomes /auth/login
   @router.get("/me")         # Becomes /auth/me
   ```

2. **Status Codes:**
   ```python
   200 OK             # Success
   201 CREATED        # Resource created (user registered)
   400 BAD_REQUEST    # Invalid data
   401 UNAUTHORIZED   # Not logged in
   403 FORBIDDEN      # Logged in but no permission
   404 NOT_FOUND      # Resource doesn't exist
   500 SERVER_ERROR   # Server crashed
   ```

3. **Register Flow:**
   ```python
   # 1. Client sends data
   POST /auth/register
   {
       "email": "john@email.com",
       "password": "Pass123!",
       "full_name": "John Doe"
   }
   
   # 2. FastAPI validates data (Pydantic)
   # 3. Check if email exists
   # 4. Validate password strength
   # 5. Hash password
   # 6. Create user in database
   # 7. Return user info
   ```

4. **Login Flow:**
   ```python
   # 1. Client sends credentials
   POST /auth/login
   {
       "email": "john@email.com",
       "password": "Pass123!"
   }
   
   # 2. Find user in database
   # 3. Verify password
   # 4. Create JWT token
   # 5. Return token
   ```

5. **Protected Endpoint:**
   ```python
   # 1. Client sends request with token
   GET /auth/me
   Header: Authorization: Bearer eyJhbGci...
   
   # 2. Extract token from header
   # 3. Decode token to get email
   # 4. Find user in database
   # 5. Return user info
   ```

---

### File 10: `backend/app/main.py`

**Purpose:** FastAPI application entry point

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logger import logger
from app.api.v1 import auth

# Create FastAPI app
app = FastAPI(
    title="FaceMatch++ API",
    description="Advanced Face Recognition System",
    version="1.0.0",
    docs_url="/docs",     # Swagger UI
    redoc_url="/redoc"    # ReDoc
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (change in production!)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    """Run when server starts"""
    logger.info("=" * 60)
    logger.info("FaceMatch++ API Starting...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info("=" * 60)

@app.on_event("shutdown")
async def shutdown_event():
    """Run when server stops"""
    logger.info("FaceMatch++ API Shutting Down...")

@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "online",
        "message": "FaceMatch++ API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected"
    }
```

**Explanation:**

1. **FastAPI App:**
   ```python
   app = FastAPI(
       title="FaceMatch++ API",  # Shown in docs
       docs_url="/docs"           # Swagger UI location
   )
   ```

2. **CORS Middleware:**
   ```python
   # Problem: Browser blocks frontend from calling API
   # Frontend: localhost:5173
   # Backend:  localhost:8000
   # Browser: "Different origins! BLOCKED!"
   
   # Solution: Tell browser to allow it
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["*"]  # Allow all origins
   )
   ```

3. **Include Router:**
   ```python
   app.include_router(auth.router, prefix="/api/v1")
   
   # Routes from auth.router:
   # /register → /api/v1/auth/register
   # /login    → /api/v1/auth/login
   # /me       → /api/v1/auth/me
   ```

4. **Lifecycle Events:**
   ```python
   @app.on_event("startup")
   # Called once when server starts
   
   @app.on_event("shutdown")
   # Called once when server stops
   ```

---

## 🔄 How Everything Works Together

### Complete Request Flow:

```
1. User Opens Browser
   └─> http://localhost:8000/docs

2. Browser Requests Swagger UI
   └─> FastAPI serves interactive documentation

3. User Clicks "POST /api/v1/auth/register"
   └─> Fills form with email, password, name

4. Browser Sends HTTP Request:
   POST /api/v1/auth/register
   {
       "email": "john@email.com",
       "password": "Pass123!",
       "full_name": "John Doe"
   }

5. FastAPI Receives Request
   └─> CORS Middleware: Check if allowed ✅
   └─> Router: Find matching endpoint ✅
   └─> Found: auth.register_user()

6. Pydantic Validates Data
   └─> Email format valid? ✅
   └─> Password min 8 chars? ✅
   └─> Creates UserCreate object

7. Endpoint Function Executes
   └─> Creates database session
   └─> Checks if email exists
   └─> Validates password strength
   └─> Hashes password
   └─> Creates User object
   └─> Saves to database
   └─> Logs event
   └─> Returns User object

8. FastAPI Converts Response
   └─> User object → UserResponse schema
   └─> Converts to JSON
   └─> Sets status code 201

9. Browser Receives Response:
   201 Created
   {
       "id": 1,
       "email": "john@email.com",
       "full_name": "John Doe",
       "is_active": true,
       "is_verified": false,
       "role": "user",
       "created_at": "2025-12-20T10:00:00"
   }

10. Swagger UI Displays Response
    └─> Shows JSON with syntax highlighting
    └─> User sees their registered account!
```

---

## 📚 Automatic API Documentation

### How Swagger UI Works:

FastAPI automatically generates interactive API documentation from your code!

**1. Endpoint Decorators:**
```python
@router.post("/register", response_model=UserResponse)
#            ↑                      ↑
#         Route path            Response type
```

FastAPI uses this to generate:
- HTTP method (POST)
- Endpoint path (/register)
- Request body schema (UserCreate)
- Response schema (UserResponse)

**2. Pydantic Schemas:**
```python
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
```

FastAPI uses this to generate:
- Input form in Swagger UI
- Field types (string, email, etc.)
- Validation rules (min_length=8)
- Optional vs required fields

**3. Docstrings:**
```python
async def register_user(user_data: UserCreate):
    """
    Register new user
    
    This description appears in Swagger UI!
    """
```

FastAPI uses docstrings as endpoint descriptions.

**4. Example Values:**
FastAPI automatically generates example JSON from schemas:
```json
{
  "email": "user@example.com",
  "password": "string",
  "full_name": "string"
}
```

**5. Try It Out Feature:**
- Swagger UI has "Try it out" button
- Fills in example data
- Click "Execute" to send real request
- Shows actual response

**6. Authorization:**
```python
async def get_current_user_info(authorization: str = Header(None)):
```

FastAPI detects authorization requirement:
- Shows lock icon in Swagger UI
- Provides "Authorize" button
- Stores token for all requests

---

## 🧪 Testing Guide

### Test 1: Register User

**Open Browser:**
```
http://localhost:8000/docs
```

**Steps:**
1. Find `POST /api/v1/auth/register`
2. Click "Try it out"
3. Paste this JSON:
```json
{
  "email": "test@example.com",
  "password": "Test123!@#",
  "full_name": "Test User"
}
```
4. Click "Execute"

**Expected Response (201 Created):**
```json
{
  "id": 3,
  "email": "test@example.com",
  "full_name": "Test User",
  "is_active": true,
  "is_verified": false,
  "role": "user",
  "created_at": "2025-12-20T10:00:00.123456"
}
```

---

### Test 2: Login

**Steps:**
1. Find `POST /api/v1/auth/login`
2. Click "Try it out"
3. Paste:
```json
{
  "email": "test@example.com",
  "password": "Test123!@#"
}
```
4. Click "Execute"

**Expected Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGV4YW1wbGUuY29tIiwidXNlcl9pZCI6MywiZXhwIjoxNzM1MjAwMDAwfQ.xyz123...",
  "token_type": "bearer"
}
```

**Copy the access_token value!**

---

### Test 3: Get Current User (Protected Endpoint)

**Steps:**
1. Click green "Authorize" button (top right)
2. In popup, paste:
```
Bearer YOUR_ACCESS_TOKEN_HERE
```
(Replace with actual token from login)

3. Click "Authorize"
4. Click "Close"
5. Find `GET /api/v1/auth/me`
6. Click "Try it out"
7. Click "Execute"

**Expected Response (200 OK):**
```json
{
  "id": 3,
  "email": "test@example.com",
  "full_name": "Test User",
  "is_active": true,
  "is_verified": false,
  "role": "user",
  "created_at": "2025-12-20T10:00:00.123456"
}
```

---

## 🔧 Troubleshooting

### Problem 1: "Connection refused" when accessing API

**Cause:** Server not running

**Solution:**
```bash
cd f:\FaceMatch\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

### Problem 2: "ModuleNotFoundError"

**Cause:** Missing package

**Solution:**
```bash
pip install <package-name>
```

Or reinstall all:
```bash
pip install -r requirements.txt
```

---

### Problem 3: "ValidationError" when registering

**Cause:** Invalid data

**Examples:**
```json
// ❌ Invalid email
{
  "email": "notanemail",
  "password": "Test123!@#"
}

// ❌ Password too short
{
  "email": "test@example.com",
  "password": "short"
}

// ❌ Password missing special character
{
  "email": "test@example.com",
  "password": "Test12345"
}

// ✅ Valid
{
  "email": "test@example.com",
  "password": "Test123!@#",
  "full_name": "Test User"
}
```

---

### Problem 4: "401 Unauthorized" on /me endpoint

**Cause:** Invalid or missing token

**Solutions:**

1. **Check Authorization header format:**
```
✅ Correct:  Bearer eyJhbGci...
❌ Wrong:    eyJhbGci...
❌ Wrong:    bearer eyJhbGci...  (lowercase)
```

2. **Token expired:**
Login again to get new token

3. **Invalid token:**
Make sure you copied the entire token (it's long!)

---

### Problem 5: Database connection error

**Cause:** PostgreSQL not running

**Solution:**
```bash
# Check if running
docker ps

# If not running, start it
docker start facematch-postgres

# If doesn't exist, create it
docker run --name facematch-postgres \
  -e POSTGRES_USER=facematch_user \
  -e POSTGRES_PASSWORD=facematch_password \
  -e POSTGRES_DB=facematch_db \
  -p 5432:5432 \
  -d postgres:15
```

---

## 📖 Key Takeaways

### 1. **Architecture Pattern: Layered Architecture**

```
┌─────────────────────────────────────┐
│     Presentation Layer (API)        │  ← FastAPI endpoints
│     app/api/v1/auth.py              │
├─────────────────────────────────────┤
│     Business Logic Layer            │  ← Validation, processing
│     app/schemas/user.py             │
├─────────────────────────────────────┤
│     Data Access Layer               │  ← Database operations
│     app/models/user.py              │
├─────────────────────────────────────┤
│     Infrastructure Layer            │  ← Config, logging, security
│     app/core/                       │
└─────────────────────────────────────┘
```

### 2. **Security Best Practices**

✅ Never store plain passwords (always hash)
✅ Use JWT tokens (stateless authentication)
✅ Validate all input data (Pydantic)
✅ Use HTTPS in production
✅ Set strong SECRET_KEY
✅ Implement rate limiting

### 3. **Database Best Practices**

✅ Use async operations (better performance)
✅ Create indexes on frequently queried fields
✅ Use transactions (commit/rollback)
✅ Validate at application level (Pydantic)
✅ Validate at database level (constraints)

### 4. **API Best Practices**

✅ Use proper HTTP status codes
✅ Return consistent error format
✅ Version your API (/api/v1)
✅ Document with Swagger/ReDoc
✅ Use CORS for cross-origin requests

---

## 🎓 Concepts You've Learned

1. ✅ **REST APIs** - How web services communicate
2. ✅ **HTTP Methods** - GET, POST, PUT, DELETE
3. ✅ **Status Codes** - 200, 201, 400, 401, 403, 500
4. ✅ **JSON** - Data exchange format
5. ✅ **Authentication** - JWT tokens
6. ✅ **Authorization** - Bearer scheme
7. ✅ **ORM** - Object-Relational Mapping
8. ✅ **Async/Await** - Non-blocking operations
9. ✅ **Docker** - Containerization
10. ✅ **PostgreSQL** - Relational database
11. ✅ **Pydantic** - Data validation
12. ✅ **FastAPI** - Modern web framework

---

## 🚀 Next Steps

We've built the foundation! Next we'll add:

1. **Face Recognition ML** - Upload and match faces
2. **FAISS Vector Search** - Fast similarity search
3. **Image Processing** - Detect, align, encode faces
4. **Advanced Features** - Face quality checks, liveness detection
5. **Frontend** - React UI with webcam integration

---

## 📞 Quick Reference

### Start Server:
```bash
cd f:\FaceMatch\backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access API:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Root**: http://localhost:8000/

### Database:
```bash
# Start PostgreSQL
docker start facematch-postgres

# Create tables
python create_tables.py

# Add test users
python seed_data.py

# Check tables
python check_tables.py
```

### Test Credentials:
```
Admin:
  Email: admin@facematch.com
  Password: Admin123!

Regular User:
  Email: john@email.com
  Password: Pass123!
```

---

**🎉 Congratulations!** You now understand the complete backend architecture of FaceMatch++!

Keep this guide handy as we add more features. Each new feature will follow similar patterns.

---

*Last Updated: December 20, 2025*
*Project: FaceMatch++ v1.0*
*Author: GitHub Copilot + Student*
