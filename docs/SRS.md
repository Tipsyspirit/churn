# Software Requirement Specification

## Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-01 | User can register with name, email, password | High |
| FR-02 | User can log in and receive JWT | High |
| FR-03 | User can upload a CSV of customers | High |
| FR-04 | System scores every valid row | High |
| FR-05 | User sees churn probability and risk band | High |
| FR-06 | User can view prediction history | Medium |
| FR-07 | Admin can view all users' predictions | Medium |
| FR-08 | Invalid rows are reported with a reason | High |

## Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | Prediction latency < 2 seconds |
| NFR-02 | Passwords stored with BCrypt |
| NFR-03 | JWT expiry enforced (8 hours) |
| NFR-04 | All endpoints documented via OpenAPI |
| NFR-05 | Containerized deployment via Docker |