# CIM Wizard Integrated - Complete Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Development Setup](#development-setup)
5. [Production Deployment](#production-deployment)
6. [Docker Configuration](#docker-configuration)
7. [Environment Configuration](#environment-configuration)
8. [File Structure](#file-structure)
9. [API Documentation](#api-documentation)
10. [Database Management](#database-management)
11. [Troubleshooting](#troubleshooting)

---

## Project Overview

CIM Wizard Integrated is a comprehensive geospatial data processing platform that provides:
- Building property calculations
- Demographic analysis
- Census data integration
- PostGIS-based spatial operations
- RESTful API with FastAPI
- Docker-based deployment

### Key Features
- **Modular Calculator System**: Extensible architecture for adding new calculation methods
- **PostGIS Integration**: Advanced spatial database capabilities
- **Docker Support**: Containerized deployment for development and production
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **Environment Flexibility**: Separate configurations for development and production

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Client Applications                  │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │     API      │  │   Services   │  │  Calculators │ │
│  │   Endpoints  │  │              │  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                  PostgreSQL + PostGIS                    │
│                   Spatial Database                       │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites
- Python 3.10+
- Docker Desktop
- Git

### Fastest Setup (Development)

```bash
# 1. Clone the repository
git clone <repository-url>
cd cim_wizard_integrated

# 2. Run development setup
./setup_dev.sh  # Unix/Linux/macOS
# OR
setup_dev.bat   # Windows

# 3. Start PostGIS database
./setup_docker_postgis.sh  # Unix/Linux/macOS
# OR
setup_docker_postgis.bat   # Windows

# 4. Run the application
python run.py
```

Access the application at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- pgAdmin: http://localhost:5050

---

## Development Setup

### Method 1: Using Setup Scripts (Recommended)

#### Windows
```batch
# Complete development environment setup
setup_dev.bat

# Start PostGIS database
setup_docker_postgis.bat

# Run application
python run.py
```

#### Unix/Linux/macOS
```bash
# Complete development environment setup
./setup_dev.sh

# Start PostGIS database
./setup_docker_postgis.sh

# Run application
python run.py
```

### Method 2: Manual Setup

1. **Create Python virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unix/Linux/macOS
   # OR
   venv\Scripts\activate.bat  # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment:**
   ```bash
   cp env.development .env
   ```

4. **Start PostGIS database:**
   ```bash
   docker-compose up postgis -d
   ```

5. **Initialize database:**
   ```bash
   python scripts/populate_sample_data.py
   ```

6. **Run application:**
   ```bash
   python run.py
   ```

### Development Tools

- **pgAdmin**: Database management interface
  ```bash
  docker-compose --profile tools up pgadmin -d
  ```
  Access at http://localhost:5050
  - Email: admin@cimwizard.com
  - Password: admin

- **Test database connection:**
  ```bash
  python scripts/test_docker_connection.py
  ```

---

## Production Deployment

### Using Deployment Scripts

#### Windows
```batch
deploy_prod.bat
```

#### Unix/Linux/macOS
```bash
./deploy_prod.sh
```

### Manual Production Deployment

1. **Configure production environment:**
   ```bash
   cp env.production .env
   # Edit .env with production values
   ```

2. **Build and start all services:**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

3. **Enable optional services:**
   ```bash
   # pgAdmin
   docker-compose -f docker-compose.prod.yml --profile tools up pgadmin -d
   
   # Nginx reverse proxy
   docker-compose -f docker-compose.prod.yml --profile proxy up nginx -d
   ```

### Production Management

- **View logs:**
  ```bash
  docker-compose -f docker-compose.prod.yml logs -f
  ```

- **Stop services:**
  ```bash
  docker-compose -f docker-compose.prod.yml down
  ```

- **Backup database:**
  ```bash
  docker exec cim_wizard_postgis_prod pg_dump -U cim_wizard_user cim_wizard_integrated > backup.sql
  ```

- **Restore database:**
  ```bash
  docker exec -i cim_wizard_postgis_prod psql -U cim_wizard_user cim_wizard_integrated < backup.sql
  ```

---

## Docker Configuration

### Docker Files Overview

| File | Purpose | Description |
|------|---------|-------------|
| `docker-compose.yml` | Development | Runs PostGIS only, app runs locally |
| `docker-compose.prod.yml` | Production | Full stack deployment |
| `Dockerfile` | App container | Application container image |
| `Dockerfile.postgis` | PostGIS container | Custom PostGIS with extensions |

### Docker Compose Services

#### Development (`docker-compose.yml`)
- **postgis**: PostgreSQL + PostGIS database
- **pgadmin**: Database management (optional, use --profile tools)

#### Production (`docker-compose.prod.yml`)
- **postgis**: PostgreSQL + PostGIS database
- **app**: CIM Wizard application
- **nginx**: Reverse proxy (optional, use --profile proxy)
- **pgadmin**: Database management (optional, use --profile tools)

### Docker Networks
- Development: `cim_wizard_dev_network`
- Production: `cim_wizard_prod_network`

### Docker Volumes
- `postgis_data_dev/prod`: Database data persistence
- `pgadmin_data_dev/prod`: pgAdmin configuration persistence

---

## Environment Configuration

### Environment Files

| File | Purpose | Usage |
|------|---------|-------|
| `env.example` | Template | Reference for all variables |
| `env.development` | Development | Local development settings |
| `env.production` | Production | Production deployment settings |
| `.env` | Active config | Created from above templates |

### Key Environment Variables

#### Database Configuration
```bash
POSTGRES_HOST=localhost       # Database host
POSTGRES_PORT=5432            # Database port
POSTGRES_DB=cim_wizard_integrated
POSTGRES_USER=cim_wizard_user
POSTGRES_PASSWORD=<secure_password>
DATABASE_URL=postgresql://...  # Full connection string
```

#### Application Settings
```bash
DEBUG=True/False              # Debug mode
LOG_LEVEL=DEBUG/INFO/WARNING  # Logging level
HOST=0.0.0.0                  # Application host
PORT=8000                     # Application port
```

#### Security Settings
```bash
SECRET_KEY=<secure_random_string>     # JWT secret
BACKEND_CORS_ORIGINS=["..."]          # Allowed origins
```

### Environment Setup Priority

1. `.env` file (if exists)
2. `env.development` (for development)
3. `env.production` (for production)
4. `env.example` (as reference)

---

## File Structure

```
cim_wizard_integrated/
│
├── app/                        # Application code
│   ├── api/                   # API endpoints
│   ├── calculators/           # Calculator modules
│   ├── core/                  # Core functionality
│   ├── db/                    # Database models
│   ├── models/                # Data models
│   ├── schemas/               # Pydantic schemas
│   └── services/              # Business logic
│
├── docs/                      # Documentation
│   ├── README.md             # This file
│   ├── adding_new_calculator.md
│   ├── architecture_overview.md
│   ├── calculator_methods.md
│   └── service_endpoints.md
│
├── init-scripts/              # Database initialization
│   ├── 01-init-database.sql
│   └── 02-create-sample-data.sql
│
├── scripts/                   # Utility scripts
│   ├── populate_sample_data.py
│   └── test_docker_connection.py
│
├── Docker files (root level)
├── docker-compose.yml         # Development Docker setup
├── docker-compose.prod.yml    # Production Docker setup
├── Dockerfile                 # Application container
├── Dockerfile.postgis         # PostGIS container
│
├── Setup scripts
├── setup_dev.sh/.bat         # Development environment setup
├── setup_docker_postgis.sh/.bat  # PostGIS setup
├── deploy_prod.sh/.bat       # Production deployment
│
├── Environment files
├── env.example               # Environment template
├── env.development           # Development settings
├── env.production           # Production settings
│
└── Application files
    ├── main.py               # FastAPI application
    ├── run.py               # Application runner
    └── requirements.txt      # Python dependencies
```

---

## API Documentation

### Accessing API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Main API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/buildings` | GET | List buildings |
| `/api/calculate/{calculator}` | POST | Run calculator |
| `/api/scenarios` | GET | List scenarios |

### Calculator Endpoints

Each calculator has its own endpoint:
- Building Height: `/api/calculate/building_height`
- Building Area: `/api/calculate/building_area`
- Building Demographics: `/api/calculate/building_demographic`
- And more...

---

## Database Management

### PostGIS Extensions

The following extensions are installed:
- PostGIS 3.4
- pgRouting
- H3
- MobilityDB
- OGR_FDW

### Database Access

#### Using psql
```bash
# Development
docker exec -it cim_wizard_postgis_dev psql -U cim_wizard_user -d cim_wizard_integrated

# Production
docker exec -it cim_wizard_postgis_prod psql -U cim_wizard_user -d cim_wizard_integrated
```

#### Using pgAdmin
1. Access pgAdmin at http://localhost:5050
2. Login with configured credentials
3. Add server:
   - Host: postgis (within Docker network) or localhost (from host)
   - Port: 5432
   - Username: cim_wizard_user
   - Password: (from .env file)

### Database Operations

#### Backup
```bash
# Development
docker exec cim_wizard_postgis_dev pg_dump -U cim_wizard_user cim_wizard_integrated > backup.sql

# Production
docker exec cim_wizard_postgis_prod pg_dump -U cim_wizard_user cim_wizard_integrated > backup.sql
```

#### Restore
```bash
# Development
docker exec -i cim_wizard_postgis_dev psql -U cim_wizard_user cim_wizard_integrated < backup.sql

# Production
docker exec -i cim_wizard_postgis_prod psql -U cim_wizard_user cim_wizard_integrated < backup.sql
```

---

## Troubleshooting

### Common Issues and Solutions

#### Docker Issues

**Problem**: Docker is not running
```
[ERROR] Docker is not running. Please start Docker Desktop first.
```
**Solution**: Start Docker Desktop application

**Problem**: Port already in use
```
Error: bind: address already in use
```
**Solution**: 
- Check what's using the port: `netstat -ano | findstr :5432`
- Stop the conflicting service or change the port in .env

#### Database Connection Issues

**Problem**: Database connection failed
```
[ERROR] Database connection failed
```
**Solution**:
1. Check if PostGIS container is running: `docker ps`
2. Check logs: `docker-compose logs postgis`
3. Verify connection string in .env file
4. Wait for database to be ready (health check)

#### Application Issues

**Problem**: Module import errors
```
ModuleNotFoundError: No module named 'app'
```
**Solution**:
1. Ensure you're in the project root directory
2. Activate virtual environment
3. Reinstall dependencies: `pip install -r requirements.txt`

### Getting Help

1. Check logs:
   ```bash
   # Docker logs
   docker-compose logs -f
   
   # Application logs
   tail -f logs/app.log
   ```

2. Test connections:
   ```bash
   python scripts/test_docker_connection.py
   ```

3. Verify environment:
   ```bash
   python -c "from app.db.database import engine; print('OK')"
   ```

---

## Additional Resources

- [Adding a New Calculator](adding_new_calculator.md)
- [Architecture Overview](architecture_overview.md)
- [Calculator Methods](calculator_methods.md)
- [Service Endpoints](service_endpoints.md)
- [OOP Approach](oop_approach.md)

---

## License

[Your License Here]

## Contributors

[Your Contributors Here]

## Support

For issues, questions, or contributions, please [contact/submit issue/etc.]