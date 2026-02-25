from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, hash_password, verify_password
from app.models import Company, User
from app.schemas.auth import LoginRequest, RefreshRequest, RegisterCompanyRequest, TokenResponse

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post('/register', response_model=TokenResponse)
def register_company(payload: RegisterCompanyRequest, response: Response, db: Session = Depends(get_db)):
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
    response.set_cookie('access_token', access, httponly=True, samesite='lax')
    response.set_cookie('refresh_token', refresh, httponly=True, samesite='lax')
    return TokenResponse(access_token=access)


@router.post('/login', response_model=TokenResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid credentials')

    access = create_access_token(str(user.id), str(user.company_id), user.role)
    refresh = create_refresh_token(str(user.id))
    response.set_cookie('access_token', access, httponly=True, samesite='lax')
    response.set_cookie(
        'refresh_token',
        refresh,
        httponly=True,
        samesite='lax',
        max_age=int(timedelta(days=settings.refresh_token_expire_days).total_seconds()),
    )
    return TokenResponse(access_token=access)


@router.post('/refresh', response_model=TokenResponse)
def refresh(payload: RefreshRequest, response: Response, db: Session = Depends(get_db)):
    from jose import jwt

    token = payload.refresh_token or response.headers.get('x-refresh-token')
    if not token:
        raise HTTPException(status_code=401, detail='Missing refresh token')
    data = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    if data.get('type') != 'refresh':
        raise HTTPException(status_code=401, detail='Invalid token type')
    user = db.query(User).filter(User.id == data['sub']).first()
    if not user:
        raise HTTPException(status_code=401, detail='User not found')
    access = create_access_token(str(user.id), str(user.company_id), user.role)
    response.set_cookie('access_token', access, httponly=True, samesite='lax')
    return TokenResponse(access_token=access)
