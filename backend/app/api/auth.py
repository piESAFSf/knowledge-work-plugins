from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.redis import redis_client
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models import Company, SecurityEvent, User, UserSession
from app.api.deps import get_current_user
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterCompanyRequest, TokenResponse

router = APIRouter(prefix='/auth', tags=['auth'])
FAILED_LIMIT = 5


@router.post('/register', response_model=TokenResponse)
def register_company(payload: RegisterCompanyRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == payload.owner_email).first()
    if exists:
        raise HTTPException(status_code=400, detail='Email already registered')

    company = Company(name=payload.company_name)
    db.add(company)
    db.flush()

    user = User(
        email=payload.owner_email,
        password_hash=hash_password(payload.owner_password),
        full_name=payload.owner_full_name,
        role='owner',
        company_id=company.id,
    )
    db.add(user)
    db.commit()

    access = create_access_token(str(user.id), str(company.id), user.role)
    refresh = create_refresh_token(str(user.id))

    session = UserSession(
        user_id=user.id,
        refresh_token=refresh,
        user_agent=request.headers.get('user-agent'),
        ip_address=request.client.host if request.client else None,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
    )
    db.add(session)
    db.commit()

    response.set_cookie('access_token', access, httponly=True, samesite='lax', secure=settings.session_cookie_secure)
    response.set_cookie(
        'refresh_token',
        refresh,
        httponly=True,
        samesite='lax',
        secure=settings.session_cookie_secure,
        max_age=int(timedelta(days=settings.refresh_token_expire_days).total_seconds()),
    )
    return TokenResponse(access_token=access)


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        fail_key = f'login_fail:{payload.email}'
        failures = redis_client.incr(fail_key)
        if failures == 1:
            redis_client.expire(fail_key, 900)
        if failures > FAILED_LIMIT and user:
            db.add(SecurityEvent(user_id=user.id, event_type='bruteforce_detected', event_metadata={'email': payload.email}))
            db.commit()
        raise HTTPException(status_code=401, detail='Invalid credentials')

    redis_client.delete(f'login_fail:{payload.email}')

    last_session = (
        db.query(UserSession)
        .filter(UserSession.user_id == user.id)
        .order_by(UserSession.created_at.desc())
        .first()
    )
    current_ip = request.client.host if request.client else None
    if last_session and last_session.ip_address and current_ip and last_session.ip_address != current_ip:
        db.add(
            SecurityEvent(
                user_id=user.id,
                event_type='ip_changed',
                event_metadata={'old_ip': last_session.ip_address, 'new_ip': current_ip},
            )
        )

    access = create_access_token(str(user.id), str(user.company_id), user.role)
    refresh = create_refresh_token(str(user.id))
    session = UserSession(
        user_id=user.id,
        refresh_token=refresh,
        user_agent=request.headers.get('user-agent'),
        ip_address=current_ip,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
    )
    db.add(session)
    db.commit()

    response.set_cookie('access_token', access, httponly=True, samesite='lax', secure=settings.session_cookie_secure)
    response.set_cookie(
        'refresh_token',
        refresh,
        httponly=True,
        samesite='lax',
        secure=settings.session_cookie_secure,
        max_age=int(timedelta(days=settings.refresh_token_expire_days).total_seconds()),
    )
    return TokenResponse(access_token=access)


@router.post('/refresh', response_model=TokenResponse)
def refresh(payload: RefreshRequest, request: Request, response: Response, db: Session = Depends(get_db)):
    token = payload.refresh_token or request.headers.get('x-refresh-token') or request.cookies.get('refresh_token')
    if not token:
        raise HTTPException(status_code=401, detail='Missing refresh token')

    try:
        data = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise HTTPException(status_code=401, detail='Invalid token') from exc

    if data.get('type') != 'refresh':
        raise HTTPException(status_code=401, detail='Invalid token type')

    session = (
        db.query(UserSession)
        .filter(
            UserSession.refresh_token == token,
            UserSession.is_revoked.is_(False),
            UserSession.expires_at > datetime.now(timezone.utc),
        )
        .first()
    )
    if not session:
        raise HTTPException(status_code=401, detail='Invalid session')

    user = db.query(User).filter(User.id == data['sub']).first()
    if not user:
        raise HTTPException(status_code=401, detail='User not found')

    session.is_revoked = True
    new_refresh = create_refresh_token(str(user.id))
    new_session = UserSession(
        user_id=user.id,
        refresh_token=new_refresh,
        user_agent=request.headers.get('user-agent') or session.user_agent,
        ip_address=request.client.host if request.client else session.ip_address,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days),
    )
    db.add(new_session)
    db.commit()

    access = create_access_token(str(user.id), str(user.company_id), user.role)
    response.set_cookie('access_token', access, httponly=True, samesite='lax', secure=settings.session_cookie_secure)
    response.set_cookie(
        'refresh_token',
        new_refresh,
        httponly=True,
        samesite='lax',
        secure=settings.session_cookie_secure,
        max_age=int(timedelta(days=settings.refresh_token_expire_days).total_seconds()),
    )
    return TokenResponse(access_token=access)


@router.post('/sessions/revoke')
def revoke_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(UserSession)
        .filter(UserSession.id == session_id, UserSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail='Session not found')

    session.is_revoked = True
    db.commit()
    return {'status': 'revoked'}
