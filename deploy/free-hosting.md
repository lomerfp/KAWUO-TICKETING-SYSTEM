# Free hosting deployment guide

This project is ready to deploy in a free-tier setup using:

- Render for the Django API and PostgreSQL database
- Vercel for the React frontend

## 1) Deploy the backend to Render

1. Push this repository to GitHub.
2. Open Render and click "New +" > "Web Service".
3. Connect the repository.
4. Use the following settings:
   - Root directory: `backend`
   - Build command: `pip install --upgrade pip && pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - Start command: `gunicorn kawuo_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2`
5. Add environment variables:
   - `SECRET_KEY`: generate a strong secret
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `localhost,127.0.0.1,kawuo-itsm-api.onrender.com`
   - `CORS_ALLOWED_ORIGINS`: `https://kawuo-itsm.vercel.app,http://localhost:3000,http://127.0.0.1:3000`
   - `CSRF_TRUSTED_ORIGINS`: `https://kawuo-itsm.vercel.app,http://localhost:3000,http://127.0.0.1:3000`
   - `DATABASE_URL`: set automatically if you create a Postgres database in Render

## 2) Deploy the frontend to Vercel

1. Import the repo into Vercel.
2. Set the project root to `frontend`.
3. Set the build command to `npm install && npm run build`.
4. Set the output directory to `dist`.
5. Add environment variable:
   - `VITE_API_BASE_URL`: `https://your-render-backend-url.onrender.com`

## 3) Final config notes

- The API expects the frontend to talk to the backend through the public Render URL.
- For local development, keep using the default `http://localhost:8000` backend.
- For production, use the live Render URL in the frontend environment variables.

## 4) Optional admin creation

After the backend is online, create a superuser:

```bash
python manage.py createsuperuser
```

## 5) Security recommendation

- Rotate the default secret keys before production use.
- Use HTTPS only in the public environment.
- Keep database credentials in your host provider’s environment variable manager.
