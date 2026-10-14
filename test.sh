#!/usr/bin/env bash
set -e

BASE="http://localhost:8000"

echo "=== 1. Health ==="
curl -s "$BASE/api/health" | python -m json.tool
echo

echo "=== 2. Login ==="
LOGIN=$(curl -s -X POST "$BASE/api/auth/login" -H "Content-Type: application/json" -d '{"email":"test@example.com","password":"secret123"}')
echo "Response: $LOGIN"
echo

TOKEN=$(echo "$LOGIN" | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
echo "Token length: ${#TOKEN}"
echo

if [ -z "$TOKEN" ] || [ "$TOKEN" = "None" ]; then
  echo "ERROR: no token. Register the user first:"
  echo "  curl -X POST $BASE/api/auth/register -H 'Content-Type: application/json' -d '{\"name\":\"Test\",\"email\":\"test@example.com\",\"password\":\"secret123\",\"role\":\"analyst\"}'"
  exit 1
fi

echo "=== 3. Predict single ==="
curl -s -X POST "$BASE/api/predict" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"id":"C-SINGLE","features":{"Tenure":12,"CityTier":1,"WarehouseToHome":15,"PreferredLoginDevice":"Mobile Phone","PreferredPaymentMode":"Debit Card","Gender":"Male","HourSpendOnApp":3,"NumberOfDeviceRegistered":3,"PreferedOrderCat":"Laptop & Accessory","SatisfactionScore":3,"MaritalStatus":"Single","NumberOfAddress":2,"Complain":0,"OrderAmountHikeFromlastYear":15,"CouponUsed":2,"OrderCount":3,"DaySinceLastOrder":5,"CashbackAmount":150}}' | python -m json.tool
echo

echo "=== 4. Predict bulk ==="
curl -s -X POST "$BASE/api/predict/bulk" -H "Content-Type: application/json" -H "Authorization: Bearer $TOKEN" -d '{"customers":[{"id":"C-BULK","features":{"Tenure":12,"CityTier":1,"WarehouseToHome":15,"PreferredLoginDevice":"Mobile Phone","PreferredPaymentMode":"Debit Card","Gender":"Male","HourSpendOnApp":3,"NumberOfDeviceRegistered":3,"PreferedOrderCat":"Laptop & Accessory","SatisfactionScore":3,"MaritalStatus":"Single","NumberOfAddress":2,"Complain":0,"OrderAmountHikeFromlastYear":15,"CouponUsed":2,"OrderCount":3,"DaySinceLastOrder":5,"CashbackAmount":150}}]}' | python -m json.tool
echo

echo "=== ALL PASSED ==="
