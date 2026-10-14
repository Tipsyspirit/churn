# Deployment

## Docker Compose (recommended)

```bash
docker-compose up --build
```

Streamlit: http://localhost:8501
Backend docs: http://localhost:8000/docs

## Cloud options

| Component | Platform | Notes |
|-----------|----------|-------|
| Backend | Render / Railway / Fly.io | Free tier supports FastAPI |
| Streamlit | Streamlit Cloud | Connect GitHub repo |
| Database | Managed Postgres | When moving off SQLite |

## Env vars required on the backend

- `SECRET_KEY`
- `DATABASE_URL`
- `CORS_ORIGINS`
- `MODEL_PATH`