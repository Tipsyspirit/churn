from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=6)
    role: Optional[str] = "analyst"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

class CustomerFeatures(BaseModel):
    Tenure: float
    CityTier: int
    WarehouseToHome: float
    PreferredLoginDevice: str
    PreferredPaymentMode: str
    Gender: str
    HourSpendOnApp: float
    NumberOfDeviceRegistered: int
    PreferedOrderCat: str
    SatisfactionScore: int
    MaritalStatus: str
    NumberOfAddress: int
    Complain: int
    OrderAmountHikeFromlastYear: float
    CouponUsed: float
    OrderCount: float
    DaySinceLastOrder: float
    CashbackAmount: float

class PredictRequest(BaseModel):
    id: Optional[str] = None
    features: CustomerFeatures

class BulkPredictRequest(BaseModel):
    customers: List[PredictRequest]

class PredictResponse(BaseModel):
    id: Optional[str]
    churn_probability: float
    predicted_churn: int
    risk: str
    threshold: float