import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 480))

# Detect Render environment
IS_RENDER = os.getenv("RENDER", "") == "true"

# Choose a writable path
if IS_RENDER:
    DATA_DIR = Path("/opt/render/project/src/data")
else:
    DATA_DIR = BASE_DIR / "data"

# Make sure the folder exists
DATA_DIR.mkdir(parents=True, exist_ok=True)

DEFAULT_DB = f"sqlite:///{DATA_DIR / 'users.db'}"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DB)

MODEL_PATH = os.getenv(
    "MODEL_PATH",
    str(BASE_DIR / "artifacts" / "customer_churn_model.joblib"),
)

CORS_ORIGINS = [
    o.strip() for o in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:8501,http://127.0.0.1:8501",
    ).split(",") if o.strip()
]