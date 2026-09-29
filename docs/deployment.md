# Deployment notes

## Local development

- use the `.env.example` file to create a local `.env`
- run PostgreSQL through Docker Compose
- use the backend virtual environment for Django migrations and tests

## Production deployment

1. set secure environment variables
2. set `DEBUG=False`
3. enforce HTTPS through Nginx and certificate automation
4. run Gunicorn behind Nginx
5. configure external PostgreSQL and Redis services
6. enable secure file storage and backup policies

### Free Render + Neon configuration

The repository Blueprint deploys the Django API and React frontend. The API connects to Neon through the secret `DATABASE_URL` setting. Django migrations create standard departments, categories, and priorities without creating demo users. Staff can register from the login page; use the documented `create_it_admin` management command in the Render API Shell to provision IT administrators. Render's free API instance can sleep after inactivity, so the first request may take longer.

## Backup strategy

- daily PostgreSQL dumps to an off-server volume
- file backups for media uploads
- configuration backup for `.env`, nginx, and docker files
- retention policy: 30-day rolling copy with weekly archival retention
