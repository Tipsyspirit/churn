# Testing

## Manual test cases

| ID | Case | Expected |
|----|------|----------|
| T1 | Register new user | JWT returned |
| T2 | Login with wrong password | 401 |
| T3 | Predict without token | 401 |
| T4 | Predict as viewer | 403 |
| T5 | Valid prediction | 0–1 probability |
| T6 | Bulk 100 rows | 100 results, < 2s |
| T7 | Invalid CSV row | Reported in upload error |
| T8 | Model file missing | Backend fails fast at startup |

## Automated

Run `pytest` in `backend/tests/`.