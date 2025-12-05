# Vercel + Railway Deployment (staging → production)

## Prerequisites
- Railway project with services: Postgres, Redis, and backend (FastAPI) container
- Vercel project for the Next.js frontend
- Environment secrets from `.env.example`/`frontend/.env.local` set in each platform

## Railway (backend)
1. Create Postgres + Redis managed services.
2. Deploy backend as a Docker service from `./backend` (Gunicorn/Uvicorn).
3. Set env vars: `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `BACKEND_CORS_ORIGINS`, `ALLOWED_HOSTS`, `ADMIN_USERS`, `PAYMENT_ENABLED`, `EXECUTION_POWER_ENABLED`.
4. Run migrations: `alembic upgrade head`.
5. Expose HTTP port 8000; add health check to `/health`.

## Vercel (frontend)
1. Set `NEXT_PUBLIC_API_URL` to the Railway backend URL and `NEXT_PUBLIC_WS_URL` to its websocket endpoint (wss).
2. `npm run build` during deploy; no server-side secrets in code.
3. Optionally add rewrite `/api/:path*` → backend URL for local dev proxying.

## CI/CD (suggested)
- Add a GitHub Actions workflow to lint/test backend & frontend, build Docker image, push to Railway.
- Add a separate job to run `alembic upgrade head` against the Railway database.
- Deploy frontend to Vercel via `vercel --prod` with env injection.

## Rollback
- Keep previous Railway deployment as rollback target; re-deploy prior image on failure.
- Revert Vercel to previous build from dashboard.

