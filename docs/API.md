# API Documentation

SanjarBot includes a FastAPI web application to handle webhooks and serve an admin/monitoring API.

## Endpoints

### `GET /health`
Returns the health status of the application, database, and Redis.

**Response:**
```json
{
  "status": "ok",
  "database": "connected",
  "redis": "connected"
}
```

### `GET /metrics`
Exposes Prometheus metrics for scraping.

### `POST /webhook`
Endpoint for receiving Telegram Webhook updates.

### `GET /api/v1/admin/users`
Returns a list of users.
**Requires Auth Header:** `Authorization: Bearer <ADMIN_TOKEN>`
