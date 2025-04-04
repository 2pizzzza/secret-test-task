# Disposable Secrets

A secure, one-time secret sharing service built with FastAPI, PostgreSQL, and Redis. This project implements a disposable secrets API where secrets are stored encrypted, accessible only once, and guaranteed to remain in the server cache for at least 5 minutes after creation, as per the technical specification.

## Features
- **One-time secrets**: Secrets can be retrieved only once and are marked as used afterward.
- **Server-side caching**: Secrets are stored in Redis with a minimum TTL of 5 minutes, even after retrieval or deletion.
- **Encryption**: All secrets and passphrases are encrypted using the `cryptography` library.
- **Passphrase protection**: Optional passphrase for secret deletion.
- **Logging**: All actions (creation, retrieval, deletion, expiration) are logged in PostgreSQL.
- **Background cleanup**: Expired secrets are automatically removed from the cache with logging.
- **No client-side caching**: HTTP headers prevent caching on the client or proxies.
- **Containerized**: Deployable with Docker and Docker Compose.

## Project Structure
```
.
├── app
│   ├── api
│   │   ├── __init__.py
│   │   └── v1
│   │       ├── __init__.py
│   │       └── secrets.py
│   ├── config.py
│   ├── __init__.py
│   ├── main.py
│   ├── models
│   │   ├── __init__.py
│   │   └── secret_log.py
│   ├── repository
│   │   ├── __init__.py
│   │   └── repository.py
│   └── services
│       ├── cache.py
│       ├── database.py
│       ├── encryption.py
│       ├── __init__.py
│       └── secret_service.py
├── docker-compose.yml
├── Dockerfile
├── README.md
├── requirements.txt
└── tests
    ├── __init__.py
    └── test_secrets.py

```

## Prerequisites
- **Python 3.9+**: For local development.
- **Docker**: For containerized deployment.

## Installation

### Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/2pizzzza/secret-test-task.git
   cd secret-test-task
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables in `.env` (example below):
   ```
   POSTGRES_HOST=localhost
   POSTGRES_PORT=5432
   POSTGRES_DB=secrets_db
   POSTGRES_USER=admin
   POSTGRES_PASSWORD=secretpassword
   REDIS_HOST=localhost
   REDIS_PORT=6379
   ```
5. Start PostgreSQL and Redis locally:
   - PostgreSQL: `sudo service postgresql start` (or equivalent).
   - Redis: `redis-server`.
6. Run the application:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```
   
The API will be available at `http://localhost:8000`.

## API Usage
The API is documented via Swagger at `http://localhost:8000/docs`. Below are the main endpoints with examples.

### 1. Create a Secret
- **Endpoint**: `POST /api/v1/secret`
- **Body**:
  ```json
  {
    "secret": "my_confidential_data",
    "passphrase": "my_passphrase",
    "ttl_seconds": 3600
  }
  ```
- **Response**:
  ```json
  {
    "secret_key": "550e8400-e29b-41d4-a716-446655440000"
  }
  ```

### 2. Retrieve a Secret
- **Endpoint**: `GET /api/v1/secret/{secret_key}`
- **Response** (first request):
  ```json
  {
    "secret": "my_confidential_data"
  }
  ```
- **Response** (subsequent requests):
  ```json
  {
    "detail": "Secret already retrieved or deleted"
  }
  ```

### 3. Delete a Secret
- **Endpoint**: `DELETE /api/v1/secret/{secret_key}`
- **Body** (if passphrase was set):
  ```json
  {
    "passphrase": "my_passphrase"
  }
  ```
- **Response**:
  ```json
  {
    "status": "secret deleted"
  }
  ```

#### Example with `curl`:
```bash
# Create secret
curl -X POST "http://localhost:8000/api/v1/secret" -H "Content-Type: application/json" -d '{"secret": "my_secret", "passphrase": "pass123", "ttl_seconds": 600}'

# Retrieve secret
curl "http://localhost:8000/api/v1/secret/550e8400-e29b-41d4-a716-446655440000"

# Delete secret
curl -X DELETE "http://localhost:8000/api/v1/secret/550e8400-e29b-41d4-a716-446655440000" -H "Content-Type: application/json" -d '{"passphrase": "pass123"}'
```

## Security
- **Encryption**: Secrets and passphrases are encrypted using Fernet (symmetric encryption).
- **No client caching**: Responses include headers `Cache-Control: no-cache, no-store, must-revalidate`, `Pragma: no-cache`, and `Expires: 0`.
- **Passphrase**: Optional protection for manual deletion.
- **TTL**: Minimum 5-minute cache retention, enforced even after retrieval or deletion.

## Logging
All actions are logged in PostgreSQL:
- **Table**: `secret_logs`
- **Fields**: `id`, `secret_key`, `action`, `ip_address`, `created_at`, `extra_data`.



