# Task Manager Backend 🚀

A modern **REST API** built with **FastAPI**, **MongoDB**, and **Poetry** for task management system.

## ✨ Features

- 🔐 **JWT Authentication** - Secure user registration and login with refresh tokens
- 👤 **User Management** - Complete user profile management
- ✅ **Task CRUD Operations** - Create, read, update, and delete tasks
- 📊 **Task Statistics** - Get insights on task completion and priorities
- 🔍 **Advanced Filtering** - Filter tasks by status, priority, and date
- 🔒 **Data Isolation** - Users can only access their own tasks
- 🧪 **Comprehensive Testing** - 100% test coverage with pytest
- 🐳 **Docker Ready** - Full containerization with Docker Compose
- 📚 **Auto Documentation** - Interactive API docs with Swagger UI

## 🏗️ Architecture

```
backend/
├── app/
│   ├── api/              # API endpoints
│   │   └── endpoints/    # Route modules (auth, tasks, users)
│   ├── core/             # Core configuration
│   │   ├── config.py     # Environment settings
│   │   ├── deps.py       # Dependencies injection
│   │   └── security.py   # JWT & password utilities
│   ├── database/         # MongoDB configuration
│   ├── models/           # Pydantic models
│   │   ├── user.py       # User schemas
│   │   ├── task.py       # Task schemas
│   │   └── token.py      # Auth schemas
│   └── repositories/     # Data access layer
├── tests/                # Comprehensive test suite
│   ├── conftest.py       # Test fixtures
│   ├── test_auth.py      # Authentication tests
│   ├── test_users.py     # User management tests
│   └── test_tasks.py     # Task operations tests
├── .env                  # Environment variables
├── Dockerfile            # Container configuration
├── pyproject.toml        # Poetry dependencies
└── docker-compose.yml    # Multi-service setup
```

## 🛠️ Tech Stack

- **FastAPI** - Modern, fast web framework with automatic API documentation
- **MongoDB** - NoSQL database with Motor async driver
- **Pydantic** - Data validation and serialization
- **JWT** - Secure authentication with access/refresh tokens
- **Poetry** - Modern dependency management
- **Pytest** - Testing framework with async support
- **Docker** - Containerization and orchestration
- **Bcrypt** - Password hashing

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone <repo-url>
cd TASK_MANAGER_CHALLENGE

# Start all services
docker-compose up -d

# Check backend logs
docker-compose logs -f backend

# API is ready at http://localhost:8000
curl http://localhost:8000/
```

### Local Development

```bash
# Navigate to backend directory
cd backend

# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Copy environment variables
cp env.example .env

# Run the server
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 📋 API Endpoints

### 🔐 Authentication
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token

### 👤 User Management
- `GET /api/v1/users/me` - Get current user profile

### ✅ Task Management
- `POST /api/v1/tasks/` - Create new task
- `GET /api/v1/tasks/` - List user tasks (with filtering)
- `GET /api/v1/tasks/{id}` - Get specific task
- `PUT /api/v1/tasks/{id}` - Update task
- `DELETE /api/v1/tasks/{id}` - Delete task
- `GET /api/v1/tasks/stats` - Get task statistics

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database Configuration
MONGODB_URL=mongodb://mongodb:27017/taskmanager
DATABASE_NAME=taskmanager

# Development Settings
DEBUG=true
ENVIRONMENT=development
```

### Complete Configuration Options

The application supports these environment variables:

- `PROJECT_NAME` - API project name
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `DEBUG` - Debug mode (default: false)
- `MONGODB_URL` - MongoDB connection string
- `DATABASE_NAME` - Database name
- `SECRET_KEY` - JWT secret key
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration (default: 30)
- `ALLOWED_HOSTS` - CORS allowed hosts

## 📊 Available Services

| Service | URL | Description |
|---------|-----|-------------|
| API | http://localhost:8000 | FastAPI Backend |
| Docs | http://localhost:8000/docs | Interactive API Documentation |
| ReDoc | http://localhost:8000/redoc | Alternative Documentation |
| MongoDB | localhost:27017 | Database |
| Mongo Express | http://localhost:8081 | MongoDB Admin UI |

## 🧪 Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test file
poetry run pytest tests/test_auth.py -v

# Run with verbose output
poetry run pytest -v -s
```

### Test Coverage
- ✅ **Authentication endpoints** - Registration, login, token refresh
- ✅ **User management** - Profile operations
- ✅ **Task operations** - Full CRUD with user isolation
- ✅ **Data validation** - Input validation and error handling
- ✅ **Security** - Authentication and authorization
- ✅ **Database operations** - Repository pattern testing

## 📦 Data Models

### User Model
```json
{
  "id": "string",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Task Model
```json
{
  "id": "string",
  "title": "Complete project",
  "description": "Finish backend development",
  "status": "por_hacer",
  "priority": "alta",
  "due_date": "2024-01-15T23:59:59Z",
  "user_id": "string",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "completed_at": null
}
```

### Task Status Options
- `por_hacer` - To Do
- `en_progreso` - In Progress
- `completada` - Completed

### Priority Levels
- `baja` - Low
- `media` - Medium
- `alta` - High

## 🔒 Authentication Flow

```bash
# 1. Register a new user
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'

# 2. Login to get tokens
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"

# 3. Use access token for authenticated requests
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 4. Refresh tokens when expired
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

## 🐛 Development & Debugging

```bash
# View container logs
docker-compose logs -f backend

# Access container shell
docker-compose exec backend bash

# Run tests inside container
docker-compose exec backend poetry run pytest

# Check database connection
docker-compose exec backend poetry run python test_config.py
```

## 📈 Performance Features

- **Database Indexing** - Optimized queries with proper MongoDB indexes
- **Async Operations** - Full async/await pattern for I/O operations
- **Connection Pooling** - Efficient database connection management
- **Pagination Support** - Built-in pagination for large datasets
- **Request Validation** - Fast input validation with Pydantic
- **In-Memory Testing** - Fast test execution with mongomock

## 🏗️ Project Highlights

### Architecture Patterns
- **Repository Pattern** - Clean separation of data access logic
- **Dependency Injection** - Modular and testable component design
- **Clean Architecture** - Well-organized layer separation
- **SOLID Principles** - Maintainable and extensible codebase

### Security Features
- **JWT Tokens** - Secure authentication with refresh token rotation
- **Password Hashing** - Bcrypt for secure password storage
- **Input Validation** - Comprehensive data validation
- **User Isolation** - Users can only access their own data
- **CORS Configuration** - Proper cross-origin request handling

### Testing Strategy
- **Comprehensive Coverage** - 99% test coverage
- **Fixture-Based Testing** - Reusable test components
- **In-Memory Database** - Fast and isolated test execution
- **Authentication Fixtures** - Simplified test setup
- **Integration Testing** - End-to-end API testing

## 🚢 Production Deployment

```bash
# Build production image
docker build -t taskmanager-backend .

# Run in production
docker run -p 8000:8000 \
  -e MONGODB_URL=mongodb://your-production-mongodb \
  -e SECRET_KEY=your-secure-secret-key \
  -e DEBUG=false \
  taskmanager-backend
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

---

**Built with ❤️ using FastAPI and modern Python practices** 