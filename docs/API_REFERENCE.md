# API Reference

Base URL: `http://localhost:8000`

## Auth

### POST /api/auth/register
```json
{"name": "Alice", "email": "a@x.com", "password": "secret123", "role": "analyst"}
```

### POST /api/auth/login
```json
{"email": "a@x.com", "password": "secret123"}
```
Returns `{"access_token": "...", "token_type": "bearer", "user": {...}}`.

### GET /api/auth/me
Header: `Authorization: Bearer <token>`

## Predictions

### POST /api/predict
```json
{
  "id": "C-1042",
  "features": {
    "Tenure": 12, "CityTier": 1, "WarehouseToHome": 15,
    "PreferredLoginDevice": "Mobile Phone",
    "PreferredPaymentMode": "Debit Card", "Gender": "Male",
    "HourSpendOnApp": 3, "NumberOfDeviceRegistered": 3,
    "PreferedOrderCat": "Laptop & Accessory", "SatisfactionScore": 3,
    "MaritalStatus": "Single", "NumberOfAddress": 2, "Complain": 0,
    "OrderAmountHikeFromlastYear": 15, "CouponUsed": 2,
    "OrderCount": 3, "DaySinceLastOrder": 5, "CashbackAmount": 150
  }
}
```

### POST /api/predict/bulk
`{"customers": [<predict>, ...]}`

### GET /api/history
Header: `Authorization: Bearer <token>`

### GET /api/health
No auth required.