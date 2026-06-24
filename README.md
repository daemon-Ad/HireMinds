# Multi-Agent AI Recruitment Platform 🚀

An intelligent, agent-driven platform for automated recruitment, candidate parsing, matching, and interview scheduling.

## Table of Contents

- [Overview](#overview)  
- [Key Features](#key-features)  
- [Tech Stack](#tech-stack)  
- [Project Structure](#project-structure)  
- [Setup and Installation](#setup-and-installation)  
- [Environment Variables](#environment-variables)  
- [Running the Application](#running-the-application)  

## Overview

The Multi-Agent AI Recruitment Platform streamlines the hiring process by intelligently parsing Job Descriptions and Candidate CVs, computing comprehensive Match Scores, and fully automating personalised interview scheduling using Large Language Models (LLMs). 

### Goals
- Fully parse and extract actionable criteria from Job Descriptions (JDs)
- Ingest applicant CVs (PDFs) and extract relevant skills and experience
- Generate automated, data-driven candidate match scores
- Schedule, postpone, and cancel interviews dynamically using AI-generated emails

## Key Features

### 📋 Job Management
- Upload raw Job Descriptions and have an AI Agent summarize requirements.
- Track all active job postings from a centralized dashboard.

### 👥 Candidate Parsing & Matching
- Upload candidate CVs (PDF) via drag-and-drop.
- **AI Match Engine**: Automatically computes a percentage-based match score prioritizing Skills, Experience, Education, and Keyword alignment.
- Sort and filter top candidates quickly.
- Global Candidates Archive to maintain past applicant data.

### 🤖 LLM-Powered Interview Scheduling
- **Interview Scheduler Agent**: Autonomously drafts hyper-personalized emails to candidates offering specific interview time slots.
- Handles context-aware actions like postponing and cancelling interviews via natural language emails without relying on rigid templates.

### 🎨 State-of-the-art UI
- Built with an ultra-premium, dark-themed **Angular 17** interface.
- Utilizes dynamic visual features such as custom Canvas-based interactive background animations (Matrix Rain, Magnetic Fields, etc.).

## Tech Stack

### Backend
- **Language**: Python 3.12+
- **Framework**: FastAPI
- **Database**: SQLite / PostgreSQL (via SQLAlchemy)
- **AI / LLM Integration**: Groq API (Llama 3.1) 
- **PDF Extraction**: PyMuPDF
- **Validation**: Pydantic

### Frontend
- **Framework**: Angular 17
- **Language**: TypeScript
- **Styling**: SCSS (Custom Design System with Glassmorphism)

## Project Structure

- `backend/`: FastAPI backend containing routers, services, DB models, and the AI Agents (`cv_parser`, `interview_scheduler`, `jd_summarizer`, `matching_engine`).
- `frontend/`: Angular 17 web application containing UI features, global state, API interceptors, and components.

## Setup and Installation

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
```

### 2. Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install
```

## Environment Variables

Create a `.env` file in the `backend/` directory with the following contents:

```ini
DATABASE_URL="sqlite:///./recruitment.db"
SECRET_KEY="your-secure-secret-key"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440
GROQ_API_KEY="your-groq-api-key"
GROQ_MODEL="llama-3.1-8b-instant"
```

## Running the Application

### Start the Backend
From the `backend/` directory, ensure your virtual environment is activated and run:
```bash
uvicorn app.main:app --reload
```
The FastAPI application will start at `http://localhost:8000`. You can access the automatic Swagger documentation at `http://localhost:8000/docs`.

### Start the Frontend
From the `frontend/` directory, run:
```bash
npm start
```
The Angular application will start at `http://localhost:4200`.

Open your browser and navigate to the frontend URL to start using the platform!
