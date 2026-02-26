# Enterprise SaaS Starter (FastAPI + React)

企業級 SaaS 專案模板，包含多租戶、權限管理、Stripe/LINE webhook、OpenAI 服務層、Redis + Celery 背景任務。

## 1) 專案目錄樹

```text
backend/
  app/
    api/
      auth.py
      company.py
      webhooks.py
    core/
      config.py
      database.py
      deps.py
      security.py
    models/
      __init__.py
      audit_log.py
      company.py
      conversation.py
      subscription.py
      usage.py
      user.py
    schemas/
      auth.py
      company.py
    services/
      line_service.py
      openai_service.py
      quota_service.py
    tasks/
      ai_tasks.py
      celery_app.py
    main.py
  alembic/
    versions/0001_initial.py
    env.py
    script.py.mako
  alembic.ini
  requirements.txt
  Dockerfile
  tests/test_health.py
frontend/
  src/
    api/client.ts
    components/Layout.tsx
    pages/
      CompanyPage.tsx
      DashboardPage.tsx
      LoginPage.tsx
      StatsPage.tsx
      SubscriptionPage.tsx
      UsersPage.tsx
    index.css
    main.tsx
  Dockerfile
  index.html
  package.json
  postcss.config.js
  tailwind.config.js
  tsconfig.json
  vite.config.ts
nginx/default.conf
.env.example
docker-compose.yml
README.md
```

## 2) 主要能力對照

- 多公司資料隔離：所有商務資料表含 `company_id`，查詢與寫入依登入使用者 company 限制。
- 角色權限：`owner / manager / staff` 與 `require_roles` 依賴。
- JWT + refresh token：登入後寫入 HttpOnly cookie。
- CSRF：雙重提交 cookie/header（`csrf_token` + `X-CSRF-Token`）。
- Rate limiting：`slowapi` 示例（`/health` 每分鐘 30 次）。
- 密碼：bcrypt (`passlib`)。
- SQL injection 防護：SQLAlchemy ORM parameterized query。
- Stripe webhook：訂閱狀態更新。
- LINE webhook：接收訊息、寫入對話、排入 Celery 任務。
- OpenAI 服務層：`OpenAIService.summarize`。

## 3) Docker 執行方式

```bash
cp .env.example .env
docker compose up --build
```

服務：
- Nginx: `http://localhost`
- API docs: `http://localhost/api/docs`（FastAPI OpenAPI）

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

## 5) 生產部署建議

1. 使用雲端託管 PostgreSQL / Redis（RDS + ElastiCache）。
2. 將 `SECRET_KEY`、Stripe/LINE/OpenAI 金鑰改成 Secret Manager 管理。
3. 啟用 HTTPS，cookie 設 `secure=true`，Nginx 加上 HSTS。
4. Gunicorn worker 數依 CPU 調整，Celery worker 分離擴展。
5. 導入監控（Prometheus + Grafana）與錯誤追蹤（Sentry）。
6. CI/CD：測試、alembic migrate、藍綠部署。

## 測試

```bash
cd backend
pytest
```
