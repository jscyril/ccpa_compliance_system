---
phase: 3
plan: 1
wave: 1
depends_on: []
files_modified:
  - backend/app/main.py
autonomous: true

must_haves:
  truths:
    - "CORS middleware is applied with settings.CORS_ORIGINS"
    - "API endpoints are protected by X-API-Key header auth"
  artifacts:
    - "main.py imports CORSMiddleware and APIKeyHeader"
    - "/analyze endpoint requires api_key_dependency"
---

# Plan 3.1: API Security (CORS & Authentication)

## Objective
Implement CORS to allow cross-origin requests from the frontend, and add stateless API key authentication using the `X-API-Key` header to protect the system from unauthorized abuse.

Purpose: Delivers REQ-05 and REQ-06 from SPEC.md. Crucial for frontend integration and portfolio deployment security.

## Context
- .gsd/SPEC.md
- backend/app/core/config.py (provides `settings.CORS_ORIGINS` and `settings.API_KEY`)
- backend/app/main.py

## Tasks

<task type="auto">
  <name>Configure CORS Middleware</name>
  <files>backend/app/main.py</files>
  <action>
    Add `CORSMiddleware` to the FastAPI app:
    1. Import `CORSMiddleware` from `fastapi.middleware.cors`
    2. Import `settings` from `app.core.config`
    3. Add the middleware to the `app` using `app.add_middleware(...)`
    4. Set `allow_origins=settings.CORS_ORIGINS`
    5. Set `allow_credentials=True`, `allow_methods=["*"]`, `allow_headers=["*"]`

    AVOID: Don't hardcode origins, always use the settings object.
  </action>
  <verify>python -c "from app.main import app; assert any(m.cls.__name__ == 'CORSMiddleware' for m in app.user_middleware); print('OK')"</verify>
  <done>CORS middleware is registered on the FastAPI app.</done>
</task>

<task type="auto">
  <name>Implement API Key Authentication</name>
  <files>backend/app/main.py</files>
  <action>
    Implement `X-API-Key` header authentication:
    1. Import `APIKeyHeader` and `Security` from `fastapi.security`. Import `status` and `Depends` from `fastapi`.
    2. Instantiate the security scheme: `api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)`
    3. Create a dependency function `async def get_api_key(api_key: str = Security(api_key_header)):`
       - If `settings.API_KEY` is set AND `api_key != settings.API_KEY`, raise `HTTPException(status_code=403, detail="Invalid API Key")`
       - If `settings.API_KEY` is empty, allow all traffic (useful for local dev).
       - Return `api_key`
    4. Protect the `analyze` endpoint by adding `api_key: str = Depends(get_api_key)` to its arguments.
    5. Do NOT protect the `/health` endpoint.

    AVOID: Don't fail if settings.API_KEY is an empty string — this allows local development without keys.
  </action>
  <verify>
    curl -s http://localhost:8000/health | grep healthy > /dev/null
    echo "Health check is unauthenticated: OK"
  </verify>
  <done>The /analyze endpoint is protected by API key auth; /health is open.</done>
</task>

## Success Criteria
- [ ] CORS middleware is visible in FastAPI app
- [ ] Requests to `/analyze` without `X-API-Key` (when configured) return 403 Forbidden
- [ ] Requests to `/health` always succeed
