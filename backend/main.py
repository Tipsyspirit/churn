from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas, database, auth, ml_service
from config import CORS_ORIGINS

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="ChurnSight API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/auth/register", response_model=schemas.TokenResponse)
def register(req: schemas.RegisterRequest, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == req.email).first():
        raise HTTPException(400, "Email already registered")
    user = models.User(
        name=req.name, email=req.email,
        password_hash=auth.hash_password(req.password),
        role=req.role or "analyst",
    )
    db.add(user); db.commit(); db.refresh(user)
    token = auth.create_access_token({"sub": user.email, "role": user.role})
    return {"access_token": token,
            "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}}

@app.post("/api/auth/login", response_model=schemas.TokenResponse)
def login(req: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user or not auth.verify_password(req.password, user.password_hash):
        raise HTTPException(401, "Invalid email or password")
    token = auth.create_access_token({"sub": user.email, "role": user.role})
    return {"access_token": token,
            "user": {"id": user.id, "name": user.name, "email": user.email, "role": user.role}}

@app.get("/api/auth/me")
def me(current=Depends(auth.get_current_user)):
    return {"id": current.id, "name": current.name,
            "email": current.email, "role": current.role}

@app.post("/api/predict", response_model=schemas.PredictResponse)
def predict(req: schemas.PredictRequest, db: Session = Depends(get_db),
            current=Depends(auth.get_current_user)):
    if current.role == "viewer":
        raise HTTPException(403, "Viewers cannot run predictions")
    try:
        result = ml_service.predict_one(req.features.model_dump())
    except Exception as e:
        raise HTTPException(500, f"Prediction failed: {e}")
    db.add(models.Prediction(
        user_id=current.id, customer_id=req.id or "manual",
        churn_probability=result["churn_probability"],
        risk=result["risk"], predicted_churn=result["predicted_churn"],
    ))
    db.commit()
    return {"id": req.id, **result}

@app.post("/api/predict/bulk")
def predict_bulk(req: schemas.BulkPredictRequest, db: Session = Depends(get_db),
                 current=Depends(auth.get_current_user)):
    if current.role == "viewer":
        raise HTTPException(403, "Viewers cannot run predictions")
    rows = [c.features.model_dump() for c in req.customers]
    results = ml_service.predict_bulk(rows)
    for c, r in zip(req.customers, results):
        db.add(models.Prediction(
            user_id=current.id, customer_id=c.id or "bulk",
            churn_probability=r["churn_probability"],
            risk=r["risk"], predicted_churn=r["predicted_churn"],
        ))
    db.commit()
    return [{"id": c.id, **{k: v for k, v in r.items() if k != "index"}}
            for c, r in zip(req.customers, results)]

@app.get("/api/history")
def history(db: Session = Depends(get_db), current=Depends(auth.get_current_user)):
    q = db.query(models.Prediction).order_by(models.Prediction.created_at.desc()).limit(200)
    if current.role != "admin":
        q = q.filter(models.Prediction.user_id == current.id)
    return [{"id": p.id, "customer_id": p.customer_id,
             "churn_probability": p.churn_probability, "risk": p.risk,
             "predicted_churn": p.predicted_churn,
             "created_at": p.created_at} for p in q.all()]

@app.get("/api/health")
def health():
    return {"status": "ok", "model_threshold": ml_service.THRESHOLD}