# TaskHub - Task & Project Management System

TaskHub is a RESTful API for managing workspaces, projects,
tasks, labels, comments and team collaboration.

The application is built with FastAPI, PostgreSQL and
asynchronous SQLAlchemy, following a layered architecture
to improve maintainability, scalability and separation
of concerns.

## Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Local Development](#local-development)
- [Running with Docker](#running-with-docker)
- [Database Migration](#database-migration)
- [Authentication and Authorization](#authentication-and-authorization)
- [Search, Filtering and Pagination](#search-filtering-and-pagination)
- [Redis Caching](#redis-caching)
- [Error Handling](#error-handling)
- [API Documentation](#api-documentation)
- [Code Quality](#code-quality)
- [Docker Management](#docker-management)
- [Troubleshooting](#troubleshooting)

## Features

### Authentication and User Management

- User registration and login.
- JWT-based authentication.
- Access token and refresh token management.
- Secure password hashing using Argon2.
- User profile management.
- User and administrator roles.

### Workspace Management

- Create, retrieve, update and delete workspaces.
- Manage workspace members.
- Assign roles to workspace members.
- Control access to workspace resources.
- Search, filter and paginate workspaces.

### Project Management

- Create and manage projects within workspaces.
- Update project information and status.
- Archive and restore projects.
- Search, filter and paginate projects.
- Workspace-based access control.

### Task Management

- Create, retrieve, update and delete tasks.
- Manage task status and priority.
- Assign tasks to users.
- Manage task deadlines.
- Associate labels with tasks.
- Search, filter and paginate tasks.

### Label Management

- Create, retrieve, update and delete labels.
- Organize tasks using labels.
- Associate multiple labels with a task.

### Comment Management

- Create, retrieve, update and delete task comments.
- Support collaboration and discussion within tasks.
- Filter and paginate comments.

### Security and Authorization

- JWT-based authentication.
- Role-Based Access Control (RBAC).
- Resource-level permission validation.
- Request data validation using Pydantic.
- Centralized exception handling.
- Environment-based configuration.
- Sensitive configuration management through environment variables.

### Performance and Deployment

- Asynchronous database operations.
- Database connection pooling.
- Database indexing.
- Redis caching with TTL.
- Cache invalidation after data modifications.
- Multi-stage Docker build.
- Docker Compose service orchestration.
- Automatic database migration on startup.
- Persistent PostgreSQL storage.
- Service health checks.
- Non-root Docker runtime user.

## Technology Stack

| Category | Technology |
| --- | --- |
| Programming Language | Python 3.13 |
| Web Framework | FastAPI |
| ASGI Server | Uvicorn |
| Database | PostgreSQL 17 |
| ORM | SQLAlchemy Async |
| Database Driver | asyncpg |
| Database Migration | Alembic |
| Data Validation | Pydantic v2 |
| Configuration | Pydantic Settings |
| Authentication | JWT, PyJWT |
| Password Hashing | pwdlib, Argon2 |
| Authorization | RBAC |
| Caching | Redis 8 |
| Package Management | uv |
| API Documentation | Swagger UI, OpenAPI, ReDoc |
| Code Quality | Ruff |
| Containerization | Docker, Docker Compose |
| Version Control | Git, GitHub |

## System Architecture

TaskHub follows a layered architecture to separate
HTTP request handling, business logic and data access.

```text
Client
  |
  v
FastAPI Router
  |
  v
Service Layer --------> Redis Cache
  |
  v
Repository Layer
  |
  v
SQLAlchemy Async
  |
  v
PostgreSQL
```

### Router Layer

- Defines RESTful API endpoints.
- Receives and validates incoming requests.
- Handles HTTP request and response processing.
- Injects required dependencies.
- Delegates business operations to the service layer.

### Service Layer

- Implements business logic.
- Validates business rules.
- Handles authorization and resource permissions.
- Coordinates repository operations.
- Manages cache retrieval and invalidation.

### Repository Layer

- Handles database access.
- Executes asynchronous SQLAlchemy queries.
- Supports CRUD operations.
- Implements searching, filtering and pagination.
- Separates database operations from business logic.

### Model Layer

- Defines SQLAlchemy ORM models.
- Represents database tables and relationships.
- Defines database constraints and indexes.

### Schema Layer

- Defines request and response schemas.
- Validates incoming data using Pydantic.
- Controls API response serialization.
- Separates API data structures from database models.

### Dependency Injection

FastAPI Dependency Injection is used to manage:

- Database sessions.
- Authentication.
- Current user information.
- Authorization.
- Service and repository dependencies.
- Redis cache services.

## Project Structure

```text
TaskHub/
├── app/
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── users.py
│   │           ├── workspaces.py
│   │           ├── projects.py
│   │           ├── tasks.py
│   │           ├── labels.py
│   │           └── comments.py
│   ├── core/
│   ├── db/
│   │   ├── session.py
│   │   └── redis.py
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   └── main.py
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

## Getting Started

TaskHub supports two development environments:

- Local development using Python and uv.
- Containerized development using Docker Compose.

### Prerequisites

For local development:

- Python 3.13 or later.
- uv package manager.
- PostgreSQL.
- Redis.
- Git.

For Docker development:

- Docker Engine or Docker Desktop.
- Docker Compose v2.
- Git.

### Clone the Repository

```bash
git clone https://github.com/huynhdoanthanhtuyen/TaskHub.git
cd TaskHub
```

## Environment Variables

Create a `.env` file from the provided template:

```bash
cp .env.example .env
```

Configure the environment variables according to your
development environment.

### Application Configuration

```env
APP_NAME=TaskHub API
APP_VERSION=0.1.0
APP_ENV=development
DEBUG=False
LOG_LEVEL=INFO
DOCS_ENABLED=True
```

### Database Configuration

```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/taskhub_db
```

Replace `YOUR_PASSWORD` with your local PostgreSQL password.

### Authentication Configuration

```env
SECRET_KEY=YOUR_SECRET_KEY_AT_LEAST_32_CHARACTERS
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Generate a secure secret key using Python:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Redis Configuration

```env
REDIS_URL=redis://127.0.0.1:6379/0
CACHE_ENABLED=True
CACHE_TTL_SECONDS=300
REDIS_TIMEOUT_SECONDS=2.0
```

### Docker PostgreSQL Configuration

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_DOCKER_DB_PASSWORD
POSTGRES_DB=taskhub_db
```

These variables are used by Docker Compose to initialize
the PostgreSQL container.

Use a strong, URL-safe password for `POSTGRES_PASSWORD`.

### Environment Variable Reference

| Variable | Description | Default / Example |
| --- | --- | --- |
| APP_NAME | Application name | TaskHub API |
| APP_VERSION | Application version | 0.1.0 |
| APP_ENV | Application environment | development |
| DEBUG | Enable debug mode | False |
| LOG_LEVEL | Application logging level | INFO |
| DOCS_ENABLED | Enable API documentation | True |
| DATABASE_URL | PostgreSQL connection URL | Required |
| SECRET_KEY | JWT signing secret | Required |
| JWT_ALGORITHM | JWT signing algorithm | HS256 |
| ACCESS_TOKEN_EXPIRE_MINUTES | Access token lifetime | 30 |
| REFRESH_TOKEN_EXPIRE_DAYS | Refresh token lifetime | 7 |
| REDIS_URL | Redis connection URL | redis://127.0.0.1:6379/0 |
| CACHE_ENABLED | Enable Redis caching | True |
| CACHE_TTL_SECONDS | Cache expiration time | 300 |
| REDIS_TIMEOUT_SECONDS | Redis connection and operation timeout | 2.0 |
| POSTGRES_USER | Docker database username | postgres |
| POSTGRES_PASSWORD | Docker database password | Required for Docker |
| POSTGRES_DB | Docker database name | taskhub_db |

### Supported Environments

| Environment | Purpose |
| --- | --- |
| development | Local development and debugging |
| testing | Application testing |
| production | Production deployment configuration |

The application validates environment configuration
during startup.

Debug mode must be disabled in the production environment.

Example production configuration:

```env
APP_ENV=production
DEBUG=False
LOG_LEVEL=INFO
DOCS_ENABLED=False
```

Production deployment requires additional infrastructure
and security configuration beyond these environment settings.

### Security Notes

- Never commit the `.env` file to version control.
- Use `.env.example` as the configuration template.
- Use strong and unique passwords.
- Use a secure JWT secret key.
- Do not expose sensitive environment variables in logs.
- Disable debug mode in production.

## Local Development

### 1. Install Dependencies

Install project dependencies using uv:

```bash
uv sync --locked
```

The `uv.lock` file ensures consistent dependency versions
across development environments.

### 2. Create PostgreSQL Database

Connect to PostgreSQL and create the database:

```sql
CREATE DATABASE taskhub_db;
```

Update `DATABASE_URL` in `.env` with the correct
database credentials.

### 3. Start Redis

If Redis is not installed locally, it can be started
using Docker:

```bash
docker run -d \
  --name taskhub-redis \
  -p 127.0.0.1:6379:6379 \
  redis:8-alpine
```

If the container already exists, start it using:

```bash
docker start taskhub-redis
```

Verify the Redis connection:

```bash
docker exec taskhub-redis redis-cli ping
```

Expected response:

```text
PONG
```

### 4. Apply Database Migrations

```bash
uv run alembic upgrade head
```

### 5. Start the Application

```bash
uv run uvicorn app.main:app --reload
```

The application is available at:

```text
http://localhost:8000
```

### 6. Verify the Application

```bash
curl http://localhost:8000/
```

Expected response:

```json
{
    "message": "Welcome to TaskHub API"
}
```

## Running with Docker

TaskHub provides Docker and Docker Compose configuration
to simplify application setup and ensure a consistent
development environment.

### Docker Architecture

```text
Client / Swagger UI
         |
         | localhost:8000
         v
+-------------------------------------------+
|            Docker Network                 |
|                                           |
|          +-------------------+            |
|          |      FastAPI      |            |
|          |    taskhub-api    |            |
|          |       :8000       |            |
|          +-------------------+            |
|              |          |                 |
|              v          v                 |
|       +----------+  +----------+          |
|       |PostgreSQL|  |  Redis   |          |
|       |    db    |  |  redis   |          |
|       |  :5432   |  |  :6379   |          |
|       +----------+  +----------+          |
|              |                            |
+--------------|----------------------------+
               v
        postgres-data
        Persistent Volume
```

### Multi-stage Docker Build

The Dockerfile uses two build stages.

#### Builder Stage

- Uses Python 3.13 slim as the base image.
- Installs uv for dependency management.
- Installs production dependencies from `uv.lock`.
- Excludes development dependencies.
- Creates an isolated Python virtual environment.
- Compiles Python bytecode.

#### Runtime Stage

- Uses a lightweight Python base image.
- Copies installed dependencies from the builder stage.
- Copies application source code.
- Includes Alembic migration files.
- Runs the application as a non-root user.
- Exposes application port 8000.

### Docker Compose Services

| Service | Container Name | Image | Port |
| --- | --- | --- | --- |
| app | taskhub-api | taskhub-api:latest | 8000 |
| db | taskhub-db | postgres:17-alpine | 5432 (internal) |
| redis | taskhub-cache | redis:8-alpine | 6379 (internal) |

PostgreSQL and Redis communicate with the application
through an internal Docker bridge network.

Only the FastAPI port is published to the host,
using the loopback address `127.0.0.1`.

### 1. Verify Docker Installation

```bash
docker --version
docker compose version
```

Ensure Docker Desktop or Docker Engine is running.

### 2. Configure Environment Variables

Create `.env` if it does not already exist:

```bash
cp .env.example .env
```

Configure the following variables:

```env
POSTGRES_USER=postgres
POSTGRES_PASSWORD=YOUR_DOCKER_DB_PASSWORD
POSTGRES_DB=taskhub_db
SECRET_KEY=YOUR_SECRET_KEY_AT_LEAST_32_CHARACTERS
```

Docker Compose automatically overrides the application
connection URLs using the internal service names:

```text
PostgreSQL: db:5432
Redis: redis:6379
```

The local database and Redis URLs in `.env` can remain
unchanged when switching between local and Docker development.

### 3. Build and Start Containers

Run the following command from the project root:

```bash
docker compose up -d --build
```

Docker Compose performs the following operations:

1. Builds the FastAPI Docker image.
2. Creates the Docker network.
3. Creates the PostgreSQL volume.
4. Starts PostgreSQL and Redis.
5. Waits for PostgreSQL and Redis health checks.
6. Starts the FastAPI container.
7. Applies database migrations.
8. Starts the Uvicorn application server.

### 4. Check Container Status

```bash
docker compose ps -a
```

Expected service status:

| Container | Status |
| --- | --- |
| taskhub-api | Running |
| taskhub-db | Healthy |
| taskhub-cache | Healthy |

### 5. Check Application Logs

```bash
docker compose logs app
```

The application logs should indicate that database
migration and application startup have completed.

### 6. Verify the Application

```bash
curl http://localhost:8000/
```

Expected response:

```json
{
    "message": "Welcome to TaskHub API"
}
```

Access Swagger UI:

```text
http://localhost:8000/docs
```

### 7. Verify PostgreSQL

Check the current migration version:

```bash
docker compose exec app alembic current
```

List database tables using the default database credentials:

```bash
docker compose exec db psql -U postgres -d taskhub_db -c "\dt"
```

### 8. Verify Redis

```bash
docker compose exec redis redis-cli ping
```

Expected response:

```text
PONG
```

### 9. Verify Runtime Image

Check the application image:

```bash
docker images taskhub-api
```

Check the Python version:

```bash
docker compose exec app python --version
```

Check the runtime user:

```bash
docker compose exec app whoami
```

Expected runtime user:

```text
appuser
```

Verify installed dependencies:

```bash
docker compose exec app python -c "import fastapi, sqlalchemy, asyncpg, redis; print('All dependencies imported successfully')"
```

## Database Migration

TaskHub uses Alembic to manage database schema changes
and maintain database version history.

### Create a Migration

After modifying SQLAlchemy models:

```bash
uv run alembic revision --autogenerate -m "migration description"
```

Review the generated migration file before applying it.

### Apply Migrations

```bash
uv run alembic upgrade head
```

### Check Current Revision

```bash
uv run alembic current
```

### View Migration History

```bash
uv run alembic history
```

### Check for Pending Schema Changes

```bash
uv run alembic check
```

### Roll Back the Latest Migration

```bash
uv run alembic downgrade -1
```

Review the migration and back up important data before
performing a downgrade.

### Automatic Migration in Docker

When the application container starts, Docker Compose
automatically executes:

```bash
alembic upgrade head
```

Uvicorn starts only after the migration succeeds.

The startup command is equivalent to:

```bash
alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000
```

For manual migration inside a running container:

```bash
docker compose exec app alembic upgrade head
```

Automatic startup migration is intended for the current
single-application-container setup.

### Database Tables

| Table | Description |
| --- | --- |
| users | User accounts and information |
| workspaces | Workspace information |
| workspace_members | Workspace membership and roles |
| projects | Projects within workspaces |
| tasks | Tasks within projects |
| labels | Labels used to organize tasks |
| task_labels | Many-to-many relationship between tasks and labels |
| comments | Comments associated with tasks |
| refresh_tokens | Refresh token management |
| admin_management_locks | Administration operation locking |
| alembic_version | Database migration revision |

## Authentication and Authorization

### Authentication

TaskHub uses JWT-based authentication with access
and refresh tokens.

The authentication flow includes:

1. The user registers an account.
2. The user submits login credentials.
3. The server validates the credentials.
4. The server generates access and refresh tokens.
5. The client includes the access token in protected requests.
6. The refresh token is used to obtain a new access token
   when the current access token expires.

Protected API requests require the Authorization header:

```http
Authorization: Bearer <access_token>
```

### Password Security

User passwords are hashed using Argon2 before being
stored in the database.

Plain-text passwords are not stored.

### Role-Based Access Control

TaskHub implements authorization at both system
and workspace levels.

#### System Roles

| Role | Description |
| --- | --- |
| ADMIN | System administration permissions |
| MEMBER | Standard user permissions |

#### Workspace Roles

| Role | Description |
| --- | --- |
| OWNER | Workspace ownership and management |
| EDITOR | Modify permitted workspace resources |
| VIEWER | Read permitted workspace resources |

Permissions are validated before protected business
operations are executed.

The exact permissions depend on the requested operation
and the user's relationship to the resource.

## Search, Filtering and Pagination

TaskHub supports searching, filtering and pagination
for resource list endpoints.

### Search

Search allows clients to retrieve resources matching
a keyword.

Example query parameters:

```text
?search=backend
```

### Filtering

Filtering allows clients to retrieve resources based
on supported resource attributes.

Examples:

```text
?status=active
?role=EDITOR
```

Available filters depend on the resource endpoint.

### Pagination

Pagination uses offset and limit parameters.

| Parameter | Description | Default |
| --- | --- | --- |
| offset | Number of records to skip | 0 |
| limit | Maximum number of records to return | 10 |

The maximum supported limit is 100.

Example:

```text
?offset=0&limit=10
```

Search, filtering and pagination can be combined:

```text
?search=backend&offset=0&limit=10
```

List queries use deterministic ordering to improve
pagination consistency.

Refer to Swagger UI for the exact query parameters
supported by each endpoint.

## Redis Caching

Redis is used to improve application performance
by reducing repeated database queries.

### Cached Resources

Caching is implemented for:

- Workspace list responses.
- Project list responses.

### Cache Strategy

TaskHub uses the Cache-Aside pattern.

```text
Client Request
      |
      v
Service Layer
      |
      v
Check Redis Cache
      |
      +--- Cache Hit ----> Return Cached Response
      |
      +--- Cache Miss ---> Query PostgreSQL
                                 |
                                 v
                          Store Result in Redis
                                 |
                                 v
                          Return Response
```

Authorization is validated according to the resource
before cached data is returned.

### Cache Key Management

Cache keys include resource and request-specific
information to distinguish cached responses.

The cache key prefix is:

```text
taskhub:v1:
```

Cache keys account for relevant information such as:

- Resource type.
- User or workspace scope.
- Search parameters.
- Filter parameters.
- Pagination parameters.

### Cache Expiration

Cache expiration is controlled by:

```env
CACHE_TTL_SECONDS=300
```

The default expiration time is 300 seconds.

### Cache Invalidation

Relevant cache entries are invalidated after
operations that modify cached resources, including:

- Creating resources.
- Updating resources.
- Deleting resources.
- Workspace membership changes.

### Cache Failure Handling

Redis is used as a performance optimization.

If Redis becomes unavailable during application
operation, supported cache operations fall back
to database queries.

Caching can also be disabled using:

```env
CACHE_ENABLED=False
```

The current Docker Compose configuration requires
Redis to pass its health check before the application
container starts.

### Inspect Cache Keys

For local Redis:

```bash
docker exec taskhub-redis redis-cli --scan --pattern "taskhub:*"
```

For Docker Compose:

```bash
docker compose exec redis redis-cli --scan --pattern "taskhub:*"
```

Cache entries are created after eligible list API
requests are executed.

## Error Handling

TaskHub uses centralized exception handling to provide
consistent API error responses.

Error handling includes:

- Request validation errors.
- Authentication errors.
- Authorization errors.
- Resource not found errors.
- Business rule violations.
- Database-related errors.
- Unexpected server errors.

### HTTP Status Codes

| Status Code | Description |
| --- | --- |
| 200 | Successful request |
| 201 | Resource created successfully |
| 204 | Successful request without response content |
| 400 | Invalid request or business rule violation |
| 401 | Authentication required or invalid credentials |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 409 | Resource conflict |
| 422 | Request validation or unprocessable content |
| 500 | Internal server error |

The exact status codes and response schemas depend
on the API endpoint.

## API Documentation

FastAPI automatically generates interactive
API documentation using OpenAPI.

| Resource | URL |
| --- | --- |
| Base URL | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| OpenAPI Schema | http://localhost:8000/openapi.json |

API documentation can be enabled or disabled through:

```env
DOCS_ENABLED=True
```

### API Versioning

The application uses versioned API endpoints.

```text
/api/v1
```

### API Modules

| Module | Description |
| --- | --- |
| Authentication | Registration, login and token management |
| Users | User information and management |
| Workspaces | Workspace and membership management |
| Projects | Project management |
| Tasks | Task management |
| Labels | Label management |
| Comments | Task comments and collaboration |

Refer to Swagger UI for available endpoints,
request schemas, response schemas and authentication
requirements.

## Code Quality

TaskHub uses Ruff for Python linting and formatting.

### Check Code

```bash
uv run ruff check .
```

### Automatically Fix Supported Issues

```bash
uv run ruff check --fix .
```

### Format Code

```bash
uv run ruff format .
```

### Check Formatting

```bash
uv run ruff format --check .
```

Ruff configuration is defined in `pyproject.toml`.

Run linting and formatting checks before committing
source code changes.

## Docker Management

### Start Services

```bash
docker compose up -d
```

### Build Application Image

```bash
docker compose build app
```

### Rebuild and Start Services

```bash
docker compose up -d --build
```

Rebuild the application image after modifying
application source code or dependencies.

### Stop Services

```bash
docker compose stop
```

### Restart Services

```bash
docker compose restart
```

### Restart Application Only

```bash
docker compose restart app
```

### Stop and Remove Containers

```bash
docker compose down
```

### Check Container Status

```bash
docker compose ps -a
```

### View All Service Logs

```bash
docker compose logs
```

### Follow Application Logs

```bash
docker compose logs -f app
```

### View PostgreSQL Logs

```bash
docker compose logs db
```

### View Redis Logs

```bash
docker compose logs redis
```

### Access Application Container

```bash
docker compose exec app sh
```

### Access PostgreSQL

```bash
docker compose exec db psql -U postgres -d taskhub_db
```

### Access Redis CLI

```bash
docker compose exec redis redis-cli
```

### Database Persistence

PostgreSQL data is stored in the `postgres-data`
named Docker volume.

Data is preserved when containers are stopped,
removed or recreated without deleting the volume.

List Docker volumes:

```bash
docker volume ls
```

The PostgreSQL database running inside Docker is
independent of the local PostgreSQL database.

Existing local database records are not automatically
imported into the Docker database.

Redis is used as a cache and does not require
persistent storage in the current configuration.

> Warning: Running `docker compose down -v` removes
> the associated PostgreSQL volume and permanently
> deletes the stored database data.

## Troubleshooting

### Docker Engine Is Not Running

Verify that Docker Desktop or Docker Engine is running:

```bash
docker info
```

### Dependency Download Failure

If the Docker build fails due to DNS or dependency
download errors, check the network connection.

Verify DNS resolution:

```bash
nslookup files.pythonhosted.org
```

Verify DNS resolution inside Docker:

```bash
docker run --rm python:3.13-slim python -c "import socket; print(socket.gethostbyname('files.pythonhosted.org'))"
```

The Dockerfile includes the following uv configuration
to improve download stability:

```dockerfile
ENV UV_HTTP_TIMEOUT=120 \
    UV_HTTP_RETRIES=5 \
    UV_CONCURRENT_DOWNLOADS=1
```

Concurrent downloads are limited to reduce simultaneous
network requests during dependency installation.

### Port 8000 Is Already in Use

Stop the local FastAPI server before starting
Docker Compose.

Alternatively, update the published application port
in `docker-compose.yml`.

### Database Connection Failure

Check the PostgreSQL container:

```bash
docker compose ps db
docker compose logs db
```

Verify the database environment variables.

PostgreSQL initialization variables are applied when
the database volume is first initialized.

Changing the variables later does not automatically
update existing database credentials.

### Redis Connection Failure

Check Redis status and connectivity:

```bash
docker compose ps redis
docker compose exec redis redis-cli ping
```

Inspect Redis logs:

```bash
docker compose logs redis
```

### Migration Failure

Inspect application logs:

```bash
docker compose logs app
```

Check the database connection and review the
migration files.

### Application Startup Failure

Check container status:

```bash
docker compose ps -a
```

Inspect application logs:

```bash
docker compose logs app
```

Verify environment variables, database connectivity,
Redis connectivity and migration status.

### API Documentation Is Not Available

Ensure API documentation is enabled:

```env
DOCS_ENABLED=True
```

Restart the local application after changing
environment configuration.

For Docker Compose, recreate the application container
to apply updated environment variables:

```bash
docker compose up -d --force-recreate app
```