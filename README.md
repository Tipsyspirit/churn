# ChurnSight — Customer Churn Prediction System

A full-stack machine learning application that predicts customer churn, categorizes risk, and supports retention workflows.

**Stack:** Streamlit (UI) → FastAPI (backend) → Extra Trees model (scikit-learn) → SQLite

## Quick start

```bash
git clone <repo-url> churnsight
cd churnsight
docker-compose up --build
```

- Streamlit UI: http://localhost:8501
- API docs: http://localhost:8000/docs

## Local development (3 terminals)

```bash
# Terminal 1 — backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2 — streamlit
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py

# Terminal 3 — one-time model copy
bash scripts/copy_model.sh
```

## Project layout

- `ml/` — training notebooks, model artifact
- `backend/` — FastAPI service, JWT auth, SQLite
- `streamlit_app/` — multipage Streamlit UI
- `docs/` — SRS, architecture, API reference, etc.
- `scripts/` — helper shell scripts

## Documentation

See `docs/` for the SRS, architecture, and deployment guides.

## Team

- P1 — ML model
- P2 — Streamlit UI
- P3 — Retention strategy
- P4 — Backend + integration