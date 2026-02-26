from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from itsdangerous import URLSafeTimedSerializer, BadSignature
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.auth import router as auth_router
from app.api.company import router as company_router
from app.api.webhooks import router as webhook_router
from app.core.config import settings

limiter = Limiter(key_func=get_remote_address)
csrf = URLSafeTimedSerializer(settings.secret_key, salt='csrf-token')

app = FastAPI(title=settings.app_name)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.allowed_origins.split(',')],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.middleware('http')
async def csrf_middleware(request: Request, call_next):
    if request.method in {'POST', 'PUT', 'PATCH', 'DELETE'} and not request.url.path.startswith('/webhooks'):
        csrf_cookie = request.cookies.get('csrf_token')
        csrf_header = request.headers.get('X-CSRF-Token')
        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            return JSONResponse({'detail': 'CSRF validation failed'}, status_code=403)
        try:
            csrf.loads(csrf_cookie, max_age=86400)
        except BadSignature:
            return JSONResponse({'detail': 'CSRF token invalid'}, status_code=403)
    response = await call_next(request)
    if not request.cookies.get('csrf_token'):
        token = csrf.dumps('csrf')
        response.set_cookie('csrf_token', token, httponly=False, samesite='lax', secure=False)
    return response


@app.get('/health')
@limiter.limit('30/minute')
def health(request: Request):
    return {'status': 'ok'}


app.include_router(auth_router, prefix='/api/v1')
app.include_router(company_router, prefix='/api/v1')
app.include_router(webhook_router, prefix='/api/v1')
