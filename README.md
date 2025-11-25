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
   ```bash
   make build
   make up
   ```
   
   *Without Make (Windows users):*
   ```bash
   docker compose build
   docker compose up -d
   ```

3. **Run database migrations**
   ```bash
   make migrate
   ```

4. **Create demo users**
   ```bash
   make createdemo
   ```
   
   This creates:
   - User: `alice`, Password: `password` (Organization A)
   - User: `bob`, Password: `password` (Organization B)

5. **Verify installation**
   ```bash
   make test
   ```
   
   You should see: `Ran 2 tests in X.XXXs - OK`

### Using the Application

1. **Open the browsable API**: http://localhost:8000/api/
2. **Login**: Click "Log in" (top-right), use `alice` / `password`
3. **Upload a file**:
   - Go to http://localhost:8000/api/files/
   - Scroll to the POST form
   - Choose a file and click POST
4. **Download a file**:
   - Note the file ID from the upload response
   - Visit http://localhost:8000/api/files/{id}/download/

### Additional Commands

```bash
make logs              # View application logs
make shell             # Open Django shell
make createsuperuser   # Create admin user
make down              # Stop services
```

---

## Development

### Project Structure

```
DjangoAPI/
├── config/              # Django settings and URLs
├── storage/             # Main application
│   ├── models.py       # Organization, User, UploadedFile, Download
│   ├── serializers.py  # DRF serializers
│   ├── views.py        # API viewsets
│   ├── tests/          # Automated tests
│   └── management/     # Custom management commands
├── docker-compose.yml  # Docker services configuration
├── Dockerfile          # Web container definition
├── Makefile           # Command shortcuts
└── requirements.txt    # Python dependencies
```

### Running Tests

```bash
make test
```

Tests cover:
- File upload functionality
- File download with tracking
- Download count aggregation
- Organization statistics
- User/file filtering

### Database

- **Development**: PostgreSQL 15 (via Docker)
- **Connection**: Configured via environment variables in `docker-compose.yml`
- **Data persistence**: Stored in Docker volume `postgres_data`

---

## Troubleshooting

### Port 8000 already in use
Change the port mapping in `docker-compose.yml`:
```yaml
ports:
  - '8001:8000'  # Use 8001 instead
```

### Docker file sharing error (Mac)
1. Open Docker Desktop
2. Settings → Resources → File Sharing
3. Add your project directory
4. Apply & Restart

### Tests not running
Ensure services are up and migrations are applied:
```bash
docker compose ps          # Check services
make migrate              # Apply migrations
make test                 # Run tests
```

---

## License

MIT
# File Storage Application

A simple file storage web application built with **Django** and **Django REST Framework**, running in **Docker** using **Docker Compose**.  
Authenticated users can upload and download files, and the system tracks all downloads per file, user, and organization.

The browsable API provided by Django REST Framework serves as the frontend.

---

## Features

The application provides:

- **Session-based authentication**
  - Users can log in and log out.
  - Each user belongs to an **organization**.
- **File uploads**
  - Authenticated users can upload files.
  - Uploaded files belong to the same organization as the uploader.
- **File downloads + tracking**
  - Users can see and download files from **any organization**.
  - Each download is recorded.
- **Aggregated statistics**
  - List all files + how many times each has been downloaded.
  - List all organizations + total download count of all files belonging to that org.
  - List all downloads done by a single user.
  - List all downloads for a single file.

---

## Tech Stack

- **Backend**: Django, Django REST Framework  
- **Auth**: Session authentication  
- **Database**: (e.g.) PostgreSQL (configurable)  
- **Containerization**: Docker, Docker Compose  

---

## Getting Started

### 1. Prerequisites

Make sure you have:

- [Docker](https://www.docker.com/)  
- [Docker Compose](https://docs.docker.com/compose/)  

Clone the repository:

```bash
git clone <YOUR_REPO_URL> file-storage-app
cd file-storage-app
