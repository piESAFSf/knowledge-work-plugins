# Enterprise Multi-tenant SaaS Scaffold

## 1) 專案目錄樹

```text
backend/
  app/
    api/
    core/
    models/
    schemas/
    services/
    tasks/
    main.py
  alembic/
  tests/
  requirements.txt
  Dockerfile
frontend/
  src/
    pages/
    components/
    api/
    main.tsx
  package.json
  vite.config.ts
  Dockerfile
nginx/
  default.conf
docker-compose.yml
.env.example
README.md
```

## 2) 核心能力
- FastAPI + SQLAlchemy + Alembic
- JWT (access + refresh) with HttpOnly cookie
- Multi-tenant company data isolation (`company_id`)
- RBAC (`owner/manager/staff`)
- Stripe webhook subscription sync
- LINE webhook + OpenAI summarization service layer
- Redis cache/broker + Celery worker
- React + Vite + TypeScript + Tailwind dashboard skeleton

## 3) Docker 執行方式
```bash
cp .env.example .env
docker compose up --build
```

服務入口:
- App: http://localhost
- OpenAPI: http://localhost/docs

## 4) 本地開發啟動步驟

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## 5) 生產環境部署說明
1. 使用安全的 `SECRET_KEY` 與雲端 PostgreSQL/Redis。
2. 將 `backend` 部署到容器平台（ECS/GKE/K8s），指令:
   `gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 app.main:app`
3. `worker` 獨立部署 Celery，監控 queue 與重試策略。
4. Nginx/ALB 終止 TLS，僅暴露 443，後端內網通訊。
5. 設定 Stripe 與 LINE webhook URL 指向 `/api/v1/webhooks/*`。
6. 啟用監控（Prometheus/Grafana/Sentry）與每日資料備份。

## 測試
```bash
cd backend
pytest
```
