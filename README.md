<div align="center">
  <img src="frontend/src/assets/logo.png" alt="HireMinds Logo" width="120" />
  <h1>HireMinds: Multi-Agent AI Recruitment Platform</h1>
  <p><strong>Intelligent, autonomous recruitment powered by Large Language Models.</strong></p>

  <a href="https://multi-agent-ai-recruitment-platform.pages.dev">
    <img src="https://img.shields.io/badge/Live_Website-hireminds-00E5FF?style=for-the-badge&logo=cloudflare" alt="Live Website" />
  </a>
  <a href="https://github.com/daemon-Ad/Multi-Agent-AI-Recruitment-Platform">
    <img src="https://img.shields.io/badge/GitHub-Repository-181717?style=for-the-badge&logo=github" alt="GitHub Repo" />
  </a>
  <br />
  <img src="https://img.shields.io/badge/Angular-17+-DD0031?style=flat-square&logo=angular" alt="Angular" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi" alt="FastAPI" />
  <img src="https://img.shields.io/badge/PostgreSQL-336791?style=flat-square&logo=postgresql" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/Llama_3.1-Groq-FF5722?style=flat-square" alt="Groq Llama 3.1" />
  <img src="https://img.shields.io/badge/License-GPLv3-blue.svg?style=flat-square" alt="License: GPL v3" />
</div>

<br />

## 🌟 Overview

The **Multi-Agent AI Recruitment Platform** entirely streamlines the hiring process by intelligently parsing Job Descriptions and Candidate CVs, computing comprehensive Match Scores, and fully automating personalized interview scheduling using state-of-the-art Large Language Models (LLMs).

**Visit the live platform:** [https://hireminds.pages.dev](https://hireminds.pages.dev)

---

## 🚀 Key Features

### 📋 Job Management
- Upload raw Job Descriptions and have an AI Agent automatically summarize core requirements.
- Track all active job postings from a centralized dashboard.

### 👥 Candidate Parsing & Matching
- Upload candidate CVs (PDF) via drag-and-drop.
- **AI Match Engine**: Automatically computes a percentage-based match score prioritizing Skills, Experience, Education, and Keyword alignment.
- Sort and filter top candidates quickly with our Global Candidates Archive.

### 🤖 Autonomous Interview Scheduling
- **Interview Scheduler Agent**: Autonomously drafts hyper-personalized emails to candidates offering specific interview time slots.
- Context-aware email generation: Handles actions like postponing and cancelling interviews via natural language without relying on rigid, robotic templates.

### 🎨 State-of-the-art UI
- Built with an ultra-premium, dark-themed **Angular 17** interface.
- Utilizes dynamic visual features such as custom Canvas-based interactive background animations (Matrix Rain, Magnetic Fields, etc.).

---

## 🛠️ Tech Stack & Architecture

This application uses a fully decoupled 2-system architecture deployed across the edge.

| Component | Technology | Hosting |
| :--- | :--- | :--- |
| **Frontend** | Angular 17, TypeScript, SCSS | Cloudflare Pages |
| **Backend** | Python 3.12, FastAPI, Pydantic | Render |
| **Database** | PostgreSQL, SQLAlchemy ORM | Supabase |
| **AI Engine** | Llama 3.1 8B (via Groq API) | Groq Cloud |
| **PDF Extraction** | PyMuPDF | - |

---

## 💻 Local Setup and Installation

### Prerequisites
- Python 3.12+
- Node.js 18.0+
- Angular CLI
- API Key from Groq

### 1. Backend Setup
```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload
```
*The FastAPI application will start at `http://localhost:8000`.*

### 2. Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```
*The Angular application will start at `http://localhost:4200`.*

---

## 🔐 Environment Variables

Create a `.env` file in the `backend/` directory with the following contents:

```ini
DATABASE_URL="postgresql://user:password@your-database-host:5432/postgres"
SECRET_KEY="your-secure-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
GROQ_API_KEY="your-groq-api-key"
GROQ_MODEL="llama-3.1-8b-instant"
FRONTEND_URL="http://localhost:4200"
```

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0 (GPLv3)**. See the [LICENSE](LICENSE) file for more details.
