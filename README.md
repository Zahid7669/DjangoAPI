# Django File Storage API

A RESTful API built with Django and Django REST Framework that allows authenticated users to upload and download files with complete download tracking.

## Features

- **User Authentication**: Session-based authentication via Django REST Framework
- **File Upload**: Users can upload any type of file
- **File Download**: Download files with automatic tracking
- **Organizations**: Users and files belong to organizations
- **Download Analytics**: Track downloads per file, per user, and per organization
- **RESTful Endpoints**: Full CRUD operations with browsable API

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework 3.15
- **Database**: PostgreSQL 15
- **Containerization**: Docker, Docker Compose
- **Testing**: Django TestCase with automated tests

## API Endpoints

- `GET/POST /api/files/` - List files (with download counts) and upload new files
- `GET /api/files/{id}/download/` - Download a file and record the download
- `GET /api/organizations/` - List organizations with total download counts
- `GET /api/downloads/?user={id}` - List downloads by a specific user
- `GET /api/downloads/?file={id}` - List downloads for a specific file

---

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed and running
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Zahid7669/DjangoAPI.git
   cd DjangoAPI
   ```

2. **Build and start services**
   
   **Option A: Using Make (recommended)**
   ```bash
   make build
   make up
   make setup
   ```
   
   **Option B: Using Docker directly**
   ```bash
   # Build the images
   docker compose build
   
   # Start the services
   docker compose up -d
   
   # Run migrations
   docker compose exec web python manage.py migrate
   
   # Create admin user
   docker compose exec web python manage.py create_admin
   
   # Create demo users
   docker compose exec web python manage.py create_demo
   ```

3. **Verify installation**
   
   **Using Make:**
   ```bash
   make test
   ```
   
   **Using Docker:**
   ```bash
   docker compose exec web python manage.py test storage
   ```
   
   You should see: `Ran 9 tests in X.XXXs - OK`

**User Credentials Created:**
- Admin: `admin` / `admin`
- Demo Users: `alice` / `password`, `bob` / `password`

### Using the Application

1. **Open the browsable API**: http://localhost:8000/api/
2. **Access Django Admin**: http://localhost:8000/admin/ (login with `admin` / `admin`)
3. **Login to API**: Click "Log in" (top-right), use `alice` / `password` or `admin` / `admin`
4. **Upload a file**:
   - Go to http://localhost:8000/api/files/
   - Scroll to the POST form
   - Choose a file and click POST
4. **Download a file**:
   - Note the file ID from the upload response
   - Visit http://localhost:8000/api/files/{id}/download/

### User Credentials

**Admin User:**
- Username: `admin`
- Password: `admin`
- Access: Django Admin + Full API access

**Demo Users:**
- `alice` / `password` (Organization A)
- `bob` / `password` (Organization B)

### Additional Commands

**Using Make:**
```bash
make up                # Start services
make down              # Stop services
make logs              # View application logs
make shell             # Open Django shell
make test              # Run tests
make migrate           # Run migrations
make createadmin       # Create admin user only
make createdemo        # Create demo users only
make createsuperuser   # Create custom admin user (interactive)
```

**Using Docker directly:**
```bash
docker compose up -d                              # Start services
docker compose down                               # Stop services
docker compose logs -f                            # View logs (follow mode)
docker compose exec web python manage.py shell   # Open Django shell
docker compose exec web python manage.py test    # Run tests
docker compose exec web python manage.py migrate # Run migrations
docker compose exec web python manage.py create_admin      # Create admin user
docker compose exec web python manage.py create_demo       # Create demo users
docker compose exec web python manage.py createsuperuser   # Create custom admin
```

---

## Development

### Running Tests

**Using Make:**
```bash
make test
```

**Using Docker:**
```bash
docker compose exec web python manage.py test storage
```

### Database

- **Development**: PostgreSQL 15 (via Docker)
- **Connection**: Configured via environment variables in `docker-compose.yml`
- **Data persistence**: Stored in Docker volume `postgres_data`

---
