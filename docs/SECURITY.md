# Security

## Password storage
BCrypt via passlib. Never stored in plaintext.

## JWT
- HS256 signature
- 8-hour expiry
- Secret key read from `SECRET_KEY` env var
- Bearer token in `Authorization` header

## Roles
- viewer: read-only
- analyst: upload + predict + tasks
- admin: everything + settings + audit log

## CORS
Only origins listed in `CORS_ORIGINS` env var are accepted.

## Recommendations for production
- HTTPS only
- Rotate SECRET_KEY
- Move from SQLite to PostgreSQL
- Use httpOnly cookies instead of localStorage if keeping an SPA