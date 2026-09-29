# API overview

## Authentication

- POST /api/auth/register/
- POST /api/auth/login/
- GET /api/auth/me/

## Tickets

- GET /api/tickets/
- POST /api/tickets/
- GET /api/tickets/{id}/
- POST /api/tickets/{id}/comment/
- POST /api/tickets/{id}/acknowledge/ (IT support/admin)
- POST /api/tickets/{id}/assign/
- POST /api/tickets/{id}/resolve/ (requires resolution summary)
- POST /api/tickets/{id}/close/ (resolved tickets only)
- GET /api/ticket-departments/, /api/categories/, /api/priorities/ (authenticated)
- GET /api/reports/tickets.csv (IT support/admin only)

## Assets and maintenance

- GET /api/assets/
- GET /api/maintenance/
- GET /api/service-requests/
- GET /api/knowledge-base/
- GET /api/notifications/

## Dashboard

- GET /api/dashboard/summary/

Staff can submit and track their own tickets and add feedback as ticket comments. IT support and administrators can review the full queue, acknowledge and assign tickets, resolve with a summary, close resolved tickets, and download the CSV report.

## Provisioning IT administrators

Public registration creates staff accounts only. To create an IT administrator, open the Render API service Shell and run:

```sh
python manage.py create_it_admin --username YOUR_ADMIN_USERNAME --email YOUR_ADMIN_EMAIL
```

The command prompts for and confirms a password and validates it against Django's password rules. Enter the password only in the interactive prompt; do not put it in source control or chat.
