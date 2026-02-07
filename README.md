# YT-Insight - Backend API

RESTful backend API for a YouTube Analytics SaaS platform that provides AI-powered insights and analytics for YouTube channels and videos. Built as an educational project for BIL-316 Database Management Systems II.

## 📋 Project Information

**Course:** BIL-316 – Database Management Systems II, 2025-2026 Spring

**Team Members:**
- Daniel Kanybekov (2204.01002)
- Beksultan Egemberdiev (2204.01023)
- Nurayim Kerimova (2104.01005)

## 🎯 Project Overview

YT-Insight Backend is a RESTful API that powers a YouTube analytics platform. The API handles user authentication, YouTube data integration, AI-powered analysis, and subscription management.

### Key Features

- 🔐 JWT-based authentication and authorization
- 📊 YouTube Data API integration for channel/video analysis
- 🤖 AI-powered insights and data interpretation
- 💬 Comment metadata and sentiment analysis
- 📈 Analysis history and tracking
- 💳 Subscription management with usage limits
- 🔄 RESTful API endpoints

## 🛠️ Technology Stack

- **Framework:** Django REST Framework (Python)
- **Database:** PostgreSQL
- **Authentication:** JWT (JSON Web Tokens)
- **External APIs:** 
  - YouTube Data API v3
  - AI-based analysis agents
- **Version Control:** GitHub
- **Project Management:** Jira
- **Development Approach:** Sprint-based workflow

## 📊 Database Schema

The application uses PostgreSQL with the following normalized schema:

### Entity Relationship Diagram

```dbml
Table users {
  id uuid [pk]
  email varchar [unique, not null]
  password_hash varchar
  created_at timestamp
}

Table subscriptions {
  id uuid [pk]
  user_id uuid [ref: > users.id]
  stripe_subscription_id varchar
  plan varchar  // free, basic, pro
  status varchar // active, canceled
  current_period_end timestamp
}

Table youtube_analyses {
  id uuid [pk]
  user_id uuid [ref: > users.id]
  youtube_type varchar // channel | video
  youtube_id varchar
  title varchar
  summary text
  created_at timestamp
}

Table analysis_questions {
  id uuid [pk]
  analysis_id uuid [ref: > youtube_analyses.id]
  question text
  answer text
  created_at timestamp
}

Table usage_limits {
  id uuid [pk]
  user_id uuid [ref: > users.id]
  videos_analyzed int
  reset_at timestamp
}
```

### Table Descriptions

**users**
- Stores user account information with hashed passwords
- Primary authentication entity
- Email is unique identifier

**subscriptions**
- Manages user subscription tiers (free, basic, pro)
- Integrates with Stripe for payment processing
- Tracks subscription status and billing cycles

**youtube_analyses**
- Stores analysis results for YouTube channels and videos
- Links each analysis to the requesting user
- Contains AI-generated summaries and metadata

**analysis_questions**
- Stores Q&A pairs generated from video/channel analysis
- Enables conversational insights exploration
- Many-to-one relationship with analyses

**usage_limits**
- Enforces plan-based API usage restrictions
- Tracks monthly analysis counts per user
- Automatic reset mechanism based on subscription cycle

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher
- PostgreSQL 14 or higher
- pip (Python package manager)
- Git
- YouTube Data API key
- (Optional) Stripe account for subscription features

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd yt-insight-backend
```

2. **Create and activate virtual environment**
```bash
python -m venv venv

# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up PostgreSQL database**
```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE yt_insight;

# Create user (optional)
CREATE USER yt_insight_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE yt_insight TO yt_insight_user;
```

5. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env file with your configuration (see below)
```

6. **Run database migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Create superuser**
```bash
python manage.py createsuperuser
```

8. **Start development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

### Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=yt_insight
DB_USER=yt_insight_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Or use DATABASE_URL (alternative)
# DATABASE_URL=postgresql://yt_insight_user:your_password@localhost:5432/yt_insight

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# YouTube API
YOUTUBE_API_KEY=your-youtube-api-key-here

# AI Analysis Service
AI_SERVICE_API_URL=https://api.example.com
AI_SERVICE_API_KEY=your-ai-service-api-key

# Stripe (for subscriptions)
STRIPE_PUBLIC_KEY=pk_test_your_stripe_public_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# CORS Settings (if frontend is on different domain)
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080
```

## 📁 Project Structure

```
yt-insight-backend/
├── config/                 # Настройки проекта (settings, wsgi, asgi)
├── apps/                   # Django приложения (разделение по доменам)
│   ├── users/              # Бывший 'accounts'. Всё про юзеров и аутентификацию
│   ├── subscriptions/      # Бывший 'billing'. Планы, Stripe, лимиты
│   └── analysis/           # Основное ядро: YouTube, AI, История
├── services/               # <--- САМОЕ ВАЖНОЕ: Чистая бизнес-логика
│   ├── youtube/            # Клиент для YouTube Data API
│   ├── ai/                 # Клиент для OpenAI/Claude/Gemini
│   └── payment/            # Логика работы со Stripe
├── shared/                 # Общие утилиты
│   ├── models.py           # Базовые абстрактные модели (UUID, Timestamps)
│   ├── mixins.py           # Полезные миксины
│   └── exceptions.py       # Кастомные ошибки
├── requirements.txt
├── manage.py
└── .env
```

## 🔌 API Endpoints

Base URL: `http://localhost:8000/api/v1/`

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user account | No |
| POST | `/auth/login` | Login and receive JWT tokens | No |
| POST | `/auth/refresh` | Refresh access token | No |
| POST | `/auth/logout` | Invalidate refresh token | Yes |
| POST | `/auth/password-reset` | Request password reset | No |
| POST | `/auth/password-reset/confirm` | Confirm password reset | No |

### User Management Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/users/profile` | Get current user profile | Yes |
| PUT | `/users/profile` | Update user profile | Yes |
| PATCH | `/users/profile` | Partial update user profile | Yes |
| DELETE | `/users/profile` | Delete user account | Yes |
| GET | `/users/subscription` | Get subscription details | Yes |
| GET | `/users/usage` | Get usage statistics | Yes |

### YouTube Analysis Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/analyses` | Submit YouTube URL for analysis | Yes |
| GET | `/analyses` | List user's analysis history | Yes |
| GET | `/analyses/{id}` | Get specific analysis details | Yes |
| DELETE | `/analyses/{id}` | Delete an analysis | Yes |
| GET | `/analyses/{id}/questions` | Get Q&A for an analysis | Yes |
| POST | `/analyses/{id}/questions` | Ask new question about analysis | Yes |

### Subscription Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/subscriptions/plans` | List available plans | No |
| POST | `/subscriptions/checkout` | Create Stripe checkout session | Yes |
| POST | `/subscriptions/cancel` | Cancel subscription | Yes |
| POST | `/subscriptions/webhook` | Stripe webhook handler | No |

### Request/Response Examples

#### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securePassword123",
  "confirm_password": "securePassword123"
}
```

Response:
```json
{
  "id": "uuid-here",
  "email": "user@example.com",
  "created_at": "2026-02-06T10:30:00Z",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Submit Analysis
```http
POST /api/v1/analyses
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "analysis_type": "video"
}
```

Response:
```json
{
  "id": "uuid-here",
  "youtube_type": "video",
  "youtube_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "summary": "AI-generated summary of the video...",
  "created_at": "2026-02-06T10:35:00Z",
  "status": "completed"
}
```

## 📝 Development Workflow

### Sprint-Based Development

1. **Sprint Planning** - Weekly sprint planning meetings
2. **Task Assignment** - Tasks tracked in Jira
3. **Development** - Feature branches for each task
4. **Code Review** - Pull requests reviewed by team members
5. **Testing** - Unit and integration tests
6. **Documentation** - Sprint reports and documentation updates

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Description of changes"

# Push to repository
git push origin feature/your-feature-name

# Create pull request for review
```

## 🧪 Testing

### Run All Tests
```bash
python manage.py test
```

### Run Specific App Tests
```bash
# Test authentication app
python manage.py test apps.authentication

# Test YouTube analysis app
python manage.py test apps.youtube_analysis

# Test subscriptions app
python manage.py test apps.subscriptions
```

### Run Tests with Coverage
```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test

# Generate coverage report
coverage report

# Generate HTML coverage report
coverage html
```

### Code Quality

```bash
# Install development dependencies
pip install flake8 black isort pylint

# Run linting
flake8 .

# Format code with black
black .

# Sort imports
isort .

# Run pylint
pylint apps/
```

### Test Database Setup

Tests automatically use a separate test database. Configure in `settings.py`:

```python
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'test_yt_insight',
    }
```

## 📚 Documentation

- [API Documentation](docs/api_documentation.md)
- [Database Schema](docs/database_schema.md)
- [Sprint Reports](docs/sprint_reports/)
- [Development Guide](docs/development_guide.md)

## 🏗️ Core Components

### Django Models

**User Model** (`apps/users/models.py`)
```python
- Custom user model extending AbstractBaseUser
- UUID primary key
- Email-based authentication
- Password hashing with Django's built-in methods
```

**Subscription Model** (`apps/subscriptions/models.py`)
```python
- Links to User model
- Stripe integration fields
- Plan tier management (free, basic, pro)
- Status tracking (active, canceled, expired)
```

**YouTubeAnalysis Model** (`apps/youtube_analysis/models.py`)
```python
- Stores analysis results
- Supports both channel and video analysis
- Contains AI-generated summaries
- Tracks analysis creation time
```

### Services Layer

**YouTube Client** (`services/youtube_client.py`)
```python
- Interfaces with YouTube Data API v3
- Fetches channel metadata
- Retrieves video information
- Handles comment extraction
- Rate limiting and error handling
```

**AI Analysis Service** (`services/ai_analysis.py`)
```python
- Processes YouTube data
- Generates insights and summaries
- Creates Q&A pairs
- Handles sentiment analysis
```

**Stripe Client** (`services/stripe_client.py`)
```python
- Manages subscription lifecycle
- Handles webhook events
- Processes payments
- Updates subscription status
```

## 🔒 Authentication & Authorization

### JWT Token Flow

1. User registers or logs in
2. Server generates access token (60 min) and refresh token (7 days)
3. Client includes access token in Authorization header
4. When access token expires, use refresh token to get new access token
5. Refresh token rotation on each use

### Token Format
```
Authorization: Bearer <access_token>
```

### Protected Routes

All endpoints except authentication and public plan listings require JWT authentication.

## 📊 Database Management

### Migrations

```bash
# Create new migration after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Show migration status
python manage.py showmigrations

# Rollback migration
python manage.py migrate app_name migration_name
```

### Database Backup

```bash
# Backup database
pg_dump -U yt_insight_user yt_insight > backup.sql

# Restore database
psql -U yt_insight_user yt_insight < backup.sql
```

### Seeding Data

```bash
# Create custom management command
python manage.py seed_database

# Or use fixtures
python manage.py loaddata initial_data.json
```

## 📦 Dependencies

Main dependencies included in `requirements.txt`:

```
Django>=4.2.0
djangorestframework>=3.14.0
psycopg2-binary>=2.9.0
PyJWT>=2.8.0
django-cors-headers>=4.0.0
python-dotenv>=1.0.0
google-api-python-client>=2.0.0
stripe>=5.0.0
celery>=5.3.0
redis>=4.5.0
gunicorn>=20.1.0
```

Development dependencies:
```
black>=23.0.0
flake8>=6.0.0
isort>=5.12.0
pylint>=2.17.0
coverage>=7.2.0
pytest>=7.3.0
pytest-django>=4.5.0
```

## 🚀 Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in settings
- [ ] Configure allowed hosts
- [ ] Set up PostgreSQL production database
- [ ] Configure static files serving
- [ ] Set up environment variables securely
- [ ] Enable HTTPS
- [ ] Configure CORS properly
- [ ] Set up logging
- [ ] Configure email backend
- [ ] Set up database backups
- [ ] Configure Celery for background tasks
- [ ] Set up monitoring and error tracking

### Deployment Options

**Option 1: Railway**
```bash
railway login
railway init
railway up
```

**Option 2: Heroku**
```bash
heroku login
heroku create yt-insight-api
heroku addons:create heroku-postgresql:hobby-dev
git push heroku main
```

**Option 3: Docker**
```bash
docker build -t yt-insight-backend .
docker run -p 8000:8000 yt-insight-backend
```

## 🎓 Learning Objectives

This project demonstrates practical application of:

### Database Management
- PostgreSQL database design and normalization
- Foreign key relationships and data integrity
- Database migrations with Django ORM
- Query optimization and indexing
- Transaction management

### Backend Development
- RESTful API design principles
- Django REST Framework implementation
- JWT authentication and authorization
- External API integration (YouTube Data API)
- Service-oriented architecture

### Software Engineering Practices
- Version control with Git
- Sprint-based development methodology
- Code review and collaboration
- Testing (unit and integration tests)
- Documentation and API specifications

### Security Best Practices
- Password hashing and storage
- JWT token management
- CORS configuration
- Input validation and sanitization
- Rate limiting and usage controls

## 🔧 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check PostgreSQL is running
sudo service postgresql status

# Check database exists
psql -U postgres -l

# Verify credentials in .env file
```

**Migration Errors**
```bash
# Reset migrations (development only!)
python manage.py migrate --fake app_name zero
python manage.py migrate app_name

# Or delete migrations and recreate
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

**JWT Token Issues**
```bash
# Verify JWT_SECRET_KEY is set in .env
# Check token expiration times
# Clear browser/client token storage
```

**YouTube API Quota Exceeded**
```bash
# Monitor quota in Google Cloud Console
# Implement caching to reduce API calls
# Use exponential backoff for retries
```

## 🤝 Contributing

This is an educational project. Team members should:

1. Follow the established coding standards
2. Write meaningful commit messages
3. Create pull requests for all changes
4. Document new features and APIs
5. Update sprint reports regularly

## 📄 License

This project is created for educational purposes as part of BIL-316 Database Management Systems II course requirements.

## 🙏 Acknowledgments

- BIL-316 Course Instructor and Teaching Assistants
- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [YouTube Data API Documentation](https://developers.google.com/youtube/v3)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- Django and Python Communities

## 📞 Contact

For questions or issues related to this project:
- Create an issue in the GitHub repository
- Contact team members through the course platform
- Email: [Add team email if applicable]

## 📈 Project Status

**Current Sprint:** [Sprint Number]  
**Last Updated:** February 2026  
**Status:** In Development

---

**⚠️ Educational Project Notice**

This is an educational project developed for BIL-316 Database Management Systems II course. It is not intended for production use without proper security audits, comprehensive testing, and additional features implementation.