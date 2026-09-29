# KAWUO IT Ticketing & Service Management System

A production-oriented ITSM foundation for the Karamoja Women Umbrella Organisation (KAWUO), implemented as a Django REST API plus a React frontend. This repository is structured as a real monorepo with backend, frontend, infrastructure, and documentation.

## Overview

The system supports:

- staff ticket submission and tracking
- IT support assignment and status changes
- role-based permissions for staff, support officers, administrators, and management
- asset, maintenance, and service-request tracking
- knowledge-base search and support articles
- notifications, audit logs, and reporting foundations
- PostgreSQL-ready deployment configuration with Docker / Nginx / Gunicorn

## Recommended architecture

- Backend: Django, Django REST Framework, JWT auth, PostgreSQL-ready settings
- Frontend: React + Vite + TypeScript
- Messaging/background jobs: Celery + Redis
- Containerization: Docker Compose
- Reverse proxy: Nginx

## Current implementation status

This repository intentionally starts with the architecture, data model, and backend foundation for the required system.

### Included

- Django project scaffold
- custom user model and RBAC-ready permissions
- ticket, category, priority, SLA, asset, and maintenance model foundations
- REST API endpoints for authentication, dashboards, tickets, assets, and knowledge-base access
- API test suite covering authentication, permission checks, and ticket flows
- backend settings split for development and production
- seed data and deployment-ready configuration files
- frontend scaffold with a dashboard layout and key screens

### Planned next phase

- expand admin screens and full React pages
- complete multi-step ticket lifecycle
- add notifications, reports, and export flows
- wire Docker/compose and production environment variables end-to-end

## Project layout

```text
kawuo-itsm/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── kawuo_backend/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   └── itsm/
│       ├── __init__.py
│       ├── admin.py
│       ├── apps.py
│       ├── models.py
│       ├── permissions.py
│       ├── serializers.py
│       ├── urls.py
│       ├── views.py
│       ├── tests/
│       │   ├── __init__.py
│       │   ├── test_models.py
│       │   └── test_api.py
│       └── fixtures/
│           └── seed_data.json
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── src/
├── docs/
│   ├── architecture.md
│   ├── api.md
│   └── deployment.md
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Environment variables

Use `.env.example` as the starting template for local environment configuration.

## Deployment

The project is prepared for a Linux VPS / Docker deployment pattern with:

- Nginx as the reverse proxy
- Gunicorn serving Django
- PostgreSQL as the database backend
- Redis and Celery for background processing
- .env-based secret management

### Free public deployment path

The repository includes deployment-ready configuration for a free-tier public setup:

- Render for the Django API + PostgreSQL database
- Vercel for the React frontend

See [deploy/free-hosting.md](deploy/free-hosting.md) for exact steps and environment variables.

## Security and governance

- role-based access control
- secure password hashing with Django defaults
- JWT-based API tokens with expiration
- input validation and model constraints
- file upload validation patterns
- audit trail fields for key actions

## Documentation

The detailed architecture and deployment notes are kept under the `docs/` directory.

## Notes

This project is intentionally designed as a strong engineering foundation that can be incrementally extended into a full enterprise ITSM platform.
