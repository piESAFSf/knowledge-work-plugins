from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from app.api import auth, dashboard, users, webhooks
from app.core.config import settings

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title=settings.app_name, version='1.0.0')
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, lambda request, exc: JSONResponse(status_code=429, content={'detail': 'Rate limit exceeded'}))
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(',')],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.middleware('http')
async def csrf_middleware(request: Request, call_next):
    unsafe = {'POST', 'PUT', 'PATCH', 'DELETE'}
    if request.method in unsafe and not request.url.path.startswith('/webhooks'):
        csrf_cookie = request.cookies.get('csrf_token')
        csrf_header = request.headers.get('X-CSRF-Token')
        if not csrf_cookie or csrf_cookie != csrf_header:
            return JSONResponse(status_code=403, content={'detail': 'CSRF validation failed'})
    response = await call_next(request)
    if not request.cookies.get('csrf_token'):
        response.set_cookie('csrf_token', 'csrf-dev-token', httponly=False, samesite='lax')
    return response


@app.get('/healthz')
@limiter.limit('30/minute')
def health(_: Request):
    return {'status': 'ok'}


app.include_router(auth.router, prefix='/api/v1')
app.include_router(users.router, prefix='/api/v1')
app.include_router(dashboard.router, prefix='/api/v1')
app.include_router(webhooks.router, prefix='/api/v1')
