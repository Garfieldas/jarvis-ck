# jarvis_django

## First run (VS Code)

Open the project folder in VS Code, then run tasks in this order from **Terminal → Run Task...**:

1. **Python: create venv**
2. **Python: install requirements**
3. **up dev stack**
4. **Django: migrate**
5. *(optional)* **Create super user**

For development, run these when needed:

- **Django: tailwind dev** (Tailwind watcher)
- **Django: rqworker --with-scheduler** (background worker)
- Start app server from **Run and Debug** using **Python Debugger: Django**

## Required environment file

Create a `.env` file in the project root before running the app. Example:

```env
# Local development only. Use a strong, random key in production.
SECRET_KEY=your-dev-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
BASE_URL=http://127.0.0.1:8000

POSTGRES_DB=jarvis
POSTGRES_USER=jarvis
POSTGRES_PASSWORD=your-local-db-password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

REDIS_PASSWORD=your-local-redis-password
REDIS_HOST=localhost
REDIS_PORT=6379
```

For Docker Compose services, the same `.env` is used by `docker-compose.yml`.

## Project structure

```text
jarvis_django/
├── app/                  # Main Django app (models, views, templates, static resources)
├── core/                 # Project config (settings, urls, asgi/wsgi)
├── theme/                # Tailwind integration and generated CSS assets
├── .vscode/              # VS Code tasks, launch, and workspace settings
├── docker-compose.yml    # Postgres/Redis/RQ local services
├── manage.py             # Django management entry point
├── requirements.txt      # Runtime Python dependencies
└── requirements_dev.txt  # Development dependencies
```
