# Architecture

## Solution overview

The KAWUO ITSM platform is built around a Django REST API for business logic and a React frontend for the user experience. PostgreSQL is the persistent relational database, Redis handles background tasks, and Nginx sits in front for HTTP routing.

## Core domains

1. Identity and access management
   - User model with role choices: staff, IT support, IT administrator, management
   - Permissions enforced at the API layer
2. Ticket lifecycle
   - ticket creation, assignment, acknowledgement, resolution, closure
   - SLA-aware deadlines and escalation
3. Asset and maintenance operations
   - asset inventory, assignment history, maintenance planning
4. Service and knowledge support
   - service requests and knowledge-base articles
5. Reporting and auditability
   - notifications, dashboards, and audit logs

## Database design principles

- normalize shared reference data such as department, category, and priority
- use foreign keys rather than duplicated data
- create explicit indexes for common search and filtering patterns
- keep audit logs immutable for traceability

## Deployment model

```text
Internet
  -> HTTPS / CDN / reverse proxy
  -> Nginx
  -> React frontend
  -> Django REST API
  -> PostgreSQL
  -> Redis/Celery
```
