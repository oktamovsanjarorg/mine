# Deployment Guide

This guide covers deploying SanjarBot using Docker Compose.

## Prerequisites
- Docker and Docker Compose plugin installed.
- A registered Telegram Bot Token.
- Domain name with SSL for webhooks.

## Steps

1. **Clone the repository:**
   ```bash
   git clone <repo-url> /opt/sanjar-bot
   cd /opt/sanjar-bot
   ```

2. **Configure environment:**
   Copy `.env.example` to `.env` and fill in the required variables (Tokens, DB passwords, etc.).

3. **Start the services:**
   ```bash
   docker compose up -d
   ```

4. **Reverse Proxy (Nginx):**
   Set up Nginx to proxy requests to port `8000` for the webhook and API, ensuring you configure Let's Encrypt SSL certificates using `certbot`.

5. **Backups:**
   Ensure `backup.yml` CI workflow is active or set up a cron job on the host machine to dump the PostgreSQL database daily.
