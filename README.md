# Multi-Agent AI Recruitment Platform 🚀

An intelligent, agent-driven platform for automated recruitment, candidate management, and hiring assistance.

## Table of Contents

- [Overview](#overview)  
- [Key Features](#key-features)  
- [Tech Stack](#tech-stack)  
- [Prerequisites](#prerequisites)  
- [Installation](#installation)  
- [Configuration](#configuration)  
- [Running the Application](#running-the-application)  
- [Agent System](#agent-system)  
- [Data Model](#data-model)  
- [Testing](#testing)  
- [Deployment](#deployment)  
- [Troubleshooting](#troubleshooting)  
- [License](#license)

## Overview

Multi-Agent AI Recruitment Platform is a comprehensive recruitment management system powered by intelligent agents. The platform automates key HR processes including job posting, candidate sourcing, resume screening, interview scheduling, and communication.

### Goals
- Streamline the hiring workflow
- Reduce time-to-hire
- Improve candidate experience
- Enable data-driven hiring decisions
- Automate repetitive HR tasks

## Key Features

### 📋 Job Management
- Create, edit, and manage job postings
- Categorize jobs by department, location, experience level
- Define job requirements and responsibilities
- Track job status (open, closed, on-hold)

### 👥 Candidate Management
- Centralized candidate database
- Detailed candidate profiles
- Skill and experience tracking
- Application history

### 🤖 Intelligent Agents
- **Resume Screening Agent**: Automatically screens resumes based on job requirements
- **Interview Scheduling Agent**: Coordinates interview schedules between candidates and hiring managers
- **Communication Agent**: Handles automated email and SMS communication
- **Analytics Agent**: Generates hiring insights and recommendations
- **Recruiter Assistant**: Supports recruiters with data and suggestions

### ⚙️ Workflow Automation
- End-to-end recruitment workflow automation
- Email/SMS notifications and reminders
- Automatic status updates
- Customizable workflows

### 📊 Analytics and Reporting
- Hiring pipeline visualization
- Time-to-hire metrics
- Candidate source effectiveness
- AI-powered hiring recommendations

### 🌐 Public Job Portal
- Publicly accessible job listings
- Online application submission
- Email notifications for new applications
- Candidate self-service

### 🔒 Security
- Role-based access control (Admin, HR, Recruiter, Hiring Manager)
- Secure authentication
- Data encryption
- Audit logging

## Tech Stack

### Backend
- **Language**: Python 3.10+
- **Framework**: FastAPI (async) 🚀
- **Database**: PostgreSQL
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Agent Framework**: CrewAI
- **Authentication**: JWT (python-jose)
- **Background Tasks**: Celery + Redis
- **Validation**: Pydantic

### Frontend
- **Framework**: Next.js (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context API
- **HTTP Client**: Axios

### Infrastructure
- **Web Server**: Nginx (optional for production)
- **Message Broker**: Redis
- **Containerization**: Docker
- **Container Orchestration**: Docker Compose

### Development Tools
- **Package Manager**: pip + npm/yarn
- **Code Quality**: Ruff, Black, isort
- **Type Checking**: Mypy
- **Testing**: pytest, httpx, requests
- **Linting**: ESLint, Stylelint

## Prerequisites

### Software Requirements
- Python 3.10 or higher
- Node.js 18.0 or higher
- PostgreSQL 13 or higher
- Redis 7.0 or higher
- Docker & Docker Compose (for containerized deployment)

### Hardware Requirements
- RAM: 4GB minimum (8GB recommended)
- Disk Space: 5GB free
- CPU: 2 cores minimum

## Installation

### Option 1: Containerized Deployment (Recommended)

1. **Clone the repository**
   ```bash
   git clone https://github.com/celestial/Multi-Agent-AI-Recruitment-Platform.git
   cd Multi-Agent-AI-Recruitment-Platform
   ```

2. **Create a .env file** (copy from .env.example)
   ```bash
   cp .env.example .env
   ```

3. **Configure environment variables** in .env

4. **Build and start containers**
   ```bash
   docker-compose up --build -d
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs

### Option 2: Local Development

1. **Backend Setup**

   ```bash
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   pip install -r requirements-dev.txt

   # Create database
   createdb recruitment

   # Run migrations (SQLModel)
   sqlmodel-alembic init
   sqlmodel-alembic upgrade head

   # Seed database (optional)
   python app/scripts/seed_admin.py
   ```

2. **Frontend Setup**

   ```bash
   # Install dependencies
   cd frontend
   npm install

   # Copy .env.local.example to .env.local
   cp .env.local.example .env.local
   ```

3. **Configure Environment Variables**

   Create `.env` files in both backend and frontend directories:

   **Backend (.env)**
   ```ini
   DATABASE_URL="postgresql://postgres:postgres@localhost:5432/recruitment"
   SECRET_KEY="your-secret-key"
   ALGORITHM="HS256"
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   REDIS_URL="redis://localhost:6379/0"
   ```

   **Frontend (.env.local)**
   ```ini
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Start Backend**

   ```bash
   uvicorn app.main:app --reload
   ```

5. **Start Frontend**

   ```bash
   cd frontend
   npm run dev
   ```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | PostgreSQL connection string |
| `SECRET_KEY` | Yes | Secret key for JWT signing |
| `ALGORITHM` | Yes | JWT signing algorithm |
| `REDIS_URL` | Yes | Redis connection string |
| `MAIL_USERNAME` | No | SMTP username |
| `MAIL_PASSWORD` | No | SMTP password |
| `MAIL_FROM` | No | Sender email |
| `MAIL_PORT` | No | SMTP port |
| `MAIL_SERVER` | No | SMTP server |
| `MAIL_STARTTLS` | No | Enable TLS |

### Agent Configuration

Agent behaviors can be configured in `app/agents/config.py`:

```python
# Resume Screening Agent configuration
SCREENING_RULES = {
    "min_experience_years": 2,
    "required_skills": ["python", "sql", "api"],
    "score_threshold": 60
}

# Interview Scheduling - buffer time between interviews
INTERVIEW_BUFFER_MINUTES = 15

# Communication templates location
EMAIL_TEMPLATES_DIR = "app/templates/emails"
```

## Running the Application

### Starting All Services (Containerized)
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Running Backend Separately
```bash
