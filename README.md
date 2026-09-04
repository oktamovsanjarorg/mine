# Sanjar Bot 🤖

All-in-one personal Telegram bot built with modern async Python.

## 🚀 Features

- **Asynchronous Processing**: Fast, non-blocking I/O using `aiogram 3.x` and `asyncio`.
- **Database**: PostgreSQL with `SQLAlchemy 2.0` (async) and `alembic` for migrations.
- **Caching & FSM**: Redis for fast storage and Finite State Machine persistence.
- **Media Storage**: MinIO (S3-compatible) for handling files and images.
- **AI Integration**: Support for OpenAI and Google Gemini APIs.
- **Scheduling**: Job scheduling with `apscheduler`.
- **Dockerized**: Easy deployment with `docker-compose`.

## 🛠 Tech Stack

- **Python**: 3.12+
- **Bot Framework**: aiogram 3.x
- **Database**: PostgreSQL + SQLAlchemy + asyncpg
- **Migrations**: Alembic
- **Caching**: Redis
- **Storage**: MinIO
- **Validation**: Pydantic v2
- **Linting & Formatting**: Ruff, MyPy

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/your-username/sanjar-bot.git
cd sanjar-bot
```

### 2. Environment Variables
Copy the example environment file and fill in your values:
```bash
cp .env.example .env
# Edit .env with your favorite editor
```

### 3. Running with Docker (Recommended)
Make sure you have Docker and Docker Compose installed.

**Development mode:**
```bash
make up
```

**Production mode:**
```bash
make up-prod
```

### 4. Database Migrations
Apply migrations to create the database schema:
```bash
make migrate
```

## 📖 Usage Guide

Check the available Makefile commands for daily development tasks:
```bash
make help
```

## 📝 License
MIT
