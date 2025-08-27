# Environment Setup Guide for CIM Wizard Integrated

This guide explains how to properly configure environment variables and run the FastAPI application.

## Quick Start

### 1. Start the Database
```bash
sudo docker-compose -f docker-compose.db.yml up -d
```

### 2. Start the Application
```bash
# Development mode (with auto-reload)
./start_app.sh dev

# Production mode
./start_app.sh prod

# Background mode
./start_app.sh bg
```

## Environment Variables

The application uses Pydantic BaseSettings for environment variable management. This provides:
- **Type safety**: Environment variables are automatically converted to the correct type
- **Validation**: Invalid values are caught at startup
- **Default values**: Sensible defaults for all settings
- **Documentation**: Each setting has a description

### Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://cim_wizard_user:cim_wizard_password@localhost:5433/cim_wizard_integrated` | Full database connection URL |
| `POSTGRES_HOST` | `localhost` | PostgreSQL host |
| `POSTGRES_PORT` | `5433` | PostgreSQL port |
| `POSTGRES_DB` | `cim_wizard_integrated` | Database name |
| `POSTGRES_USER` | `cim_wizard_user` | Database username |
| `POSTGRES_PASSWORD` | `cim_wizard_password` | Database password |

### Application Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `PROJECT_NAME` | `CIM Wizard Integrated` | Application name |
| `VERSION` | `2.0.0` | Application version |
| `API_V1_STR` | `/api` | API version prefix |
| `HOST` | `0.0.0.0` | Server host |
| `PORT` | `8000` | Server port |
| `DEBUG` | `True` | Debug mode |

### Security Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | `dev-secret-key-only-for-development` | Secret key for JWT tokens |
| `BACKEND_CORS_ORIGINS` | `["*"]` | Allowed CORS origins |

### Database Performance

| Variable | Default | Description |
|----------|---------|-------------|
| `POOL_SIZE` | `10` | Database connection pool size |
| `MAX_OVERFLOW` | `20` | Database connection pool max overflow |
| `POOL_PRE_PING` | `True` | Database connection pool pre-ping |
| `POOL_RECYCLE` | `3600` | Database connection pool recycle time |

### 🛠️ Development Settings

| Variable | Default | Description |
|----------|---------|-------------|
| `RELOAD` | `True` | Auto-reload on code changes |
| `SHOW_SQL_QUERIES` | `False` | Show SQL queries in logs |
| `DOCS_ENABLED` | `True` | Enable API documentation |

## Environment Files

The application supports multiple environment files:

### Development Environment (`env.development`)
```bash
# Copy development environment
cp env.development .env
```

### Production Environment (`env.production`)
```bash
# Copy production environment
cp env.production .env
```

### Custom Environment
Create your own `.env` file:
```bash
# Example .env file
DATABASE_URL=postgresql://user:pass@host:port/db
DEBUG=False
PORT=9000
```

## How to Set Environment Variables

### Method 1: Environment File (Recommended)
Create a `.env` file in the project root:
```bash
# .env
DATABASE_URL=postgresql://myuser:mypass@localhost:5433/mydb
DEBUG=True
PORT=8000
```

### Method 2: System Environment Variables
Set environment variables in your shell:
```bash
export DATABASE_URL="postgresql://myuser:mypass@localhost:5433/mydb"
export DEBUG=True
export PORT=8000
```

### Method 3: Inline with Command
Set environment variables for a single command:
```bash
DATABASE_URL="postgresql://myuser:mypass@localhost:5433/mydb" DEBUG=True uvicorn main:app --reload
```

## Application Management

### Using the Startup Script

The `start_app.sh` script provides multiple ways to manage the application:

```bash
# Development mode (with auto-reload)
./start_app.sh dev

# Production mode (multiple workers)
./start_app.sh prod

# Background mode (daemon)
./start_app.sh bg

# Stop the application
./start_app.sh stop

# Check application status
./start_app.sh status

# View application logs
./start_app.sh logs

# Show help
./start_app.sh help
```

### Manual Commands

```bash
# Development with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production with multiple workers
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Background mode
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
```

## Troubleshooting

### Database Connection Issues

1. **Check if Docker container is running**:
   ```bash
   sudo docker ps | grep integrateddb
   ```

2. **Start the database container**:
   ```bash
   sudo docker-compose -f docker-compose.db.yml up -d
   ```

3. **Test database connection**:
   ```bash
   python -c "import psycopg2; conn = psycopg2.connect('postgresql://cim_wizard_user:cim_wizard_password@localhost:5433/cim_wizard_integrated'); print('Success'); conn.close()"
   ```

### Environment Variable Issues

1. **Check current environment variables**:
   ```bash
   env | grep DATABASE
   ```

2. **Unset conflicting variables**:
   ```bash
   unset DATABASE_URL
   ```

3. **Verify .env file is loaded**:
   ```bash
   python -c "from app.core.settings import settings; print(settings.DATABASE_URL)"
   ```

### Permission Issues

1. **Fix pgdata permissions**:
   ```bash
   sudo chown -R 999:999 pgdata/
   ```

2. **Restart database container**:
   ```bash
   sudo docker-compose -f docker-compose.db.yml restart
   ```

## Monitoring

### Check Application Status
```bash
# Check if application is running
ps aux | grep uvicorn

# Check application logs
tail -f app.log

# Test API endpoints
curl http://localhost:8000/health
curl http://localhost:8000/
```

### Check Database Status
```bash
# Check Docker container
sudo docker ps | grep integrateddb

# Check database logs
sudo docker logs integrateddb

# Test database connection
python -c "import psycopg2; conn = psycopg2.connect('postgresql://cim_wizard_user:cim_wizard_password@localhost:5433/cim_wizard_integrated'); print('Connected'); conn.close()"
```

## Advanced Configuration

### Custom Database URL
```bash
# Set custom database URL
export DATABASE_URL="postgresql://user:pass@host:port/db"

# Or in .env file
echo "DATABASE_URL=postgresql://user:pass@host:port/db" >> .env
```

### Different Port
```bash
# Set custom port
export PORT=9000

# Or start with specific port
uvicorn main:app --host 0.0.0.0 --port 9000
```

### Disable Auto-reload
```bash
# Set environment variable
export RELOAD=False

# Or start without reload
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Best Practices

1. **Use .env files** for development and production configurations
2. **Never commit sensitive data** to version control
3. **Use different configurations** for different environments
4. **Validate environment variables** at startup
5. **Use the startup script** for consistent application management
6. **Monitor logs** for debugging and performance issues

## Getting Help

If you encounter issues:

1. Check the application logs: `./start_app.sh logs`
2. Verify database connection: `./start_app.sh status`
3. Check environment variables: `python -c "from app.core.settings import settings; print(settings.DATABASE_URL)"`
4. Review this documentation
5. Check the FastAPI documentation: https://fastapi.tiangolo.com/
