# Architecture

```mermaid
graph LR
  A[Streamlit UI] -->|HTTPS + JWT| B[FastAPI Backend]
  B -->|joblib in RAM| C[Extra Trees Model]
  B --> D[(SQLite)]
```

## Components

| Component | Technology | Responsibility |
|-----------|-----------|----------------|
| UI | Streamlit | Forms, uploads, charts, retention tasks |
| API | FastAPI | Auth, JWT validation, prediction proxy |
| Model | Extra Trees (sklearn) | Binary churn probability |
| DB | SQLite | Users, predictions, audit log |

## Prediction flow

```mermaid
sequenceDiagram
  User->>Streamlit: Enter customer
  Streamlit->>FastAPI: POST /api/predict (JWT)
  FastAPI->>Model: predict_proba(features)
  Model-->>FastAPI: probability
  FastAPI->>SQLite: save prediction
  FastAPI-->>Streamlit: JSON
  Streamlit-->>User: probability + risk
```